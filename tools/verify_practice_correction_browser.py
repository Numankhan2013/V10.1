#!/usr/bin/env python3
"""Exercise a real missed Practice question through a linked correction pass."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
QUESTION_ID = "1-1"  # PrepLadder Biochemistry source answer B; first pass chooses A.


def main() -> None:
    web = ROOT / "build/web"
    assert "NK_PRACTICE_CORRECTION_V1_START" in (web / "index.html").read_text(encoding="utf-8")
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for device, viewport in (("phone", {"width": 390, "height": 844}),
                                     ("tablet", {"width": 800, "height": 1080})):
                context = browser.new_context(viewport=viewport, service_workers="block")
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#more", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState")
                page.get_by_role("button", name="Find a question").click()
                page.get_by_role("searchbox", name="Search all questions").fill(QUESTION_ID)
                page.wait_for_function("document.querySelectorAll('.nk-question-search-item').length>0")
                item = page.locator(".nk-question-search-item").first
                assert item.locator(".nk-question-search-id").inner_text().startswith(QUESTION_ID + " · ")
                item.get_by_role("button", name="Practice").click()
                page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.[0]===id", arg=QUESTION_ID)
                page.locator("button.option").nth(0).click()
                page.get_by_text("Incorrect", exact=True).first.wait_for(state="visible")
                page.evaluate("window.QB.nkSubmitPracticeSession()")
                page.wait_for_function("location.hash.startsWith('#result/') && !window.QB.getState().activeSession")
                first_id = page.evaluate("window.QB.getState().tests.at(-1).id")
                assert page.locator(".nk-correction-action button").count() == 1
                page.wait_for_function("Date.now()-window.QB.getState().tests.at(-1).createdAt>950")
                page.screenshot(path=str(output / f"practice-correction-initial-{device}.png"), full_page=True)
                page.locator(".nk-correction-action button").click()
                page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.[0]===id", arg=QUESTION_ID)
                assert page.evaluate("window.QB.getState().activeSession.answers") == {}, "Correction answers must start blank"
                page.reload(wait_until="domcontentloaded")
                page.wait_for_function("id => window.QB?.getState().activeSession?.questionIds?.[0]===id", arg=QUESTION_ID)
                page.locator("button.option").nth(1).click()
                page.get_by_text("Correct", exact=True).first.wait_for(state="visible")
                page.evaluate("window.QB.nkSubmitPracticeSession()")
                page.wait_for_function("location.hash.startsWith('#result/') && !window.QB.getState().activeSession")
                result = page.evaluate("window.QB.getState().tests.at(-1)")
                assert result["correctionOf"] == first_id
                assert result["correct"] == 1 and result["incorrect"] == 0
                section = page.locator(".nk-correction-section")
                assert "1 corrected" in section.inner_text()
                assert "All questions in this pass were correct" in section.inner_text()
                page.screenshot(path=str(output / f"practice-correction-complete-{device}.png"), full_page=True)
                page.reload(wait_until="domcontentloaded")
                page.wait_for_function("document.querySelector('.nk-correction-section')!==null")
                assert "1 corrected" in page.locator(".nk-correction-section").inner_text()
                page.get_by_role("button", name="View previous result").click()
                page.wait_for_function("id => decodeURIComponent(location.hash)==='#result/'+id", arg=first_id)
                assert page.evaluate("id => window.QB.getState().tests.find(t=>t.id===id).incorrect", first_id) == 1
                assert not errors, f"{device} browser errors: {errors!r}"
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print("PRACTICE_CORRECTION_BROWSER_OK phone=true tablet=true exactMiss=true reload=true comparison=true originalPreserved=true")


if __name__ == "__main__":
    main()
