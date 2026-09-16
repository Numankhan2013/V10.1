#!/usr/bin/env python3
"""Source-level contracts for the Linux-only PrepLadder visual pipeline."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
generator = (ROOT / "tools/build_source_visual_metadata.py").read_text(encoding="utf-8")
audit = (ROOT / "tools/improve_source_visual_assets_v1.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/build-apk.yml").read_text(encoding="utf-8")
web = (ROOT / "tools/build_web_dist.py").read_text(encoding="utf-8")
renderer = (ROOT / "app/src/main/assets/source_visual_renderer.js").read_text(encoding="utf-8")
browser = (ROOT / "tools/verify_prepladder_visuals_browser.py").read_text(encoding="utf-8")

for forbidden in ("crop_native_figure", "Image.Resampling", "LANCZOS", "dominant_edge"):
    assert forbidden not in generator
    assert forbidden not in audit
for required in (
    "native-jpeg-byte-copy",
    "native-raster-lossless-png-full-frame",
    "pdf-region-288dpi",
    "source_visual_inventory.json",
    "sourceComparisonCrop",
    "questionId",
    "riskFlags",
    "crop_box(page,bbox,0)",
    "pad=72",
):
    assert required in generator, required
assert "if cache_key in asset_cache and asset_cache[cache_key] is not None" in generator
assert "if cache_key and visual is not None:asset_cache[cache_key]=dict(visual)" in generator
assert "if cache_key:asset_cache[cache_key]=visual" not in generator
for required in (
    "technicalChecks",
    "answer-revealing source text intersects visual crop",
    "detected text touches PDF-region boundary",
    "comparison-batch-",
    "PENDING_MANUAL_REVIEW",
    "prepladder_visual_reviews.json",
    "PDF-region safety canvas missing",
):
    assert required in audit or required in generator, required
for required in (
    "BY_QID",
    "activeSession",
    "questionId",
    "nk-v113-question",
    "Prep\\s*ladder\\s*X\\s*Qbank",
    "findVisual(card,qt.textContent||'')",
):
    assert required in renderer, required
for required in (
    "window.QB&&window.QB.getState",
    "activeSession",
    "session.questionIds[session.index]",
    "Stable PrepLadder owner mismatch",
):
    assert required in browser, required
assert "BY_ID" not in browser
assert workflow.index("build_source_visual_metadata.py") < workflow.index("improve_source_visual_assets_v1.py") < workflow.index("verify_source_visual_contract.py")
assert "verify_prepladder_visuals_browser.py" in workflow
assert "source_visuals').rglob" in web
print("PREPLADDER_VISUAL_PIPELINE_TEST_OK destructive_crops=0 inventory=true crop_safety=true review_batches=true offline=true browser=true stable_identity=true public_owner_check=true")
