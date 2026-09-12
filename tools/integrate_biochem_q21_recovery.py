#!/usr/bin/env python3
"""One-purpose, fail-closed installer for Biochemistry Ch2 Q21 source figure."""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import shutil

from PIL import Image
import fitz

from marrow_images import DATA, ROOT, sha, validate, write_json

QUESTION_ID = "marrow__BIOCHEM_CH02_Q021"
REFERENCE_ID = QUESTION_ID + ":figure:1"
ASSET_ID = "biochemistry-07082b9d273f1088"
BATCH_ID = "NKQ_BIOCHEM_COVERAGE_Q21_20260912"
SOURCE_FILE = "biochemistryed8.pdf"
SOURCE_SHA = "463cb586aa18b702243d2467b4ad1f7fb24537d7ae73388607421516660643eb"
PAGE = 39
PRIMARY_XREF = 83
COMPOSITE_XREFS = [83, 84, 85]
EXCLUDED_XREF = 86
REGION = [161.491, 55.671, 450.509, 272.328]
DPI = 300
EXPECTED_SHA = "07082b9d273f10881d05557827fff479dd18ed450f2ae874aa51bc460a7b03a4"
WIDTH = 1206
HEIGHT = 904


def exact_reviewed_png(source: Path) -> bytes:
    """Reproduce the previously inspected losslessly optimized region render."""
    with fitz.open(source) as document:
        assert 1 <= PAGE <= len(document)
        page = document[PAGE - 1]
        assert page.rotation == 0
        rect = fitz.Rect(REGION)
        assert page.rect.contains(rect)
        raw = page.get_pixmap(matrix=fitz.Matrix(DPI / 72, DPI / 72), clip=rect, alpha=False).tobytes("png")
    image = Image.open(BytesIO(raw))
    assert image.size == (WIDTH, HEIGHT), image.size
    out = BytesIO()
    image.save(out, format="PNG", optimize=True)
    optimized = out.getvalue()
    assert sha(optimized) == EXPECTED_SHA, (
        "Lossless optimized Q21 PNG digest drift; do not substitute a new unreviewed encoding: "
        + sha(optimized)
    )
    return optimized


def main() -> None:
    source = DATA / "source_pdfs" / SOURCE_FILE
    assert source.is_file(), source
    assert sha(source.read_bytes()) == SOURCE_SHA, "Authoritative Biochemistry PDF hash drift"

    checkpoint = DATA / "images/recovery_checkpoints/biochem_ch02_q021_20260912.json"
    cp = json.loads(checkpoint.read_text())
    assert cp["status"] == "CURRENT_UNFINISHED"
    assert cp["questionId"] == QUESTION_ID and cp["referenceId"] == REFERENCE_ID
    assert cp["source"]["page"] == PAGE
    assert cp["source"]["compositeXrefs"] == COMPOSITE_XREFS
    assert cp["source"]["excludedNeighborXref"] == EXCLUDED_XREF
    assert cp["source"]["region"] == REGION
    assert cp["candidate"]["sha256"] == EXPECTED_SHA
    assert cp["sourceComparison"]["fullPageInspected"] is True
    assert cp["sourceComparison"]["exactRegionInspected"] is True
    assert cp["sourceComparison"]["phonePreviewInspected"] is True
    assert cp["sourceComparison"]["expandedPreviewInspected"] is True

    png = exact_reviewed_png(source)
    original_path = DATA / "images/originals" / f"{EXPECTED_SHA}.png"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    if original_path.exists():
        assert original_path.read_bytes() == png, "Immutable original conflict"
    else:
        original_path.write_bytes(png)

    production_path = DATA / "images/production" / f"{EXPECTED_SHA}.png"
    production_path.parent.mkdir(parents=True, exist_ok=True)
    if production_path.exists():
        assert production_path.read_bytes() == png, "Production conflict"
    else:
        production_path.write_bytes(png)

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
        and (binding.get("source") or {}).get("page") == PAGE
    ]
    if q21_bindings:
        assert len(q21_bindings) == 1
        asset, binding = q21_bindings[0]
        assert asset["id"] == ASSET_ID, "Q21 already belongs to a different asset"
        assert asset.get("production", {}).get("sha256") == EXPECTED_SHA
        assert binding.get("status") == "PASS"
        print("BIOCHEM_Q21_RECOVERY_ALREADY_INTEGRATED", ASSET_ID)
        return

    identical = [a for a in value["assets"] if (a.get("production") or {}).get("sha256") == EXPECTED_SHA]
    assert not identical, "Identical Q21 production asset already exists; review reuse explicitly"
    assert all(a.get("id") != ASSET_ID for a in value["assets"])

    record = {
        "path": f"data/marrow/images/originals/{EXPECTED_SHA}.png",
        "sha256": EXPECTED_SHA,
        "width": WIDTH,
        "height": HEIGHT,
    }
    production = {
        "path": f"data/marrow/images/production/{EXPECTED_SHA}.png",
        "sha256": EXPECTED_SHA,
        "width": WIDTH,
        "height": HEIGHT,
    }
    notes = (
        "Source-compared Biochemistry ED8 page 39 Q21 composite. Exact 300-DPI region contains "
        "the red glycolysis pathway, blue gluconeogenesis pathway, central intermediates, "
        "lactate/TCA connections and ATP/NADH/regulatory annotations. Composite xrefs 83/84/85 "
        "are inside Q21; neighboring xref 86 belongs to Q22 and is excluded. No reconstruction, "
        "generation, inpainting or medical-pixel alteration."
    )
    evidence = (
        "data/marrow/images/recovery_checkpoints/biochem_ch02_q021_20260912.json; "
        f"{SOURCE_FILE} sha256={SOURCE_SHA} page={PAGE} region={REGION} dpi={DPI} "
        f"composite_xrefs={COMPOSITE_XREFS} excluded_neighbor_xref={EXCLUDED_XREF}"
    )

    value["assets"].append({
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
        "original": record,
        "production": production,
        "method": "region-render",
        "status": "PASS",
        "qa": {
            "sourceCompared": True,
            "notes": notes,
            "evidence": evidence,
            "originalSha256": EXPECTED_SHA,
            "productionSha256": EXPECTED_SHA,
        },
    })
    write_json(registry_path, value)
    validate(registry_path)

    cp["status"] = "STATIC_VALIDATED"
    cp["candidate"]["learnerFacing"] = True
    cp["registryAssetId"] = ASSET_ID
    cp["blocker"] = None
    cp["nextAction"] = (
        "Regenerate progress/coverage/runtime release, run all image/browser/PWA/APK/package gates, "
        "then reconcile this exact verified batch into feature/marrow-canonical-full-current before releasing the image lane."
    )
    write_json(checkpoint, cp)
    print("BIOCHEM_Q21_RECOVERY_INTEGRATED", ASSET_ID, EXPECTED_SHA)


if __name__ == "__main__":
    main()
