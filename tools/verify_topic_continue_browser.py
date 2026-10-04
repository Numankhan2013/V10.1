#!/usr/bin/env python3
"""Exercise scoped Topics continuation and Today’s Focus against durable state."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]


def main():
    web = ROOT / 'build/web'
    html = (web / 'index.html').read_text()
    probe = 'window.__topicContinue={current:()=>nkCurrentQuestion(),context:()=>nkLatestPracticeContext(),record:(s,b)=>nkBankRecord(s,b)};\n'
    diagnostic = html.replace('  window.QB={', probe + '  window.QB={', 1).encode()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?',1)[0] in ['/', '/index.html']:
                self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(diagnostic)
            else:
                super().do_GET()
        def log_message(self,*_):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(web)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    out=ROOT/'build/topic-continue-checks';out.mkdir(exist_ok=True);reports=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for width,height in [(390,844),(820,1180),(1440,1000)]:
                context=browser.new_context(viewport={'width':width,'height':height},service_workers='block')
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin);page.wait_for_function('QB?.getState')
                page.evaluate('QB.openBank("Anatomy","Marrow")')
                chapter=page.evaluate('__topicContinue.record("Anatomy","Marrow").topics[0].id')
                page.evaluate('id=>QB.openChapter(id)',chapter)
                page.locator('.nk-chapter-actions').get_by_role('button',name='Practice',exact=False).click()
                page.locator('#modal').get_by_role('button',name='Start Practice',exact=True).click()
                page.locator('.option-list button').first.wait_for()
                original=page.evaluate('QB.getState().activeSession')
                assert len(original['questionIds'])>1
                page.locator('.option-list button').first.click()
                page.get_by_role('button',name='Next',exact=True).click()
                before=page.evaluate('QB.getState().activeSession')
                page.evaluate('QB.openSessionReview()')
                page.locator('#nk-session-review').get_by_role('button',name='Pause',exact=True).click()
                page.wait_for_function('QB.getState().activeSession?.lifecycle==="paused"')
                expect(page.locator('.nk-home-focus-card')).to_contain_text(f"Question 2 of {len(original['questionIds'])}")
                page.screenshot(path=str(out/f'todays-focus-{width}.png'))
                # Persisted state, not the old heap, must power the Topics tray.
                page.reload();page.wait_for_function('QB?.getState')
                page.evaluate('QB.openBank("Anatomy","Marrow")')
                tray=page.locator('.nk-continue-learning')
                expect(tray).to_contain_text('RESUME PRACTICE')
                expect(tray).to_contain_text(f"Question 2 of {len(original['questionIds'])}")
                page.screenshot(path=str(out/f'topics-resume-{width}.png'))
                tray.get_by_role('button',name='Continue learning',exact=True).click()
                resumed=page.evaluate('QB.getState().activeSession')
                assert resumed['id']==original['id'] and resumed['questionIds']==original['questionIds']
                assert resumed['index']==1 and resumed['answers']==before['answers'] and resumed['submitted']==before['submitted']
                assert not resumed['submitted'].get(resumed['questionIds'][1])
                page.evaluate('QB.nkPausePractice()')
                # A special mode can occupy activeSession without hiding the saved
                # normal Practice or changing what the scoped tray resumes.
                page.evaluate('''()=>{const s=QB.getState();s.activeSession={id:'other-review',mode:'review',questionIds:['1-1'],index:0,answers:{},submitted:{}};QB.saveState();QB.openBank('Anatomy','Marrow');}''')
                expect(page.locator('.nk-continue-learning')).to_contain_text('RESUME PRACTICE')
                page.locator('.nk-continue-learning button').click()
                assert page.evaluate('QB.getState().activeSession.id')==original['id']
                page.evaluate('QB.nkPausePractice()')
                # Bank boundaries: PrepLadder must offer its own topic, never the
                # paused Marrow session, even though the subject is identical.
                page.evaluate('QB.openBank("Anatomy","PrepLadder")')
                assert 'RESUME PRACTICE' not in page.locator('.nk-continue-learning').inner_text()
                page.locator('.nk-continue-learning button').click()
                page.locator('.nk-chapter-v114').wait_for()
                assert page.locator('.nk-chapter-v114').count()==1
                assert page.evaluate('QB.getState().activeSession.id')==original['id']
                # Finish any saved work, then completed banks have no misleading
                # "0 questions left" continuation control.
                page.evaluate('''()=>{const s=QB.getState();s.activeSession=null;s.normalPracticeCheckpoints=[];s.normalPracticeCheckpoint=null;const r=__topicContinue.record('Anatomy','Marrow');for(const q of r.questions)s.attempts[q.id]=[{id:'complete-'+q.id,selected:q.correctOption,correct:true,at:Date.now(),source:'practice'}];QB.saveState();QB.openBank('Anatomy','Marrow');}''')
                expect(page.locator('.nk-continue-learning')).to_have_count(0)
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert not errors,errors
                reports.append({'width':width,'durable_scoped_resume':True,'same_ids_position_answers':True,'special_mode_restore':True,'bank_boundary':True,'completed_bank':True,'focus_progress':True})
                context.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    (out/'report.json').write_text(json.dumps(reports,indent=2))
    print('TOPIC_CONTINUE_BROWSER_OK',json.dumps(reports))


if __name__=='__main__':main()
