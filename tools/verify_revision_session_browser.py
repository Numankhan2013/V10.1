#!/usr/bin/env python3
"""Continuous Revision queue snapshots, durable Pause and answered-only Finish in the real app."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import threading,json
from playwright.sync_api import sync_playwright
from verify_learning_insights_browser import PROBE
ROOT=Path(__file__).resolve().parents[1]

SEED='''(kind)=>{
 const s=QB.getState(),qs=__nkLearningTest.questions().filter(q=>q.subject==='Biochemistry'&&q.bank==='Marrow').slice(0,27),now=Date.now();
 Object.assign(s,{attempts:{},bookmarks:{},tests:[],activeSession:null,reviews:{},fsrsReviewEligible:{},fsrsRatingRevisions:{},normalPracticeCheckpoints:[],normalPracticeCheckpoint:null,fsrsPreferences:{desiredRetention:.9,dailyCap:23,maximumInterval:365}});
 for(const q of qs){if(kind==='bookmarks')s.bookmarks[q.id]={addedAt:now};else s.attempts[q.id]=[{id:'revision-seed-'+q.id,selected:Number(q.correctOption)%q.options.length+1,correct:false,at:now-86400000,reviewedAt:now-86400000,source:'practice',rating:1}];}
 QB.saveState();QB.nkOpenRevisionHub();return qs.map(q=>q.id);
}'''

def main():
    web=ROOT/'build/web';html=(web/'index.html').read_text();assert 'NK_REVISION_SESSION_V1_START' in html
    probe=PROBE+'''window.__revisionCurrent=()=>nkCurrentQuestion();window.__revisionRestore=cp=>nkPracticeSessionFromCheckpoint(cp);window.__revisionDue=()=>nkFsrsQueue({});window.__revisionFail=fail=>{window.__NK_STORAGE_ADAPTER=fail?{getItem:k=>localStorage.getItem(k),setItem:()=>{throw new Error('Revision QA storage failure');},removeItem:k=>localStorage.removeItem(k)}:undefined;};\n'''
    diagnostic=html.replace('  window.QB={',probe+'  window.QB={',1).encode()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?',1)[0] in ('/','/index.html'):
                self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()
                try:self.wfile.write(diagnostic)
                except (BrokenPipeError,ConnectionResetError):pass
            else:super().do_GET()
        def log_message(self,*_):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(web)));threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}';out=ROOT/'build/ui-checks';out.mkdir(exist_ok=True);reports=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for width,height in [(390,844),(820,1180)]:
                context=browser.new_context(viewport={'width':width,'height':height},service_workers='block',has_touch=True,is_mobile=True)
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin);page.wait_for_function('QB?.getState');ids=page.evaluate(SEED,'wrong')
                page.get_by_role('button',name='Practice mistakes',exact=True).click();page.wait_for_selector('.option')
                session=page.evaluate('QB.getState().activeSession');assert set(session['questionIds'])==set(ids) and len(session['questionIds'])==27
                q=page.evaluate('__revisionCurrent()');choice=next(i for i,o in enumerate(q['options']) if ord(o['letter'].upper())-64==int(q['correctOption']))
                page.locator('.option').nth(choice).click();page.get_by_role('button',name='Next',exact=True).click()
                paused_before=page.evaluate('JSON.parse(JSON.stringify(QB.getState().activeSession))')
                page.evaluate('QB.openQuestionNavigator()');sheet=page.locator('#nk-session-review');sheet.wait_for()
                assert page.locator('#qb-question-navigator').count()==0
                assert sheet.get_by_role('button',name='Pause',exact=True).count()==1 and sheet.get_by_role('button',name='Finish session',exact=True).count()==1
                assert sheet.get_by_role('button',name='Review unanswered',exact=True).count()==0
                assert 'only the questions you answered' in sheet.inner_text()
                page.screenshot(path=str(out/f'revision-session-{width}.png'))
                page.evaluate('__revisionFail(true)');sheet.get_by_role('button',name='Pause',exact=True).click()
                assert page.evaluate('QB.getState().activeSession.lifecycle')=='active' and page.evaluate('location.hash')=='#practice'
                assert page.evaluate('QB.getState().activeSession.id')==session['id'];assert sheet.is_visible()
                page.evaluate('__revisionFail(false)');page.get_by_role('button',name='Retry save',exact=True).click();sheet.get_by_role('button',name='Pause',exact=True).click()
                page.get_by_role('heading',name='Revision',exact=True).wait_for()
                saved=page.evaluate('QB.getState().normalPracticeCheckpoints.find(cp=>cp.sessionId===QB.getState().activeSession.id)')
                assert saved['lifecycle']=='paused' and saved['sessionQuestionIds']==session['questionIds']
                assert saved['position']['index']==1 and saved['answers']==paused_before['answers'] and saved['submitted']==paused_before['submitted']
                assert not page.evaluate('(ids)=>ids.slice(1).some(id=>QB.getState().fsrsReviewEligible?.[id]?.reason==="skipped")',session['questionIds'])
                page.reload();page.get_by_role('button',name='Resume mistakes',exact=True).wait_for();page.screenshot(path=str(out/f'revision-paused-{width}.png'))
                page.get_by_role('button',name='Resume mistakes',exact=True).click();page.wait_for_selector('.option')
                resumed=page.evaluate('QB.getState().activeSession');assert resumed['id']==session['id'] and resumed['questionIds']==session['questionIds'] and resumed['index']==1
                assert resumed['answers']==saved['answers'] and resumed['submitted']==saved['submitted'] and resumed['questionTimes']==saved['questionTimes']
                rebuilt=page.evaluate('(cp)=>__revisionRestore(cp)',saved);assert rebuilt['revisionQueueKind']=='wrong' and rebuilt['context']=='wrong' and rebuilt['originRoute']=='quick-revision'
                attempts_before=page.evaluate('JSON.stringify(QB.getState().attempts)');page.evaluate('QB.openQuestionNavigator();__revisionFail(true)')
                sheet.get_by_role('button',name='Finish session',exact=True).click();assert page.evaluate('location.hash')=='#practice' and page.evaluate('QB.getState().activeSession.id')==session['id']
                assert page.evaluate('QB.getState().tests.length')==0 and page.evaluate('JSON.stringify(QB.getState().attempts)')==attempts_before
                page.evaluate('__revisionFail(false)');page.get_by_role('button',name='Retry save',exact=True).click();sheet.get_by_role('button',name='Finish session',exact=True).click();page.locator('.nk-refined-analysis').wait_for()
                result=page.evaluate('QB.getState().tests.at(-1)');assert result['questionIds']==[q['id']] and result['total']==1 and result['unattempted']==0 and result['correct']==1
                assert page.evaluate('QB.getState().activeSession') is None
                assert not page.evaluate('(ids)=>ids.slice(1).some(id=>QB.getState().fsrsReviewEligible?.[id]?.reason==="skipped")',session['questionIds'])
                page.locator('.nk-na-back').click();page.get_by_role('heading',name='Revision',exact=True).wait_for();assert page.get_by_role('button',name='Resume mistakes',exact=True).count()==0
                assert page.locator('.nk-revision-card').first.locator('b').inner_text()=='26'
                page.evaluate(SEED,'bookmarks');page.get_by_role('button',name='Practice bookmarks',exact=True).click();page.wait_for_selector('.option')
                assert page.evaluate('QB.getState().activeSession.questionIds.length')==27
                # A final-question Next uses the identical revision sheet; finishing untouched saves no result.
                page.evaluate('QB.goIndex(26)');page.get_by_role('button',name='Next',exact=True).click();sheet.wait_for()
                sheet.get_by_role('button',name='Finish session',exact=True).click();page.get_by_role('heading',name='Revision',exact=True).wait_for()
                assert page.evaluate('QB.getState().tests.length')==0 and page.locator('.nk-revision-card').nth(1).locator('b').inner_text()=='27'
                # Go beyond the old twentieth-question boundary and complete the entire bookmarked set.
                page.get_by_role('button',name='Practice bookmarks',exact=True).click();page.wait_for_selector('.option')
                page.evaluate('''()=>{for(let i=0;i<27;i++){const q=__revisionCurrent();QB.selectPractice(q.id,Number(q.correctOption));QB.nextQ();}}''')
                sheet.wait_for();assert sheet.locator('.nk-session-review-q').count()==27
                assert page.evaluate('Object.values(QB.getState().activeSession.submitted).filter(Boolean).length')==27
                sheet.get_by_role('button',name='Finish session',exact=True).click();page.locator('.nk-refined-analysis').wait_for()
                full=page.evaluate('QB.getState().tests.at(-1)');assert full['total']==27 and full['correct']==27 and full['unattempted']==0
                page.evaluate(SEED,'due');due=page.evaluate('__revisionDue()');assert len(due['cards'])==23 and due['rolledOver']==4
                page.get_by_role('button',name='Review due',exact=True).click();page.wait_for_selector('.option');due_session=page.evaluate('QB.getState().activeSession')
                assert due_session['questionIds']==[str(q['id']) for q in due['cards']] and due_session['context']=='fsrs'
                q=page.evaluate('__revisionCurrent()');choice=next(i for i,o in enumerate(q['options']) if ord(o['letter'].upper())-64==int(q['correctOption']))
                page.locator('.option').nth(choice).click();page.evaluate('QB.openQuestionNavigator()');sheet.get_by_role('button',name='Pause',exact=True).click()
                cp=page.evaluate('QB.getState().normalPracticeCheckpoints.find(cp=>cp.sessionId===QB.getState().activeSession.id)');restored=page.evaluate('(cp)=>__revisionRestore(cp)',cp)
                assert restored['context']=='fsrs' and restored['revisionQueueKind']=='due'
                active=page.evaluate('(id)=>QB.getState().attempts[id].filter(a=>!a.isUndo)',q['id']);assert active[-1]['source']=='fsrs-review'
                # A queue start must preserve an active timed test and cannot relabel it.
                page.evaluate('QB.getState().activeSession={id:"revision-protected-test",mode:"exam",questionIds:[],answers:{}};QB.nkStartRevisionQueue("wrong")')
                assert page.evaluate('QB.getState().activeSession.id')=='revision-protected-test'
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth') and not errors,errors
                reports.append({'width':width,'fullMistakes':27,'fullBookmarks':27,'fullCompletion':27,'dueAdmitted':23,'pauseReload':True,'pauseFailure':True,'finishFailure':True,'answeredOnly':True,'dueSourcePreserved':True,'finalBoundary':True,'examProtected':True})
                context.close()
            browser.close()
        (out/'revision-session-report.json').write_text(json.dumps(reports,indent=2));print('REVISION_SESSION_BROWSER_OK '+json.dumps(reports))
    finally:server.shutdown()
if __name__=='__main__':main()
