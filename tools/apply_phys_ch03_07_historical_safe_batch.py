#!/usr/bin/env python3
"""Revalidate and apply only deterministic A/C decisions from the historical Physiology fast lane.

The historical source review is donor evidence, not authority. This script accepts
an old reviewed request only when the immutable PDF hash still matches and the
live source audit/coverage still agree on reference identity, role, order, page,
and extraction candidates. Ambiguous D decisions are never mutated here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/marrow"
PDF = DATA / "source_pdfs/physiologyed8.pdf"
REGISTRY = DATA / "images/registry.json"
COVERAGE = DATA / "images/coverage.json"
AUDIT = ROOT / "build/marrow-images/audit.json"
ADJUDICATIONS = DATA / "images/source_reference_adjudications.json"
REVALIDATION = DATA / "images/review_requests/MANUAL_PHYS_CH03_07_SAFE_REVALIDATED_20260928.json"
SOURCE_SHA256 = "03834d3e9ec9723484387cd828a6f68cd999ec5187d167213f0bab9b967e0cfe"
HISTORICAL_RUN = 34700776495
BATCH = "manual-physiology-ch03-07-20260928-safe-donor"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def native_jpeg(reader: PdfReader, page_number: int, xref: int) -> tuple[bytes, int, int]:
    page = reader.pages[page_number - 1]
    objects = page.get("/Resources", {}).get("/XObject", {})
    matches = [ref.get_object() for ref in objects.values() if getattr(ref, "idnum", None) == xref]
    if len(matches) != 1:
        raise AssertionError(f"Expected one xref {xref} on page {page_number}, found {len(matches)}")
    obj = matches[0]
    filters = obj.get("/Filter")
    if obj.get("/Subtype") != "/Image" or not (filters == "/DCTDecode" or filters == ["/DCTDecode"]):
        raise AssertionError(f"xref {xref} is not a direct JPEG stream")
    if obj.get("/SMask") or obj.get("/Mask"):
        raise AssertionError(f"xref {xref} requires masked compositing")
    return obj._data, int(obj["/Width"]), int(obj["/Height"])


def render_region(page_number: int, region: list[float], dpi: int) -> tuple[bytes, int, int]:
    import fitz
    if not 144 <= dpi <= 600:
        raise AssertionError(f"Unsafe render DPI: {dpi}")
    with fitz.open(PDF) as document:
        page = document[page_number - 1]
        if page.rotation != 0:
            raise AssertionError("Resolve page rotation before region rendering")
        rect = fitz.Rect(region)
        if rect.is_empty or not page.rect.contains(rect):
            raise AssertionError(f"Invalid render region on page {page_number}: {region}")
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), clip=rect, alpha=False)
        raw = pix.tobytes("png")
        return raw, pix.width, pix.height


def expected_row(ref_id: str, coverage_by_id: dict, audit_by_id: dict) -> tuple[dict, dict]:
    coverage = coverage_by_id.get(ref_id)
    audit = audit_by_id.get(ref_id)
    if not coverage or not audit:
        raise AssertionError(f"Reference missing from live source state: {ref_id}")
    if coverage.get("coverageStatus") in {"RELEASED", "SOURCE_METADATA_INVALID"}:
        raise AssertionError(f"Historical donor reference is already resolved: {ref_id}")
    if coverage.get("questionId") != audit.get("questionId") or coverage.get("subject") != "Physiology":
        raise AssertionError(f"Reference identity drift: {ref_id}")
    return coverage, audit


def existing_asset_by_digest(registry: dict, digest: str) -> dict | None:
    matches = [a for a in registry["assets"]
               if digest in {(a.get("original") or {}).get("sha256"), (a.get("production") or {}).get("sha256")}]
    if len(matches) > 1:
        raise AssertionError(f"Ambiguous existing asset for digest {digest}")
    return matches[0] if matches else None


def matching_binding(asset: dict, qid: str, role: str, order: int) -> dict | None:
    rows = [b for b in asset.get("bindings", [])
            if b.get("questionId") == qid and b.get("role") == role and b.get("order") == order]
    if len(rows) > 1:
        raise AssertionError(f"Duplicate binding in {asset.get('id')} for {qid}/{role}/{order}")
    return rows[0] if rows else None


def promote(asset: dict, kind: str, notes: str, evidence: str) -> None:
    original = asset.get("original") or {}
    production = asset.get("production") or {}
    if not original.get("sha256") or not production.get("sha256"):
        raise AssertionError(f"Incomplete asset cannot be released: {asset.get('id')}")
    asset["status"] = "PASS"
    asset["kind"] = kind
    asset["reviewBatch"] = BATCH
    asset["qa"] = {
        "sourceCompared": True,
        "notes": notes,
        "evidence": evidence,
        "originalSha256": original["sha256"],
        "productionSha256": production["sha256"],
    }


def choose_alt(audit_row: dict) -> str:
    metadata = audit_row.get("metadata") or {}
    for key in ("alt", "caption", "title", "description", "label"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:300]
    return "Source figure"


def apply_c(reader: PdfReader, registry: dict, coverage_row: dict, audit_row: dict, decision: dict) -> str:
    extraction = decision.get("extraction") or {}
    method = extraction.get("method")
    page = int(extraction.get("page", 0))
    xref = int(extraction.get("xref", 0))
    region = extraction.get("region")
    if page not in coverage_row.get("sourcePages", []):
        raise AssertionError(f"Historical extraction page no longer belongs to {decision['sourceReferenceId']}")
    if not isinstance(region, list) or len(region) != 4:
        raise AssertionError(f"Historical extraction region missing for {decision['sourceReferenceId']}")

    candidates = [c for c in audit_row.get("candidateImages", []) if c.get("page") == page]
    current_xrefs = {int(c["xref"]) for c in candidates if isinstance(c.get("xref"), int)}
    required_xrefs = {int(value) for value in extraction.get("xrefs", [xref])}
    if not required_xrefs or not required_xrefs.issubset(current_xrefs):
        raise AssertionError(f"Live candidate xrefs drifted for {decision['sourceReferenceId']}: {required_xrefs} vs {current_xrefs}")

    if method == "native-jpeg-stream":
        raw, width, height = native_jpeg(reader, page, xref)
        digest = sha256(raw)
        if digest != extraction.get("expectedStreamSha256"):
            raise AssertionError(f"Native stream drift for {decision['sourceReferenceId']}: {digest}")
        suffix = ".jpg"
    elif method == "region-render":
        dpi = int(extraction.get("dpi", 300))
        raw, width, height = render_region(page, region, dpi)
        digest = sha256(raw)
        suffix = ".png"
    else:
        raise AssertionError(f"Unsupported deterministic extraction method: {method}")

    originals = DATA / "images/originals"
    originals.mkdir(parents=True, exist_ok=True)
    target = originals / f"{digest}{suffix}"
    if target.exists() and target.read_bytes() != raw:
        raise AssertionError(f"Immutable extraction conflict: {target}")
    if not target.exists():
        target.write_bytes(raw)

    qid = coverage_row["questionId"]
    role = coverage_row.get("role")
    order = int(coverage_row.get("order"))
    if role not in {"question", "explanation"}:
        raise AssertionError(f"Live role is not releasable for {decision['sourceReferenceId']}: {role}")
    kind = extraction.get("kind", "diagram")
    source_binding = {"page": page, "xref": xref, "region": region}
    evidence = (
        f"Historical source review run {HISTORICAL_RUN} revalidated on current branch: immutable "
        f"physiologyed8.pdf SHA-256 {SOURCE_SHA256}, live audit candidate page {page}/xref {xref}, "
        f"current role/order {role}/{order}."
    )
    notes = decision.get("notes") or "Source-faithful extraction revalidated against current audit."

    asset = existing_asset_by_digest(registry, digest)
    if asset:
        if asset.get("subject") != "Physiology":
            raise AssertionError(f"Cross-subject digest collision: {asset.get('id')}")
        binding = matching_binding(asset, qid, role, order)
        if not binding:
            asset.setdefault("bindings", []).append({
                "questionId": qid,
                "role": role,
                "order": order,
                "alt": choose_alt(audit_row),
                "source": source_binding,
            })
        else:
            if binding.get("status") == "REJECTED":
                raise AssertionError(f"Current explicit rejection conflicts with donor C decision: {decision['sourceReferenceId']}")
            binding["source"] = source_binding
            if "status" in binding:
                binding["status"] = "PASS"
                binding["qa"] = {"sourceCompared": True, "notes": notes, "evidence": evidence}
        promote(asset, kind, notes, evidence)
        return asset["id"]

    asset_id = f"physiology-{digest[:16]}"
    if any(a.get("id") == asset_id for a in registry["assets"]):
        raise AssertionError(f"Asset id collision: {asset_id}")
    rel = f"data/marrow/images/originals/{digest}{suffix}"
    asset = {
        "id": asset_id,
        "subject": "Physiology",
        "kind": kind,
        "reviewBatch": BATCH,
        "source": {
            "file": "physiologyed8.pdf",
            "sha256": SOURCE_SHA256,
            "page": page,
            "xref": xref,
            "region": region,
        },
        "bindings": [{
            "questionId": qid,
            "role": role,
            "order": order,
            "alt": choose_alt(audit_row),
        }],
        "original": {"path": rel, "sha256": digest, "width": width, "height": height},
        "production": {"path": rel, "sha256": digest, "width": width, "height": height},
        "method": method,
        "status": "PASS",
        "qa": {
            "sourceCompared": True,
            "notes": notes,
            "evidence": evidence,
            "originalSha256": digest,
            "productionSha256": digest,
        },
    }
    registry["assets"].append(asset)
    return asset_id


def apply_a(adjudications: dict, coverage_row: dict, decision: dict) -> None:
    role = coverage_row.get("role")
    pages = coverage_row.get("sourcePages")
    if role not in {"question", "explanation"} or not pages:
        raise AssertionError(f"Live source identity cannot support adjudication: {decision['sourceReferenceId']}")
    entry = {
        "id": decision["sourceReferenceId"],
        "questionId": coverage_row["questionId"],
        "subject": "Physiology",
        "role": role,
        "sourcePages": pages,
        "status": "SOURCE_METADATA_INVALID",
        "source": {"file": "physiologyed8.pdf", "sha256": SOURCE_SHA256},
        "reason": decision.get("notes") or "Historical source review established that this metadata binding is not source-owned by the question.",
        "evidence": (
            f"Historical manual source review run {HISTORICAL_RUN} revalidated against the live canonical "
            f"source reference on 2026-09-28. Immutable PDF hash, question identity, role/order and source "
            f"page set still match; no registry state was transplanted."
        ),
    }
    existing = [row for row in adjudications.get("entries", []) if row.get("id") == entry["id"]]
    if existing:
        if existing[0] != entry:
            raise AssertionError(f"Conflicting live adjudication: {entry['id']}")
        return
    adjudications.setdefault("entries", []).append(entry)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical", type=Path, required=True)
    args = parser.parse_args()

    if sha256(PDF.read_bytes()) != SOURCE_SHA256:
        raise AssertionError("Physiology source PDF hash changed")
    historical = json.loads(args.historical.read_text())
    if historical.get("kind") != "MARROW_IMAGE_FAST_LANE_REVIEW_REQUEST" or historical.get("subject") != "Physiology":
        raise AssertionError("Unexpected historical review schema")
    if historical.get("source", {}).get("sha256") != SOURCE_SHA256:
        raise AssertionError("Historical review used a different source PDF")
    decisions = historical.get("decisions", [])
    if len(decisions) != 40 or {d.get("decision") for d in decisions} - {"A", "C", "D"}:
        raise AssertionError("Historical donor request drift")
    safe = [d for d in decisions if d.get("decision") in {"A", "C"}]
    if len(safe) != 26:
        raise AssertionError(f"Expected 26 deterministic donor decisions, found {len(safe)}")

    registry = json.loads(REGISTRY.read_text())
    coverage = json.loads(COVERAGE.read_text())
    audit = json.loads(AUDIT.read_text())
    adjudications = json.loads(ADJUDICATIONS.read_text())
    coverage_by_id = {row["id"]: row for row in coverage.get("sourceVisuals", [])}
    audit_by_id = {row["id"]: row for row in audit.get("bindings", [])}
    reader = PdfReader(PDF)

    outcomes = []
    for decision in safe:
        ref_id = decision["sourceReferenceId"]
        coverage_row, audit_row = expected_row(ref_id, coverage_by_id, audit_by_id)
        if decision["decision"] == "C":
            asset_id = apply_c(reader, registry, coverage_row, audit_row, decision)
            outcome = {"sourceReferenceId": ref_id, "decision": "C", "outcome": "RELEASED", "assetId": asset_id}
        else:
            apply_a(adjudications, coverage_row, decision)
            outcome = {"sourceReferenceId": ref_id, "decision": "A", "outcome": "SOURCE_METADATA_INVALID"}
        outcomes.append(outcome)

    write_json(REGISTRY, registry)
    write_json(ADJUDICATIONS, adjudications)
    write_json(REVALIDATION, {
        "schemaVersion": 1,
        "kind": "MARROW_IMAGE_SAFE_DONOR_REVALIDATION",
        "batchId": "MANUAL_PHYS_CH03_07_SAFE_REVALIDATED_20260928",
        "subject": "Physiology",
        "historicalSourceReviewRun": HISTORICAL_RUN,
        "historicalCanonicalBaseSha": historical.get("canonicalBaseSha"),
        "liveSourceSha256": SOURCE_SHA256,
        "reviewedReferenceCount": 40,
        "appliedDeterministicCount": len(outcomes),
        "deferredAmbiguousCount": sum(d.get("decision") == "D" for d in decisions),
        "outcomes": outcomes,
        "guardrails": [
            "Immutable source PDF hash matched historical source review.",
            "Every applied reference still existed unresolved in live coverage.",
            "Question identity, role, order and source pages were taken from live coverage/audit.",
            "C extractions required live candidate xrefs to match historical extraction evidence.",
            "D decisions were not mutated and remain for direct source review."
        ]
    })
    print("PHYS_SAFE_DONOR_APPLIED", len(outcomes), "DEFERRED_D", sum(d.get("decision") == "D" for d in decisions))


if __name__ == "__main__":
    main()
