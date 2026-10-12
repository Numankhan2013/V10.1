#!/usr/bin/env python3
"""Exercise the primary Revision hub, global counts, graphs and shared Practice engine."""

from functools import partial
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright
from app_page import built_page


ROOT = Path(__file__).resolve().parents[1]
WRONG_ID = "marrow__ANAT_CH01_Q001"
BOOKMARK_ID = "physiology-9-6"


def main() -> None:
    web = ROOT / "build/web"
    html = built_page(web)
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
            # Flame milestones are driven by the unchanged canonical study-day count.
            original_attempts=page.evaluate('JSON.parse(JSON.stringify(window.QB.getState().attempts))')
            for streak,level in [(0,'rest'),(1,'spark'),(3,'warm'),(7,'fire'),(14,'blaze'),(30,'radiant')]:
                page.evaluate("""([count,id])=>{
                  const s=window.QB.getState(),attempts=[];
                  for(let i=0;i<count;i++){const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()-i);attempts.push({id:'streak-'+i,at:d.getTime(),correct:true,selected:1,source:'practice'});}
                  s.attempts=count?{[id]:attempts}:{};
                  window.QB.saveState();window.QB.nav('more');
                }""",[streak,WRONG_ID])
                page.get_by_role('heading',name='More',exact=True).wait_for()
                page.locator('.bottom-nav button').filter(has_text='Home').click()
                card=page.locator('.nk-home-streak-card')
                card.wait_for()
                assert card.get_attribute('data-streak-level')==level
                # Geist lays the number out as its own flex item and counts it up when the
                # streak grows, so compare the settled, whitespace-normalised label.
                page.wait_for_function(
                    "text=>{const n=document.querySelector('.nk-home-streak-card .nk-home-streak-copy strong');return n&&n.textContent.replace(/\\s+/g,' ').trim()===text}",
                    arg=f'{streak} day streak',timeout=5000)
                assert card.get_attribute('aria-label').startswith(f'{streak} day study streak')
                if streak>=7:
                    assert card.locator('.is-linked').count()==datetime.now().weekday()
                for width,height,name in [(320,844,'small-phone'),(390,844,'phone'),(889,1280,'tablet')]:
                    page.set_viewport_size({'width':width,'height':height})
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                    assert card.locator('svg.nk-streak-flame-svg').is_visible()
                    page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
                    page.screenshot(path=str(output/f'streak-{streak}-{name}.png'),full_page=True)
            frontier=page.locator('.nk-home-week-day.is-frontier')
            assert frontier.count()==(0 if datetime.now().weekday()==6 else 1)
            if frontier.count():
                assert frontier.evaluate('(n)=>!n.nextElementSibling.classList.contains("is-done")'),'motion never marks a future day studied'
            linked=page.locator('.nk-home-week-day.is-linked')
            if not linked.count():
                assert datetime.now().weekday()==0,'linked connector should only be absent on Monday'
            # Geist draws the week as calm dots: studied days filled, the rest dashed rings.
            # It intentionally drops the legacy liquid connector/edge (::before/::after).
            dots=page.locator('.nk-home-week-day').evaluate_all("""nodes=>nodes.map(n=>{const i=getComputedStyle(n.querySelector('i'));
              return {done:n.classList.contains('is-done'),bg:i.backgroundColor,border:i.borderStyle,
                      pseudo:[getComputedStyle(n,'::before').display,getComputedStyle(n,'::after').display]}})""")
            assert len(dots)==7
            assert all((d['bg'] not in ('rgba(0, 0, 0, 0)','transparent'))==d['done'] for d in dots),dots
            assert all(d['border']=='dashed' for d in dots if not d['done']),dots
            assert all(p=='none' for d in dots for p in d['pseudo']),dots
            # Geist's living flame: a slow flicker driven by Motion while the streak is alive.
            flame=page.locator('.nk-home-streak-flame svg')
            before=flame.evaluate('(n)=>n.style.transform')
            page.wait_for_timeout(350)
            after=flame.evaluate('(n)=>n.style.transform')
            assert before!=after,'living flame should flicker while a streak is alive'
            page.emulate_media(reduced_motion='reduce')
            # Motion is decided when Home renders, so re-open Home under reduced motion.
            page.evaluate("window.QB.nav('more')")
            page.get_by_role('heading',name='More',exact=True).wait_for()
            page.locator('.bottom-nav button').filter(has_text='Home').click()
            page.wait_for_function("document.querySelector('.nk-home-streak-card')&&document.querySelector('.nk-home-streak-card').__nkg")
            flame=page.locator('.nk-home-streak-flame svg')
            before=flame.evaluate('(n)=>n.style.transform')
            page.wait_for_timeout(350)
            assert flame.evaluate('(n)=>n.style.transform')==before=='','reduced motion must keep the flame still'
            assert page.locator('.nk-streak-flame-svg').evaluate('(n)=>getComputedStyle(n).animationName')=='none'
            assert page.locator('.nk-home-week-day.is-today i').evaluate('(n)=>getComputedStyle(n).animationName')=='none'
            page.emulate_media(reduced_motion='no-preference')
            page.evaluate('(attempts)=>{window.QB.getState().attempts=attempts;window.QB.saveState();window.QB.nav("more");}',original_attempts)
            page.get_by_role('heading',name='More',exact=True).wait_for()
            page.locator('.bottom-nav button').filter(has_text='Home').click()
            page.locator('.nk-home-streak-card').wait_for()
            page.set_viewport_size({'width':390,'height':844})
            page.locator('.bottom-nav button').filter(has_text='Revision').click()
            page.get_by_role('heading',name='Revision',exact=True).wait_for()
            assert page.locator('.nk-revision-card.is-red b').inner_text()=='0'
            assert page.locator('.nk-revision-card.is-green b').inner_text()=='0'
            assert page.locator('.nk-revision-card.is-green button').is_disabled()
            # Geist draws empty days as a 2px baseline stub (span.nkg-zero) instead of nothing.
            assert page.locator('.nk-revision-forecast .nk-review-chart > span').evaluate_all(
                "(nodes)=>nodes.length===7&&nodes.every(n=>n.classList.contains('nkg-zero')&&n.querySelector('b').textContent.trim()==='0'&&n.querySelector('i').style.height==='0px'&&n.querySelector('i').getBoundingClientRect().height<=2)")
            page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
            page.screenshot(path=str(output/'revision-empty-phone.png'),full_page=True)
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
            page.get_by_role('heading',name='More',exact=True).wait_for()
            assert page.get_by_role('button',name='Quick revision').count()==0
            assert page.locator('.nk-settings-row').count()>=2
            assert page.locator('.nk-settings-row').evaluate_all('(nodes)=>nodes.every(n=>getComputedStyle(n).backgroundColor==="rgb(255, 255, 255)")')
            page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
            page.screenshot(path=str(output/'revision-more-phone.png'),full_page=True)
            page.evaluate("window.QB.nav('dashboard')")
            page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
            assert page.locator('.nk-home-revision .nk-count-due').inner_text() == '1'
            assert page.locator('.nk-home-revision .nk-count-missed').inner_text() == '1'
            for width,height,name in [(390,844,'phone'),(889,1280,'tablet')]:
                page.set_viewport_size({'width':width,'height':height})
                page.screenshot(path=str(output / ('revision-home-'+name+'.png')),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            page.locator(".bottom-nav button").filter(has_text="Revision").click()
            page.get_by_role("heading", name="Revision", exact=True).wait_for(state="visible")
            page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
            assert page.locator('.bottom-nav button[aria-current="page"]').inner_text().startswith('Revision')
            assert page.locator('.nk-revision-forecast .nk-review-chart span').count() == 7
            # Geist turns the forecast image into a group of selectable day columns with a live readout.
            forecast=page.locator('.nk-revision-forecast .nk-review-chart')
            assert forecast.get_attribute('role')=='group'
            assert forecast.locator('> span').first.get_attribute('aria-label').startswith('Today: 1 review')
            assert '1 review due' in ' '.join(page.locator('.nk-revision-forecast .nkg-fc-readout').inner_text().split())
            cards = page.locator(".nk-revision-card")
            assert cards.count() == 4, "Revision desk should show mistakes, bookmarks, unseen, and due"
            assert cards.nth(0).locator("b").inner_text() == "1"
            assert cards.nth(1).locator("b").inner_text() == "1"
            assert int(cards.nth(2).locator("b").inner_text().replace(",", "")) > 0
            assert cards.nth(3).locator("b").inner_text() == "1"
            scope = " ".join(page.locator(".nk-revision-scope").inner_text().split())
            assert scope == "All subjects · All question banks", f"Unexpected revision scope: {scope!r}"
            for width,height,name in [(390,844,'phone'),(889,1280,'tablet'),(320,740,'small-phone')]:
                page.set_viewport_size({'width':width,'height':height})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                assert cards.first.evaluate('(n)=>getComputedStyle(n).borderColor') == cards.last.evaluate('(n)=>getComputedStyle(n).borderColor')
                page.screenshot(path=str(output / ('revision-desk-'+name+'.png')),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            page.get_by_role('button',name='Open FSRS',exact=True).click()
            page.get_by_role('heading',name='FSRS Review',exact=True).wait_for()
            assert page.locator('.nk-fsrs-page-v3 .nk-review-chart span').count()==7
            assert page.locator('.bottom-nav button[aria-current="page"]').inner_text().startswith('Revision')
            page.locator('.nk-back-link').filter(has_text='Revision').click()
            page.get_by_role('heading',name='Revision',exact=True).wait_for()
            page.get_by_role('button',name='Review settings',exact=True).click()
            page.get_by_role('heading',name='Review settings',exact=True).wait_for()
            assert page.locator('.nk-fsrs-settings').count()==1
            assert page.locator('.bottom-nav button[aria-current="page"]').inner_text().startswith('Revision')
            page.get_by_role('button',name='Cancel',exact=True).click()
            page.locator('.bottom-nav button').filter(has_text='Revision').click()


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
            page.locator(".nk-back-link").filter(has_text="Revision").click()
            page.get_by_role("button", name="Clear focus").click()
            assert " ".join(page.locator(".nk-revision-scope").inner_text().split()) == "All subjects · All question banks"
            # Geist re-renders the counts a frame after the scope clears.
            expect(cards.nth(1).locator("b")).to_have_text("1")

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
            page.evaluate("window.QB.nkOpenRevisionHub()")
            page.get_by_role("heading",name="Revision",exact=True).wait_for()
            cards = page.locator(".nk-revision-card")
            cards.nth(0).get_by_role("button", name="Practice mistakes").click()
            page.wait_for_function(
                "([id,previous]) => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.includes(id) && window.QB.getState().activeSession?.id!==previous",
                arg=[WRONG_ID, previous_session],
            )
            assert page.evaluate("window.QB.getState().activeSession?.originRoute") == "quick-revision"

            page.evaluate("window.QB.nkOpenRevisionHub()")
            page.get_by_role("heading",name="Revision",exact=True).wait_for()
            cards = page.locator(".nk-revision-card")
            cards.nth(1).get_by_role("button", name="Practice bookmarks").click()
            page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.includes(id)", arg=BOOKMARK_ID)

            page.evaluate("window.QB.nkOpenRevisionHub()")
            page.get_by_role("heading",name="Revision",exact=True).wait_for()
            cards = page.locator(".nk-revision-card")
            cards.nth(2).get_by_role("button", name="Practice 20 unseen").click()
            page.wait_for_function("location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.length===20")
            unseen_ids = page.evaluate("window.QB.getState().activeSession.questionIds")
            assert WRONG_ID not in unseen_ids and BOOKMARK_ID not in unseen_ids, "Unseen sampling included attempted questions"
            assert page.evaluate("""ids => {
              const s=window.QB.getState();
              return ids.every(id => !(s.attempts[id]||[]).some(a=>!a.isUndo) && s.fsrsReviewEligible?.[id]?.reason!=='skipped');
            }""", unseen_ids), "Unseen queue included attempted or submitted-skipped questions"

            page.evaluate("window.QB.nkOpenRevisionHub()")
            page.get_by_role("heading",name="Revision",exact=True).wait_for()
            cards = page.locator(".nk-revision-card")
            cards.nth(3).get_by_role("button", name="Review due").click()
            page.wait_for_function("id => location.hash==='#practice' && window.QB.getState().activeSession?.questionIds?.includes(id)", arg=WRONG_ID)
            assert page.evaluate("window.QB.getState().activeSession?.originRoute") == "quick-revision"
            assert not errors, f"Browser errors: {errors!r}"
            print("REVISION_DESK_BROWSER_OK global=true mistakes=true bookmarks=true unseen=true due=true")
            browser.close()
        from verify_revision_session_browser import main as verify_revision_sessions
        verify_revision_sessions()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
