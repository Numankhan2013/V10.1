#!/usr/bin/env python3
"""Learner path for Microbiology's Marrow bank in a real browser.

Home -> My Subjects -> Microbiology -> Marrow bank (beside PrepLadder) -> Topics (Immunology,
Systemic bacteriology) -> topic -> question -> answer -> Key takeaway +
ordered structured explanation (Marrow Pearl, table, figure). Also checks the
question-stem figure, the source peer statistics (UWorld-style "% got this
right" chip and per-option pick rates, hidden until answered), a part-02
question (Pearl table + footnote), that every PrepLadder+Marrow subject
offers two banks, and that no page error is raised.

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
    page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=8000)
    page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===25", timeout=8000)
    row = page.locator("button.nk-topic-row").filter(has_text=title_part)
    if row.count() != 1:
        fail(f"topic filter {title_part!r} matched {row.count()} rows")
    row.click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-library-row').length>0", timeout=8000)


def check_stats(page, peer: int, polls: list[str]) -> None:
    page.wait_for_timeout(200)
    chip = page.locator(".nk-study-support > .nk-uworld-cohort")
    if chip.count() != 1:
        fail("'% got this right' chip missing")
    if f"{peer}%" not in chip.inner_text():
        fail(f"cohort chip shows {chip.inner_text()!r}, expected {peer}%")
    label = chip.get_attribute("aria-label") or ""
    if "UWorld" in label:
        fail(f"cohort chip credits UWorld: {label!r}")
    shown = [page.locator(".option-list .option").nth(i).locator(".nk-uworld-option-percent").inner_text().strip() for i in range(4)]
    if shown != polls:
        fail(f"option pick rates {shown}, expected {polls}")


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
            if "1,768" not in micro.inner_text() or "Marrow" not in micro.inner_text() or "PrepLadder" not in micro.inner_text():
                fail(f"Microbiology card counts wrong: {micro.inner_text()!r}")

            # My Subjects groups the subjects by professional year and both groups
            # start collapsed; Microbiology is the single Second Prof subject.
            first = page.locator('.nk-prof-group[data-nk-prof="first"]')
            second = page.locator('.nk-prof-group[data-nk-prof="second"]')
            if first.count() != 1 or second.count() != 1:
                fail("First Prof / Second Prof groups missing on Home")
            if first.locator(".nk-prof-body[inert]").count() != 1 or second.locator(".nk-prof-body[inert]").count() != 1:
                fail("subject groups should open collapsed")
            if "3 subjects" not in first.inner_text() or "Microbiology" not in second.inner_text():
                fail(f"group summaries wrong: {first.inner_text()!r} / {second.inner_text()!r}")
            # The Motion layer (nk-feel) pins the reveal: a live band rests at a
            # true 0px when closed, and springs 0 <-> content height when tapped.
            page.wait_for_function(
                "() => document.querySelector('.nk-prof-group[data-nk-prof=\"second\"]').classList.contains('nkg-prof-live')",
                timeout=8000,
            )
            if first.evaluate("g => g.classList.contains('nkg-prof-live')") is not True:
                fail("professional bands are missing the Motion reveal layer")
            if first.locator(".nk-prof-body").evaluate("n => n.style.height") != "0px":
                fail("a closed band should rest at a true 0 height")
            page.screenshot(path=str(OUT / "micro-00-home.png"), full_page=True)

            head = second.locator(".nk-prof-head")
            if head.get_attribute("aria-expanded") != "false":
                fail("Second Prof band did not start closed")
            head.click()
            page.wait_for_function(
                "() => document.querySelector('.nk-prof-group[data-nk-prof=\"second\"]').classList.contains('is-open')",
                timeout=5000,
            )
            if second.locator(".nk-prof-body[inert]").count() != 0 or head.get_attribute("aria-expanded") != "true":
                fail("Second Prof did not open for the learner")
            page.wait_for_function(
                "() => document.querySelector('.nk-prof-group[data-nk-prof=\"second\"] .nk-prof-body').style.height === ''",
                timeout=5000,
            )
            # One close/reopen cycle: both spring paths end in the right resting state.
            head.click()
            page.wait_for_function(
                "() => !document.querySelector('.nk-prof-group[data-nk-prof=\"second\"]').classList.contains('is-open')",
                timeout=5000,
            )
            page.wait_for_function(
                "() => document.querySelector('.nk-prof-group[data-nk-prof=\"second\"] .nk-prof-body').style.height === '0px'",
                timeout=5000,
            )
            head.click()
            page.wait_for_function(
                "() => document.querySelector('.nk-prof-group[data-nk-prof=\"second\"]').classList.contains('is-open')",
                timeout=5000,
            )
            page.wait_for_function(
                "() => document.querySelector('.nk-prof-group[data-nk-prof=\"second\"] .nk-prof-body').style.height === ''",
                timeout=5000,
            )
            if not micro.is_visible():
                fail("Microbiology card is still hidden after opening Second Prof")
            page.screenshot(path=str(OUT / "micro-00b-home-expanded.png"), full_page=True)

            micro.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=8000)
            bank = page.locator("button.nk-bank-card").filter(has_text="Marrow")
            if "Marrow" not in bank.inner_text() or "726 questions" not in bank.inner_text():
                fail(f"Microbiology bank card wrong: {bank.inner_text()!r}")
            bank.click()
            page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===25", timeout=8000)
            body = page.locator("body").inner_text()
            for section in ("Immunology", "Systemic bacteriology", "Virology", "Mycology", "Parasitology", "Applied microbiology"):
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
            if page.locator(".option-list .nk-uworld-option-percent").count() != 0:
                fail("pick rates visible before answering")
            if page.locator(".option-list .nk-uworld-percent-space").count() != 4:
                fail("pick-rate column not reserved before answering")
            page.locator(".option-list button").nth(2).click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            check_stats(page, 61, ["4%", "18%", "61%", "17%"])
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

            # Part 02, module 5 Q18 (MCQ MA1547): Pearl table with its footnote, wrong answer.
            open_topic(page, "Staphylococcus, Streptococcus")
            if page.locator("button.nk-library-row").count() != 60:
                fail("module 5 should list 60 questions after part 02")
            page.locator("button.nk-library-row").nth(17).click()
            page.wait_for_function("() => (document.querySelector('.question-text')?.innerText||'').includes('tricuspid valve vegetation')", timeout=8000)
            page.locator(".option-list button").nth(1).click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            check_stats(page, 70, ["70%", "4%", "7%", "19%"])
            text = page.locator(".nk-marrow-ordered").inner_text()
            for needle in ("Marrow Pearl · Microbiology of Infective Endocarditis", "Viridans group streptococci", "CoNS includes"):
                if needle not in text:
                    fail(f"part-02 explanation missing {needle!r}")
            for junk in ("clipped at", "[Marrow Pearl", "**"):
                if junk in text:
                    fail(f"part-02 explanation shows {junk!r}")
            page.screenshot(path=str(OUT / "micro-04-part02-stats.png"), full_page=True)

            # Ch7 Q10 has no reviewed Key takeaway, so the card derives its
            # sentence from the explanation; both that card and the explanation
            # carry source emphasis markers (**bold**, *italic*) that must
            # render as emphasis, never as raw markers.
            open_topic(page, "Clostridium")
            if page.locator("button.nk-library-row").count() != 44:
                fail("chapter 7 should list 44 questions after parts 02-03")
            page.locator("button.nk-library-row").nth(9).click()
            page.wait_for_function(
                "() => (document.querySelector('.question-text')?.innerText||'').includes('spontaneous gas gangrene')",
                timeout=8000,
            )
            page.locator(".option-list button").nth(0).click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            takeaway_card = page.locator(".nk-key-takeaway")
            if takeaway_card.count() != 1:
                fail("derived Key takeaway card missing for Ch7 Q10")
            takeaway_text = takeaway_card.inner_text()
            if "*" in takeaway_text or "[object Object]" in takeaway_text:
                fail(f"Key takeaway leaks markers: {takeaway_text!r}")
            if "<strong>blood should be cultured" not in takeaway_card.inner_html():
                fail("derived Key takeaway lost its bold span")
            explanation_surface = page.locator(".nk-marrow-ordered")
            explanation_html = explanation_surface.inner_html()
            if "*" in explanation_surface.inner_text():
                fail("explanation leaks raw emphasis markers")
            for span in ("<em>C. septicum, C. perfringens</em>", "<em>C. novyi</em>"):
                if span not in explanation_html:
                    fail(f"explanation lost its italic span {span!r}")
            page.screenshot(path=str(OUT / "micro-05-emphasis.png"), full_page=True)

            # Ch3 Q15 (MCQ MC4680): the question stem carries its figure.
            open_topic(page, "Hypersensitivity")
            page.locator("button.nk-library-row").nth(14).click()
            page.wait_for_function("() => (document.querySelector('.question-text')?.innerText||'').includes('antigen is produced')", timeout=8000)
            page.wait_for_function("() => { const f=document.querySelector('.question-text + .nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            page.screenshot(path=str(OUT / "micro-03-stem-figure.png"), full_page=True)

            # Part 07 completes the merged Mycology module (15+20=35) and adds
            # Protozoology (39): both must answer with peer statistics.
            open_topic(page, "Mycology")
            if page.locator("button.nk-library-row").count() != 35:
                fail("Mycology should list 35 questions after part 07")
            open_topic(page, "Protozoology (Entamoeba")
            if page.locator("button.nk-library-row").count() != 39:
                fail("Protozoology should list 39 questions after part 07")
            page.locator("button.nk-library-row").first.click()
            page.wait_for_function("() => (document.querySelector('.question-text')?.innerText||'').length > 20", timeout=8000)
            page.locator(".option-list button").nth(0).click()
            page.wait_for_selector(".nk-marrow-ordered", timeout=8000)
            page.wait_for_timeout(250)
            chip = page.locator(".nk-study-support > .nk-uworld-cohort")
            if chip.count() != 1 or "%" not in chip.inner_text():
                fail("part-07 question shows no peer chip")
            pcts = [page.locator(".option-list .option").nth(i).locator(".nk-uworld-option-percent").inner_text().strip() for i in range(4)]
            if any(not p.endswith("%") for p in pcts):
                fail(f"part-07 pick rates missing: {pcts}")
            page.screenshot(path=str(OUT / "micro-06-part07.png"), full_page=True)

            # Every incumbent subject offers PrepLadder + Marrow.
            for subject in ("Anatomy", "Physiology", "Biochemistry", "Microbiology"):
                page.evaluate(f"window.QB.nkOpenSubjectLibrary('{subject}')")
                page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=8000)

            if errors:
                fail("page errors: " + " | ".join(errors[:5]))
            browser.close()
    print("MICROBIOLOGY_BROWSER_OK subject=Microbiology bank=Marrow topics=25 sections=6 questions=726 peer_stats=on part02=on ordered_explanation=on emphasis=on stem_figure=on part07=on banks=2 prof_groups=on")


if __name__ == "__main__":
    main()
