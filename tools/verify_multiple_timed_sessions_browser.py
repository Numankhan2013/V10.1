#!/usr/bin/env python3
"""Exercise two independent timed tests in the generated PWA on phone and tablet."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    assert "NK_TIMED_RESUME_CARD_V1_START" in html
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width, height in ((390, 844), (820, 1180)):
                context = browser.new_context(viewport={"width": width, "height": height}, service_workers="block")
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#tests", wait_until="domcontentloaded")
                page.wait_for_function("window.QB?.getState")

                page.evaluate("window.QB.openMultiSubjectTestBuilder()")
                page.locator("#modal").get_by_role("button", name="Start Exam").click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                first = page.evaluate("""() => {
                  const s=window.QB.getState().activeSession;
                  return {id:s.id,title:s.title,deadlineAt:s.deadlineAt,questionIds:s.questionIds};
                }""")
                assert len(first["questionIds"]) > 1

                page.evaluate("window.QB.nav('tests')")
                page.evaluate("window.QB.nkStartTopicTimedTest('1-1')")
                dialog = page.locator("#nk-timed-session-conflict")
                dialog.wait_for(state="visible")
                dialog.get_by_role("button", name="Keep test and continue").click()
                page.wait_for_function("s=>window.QB.getState().activeSession?.id!==s", arg=first["id"])
                second = page.evaluate("""() => {
                  const s=window.QB.getState().activeSession;
                  return {id:s.id,title:s.title,timerMode:s.timerMode,questionIds:s.questionIds};
                }""")
                assert second["timerMode"] == "per-question", "deferred topic test lost its strict timer"
                assert second["questionIds"]
                assert page.evaluate("id=>window.QB.getState().timedSessions.find(s=>s.id===id).deadlineAt", first["id"]) == first["deadlineAt"]

                page.evaluate("window.QB.nav('tests')")
                cards = page.locator(".nk-timed-resume.is-tests")
                assert cards.count() == 2, "both unfinished tests must appear on Tests"
                page.screenshot(path=str(output / f"timed-sessions-{width}.png"), full_page=True)

                page.reload(wait_until="domcontentloaded")
                page.wait_for_function("window.QB?.getState")
                page.evaluate("window.QB.nav('tests')")
                assert page.locator(".nk-timed-resume.is-tests").count() == 2, "reload lost a timed test"
                page.locator(".nk-timed-resume.is-tests").filter(has_text=first["title"]).get_by_role("button", name="Resume timed test").click()
                page.wait_for_function("id=>window.QB.getState().activeSession?.id===id", arg=first["id"])
                assert page.evaluate("window.QB.getState().activeSession.deadlineAt") == first["deadlineAt"]
                assert page.evaluate("id=>window.QB.getState().timedSessions.find(s=>s.id===id)?.lifecycle", second["id"]) == "paused"

                page.evaluate("window.QB.submitExam(false)")
                page.wait_for_function("id=>window.QB.getState().tests.some(t=>t.id==='exam_'+id)", arg=first["id"])
                assert page.evaluate("id=>window.QB.getState().timedSessions.find(s=>s.id===id)?.lifecycle", first["id"]) == "submitted"
                page.evaluate("window.QB.nav('tests')")
                assert page.locator(".nk-timed-resume.is-tests").count() == 1, "finishing one test removed the other"
                page.locator(".nk-timed-resume.is-tests").get_by_role("button", name="Resume timed test").click()
                page.wait_for_function("id=>window.QB.getState().activeSession?.id===id", arg=second["id"])
                assert page.evaluate("window.QB.getState().activeSession.timerMode") == "per-question"
                assert not errors, errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print("MULTIPLE_TIMED_SESSIONS_BROWSER_OK phone=true tablet=true reload=true independentSubmission=true")


if __name__ == "__main__":
    main()
