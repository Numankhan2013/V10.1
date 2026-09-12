#!/usr/bin/env python3
"""Fail the build when a protected NK QBank product contract regresses."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
MAIN = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"
ASSETS = ROOT / "app/src/main/assets"


def require(text: str, markers: list[str], scope: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{scope}: missing protected markers: {missing}")


def check_javascript(html: str) -> int:
    scripts = re.findall(r"<script(?:[^>]*)>(.*?)</script>", html, re.S | re.I)
    with tempfile.TemporaryDirectory() as td:
        checked = 0
        for index, source in enumerate(scripts):
            if not source.strip():
                continue
            path = Path(td) / f"inline_{index}.js"
            path.write_text(source, encoding="utf-8")
            subprocess.run(["node", "--check", str(path)], check=True)
            checked += 1
    return checked


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("source", "generated", "packaged"), default="source")
    parser.add_argument("--html", type=Path, default=HTML)
    args = parser.parse_args()

    html_path = args.html if args.html.is_absolute() else ROOT / args.html
    html = html_path.read_text(encoding="utf-8")
    native = MAIN.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")

    require(html, [
        ".bottom-nav", ".navigator", ".question-shell", ".question-card",
        ".question-text", ".option-list", ".feedback", ".q-footer",
        "localStorage", "activeSession",
    ], "source contract")
    require(manifest, ['android:label="NK QBank"', 'android:usesCleartextTraffic="false"', 'android.permission.INTERNET'], "Android manifest")
    require(native, ["setJavaScriptEnabled(true)", "setDomStorageEnabled(true)",
                     "setAllowContentAccess(false)", "MIXED_CONTENT_NEVER_ALLOW", "APP_ORIGIN", "serveAppAsset", "qbank_origin_migration_v1"], "WebView contract")

    for asset in (
        "Biochemistry_QBank_Source.pdf", "Physiology_QBank_Source.pdf",
        "Anatomy_QBank_Source.pdf",
    ):
        path = ASSETS / asset
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"Missing or empty protected source asset: {asset}")

    bottom_navs = re.findall(
        r'<[^>]+class=["\'][^"\']*\bbottom-nav\b[^"\']*["\'][^>]*>', html
    )
    if len(bottom_navs) > 1:
        raise SystemExit(f"Duplicate persistent navigation detected: {len(bottom_navs)} bottom-nav containers")

    if args.stage in {"generated", "packaged"}:
        forbidden = [
            'id="v102-streak-layer-script"', 'id="v102-streak-layer"',
            "home_polish_v3.js",
            'id="v102-practice-layer-script"', "v102-practice-submit-hidden",
        ]
        present = [marker for marker in forbidden if marker in html]
        if present:
            raise SystemExit(f"Forbidden generated-app regression markers present: {present}")
        require(html, [
            "SOURCE_PDF_EXPLANATION_V18", "BIOCHEM_SOURCE_SOLUTIONS",
            "SUBJECT_SOURCE_SOLUTIONS", "NK_SOURCE_VISUALS_V11",
            "qbank-question-ui-v2", "nk-home-v4", "NK_HOME_V5_FIXES",
            "nk-home-streak-header-v1", "nk-home-actions-v1",
            "nk-session-review", "nk-cbt-review-footer-v1",
            "nk-review-solution-grid-style", 'id="cr-grid"',
            "qb-nav-submit",
            "window.QB.openQuestionNavigator()", "Continue Practice",
            "Full Question Bank", "nk-custom-study-modules-v1",
            "nk-home-command-center-v1", "Question Source",
            "NK_CONTINUE_PRACTICE_RESUME_V1_START", "nk-practice-session-controls",
            "nkPausePractice", "nkSubmitPracticeSession", "sessionQuestionIds", "practiceContext",
            "openStudyModuleBuilder", "nkSelectModuleQuestionIds",
            "route.page==='module-builder'", "studyModules: []",
            "nkSyncModuleFromSession",
            "NK_QUESTION_CONTENT_HYGIENE_V1_START", "nkCleanQuestionStem",
            "nkTableTakeaway", "NK_CROSS_DEVICE_SYNC_V1_START",
            "nkCloudAccountCard", "manifest.webmanifest", "web_pdf_renderer.mjs",
            "NK_MARROW_BANK_PILOT_V1_START", "function nkRenderMarrowExplanation(q)",
            "qbank_active_bank_v1", "marrow__ANAT_CH01_Q001",
        ], f"{args.stage} contract")

    checked = check_javascript(html)
    print(
        f"PRODUCT_CONTRACT_OK stage={args.stage} scripts={checked} "
        f"bottom_nav={len(bottom_navs)}"
    )


if __name__ == "__main__":
    main()
