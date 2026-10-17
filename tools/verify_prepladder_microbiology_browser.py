#!/usr/bin/env python3
"""Learner path for PrepLadder Microbiology in a real browser.

Microbiology -> PrepLadder bank (beside Marrow, "Text explanations") -> 42
lessons in six sections -> lesson 1 Q1: stem figure, answer, ordered text
explanation (headings, table, option analysis in bold) -> lesson 2 Q11: the
stem's matching table renders as a table -> a PYQ lesson lists its 47 questions.

  python3 tools/verify_prepladder_microbiology_browser.py [--web build/web]
"""
from __future__ import annotations

import argparse
import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "marrow-ui-checks"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def fail(message: str) -> None:
    raise SystemExit("PREPLADDER_MICROBIOLOGY_BROWSER_FAIL: " + message)


def open_lesson(page, title: str, nth: int = 0) -> None:
    page.evaluate("window.QB.nkOpenSubjectLibrary('Microbiology')")
    page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=8000)
    page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===42", timeout=8000)
    page.locator("button.nk-topic-row").filter(has_text=title).nth(nth).click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-library-row').length>0", timeout=8000)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", type=Path, default=ROOT / "build" / "web")
    web = parser.parse_args().web.resolve()
    if not (web / "index.html").exists():
        fail(f"{web}/index.html missing; run after the app data step")
    OUT.mkdir(parents=True, exist_ok=True)
    handler = lambda *a, **k: Quiet(*a, directory=str(web), **k)
    with socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler) as server:
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")

            page.evaluate("window.QB.nkOpenSubjectLibrary('Microbiology')")
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=8000)
            card = page.locator("button.nk-bank-card").filter(has_text="PrepLadder")
            if "1,042 questions" not in card.inner_text() or "Text explanations" not in card.inner_text():
                fail(f"PrepLadder card wrong: {card.inner_text()!r}")
            card.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===42", timeout=8000)
            body = page.locator("body").inner_text()
            for section in ("General Microbiology", "Bacteriology", "Virology", "Mycology", "Parasitology", "Immunology"):
                if section not in body:
                    fail(f"section {section!r} missing")
            if page.locator("button.nk-topic-row").filter(has_text="Previous Year Questions").count() != 6:
                fail("expected six Previous Year Questions lessons")
            page.screenshot(path=str(OUT / "plmicro-01-topics.png"), full_page=True)

            open_lesson(page, "Scientists, Stains")
            page.locator("button.nk-library-row").first.click()
            page.wait_for_function("() => (document.querySelector('.question-text')?.innerText||'').includes('pseudomembrane')", timeout=8000)
            page.wait_for_function("() => { const f=document.querySelector('.question-text + .nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            page.locator(".option-list button").first.click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            support = page.locator(".nk-study-support").inner_text()
            if "Structured text" not in support or "Original PDF" in support:
                fail("explanation surface label wrong")
            explanation = page.locator(".nk-marrow-ordered")
            text = explanation.inner_text()
            for needle in ("Albert Stain", "Procedure", "Malachite Green", "Gram stain (Option B):"):
                if needle not in text:
                    fail(f"explanation missing {needle!r}")
            for junk in ("**", "Correct Answer", "[object Object]", "data-", "content truncated"):
                if junk in text:
                    fail(f"explanation shows {junk!r}")
            if explanation.locator(".nk-marrow-heading").count() < 3 or explanation.locator(".nk-marrow-table td").count() < 4:
                fail("headings or table did not render")
            if "<strong>Gram stain (Option B):</strong>" not in explanation.inner_html():
                fail("option analysis lost its bold label")
            page.screenshot(path=str(OUT / "plmicro-02-explanation.png"), full_page=True)

            open_lesson(page, "Bacterial Anatomy")
            page.locator("button.nk-library-row").nth(10).click()
            page.wait_for_function("() => (document.querySelector('.question-text')?.innerText||'').includes('types of motility')", timeout=8000)
            table = page.locator(".question-text .nk-match-table")
            if table.count() != 1 or "Twitching motility" not in table.inner_text() or table.locator("tbody tr").count() != 4:
                fail("stem matching table did not render")
            page.screenshot(path=str(OUT / "plmicro-03-stem-table.png"), full_page=True)

            open_lesson(page, "Previous Year Questions")
            if page.locator("button.nk-library-row").count() != 47:
                fail("General Microbiology PYQ lesson should list 47 questions")

            if errors:
                fail("page errors: " + " | ".join(errors[:5]))
            browser.close()
    print("PREPLADDER_MICROBIOLOGY_BROWSER_OK bank=PrepLadder topics=42 sections=6 stem_figure=on ordered_explanation=on stem_table=on pyq=on")


if __name__ == "__main__":
    main()
