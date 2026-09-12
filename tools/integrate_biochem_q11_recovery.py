#!/usr/bin/env python3
"""Fail-closed installer for Biochemistry Ch4 Q11 corrected galactose figure."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz

from marrow_images import DATA, validate, write_json

QUESTION_ID = "marrow__BIOCHEM_CH04_Q011"
REFERENCE_ID = QUESTION_ID + ":figure:1"
ASSET_ID = "biochemistry-e302242457457cdc"
WRONG_ASSET_ID = "biochemistry-bb781d8346ed1c36"
BATCH_ID = "NKQ_BIOCHEM_COVERAGE_Q11_20260912"
SOURCE_FILE = "biochemistryed8.pdf"
SOURCE_SHA = "463cb586aa18b702243d2467b4ad1f7fb24537d7ae73388607421516660643eb"
METADATA_PAGE = 69
CORRECT_PAGE = 70
WRONG_XREF = 1146
CORRECT_XREF = 162
REGION = [162.0, 56.0, 450.0, 272.0]
WRONG_SHA = "bb781d8346ed1c3677ac8faf3a5a54501d09f583509a91d1aa0d7ecf9d1198d4"
EXPECTED_SHA = "e302242457457cdcabcca8ced492809b2f1947c049b719ff49a0be6bd6a222f6"
WIDTH = 600
HEIGHT = 451
CHECKPOINT = DATA / "images/recovery_checkpoints/biochem_ch04_q011_20260912.json"
ADJUDICATIONS = DATA / "images/source_reference_adjudications.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rounded_rect(rect):
    return [round(rect.x0, 3), round(rect.y0, 3), round(rect.x1, 3), round(rect.y1, 3)]


def main() -> None:
    source = DATA / "source_pdfs" / SOURCE_FILE
    assert source.is_file(), source
    assert source.stat().st_size == 7_958_177, "Authoritative Biochemistry PDF size drift"
    assert sha(source.read_bytes()) == SOURCE_SHA, "Authoritative Biochemistry PDF hash drift"

    doc = fitz.open(source)
    page69 = doc[METADATA_PAGE - 1]
    page70 = doc[CORRECT_PAGE - 1]

    wrong_rects = page69.get_image_rects(WRONG_XREF)
    assert len(wrong_rects) == 1, wrong_rects
    assert rounded_rect(wrong_rects[0]) == REGION, rounded_rect(wrong_rects[0])
    wrong = doc.extract_image(WRONG_XREF)
    assert wrong["width"] == 600 and wrong["height"] == 451
    assert sha(wrong["image"]) == WRONG_SHA, "Page-69 fructose figure drift"

    correct_rects = page70.get_image_rects(CORRECT_XREF)
    assert len(correct_rects) == 1, correct_rects
    assert rounded_rect(correct_rects[0]) == REGION, rounded_rect(correct_rects[0])
    info = doc.extract_image(CORRECT_XREF)
    payload = info["image"]
    assert info["width"] == WIDTH and info["height"] == HEIGHT, (info["width"], info["height"])
    assert info["ext"] in {"jpg", "jpeg"}, info["ext"]
    assert sha(payload) == EXPECTED_SHA, "Native Q11 galactose JPEG digest drift"

    # Page ownership evidence: Q11 begins on page 69 and explicitly points to a
    # galactose flowchart below; page 70 contains the standalone galactose pathway.
    page69_text = page69.get_text("text")
    page70_text = page70.get_text("text")
    assert "Solution to Question 11" in page69_text
    assert "galactose" in page69_text.lower()
    assert "Metabolism of galactose" in page70_text

    original_path = DATA / "images/originals" / f"{EXPECTED_SHA}.jpg"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    if original_path.exists():
        assert original_path.read_bytes() == payload, "Q11 original path conflict"
    else:
        original_path.write_bytes(payload)

    registry_path = DATA / "images/registry.json"
    value = json.loads(registry_path.read_text())
    assert value.get("schemaVersion") == 1

    wrong_assets = [a for a in value["assets"] if a.get("id") == WRONG_ASSET_ID]
    assert len(wrong_assets) == 1, "Expected tracked fructose asset"
    rejected = [
        b for b in wrong_assets[0].get("bindings", [])
        if b.get("questionId") == QUESTION_ID
        and b.get("role") == "explanation"
        and b.get("order") == 1
        and b.get("status") == "REJECTED"
    ]
    assert len(rejected) == 1, "Expected preserved rejected Q11/fructose binding"
    rejected_source = rejected[0].get("source") or wrong_assets[0].get("source") or {}
    assert rejected_source.get("page") == METADATA_PAGE

    released_competing = [
        (asset, binding)
        for asset in value["assets"]
        for binding in asset.get("bindings", [])
        if binding.get("questionId") == QUESTION_ID
        and binding.get("role") == "explanation"
        and binding.get("order") == 1
        and binding.get("status", asset.get("status")) in {"PASS", "SOURCE_LIMITED"}
    ]
    assert not released_competing, "Q11 already has a releasable explanation binding"
    assert all(a.get("id") != ASSET_ID for a in value["assets"])
    identical = [
        a for a in value["assets"]
        if (a.get("production") or {}).get("sha256") == EXPECTED_SHA
        or (a.get("original") or {}).get("sha256") == EXPECTED_SHA
    ]
    assert not identical, "Identical source bytes already exist; explicit reuse review required"

    notes = (
        "Direct source comparison of hash-verified Biochemistry ED8 pages 69-70. The only native figure "
        "on page 69 is the fructose-metabolism pathway (xref 1146), which is already correctly rejected "
        "for Q11. Q11's explanation states that the flowchart below depicts galactose metabolism, and "
        "the immediately following page 70 contains the standalone 'Metabolism of galactose' figure as "
        "native xref 162. The recovered 600x451 JPEG preserves Galactose, Galactose-1-phosphate, UDP "
        "glucose/UDP galactose, galactokinase, GALT, epimerase, lactose/complex-carbohydrate branches, "
        "and classical/non-classical galactosemia annotations. Native JPEG bytes are retained exactly; "
        "no crop, reconstruction, generation, inpainting, sharpening, or invented medical detail."
    )
    evidence = (
        "automation runtime direct full-page/native inspection on 2026-09-12; "
        f"{SOURCE_FILE} sha256={SOURCE_SHA} size=7958177; metadata_page={METADATA_PAGE} "
        f"wrong_xref={WRONG_XREF} wrong_sha={WRONG_SHA}; correct_page={CORRECT_PAGE} "
        f"correct_xref={CORRECT_XREF} region={REGION}; native_sha256={EXPECTED_SHA}"
    )

    asset = {
        "id": ASSET_ID,
        "subject": "Biochemistry",
        "kind": "diagram",
        "reviewBatch": BATCH_ID,
        "source": {
            "file": SOURCE_FILE,
            "sha256": SOURCE_SHA,
            "page": CORRECT_PAGE,
            "xref": CORRECT_XREF,
            "region": REGION,
            "sourceMetadataCorrection": {
                "referenceId": REFERENCE_ID,
                "recordedPage": METADATA_PAGE,
                "correctPage": CORRECT_PAGE,
                "reason": "Figure continues onto the next authoritative page; page 69 candidate is fructose metabolism."
            },
        },
        "bindings": [{
            "questionId": QUESTION_ID,
            "role": "explanation",
            "order": 1,
            "alt": "Galactose metabolism pathway",
            "status": "PASS",
            "reviewBatch": BATCH_ID,
            "source": {
                "page": CORRECT_PAGE,
                "xref": CORRECT_XREF,
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

    adjudications = json.loads(ADJUDICATIONS.read_text())
    assert adjudications.get("schemaVersion") == 1
    assert not any(e.get("id") == REFERENCE_ID for e in adjudications.get("entries", []))
    adjudications["entries"].append({
        "id": REFERENCE_ID,
        "questionId": QUESTION_ID,
        "subject": "Biochemistry",
        "role": "explanation",
        "sourcePages": [METADATA_PAGE],
        "status": "SOURCE_METADATA_INVALID",
        "source": {"file": SOURCE_FILE, "sha256": SOURCE_SHA},
        "reason": (
            "Canonical source metadata records Q11's galactose-metabolism figure on page 69. Direct "
            "inspection proves page 69's only native educational figure is the fructose pathway; the "
            "Q11 explanation continues to the correct galactose-metabolism figure on authoritative page 70."
        ),
        "evidence": (
            "2026-09-12 coverage recovery: hash-verified ED8 pages 69-70 inspected together. Page 69 "
            "contains Solution to Question 11 and explicitly says the flowchart below depicts galactose "
            "metabolism; xref 1146 on page 69 is fructose metabolism and remains REJECTED for Q11. "
            "Page 70 contains native xref 162 titled Metabolism of galactose, SHA-256 " + EXPECTED_SHA + "."
        ),
    })
    write_json(ADJUDICATIONS, adjudications)

    checkpoint = {
        "status": "STATIC_VALIDATED",
        "batchId": BATCH_ID,
        "questionId": QUESTION_ID,
        "referenceId": REFERENCE_ID,
        "role": "explanation",
        "order": 1,
        "source": {
            "file": SOURCE_FILE,
            "sha256": SOURCE_SHA,
            "recordedPage": METADATA_PAGE,
            "correctPage": CORRECT_PAGE,
            "wrongXref": WRONG_XREF,
            "correctXref": CORRECT_XREF,
            "region": REGION,
        },
        "asset": {"id": ASSET_ID, "sha256": EXPECTED_SHA, "width": WIDTH, "height": HEIGHT},
        "method": "native-jpeg-stream",
        "qa": {
            "fullPagesInspected": [METADATA_PAGE, CORRECT_PAGE],
            "nativeOriginalInspected": True,
            "sourceCompared": True,
            "answerSafe": True,
            "notes": notes,
            "evidence": evidence,
        },
    }
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    write_json(CHECKPOINT, checkpoint)
    print("BIOCHEM_Q11_RECOVERY_STATIC_PASS", ASSET_ID, EXPECTED_SHA)


if __name__ == "__main__":
    main()
