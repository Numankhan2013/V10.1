#!/usr/bin/env python3
"""Learner path for the Marrow-only Microbiology subject in a real browser.

Home -> My Subjects -> Microbiology -> one Marrow bank -> Topics (Immunology,
Systemic bacteriology) -> topic -> question -> answer -> Key takeaway +
ordered structured explanation (Marrow Pearl, table, figure). Also checks the
question-stem figure, that the three PrepLadder+Marrow subjects still offer two
banks, and that no page error is raised.

  python3 tools/verify_microbiology_marrow_browser.py [--web build/web]
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
    raise SystemExit("MICROBIOLOGY_BROWSER_FAIL: " + message)


def open_topic(page, title_part: str) -> None:
    page.evaluate("window.QB.nkOpenSubjectLibrary('Microbiology')")
    page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===1", timeout=8000)
    page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===5", timeout=8000)
    page.locator("button.nk-topic-row").filter(has_text=title_part).click()
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

            cards = page.locator(".nk-home-subjects button.nk-v3-subject-card")
            names = [cards.nth(i).inner_text() for i in range(cards.count())]
            micro = page.locator(".nk-home-subjects button.nk-v3-subject-card").filter(has_text="Microbiology")
            if micro.count() != 1:
                fail(f"Microbiology subject card missing; cards={names}")
            if "102" not in micro.inner_text() or "Marrow" not in micro.inner_text():
                fail(f"Microbiology card counts wrong: {micro.inner_text()!r}")
            page.screenshot(path=str(OUT / "micro-00-home.png"), full_page=True)

            micro.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===1", timeout=8000)
            bank = page.locator("button.nk-bank-card")
            if "Marrow" not in bank.inner_text() or "102 questions" not in bank.inner_text():
                fail(f"Microbiology bank card wrong: {bank.inner_text()!r}")
            bank.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===5", timeout=8000)
            body = page.locator("body").inner_text()
            for section in ("Immunology", "Systemic bacteriology"):
                if section not in body:
                    fail(f"Topics section {section!r} missing")
            if "Needs classification review" in body:
                fail("Microbiology topics fell back to the unclassified section")
            page.screenshot(path=str(OUT / "micro-01-topics.png"), full_page=True)

            # Ch4 Q5 (MCQ MA7014): two Marrow Pearls, a table and an in-pearl figure.
            page.locator("button.nk-topic-row").filter(has_text="Primary Immunodeficiency").click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-library-row').length===18", timeout=8000)
            page.locator("button.nk-library-row").nth(4).click()
            page.wait_for_function("() => (document.querySelector('.question-text')?.innerText||'').includes('Nitroblue tetrazolium')", timeout=8000)
            page.locator(".option-list button").nth(2).click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            page.wait_for_timeout(300)
            support = page.locator(".nk-study-support").inner_text()
            if "Key takeaway".lower() not in support.lower():
                fail("Key takeaway missing")
            if "Structured text" not in support or "Original PDF" in support:
                fail("Marrow explanation surface label wrong")
            explanation = page.locator(".nk-marrow-ordered")
            text = explanation.inner_text()
            for needle in ("Marrow Pearl · Primary Immunodeficiency Disorders", "Marrow Pearl · Chronic Granulomatous Disease",
                           "Positive test", "NADPH oxidase"):
                if needle not in text:
                    fail(f"ordered explanation missing {needle!r}")
            for junk in ("[object Object]", "**", "[ty]", "screenshot", "Ref:"):
                if junk in text:
                    fail(f"explanation shows {junk!r}")
            cells = page.locator(".nk-marrow-ordered .nk-marrow-table td")
            if cells.count() < 10 or "Common variable immunodeficiency" not in cells.nth(1).inner_text():
                fail("Pearl table did not render its cells")
            if text.index("Positive test") > text.index("Common variable immunodeficiency"):
                fail("table rendered out of source order")
            page.wait_for_function("() => [...document.querySelectorAll('.nk-marrow-figures img')].some(i => i.complete && i.naturalWidth > 0)", timeout=8000)
            page.screenshot(path=str(OUT / "micro-02-explanation.png"), full_page=True)

            # Ch3 Q15 (MCQ MC4680): the question stem carries its figure.
            open_topic(page, "Hypersensitivity")
            page.locator("button.nk-library-row").nth(14).click()
            page.wait_for_function("() => (document.querySelector('.question-text')?.innerText||'').includes('antigen is produced')", timeout=8000)
            page.wait_for_function("() => { const f=document.querySelector('.question-text + .nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            page.screenshot(path=str(OUT / "micro-03-stem-figure.png"), full_page=True)

            # The canonical subjects still offer PrepLadder + Marrow.
            for subject in ("Anatomy", "Physiology", "Biochemistry"):
                page.evaluate(f"window.QB.nkOpenSubjectLibrary('{subject}')")
                page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=8000)

            if errors:
                fail("page errors: " + " | ".join(errors[:5]))
            browser.close()
    print("MICROBIOLOGY_BROWSER_OK subject=Microbiology bank=Marrow topics=5 sections=2 ordered_explanation=on stem_figure=on canonical_banks=2")


if __name__ == "__main__":
    main()
