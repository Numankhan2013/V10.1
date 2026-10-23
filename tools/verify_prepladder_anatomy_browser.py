#!/usr/bin/env python3
"""Learner path for PrepLadder Anatomy (2025 edition) in a real browser.

Anatomy -> PrepLadder bank -> 54 lessons in the PDF's ten regions, 14 PYQ
lessons -> a 2025 question that continues an earlier one (anatomy-12-11):
answer, the ordered text explanation, references last -> an earlier question
the 2025 edition dropped (anatomy-1-11) and one whose 2025 explanation is
unusable (anatomy-29-7) keep their PDF-page explanations.

  python3 tools/verify_prepladder_anatomy_browser.py [--web build/web]
"""
from __future__ import annotations

import argparse
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_prepladder_anatomy_bank import BANK  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "marrow-ui-checks"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def fail(message: str) -> None:
    raise SystemExit("PREPLADDER_ANATOMY_BROWSER_FAIL: " + message)


def open_practice(page, question_id: str) -> None:
    page.evaluate("""() => { const s = window.QB.getState(); s.activeSession = null;
        s.normalPracticeCheckpoints = []; s.normalPracticeCheckpoint = null; }""")
    page.evaluate("id => window.QB.practiceOne(id)", question_id)
    page.locator(".option-list button").first.wait_for(timeout=8000)


def answer(page) -> None:
    page.locator(".option-list button").first.click()
    page.wait_for_selector(".nk-study-support", timeout=8000)


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

            page.evaluate("window.QB.nkOpenSubjectLibrary('Anatomy')")
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length>0", timeout=8000)
            bank = page.locator("button.nk-bank-card").filter(has_text="PrepLadder")
            if "1,135 questions" not in bank.inner_text():
                fail(f"PrepLadder card wrong: {bank.inner_text()!r}")
            bank.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===54", timeout=8000)
            headings = page.locator(".nk-topic-group > h2").all_inner_texts()
            if headings != [section for section, _ in BANK.index]:
                fail(f"sections not in study-index order: {headings!r}")
            if page.locator("button.nk-topic-row").filter(has_text="Previous Year Questions").count() != 14:
                fail("expected 14 Previous Year Questions lessons")
            page.screenshot(path=str(OUT / "planat-01-topics.png"), full_page=True)

            # A continued question explains in text, without the PDF's answer lead.
            open_practice(page, "anatomy-12-11")
            answer(page)
            page.wait_for_selector(".nk-marrow-ordered .nk-explain-refs", timeout=8000)
            support = page.locator(".nk-study-support").inner_text()
            if "Structured text" not in support or "Original PDF" in support:
                fail("explanation surface label wrong")
            text = page.locator(".nk-marrow-ordered").inner_text()
            if not text.lstrip().startswith("Danger space extends from the base"):
                fail(f"explanation opening wrong: {text[:120]!r}")
            for junk in ("**", "Correct Answer", "Correct Option", "[object Object]", "data-", ""):
                if junk in text:
                    fail(f"explanation shows {junk!r}")
            if page.evaluate("document.scrollingElement.scrollWidth") > 390:
                fail("the explanation widens the page past the phone width")
            page.screenshot(path=str(OUT / "planat-02-explanation.png"), full_page=True)

            # Earlier questions keep their PDF-page explanations.
            for qid in ("anatomy-1-11", "anatomy-29-7"):
                open_practice(page, qid)
                answer(page)
                if page.locator(".nk-marrow-ordered").count():
                    fail(f"{qid} should keep its PDF-page explanation")
                page.wait_for_selector(".nk-web-pdf-segment", timeout=15000)
            page.screenshot(path=str(OUT / "planat-04-earlier.png"), full_page=True)

            if errors:
                fail("page errors: " + " | ".join(errors[:5]))
            browser.close()
    print("PREPLADDER_ANATOMY_BROWSER_OK bank=PrepLadder questions=1135 topics=54 pyq=14 text_explanation=on "
          "earlier_pdf=on")


if __name__ == "__main__":
    main()
