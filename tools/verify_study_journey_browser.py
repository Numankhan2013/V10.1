#!/usr/bin/env python3
"""Exercise Home focus and fresh results in the generated PWA across view sizes."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    web = ROOT / "build/web"
    source = (web / "index.html").read_text(encoding="utf-8")
    assert "NK_TIMED_RESUME_CARD_V1_START" in source
    output = ROOT / "build/study-journey"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for label, width, height, zoom in (("phone-320", 320, 720, 1),
                                               ("phone-390", 390, 844, 1),
                                               ("phone-large-text", 390, 844, 1.25),
                                               ("tablet-820", 820, 1180, 1)):
                context = browser.new_context(viewport={"width": width, "height": height}, service_workers="block")
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB?.getState && document.querySelector('.nk-home-focus-action')")
                if zoom != 1:
                    page.evaluate("factor => { document.documentElement.style.zoom = factor; }", zoom)
                focus = page.locator(".nk-home-focus-card")
                expect(focus.get_by_role("button", name="Choose a subject")).to_be_visible()
                assert page.locator(".nk-timed-resume.is-home").count() == 0
                assert "Unique questions answered" in page.locator(".nk-home-progress-card").inner_text()
                assert "Answer accuracy" in page.locator(".nk-home-progress-card").inner_text()
                assert " / " not in page.locator(".nk-home-progress-card").inner_text()
                page.screenshot(path=str(output / f"{label}-home-empty.png"), full_page=True, animations="disabled")

                ids = page.evaluate("""() => {
                  const questions=window.SUBJECT_QBANK_DATA.subjects[0].questions;
                  const ids=questions.filter(q=>Number(q.correctOption)>=1&&Number(q.correctOption)<=4).slice(0,3).map(q=>String(q.id));
                  const state=window.QB.getState(),now=Date.now();
                  state.activeSession={id:'journey_exam',mode:'exam',title:'Study journey CBT',questionIds:ids,index:0,
                    answers:{[ids[0]]:1},markedForReview:{[ids[1]]:true},questionTimes:{},startedAt:now,deadlineAt:now+180000,
                    questionEnteredAt:now,timerMode:'global',timerEnabled:true,lifecycle:'active',originRoute:'tests'};
                  window.QB.saveState();window.QB.nav('dashboard');return ids;
                }""")
                expect(focus.get_by_role("button", name="Resume timed test")).to_be_visible()
                assert "Study journey CBT" in focus.inner_text()
                assert "1 of 3 answered · 1 marked for review" in focus.inner_text()
                assert page.locator(".nk-timed-resume.is-home").count() == 0
                page.screenshot(path=str(output / f"{label}-home-timed.png"), full_page=True, animations="disabled")
                focus.get_by_role("button", name="Resume timed test").click()
                page.wait_for_function("location.hash==='#exam' && window.QB.getState().activeSession?.id==='journey_exam'")
                page.evaluate("() => window.QB.nav('dashboard')")
                page.wait_for_function("location.hash==='#dashboard'")
                page.evaluate("""() => {const state=window.QB.getState();state.activeSession.deadlineAt=Date.now()-1;
                  window.QB.saveState();window.QB.nav('dashboard');}""")
                expect(focus.get_by_role("button", name="Finish timed test")).to_be_visible()
                focus.get_by_role("button", name="Finish timed test").click()
                page.wait_for_function("!window.QB.getState().activeSession && location.hash.startsWith('#result')")
                result = page.locator(".nk-result-v114")
                assert "Score: all questions" in result.inner_text()
                assert "Accuracy: answered questions" in result.inner_text()
                page.screenshot(path=str(output / f"{label}-result-partial.png"), full_page=True, animations="disabled")
                assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2"), label
                if label == "phone-390":
                    page.get_by_role("button", name="Review Solutions").click()
                    page.wait_for_function("window.QB.getState().activeSession?.mode==='review'")
                    page.evaluate("() => window.QB.nav('result',window.QB.getState().tests.at(-1).id)")
                    page.wait_for_function("document.querySelector('.nk-result-v114')")
                    page.get_by_role("button", name="Practise marked questions").click()
                    page.wait_for_function("window.QB.getState().activeSession?.mode==='practice'")
                assert not errors, errors
                context.close()
            # A fresh result with no answers has no answered-question accuracy.
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB?.getState")
            page.evaluate("""() => {const state=window.QB.getState(),q=window.SUBJECT_QBANK_DATA.subjects[0].questions[0];
              state.tests.push({id:'empty-result',title:'Unanswered test',kind:'exam',questionIds:[String(q.id)],answers:{},
                correct:0,incorrect:0,unattempted:1,total:1,attempted:0,totalTimeMs:1000,createdAt:Date.now(),timerMode:'global'});
              window.QB.saveState();window.QB.nav('result','empty-result');}""")
            expect(page.locator(".nk-result-percentages")).to_contain_text("Accuracy: answered questions")
            assert "—" in page.locator(".nk-result-percentages").inner_text()
            page.screenshot(path=str(output / "phone-390-result-unanswered.png"), full_page=True, animations="disabled")
            page.get_by_role("button", name="Retake timed CBT").click()
            page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print("STUDY_JOURNEY_BROWSER_OK focus=true expiry=true metrics=true result=true immediate=true views=4")


if __name__ == "__main__":
    main()
