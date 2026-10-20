#!/usr/bin/env python3
"""Learner path for PrepLadder Biochemistry (2025 edition) in a real browser.

Biochemistry -> PrepLadder bank -> 39 lessons in the study-index sections, 19
PYQ lessons -> a 2025 question that continues an earlier one (6-4): answer, the
ordered text explanation without its "Correct answer C)" lead, references last
-> a statement list the PDF ran together (5-10) shows as a numbered table -> an
earlier question the 2025 edition dropped (7-8) and one whose 2025 explanation
is unusable (21-29) keep their PDF-page explanations.

  python3 tools/verify_prepladder_biochemistry_browser.py [--web build/web]
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
from build_prepladder_biochemistry_bank import BANK  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "marrow-ui-checks"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def fail(message: str) -> None:
    raise SystemExit("PREPLADDER_BIOCHEMISTRY_BROWSER_FAIL: " + message)


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

            page.evaluate("window.QB.nkOpenSubjectLibrary('Biochemistry')")
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length>0", timeout=8000)
            bank = page.locator("button.nk-bank-card").filter(has_text="PrepLadder")
            if "867 questions" not in bank.inner_text():
                fail(f"PrepLadder card wrong: {bank.inner_text()!r}")
            bank.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===39", timeout=8000)
            headings = page.locator(".nk-topic-group > h2").all_inner_texts()
            if headings != [section for section, _ in BANK.index]:
                fail(f"sections not in study-index order: {headings!r}")
            if page.locator("button.nk-topic-row").filter(has_text="Previous Year Questions").count() != 19:
                fail("expected 19 Previous Year Questions lessons")
            page.screenshot(path=str(OUT / "plbiochem-01-topics.png"), full_page=True)

            # A continued question explains in text, without the PDF's answer lead.
            open_practice(page, "6-4")
            answer(page)
            page.wait_for_selector(".nk-marrow-ordered .nk-explain-refs", timeout=8000)
            support = page.locator(".nk-study-support").inner_text()
            if "Structured text" not in support or "Original PDF" in support:
                fail("explanation surface label wrong")
            text = page.locator(".nk-marrow-ordered").inner_text()
            if not text.lstrip().startswith("Biotin is a crucial coenzyme for pyruvate carboxylase,"):
                fail(f"explanation opening wrong: {text[:120]!r}")
            for junk in ("**", "Correct Answer", "Correct Option", "[object Object]", "data-", ""):
                if junk in text:
                    fail(f"explanation shows {junk!r}")
            if page.evaluate("document.scrollingElement.scrollWidth") > 390:
                fail("the explanation widens the page past the phone width")
            page.screenshot(path=str(OUT / "plbiochem-02-explanation.png"), full_page=True)

            # Statements the PDF ran together read as a numbered table.
            open_practice(page, "5-10")
            rows = page.locator(".question-text .nk-match-table tbody tr").all_inner_texts()
            if len(rows) != 3 or "α-1,4" not in rows[1]:
                fail(f"glycogen statements are not a numbered table: {rows!r}")
            if page.locator(".nk-question-unavailable").count():
                fail("statement-table question cannot be answered")
            page.screenshot(path=str(OUT / "plbiochem-03-statements.png"), full_page=True)

            # Earlier questions keep their PDF-page explanations.
            for qid in ("7-8", "21-29"):
                open_practice(page, qid)
                answer(page)
                if page.locator(".nk-marrow-ordered").count():
                    fail(f"{qid} should keep its PDF-page explanation")
                page.wait_for_selector(".nk-web-pdf-segment", timeout=15000)
            page.screenshot(path=str(OUT / "plbiochem-04-earlier.png"), full_page=True)

            if errors:
                fail("page errors: " + " | ".join(errors[:5]))
            browser.close()
    print("PREPLADDER_BIOCHEMISTRY_BROWSER_OK bank=PrepLadder questions=867 topics=39 pyq=19 text_explanation=on "
          "answer_lead=stripped statement_table=on earlier_pdf=on")


if __name__ == "__main__":
    main()
