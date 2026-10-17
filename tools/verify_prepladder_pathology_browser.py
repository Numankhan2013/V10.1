#!/usr/bin/env python3
"""Learner path for PrepLadder Pathology in a real browser.

Home: Pathology sits in Second Prof beside Microbiology -> Pathology ->
PrepLadder bank ("Text explanations") -> 90 lessons in four sections, 27 PYQ
lessons -> Cell Death Q3: stem figure -> Acute Inflammation Q3: answer, ordered
text explanation with option analysis in bold and an explanation figure -> a
PYQ question the source PDF prints no explanation for shows the plain note.

  python3 tools/verify_prepladder_pathology_browser.py [--web build/web]
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
    raise SystemExit("PREPLADDER_PATHOLOGY_BROWSER_FAIL: " + message)


def open_lesson(page, title: str, nth: int = 0) -> None:
    page.evaluate("window.QB.nkOpenSubjectLibrary('Pathology')")
    page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===1", timeout=8000)
    page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===90", timeout=8000)
    page.locator("button.nk-topic-row").filter(has_text=title).nth(nth).click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-library-row').length>0", timeout=8000)


def open_question(page, n: int, needle: str) -> None:
    page.locator("button.nk-library-row").nth(n).click()
    page.wait_for_function(f"() => (document.querySelector('.question-text')?.innerText||'').includes({needle!r})", timeout=8000)


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

            card = page.locator(".nk-home-subjects button.nk-v3-subject-card").filter(has_text="Pathology")
            if card.count() != 1 or "1,459" not in card.inner_text():
                fail(f"Pathology subject card missing or wrong: {card.all_inner_texts()!r}")
            if "is-pathology" not in (card.get_attribute("class") or ""):
                fail("Pathology card has no subject identity class")
            second = page.locator('.nk-prof-group[data-nk-prof="second"]')
            if "Pathology" not in second.inner_text() or "Microbiology" not in second.inner_text():
                fail(f"Second Prof should hold Microbiology and Pathology: {second.inner_text()!r}")

            page.evaluate("window.QB.nkOpenSubjectLibrary('Pathology')")
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===1", timeout=8000)
            bank = page.locator("button.nk-bank-card")
            if "1,459 questions" not in bank.inner_text() or "Text explanations" not in bank.inner_text():
                fail(f"PrepLadder card wrong: {bank.inner_text()!r}")
            bank.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===90", timeout=8000)
            body = page.locator("body").inner_text()
            for section in ("General Pathology", "Systemic Pathology", "Hematology", "Blood Banking and Clinical Pathology"):
                if section not in body:
                    fail(f"section {section!r} missing")
            if page.locator("button.nk-topic-row").filter(has_text="Previous Year Questions").count() != 27:
                fail("expected 27 Previous Year Questions lessons")
            if page.locator("button.nk-topic-row").filter(has_text="CML and CLL").count() != 1:
                fail("lesson titles were not cleaned")
            page.screenshot(path=str(OUT / "plpatho-01-topics.png"), full_page=True)

            open_lesson(page, "Cell Death")
            open_question(page, 2, "persistent cough")
            page.wait_for_function("() => { const f=document.querySelector('.question-text + .nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            page.screenshot(path=str(OUT / "plpatho-02-stem-figure.png"), full_page=True)

            # Q4: "P - K - K" keeps its dashes (no K⁻ ion superscript); the
            # references sit below the figure, with the book title in italics.
            open_lesson(page, "Cell Injury, Free Radical")
            open_question(page, 3, "nuclear changes")
            page.locator(".option-list button").first.click()
            page.wait_for_selector(".nk-marrow-ordered .nk-explain-refs", timeout=8000)
            page.wait_for_selector(".nk-marrow-ordered .nk-marrow-figures img", timeout=8000)
            ordered = page.locator(".nk-marrow-ordered")
            if "P - K - K: Pyknosis" not in ordered.inner_text() or "nk-sci-sup" in ordered.inner_html():
                fail("P - K - K is not shown as written")
            if not page.evaluate("(() => { const f=document.querySelector('.nk-marrow-ordered .nk-marrow-figures'), r=document.querySelector('.nk-marrow-ordered .nk-explain-refs'); return f.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING; })()"):
                fail("references are not below the figure")
            refs = page.locator(".nk-explain-refs")
            if refs.locator("cite").inner_text() != "Robbins and Cotran, Pathologic Basis of Disease":
                fail(f"reference title not italic: {refs.inner_html()!r}")
            body_size = page.evaluate("parseFloat(getComputedStyle(document.querySelector('.nk-marrow-ordered > p')).fontSize)")
            ref_size = page.evaluate("parseFloat(getComputedStyle(document.querySelector('.nk-explain-refs p')).fontSize)")
            if not ref_size < body_size:
                fail(f"references ({ref_size}px) should be smaller than the explanation ({body_size}px)")
            page.screenshot(path=str(OUT / "plpatho-025-references.png"), full_page=True)

            open_lesson(page, "Acute Inflammation")
            open_question(page, 2, "Leukocyte Adhesion Deficiency")
            page.locator(".option-list button").first.click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            support = page.locator(".nk-study-support").inner_text()
            if "Structured text" not in support or "Original PDF" in support:
                fail("explanation surface label wrong")
            explanation = page.locator(".nk-marrow-ordered")
            text = explanation.inner_text()
            for needle in ("β2 integrin", "Myeloperoxidase deficiency (Option D):", "References"):
                if needle not in text:
                    fail(f"explanation missing {needle!r}")
            for junk in ("**", "Correct Answer", "[object Object]", "data-", ";="):
                if junk in text:
                    fail(f"explanation shows {junk!r}")
            if "<strong>Myeloperoxidase deficiency (Option D):</strong>" not in explanation.inner_html():
                fail("option analysis lost its bold label")
            page.wait_for_function("() => { const f=document.querySelector('.nk-marrow-ordered img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            # Reference URLs are long and unbroken; they must wrap on a phone.
            # (A wide table scrolls inside its own box.)
            if page.evaluate("Math.max(document.scrollingElement.scrollWidth, ...[...document.querySelectorAll('.nk-marrow-ordered *')].filter(e => !e.closest('.nk-marrow-table table')).map(e => e.getBoundingClientRect().right))") > 390:
                fail("the explanation widens the page past the phone width")
            page.screenshot(path=str(OUT / "plpatho-03-explanation.png"), full_page=True)

            open_lesson(page, "Previous Year Questions")
            if page.locator("button.nk-library-row").count() != 34:
                fail("the first General Pathology PYQ lesson should list 34 questions")
            open_question(page, 30, "calcification")
            page.locator(".option-list button").first.click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            if "The source PDF prints no explanation for this question." not in page.locator(".nk-marrow-ordered").inner_text():
                fail("missing explanation is not marked")

            if errors:
                fail("page errors: " + " | ".join(errors[:5]))
            browser.close()
    print("PREPLADDER_PATHOLOGY_BROWSER_OK bank=PrepLadder topics=90 sections=4 second_prof=on stem_figure=on "
          "ordered_explanation=on references=on pyq=27 lost_note=on")


if __name__ == "__main__":
    main()
