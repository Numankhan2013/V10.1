#!/usr/bin/env python3
"""Stable-ID browser regression for Anatomy Ch6 Q18 explanation/table rendering."""
from __future__ import annotations

import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "build" / "web"
OUT = ROOT / "build" / "marrow-ui-checks"
STABLE_ID = "marrow__ANAT_CH06_Q018"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def main() -> None:
    index = WEB / "index.html"
    if not index.exists():
        raise SystemExit("Generated PWA is missing; build_web_dist must run first")
    generated = index.read_text(encoding="utf-8")
    if STABLE_ID not in generated:
        raise SystemExit(f"Stable ID {STABLE_ID} missing from generated PWA")
    OUT.mkdir(parents=True, exist_ok=True)
    handler = lambda *a, **k: Quiet(*a, directory=str(WEB), **k)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            page.evaluate("window.QB.nkOpenSubjectLibrary('Anatomy')")
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=5000)
            page.locator("button.nk-bank-card").filter(has_text="Marrow").click(timeout=5000)
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===63", timeout=5000)
            topic = page.locator("button.nk-topic-row").filter(has_text="Cardiovascular and Respiratory Systems")
            if topic.count() != 1:
                raise SystemExit(f"Anatomy Ch6 topic count={topic.count()}")
            topic.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-library-row').length>=18", timeout=5000)
            page.locator("button.nk-library-row").nth(17).click()
            page.wait_for_function("() => document.querySelectorAll('.option-list button').length===4", timeout=5000)
            page.locator(".option-list button").nth(3).click()
            page.wait_for_timeout(120)
            support = page.locator(".nk-study-support").inner_text().lower()
            for marker in ("key takeaway", "medial umbilical ligaments", "superior vesical arteries", "median umbilical ligament"):
                if marker not in support:
                    raise SystemExit(f"{STABLE_ID} learner explanation missing {marker!r}")
            if page.locator(".nk-gold-wrong-row").count() != 3:
                raise SystemExit(f"{STABLE_ID} must render exactly three distractor rationales")
            table_text = page.locator(".nk-marrow-table").inner_text().lower()
            for marker in ("embryological structure", "left umbilical vein", "ligamentum teres", "umbilical arteries", "medial umbilical ligaments", "urachus", "median umbilical ligament"):
                if marker not in table_text:
                    raise SystemExit(f"{STABLE_ID} structured table missing {marker!r}")
            if "[object object]" in table_text:
                raise SystemExit(f"{STABLE_ID} structured table stringified an object")
            if not page.locator(".nk-fsrs-rating").is_visible():
                raise SystemExit(f"{STABLE_ID} lost the shared FSRS recall dock")
            if errors:
                raise SystemExit(f"Browser errors while rendering {STABLE_ID}: {errors}")
            page.screenshot(path=str(OUT / "anatomy-ch06-q018-stable-id.png"), full_page=True)
            browser.close()
        server.shutdown()
    print(f"MARROW_ANATOMY_CH06_Q018_BROWSER_OK stable_id={STABLE_ID} rationales=3 table=preserved")

if __name__ == "__main__":
    main()
