#!/usr/bin/env python3
"""Exercise draft continuity, progressive search and module focus on phone/tablet."""
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
    probe = PROBE+'window.__visualQuestion=()=>nkCurrentQuestion();window.__studyPersistence=saveState;window.__studyFailSave=()=>{saveState=()=>false;};window.__studyRestoreSave=()=>{saveState=window.__studyPersistence;};\n'
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
    output = ROOT/'build/study-flow-checks';output.mkdir(exist_ok=True)
    reports=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for width,height in [(390,844),(820,1180)]:
                context=browser.new_context(viewport={'width':width,'height':height},service_workers='block',has_touch=True,is_mobile=True)
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin);page.wait_for_function('QB?.getState');page.evaluate('QB.startAllPractice()')
                page.wait_for_selector('.option-list button');q=page.evaluate('__visualQuestion()')
                page.locator('.option-list button').nth(int(q['correctOption'])-1).click()
                page.locator('.nk-note-add').click()
                bounds=page.locator('.nk-note-save').bounding_box()
                footer=page.locator('.nk-session-footer').bounding_box()
                assert bounds['y']>=0 and bounds['y']+bounds['height']<=footer['y'],('editor hidden',width,bounds,footer)
                draft='Recall cue with α and العربية <script>safe</script>'
                page.locator('textarea').fill(draft)
                page.screenshot(path=str(output/f'note-{width}.png'))
                page.get_by_role('button',name='Next',exact=True).click()
                page.get_by_role('button',name='Previous',exact=True).click()
                assert page.locator('textarea').input_value()==draft
                assert not page.locator('textarea').evaluate('n=>n===document.activeElement'),'restored draft stole focus'
                assert not page.evaluate('Object.values(QB.getState().questionNotes||{}).some(n=>n.text?.includes("Recall cue"))'),'draft persisted without Save'
                page.locator('.nk-note-cancel').click()
                page.locator('.nk-note-add').click();assert page.locator('textarea').input_value()==''
                page.locator('textarea').fill(draft);page.locator('.nk-note-save').click()
                assert page.locator('.nk-note-readonly').inner_text()==draft
                page.locator('.nk-note-edit').click();page.locator('textarea').fill('Failed save: keep my recall cue')
                page.evaluate('__studyFailSave()');page.locator('.nk-note-save').click()
                assert 'Save failed' in page.locator('.nk-question-note [role="status"]').inner_text()
                assert page.locator('textarea').input_value()=='Failed save: keep my recall cue'
                assert page.evaluate('Object.values(QB.getState().questionNotes).some(n=>n.text.includes("<script>safe</script>"))')
                page.evaluate('__studyRestoreSave()');page.locator('.nk-note-cancel').click()
                page.evaluate("QB.nav('notes')")
                notesSearch=page.locator('.nk-notes-search input');notesSearch.fill('Recall cue')
                assert notesSearch.evaluate('n=>getComputedStyle(n).fontSize')=='16px'
                assert page.locator('.nk-notes-search svg').count()==1
                page.locator('.nk-notes-item:visible button').first.click();page.wait_for_selector('.option')
                assert page.evaluate('QB.getState().activeSession.originRoute')=='notes'
                page.locator('.option').first.click();page.evaluate('QB.endSession()')
                page.locator('.nk-na-back').wait_for();assert page.locator('.nk-na-back').get_attribute('aria-label')=='Back to notes'
                page.locator('.nk-na-back').click();page.wait_for_selector('.nk-notes-search input')
                assert page.locator('.nk-notes-search input').input_value()=='Recall cue'
                assert page.locator('.nk-notes-item:visible').count()==1
                page.screenshot(path=str(output/f'notes-return-{width}.png'))
                page.evaluate("QB.nav('question-search')")
                page.locator('.nk-question-search-filters select').first.select_option('Anatomy')
                page.evaluate('window.__oldRow=document.querySelector(".nk-question-search-item")')
                count=page.locator('.nk-question-search-item').count()
                more=page.locator('.nk-question-search-more');more.focus();page.keyboard.press('Enter')
                assert page.evaluate('__oldRow.isConnected')
                assert page.locator('.nk-question-search-item').count()==count+30
                assert page.evaluate('document.activeElement.closest(".nk-question-search-item")!==null'),'pagination lost keyboard focus'
                for _ in range(4):
                    page.locator('.nk-question-search-more').click()
                    assert page.evaluate('__oldRow.isConnected')
                ids=page.locator('.nk-question-search-id').all_text_contents()
                assert len(ids)==len(set(ids))==180,'duplicate or dropped results after repeated append'
                page.screenshot(path=str(output/f'search-{width}.png'))
                page.evaluate('QB.openStudyModuleBuilder()')
                page.get_by_role('button',name='Continue',exact=True).click()
                assert page.evaluate('document.activeElement.matches(".nk-module-builder h1")')
                page.get_by_role('button',name='Select all',exact=True).click()
                page.get_by_role('button',name='Continue to questions',exact=True).click()
                custom=page.get_by_role('button',name='Custom',exact=True);custom.focus();page.keyboard.press('Enter')
                assert page.evaluate('document.activeElement.textContent==="Custom"')
                assert page.locator('.nk-module-count-block input').evaluate('n=>getComputedStyle(n).fontSize')=='16px'
                countInput=page.locator('#nk-module-custom-count')
                for invalid in ['', '0', '501', '1.5']:
                    countInput.fill(invalid)
                    assert page.get_by_role('button',name='Continue',exact=True).is_disabled(),('invalid count advanced',invalid)
                    assert countInput.get_attribute('aria-invalid')=='true'
                    assert 'whole number from 1 to 500' in page.locator('#nk-module-availability').inner_text()
                countInput.fill('24')
                assert page.get_by_role('button',name='Continue',exact=True).is_enabled()
                assert countInput.get_attribute('aria-invalid')=='false'
                page.get_by_role('button',name='Continue',exact=True).click()
                assert page.locator('.nk-module-name input').evaluate('n=>getComputedStyle(n).fontSize')=='16px'
                assert page.evaluate('document.activeElement.matches(".nk-module-builder h1")')
                gap=page.locator('.nk-module-builder-card').evaluate('n=>n.getBoundingClientRect().bottom-n.lastElementChild.getBoundingClientRect().bottom')
                assert gap<=24,('review leaves oversized blank space',width,gap)
                page.screenshot(path=str(output/f'module-review-{width}.png'))
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert not errors,errors
                reports.append({'width':width,'draft_save_cancel':True,'editor_clear':True,'append_and_focus':True,'module_focus':True,'notes_roundtrip':True,'save_failure':True,'invalid_counts':True,'repeat_pagination':True})
                context.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    (output/'report.json').write_text(json.dumps(reports,indent=2))
    print('STUDY_FLOW_BROWSER_OK',json.dumps(reports))
if __name__=='__main__':main()
