#!/usr/bin/env python3
"""Exercise all-bank question finding and exact Practice entry on phone/tablet."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
MARROW_ID = "marrow__ANAT_CH01_Q001"
PREP_ID = "physiology-9-6"


def main() -> None:
    web = ROOT / "build/web"
    assert "NK_QUESTION_SEARCH_V1_START" in (web / "index.html").read_text(encoding="utf-8")
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
                page.get_by_role("heading", name="Find a question").wait_for(state="visible")
                assert page.locator(".nk-question-search-item").count() == 0

                search = page.get_by_role("searchbox", name="Search all questions")
                search.fill(MARROW_ID)
                page.wait_for_function("document.querySelectorAll('.nk-question-search-item').length===1")
                item = page.locator(".nk-question-search-item").first
                assert "Anatomy · Marrow" in item.locator(".nk-question-search-meta").inner_text()
                assert MARROW_ID in item.locator(".nk-question-search-id").inner_text()
                page.screenshot(path=str(output / f"question-search-{device}.png"), full_page=True)
                item.get_by_role("button", name="Practice").click()
                page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.[0]===id", arg=MARROW_ID)
                assert page.evaluate("window.QB.getState().activeSession.originRoute") == "question-search"

                page.evaluate("window.QB.nav('question-search')")
                search.fill(PREP_ID)
                page.wait_for_function("document.querySelectorAll('.nk-question-search-item').length===1")
                assert "Physiology · PrepLadder" in page.locator(".nk-question-search-meta").inner_text()
                page.locator(".nk-question-search-filters select").nth(1).select_option("Marrow")
                assert page.locator(".nk-question-search-item").count() == 0, "Bank filter leaked a PrepLadder question"
                page.locator(".nk-question-search-filters select").nth(1).select_option("PrepLadder")
                assert page.locator(".nk-question-search-item").count() == 1
                page.get_by_role("button", name="Practice first 1 match").click()
                page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.[0]===id", arg=PREP_ID)

                page.evaluate("window.QB.nav('question-search')")
                page.evaluate("""() => {const s=window.QB.getState();s.activeSession={id:'search-guard-exam',mode:'exam',questionIds:['x'],index:0,answers:{}};}""")
                page.locator(".nk-question-search-item button").click()
                assert page.evaluate("window.QB.getState().activeSession?.id") == "search-guard-exam", "Search replaced an active timed test"
                assert not errors, f"{device} browser errors: {errors!r}"
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print("QUESTION_SEARCH_BROWSER_OK phone=true tablet=true exactIds=true bankIsolation=true practice=true testGuard=true")


if __name__ == "__main__":
    main()
