#!/usr/bin/env python3
"""Verify compact screen geometry without reducing the controls or their labels."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]

def main():
    web=ROOT/'build/web';assert 'NK_APP_CLARITY_V1_START' in (web/'index.html').read_text()
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(web)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    output=ROOT/'build/ui-checks';output.mkdir(exist_ok=True,parents=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            for width,height in [(320,844),(390,844),(820,1180)]:
                context=browser.new_context(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
                page=context.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin,wait_until='domcontentloaded');page.wait_for_function('window.QB?.getState')
                page.evaluate('''()=>{const s=window.QB.getState();s.attempts['1-1']=[{id:'clarity-miss',selected:1,correct:false,at:Date.now(),source:'practice'}];s.bookmarks['1-2']=true;window.QB.saveState();}''')
                for route,title in [('quick-revision','Revision'),('analytics','Insights'),('tests','Timed tests'),('more','More'),('fsrs','FSRS Review'),('fsrs-settings','Review settings'),('study-library','My Subjects'),('question-search','Find a question'),('notes','My notes'),('dashboard',None)]:
                    page.evaluate('(r)=>window.QB.nav(r)',route)
                    if title:expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
                    page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(route,width)
                    text=page.locator('#app').inner_text()
                    assert 'Small steps every day' not in text
                    assert 'Questions you have answered incorrectly.' not in text
                    if route=='quick-revision':
                        assert page.locator('.nk-revision-card').count()==4
                        assert page.locator('.nk-revision-card.is-red b').inner_text()=='1'
                        assert page.locator('.nk-revision-card.is-violet b').inner_text()=='1'
                        due=page.locator('.nk-revision-card.is-green').bounding_box()
                        nav=page.locator('.bottom-nav').bounding_box()
                        page.screenshot(path=str(output/f'clarity-revision-top-{width}.png'))
                        assert due['y']+due['height']<(nav['y'] if width<768 else height), (width,due,nav,page.locator('.nk-revision-list').inner_text(),'All four revision queues must fit above phone navigation')
                        page.get_by_role('button',name='Focus questions',exact=True).click()
                        expect(page.locator('#nk-revision-subject')).to_be_visible()
                        page.locator('#nk-revision-subject').select_option('Biochemistry')
                        assert 'Questions you have' not in page.locator('.nk-revision-list').inner_text()
                        assert 'Choose one area' not in page.locator('.nk-revision-focus-wrap').inner_text()
                        assert 'Scheduled reviews for this focus' not in page.locator('.nk-revision-forecast').inner_text()
                        page.get_by_role('button',name='Hide focus',exact=True).click()
                    if route=='analytics':
                        assert page.locator('.nk-li-year-activity').bounding_box()['y']<280,(width,'heatmap starts too low')
                        assert page.locator('.nk-li-year-grid button').count()>=365
                        assert page.locator('.nk-li-card').count()==8
                        assert page.get_by_role('heading',name='Missed-question revision',exact=True).count()==0
                    if route=='fsrs-settings':
                        assert page.locator('.nk-fsrs-field input').count()==3
                        expect(page.get_by_role('button',name='Save changes',exact=True)).to_be_visible()
                        assert page.locator('.nk-clarity-help').count()==1
                    page.screenshot(path=str(output/f'clarity-{route}-{width}.png'),full_page=True)
                page.evaluate('window.QB.openMultiSubjectTestBuilder()')
                expect(page.locator('.nk-cbt-builder')).to_be_visible()
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                expect(page.get_by_role('button',name='Continue to topics',exact=True)).to_be_visible()
                page.evaluate("window.QB.nav('dashboard');window.QB.openStudyModuleBuilder()")
                expect(page.locator('.nk-module-builder')).to_be_visible()
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert not errors,errors
                context.close()
            browser.close()
    finally:server.shutdown()
    print('APP_CLARITY_BROWSER_OK viewports=320,390,820 screens=10 builders=2 counts=true focus=true controls=true all_revision_queues_visible=true no_overflow=true')
if __name__=='__main__':main()
