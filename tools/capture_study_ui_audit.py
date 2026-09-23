#!/usr/bin/env python3
"""Capture the generated learner journey at phone and tablet viewports.

This is an evidence capture, not a visual pass/fail oracle. It records geometry
and screenshots so layout defects can be confirmed before changing product CSS.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/study-ui-audit"
SIZES = (("small-phone", 320, 640, False), ("phone", 390, 844, False),
         ("large-text-phone", 390, 844, True), ("tablet", 820, 1180, False))


def capture(page, name, observations, *, full_page=False):
    page.wait_for_timeout(120)
    path = OUT / f"{name}.png"
    page.screenshot(path=str(path), full_page=full_page, animations="disabled")
    observations.append(page.evaluate("""name => {
      const root=document.documentElement, viewport={width:innerWidth,height:innerHeight};
      const selectors=['.nk-session-footer','.nk-fsrs-rating','#nk-session-review',
        '.nk-source-visual img','.nk-marrow-figure-button img','.nk-bottom-nav'];
      const boxes={};
      for(const selector of selectors){const node=document.querySelector(selector);
        if(node){const r=node.getBoundingClientRect();boxes[selector]={x:r.x,y:r.y,width:r.width,height:r.height};}}
      return {name,hash:location.hash,viewport,documentWidth:root.scrollWidth,
        horizontalOverflow:Math.max(0,root.scrollWidth-root.clientWidth),
        textScale:getComputedStyle(root).webkitTextSizeAdjust,
        visibleText:document.body.innerText.slice(0,500),boxes};
    }""", name))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    web = ROOT / "build/web"
    assert (web / "index.html").is_file(), "Generate build/web before UI capture"
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    report = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for label, width, height, large_text in SIZES:
                context = browser.new_context(viewport={"width": width, "height": height}, is_mobile=True,
                                              has_touch=True, reduced_motion="reduce", service_workers="block")
                page = context.new_page()
                errors = []
                observations = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState")
                if large_text:
                    # Browser approximation of increased system text size; the
                    # exact Android font scale still needs physical verification.
                    page.add_style_tag(content="html{font-size:125% !important;-webkit-text-size-adjust:150% !important;text-size-adjust:150% !important}")
                capture(page, f"{label}-01-home", observations)

                page.locator("button.nk-v3-subject-card").filter(has_text="Biochemistry").click()
                page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
                page.locator("button.nk-topic-row").first.wait_for(state="visible")
                capture(page, f"{label}-02-topics", observations)
                page.locator("button.nk-topic-row").first.click()
                page.locator("button.nk-library-row").first.wait_for(state="visible")
                capture(page, f"{label}-03-chapter", observations)
                page.locator("button.nk-library-row").first.click()
                page.locator(".option-list button").first.wait_for(state="visible")
                capture(page, f"{label}-04-question", observations)
                page.locator(".option-list button").first.click()
                page.locator(".nk-study-support").wait_for(state="visible")
                capture(page, f"{label}-05-answer", observations)
                capture(page, f"{label}-06-long-explanation", observations, full_page=True)
                page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
                capture(page, f"{label}-07-explanation-bottom", observations)
                page.evaluate("window.QB.openSessionReview()")
                page.locator("#nk-session-review").wait_for(state="visible")
                capture(page, f"{label}-08-final-grid", observations)
                page.locator("#nk-session-review").get_by_role("button", name="Submit", exact=True).click()
                page.get_by_role("button", name="Review Solutions", exact=True).wait_for(state="visible")
                capture(page, f"{label}-09-analysis", observations)
                page.get_by_role("button", name="Review Solutions", exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='review'")
                capture(page, f"{label}-10-review", observations)
                page.locator("#cr-grid").click()
                page.locator("#qb-question-navigator").wait_for(state="visible")
                capture(page, f"{label}-11-review-grid", observations)
                page.locator("#qb-question-navigator").get_by_role("button", name="End Review", exact=True).click()

                page.evaluate("window.QB.nav('fsrs')")
                capture(page, f"{label}-12-fsrs", observations)
                page.evaluate("window.QB.nav('tests')")
                capture(page, f"{label}-13-tests", observations)
                page.evaluate('window.QB.openSessionBuilder(null,"exam")')
                page.locator("#modal").get_by_role("button", name="Start Exam", exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                capture(page, f"{label}-14-cbt", observations)
                page.locator(".option-list button").first.click()
                capture(page, f"{label}-15-cbt-selected", observations)
                page.evaluate("window.QB.openSessionReview()")
                capture(page, f"{label}-16-cbt-grid", observations)

                report.append({"size": label, "width": width, "height": height,
                               "largeTextSimulation": large_text,
                               "observations": observations, "pageErrors": errors})
                context.close()
            browser.close()
    finally:
        server.shutdown()
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("STUDY_UI_AUDIT_CAPTURE_OK " + json.dumps({item["size"]: len(item["observations"]) for item in report}))


if __name__ == "__main__":
    main()
