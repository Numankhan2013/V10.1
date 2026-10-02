#!/usr/bin/env python3
"""Actual touch flows, stable DOM/scroll, haptic policy and reduced-motion QA."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def main():
    web=ROOT/'build/web';html=(web/'index.html').read_text()
    assert 'NK_INTERACTION_POLISH_V1_START' in html
    probe="window.__nkInteractionProbe={question:()=>nkCurrentQuestion(),render:()=>render()};"
    diagnostic=html.replace('  window.QB={',probe+'\n  window.QB={',1).encode()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?',1)[0] in ('/','/index.html'):
                self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(diagnostic)
            else:super().do_GET()
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(web)));threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
    out=ROOT/'build/ui-checks';out.mkdir(exist_ok=True);reports=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for w,h,reduced in [(320,844,False),(390,844,False),(820,1180,False),(1194,834,False),(390,844,True)]:
                context=browser.new_context(viewport={'width':w,'height':h},is_mobile=True,has_touch=True,service_workers='block',reduced_motion='reduce' if reduced else 'no-preference')
                context.add_init_script("window.__vibrations=[];Object.defineProperty(Navigator.prototype,'vibrate',{configurable:true,value:function(pattern){window.__vibrations.push(pattern);return true;}})")
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort());page.goto(origin+'/#dashboard',wait_until='domcontentloaded');page.wait_for_function('!!window.QB?.getState')
                # Shared controls respond during touch-down and release without
                # interpolating away their committed state, on every screen.
                nav=page.locator('.bottom-nav button,.nav-item').first
                nav.dispatch_event('pointerdown',{'isPrimary':True,'button':0,'clientX':20,'clientY':20})
                assert nav.evaluate("el=>getComputedStyle(el).filter")=='brightness(0.96)'
                assert nav.evaluate("el=>getComputedStyle(el).transform")=='none'
                nav.dispatch_event('pointercancel',{'pointerId':1})
                assert nav.evaluate("el=>getComputedStyle(el).filter")=='none'
                assert nav.evaluate("el=>el.getAnimations().length")==0
                page.evaluate("QB.practiceOne('1-1')");page.wait_for_selector('.option-list button');question=page.evaluate('__nkInteractionProbe.question()');option=page.locator('.option-list button').nth(int(question['correctOption'])-1)
                option.dispatch_event('pointerdown',{'pointerId':1,'isPrimary':True,'pointerType':'touch','button':0,'clientX':30,'clientY':30})
                assert option.evaluate("el=>el.classList.contains('nk-pressed')"),'press has no immediate feedback'
                assert option.evaluate("el=>getComputedStyle(el).transitionDuration")=="0s",'answer press/release must be immediate'
                assert option.evaluate("el=>getComputedStyle(el).transform")=="none",'answer tap must not shrink and rebound'
                if reduced:assert option.evaluate("el=>getComputedStyle(el).transform")=='none','reduced-motion press moved the answer'
                option.dispatch_event('pointercancel',{'pointerId':1,'pointerType':'touch'});assert not option.evaluate("el=>el.classList.contains('nk-pressed')"),'cancelled gesture remained pressed'
                option.tap();page.wait_for_selector('.nk-fsrs-rating');assert page.evaluate('__vibrations')==[7],'correct answer should emit one gentle 7 ms pulse'
                assert page.locator('.option-list .correct').count()==1
                page.evaluate("window.__stem=document.querySelector('.question-text');window.__dock=document.querySelector('.nk-fsrs-rating');window.scrollTo(0,document.body.scrollHeight)")
                before=page.evaluate('scrollY');page.evaluate('QB.toggleBookmark(QB.getState().activeSession.questionIds[0])');assert page.evaluate('scrollY')==before
                assert page.evaluate("__stem===document.querySelector('.question-text')"),'bookmark rebuilt question'
                assert page.locator('.bookmark-toggle').get_attribute('aria-pressed')=='true'
                # Real visible rating changes retain the group, question and one attempt.
                page.get_by_role('button',name='Hard',exact=True).tap();page.get_by_role('button',name='Easy',exact=True).tap()
                assert page.evaluate("__dock===document.querySelector('.nk-fsrs-rating')&&__stem===document.querySelector('.question-text')")
                assert page.get_by_role('button',name='Easy',exact=True).get_attribute('aria-pressed')=='true'
                state=page.evaluate('QB.getState()');qid=state['activeSession']['questionIds'][0];assert len(state['attempts'][qid])==1
                # Failure never publishes a new rating or outcome pulse.
                page.evaluate("window.__NK_STORAGE_ADAPTER={getItem:k=>localStorage.getItem(k),removeItem:k=>localStorage.removeItem(k),setItem:()=>{throw Error('quota QA')}}");previous=page.evaluate('JSON.stringify(QB.getState())');vibrations=page.evaluate('__vibrations.length');page.get_by_role('button',name='Good',exact=True).tap()
                assert page.evaluate('JSON.stringify(QB.getState())')==previous;assert page.get_by_role('button',name='Easy',exact=True).get_attribute('aria-pressed')=='true';assert page.evaluate('__vibrations.length')==vibrations;page.evaluate('delete window.__NK_STORAGE_ADAPTER;QB.nkRetryPersistence()')
                page.locator('.nk-grid-trigger').tap();page.wait_for_selector('#nk-session-review');assert page.evaluate("document.body.style.overflow==='hidden'")
                page.keyboard.press('Shift+Tab');assert page.evaluate("document.querySelector('#nk-session-review').contains(document.activeElement)")
                page.get_by_role('button',name='Pause',exact=True).tap();page.wait_for_url('**/#dashboard');page.wait_for_function("document.body.style.overflow!=='hidden'")
                page.evaluate('QB.openTestBuilder();QB.nkCbtSetStep(2);QB.nkCbtSelectVerifiedPyqs();QB.nkCbtSetStep(3);QB.nkCbtSetCount(10);QB.nkCbtStart()');page.wait_for_selector('.is-exam .option-list button')
                page.evaluate("window.__stem=document.querySelector('.question-text')")
                choices=page.locator('.is-exam .option-list button');choices.nth(0).tap();choices.nth(1).tap();assert page.evaluate("__stem===document.querySelector('.question-text')");assert choices.nth(1).get_attribute('aria-pressed')=='true'
                appearance=page.evaluate("""async() => {
                    const b=document.querySelectorAll('.is-exam .option-list button')[1];
                    const color=getComputedStyle(b).backgroundColor;
                    QB.selectExam(1);
                    const immediate=getComputedStyle(b).backgroundColor;
                    await new Promise(requestAnimationFrame);
                    return {changed:color!==immediate,firstFrame:getComputedStyle(b).backgroundColor===immediate,
                        animations:b.getAnimations().length,duration:getComputedStyle(b).transitionDuration};
                }""")
                assert appearance=={'changed':True,'firstFrame':True,'animations':0,'duration':'0s'},appearance
                timing=page.evaluate("""() => {const ms=[];for(let i=0;i<12;i++){const t=performance.now();QB.selectExam(i%2+1);ms.push(performance.now()-t);}return ms.sort((a,b)=>a-b)[6];}""")
                assert page.evaluate("__stem===document.querySelector('.question-text')")
                page.locator('.nk-exam-review-toggle').tap();assert page.locator('.nk-exam-review-toggle').get_attribute('aria-pressed')=='true';assert page.evaluate("__stem===document.querySelector('.question-text')");pulses=page.evaluate('__vibrations.length')
                page.evaluate('QB.nextQ()');assert page.evaluate('__vibrations.length')==pulses;assert page.evaluate('QB.getState().activeSession.index')==1;assert page.evaluate('scrollY')==0
                if reduced:assert page.evaluate("document.querySelector('.question-card').getAnimations().length") == 0
                page.screenshot(path=str(out/f'interaction-polished-{w}-{reduced}.png'),animations='disabled')
                page.reload(wait_until='domcontentloaded');page.wait_for_selector('.is-exam .option-list button');assert page.evaluate('QB.getState().activeSession.answers[QB.getState().activeSession.questionIds[0]]')==2
                assert not errors,errors;reports.append({'width':w,'reduced_motion':reduced,'in_place':True,'rollback':True,'rating_edit':True,'rapid_choice_median_ms':round(timing,2)});context.close()
            browser.close()
    finally:server.shutdown()
    print('INTERACTION_POLISH_BROWSER_OK '+json.dumps(reports))
if __name__=='__main__':main()
