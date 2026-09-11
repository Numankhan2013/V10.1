#!/usr/bin/env python3
"""Run the shared Marrow browser suite, then verify current explanation rollouts by stable IDs."""
from __future__ import annotations

import importlib.util
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "_verify_marrow_bank_browser_base.py"
spec = importlib.util.spec_from_file_location("_marrow_browser_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit("Unable to load Marrow browser base")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.main()

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "build/web"
OUT = ROOT / "build/marrow-ui-checks"
OUT.mkdir(parents=True, exist_ok=True)

handler = lambda *a, **k: base.Quiet(*a, directory=str(WEB), **k)
with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Current Anatomy rollout regression retained unchanged.
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.route(
            "**/*.pdf*",
            lambda route: route.fulfill(
                path=str(ROOT / "app/src/main/assets/Anatomy_QBank_Source.pdf"),
                content_type="application/pdf",
                headers={"Access-Control-Allow-Origin": "*"},
            ) if "anatomy" in route.request.url.lower() else route.continue_(),
        )
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
        page.locator("button.nk-subject-row").filter(has_text="Anatomy").click()
        page.wait_for_timeout(80)
        if "#banks/Anatomy" not in page.url:
            raise SystemExit(f"Anatomy did not open bank selector: {page.url}")
        page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
        page.wait_for_timeout(100)
        if page.locator("button.nk-topic-row").count() != 48:
            raise SystemExit("Marrow Anatomy topic count is not 48")
        chapter = page.locator("button.nk-topic-row[onclick=\"window.QB.openChapter('5')\"]")
        if chapter.count() != 1:
            raise SystemExit(f"Stable Anatomy Chapter 5 selector count: {chapter.count()}")
        chapter.click()
        page.wait_for_timeout(80)
        rows = page.locator("button.nk-library-row")
        if rows.count() != 24:
            raise SystemExit(f"Marrow Anatomy Chapter 5 count is not 24: {rows.count()}")
        rows.nth(8).click()
        page.wait_for_timeout(80)
        if "mandibular nerve injury" not in page.locator(".question-text").inner_text().lower():
            raise SystemExit("Anatomy Chapter 5 Q9 did not open by stable source order")
        page.locator(".option-list button").first.click()
        page.wait_for_timeout(120)
        support = page.locator(".nk-study-support").inner_text().lower()
        for required in (
            "key takeaway",
            "detailed explanation",
            "structured text",
            "why the other options are wrong",
            "mandibular division (v3)",
            "tensor tympani",
            "stylopharyngeus",
        ):
            if required not in support:
                raise SystemExit(f"Anatomy Chapter 5 Q9 explanation missing {required}")
        if page.locator(".nk-gold-wrong-row").count() != 3:
            raise SystemExit("Anatomy Chapter 5 Q9 must render exactly three distractor rationales")
        if page.locator(".nk-marrow-table").count() < 1:
            raise SystemExit("Anatomy Chapter 5 Q9 source table was not preserved")
        page.screenshot(path=str(OUT / "anatomy-ch05-q09-arch-muscle-table.png"), full_page=True)
        if errors:
            raise SystemExit("Anatomy Chapter 5 browser errors: " + " | ".join(errors))
        page.close()

        # Physiology Chapter 10 Q13: reconstruction-sensitive autonomic exception.
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
        page.locator("button.nk-subject-row").filter(has_text="Physiology").click()
        page.wait_for_timeout(80)
        if "#banks/Physiology" not in page.url:
            raise SystemExit(f"Physiology did not open bank selector: {page.url}")
        page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
        page.wait_for_timeout(100)
        if page.locator("button.nk-topic-row").count() != 33:
            raise SystemExit("Marrow Physiology topic count is not 33")
        chapter = page.locator("button.nk-topic-row[onclick=\"window.QB.openChapter('10')\"]")
        if chapter.count() != 1:
            raise SystemExit(f"Stable Physiology Chapter 10 selector count: {chapter.count()}")
        chapter.click()
        page.wait_for_timeout(80)
        rows = page.locator("button.nk-library-row")
        if rows.count() != 18:
            raise SystemExit(f"Marrow Physiology Chapter 10 count is not 18: {rows.count()}")
        rows.nth(12).click()
        page.wait_for_timeout(80)
        page.locator(".option-list button").first.click()
        page.wait_for_timeout(120)
        support = page.locator(".nk-study-support").inner_text().lower()
        for required in (
            "key takeaway",
            "detailed explanation",
            "structured text",
            "why the other options are wrong",
            "eccrine sweat gland",
            "sympathetic postganglionic fibers are cholinergic",
            "sympathetic adrenergic",
        ):
            if required not in support:
                raise SystemExit(f"Physiology Chapter 10 Q13 explanation missing {required}")
        if page.locator(".nk-gold-wrong-row").count() != 3:
            raise SystemExit("Physiology Chapter 10 Q13 must render exactly three distractor rationales")
        page.screenshot(path=str(OUT / "physiology-ch10-q13-sweat-gland-reconstruction.png"), full_page=True)
        if errors:
            raise SystemExit("Physiology Chapter 10 browser errors: " + " | ".join(errors))
        page.close()

        browser.close()
    server.shutdown()
print("MARROW_EXPLANATION_BROWSER_OK anatomy_ch05_q09=verified physiology_ch10_q13=verified rationales=3")
