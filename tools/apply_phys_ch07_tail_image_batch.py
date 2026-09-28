#!/usr/bin/env python3
"""Apply the reviewed Physiology Ch7 tail image batch deterministically.

This script only consumes the checked-in manual review request. It verifies the
immutable source PDF and native JPEG streams before mutating the image registry
or source-reference adjudications. Generated coverage/progress/runtime files are
rebuilt by the workflow after this script succeeds.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/marrow"
REGISTRY = DATA / "images/registry.json"
ADJUDICATIONS = DATA / "images/source_reference_adjudications.json"
REQUEST = DATA / "images/review_requests/MANUAL_PHYS_CH07_TAIL_20260928.json"
PDF = DATA / "source_pdfs/physiologyed8.pdf"
SOURCE_SHA256 = "03834d3e9ec9723484387cd828a6f68cd999ec5187d167213f0bab9b967e0cfe"
BATCH = "manual-physiology-ch03-07-20260928-ch07-tail"
EXPECTED_REFS = {
    "marrow__PHYS_CH07_Q024:figure:2",
    "marrow__PHYS_CH07_Q025:figure:1",
    "marrow__PHYS_CH07_Q029:figure:1",
    "marrow__PHYS_CH07_Q030:figure:1",
    "marrow__PHYS_CH07_Q032:figure:1",
    "marrow__PHYS_CH07_Q033:figure:1",
    "marrow__PHYS_CH07_Q033:figure:2",
    "marrow__PHYS_CH07_Q034:figure:1",
    "marrow__PHYS_CH07_Q035:figure:1",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def native_jpeg(reader: PdfReader, page_number: int, xref: int) -> tuple[bytes, int, int]:
    page = reader.pages[page_number - 1]
    objects = page.get("/Resources", {}).get("/XObject", {})
    matches = []
    for ref in objects.values():
        if getattr(ref, "idnum", None) == xref:
            matches.append(ref.get_object())
    if len(matches) != 1:
        raise AssertionError(f"Expected one xref {xref} on page {page_number}, found {len(matches)}")
    obj = matches[0]
    if obj.get("/Subtype") != "/Image":
        raise AssertionError(f"xref {xref} is not an image")
    filters = obj.get("/Filter")
    if not (filters == "/DCTDecode" or filters == ["/DCTDecode"]):
        raise AssertionError(f"xref {xref} is not a direct JPEG stream: {filters}")
    if obj.get("/SMask") or obj.get("/Mask"):
        raise AssertionError(f"xref {xref} requires masked compositing")
    return obj._data, int(obj["/Width"]), int(obj["/Height"])


def binding_for(asset: dict, question_id: str, role: str, order: int) -> dict | None:
    rows = [b for b in asset.get("bindings", [])
            if b.get("questionId") == question_id and b.get("role") == role and b.get("order") == order]
    if len(rows) > 1:
        raise AssertionError(f"Duplicate binding in {asset.get('id')}: {question_id}/{role}/{order}")
    return rows[0] if rows else None


def promote_asset(asset: dict, notes: str, evidence: str) -> None:
    original = asset.get("original") or {}
    production = asset.get("production") or {}
    if not original.get("sha256") or not production.get("sha256"):
        raise AssertionError(f"Cannot promote incomplete asset {asset.get('id')}")
    asset["status"] = "PASS"
    asset["kind"] = "diagram"
    asset["reviewBatch"] = BATCH
    asset["qa"] = {
        "sourceCompared": True,
        "notes": notes,
        "evidence": evidence,
        "originalSha256": original["sha256"],
        "productionSha256": production["sha256"],
    }


def apply_extraction(reader: PdfReader, registry: dict, decision: dict) -> str:
    extraction = decision["extraction"]
    if extraction.get("method") != "native-jpeg-stream":
        raise AssertionError("This batch only permits reviewed native JPEG extraction")
    page = int(extraction["page"])
    xref = int(extraction["xref"])
    raw, width, height = native_jpeg(reader, page, xref)
    digest = sha256(raw)
    if digest != extraction["expectedStreamSha256"]:
        raise AssertionError(f"Source stream drift for {decision['sourceReferenceId']}: {digest}")

    originals = DATA / "images/originals"
    originals.mkdir(parents=True, exist_ok=True)
    target = originals / f"{digest}.jpg"
    if target.exists():
        if target.read_bytes() != raw:
            raise AssertionError(f"Immutable image conflict: {target}")
    else:
        target.write_bytes(raw)

    matches = [a for a in registry["assets"]
               if digest in {(a.get("original") or {}).get("sha256"), (a.get("production") or {}).get("sha256")}]
    if len(matches) > 1:
        raise AssertionError(f"Ambiguous existing asset for source stream {digest}")

    qid = extraction["questionId"]
    role = extraction["role"]
    order = int(extraction["order"])
    source = {
        "page": page,
        "xref": xref,
        "region": extraction["region"],
    }
    evidence = (
        f"Manual authoritative source review {BATCH}: physiologyed8.pdf page {page}, "
        f"xref {xref}, immutable stream SHA-256 {digest}."
    )
    notes = decision["notes"]

    if matches:
        asset = matches[0]
        if asset.get("subject") != "Physiology":
            raise AssertionError(f"Cross-subject stream collision: {asset.get('id')}")
        binding = binding_for(asset, qid, role, order)
        if not binding:
            asset.setdefault("bindings", []).append({
                "questionId": qid,
                "role": role,
                "order": order,
                "alt": extraction["alt"],
                "source": source,
            })
        else:
            binding["alt"] = extraction["alt"]
            binding["source"] = source
            if binding.get("status") == "REJECTED":
                raise AssertionError(f"Refusing to override rejected binding for {qid}")
            if "status" in binding:
                binding["status"] = "PASS"
                binding["qa"] = {"sourceCompared": True, "notes": notes, "evidence": evidence}
        promote_asset(asset, notes, evidence)
        return asset["id"]

    asset_id = f"physiology-{digest[:16]}"
    if any(a.get("id") == asset_id for a in registry["assets"]):
        raise AssertionError(f"Asset id collision: {asset_id}")
    rel = f"data/marrow/images/originals/{digest}.jpg"
    asset = {
        "id": asset_id,
        "subject": "Physiology",
        "kind": extraction.get("kind", "diagram"),
        "reviewBatch": BATCH,
        "source": {
            "file": "physiologyed8.pdf",
            "sha256": SOURCE_SHA256,
            "page": page,
            "xref": xref,
            "region": extraction["region"],
        },
        "bindings": [{
            "questionId": qid,
            "role": role,
            "order": order,
            "alt": extraction["alt"],
        }],
        "original": {"path": rel, "sha256": digest, "width": width, "height": height},
        "production": {"path": rel, "sha256": digest, "width": width, "height": height},
        "method": "native-jpeg-stream",
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


def apply_reuse(registry: dict, decision: dict) -> str:
    reuse = decision["reuse"]
    matches = [a for a in registry["assets"] if a.get("id") == reuse["assetId"]]
    if len(matches) != 1:
        raise AssertionError(f"Expected tracked asset {reuse['assetId']}")
    asset = matches[0]
    if (asset.get("original") or {}).get("sha256") != reuse["expectedStreamSha256"]:
        raise AssertionError(f"Tracked asset stream drift: {asset['id']}")
    if asset.get("source", {}).get("page") != reuse["page"]:
        raise AssertionError(f"Tracked asset page drift: {asset['id']}")
    binding = binding_for(asset, reuse["questionId"], reuse["role"], int(reuse["order"]))
    if not binding:
        raise AssertionError(f"Expected existing binding for {decision['sourceReferenceId']}")
    evidence = (
        f"Manual authoritative source review {BATCH}: physiologyed8.pdf page {reuse['page']}, "
        f"xref {reuse['xref']}, existing immutable stream {reuse['expectedStreamSha256']}."
    )
    if "status" in binding:
        binding["status"] = "PASS"
        binding["qa"] = {"sourceCompared": True, "notes": decision["notes"], "evidence": evidence}
    binding["source"] = {"page": reuse["page"], "xref": reuse["xref"], "region": reuse["region"]}
    promote_asset(asset, decision["notes"], evidence)
    return asset["id"]


def apply_adjudication(adjudications: dict, decision: dict) -> None:
    adj = decision["adjudication"]
    entry = {
        "id": decision["sourceReferenceId"],
        "questionId": adj["questionId"],
        "subject": "Physiology",
        "role": adj["role"],
        "sourcePages": adj["sourcePages"],
        "status": "SOURCE_METADATA_INVALID",
        "source": {"file": "physiologyed8.pdf", "sha256": SOURCE_SHA256},
        "reason": adj["reason"],
        "evidence": (
            f"Manual authoritative source review {BATCH}: rendered page(s) "
            f"{','.join(map(str, adj['sourcePages']))} inspected against solution ownership. "
            f"{decision['notes']}"
        ),
    }
    existing = [e for e in adjudications.get("entries", []) if e.get("id") == entry["id"]]
    if existing:
        if existing[0] != entry:
            raise AssertionError(f"Conflicting adjudication already exists: {entry['id']}")
        return
    adjudications.setdefault("entries", []).append(entry)


def main() -> None:
    if sha256(PDF.read_bytes()) != SOURCE_SHA256:
        raise AssertionError("Physiology source PDF hash changed")
    request = json.loads(REQUEST.read_text())
    if request.get("schemaVersion") != 1 or request.get("kind") != "MARROW_IMAGE_MANUAL_INTEGRATION_REQUEST":
        raise AssertionError("Unexpected integration request schema")
    decisions = request.get("decisions", [])
    refs = [row.get("sourceReferenceId") for row in decisions]
    if len(decisions) != 9 or set(refs) != EXPECTED_REFS or len(set(refs)) != 9:
        raise AssertionError("Ch7-tail request scope drift")
    if request.get("source", {}).get("sha256") != SOURCE_SHA256:
        raise AssertionError("Review request source hash drift")

    registry = json.loads(REGISTRY.read_text())
    adjudications = json.loads(ADJUDICATIONS.read_text())
    reader = PdfReader(PDF)
    applied = []
    for decision in decisions:
        lane = decision.get("decision")
        if lane == "C":
            applied.append((decision["sourceReferenceId"], "RELEASED", apply_extraction(reader, registry, decision)))
        elif lane == "B":
            applied.append((decision["sourceReferenceId"], "RELEASED", apply_reuse(registry, decision)))
        elif lane == "A":
            apply_adjudication(adjudications, decision)
            applied.append((decision["sourceReferenceId"], "SOURCE_METADATA_INVALID", None))
        else:
            raise AssertionError(f"Unsupported reviewed lane in this batch: {lane}")

    write_json(REGISTRY, registry)
    write_json(ADJUDICATIONS, adjudications)
    print("PHYS_CH07_TAIL_APPLIED", json.dumps(applied, separators=(",", ":")))


if __name__ == "__main__":
    main()
