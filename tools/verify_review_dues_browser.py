#!/usr/bin/env python3
"""Due reviews by subject, bank and topic: counts, drill-down and a scoped, pausable review session."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright
from app_page import built_page


ROOT = Path(__file__).resolve().parents[1]
ANAT_DUE = "marrow__ANAT_CH01_Q001"
ANAT_MATURE = "marrow__ANAT_CH01_Q002"
ANAT_LEARNING = "marrow__ANAT_CH02_Q001"
PHYSIO_DUE = "physiology-9-6"

SEED = """([dueA,matureA,learnA,dueP])=>{
  const s=window.QB.getState(),now=Date.now(),day=86400000;
  const attempt=(id,correct)=>[{id:'rd-'+id,selected:1,correct,at:now-3*day,reviewedAt:now-3*day,source:'practice',rating:correct?3:1}];
  const review=(stateNo,stability,due)=>({schemaVersion:2,due,nextReviewAt:due,state:stateNo,stability,difficulty:5,repetitions:2,lapses:0,elapsedDays:3,scheduledDays:3,lastReview:now-3*day});
  s.attempts={[dueA]:attempt(dueA,true),[matureA]:attempt(matureA,true),[learnA]:attempt(learnA,true),[dueP]:attempt(dueP,true)};
  s.reviews={[dueA]:review(2,5,now-1000),[matureA]:review(2,30,now+10*day),[learnA]:review(1,1,now-1000),[dueP]:review(2,4,now-1000)};
  s.activeSession=null;window.QB.saveState();
}"""


def main() -> None:
    web = ROOT / "build/web"
    html = built_page(web)
    assert "nkReviewDuesPage" in html
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for scheme in ("light", "dark"):
                context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block", color_scheme=scheme)
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState")
                page.evaluate(SEED, [ANAT_DUE, ANAT_MATURE, ANAT_LEARNING, PHYSIO_DUE])

                # The Revision Due card keeps Review due and adds the way in by subject.
                page.evaluate("window.QB.nkOpenRevisionHub()")
                page.get_by_role("heading", name="Revision", exact=True).wait_for()
                page.get_by_role("button", name="Due reviews by subject and topic").click()
                page.get_by_role("heading", name="Due reviews", exact=True).wait_for()
                assert page.locator(".bottom-nav .nav-item.active").inner_text().strip().startswith("Revision")

                rows = page.locator(".nk-rd-list > .nk-rd-row")
                assert rows.count() == 2, rows.count()
                first = rows.nth(0)
                assert "Anatomy" in first.locator("strong").inner_text()
                assert first.locator(".nk-rd-counts b.is-due").inner_text() == "2"
                assert first.locator(".nk-rd-counts b.is-learn").inner_text() == "1"
                assert first.locator(".nk-rd-counts b.is-mature").inner_text() == "1"
                assert page.locator(".nk-rd-all").inner_text().startswith("Review all 3 due")
                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
                page.screenshot(path=str(output / f"review-dues-{scheme}.png"), full_page=True)

                # Drill into the subject: banks with their topics, each reviewable on its own.
                first.locator(".nk-rd-open").click()
                page.get_by_role("heading", name="Anatomy", exact=True).wait_for()
                topics = page.locator(".nk-rd-bank .nk-rd-row.is-topic")
                assert topics.count() == 2, topics.count()
                assert page.locator(".nk-rd-bank[open]").count() >= 1
                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth")
                page.screenshot(path=str(output / f"review-dues-subject-{scheme}.png"), full_page=True)

                # Topic 1 holds one due card and one mature card: only the due one is reviewed.
                topic_one = topics.filter(has=page.locator("b.is-mature", has_text="1")).first
                topic_one.locator("button.nk-rd-go").click()
                page.wait_for_selector(".option")
                session = page.evaluate("window.QB.getState().activeSession")
                assert session["questionIds"] == [ANAT_DUE], session["questionIds"]
                assert session["context"] == "fsrs"
                scope = session["practiceContext"]["revisionScope"]
                assert scope["subject"] == "Anatomy" and scope["topic"], scope

                # Review all in a subject leaves the other subject alone.
                page.evaluate("window.QB.getState().activeSession=null;window.QB.saveState()")
                page.evaluate("window.QB.nkReviewDuesStart({subject:'Physiology'})")
                page.wait_for_selector(".option")
                assert page.evaluate("window.QB.getState().activeSession.questionIds") == [PHYSIO_DUE]
                assert not errors, errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print("REVIEW_DUES_BROWSER_OK")


if __name__ == "__main__":
    main()
