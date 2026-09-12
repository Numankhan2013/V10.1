#!/usr/bin/env python3
"""Exercise the single-grid Practice end flow and durable Home Pause/Continue in the built PWA."""

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

            # Real Home lifecycle regression test. Start a genuine Practice 20, pause
            # it from the final grid, then click the actual visible Continue Practice
            # button. The same session, all IDs, progress and position must survive.
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            page.evaluate("window.QB.startAllPractice()")
            page.wait_for_function("window.QB.getState().activeSession?.questionIds?.length > 1")

            original = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {id:s.id, ids:[...s.questionIds]};
            }""")
            if len(original["ids"]) < 5:
                raise SystemExit(f"Practice 20 did not create a multi-question session: {original}")
            current_id = original["ids"][4]
            answered_ids = original["ids"][:4]

            page.evaluate("""({answered,current}) => {
              const s=window.QB.getState().activeSession;
              s.index=4;
              s.answers={};
              s.submitted={};
              answered.forEach((id,i)=>{s.answers[id]=i%4;s.submitted[id]=true;});
              s.questionTimes={[current]:10};
            }""", {"answered": answered_ids, "current": current_id})

            page.evaluate("window.QB.openSessionReview()")
            review = page.locator("#nk-session-review")
            review.wait_for(state="visible")
            review.get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")

            paused = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {id:s.id, ids:s.questionIds, sessionIds:s.sessionQuestionIds, index:s.pausedIndex};
            }""")
            if paused["id"] != original["id"] or paused["ids"] != original["ids"] or paused["sessionIds"] != original["ids"] or paused["index"] != 4:
                raise SystemExit(f"Pause did not preserve the original Practice session: {paused}")

            # This exact Home button used to call legacy continuePractice(), which
            # created startSession([q.id]) and produced the user-visible 1/1 bug.
            continue_button = page.locator("button.nk-home-v4-action-continue")
            continue_button.wait_for(state="visible")
            continue_button.click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")

            result = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {
                id:s.id,
                ids:s.questionIds,
                current:s.questionIds[s.index],
                index:s.index,
                submitted:s.submitted,
                sessionIds:s.sessionQuestionIds
              };
            }""")
            if result["id"] != original["id"]:
                raise SystemExit(f"Home Continue created a new session instead of resuming the paused one: {result}")
            if result["ids"] != original["ids"] or len(result["ids"]) <= 1:
                raise SystemExit(f"Home Continue collapsed the paused test to a one-question session: {result}")
            if result["current"] != current_id or result["index"] != 4:
                raise SystemExit(f"Home Continue did not restore the saved question position: {result}")
            if result["sessionIds"] != original["ids"]:
                raise SystemExit(f"Visible session diverged from the canonical paused test: {result}")
            if not all(result["submitted"].get(qid) for qid in answered_ids):
                raise SystemExit(f"Answered progress was lost while resuming from Home: {result}")

            # Persisted-state repair: a previous buggy client may have reduced only
            # questionIds. The preserved sessionQuestionIds must still rebuild all IDs
            # when the same Home Continue button is used again.
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            page.evaluate("""({current}) => {
              const s=window.QB.getState().activeSession;
              s.questionIds=[current];
              s.index=0;
            }""", {"current": current_id})
            page.locator("button.nk-home-v4-action-continue").click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")
            repaired = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {id:s.id,ids:s.questionIds,index:s.index,current:s.questionIds[s.index]};
            }""")
            if repaired["id"] != original["id"] or repaired["ids"] != original["ids"] or repaired["index"] != 4 or repaired["current"] != current_id:
                raise SystemExit(f"Home Continue did not repair persisted one-question state: {repaired}")

            context.close()
            browser.close()
    finally:
        server.shutdown()

    print("CONTINUE_PRACTICE_BROWSER_OK widths=320,390,768 single_review_grid=true footer=previous_next home_continue=true real_practice_session=true saved_index=4")


if __name__ == "__main__":
    main()
