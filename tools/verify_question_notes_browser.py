#!/usr/bin/env python3
"""Exercise question notes through generated Practice, reload, and Review."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
QUESTION_ID = "physiology-9-6"


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    assert "NK_QUESTION_NOTES_V1_START" in html
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            page.locator("button.nk-v3-subject-card").filter(has_text="Physiology").click()
            page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
            page.evaluate("id => window.QB.practiceOne(id)", QUESTION_ID)
            page.wait_for_function("id => window.QB.getState().activeSession?.questionIds?.[0]===id", arg=QUESTION_ID)
            page.evaluate("window.QB.nav('practice')")
            assert page.locator(".nk-question-note").count() == 0, "Notes should appear after answering"
            page.locator(".option").first.click()
            page.evaluate("window.QB.submitPractice()")
            note = page.locator(".nk-question-note")
            note.wait_for(state="visible")
            note.get_by_role("button", name="Add note").click()
            note.locator("textarea").fill("My recall cue: compare the two fibres.")
            note.get_by_role("button", name="Save note").click()
            assert page.evaluate("id => window.QB.getState().questionNotes?.[id]?.text", QUESTION_ID) == "My recall cue: compare the two fibres."
            assert note.locator("textarea").count() == 0
            assert note.get_by_role("button", name="Save note").count() == 0
            assert note.get_by_role("button", name="Cancel").count() == 0
            assert note.locator(".nk-note-readonly").inner_text() == "My recall cue: compare the two fibres."
            page.screenshot(path=str(output / "question-notes-practice-phone.png"), full_page=True)

            page.reload(wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            note.wait_for(state="visible")
            assert note.locator(".nk-note-readonly").inner_text() == "My recall cue: compare the two fibres.", "Note was lost after reload"
            note.get_by_role("button", name="Edit note").click()
            note.locator("textarea").fill("Unsaved change")
            note.get_by_role("button", name="Cancel").click()
            assert note.locator(".nk-note-readonly").inner_text() == "My recall cue: compare the two fibres.", "Cancel changed the saved note"

            page.evaluate("window.QB.nav('more')")
            page.get_by_role("button", name="My notes").click()
            assert page.locator(".nk-notes-item").count() == 1, "More should open the saved-note index"
            assert page.locator(".nk-notes-item-text").inner_text() == "My recall cue: compare the two fibres."
            page.locator(".nk-notes-search input").fill("no match")
            assert page.locator(".nk-notes-item:visible").count() == 0
            page.locator(".nk-notes-search input").fill("fibres")
            assert page.locator(".nk-notes-item:visible").count() == 1
            page.locator(".nk-notes-item button").click()
            page.wait_for_function("id => window.QB.getState().activeSession?.questionIds?.[0]===id", arg=QUESTION_ID)
            page.locator(".option").first.click()
            page.evaluate("window.QB.submitPractice()")
            note.wait_for(state="visible")
            assert note.locator(".nk-note-readonly").inner_text() == "My recall cue: compare the two fibres."

            page.evaluate("""id => {
              const s=window.QB.getState();
              s.tests.push({id:'notes-review-test',title:'Notes review',questionIds:[id],answers:{[id]:1},
                questionTimes:{},createdAt:Date.now(),total:1,correct:1,incorrect:0,unattempted:0});
              window.QB.saveState();window.QB.reviewTest('notes-review-test');
            }""", QUESTION_ID)
            note = page.locator(".nk-question-note")
            note.wait_for(state="visible")
            assert note.locator(".nk-note-readonly").inner_text() == "My recall cue: compare the two fibres.", "Review did not show the note"
            note.get_by_role("button", name="Delete note").click()
            assert page.evaluate("id => window.QB.getState().questionNotes?.[id]?.deleted", QUESTION_ID), "Removing a note needs a sync tombstone"
            assert note.get_by_role("button", name="Add note").count() == 1
            page.screenshot(path=str(output / "question-notes-review-phone.png"), full_page=True)
            assert not errors, f"Browser errors: {errors!r}"
            print("QUESTION_NOTES_BROWSER_OK practice=true reload=true review=true removal=true")
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
