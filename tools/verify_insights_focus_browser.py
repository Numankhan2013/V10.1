#!/usr/bin/env python3
"""Exercise cross-bank Insights evidence and direct targeted Practice."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
WRONG_IDS = ["marrow__ANAT_CH01_Q001", "marrow__ANAT_CH01_Q002"]
RIGHT_ID = "marrow__ANAT_CH01_Q003"


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    assert "NK_INSIGHTS_FOCUS_V1_START" in html
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
            page.evaluate("window.QB.nav('analytics')")
            page.get_by_role("heading", name="Topics to revisit").wait_for(state="visible")
            focus = page.locator(".nk-insights-focus")
            assert "Keep studying to reveal your focus areas" in focus.inner_text()

            page.evaluate("""([wrong1,wrong2,right]) => {
              const s=window.QB.getState(),now=Date.now();
              s.attempts[wrong1]=[{id:'insight-1',selected:1,correct:false,at:now-3000}];
              s.attempts[wrong2]=[{id:'insight-2',selected:1,correct:false,at:now-2000}];
              s.attempts[right]=[{id:'insight-3',selected:1,correct:true,at:now-1000}];
              window.QB.saveState();
            }""", [*WRONG_IDS, RIGHT_ID])
            page.evaluate("window.QB.nav('more')")
            page.locator(".nk-more-v114").wait_for(state="visible")
            page.evaluate("window.QB.nav('analytics')")
            row = page.locator(".nk-insights-focus-row")
            row.wait_for(state="visible")
            assert row.count() == 1
            assert "Anatomy · Marrow" in row.locator("small").inner_text()
            assert "2 still missed · 3 answered" in row.inner_text()
            page.screenshot(path=str(output / "insights-focus-phone.png"), full_page=True)
            row.get_by_role("button", name="Practice 2 missed").click()
            page.wait_for_function("location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.length===2")
            session = page.evaluate("window.QB.getState().activeSession")
            assert set(session["questionIds"]) == set(WRONG_IDS)
            assert session["originRoute"] == "wrong"

            page.evaluate("""id => {
              const s=window.QB.getState();
              s.attempts[id].push({id:'insight-improved',selected:1,correct:true,at:Date.now()});
              window.QB.saveState();
            }""", WRONG_IDS[0])
            page.evaluate("window.QB.nav('analytics')")
            page.get_by_role("heading", name="Topics to revisit").wait_for(state="visible")
            assert page.locator(".nk-insights-focus-row").count() == 0
            assert "No topic needs a targeted retry" in page.locator(".nk-insights-focus").inner_text()
            assert not errors, f"Browser errors: {errors!r}"
            print("INSIGHTS_FOCUS_BROWSER_OK evidence=true bank=true practice=true recovery=true")
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
