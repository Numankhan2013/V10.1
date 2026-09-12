#!/usr/bin/env python3
"""Apply one human-reviewed Marrow fast-lane A/C/D manifest fail-closed.

This command is intentionally mutation-capable and must run only on Ubuntu CI
after the proposal-only source-review artifact has been inspected by a human.
It never rewrites source PDFs or raw Marrow question bundles.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image

from marrow_image_fast_lane import validate_reviewed_plan
from marrow_images import (
    DATA,
    ROOT,
    SOURCES,
    extract,
    render_region,
    release,
    sha,
    validate,
    write_json,
)

REGISTRY = DATA / "images/registry.json"
PROGRESS = DATA / "images/progress.json"
COVERAGE = DATA / "images/coverage.json"
ADJUDICATIONS = DATA / "images/source_reference_adjudications.json"
AUDIT = ROOT / "build/marrow-images/audit.json"
ORIGINALS = DATA / "images/originals"
ADJ_STATUS = "SOURCE_METADATA_INVALID"


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_region(a, b, tol=0.002):
    return len(a or []) == len(b or []) == 4 and all(abs(float(x) - float(y)) <= tol for x, y in zip(a, b))


def subprocess_checked(*args):
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True)


def assert_input_fingerprints(plan):
    expected = plan["inputFingerprints"]
    actual = {
        "registrySha256": file_sha(REGISTRY),
        "progressSha256": file_sha(PROGRESS),
        "coverageSha256": file_sha(COVERAGE),
    }
    if actual != expected:
        raise SystemExit(
            "Shared image state changed after review; refusing mutation.\n"
            f"expected={json.dumps(expected, sort_keys=True)}\n"
            f"actual={json.dumps(actual, sort_keys=True)}"
        )


def audit_row_map():
    value = json.loads(AUDIT.read_text())
    return value, {row["id"]: row for row in value["bindings"]}


def assert_review_matches_audit(row, audit_row):
    assert row["questionId"] == audit_row["questionId"], row["sourceReferenceId"]
    assert row["sourcePages"], row["sourceReferenceId"]
    metadata = audit_row.get("metadata") or {}
    pages = metadata.get("source_pages")
    if not isinstance(pages, list):
        page = metadata.get("source_page")
        pages = [page] if isinstance(page, int) else []
    pages = sorted({int(page) for page in pages if isinstance(page, int) and page > 0})
    assert pages == sorted(row["sourcePages"]), (row["sourceReferenceId"], pages, row["sourcePages"])


def verify_recipe_against_audit(row, audit_row):
    recipe = row["extraction"]
    candidates = audit_row.get("candidateImages", [])
    page = recipe["page"]
    xrefs = list(recipe.get("xrefs") or [recipe["xref"]])
    chosen = [c for c in candidates if c.get("page") == page and c.get("xref") in xrefs]
    assert {c["xref"] for c in chosen} == set(xrefs), (
        row["sourceReferenceId"], "review recipe no longer matches source audit", xrefs
    )
    if recipe["method"] == "native-jpeg-stream":
        assert len(xrefs) == 1
        c = chosen[0]
        assert not c.get("mask")
        assert c.get("filter") in {"/DCTDecode", "['/DCTDecode']"}
        assert c["streamSha256"] == recipe["expectedStreamSha256"]
        assert same_region(c["region"], recipe["region"])
    else:
        assert recipe["method"] == "region-render"
        assert 144 <= int(recipe.get("dpi", 300)) <= 600
        x1, y1, x2, y2 = map(float, recipe["region"])
        for c in chosen:
            a, b, d, e = map(float, c["region"])
            assert x1 <= a + .01 and y1 <= b + .01 and x2 >= d - .01 and y2 >= e - .01


def find_region_sidecar(recipe):
    matches = []
    for path in ORIGINALS.glob("*.json"):
        try:
            value = json.loads(path.read_text())
        except Exception:
            continue
        if value.get("method") != "region-render":
            continue
        if value.get("source") != SOURCES["Physiology"][1]:
            continue
        if value.get("page") != recipe["page"] or int(value.get("dpi", 0)) != int(recipe["dpi"]):
            continue
        if same_region(value.get("region", []), recipe["region"]):
            matches.append((path, value))
    assert len(matches) == 1, ("region-render sidecar match", recipe, [str(p) for p, _ in matches])
    return matches[0]


def dimensions(path: Path):
    with Image.open(path) as im:
        width, height = im.size
    assert width > 0 and height > 0
    return int(width), int(height)


def add_adjudication(row, adjudications, source):
    proposed = {
        "id": row["sourceReferenceId"],
        "questionId": row["questionId"],
        "subject": "Physiology",
        "role": row["role"],
        "sourcePages": row["sourcePages"],
        "status": ADJ_STATUS,
        "source": source,
        "reason": row["adjudication"]["reason"],
        "evidence": row["adjudication"]["evidence"],
    }
    matches = [entry for entry in adjudications["entries"] if entry.get("id") == proposed["id"]]
    if matches:
        assert len(matches) == 1 and matches[0] == proposed, f"Conflicting adjudication: {proposed['id']}"
        return False
    adjudications["entries"].append(proposed)
    return True


def existing_hash_owners(registry):
    owners = {}
    for asset in registry["assets"]:
        for key in ("original", "production"):
            rec = asset.get(key) or {}
            digest = rec.get("sha256")
            if digest:
                owners.setdefault(digest, set()).add(asset["id"])
    return owners


def materialize_c(row, audit_row, registry, source, batch_id):
    recipe = row["extraction"]
    verify_recipe_against_audit(row, audit_row)

    if recipe["method"] == "native-jpeg-stream":
        extract("Physiology", recipe["page"], recipe["xref"], ORIGINALS)
        digest = recipe["expectedStreamSha256"]
        image_path = ORIGINALS / f"{digest}.jpg"
        sidecar_path = ORIGINALS / f"{digest}.json"
        assert image_path.exists() and sidecar_path.exists()
        sidecar = json.loads(sidecar_path.read_text())
        assert sidecar["sha256"] == digest and sidecar["page"] == recipe["page"] and sidecar["xref"] == recipe["xref"]
        assert same_region(recipe["region"], next(c["region"] for c in audit_row["candidateImages"]
                                                  if c["page"] == recipe["page"] and c["xref"] == recipe["xref"]))
    else:
        render_region("Physiology", recipe["page"], recipe["region"], int(recipe["dpi"]), ORIGINALS)
        _, sidecar = find_region_sidecar(recipe)
        digest = sidecar["sha256"]
        image_path = ORIGINALS / f"{digest}.png"
        assert image_path.exists() and file_sha(image_path) == digest

    owners = existing_hash_owners(registry)
    if digest in owners:
        raise AssertionError(
            f"{row['sourceReferenceId']}: reviewed C output duplicates existing asset(s) {sorted(owners[digest])}; "
            "reclassify as reuse instead of silently duplicating it"
        )

    asset_id = f"physiology-{digest[:16]}"
    assert not any(asset["id"] == asset_id for asset in registry["assets"]), asset_id
    width, height = dimensions(image_path)
    relpath = image_path.relative_to(ROOT).as_posix()
    original = {"path": relpath, "sha256": digest, "width": width, "height": height}
    xrefs = list(recipe.get("xrefs") or [recipe["xref"]])
    title = str((row.get("metadata") or {}).get("title") or "Source explanation figure")
    alt = "Source question figure" if row["role"] == "question" else title
    source_ref = {
        "page": int(recipe["page"]),
        "xref": int(recipe["xref"]),
        "xrefs": [int(x) for x in xrefs],
        "region": [float(x) for x in recipe["region"]],
    }
    method_label = (
        f"native PDF JPEG xref {recipe['xref']}"
        if recipe["method"] == "native-jpeg-stream"
        else f"precise 300-DPI render of source xref(s) {','.join(map(str, xrefs))}"
    )
    evidence = (
        f"Fast-lane source-review workflow 34700776495; authoritative Physiology ED8 page {recipe['page']} "
        f"inspected against {row['questionId']}; {method_label}; source region {recipe['region']}."
    )
    notes = (
        f"Source ownership, role/order, labels/extent, and answer timing reviewed for "
        f"{row['sourceReferenceId']}. Materialized without generative editing."
    )
    asset_source = {"file": source["file"], "sha256": source["sha256"], **source_ref}
    binding_source = dict(source_ref)
    asset = {
        "id": asset_id,
        "subject": "Physiology",
        "kind": recipe["kind"],
        "reviewBatch": batch_id,
        "source": asset_source,
        "bindings": [{
            "questionId": row["questionId"],
            "role": row["role"],
            "order": int(row["order"]),
            "alt": alt,
            "status": "PASS",
            "reviewBatch": batch_id,
            "source": binding_source,
            "qa": {"sourceCompared": True, "notes": notes, "evidence": evidence},
        }],
        "original": original,
        "production": dict(original),
        "method": recipe["method"],
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
    row["extraction"]["assetId"] = asset_id
    row["extraction"]["sha256"] = digest
    row["extraction"]["width"] = width
    row["extraction"]["height"] = height
    row["extraction"]["newUniqueAsset"] = True
    return asset_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    review_root = (DATA / "images/review_batches").resolve()
    if not plan_path.is_relative_to(review_root):
        raise SystemExit("Reviewed plan must live under data/marrow/images/review_batches")

    plan = json.loads(plan_path.read_text())
    validate_reviewed_plan(plan)
    assert plan["subject"] == "Physiology"
    counts = {lane: sum(row["decision"] == lane for row in plan["entries"]) for lane in "ABCD"}
    assert counts == {"A": 14, "B": 0, "C": 12, "D": 14}, counts
    assert_input_fingerprints(plan)

    audit, audit_rows = audit_row_map()
    assert audit["sources"]["Physiology"]["file"] == plan["source"]["file"]
    assert audit["sources"]["Physiology"]["sha256"] == plan["source"]["sha256"]
    source_pdf = DATA / "source_pdfs" / SOURCES["Physiology"][1]
    assert sha(source_pdf.read_bytes()) == plan["source"]["sha256"]

    registry = validate(REGISTRY)
    adjudications = json.loads(ADJUDICATIONS.read_text())
    assert adjudications.get("schemaVersion") == 1
    assert isinstance(adjudications.get("entries"), list)

    a_added = 0
    c_assets = []
    source = {"file": plan["source"]["file"], "sha256": plan["source"]["sha256"]}
    for row in plan["entries"]:
        ref = row["sourceReferenceId"]
        assert ref in audit_rows, ref
        audit_row = audit_rows[ref]
        assert_review_matches_audit(row, audit_row)
        if row["decision"] == "A":
            a_added += int(add_adjudication(row, adjudications, source))
        elif row["decision"] == "C":
            c_assets.append(materialize_c(row, audit_row, registry, source, plan["batchId"]))
        elif row["decision"] == "D":
            assert row["defer"]["status"] == "REVIEW_REQUIRED"
        else:
            raise AssertionError("This batch intentionally contains no reuse lane B items")

    write_json(REGISTRY, registry)
    adjudications["entries"].sort(key=lambda entry: (entry.get("subject", ""), entry.get("id", "")))
    write_json(ADJUDICATIONS, adjudications)
    write_json(plan_path, plan)

    validate(REGISTRY)
    release(REGISTRY)
    subprocess_checked("tools/marrow_image_progress.py")
    subprocess_checked("tools/marrow_image_coverage.py", "--subject", "Physiology")

    coverage = json.loads(COVERAGE.read_text())
    progress = json.loads(PROGRESS.read_text())
    plan["outputFingerprints"] = {
        "registrySha256": file_sha(REGISTRY),
        "progressSha256": file_sha(PROGRESS),
        "coverageSha256": file_sha(COVERAGE),
        "adjudicationsSha256": file_sha(ADJUDICATIONS),
    }
    plan["outputSummary"] = {
        "decisions": counts,
        "newAdjudications": a_added,
        "newAssetIds": c_assets,
        "physiologyCoverage": coverage["summary"]["Physiology"],
        "releasedQuestionCount": progress["bindings"]["releasedQuestionCount"],
    }
    write_json(plan_path, plan)
    validate_reviewed_plan(plan)

    summary = coverage["summary"]["Physiology"]
    assert summary["resolvedSourceVisualReferences"] >= 74, summary
    assert summary["releasedSourceVisualReferences"] >= 56, summary
    assert summary["invalidSourceMetadataReferences"] >= 18, summary
    print("MARROW_FAST_LANE_APPLY_OK", json.dumps(plan["outputSummary"], sort_keys=True))


if __name__ == "__main__":
    main()
