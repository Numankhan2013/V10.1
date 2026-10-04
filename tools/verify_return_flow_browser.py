#!/usr/bin/env python3
"""Exercise revision return destinations, checkpoint recovery and saved-test feedback."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright
from verify_learning_insights_browser import PROBE
ROOT=Path(__file__).resolve().parents[1]
def main():
    web = ROOT/'build/web'
    html = (web/'index.html').read_text()
    assert 'id="nk-visual-refinement-v1"' in html
    probe = PROBE+'window.__returnQuestion=()=>nkCurrentQuestion();window.__returnPause=()=>nkPausePractice();window.__returnCheckpoint=id=>nkPracticeFindCheckpoint(id);window.__returnRestore=cp=>nkPracticeSessionFromCheckpoint(cp);window.__returnPersistence=saveState;window.__returnFailSave=()=>{saveState=()=>false;};window.__returnSave=()=>{saveState=window.__returnPersistence;};\n'
    diagnostic = html.replace('  window.QB={', probe+'  window.QB={', 1).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?',1)[0] in ('/','/index.html'):
                self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()
                try:
                    self.wfile.write(diagnostic)
                except (BrokenPipeError,ConnectionResetError):
                    pass
            else:
                super().do_GET()

        def log_message(self,*_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(web)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    output = ROOT/'build/return-flow-checks';output.mkdir(exist_ok=True)
    reports=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for width,height in [(390,844),(820,1180)]:
                context=browser.new_context(viewport={'width':width,'height':height},service_workers='block',has_touch=True,is_mobile=True)
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin);page.wait_for_function('QB?.getState');page.evaluate('QB.startAllPractice()')
                page.wait_for_selector('.option');q=page.evaluate('__returnQuestion()')
                page.evaluate('(id)=>{QB.getState().bookmarks[id]={addedAt:Date.now()};QB.saveState();QB.nav("quick-revision");}',q['id'])
                page.get_by_role('button',name='View all bookmarks',exact=True).click()
                search=page.locator('.nk-revision-search input');search.fill(q['subject'])
                assert search.evaluate('n=>getComputedStyle(n).fontSize')=='16px'
                page.locator('.nk-revision-item:visible button').first.click();page.wait_for_selector('.option')
                sid=page.evaluate('QB.getState().activeSession.id')
                assert page.evaluate('QB.getState().activeSession.originRoute')=='revision-browse/bookmarks'
                assert page.evaluate('(id)=>__returnCheckpoint(id)',sid) is None,'bookmark review created normal Practice checkpoint'
                page.locator('.option').first.click();page.evaluate('QB.endSession()');page.locator('.nk-na-back').wait_for()
                assert page.locator('.nk-na-back').get_attribute('aria-label')=='Back to Bookmarks'
                page.locator('.nk-na-back').click();page.wait_for_selector('.nk-revision-search input')
                assert page.locator('.nk-revision-search input').input_value()==q['subject']
                page.screenshot(path=str(output/f'bookmarks-return-{width}.png'))
                page.evaluate('(q)=>{const s=QB.getState();s.attempts[q.id]=[{id:"return-wrong",correct:false,selected:Number(q.correctOption)%q.options.length+1,at:Date.now(),source:"practice"}];QB.saveState();QB.nav("quick-revision");}',q)
                page.get_by_role('button',name='View all mistakes',exact=True).click();page.locator('.nk-revision-search input').fill(q['subject'])
                page.locator('.nk-revision-item:visible button').first.click();page.wait_for_selector('.option')
                sid=page.evaluate('QB.getState().activeSession.id')
                assert page.evaluate('QB.getState().activeSession.originRoute')=='revision-browse/wrong'
                assert page.evaluate('(id)=>__returnCheckpoint(id)',sid) is None
                page.locator('.option').nth(int(q['correctOption'])%len(q['options'])).click();page.evaluate('QB.endSession()')
                page.locator('.nk-na-back').wait_for();assert page.locator('.nk-na-back').get_attribute('aria-label')=='Back to Mistakes'
                page.locator('.nk-na-back').click();page.wait_for_selector('.nk-revision-search input')
                assert page.locator('.nk-revision-search input').input_value()==q['subject']
                page.screenshot(path=str(output/f'mistakes-return-{width}.png'))
                # Search sessions remain resumable, including restoration without the live object.
                page.evaluate('QB.nav("question-search")');page.locator('.nk-question-search-filters select').first.select_option('Anatomy')
                page.locator('.nk-question-search-item button').first.click();page.wait_for_selector('.option')
                page.locator('.option').first.click();sid=page.evaluate('QB.getState().activeSession.id')
                page.evaluate('__returnPause()');cp=page.evaluate('(id)=>__returnCheckpoint(id)',sid)
                assert cp['context']['originRoute']=='question-search'
                restored=page.evaluate('(cp)=>__returnRestore(cp)',cp)
                assert restored['originRoute']=='question-search'
                assert restored['questionIds']==cp['sessionQuestionIds'] and restored['answers']==cp['answers']
                assert restored['submitted']==cp['submitted'] and restored['questionTimes']==cp['questionTimes']
                legacy={**cp,'context':{k:v for k,v in cp['context'].items() if k!='originRoute'}}
                assert page.evaluate('(cp)=>__returnRestore(cp).originRoute',legacy)=='topics'
                page.evaluate('(q)=>{const s=QB.getState();s.tests.push({id:"return-rename",title:"Original test",updatedAt:7,questionIds:[q.id],answers:{[q.id]:q.correctOption},createdAt:Date.now(),total:1,correct:1,incorrect:0,unattempted:0});QB.saveState();QB.nav("result","return-rename");}',q)
                page.get_by_role('button',name='Rename test',exact=True).click();title=page.locator('#nk-na-title');title.fill(' ')
                page.get_by_role('button',name='Save name',exact=True).click()
                assert title.get_attribute('aria-invalid')=='true'
                assert 'Enter a test name' in page.locator('#nk-na-rename-status').inner_text()
                title.fill('New title with α and العربية')
                assert title.get_attribute('aria-invalid') is None
                assert title.evaluate('n=>getComputedStyle(n).fontSize')=='16px'
                page.evaluate('__returnFailSave()');page.get_by_role('button',name='Save name',exact=True).click()
                assert 'Your text is still here' in page.locator('#nk-na-rename-status').inner_text()
                assert title.input_value()=='New title with α and العربية'
                assert page.evaluate('QB.getState().tests.find(t=>t.id==="return-rename").title')=='Original test'
                assert page.evaluate('QB.getState().tests.find(t=>t.id==="return-rename").updatedAt')==7
                page.screenshot(path=str(output/f'rename-failure-{width}.png'))
                page.evaluate('__returnSave()');page.get_by_role('button',name='Save name',exact=True).click()
                assert page.evaluate('document.activeElement.getAttribute("aria-label")')=='Rename test'
                assert page.evaluate('QB.getState().tests.find(t=>t.id==="return-rename").title')=='New title with α and العربية'
                page.evaluate('(id)=>{QB.getState().savedMocks=[{id:"return-one",name:"First mock",questionIds:[id],createdAt:1,updatedAt:1},{id:"return-two",name:"Second mock",questionIds:[id],createdAt:2,updatedAt:2}];QB.saveState();QB.nav("tests");}',q['id'])
                remove=page.locator('.nk-na-remove').last;size=remove.bounding_box();assert size['width']>=44 and size['height']>=44
                page.evaluate('__returnFailSave()');remove.focus();page.keyboard.press('Enter')
                assert page.locator('.nk-na-mock-row').count()==2
                assert page.evaluate('document.activeElement.matches(".nk-na-remove")')
                page.evaluate('__returnSave()');page.keyboard.press('Enter')
                assert page.locator('.nk-na-mock-row').count()==1
                assert page.evaluate('document.activeElement.matches(".nk-na-mock-row>button:first-child")')
                page.locator('.nk-na-remove').focus();page.keyboard.press('Enter')
                assert page.locator('.nk-na-mock-row').count()==0
                assert page.evaluate('document.activeElement.tagName')=='H1'
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert not errors,errors
                reports.append({'width':width,'bookmark_return':True,'mistakes_return':True,'restore_origin':True,'legacy_recovery':True,'rename_failure_retry':True,'remove_keyboard':True,'remove_rollback':True})
                context.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    (output/'report.json').write_text(json.dumps(reports,indent=2))
    print('RETURN_FLOW_BROWSER_OK',json.dumps(reports))
if __name__=='__main__':main()
