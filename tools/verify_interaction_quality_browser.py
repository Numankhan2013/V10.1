#!/usr/bin/env python3
"""Verify reading continuity, immediate outcomes and retained filter focus."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright, expect
from verify_learning_insights_browser import PROBE, SEED

ROOT = Path(__file__).resolve().parents[1]


def main():
    web = ROOT / 'build/web'
    html = (web / 'index.html').read_text()
    probe = PROBE + 'window.__nkQuality={question:()=>nkCurrentQuestion()};\n'
    diagnostic = html.replace('  window.QB={', probe + '  window.QB={', 1).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?', 1)[0] in ('/', '/index.html'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(diagnostic)
            else:
                super().do_GET()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    output = ROOT / 'build/ui-checks'
    output.mkdir(exist_ok=True)
    reports = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height, reduced in [(320,844,False),(390,844,False),(820,1180,False),(1194,834,False),(390,844,True)]:
                context = browser.new_context(viewport={'width':width,'height':height}, has_touch=True, is_mobile=True,
                                              service_workers='block', reduced_motion='reduce' if reduced else 'no-preference')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.route('**/*', lambda r: r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin+'/#dashboard', wait_until='domcontentloaded')
                page.wait_for_function('window.QB?.getState')
                page.evaluate(SEED)
                saved = page.evaluate('JSON.stringify(QB.getState())')
                page.locator('.nk-li-methods').evaluate('n=>n.open=true')
                for label, value in [('Time period','month'),('Insights subject','Anatomy'),('Insights bank','Marrow')]:
                    control = page.get_by_label(label, exact=True)
                    control.focus()
                    page.evaluate('window.__control=document.activeElement;window.__shell=document.querySelector(".bottom-nav")')
                    control.select_option(value)
                    assert page.evaluate('__control.isConnected && __control===document.activeElement'), label
                    assert page.evaluate('__shell===document.querySelector(".bottom-nav")')
                    assert control.input_value() == value
                    assert page.locator('.nk-li-methods').evaluate('n=>n.open')
                previous = page.get_by_role('button', name='Previous month', exact=True)
                previous.focus(); previous.click()
                assert page.evaluate('document.activeElement.getAttribute("aria-label")') == 'Previous month'
                page.get_by_role('button',name='Today',exact=True).click()
                assert not page.evaluate('document.activeElement.disabled')
                mode = page.get_by_role('button',name='Top performing',exact=True)
                mode.scroll_into_view_if_needed();mode.focus()
                y = page.evaluate('scrollY');mode.click()
                assert page.evaluate('document.activeElement.textContent.trim()') == 'Top performing'
                assert abs(page.evaluate('scrollY')-y) <= 1
                assert page.get_by_role('button',name='Top performing',exact=True).get_attribute('aria-pressed') == 'true'
                year = page.get_by_label('Activity year',exact=True)
                year.focus();year.select_option(str(page.evaluate('new Date().getFullYear()')))
                assert page.evaluate('document.activeElement.getAttribute("aria-label")') == 'Activity year'
                days = page.locator('.nk-li-year-grid button:not(:disabled)')
                assert page.locator('.nk-li-year-grid button[tabindex="0"]').count() == 1
                days.last.focus();page.keyboard.press('ArrowUp')
                assert days.nth(days.count()-2).evaluate('n=>n===document.activeElement')
                page.keyboard.press('Enter')
                assert 'answers' in page.locator('#nk-li-year-detail').inner_text()
                assert page.locator('.nk-li-year-grid .is-selected').get_attribute('aria-pressed') == 'true'
                assert page.locator('.nk-li-year-grid button[tabindex="0"]').count() == 1
                page.keyboard.press('Tab')
                assert not page.evaluate('document.activeElement.matches(".nk-li-year-grid button")')
                assert page.evaluate('JSON.stringify(QB.getState())') == saved, 'Insights interactions mutated study state'
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                page.screenshot(path=str(output/f'quality-insights-{width}-{reduced}.png'),full_page=True)
                # Use real existing Practice and source-rendering paths, with both
                # outcomes. The pending Good rating and immutable answer stay intact.
                page.evaluate("QB.nav('dashboard');QB.startAllPractice()")
                for correct in [True,False]:
                    page.wait_for_selector('.option-list button')
                    q = page.evaluate('__nkQuality.question()')
                    n = int(q['correctOption']) if correct else int(q['correctOption']) % len(q['options']) + 1
                    page.evaluate('window.__stem=document.querySelector(".question-text");window.__options=document.querySelector(".option-list");window.__header=document.querySelector(".nk-session-header")')
                    option = page.locator('.option-list button').nth(n-1)
                    option.focus()
                    appearance = page.evaluate('''async(n)=>{
                      const s=QB.getState().activeSession,id=s.questionIds[s.index],t=performance.now();
                      QB.selectPractice(id,n,s.id);
                      const immediate=document.querySelector('.option.correct');
                      const color=getComputedStyle(immediate).backgroundColor;
                      const synchronous=Boolean(QB.getState().activeSession.submitted[id]&&document.querySelector('.nk-answer-outcome'));
                      const ms=performance.now()-t;await new Promise(requestAnimationFrame);
                      return {synchronous,ms,firstFrame:color===getComputedStyle(immediate).backgroundColor,
                        retained:__stem===document.querySelector('.question-text')&&__options===document.querySelector('.option-list')};
                    }''', n)
                    assert appearance['synchronous'] and appearance['firstFrame'] and appearance['retained'], appearance
                    assert page.locator('.option-list button').count() == 0, 'submitted answers must stay locked'
                    assert page.locator('.option.correct').count() == 1
                    assert page.locator('.option.wrong').count() == (0 if correct else 1)
                    expect(page.locator('.nk-answer-outcome')).to_contain_text('Correct' if correct else 'Incorrect')
                    assert page.evaluate('document.activeElement.matches(".nk-fsrs-pill,.nk-session-footer .primary-btn")')
                    assert page.locator('.nk-question-note').count() == 1
                    page.screenshot(path=str(output/f'quality-answer-{width}-{correct}-{reduced}.png'),full_page=True)
                    index = page.evaluate('QB.getState().activeSession.index')
                    page.get_by_role('button',name='Next',exact=True).click()
                    assert page.evaluate('QB.getState().activeSession.index') == index+1
                    assert page.evaluate('scrollY') == 0
                    assert page.evaluate('document.activeElement.textContent.trim()') == 'Next'
                assert not errors, errors
                reports.append({'width':width,'reduced_motion':reduced,'retained_question':True,'retained_picker':True,'immediate_outcome':True,'read_only_insights':True})
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print('INTERACTION_QUALITY_BROWSER_OK '+json.dumps(reports))


if __name__ == '__main__':
    main()
