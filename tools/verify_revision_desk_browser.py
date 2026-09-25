#!/usr/bin/env python3
"""Exercise all-bank Quick Revision from More through the Practice engine."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
WRONG_ID = "marrow__ANAT_CH01_Q001"
BOOKMARK_ID = "physiology-9-6"


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    assert "NK_REVISION_DESK_V1_START" in html
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
            page.evaluate("""([wrong,bookmark]) => {
              const s=window.QB.getState(),now=Date.now();
              s.attempts[wrong]=[{id:'revision-wrong',selected:1,correct:false,at:now,reviewedAt:now,source:'practice',rating:1}];
              s.reviews[wrong]={schemaVersion:2,due:now-1000,nextReviewAt:now-1000,state:2,stability:1,difficulty:5,repetitions:1,lapses:1,elapsedDays:0,scheduledDays:1,lastReview:now-86400000};
              s.attempts[bookmark]=[{id:'revision-bookmark',selected:1,correct:true,at:now-2000,reviewedAt:now-2000,source:'practice',rating:3}];
              s.reviews[bookmark]={schemaVersion:2,due:now+86400000,nextReviewAt:now+86400000,state:2,stability:4,difficulty:5,repetitions:1,lapses:0,elapsedDays:0,scheduledDays:1,lastReview:now-2000};
              s.bookmarks[bookmark]={addedAt:now};
              window.QB.saveState();
            }""", [WRONG_ID, BOOKMARK_ID])
            page.evaluate("window.QB.nav('more')")
            page.get_by_role("button", name="Quick revision").click()
            page.get_by_role("heading", name="Quick revision").wait_for(state="visible")
            cards = page.locator(".nk-revision-card")
            assert cards.count() == 4, "Revision desk should show mistakes, bookmarks, unseen, and due"
            assert cards.nth(0).locator("b").inner_text() == "1"
            assert cards.nth(1).locator("b").inner_text() == "1"
            assert int(cards.nth(2).locator("b").inner_text().replace(",", "")) > 0
            assert cards.nth(3).locator("b").inner_text() == "1"
            scope = " ".join(page.locator(".nk-revision-scope").inner_text().split())
            assert scope == "All subjects · All question banks", f"Unexpected revision scope: {scope!r}"
            page.screenshot(path=str(output / "revision-desk-phone.png"), full_page=True)

            page.get_by_role("button", name="Focus questions").click()
            page.locator("#nk-revision-subject").select_option("Anatomy")
            assert page.locator(".nk-revision-scope").inner_text() == "Anatomy · All question banks"
            page.locator("#nk-revision-bank").select_option("Marrow")
            assert page.locator(".nk-revision-scope").inner_text() == "Anatomy · Marrow"
            assert cards.nth(0).locator("b").inner_text() == "1"
            assert cards.nth(1).locator("b").inner_text() == "0"
            page.locator("#nk-revision-topic").select_option(index=1)
            assert "Anatomy · Marrow · " in page.locator(".nk-revision-scope").inner_text()
            assert cards.nth(0).locator("b").inner_text() == "1"
            cards.nth(0).get_by_role("button", name="View all mistakes").click()
            page.get_by_role("heading", name="Mistakes").wait_for(state="visible")
            assert page.locator(".nk-revision-item").count() == 1
            assert "Anatomy · Marrow" in page.locator(".nk-v3-page-hero .nk-kicker").inner_text()
            page.get_by_role("button", name="Quick revision").click()
            page.get_by_role("button", name="Clear focus").click()
            assert " ".join(page.locator(".nk-revision-scope").inner_text().split()) == "All subjects · All question banks"
            assert cards.nth(1).locator("b").inner_text() == "1"

            cards.nth(0).get_by_role("button", name="View all mistakes").click()
            page.get_by_role("heading", name="Mistakes").wait_for(state="visible")
            items = page.locator(".nk-revision-item")
            assert items.count() == 1
            assert "Anatomy · Marrow" in items.first.locator("small").inner_text()
            page.locator(".nk-revision-search input").fill("zzrevisionnomatchzz")
            assert page.locator(".nk-revision-item:visible").count() == 0
            page.locator(".nk-revision-search input").fill("anatomy")
            assert page.locator(".nk-revision-item:visible").count() == 1
            items.first.get_by_role("button", name="Open question").click()
            page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.includes(id)", arg=WRONG_ID)

            previous_session = page.evaluate("window.QB.getState().activeSession?.id")
            page.evaluate("window.QB.nav('more')")
            page.get_by_role("button", name="Quick revision").click()
            cards = page.locator(".nk-revision-card")
            cards.nth(0).get_by_role("button", name="Practice 1 mistakes").click()
            page.wait_for_function(
                "([id,previous]) => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.includes(id) && window.QB.getState().activeSession?.id!==previous",
                arg=[WRONG_ID, previous_session],
            )
            assert page.evaluate("window.QB.getState().activeSession?.originRoute") == "wrong"

            page.evaluate("window.QB.nav('more')")
            page.get_by_role("button", name="Quick revision").click()
            cards = page.locator(".nk-revision-card")
            cards.nth(1).get_by_role("button", name="Practice 1 bookmarks").click()
            page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.includes(id)", arg=BOOKMARK_ID)

            page.evaluate("window.QB.nav('more')")
            page.get_by_role("button", name="Quick revision").click()
            cards = page.locator(".nk-revision-card")
            cards.nth(2).get_by_role("button", name="Practice 20 unseen").click()
            page.wait_for_function("location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.length===20")
            unseen_ids = page.evaluate("window.QB.getState().activeSession.questionIds")
            assert WRONG_ID not in unseen_ids and BOOKMARK_ID not in unseen_ids, "Unseen sampling included attempted questions"
            assert page.evaluate("""ids => {
              const s=window.QB.getState();
              return ids.every(id => !(s.attempts[id]||[]).some(a=>!a.isUndo) && s.fsrsReviewEligible?.[id]?.reason!=='skipped');
            }""", unseen_ids), "Unseen queue included attempted or submitted-skipped questions"

            page.evaluate("window.QB.nav('more')")
            page.get_by_role("button", name="Quick revision").click()
            cards = page.locator(".nk-revision-card")
            cards.nth(3).get_by_role("button", name="Review 1 due").click()
            page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.includes(id)", arg=WRONG_ID)
            assert page.evaluate("window.QB.getState().activeSession?.originRoute") == "fsrs"
            assert not errors, f"Browser errors: {errors!r}"
            print("REVISION_DESK_BROWSER_OK global=true mistakes=true bookmarks=true unseen=true due=true")
            browser.close()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
