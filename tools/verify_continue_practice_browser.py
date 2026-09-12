#!/usr/bin/env python3
"""Exercise Pause/Continue and viewport-safe Practice controls in the built PWA."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    if "NK_CONTINUE_PRACTICE_RESUME_V1_START" not in html:
        raise SystemExit("Continue Practice resume layer missing from built PWA")
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width in (320, 390, 768):
                context = browser.new_context(viewport={"width": width, "height": 844}, service_workers="block", reduced_motion="reduce")
                page = context.new_page()
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState")
                page.evaluate("window.QB.practiceOne('1-1')")
                controls = page.locator(".nk-practice-session-controls")
                controls.wait_for(state="visible")
                pause = controls.get_by_role("button", name="Pause", exact=True)
                submit = controls.get_by_role("button", name="Submit", exact=True)
                for button in (pause, submit):
                    box = button.bounding_box()
                    if not box or box["width"] < 44 or box["height"] < 44:
                        raise SystemExit(f"{button.inner_text()} control is not a reachable 44px target at {width}px")
                    if box["x"] < 0 or box["x"] + box["width"] > width + 1 or box["y"] + box["height"] > 844:
                        raise SystemExit(f"{button.inner_text()} control is clipped at {width}px: {box}")
                nav = page.locator(".nk-session-footer .fixed-actions-inner").bounding_box()
                group = controls.bounding_box()
                if not nav or not group or group["y"] + group["height"] > nav["y"] + 1:
                    raise SystemExit(f"Practice controls collide with Previous/Next at {width}px")
                page.locator(".nk-session-footer").screenshot(path=str(output / f"continue-practice-controls-{width}.png"))
                context.close()

            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            page.evaluate("""() => {
              window.QB.practiceOne('1-1');
              const s=window.QB.getState().activeSession;
              s.questionIds=Array.from({length:20},(_,i)=>`1-${i+1}`);s.index=4;
              s.answers={'1-1':1,'1-2':1,'1-3':1,'1-4':1};s.submitted={'1-1':true,'1-2':true,'1-3':true,'1-4':true};s.questionTimes={'1-5':10};
            }""")
            page.get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            # Reproduce the shipped regression: an older resume path could leave only
            # the current question visible even though the canonical session stayed intact.
            page.evaluate("""() => {const s=window.QB.getState().activeSession;s.questionIds=['1-5'];s.index=0;}""")
            page.evaluate("window.QB.nkContinueRecentPractice()")
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")
            result = page.evaluate("""() => {const s=window.QB.getState().activeSession;return {ids:s.questionIds,current:s.questionIds[s.index],index:s.index,submitted:s.submitted,sessionIds:s.sessionQuestionIds};}""")
            if len(result["ids"]) != 20 or result["ids"][:2] != ["1-1", "1-2"] or result["ids"][-1] != "1-20":
                raise SystemExit(f"Pause/Continue did not restore the complete 20-question session: {result}")
            if result["current"] != "1-5" or result["index"] != 4:
                raise SystemExit(f"Pause/Continue did not restore the saved question position: {result}")
            if result["sessionIds"] != result["ids"]:
                raise SystemExit(f"Visible session diverged from canonical paused test: {result}")
            if not all(result["submitted"].get(qid) for qid in ("1-1", "1-2", "1-3", "1-4")):
                raise SystemExit(f"Answered progress was lost while resuming: {result}")
            browser.close()
    finally:
        server.shutdown()
    print("CONTINUE_PRACTICE_BROWSER_OK widths=320,390,768 full_session=20 saved_index=4 regression=covered")


if __name__ == "__main__":
    main()
