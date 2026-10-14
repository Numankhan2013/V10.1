#!/usr/bin/env python3
"""Microbiology Marrow figures: inventory, validation and app release.

The figures are the crops named in the Microbiology JSONL (`images[]`, each with
its source page and bounding box in data/marrow/source_pdfs/Microbiology Marrow
Qbank.pdf). Files live in data/marrow/microbiology/visuals/<image_id>.jpg and
are listed in data/marrow/microbiology/visuals.json with their hash, size and
question binding. Crop quality is not yet reviewed (`review: "pending"`); the
image lane fixes crops later by replacing a file and re-running `inventory`.

Release copies each figure to app/src/main/assets/marrow_visuals/<sha256>.jpg
(the same content-addressed folder the offline cache already covers) and writes
app/src/main/assets/microbiology_visual_metadata.js, which adds the bindings to
window.MARROW_VISUALS so the existing figure renderer and viewer show them. The
ED8 image registry and its package checks are untouched.

  python3 tools/microbiology_visuals.py inventory   # rewrite visuals.json from the JSONL + files
  python3 tools/microbiology_visuals.py validate
  python3 tools/microbiology_visuals.py release
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MICRO = ROOT / "data/marrow/microbiology"
FILES = MICRO / "visuals"
MANIFEST = MICRO / "visuals.json"
ASSETS = ROOT / "app/src/main/assets"
RUNTIME = ASSETS / "microbiology_visual_metadata.js"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jpeg_size(data: bytes) -> tuple[int, int]:
    """Width/height from a baseline or progressive JPEG header (no Pillow needed)."""
    assert data[:2] == b"\xff\xd8", "not a JPEG"
    i = 2
    while i < len(data):
        assert data[i] == 0xFF, "corrupt JPEG marker"
        marker = data[i + 1]
        length = int.from_bytes(data[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + length
    raise AssertionError("JPEG size not found")


def source_images() -> list[tuple[dict, dict]]:
    rows = []
    for path in sorted((MICRO / "source").glob("Microbiology_Marrow_Qbank_*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                q = json.loads(line)
                rows.extend((q, image) for image in q.get("images") or [])
    return rows


def question_ids() -> dict[str, str]:
    """MCQ ID -> namespaced app question ID, from the built bank."""
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from marrow_bank_data import load_sharded, MICROBIOLOGY_PREFIX
    bank = load_sharded(MICROBIOLOGY_PREFIX)
    return {q["mcqId"]: q["id"] for q in bank["questions"]}


def inventory() -> None:
    previous = {}
    if MANIFEST.exists():
        previous = {f["imageId"]: f for f in json.loads(MANIFEST.read_text(encoding="utf-8"))["figures"]}
    ids = question_ids()
    figures = []
    order: dict[tuple[str, str], int] = {}
    for q, image in source_images():
        image_id = image["image_id"]
        path = FILES / f"{image_id}.jpg"
        assert path.exists(), f"missing figure file {path.relative_to(ROOT)}"
        data = path.read_bytes()
        width, height = jpeg_size(data)
        role = "question" if image.get("location") == "question_stem" else "explanation"
        key = (q["id"], role)
        order[key] = order.get(key, 0) + 1
        old = previous.get(image_id, {})
        figures.append({
            "imageId": image_id,
            "questionId": ids[q["id"]],
            "mcqId": q["id"],
            "role": role,
            "order": order[key],
            "alt": str(image.get("caption") or "Source figure").strip(),
            "file": path.relative_to(ROOT).as_posix(),
            "sha256": sha(data),
            "width": width,
            "height": height,
            "sourcePage": image.get("source_page"),
            "boundingBox": image.get("bounding_box"),
            "origin": old.get("origin", "model-extracted crop"),
            "review": old.get("review", "pending") if old.get("sha256") == sha(data) else "pending",
        })
    value = {
        "schemaVersion": 1,
        "subject": "Microbiology",
        "sourcePdf": "data/marrow/source_pdfs/Microbiology Marrow Qbank.pdf",
        "note": "Crops follow the JSONL bounding boxes on the source PDF pages; crop quality review is pending.",
        "figures": figures,
    }
    MANIFEST.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MICROBIOLOGY_VISUALS_INVENTORY_OK figures={len(figures)}")


def validate() -> dict:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert value["schemaVersion"] == 1 and value["subject"] == "Microbiology"
    ids = set(question_ids().values())
    expected = {image["image_id"] for _, image in source_images()}
    seen = set()
    for figure in value["figures"]:
        assert figure["imageId"] not in seen, figure["imageId"]
        seen.add(figure["imageId"])
        assert figure["questionId"] in ids, figure["questionId"]
        assert figure["role"] in {"question", "explanation"}
        assert isinstance(figure["order"], int) and figure["order"] >= 1
        data = (ROOT / figure["file"]).read_bytes()
        assert sha(data) == figure["sha256"], f"figure changed since inventory: {figure['imageId']}"
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
    assert seen == expected, f"figures differ from JSONL images: missing={sorted(expected - seen)} extra={sorted(seen - expected)}"
    return value


def release() -> None:
    value = validate()
    runtime: dict[str, list[dict]] = {}
    for figure in value["figures"]:
        rel = f"marrow_visuals/{figure['sha256']}.jpg"
        target = ASSETS / rel
        data = (ROOT / figure["file"]).read_bytes()
        if target.exists():
            assert target.read_bytes() == data, f"content-addressed figure conflict: {rel}"
        else:
            target.write_bytes(data)
        runtime.setdefault(figure["questionId"], []).append({
            "id": f"microbiology-{figure['imageId']}", "role": figure["role"], "order": figure["order"],
            "src": rel, "alt": figure["alt"], "status": "PASS",
            "width": figure["width"], "height": figure["height"],
        })
    for rows in runtime.values():
        rows.sort(key=lambda r: (r["role"], r["order"], r["id"]))
    payload = json.dumps(runtime, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    RUNTIME.write_text(
        "/* Microbiology Marrow figures (generated by tools/microbiology_visuals.py). */\n"
        f"window.MARROW_VISUALS=Object.assign(window.MARROW_VISUALS||{{}},{payload});\n",
        encoding="utf-8",
    )
    print(f"MICROBIOLOGY_VISUALS_RELEASE_OK questions={len(runtime)} figures={len(value['figures'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["inventory", "validate", "release"])
    command = parser.parse_args().command
    if command == "inventory":
        inventory()
    elif command == "validate":
        validate()
        print("MICROBIOLOGY_VISUALS_OK")
    else:
        release()


if __name__ == "__main__":
    main()
