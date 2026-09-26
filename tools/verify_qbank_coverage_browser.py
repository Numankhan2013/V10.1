#!/usr/bin/env python3
"""Exercise the all-bank study map and exact topic entry in a phone browser."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    web = ROOT / "build/web"
    assert "NK_QBANK_COVERAGE_V1_START" in (web / "index.html").read_text(encoding="utf-8")
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
            page.goto(origin + "/#analytics", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            expect(page.get_by_role("heading", name="Your study map")).to_be_visible()
            assert page.locator(".nk-coverage-bank").count() == 6
            assert "0/" in page.locator(".nk-coverage-overall").inner_text() or "0% covered" in page.locator(".nk-coverage-overall").inner_text()

            page.evaluate("""() => {
              const state=window.QB.getState(),now=Date.now();
              const prep=window.SUBJECT_QBANK_DATA.subjects.find(s=>s.subject==='Anatomy').questions
                .find(q=>Number(q.correctOption)>=1&&Number(q.correctOption)<=4);
              state.attempts[prep.id]=[{id:'coverage-prep',selected:prep.correctOption,correct:true,at:now-2000}];
              state.attempts['marrow__ANAT_CH01_Q001']=[{id:'coverage-marrow',selected:1,correct:false,at:now-1000}];
              window.QB.saveState();window.QB.nav('analytics');
            }""")
            tracker = page.locator(".nk-coverage")
            assert "2/" in tracker.locator(".nk-section-head").inner_text()
            prep = tracker.locator(".nk-coverage-bank").filter(has_text="Anatomy").filter(has_text="PrepLadder")
            marrow = tracker.locator(".nk-coverage-bank").filter(has_text="Anatomy").filter(has_text="Marrow")
            assert "1/1068 attempted" in prep.inner_text()
            assert "1/1115 attempted" in marrow.inner_text()
            marrow.click()
            assert "Anatomy · Marrow" in tracker.locator(".nk-coverage-detail-head").inner_text()
            tracker.locator(".nk-coverage-filter select").select_option("progress")
            rows = tracker.locator(".nk-coverage-topic")
            assert rows.count() == 1
            assert "1/" in rows.first.inner_text()
            page.screenshot(path=str(output / "qbank-coverage-phone.png"), full_page=True)
            tracker.locator(".nk-coverage-search input").fill("topic-that-does-not-exist")
            expect(tracker.locator(".nk-coverage-empty")).to_be_visible()
            tracker.locator(".nk-coverage-search input").fill("")
            title = rows.first.locator("strong").inner_text()
            rows.first.click()
            page.wait_for_function("location.hash.startsWith('#chapter/')")
            assert title in page.locator("body").inner_text()
            page.reload(wait_until="domcontentloaded")
            page.evaluate("window.QB.nav('analytics')")
            expect(page.get_by_role("heading", name="Your study map")).to_be_visible()
            assert "2/" in page.locator(".nk-coverage .nk-section-head").inner_text()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
    print("QBANK_COVERAGE_BROWSER_OK allBanks=true exactCounts=true filters=true navigation=true persistence=true")


if __name__ == "__main__":
    main()
