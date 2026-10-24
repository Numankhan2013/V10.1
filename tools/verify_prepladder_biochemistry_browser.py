#!/usr/bin/env python3
"""Learner path for PrepLadder Biochemistry (2025 edition) in a real browser.

Biochemistry -> PrepLadder bank -> 39 lessons in the study-index sections, 19
PYQ lessons -> a 2025 question that continues an earlier one (6-4): answer, the
ordered text explanation without its "Correct answer C)" lead, references last
-> a statement list the PDF ran together (5-10) shows as a numbered table -> the
2025 visual-table solution for 15-2 renders instead of an empty explanation ->
an earlier question the 2025 edition dropped (7-8) and one whose 2025 explanation
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

            # A long topic must stay a readable question map. The 62-question
            # mixed PYQ set previously rendered 19px cells with the numbers
            # hidden, so the whole map looked like a field of blank dots.
            page.evaluate("window.QB.openChapter('biochemistry-19')")
            page.wait_for_function("() => document.querySelectorAll('.nk-topic-map .nk-topic-cell').length === 62", timeout=8000)
            cells = page.locator(".nk-topic-map .nk-topic-cell")
            if cells.first.inner_text().strip() != "1" or cells.last.inner_text().strip() != "62":
                fail("the 62-question topic map is missing its question numbers")
            first_cell = cells.first.bounding_box()
            if not first_cell or first_cell["width"] < 40 or first_cell["height"] < 40:
                fail(f"the 62-question topic map cells are too small: {first_cell!r}")
            cell_type = page.evaluate("""() => {
                const el = document.querySelector('.nk-topic-map .nk-topic-cell');
                const style = getComputedStyle(el);
                return {fontSize: style.fontSize, color: style.color};
            }""")
            if cell_type["fontSize"] == "0px" or cell_type["color"] in ("rgba(0, 0, 0, 0)", "transparent"):
                fail(f"the 62-question topic map hides its question numbers: {cell_type!r}")
            page.screenshot(path=str(OUT / "plbiochem-01b-topic-map.png"), full_page=True)

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

            # 15-2's 2025 solution is a table image, not an empty explanation.
            open_practice(page, "15-2")
            answer(page)
            figure = page.locator(".nk-marrow-ordered .nk-marrow-figures img").first
            figure.wait_for(timeout=15000)
            page.wait_for_function("""() => {
                const img = document.querySelector('.nk-marrow-ordered .nk-marrow-figures img');
                return img && img.complete && img.naturalWidth > 0;
            }""", timeout=15000)
            if page.locator(".nk-source-empty").count():
                fail("15-2 fell back to an empty explanation")
            support = page.locator(".nk-study-support").inner_text()
            if "No source explanation was provided" in support:
                fail("15-2 says the source explanation is missing")
            size = figure.evaluate("img => ({width: img.naturalWidth, height: img.naturalHeight})")
            if size != {"width": 1000, "height": 736}:
                fail(f"15-2 table image is the wrong asset: {size!r}")
            figure.scroll_into_view_if_needed()
            page.wait_for_timeout(600)
            page.screenshot(path=str(OUT / "plbiochem-04-table-explanation.png"))

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
          "answer_lead=stripped statement_table=on table_explanation=on earlier_pdf=on")


if __name__ == "__main__":
    main()
