#!/usr/bin/env python3
"""Fail-closed installer for Biochemistry Ch2 Q21 after fresh visual QA."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import fitz

from marrow_images import DATA, validate, write_json

QUESTION_ID = "marrow__BIOCHEM_CH02_Q021"
REFERENCE_ID = QUESTION_ID + ":figure:1"
ASSET_ID = "biochemistry-f2a6b0691fffcbe3"
BATCH_ID = "NKQ_BIOCHEM_COVERAGE_Q21_20260912_R2"
SOURCE_FILE = "biochemistryed8.pdf"
SOURCE_SHA = "463cb586aa18b702243d2467b4ad1f7fb24537d7ae73388607421516660643eb"
PAGE = 39
PRIMARY_XREF = 83
COMPOSITE_XREFS = [83, 84, 85]
EXCLUDED_XREF = 86
REGION = [161.491, 55.671, 450.509, 272.328]
DPI = 300
EXPECTED_SHA = "f2a6b0691fffcbe3756d9db58d2baf28c3254f54ede9de577071b7b244bdc789"
WIDTH = 1206
HEIGHT = 904
CHECKPOINT = DATA / "images/recovery_checkpoints/biochem_ch02_q021_20260912_r2.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render_exact(source: Path, destination: Path) -> None:
    doc = fitz.open(source)
    page = doc[PAGE - 1]
    pix = page.get_pixmap(
        matrix=fitz.Matrix(DPI / 72, DPI / 72),
        clip=fitz.Rect(*REGION),
        alpha=False,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    pix.save(destination)


def main() -> None:
    source = DATA / "source_pdfs" / SOURCE_FILE
    assert source.is_file(), source
    assert sha(source.read_bytes()) == SOURCE_SHA, "Authoritative Biochemistry PDF hash drift"

    cp = json.loads(CHECKPOINT.read_text())
    assert cp["status"] == "VISUAL_QA_PASS_PENDING_INTEGRATION"
    assert cp["canonicalBase"] == "d84a8093468c278a19e81e917bcc66da91f33574"
    assert cp["questionId"] == QUESTION_ID and cp["referenceId"] == REFERENCE_ID
    assert cp["source"]["page"] == PAGE
    assert cp["source"]["compositeXrefs"] == COMPOSITE_XREFS
    assert cp["source"]["excludedNeighborXref"] == EXCLUDED_XREF
    assert cp["source"]["region"] == REGION
    assert cp["candidate"]["sha256"] == EXPECTED_SHA
    for key in ("fullPageInspected", "exactRegionInspected", "phonePreviewInspected", "expandedPreviewInspected"):
        assert cp["sourceComparison"][key] is True

    original_path = DATA / "images/originals" / f"{EXPECTED_SHA}.png"
    render_exact(source, original_path)
    payload = original_path.read_bytes()
    assert sha(payload) == EXPECTED_SHA, "Fresh-reviewed deterministic Q21 render digest drift"

    try:
        from PIL import Image
        with Image.open(original_path) as image:
            assert image.size == (WIDTH, HEIGHT), image.size
    except ImportError:
        pass

    production_path = DATA / "images/production" / f"{EXPECTED_SHA}.png"
    production_path.parent.mkdir(parents=True, exist_ok=True)
    if production_path.exists():
        assert production_path.read_bytes() == payload, "Q21 production path conflict"
    else:
        shutil.copyfile(original_path, production_path)

    registry_path = DATA / "images/registry.json"
    value = json.loads(registry_path.read_text())
    assert value.get("schemaVersion") == 1

    q21_bindings = [
        (asset, binding)
        for asset in value["assets"]
        for binding in asset.get("bindings", [])
        if binding.get("questionId") == QUESTION_ID
        and binding.get("role") == "explanation"
        and binding.get("order") == 1
        and (binding.get("source") or asset.get("source") or {}).get("page") == PAGE
    ]
    assert not q21_bindings, "Q21 already has a competing explanation binding"
    assert all(a.get("id") != ASSET_ID for a in value["assets"])
    identical = [a for a in value["assets"] if (a.get("production") or {}).get("sha256") == EXPECTED_SHA]
    assert not identical, "Identical production bytes already exist; explicit reuse review required"

    notes = (
        "Fresh source comparison of Biochemistry ED8 page 39 Q21 composite. The exact region is owned by "
        "Solution to Question 21 and preserves the red glycolysis pathway, blue gluconeogenesis pathway, "
        "central metabolites, enzyme labels, directional/reversible arrows and regulatory annotations. "
        "Composite xrefs 83/84/85 are included; neighboring xref 86 belongs to Q22 and is excluded. "
        "The native 1206x904 render and expanded view are readable; the compact phone view remains usable "
        "with the existing fullscreen zoom/pan viewer. No reconstruction, generation, inpainting or medical-pixel alteration."
    )
    evidence = (
        "fresh QA workflow 34686576057 artifact 10295084510; "
        "data/marrow/images/recovery_checkpoints/biochem_ch02_q021_20260912_r2.json; "
        f"{SOURCE_FILE} sha256={SOURCE_SHA} page={PAGE} region={REGION} dpi={DPI} "
        f"composite_xrefs={COMPOSITE_XREFS} excluded_neighbor_xref={EXCLUDED_XREF}"
    )

    asset = {
        "id": ASSET_ID,
        "subject": "Biochemistry",
        "kind": "diagram",
        "reviewBatch": BATCH_ID,
        "source": {
            "file": SOURCE_FILE,
            "sha256": SOURCE_SHA,
            "page": PAGE,
            "xref": PRIMARY_XREF,
            "compositeXrefs": COMPOSITE_XREFS,
            "excludedNeighborXref": EXCLUDED_XREF,
            "region": REGION,
        },
        "bindings": [{
            "questionId": QUESTION_ID,
            "role": "explanation",
            "order": 1,
            "alt": "Glycolysis and gluconeogenesis pathway",
            "status": "PASS",
            "reviewBatch": BATCH_ID,
            "source": {
                "page": PAGE,
                "xref": PRIMARY_XREF,
                "compositeXrefs": COMPOSITE_XREFS,
                "excludedNeighborXref": EXCLUDED_XREF,
                "region": REGION,
            },
            "qa": {"sourceCompared": True, "notes": notes, "evidence": evidence},
        }],
        "original": {
            "path": f"data/marrow/images/originals/{EXPECTED_SHA}.png",
            "sha256": EXPECTED_SHA,
            "width": WIDTH,
            "height": HEIGHT,
        },
        "production": {
            "path": f"data/marrow/images/production/{EXPECTED_SHA}.png",
            "sha256": EXPECTED_SHA,
            "width": WIDTH,
            "height": HEIGHT,
        },
        "method": "region-render",
        "status": "PASS",
        "qa": {
            "sourceCompared": True,
            "notes": notes,
            "evidence": evidence,
            "originalSha256": EXPECTED_SHA,
            "productionSha256": EXPECTED_SHA,
        },
    }
    value["assets"].append(asset)
    write_json(registry_path, value)
    validate(registry_path)

    cp["status"] = "STATIC_VALIDATED"
    cp["candidate"]["learnerFacing"] = True
    cp["registryAssetId"] = ASSET_ID
    cp["nextAction"] = "Regenerate release/progress/coverage, update memory with the next deterministic reference, run exact-head product gates, then reconcile into canonical."
    write_json(CHECKPOINT, cp)
    print("BIOCHEM_Q21_R2_INTEGRATED", ASSET_ID, EXPECTED_SHA)


if __name__ == "__main__":
    main()
