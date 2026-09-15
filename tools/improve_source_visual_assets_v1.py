#!/usr/bin/env python3
"""Audit PrepLadder visuals and emit bounded source/production review sheets.

Despite the historical filename, this stage is intentionally non-destructive:
it never crops, sharpens, resizes, or rewrites production visuals. Generation
is owned solely by build_source_visual_metadata.py.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import shutil

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
INVENTORY = ASSETS / "source_visual_inventory.json"
REVIEWS = ROOT / "data/prepladder_visual_reviews.json"
OUT = ROOT / "build/prepladder-visual-audit"
BATCH_SIZE = 8
ANSWER_REVEAL = re.compile(r"\b(correct\s+answer|answer\s+is|solution\s+for\s+question|explanation\s*:)", re.I)
QUESTION_START = re.compile(r"(?m)^\s*(\d{1,4})[.)]\s+")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_rect(value):
    return fitz.Rect(value["left"], value["top"], value["right"], value["bottom"])


def dark_edge_fraction(image: Image.Image) -> float:
    rgb = image.convert("RGB")
    width, height = rgb.size
    band = max(2, round(min(width, height) * 0.008))
    pixels = []
    pixels.extend(rgb.crop((0, 0, width, band)).getdata())
    pixels.extend(rgb.crop((0, height - band, width, height)).getdata())
    pixels.extend(rgb.crop((0, 0, band, height)).getdata())
    pixels.extend(rgb.crop((width - band, 0, width, height)).getdata())
    return sum(min(pixel) < 225 for pixel in pixels) / max(1, len(pixels))


def content_risk_metrics(image: Image.Image):
    sample = ImageOps.contain(image.convert("RGB"), (512, 512))
    gray = sample.convert("L")
    edge = gray.filter(ImageFilter.FIND_EDGES)
    edge_fraction = sum(count for value, count in enumerate(edge.histogram()) if value > 48) / max(1, edge.width * edge.height)
    light_fraction = sum(count for value, count in enumerate(gray.histogram()) if value > 232) / max(1, gray.width * gray.height)
    corners = [sample.getpixel(point) for point in ((0, 0), (sample.width - 1, 0), (0, sample.height - 1), (sample.width - 1, sample.height - 1))]
    background = tuple(round(sum(color[channel] for color in corners) / 4) for channel in range(3))
    difference = ImageChops.difference(sample, Image.new("RGB", sample.size, background)).convert("L")
    bbox = difference.point(lambda value: 255 if value > 18 else 0).getbbox()
    reduction = 0.0 if not bbox else 1 - ((bbox[2] - bbox[0]) * (bbox[3] - bbox[1])) / (sample.width * sample.height)
    return round(edge_fraction, 6), round(light_fraction, 6), round(reduction, 6)


def source_preview(document, item):
    page = document[int(item["sourcePage"]) - 1]
    clip = as_rect(item["sourceComparisonCrop"])
    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip, alpha=False)
    return Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)


def technical_checks(item, document):
    path = ASSETS / str(item.get("productionPath") or "")
    failures = []
    if not item.get("productionPath") or not path.is_file():
        return {"status": "FAIL", "failures": ["production asset missing"]}
    digest = sha256(path)
    if digest != item.get("productionSha256"):
        failures.append("production hash mismatch")
    with Image.open(path) as opened:
        image = opened.convert("RGB")
    width, height = image.size
    if [width, height] != [item.get("productionWidth"), item.get("productionHeight")]:
        failures.append("recorded dimensions mismatch")
    if width < 40 or height < 40:
        failures.append("unreadably small output")
    edge_density, light_fraction, legacy_reduction = content_risk_metrics(image)
    flags = list(item.get("riskFlags", []))
    if light_fraction > 0.40 and edge_density > 0.025:
        flags.append("possible-raster-text-or-linework")
    if legacy_reduction > 0.25:
        flags.append("legacy-crop-would-remove-25-percent")
    item["riskFlags"] = list(dict.fromkeys(flags))
    item["highRisk"] = bool(item["riskFlags"])
    item["contentRiskMetrics"] = {"edgeDensity": edge_density, "lightPixelFraction": light_fraction, "legacyCropReductionEstimate": legacy_reduction}

    method = item.get("extractionMethod")
    pad = int(item.get("safetyPadPixels") or 0)
    pad_x, pad_y = int(item.get("safetyPadX") or pad), int(item.get("safetyPadY") or pad)
    if method == "native-jpeg-byte-copy":
        if digest != item.get("sourceSha256"):
            failures.append("native JPEG bytes changed")
        boundary = "SAFE_COMPLETE_NATIVE_FRAME"
    elif method == "native-raster-lossless-png-full-frame":
        if min(pad_x, pad_y) < 12 or width <= pad_x * 2 or height <= pad_y * 2:
            failures.append("lossless raster safety canvas missing")
        else:
            inner = image.crop((pad_x, pad_y, width - pad_x, height - pad_y))
            if dark_edge_fraction(image) > 0.001:
                failures.append("meaningful pixels touch PNG safety boundary")
            if item.get("sourceXref") and not item.get("sourceSmask"):
                raw = document.extract_image(int(item["sourceXref"])).get("image") or b""
                try:
                    source = Image.open(__import__('io').BytesIO(raw)).convert("RGB")
                    if source.size != inner.size or source.tobytes() != inner.tobytes():
                        failures.append("native source pixels changed")
                except Exception:
                    failures.append("native source pixels could not be verified")
        boundary = "SAFE_PADDED_COMPLETE_NATIVE_FRAME"
    elif method == "pdf-region-288dpi":
        if min(pad_x, pad_y) < 32 or width <= pad_x * 2 or height <= pad_y * 2:
            failures.append("PDF-region safety canvas missing")
        elif dark_edge_fraction(image) > 0.001:
            failures.append("meaningful pixels touch PDF-region boundary")
        boundary = "SAFE_PADDED_PDF_REGION"
    else:
        failures.append("unsupported extraction method")
        boundary = "UNKNOWN"

    crop = as_rect(item["sourceComparisonCrop"])
    page = document[int(item["sourcePage"]) - 1]
    crop_text = page.get_text("text", clip=crop) or ""
    if method == "pdf-region-288dpi" and ANSWER_REVEAL.search(crop_text):
        failures.append("answer-revealing source text intersects visual crop")
    neighboring = sorted({int(number) for number in QUESTION_START.findall(crop_text) if method == "pdf-region-288dpi" and int(number) != int(item.get("questionNumber") or -1)})
    if neighboring:
        failures.append("neighboring question text intersects visual crop")
    touching_text = []
    if method == "pdf-region-288dpi":
        for word in page.get_text("words", clip=crop):
            rect = fitz.Rect(word[:4])
            if min(rect.x0 - crop.x0, rect.y0 - crop.y0, crop.x1 - rect.x1, crop.y1 - rect.y1) < 2:
                touching_text.append(str(word[4]))
        if touching_text:
            failures.append("detected text touches PDF-region boundary")

    source_ratio = float(item.get("sourceWidth") or 0) / max(1.0, float(item.get("sourceHeight") or 0))
    if method == "native-raster-lossless-png-full-frame" and pad:
        production_ratio = (width - 2 * pad_x) / max(1, height - 2 * pad_y)
    elif method == "pdf-region-288dpi":
        production_ratio = (width - 2 * pad_x) / max(1, height - 2 * pad_y)
        source_ratio = crop.width / max(1, crop.height)
    else:
        production_ratio = width / max(1, height)
    if source_ratio and abs(production_ratio / source_ratio - 1) > 0.015:
        failures.append("aspect ratio changed")
    return {
        "status": "FAIL" if failures else "PASS",
        "failures": failures,
        "boundarySafety": boundary,
        "darkEdgeFraction": round(dark_edge_fraction(image), 6),
        "detectedTextAtBoundary": touching_text,
        "answerRevealTextDetected": method == "pdf-region-288dpi" and bool(ANSWER_REVEAL.search(crop_text)),
        "neighboringQuestionNumbers": neighboring,
    }


def fit_panel(image, size=(760, 430)):
    panel = Image.new("RGB", size, "white")
    fitted = ImageOps.contain(image.convert("RGB"), (size[0] - 24, size[1] - 24))
    panel.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    return panel


def comparison_sheet(batch, documents, target):
    row_height, width = 500, 1560
    sheet = Image.new("RGB", (width, 54 + len(batch) * row_height), "#edf1f7")
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 18), "PrepLadder source PDF region / production visual", fill="#111827")
    for index, item in enumerate(batch):
        y = 54 + index * row_height
        source = source_preview(documents[item["sourcePdf"]], item)
        with Image.open(ASSETS / item["productionPath"]) as opened:
            production = opened.convert("RGB")
        sheet.paste(fit_panel(source), (10, y + 56))
        sheet.paste(fit_panel(production), (790, y + 56))
        label = f"{item['id']} | {item['subject']} | {item['questionId']} | PDF p{item['sourcePage']} | {item['extractionMethod']} | {item['technicalChecks']['status']}"
        draw.rectangle((10, y + 8, width - 10, y + 48), fill="white")
        draw.text((18, y + 20), label, fill="#111827")
        draw.text((18, y + 60), "SOURCE", fill="#334155")
        draw.text((798, y + 60), "PRODUCTION", fill="#334155")
    sheet.save(target, format="PNG", optimize=False)


def main():
    if not INVENTORY.is_file():
        raise SystemExit("source_visual_inventory.json missing; run the generator first")
    value = json.loads(INVENTORY.read_text(encoding="utf-8"))
    items = value.get("items", [])
    if len(items) < 10:
        raise SystemExit(f"Unexpected PrepLadder visual inventory size: {len(items)}")
    reviews = json.loads(REVIEWS.read_text(encoding="utf-8")) if REVIEWS.is_file() else {"schemaVersion": 1, "reviews": {}}
    if reviews.get("schemaVersion") != 1 or not isinstance(reviews.get("reviews"), dict):
        raise SystemExit("Invalid PrepLadder visual review registry")
    review_map = reviews["reviews"]
    orphaned = sorted(set(review_map) - {item["id"] for item in items})
    if orphaned:
        raise SystemExit(f"Orphaned PrepLadder visual reviews: {orphaned[:8]}")
    for item in items:
        review = review_map.get(item["id"])
        if not review:
            continue
        expected = {"questionId": item["questionId"], "sourcePdf": item["sourcePdf"], "sourcePage": item["sourcePage"], "productionSha256": item["productionSha256"], "sourceComparisonCrop": item["sourceComparisonCrop"]}
        if any(review.get(key) != expected_value for key, expected_value in expected.items()):
            raise SystemExit(f"Stale or mismatched PrepLadder visual review: {item['id']}")
        if review.get("status") != "PASS" or not str(review.get("notes") or "").strip():
            raise SystemExit(f"PrepLadder visual review is not releasable: {item['id']}")
        item["reviewStatus"] = "PASS"
        item["reviewNotes"] = review["notes"]
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    documents = {name: fitz.open(ASSETS / name) for name in sorted({item["sourcePdf"] for item in items})}
    try:
        for item in items:
            item["technicalChecks"] = technical_checks(item, documents[item["sourcePdf"]])
        ordered = sorted(items, key=lambda item: (not item.get("highRisk", False), item["subject"], item["sourcePage"], item["questionId"], item["id"]))
        batches = []
        for offset in range(0, len(ordered), BATCH_SIZE):
            batch = ordered[offset : offset + BATCH_SIZE]
            name = f"comparison-batch-{offset // BATCH_SIZE + 1:03d}.png"
            comparison_sheet(batch, documents, OUT / name)
            batches.append({"batch": offset // BATCH_SIZE + 1, "comparisonSheet": name, "highRiskFirst": any(item.get("highRisk") for item in batch), "visualIds": [item["id"] for item in batch]})
    finally:
        for document in documents.values():
            document.close()
    failures = [item for item in items if item["technicalChecks"]["status"] != "PASS"]
    value["items"] = items
    value["technicalSummary"] = {"total": len(items), "passed": len(items) - len(failures), "failed": len(failures), "highRisk": sum(bool(item.get("highRisk")) for item in items), "manualReviewPassed": sum(item.get("reviewStatus") == "PASS" for item in items), "manualReviewPending": sum(item.get("reviewStatus") != "PASS" for item in items)}
    value["reviewBatches"] = batches
    INVENTORY.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "audit.json").write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if failures:
        sample = "; ".join(f"{item['id']}:{','.join(item['technicalChecks']['failures'])}" for item in failures[:12])
        raise SystemExit(f"SOURCE_VISUAL_CROP_SAFETY_FAILED count={len(failures)} {sample}")
    print(f"SOURCE_VISUAL_QUALITY_OK total={len(items)} high_risk={value['technicalSummary']['highRisk']} destructive_crops=0 resampled_native_pixels=0 review_batches={len(batches)} manual_review_pending={len(items)}")


if __name__ == "__main__":
    main()
