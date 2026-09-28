#!/usr/bin/env python3
"""Generated phone/tablet CBT selection stays durable and paints without a full view rebuild."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'build/web'


def main():
    assert 'function nkPatchExamChoice()' in (WEB / 'index.html').read_text(encoding='utf-8')
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(WEB)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    report = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height in ((390, 844), (820, 1180)):
                context = browser.new_context(viewport={'width': width, 'height': height}, is_mobile=True, has_touch=True, service_workers='block')
                context.add_init_script("""window.__vibrations=[];Object.defineProperty(Navigator.prototype,'vibrate',{configurable:true,value:function(pattern){window.__vibrations.push(pattern);return true;}});""")
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(origin + '/#dashboard', wait_until='domcontentloaded')
                page.wait_for_function('window.QB?.nkCbtSetStep')
                page.evaluate("""() => {
                  window.QB.openTestBuilder();window.QB.nkCbtSetStep(2);
                  window.QB.nkCbtSelectVerifiedPyqs();window.QB.nkCbtSetStep(3);
                  window.QB.nkCbtSetCount(10);window.QB.nkCbtStart();
                }""")
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                page.wait_for_selector('.nk-v114-session.is-exam .option-list button.option')
                page.evaluate("window.__questionNode=document.querySelector('.nk-v114-session .question-text')")
                choices = page.locator('.nk-v114-session .option-list button.option')
                choices.nth(0).tap()
                assert page.locator('.nk-v114-session .option-list .selected').count() == 1
                choices.nth(1).tap()
                assert page.locator('.nk-v114-session .option-list .selected').count() == 1
                assert page.evaluate("document.querySelector('.nk-v114-session .question-text')===window.__questionNode"), 'CBT answer rebuilt the question view'
                assert page.evaluate("window.QB.getState().activeSession.answers[window.QB.getState().activeSession.questionIds[0]]") == 2
                assert 7 in page.evaluate('window.__vibrations'), 'choice press lacked immediate feedback'
                timings = page.evaluate("""() => {
                  const ms=[],s=window.QB.getState().activeSession,id=s.questionIds[s.index];
                  for(let i=0;i<12;i++){const start=performance.now();window.QB.selectExam(i%2?2:1,id,s.id);ms.push(performance.now()-start);}
                  return ms;
                }""")
                assert page.evaluate("document.querySelector('.nk-v114-session .question-text')===window.__questionNode"), 'rapid answers rebuilt the question view'
                # A failed save must leave the visible selection and saved answer intact.
                page.evaluate("window.__NK_STORAGE_ADAPTER={getItem:k=>localStorage.getItem(k),removeItem:k=>localStorage.removeItem(k),setItem:()=>{throw Error('quota test')}}")
                choices.nth(2).tap()
                assert page.evaluate("window.QB.getState().activeSession.answers[window.QB.getState().activeSession.questionIds[0]]") == 2
                assert choices.nth(1).get_attribute('class').find('selected') >= 0
                page.evaluate('delete window.__NK_STORAGE_ADAPTER')
                page.reload(wait_until='domcontentloaded')
                page.wait_for_selector('.nk-v114-session.is-exam .option-list button.option')
                assert page.locator('.nk-v114-session .option-list button.option').nth(1).get_attribute('class').find('selected') >= 0
                assert not errors, errors
                report.append({'viewport': width, 'durable_answer': 2, 'in_place_selection': True, 'choice_haptic': True,
                               'rapid_answer_median_ms': round(sorted(timings)[len(timings)//2], 1)})
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print('INTERACTION_FEEDBACK_BROWSER_OK ' + json.dumps(report))


if __name__ == '__main__':
    main()
