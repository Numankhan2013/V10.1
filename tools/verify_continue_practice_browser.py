#!/usr/bin/env python3
"""Exercise the single-grid Practice end flow and durable Pause/Continue in the built PWA."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def button_labels(locator):
    return [locator.nth(i).inner_text().strip() for i in range(locator.count())]


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    for marker in ("NK_CONTINUE_PRACTICE_RESUME_V1_START", "NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START"):
        if marker not in html:
            raise SystemExit(f"Practice flow layer missing from built PWA: {marker}")

    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()

            for width in (320, 390, 768):
                context = browser.new_context(
                    viewport={"width": width, "height": 844},
                    service_workers="block",
                    reduced_motion="reduce",
                )
                page = context.new_page()
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState")
                page.evaluate("window.QB.practiceOne('1-1')")

                # Question screen: the session footer must be only Previous + Next.
                footer = page.locator(".nk-session-footer")
                footer.wait_for(state="visible")
                if page.locator(".nk-practice-session-controls").count():
                    raise SystemExit(f"Pause/Submit leaked back onto the question screen at {width}px")
                labels = button_labels(footer.locator(".fixed-actions-inner button"))
                if labels != ["Previous", "Next"]:
                    raise SystemExit(f"Question footer is not Previous/Next only at {width}px: {labels}")

                # Opening the grid must go straight to the one final review sheet.
                page.evaluate("window.QB.openQuestionNavigator()")
                review = page.locator("#nk-session-review")
                review.wait_for(state="visible")
                if page.locator("#qb-question-navigator").count():
                    raise SystemExit(f"Redundant Question Navigator still exists at {width}px")
                if not review.evaluate("el => el.classList.contains('nk-practice-final-review')"):
                    raise SystemExit(f"Final Practice review sheet was not normalized at {width}px")

                actions = review.locator(".nk-session-review-actions")
                action_labels = button_labels(actions.locator("button"))
                if action_labels != ["Pause", "Submit"]:
                    raise SystemExit(f"Final review actions are not exactly Pause/Submit at {width}px: {action_labels}")
                if review.get_by_role("button", name="Back to question", exact=False).count():
                    raise SystemExit("Back to question must not exist in the final Practice grid")
                if review.get_by_role("button", name="Review unanswered", exact=False).count():
                    raise SystemExit("Review unanswered must not exist in the final Practice grid")
                if footer.is_visible():
                    raise SystemExit(f"Question footer is visible over the final grid at {width}px")

                # The final sheet must retain question navigation controls beyond Pause/Submit.
                if review.locator("button").count() < 3:
                    raise SystemExit(f"Final grid lost question navigation controls at {width}px")

                review.screenshot(path=str(output / f"practice-final-review-{width}.png"))
                context.close()

            # Durable Pause/Continue: pause only from the final grid, then restore the
            # complete original test and its saved question position/progress.
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            page.evaluate("window.QB.practiceOne('1-1')")
            page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              s.questionIds=Array.from({length:20},(_,i)=>`1-${i+1}`);
              s.index=4;
              s.answers={'1-1':1,'1-2':1,'1-3':1,'1-4':1};
              s.submitted={'1-1':true,'1-2':true,'1-3':true,'1-4':true};
              s.questionTimes={'1-5':10};
            }""")
            page.evaluate("window.QB.openSessionReview()")
            review = page.locator("#nk-session-review")
            review.wait_for(state="visible")
            review.get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")

            # Reproduce the reported regression: an older resume path could persist
            # only the current question even though sessionQuestionIds still held all 20.
            page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              s.questionIds=['1-5'];
              s.index=0;
            }""")
            page.evaluate("window.QB.nkContinueRecentPractice()")
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")
            result = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {
                ids:s.questionIds,
                current:s.questionIds[s.index],
                index:s.index,
                submitted:s.submitted,
                sessionIds:s.sessionQuestionIds
              };
            }""")
            if len(result["ids"]) != 20 or result["ids"][:2] != ["1-1", "1-2"] or result["ids"][-1] != "1-20":
                raise SystemExit(f"Pause/Continue did not restore the complete 20-question session: {result}")
            if result["current"] != "1-5" or result["index"] != 4:
                raise SystemExit(f"Pause/Continue did not restore the saved question position: {result}")
            if result["sessionIds"] != result["ids"]:
                raise SystemExit(f"Visible session diverged from the canonical paused test: {result}")
            if not all(result["submitted"].get(qid) for qid in ("1-1", "1-2", "1-3", "1-4")):
                raise SystemExit(f"Answered progress was lost while resuming: {result}")
            context.close()
            browser.close()
    finally:
        server.shutdown()

    print("CONTINUE_PRACTICE_BROWSER_OK widths=320,390,768 single_review_grid=true footer=previous_next full_session=20 saved_index=4")


if __name__ == "__main__":
    main()
