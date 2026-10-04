#!/usr/bin/env python3
"""Verify audited narrow-screen controls, auth continuity and inert learner text."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = '<img src=x onerror="window.__auditXss=1"> learner note'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url')
    args = parser.parse_args()
    output = ROOT / 'build/preproduction-audit'
    output.mkdir(parents=True, exist_ok=True)

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT / 'build/web')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = args.url.rstrip('/') if args.url else f'http://127.0.0.1:{server.server_port}'
    reports = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height in [(320, 640), (390, 844), (820, 1180), (1440, 1000)]:
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block', has_touch=width <= 820)
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + '/#more', wait_until='domcontentloaded')
                page.wait_for_function('window.QB && QB.getState')
                # No live account is created or signed into. Exercise the form
                # using a synthetic public configuration and block all APIs.
                page.evaluate("window.NK_QBANK_FIREBASE_CONFIG={apiKey:'audit-only',projectId:'audit-only'}; QB.nav('more')")
                page.get_by_role('button', name='Create account', exact=True).click()
                page.locator('#nk-cloud-create-email').fill('audit@example.invalid')
                assert page.get_by_role('button', name='Next', exact=True).evaluate("n=>getComputedStyle(n).color") == 'rgb(255, 255, 255)', 'Account action contrast regressed'
                page.get_by_role('button', name='Next', exact=True).click()
                page.locator('#nk-cloud-create-password').fill('unsaved-test-password')
                page.get_by_role('button', name='Back', exact=True).click()
                expect(page.locator('#nk-cloud-create-email')).to_have_value('audit@example.invalid')
                expect(page.locator('#nk-cloud-create-email')).to_be_focused()
                page.screenshot(path=str(output / f'auth-back-{width}.png'))
                page.get_by_role('button', name='Next', exact=True).click()
                expect(page.locator('#nk-cloud-create-password')).to_have_value('')
                page.get_by_role('button', name='Back', exact=True).click()
                page.get_by_role('button', name='Back to sign in', exact=True).click()
                expect(page.locator('#nk-cloud-email')).to_be_visible()
                assert page.evaluate("!localStorage.getItem('qbank_firebase_auth_v1')"), 'Unauthenticated navigation stored credentials'

                page.evaluate("QB.openBank('Biochemistry','Marrow'); scrollTo(0,0)")
                controls = page.locator('.nk-journey-heading button')
                bounds = controls.evaluate_all('nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {x:r.x,right:r.right,width:r.width,height:r.height}})')
                assert len(bounds) == 3 and all(r['x'] >= 0 and r['right'] <= width and r['width'] >= 44 and r['height'] >= 44 for r in bounds), bounds
                tabs = page.locator('.nk-topics-v114 .nk-filter-tabs button')
                assert tabs.evaluate_all('nodes=>nodes.every(n=>n.scrollWidth<=n.clientWidth+1)'), 'Filter labels overlap their controls'
                tabs.last.focus()
                page.keyboard.press('Space')
                expect(tabs.last).to_have_attribute('aria-pressed', 'true')
                expect(tabs.last).to_be_focused()
                assert tabs.last.evaluate('n=>{const r=n.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth}'), 'Keyboard focus did not reveal the last filter'
                page.screenshot(path=str(output / f'topic-controls-{width}.png'))

                page.evaluate("QB.nav('fsrs')")
                empty = page.get_by_role('button', name='No reviews due', exact=False)
                expect(empty).to_be_disabled()
                page.screenshot(path=str(output / f'fsrs-empty-{width}.png'))

                page.evaluate("QB.openBank('Biochemistry','Marrow'); QB.practiceOne('marrow__BIOCHEM_CH01_Q001')")
                page.locator('.option-list button').first.click()
                page.locator('.nk-note-add').click()
                page.locator('#nk-question-note-text').fill(PAYLOAD)
                page.get_by_role('button', name='Save note', exact=True).click()
                expect(page.locator('.nk-note-readonly')).to_have_text(PAYLOAD)
                page.evaluate("QB.nav('notes')")
                expect(page.locator('.nk-notes-item-text')).to_have_text(PAYLOAD)
                assert page.locator('.nk-notes-item-text img').count() == 0
                assert page.evaluate('window.__auditXss===undefined')
                assert not errors, errors
                reports.append({'width': width, 'auth_back_preserves_email': True, 'password_not_retained': True, 'header_controls_reachable': True, 'filter_labels_readable': True, 'empty_fsrs_disabled': True, 'learner_html_inert': True})
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (output / 'report.json').write_text(json.dumps(reports, indent=2))
    print('PREPRODUCTION_BROWSER_OK', json.dumps(reports))


if __name__ == '__main__':
    main()
