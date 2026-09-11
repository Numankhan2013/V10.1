#!/usr/bin/env python3
"""Preserve verified Marrow browser history, then test the current Biochemistry batch."""
from __future__ import annotations

import importlib.util
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HISTORY_PATH = HERE / "_verify_marrow_bank_browser_rollout_history.py"
spec = importlib.util.spec_from_file_location("_marrow_rollout_browser_history", HISTORY_PATH)
if spec is None or spec.loader is None:
    raise SystemExit("Unable to load prior Marrow rollout browser regressions")
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "build/web"
OUT = ROOT / "build/marrow-ui-checks"
OUT.mkdir(parents=True, exist_ok=True)

# Current Biochemistry Chapter 12 Q7: stable-ID/source-order regression for an
# unrecoverable numbered-list omission. The product must teach the recoverable
# semantic answer without inventing the missing 1–4 statement mapping.
handler = lambda *a, **k: history.base.Quiet(*a, directory=str(WEB), **k)
with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.route(
            "**/*.pdf*",
            lambda route: route.fulfill(
                path=str(ROOT / "app/src/main/assets/Biochemistry_QBank_Source.pdf"),
                content_type="application/pdf",
                headers={"Access-Control-Allow-Origin": "*"},
            ) if "biochem" in route.request.url.lower() else route.continue_(),
        )
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
        page.locator("button.nk-subject-row").filter(has_text="Biochemistry").click()
        page.wait_for_timeout(80)
        if "#banks/Biochemistry" not in page.url:
            raise SystemExit(f"Biochemistry did not open bank selector: {page.url}")
        page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
        page.wait_for_timeout(100)
        if page.locator("button.nk-topic-row").count() != 26:
            raise SystemExit("Marrow Biochemistry topic count is not 26")
        chapter = page.locator("button.nk-topic-row[onclick=\"window.QB.openChapter('12')\"]")
        if chapter.count() != 1:
            raise SystemExit(f"Stable Biochemistry Chapter 12 selector count: {chapter.count()}")
        chapter.click()
        page.wait_for_timeout(80)
        rows = page.locator("button.nk-library-row")
        if rows.count() != 14:
            raise SystemExit(f"Marrow Biochemistry Chapter 12 count is not 14: {rows.count()}")
        rows.nth(6).click()
        page.wait_for_timeout(80)
        question = page.locator(".question-text").inner_text().lower()
        if "essential fatty acids" not in question:
            raise SystemExit("Biochemistry Chapter 12 Q7 did not open by stable source order")
        option_text = page.locator(".option-list").inner_text().replace(" ", "")
        if "1,3" not in option_text:
            raise SystemExit("Biochemistry Chapter 12 Q7 source-keyed numeric options were not preserved")
        page.locator(".option-list button").first.click()
        page.wait_for_timeout(120)
        support = page.locator(".nk-study-support").inner_text().lower()
        for required in (
            "key takeaway",
            "detailed explanation",
            "why the other options are wrong",
            "linoleic acid",
            "α-linolenic acid",
            "source limitation",
            "option c (1,3)",
            "not reconstructed or invented",
        ):
            if required not in support:
                raise SystemExit(f"Biochemistry Chapter 12 Q7 explanation missing {required}")
        if page.locator(".nk-gold-wrong-row").count() != 3:
            raise SystemExit("Biochemistry Chapter 12 Q7 must render exactly three distractor rationales")
        page.screenshot(path=str(OUT / "biochem-ch12-q07-essential-fatty-acid-source-omission.png"), full_page=True)
        if errors:
            raise SystemExit("Biochemistry Chapter 12 Q7 browser errors: " + " | ".join(errors))
        browser.close()
    server.shutdown()

print("MARROW_EXPLANATION_BROWSER_CURRENT_OK biochemistry_ch12_q07=verified reconstruction=needs_manual_review rationales=3")
