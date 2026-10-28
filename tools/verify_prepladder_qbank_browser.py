#!/usr/bin/env python3
"""Learner path for the PrepLadder Version XI subjects (web export) in a real browser.

For each of the 13 Third and Final Prof subjects: the subject offers PrepLadder beside
Marrow; the PrepLadder card shows the bank's count; the lessons list in the official
app's index order. Then a stem figure from PrepLadder's image server renders in place,
and an explanation figure over 8 MB waits behind "Tap to load" until tapped.

PrepLadder's image server is not contacted: the browser answers its URLs with a 1-pixel
PNG, so the check is about the app, not the network.

  python3 tools/verify_prepladder_qbank_browser.py [--web build/web]
"""
from __future__ import annotations

import argparse
import base64
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepladder_qbank_bank as bank  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "prepladder-qbank-checks"
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def fail(message: str) -> None:
    raise SystemExit("PREPLADDER_QBANK_BROWSER_FAIL: " + message)


def open_bank(page, subject: str) -> None:
    page.evaluate(f"window.QB.nkOpenSubjectLibrary({subject!r})")
    page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=8000)


def open_question(page, record: dict, question: dict) -> None:
    """Open the lesson of `question` and then the question itself."""
    topics = record["topics"]
    t = next(n for n, topic in enumerate(topics) if topic["id"] == question["chapterId"])
    open_bank(page, record["subject"])
    page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
    page.wait_for_function(f"() => document.querySelectorAll('button.nk-topic-row').length==={len(topics)}", timeout=8000)
    page.locator("button.nk-topic-row").nth(t).click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-library-row').length>0", timeout=8000)
    lesson = [q for q in record["questions"] if q["chapterId"] == question["chapterId"]]
    if page.locator("button.nk-library-row").count() != len(lesson):
        fail(f"{topics[t]['title']}: lists {page.locator('button.nk-library-row').count()} questions, not {len(lesson)}")
    page.locator("button.nk-library-row").nth(lesson.index(question)).click()
    page.wait_for_selector(".question-text", timeout=8000)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", type=Path, default=ROOT / "build" / "web")
    web = parser.parse_args().web.resolve()
    if not (web / "index.html").exists():
        fail(f"{web}/index.html missing; run after the web build")
    OUT.mkdir(parents=True, exist_ok=True)
    records = {slug: bank.stored_record(slug) for slug, cfg in bank.SUBJECTS.items() if not cfg.get("supplement")}
    figures = {slug: json_figures(slug) for slug in records}
    handler = lambda *a, **k: Quiet(*a, directory=str(web), **k)
    with socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler) as server:
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            requested: list[str] = []

            def pixel(route):
                requested.append(route.request.url)
                route.fulfill(status=200, content_type="image/png", body=PIXEL)
            page.route("https://image.prepladder.com/**", pixel)
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")

            for slug, record in records.items():
                open_bank(page, record["subject"])
                card = page.locator("button.nk-bank-card").filter(has_text="PrepLadder")
                if card.count() != 1 or f"{len(record['questions']):,} questions" not in card.inner_text():
                    fail(f"{slug}: PrepLadder card wrong: {card.all_inner_texts()!r}")
                card.click()
                page.wait_for_function(f"() => document.querySelectorAll('button.nk-topic-row').length==={len(record['topics'])}", timeout=8000)
                sections = list(dict.fromkeys(t["section"] for t in record["topics"]))
                headings = page.locator(".nk-topic-group > h2").all_inner_texts()
                if [h.strip() for h in headings] != sections:
                    fail(f"{slug}: indexes not in the official app's order: {headings!r} vs {sections!r}")
                rows = page.locator("button.nk-topic-row").all_inner_texts()
                for row, topic in zip(rows, record["topics"]):
                    if topic["title"] not in row:
                        fail(f"{slug}: lesson row {row!r} is not {topic['title']!r}")
            page.screenshot(path=str(OUT / "prepladder-qbank-01-topics.png"), full_page=True)

            # A stem figure: the image comes from PrepLadder's server, at the probed size.
            slug = "ent"
            figure = next(f for f in figures[slug] if f["role"] == "question")
            question = next(q for q in records[slug]["questions"] if q["id"] == figure["questionId"])
            open_question(page, records[slug], question)
            img = page.locator(".question-text + .nk-marrow-figures img").first
            img.wait_for(timeout=8000)
            if img.get_attribute("src") != figure["url"]:
                fail(f"stem figure src {img.get_attribute('src')!r} is not {figure['url']!r}")
            if img.get_attribute("width") != str(figure["width"]) or img.get_attribute("height") != str(figure["height"]):
                fail("stem figure does not reserve its probed size")
            page.wait_for_function("() => { const f=document.querySelector('.question-text + .nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            page.screenshot(path=str(OUT / "prepladder-qbank-02-stem-figure.png"), full_page=True)

            # A very large explanation figure waits for a tap.
            slug, big = next((s, f) for s in records for f in figures[s]
                             if f["role"] == "explanation" and f["bytes"] > 8e6
                             and sum(1 for g in figures[s] if g["questionId"] == f["questionId"]) == 1)
            question = next(q for q in records[slug]["questions"] if q["id"] == big["questionId"])
            open_question(page, records[slug], question)
            page.locator(".option-list button").first.click()
            held = page.locator(".nk-marrow-figure-button.is-held")
            held.wait_for(timeout=8000)
            if "Tap to load" not in held.inner_text() or big["url"] in requested:
                fail("a figure over 8 MB downloaded on its own")
            held.scroll_into_view_if_needed()
            page.wait_for_timeout(600)
            held.locator("xpath=..").screenshot(path=str(OUT / "prepladder-qbank-03-held-card.png"))
            held.click()
            page.wait_for_function("() => { const f=document.querySelector('.nk-marrow-figures img'); return f && f.complete && f.naturalWidth>0; }", timeout=8000)
            if big["url"] not in requested:
                fail("tapping the held figure did not load it")
            page.screenshot(path=str(OUT / "prepladder-qbank-03-held-figure.png"), full_page=True)

            if errors:
                fail("page errors: " + "; ".join(errors[:3]))
            browser.close()
    print(f"PREPLADDER_QBANK_BROWSER_OK subjects={len(records)} indexes=official stem_figure=remote held_figure=on")


def json_figures(slug: str) -> list[dict]:
    import json  # noqa: PLC0415
    return json.loads((bank.QBANK / slug / "visuals.json").read_text(encoding="utf-8"))["figures"]


if __name__ == "__main__":
    main()
