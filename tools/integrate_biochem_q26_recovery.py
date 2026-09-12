#!/usr/bin/env python3
"""Fail-closed installer for Biochemistry Ch2 Q26 after direct source QA."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz

from marrow_images import DATA, validate, write_json

QUESTION_ID = "marrow__BIOCHEM_CH02_Q026"
REFERENCE_ID = QUESTION_ID + ":figure:1"
ASSET_ID = "biochemistry-22651a6eb0d53c78"
BATCH_ID = "NKQ_BIOCHEM_COVERAGE_Q26_20260912"
SOURCE_FILE = "biochemistryed8.pdf"
SOURCE_SHA = "463cb586aa18b702243d2467b4ad1f7fb24537d7ae73388607421516660643eb"
PAGE = 41
XREF = 92
EXCLUDED_XREF = 91
REGION = [162.0, 515.0, 450.0, 731.0]
EXPECTED_SHA = "22651a6eb0d53c783ebdaa8d967948ed3a88a2ef96669ed84c6788e18bf8645c"
WIDTH = 960
HEIGHT = 540
CHECKPOINT = DATA / "images/recovery_checkpoints/biochem_ch02_q026_20260912.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    source = DATA / "source_pdfs" / SOURCE_FILE
    assert source.is_file(), source
    assert source.stat().st_size == 7_958_177, "Authoritative Biochemistry PDF size drift"
    assert sha(source.read_bytes()) == SOURCE_SHA, "Authoritative Biochemistry PDF hash drift"

    cp = json.loads(CHECKPOINT.read_text())
    assert cp["status"] == "VISUAL_QA_PASS_PENDING_INTEGRATION"
    assert cp["canonicalBase"] == "72fa0b6a921015c2e35addaccf06c1949d938f35"
    assert cp["questionId"] == QUESTION_ID and cp["referenceId"] == REFERENCE_ID
    assert cp["role"] == "explanation" and cp["order"] == 1
    assert cp["source"]["page"] == PAGE
    assert cp["source"]["xref"] == XREF
    assert cp["source"]["excludedNeighborXref"] == EXCLUDED_XREF
    assert cp["source"]["region"] == REGION
    assert cp["candidate"]["method"] == "native-jpeg-stream"
    assert cp["candidate"]["sha256"] == EXPECTED_SHA
    for key in ("fullPageInspected", "nativeOriginalInspected", "phonePreviewInspected", "expandedPreviewInspected"):
        assert cp["sourceComparison"][key] is True

    doc = fitz.open(source)
    page = doc[PAGE - 1]
    rects = page.get_image_rects(XREF)
    assert len(rects) == 1, rects
    r = rects[0]
    actual_region = [round(r.x0, 3), round(r.y0, 3), round(r.x1, 3), round(r.y1, 3)]
    assert actual_region == REGION, actual_region
    excluded_rects = page.get_image_rects(EXCLUDED_XREF)
    assert excluded_rects, "Expected excluded neighboring xref 91 on page 41"

    info = doc.extract_image(XREF)
    payload = info["image"]
    assert info["width"] == WIDTH and info["height"] == HEIGHT, (info["width"], info["height"])
    assert info["ext"] in {"jpg", "jpeg"}, info["ext"]
    assert sha(payload) == EXPECTED_SHA, "Native Q26 JPEG digest drift"

    original_path = DATA / "images/originals" / f"{EXPECTED_SHA}.jpg"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    if original_path.exists():
        assert original_path.read_bytes() == payload, "Q26 original path conflict"
    else:
        original_path.write_bytes(payload)

    registry_path = DATA / "images/registry.json"
    value = json.loads(registry_path.read_text())
    assert value.get("schemaVersion") == 1

    competing = [
        (asset, binding)
        for asset in value["assets"]
        for binding in asset.get("bindings", [])
        if binding.get("questionId") == QUESTION_ID
        and binding.get("role") == "explanation"
        and binding.get("order") == 1
    ]
    assert not competing, "Q26 already has a competing explanation binding"
    assert all(a.get("id") != ASSET_ID for a in value["assets"])
    identical = [
        a for a in value["assets"]
        if (a.get("production") or {}).get("sha256") == EXPECTED_SHA
        or (a.get("original") or {}).get("sha256") == EXPECTED_SHA
    ]
    assert not identical, "Identical source bytes already exist; explicit reuse review required"

    notes = (
        "Direct source comparison of hash-verified Biochemistry ED8 page 41. Xref 92 is the 960x540 "
        "glycolysis/gluconeogenesis pathway located inside Solution to Question 26 and is the correct "
        "explanation-owned visual. Xref 91 is the separate pyruvate-carboxylase figure above the Q26 "
        "solution heading and is excluded. Native JPEG bytes preserve pathway boxes, enzyme labels, "
        "glycolysis/gluconeogenesis directionality and shared/reversible steps. No crop, reconstruction, "
        "generation, inpainting or sharpening was applied. Phone view is compact but usable with existing "
        "fullscreen zoom/pan; expanded view is readable."
    )
    evidence = (
        "automation runtime direct page/native/phone/expanded visual inspection on 2026-09-12; "
        "data/marrow/images/recovery_checkpoints/biochem_ch02_q026_20260912.json; "
        f"{SOURCE_FILE} sha256={SOURCE_SHA} size=7958177 page={PAGE} xref={XREF} "
        f"excluded_neighbor_xref={EXCLUDED_XREF} region={REGION}; native_sha256={EXPECTED_SHA}"
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
            "xref": XREF,
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
                "xref": XREF,
                "excludedNeighborXref": EXCLUDED_XREF,
                "region": REGION,
            },
            "qa": {"sourceCompared": True, "notes": notes, "evidence": evidence},
        }],
        "original": {
            "path": f"data/marrow/images/originals/{EXPECTED_SHA}.jpg",
            "sha256": EXPECTED_SHA,
            "width": WIDTH,
            "height": HEIGHT,
        },
        "production": {
            "path": f"data/marrow/images/originals/{EXPECTED_SHA}.jpg",
            "sha256": EXPECTED_SHA,
            "width": WIDTH,
            "height": HEIGHT,
        },
        "method": "native-jpeg-stream",
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
    print("BIOCHEM_Q26_INTEGRATED", ASSET_ID, EXPECTED_SHA)


if __name__ == "__main__":
    main()
