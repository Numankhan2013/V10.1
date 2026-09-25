#!/usr/bin/env python3
"""Exercise full-page bank/topic selection and a Marrow timed CBT on a phone."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    web = ROOT / "build/web"
    assert "NK_BANK_AWARE_CBT_BUILDER_V1_START" in (web / "index.html").read_text(encoding="utf-8")
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
            page.goto(origin + "/#tests", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            page.get_by_role("button", name="Choose subjects and topics").click()
            page.wait_for_url("**/#test-builder")
            expect(page.locator(".nk-cbt-builder .nk-module-subject")).to_have_count(6)
            page.get_by_role("button", name="Clear all").click()
            marrow = page.locator(".nk-cbt-builder .nk-module-subject").filter(has_text="Anatomy").filter(has_text="Marrow")
            marrow.click()
            assert marrow.get_attribute("aria-pressed") == "true"
            page.get_by_role("button", name="Continue to topics").click()
            group = page.locator(".nk-cbt-topic-group")
            expect(group).to_have_count(1)
            assert "Anatomy · Marrow" in group.locator(".nk-module-group-title").inner_text()
            assert group.locator(".nk-cbt-topic").count() == 63
            assert page.evaluate("getComputedStyle(document.querySelector('.nk-module-topic-groups')).overflowY") != "auto"
            page.screenshot(path=str(output / "cbt-builder-topics-phone.png"), full_page=True)
            page.get_by_role("button", name="Clear all").click()
            row = group.locator(".nk-cbt-topic").nth(25)
            row.scroll_into_view_if_needed()
            before = page.evaluate("window.scrollY")
            row.click()
            after = page.evaluate("window.scrollY")
            assert abs(after - before) < 40, "topic selection must not jump to the top"
            assert row.get_attribute("aria-pressed") == "true"
            assert "1 topic" in page.locator("#nk-cbt-footer-count").inner_text()
            page.get_by_role("button", name="Continue to questions").click()
            pool = int(page.locator(".nk-cbt-summary > div").nth(1).locator("strong").inner_text().split()[0].replace(",", ""))
            assert pool > 0
            page.locator("#nk-cbt-custom-count").fill("10")
            page.locator("#nk-cbt-custom-count").dispatch_event("input")
            assert str(min(10, pool)) in page.locator("#nk-cbt-count-result").inner_text()
            page.screenshot(path=str(output / "cbt-builder-questions-phone.png"), full_page=True)
            page.get_by_role("button", name="Start timed CBT").click()
            page.wait_for_function("location.hash==='#exam' && window.QB.getState().activeSession?.mode==='exam'")
            session = page.evaluate("window.QB.getState().activeSession")
            assert len(session["questionIds"]) == min(10, pool)
            assert all(str(qid).startswith("marrow__ANAT") for qid in session["questionIds"])
            assert session["originRoute"] == "tests"
            assert "Anatomy · Marrow CBT" == session["title"]
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
    print("BANK_AWARE_CBT_BROWSER_OK fullPage=true marrow=true stableScroll=true exam=true")


if __name__ == "__main__":
    main()
