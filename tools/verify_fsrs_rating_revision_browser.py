#!/usr/bin/env python3
"""Verify correction queues and rating amendments against the generated runtime."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''window.__nkFsrsTest={
 questions:()=>nkFsrsAllQuestions().filter(q=>nkQuestionPresentationFor(q).valid).map(q=>({id:q.id,subject:q.subject,bank:q.bank,correctOption:q.correctOption,optionCount:q.options.length})),
 start:ids=>{BY_ID={...BY_ID,...nkFsrsAllById()};return startSession(ids,'exam','Biochemistry rating regression','normal');},
 active:id=>nkFsrsActiveAttempts(id),merge:cp=>nkMergePracticeCheckpoint(cp),
 metrics:()=>({attempts:totalAttempts(),incorrect:totalIncorrectAttempts(),days:[...studyDayKeys()]}),
 apply:e=>nkApplyCloudEnvelope(e),replay:id=>nkFsrsReplay(id),render:()=>render()
};'''


def main():
    web = ROOT/'build/web'
    html = (web/'index.html').read_text()
    assert html.count('/* NK_FSRS_V6_END */') == 1
    # Expose read/merge commands only in the test response, never in app assets.
    diagnostic = html.replace('/* NK_FSRS_V6_END */', PROBE+'\n/* NK_FSRS_V6_END */').encode()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            try:
                if self.path.split('?',1)[0] in ('/','/index.html'):
                    self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(diagnostic)
                else: super().do_GET()
            except (BrokenPipeError,ConnectionResetError): pass
        def log_message(self,*args): pass
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(web)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    output=ROOT/'build/ui-checks';output.mkdir(parents=True,exist_ok=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            for width,height in [(390,844),(820,1180)]:
                def open_page():
                    context=browser.new_context(viewport={'width':width,'height':height},service_workers='block')
                    page=context.new_page()
                    page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                    page.goto(origin+'/#dashboard',wait_until='domcontentloaded')
                    page.wait_for_function('window.QB && window.__nkFsrsTest')
                    return context,page
                context,page=open_page()
                questions=page.evaluate("window.__nkFsrsTest.questions().filter(q=>q.subject==='Biochemistry'&&q.bank==='PrepLadder').slice(0,24)")
                assert len(questions)==24
                by_id={q['id']:q for q in questions};ids=list(by_id)
                page.evaluate('ids=>window.__nkFsrsTest.start(ids)',ids)
                for i,q in enumerate(questions):
                    selected=q['correctOption'] if i<21 else q['correctOption']%q['optionCount']+1
                    page.evaluate('([i,n])=>{window.QB.goIndex(i);window.QB.selectExam(n);}',[i,selected])
                page.evaluate('window.QB.submitExam(false)')
                page.wait_for_function("location.hash.startsWith('#result')")
                test=page.evaluate('window.QB.getState().tests.at(-1)')
                assert (test['correct'],test['incorrect'])==(21,3)
                page.get_by_role('button',name='Practise missed questions',exact=False).click()
                queue=page.evaluate('window.QB.getState().activeSession.questionIds')
                assert set(queue)==set(ids[-3:])
                for index,qid in enumerate(queue):
                    page.evaluate('i=>window.QB.goIndex(i)',index)
                    page.evaluate('([id,n])=>window.QB.selectPractice(id,n)',[qid,by_id[qid]['correctOption']])
                    stale=page.evaluate('JSON.parse(JSON.stringify(window.QB.getState().normalPracticeCheckpoint))')
                    dock=page.locator('.nk-fsrs-rating');dock.wait_for()
                    for grade,label in [(2,'Hard'),(3,'Good'),(4,'Easy'),(3,'Good')]:
                        dock.get_by_role('button',name=label,exact=True).click()
                        assert dock.get_by_role('button',name=label,exact=True).get_attribute('aria-pressed')=='true'
                        assert page.evaluate('id=>window.__nkFsrsTest.active(id).at(-1).rating',qid)==grade
                        assert page.evaluate('id=>window.QB.getState().reviews[id].repetitions',qid)==2
                        assert page.evaluate('id=>window.QB.getState().attempts[id].length',qid)==2
                    due=page.evaluate('id=>window.QB.getState().reviews[id].due',qid)
                    page.evaluate('([cp,id])=>{window.__nkFsrsTest.merge(cp);window.QB.saveState();window.__nkFsrsTest.replay(id);window.__nkFsrsTest.render();}',[stale,qid])
                    assert page.evaluate('id=>window.QB.getState().activeSession.pendingRating?.[id]||null',qid) is None
                    assert dock.get_by_role('button',name='Good',exact=True).get_attribute('aria-pressed')=='true'
                    assert page.evaluate('id=>window.QB.getState().reviews[id].due',qid)==due
                page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
                page.locator('.nk-session-footer').screenshot(path=str(output/f'fsrs-editable-rating-{width}.png'))
                saved=page.evaluate('JSON.parse(JSON.stringify(window.QB.getState()))')
                metrics=page.evaluate('window.__nkFsrsTest.metrics()')
                peer_context,peer=open_page()
                peer.evaluate('s=>{Object.assign(window.QB.getState(),s);window.QB.saveState();window.QB.nav("practice");}',saved)
                peer.locator('.nk-fsrs-rating').wait_for()
                peer.locator('.nk-fsrs-rating').get_by_role('button',name='Easy',exact=True).click()
                event=peer.evaluate('id=>window.QB.getState().fsrsRatingRevisions[id].at(-1)',qid)
                page.evaluate('([id,a])=>{const e={kind:"attempts",entityId:a.id,ownerDevice:"peer",updatedAt:a.at,deleted:false,payload:JSON.stringify({qid:id,attempt:a}),schemaVersion:1};window.__nkFsrsTest.apply(e);window.__nkFsrsTest.apply(e);window.__nkFsrsTest.replay(id);window.QB.saveState();window.__nkFsrsTest.render();}',[qid,event])
                assert page.locator('.nk-fsrs-rating').get_by_role('button',name='Easy',exact=True).get_attribute('aria-pressed')=='true'
                assert page.evaluate('id=>window.QB.getState().reviews[id].repetitions',qid)==2
                assert page.evaluate('id=>window.QB.getState().attempts[id].length',qid)==2
                assert page.evaluate('window.__nkFsrsTest.metrics()')==metrics
                peer_context.close()
                page.evaluate('window.QB.nkFsrsUndo()')
                assert page.locator('.nk-fsrs-rating').get_by_role('button',name='Good',exact=True).get_attribute('aria-pressed')=='true'
                assert page.evaluate('id=>window.QB.getState().reviews[id].repetitions',qid)==2
                assert page.evaluate('window.__nkFsrsTest.metrics()')==metrics
                page.reload(wait_until='domcontentloaded');page.locator('.nk-fsrs-rating').wait_for()
                assert page.locator('.nk-fsrs-rating').get_by_role('button',name='Good',exact=True).get_attribute('aria-pressed')=='true'
                page.evaluate('window.QB.endSession()')
                page.wait_for_function("location.hash.startsWith('#result')")
                page.evaluate('id=>window.QB.openTest(id)',test['id'])
                page.get_by_role('heading',name='Topic breakdown',exact=True).wait_for()
                assert page.get_by_role('button',name='Practise missed questions',exact=False).count()==0
                assert page.locator('.nk-cbt-followup').inner_text().startswith('All original misses corrected')
                after=page.evaluate('id=>window.QB.getState().tests.find(t=>t.id===id)',test['id'])
                assert after['correct']==21 and after['incorrect']==3
                page.evaluate('window.QB.nkOpenRevisionHub()')
                page.get_by_role('heading',name='Revision',exact=True).wait_for()
                assert page.locator('.nk-revision-card.is-red b').inner_text()=='0'
                # A fresh wrong retry restores the unresolved mistake and Again.
                q=by_id[qid]
                page.evaluate('id=>window.QB.practiceOne(id)',qid)
                page.evaluate('([id,n])=>window.QB.selectPractice(id,n)',[qid,q['correctOption']%q['optionCount']+1])
                assert page.evaluate('id=>window.__nkFsrsTest.active(id).at(-1).rating',qid)==1
                page.evaluate('window.QB.endSession();window.QB.nkOpenRevisionHub()')
                page.get_by_role('heading',name='Revision',exact=True).wait_for()
                assert page.locator('.nk-revision-card.is-red b').inner_text()=='1'
                context.close()
            browser.close()
    finally:server.shutdown()
    print('FSRS_RATING_REVISION_BROWSER_OK correction24=true editable=true one_review=true sync=true stale_pending=false reload=true historical_score=true remiss=true')


if __name__=='__main__':main()
