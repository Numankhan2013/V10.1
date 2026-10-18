#!/usr/bin/env python3
"""Learner path for PrepLadder Pharmacology in a real browser.

Home: Pharmacology sits in Second Prof beside Microbiology and Pathology ->
Pharmacology -> PrepLadder bank ("Text explanations") -> 59 lessons in 13
sections, 16 PYQ lessons -> Pharmacokinetics Q14: stem figure ->
Pharmacodynamics Q1: answer, ordered text explanation with option analysis in
bold, a figure, then the references with the book title in italics -> a
five-option PYQ question -> a question the PDF prints no explanation for shows
the plain note.

  python3 tools/verify_prepladder_pharmacology_browser.py [--web build/web]
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
    raise SystemExit("PREPLADDER_PHARMACOLOGY_BROWSER_FAIL: " + message)


def open_lesson(page, title: str, nth: int = 0) -> None:
    page.evaluate("window.QB.nkOpenSubjectLibrary('Pharmacology')")
    page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===1", timeout=8000)
    page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===59", timeout=8000)
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

            card = page.locator(".nk-home-subjects button.nk-v3-subject-card").filter(has_text="Pharmacology")
            if card.count() != 1 or "1,321" not in card.inner_text():
                fail(f"Pharmacology subject card missing or wrong: {card.all_inner_texts()!r}")
            if "is-pharmacology" not in (card.get_attribute("class") or ""):
                fail("Pharmacology card has no subject identity class")
            second = page.locator('.nk-prof-group[data-nk-prof="second"]')
            if not all(s in second.inner_text() for s in ("Microbiology", "Pathology", "Pharmacology")):
                fail(f"Second Prof should hold Microbiology, Pathology and Pharmacology: {second.inner_text()!r}")

            page.evaluate("window.QB.nkOpenSubjectLibrary('Pharmacology')")
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===1", timeout=8000)
            bank = page.locator("button.nk-bank-card")
            if "1,321 questions" not in bank.inner_text() or "Text explanations" not in bank.inner_text():
                fail(f"PrepLadder card wrong: {bank.inner_text()!r}")
            bank.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===59", timeout=8000)
            body = page.locator("body").inner_text()
            for section in ("General Pharmacology", "Autonomic Nervous System", "Antimicrobials and Chemotherapy",
                            "Anaesthetics and Miscellaneous Pharmacology"):
                if section not in body:
                    fail(f"section {section!r} missing")
            if page.locator("button.nk-topic-row").filter(has_text="Previous Year Questions").count() != 16:
                fail("expected 16 Previous Year Questions lessons")
            if page.locator("button.nk-topic-row").filter(has_text="ANS Introduction and Cholinergic Drugs").count() != 1:
                fail("lesson titles were not cleaned")
            page.screenshot(path=str(OUT / "plpharma-01-topics.png"), full_page=True)

            open_lesson(page, "Pharmacokinetics")
            open_question(page, 13, "Match the following")
            header = page.locator(".question-text .nk-match-table th").all_text_contents()
            if [h.strip().lower() for h in header] != ["route", "percentage bioavailability"]:
                fail(f"bioavailability matching stem is not a table: {header!r}")
            page.wait_for_function("() => { const f=document.querySelector('.question-text + .nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            page.screenshot(path=str(OUT / "plpharma-02-stem-figure.png"), full_page=True)

            open_lesson(page, "Pharmacodynamics")
            open_question(page, 0, "does not have any effect of its own")
            page.locator(".option-list button").first.click()
            page.wait_for_selector(".nk-marrow-ordered .nk-explain-refs", timeout=8000)
            support = page.locator(".nk-study-support").inner_text()
            if "Structured text" not in support or "Original PDF" in support:
                fail("explanation surface label wrong")
            explanation = page.locator(".nk-marrow-ordered")
            text = explanation.inner_text()
            for needle in ("Drug C (Option C):", "Naloxone", "References"):
                if needle not in text:
                    fail(f"explanation missing {needle!r}")
            for junk in ("**", "Correct Option", "Correct Answer", "[object Object]", "data-", ";="):
                if junk in text:
                    fail(f"explanation shows {junk!r}")
            if "<strong>Drug A (Option A):</strong>" not in explanation.inner_html():
                fail("option analysis lost its bold label")
            page.wait_for_function("() => { const f=document.querySelector('.nk-marrow-ordered .nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            if not page.evaluate("(() => { const f=document.querySelector('.nk-marrow-ordered .nk-marrow-figures'), r=document.querySelector('.nk-marrow-ordered .nk-explain-refs'); return f.compareDocumentPosition(r) & Node.DOCUMENT_POSITION_FOLLOWING; })()"):
                fail("references are not below the figure")
            if page.locator(".nk-explain-refs cite").inner_text() != "K D Tripathi, Essentials of Medical Pharmacology":
                fail(f"reference title not italic: {page.locator('.nk-explain-refs').inner_html()!r}")
            # (A wide table scrolls inside its own box.)
            if page.evaluate("Math.max(document.scrollingElement.scrollWidth, ...[...document.querySelectorAll('.nk-marrow-ordered *')].filter(e => !e.closest('.nk-marrow-table table')).map(e => e.getBoundingClientRect().right))") > 390:
                fail("the explanation widens the page past the phone width")
            page.screenshot(path=str(OUT / "plpharma-03-explanation.png"), full_page=True)

            # Antimicrobials PYQs (the ninth PYQ lesson): Q30 prints options A-E.
            open_lesson(page, "Previous Year Questions", 8)
            if page.locator("button.nk-library-row").count() != 100:
                fail("the Antimicrobials PYQ lesson should list 100 questions")
            open_question(page, 29, "foscarnet")
            if page.locator(".option-list button").count() != 5:
                fail("five-option question does not show options A-E")
            page.locator(".option-list button").nth(4).click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            if "Option E: It can cause genital ulceration" not in page.locator(".nk-marrow-ordered").inner_text():
                fail("five-option explanation missing option E")

            # A matching stem the parser cannot lay out ("e:" for "e.") shows its hand-checked table and keeps its options.
            open_lesson(page, "Clinical Trials")
            open_question(page, 3, "Match the phases of drug trials")
            if page.locator(".option-list button").count() != 4 or page.locator(".nk-question-unavailable").count():
                fail("matching question lost its options")
            if page.locator(".question-text .nk-match-table tbody tr").count() < 4:
                fail("drug-trial phases are not laid out as a table")

            # Renal PYQs (the fifth PYQ lesson): Q13 prints only references.
            open_lesson(page, "Previous Year Questions", 4)
            open_question(page, 12, "road traffic accident")
            page.locator(".option-list button").first.click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            if "The source PDF prints no explanation for this question." not in page.locator(".nk-marrow-ordered").inner_text():
                fail("missing explanation is not marked")

            if errors:
                fail("page errors: " + " | ".join(errors[:5]))
            browser.close()
    print("PREPLADDER_PHARMACOLOGY_BROWSER_OK bank=PrepLadder topics=59 sections=13 second_prof=on stem_figure=on "
          "ordered_explanation=on references=on five_options=on matching_options=on pyq=16 lost_note=on")


if __name__ == "__main__":
    main()
