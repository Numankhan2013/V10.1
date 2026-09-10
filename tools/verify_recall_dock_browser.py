#!/usr/bin/env python3
"""Linux CI: exercise the generated app and capture the actual recall footer."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    web = ROOT / 'build/web'
    assert 'NK_FSRS_RECALL_DOCK_V2' in (web / 'index.html').read_text(), 'New dock CSS missing from generated app'
    output = ROOT / 'build/ui-checks'
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width in (320, 390, 768):
                context = browser.new_context(viewport={'width': width, 'height': 844}, device_scale_factor=1, reduced_motion='reduce', service_workers='block')
                page = context.new_page()
                # No real account or cloud requests are needed for this UI check.
                page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + '/#dashboard', wait_until='domcontentloaded')
                page.wait_for_function('window.QB && window.QB.getState')
                page.evaluate("window.QB.practiceOne('1-1')")
                assert page.locator('.nk-fsrs-rating').count() == 0, 'Dock appeared before answering'
                page.evaluate("window.QB.selectPractice('1-1',2)")
                dock = page.locator('.nk-session-footer .nk-fsrs-rating')
                dock.wait_for(state='visible')
                buttons = dock.locator('button')
                assert buttons.all_text_contents() == ['Hard', 'Good', 'Easy']
                assert dock.locator('svg').count() == 1
                assert dock.get_by_role('button', name='Good', exact=True).get_attribute('aria-pressed') == 'true'
                box = dock.bounding_box()
                nav = page.locator('.nk-session-footer .fixed-actions-inner').bounding_box()
                assert box and nav and box['y'] + box['height'] <= nav['y'], 'Dock must sit above Previous/Next'
                assert box['x'] >= 0 and box['x'] + box['width'] <= width + 1, 'Dock overflows viewport'
                assert nav['y'] + nav['height'] <= 844, 'Navigation is below the viewport'
                for button in buttons.all():
                    bounds = button.bounding_box()
                    assert bounds['width'] >= 40 and bounds['height'] >= 44, 'Rating target too small'
                page.locator('.nk-session-footer').screenshot(path=str(output / f'recall-dock-{width}.png'))
                # Scroll through the explanation; the dock stays next to navigation.
                top = box['y']
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                assert abs(dock.bounding_box()['y'] - top) < 1, 'Dock moved with content'
                dock.get_by_role('button', name='Hard', exact=True).click()
                assert page.locator('.nk-fsrs-rating').count() == 0
                assert page.evaluate("window.QB.getState().attempts['1-1'].at(-1).rating") == 2
                context.close()

            # Physiology Chapter 9 stable-identity reconstruction regression.
            # Select the chapter by its canonical ID and the 24th source-order row;
            # the distinctive post-answer reconstruction assertions below prove the
            # expected Q24 record without coupling the gate to mutable stem wording.
            context = browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, reduced_motion='reduce', service_workers='block')
            page = context.new_page()
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + '/#dashboard', wait_until='domcontentloaded')
            page.wait_for_function('window.QB && window.QB.getState')
            page.evaluate("window.QB.nav('banks','Physiology')")
            page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click()
            page.wait_for_timeout(80)
            page.locator("button.nk-topic-row[onclick=\"window.QB.openChapter('9')\"]").click()
            page.wait_for_timeout(80)
            assert page.locator('button.nk-library-row').count() == 27, 'Marrow Physiology Chapter 9 count is not 27'
            page.locator('button.nk-library-row').nth(23).click()
            page.wait_for_timeout(80)
            page.locator('.option-list button').first.click()
            page.wait_for_timeout(120)
            support = page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway', 'detailed explanation', 'structured text', 'why the other options are wrong', 'enkephalins', 'δ receptors', 'dynorphins', 'κ receptors', 'β-endorphin', 'μ'):
                assert required in support, f'Physiology Chapter 9 Q24 reconstruction missing {required}'
            assert page.locator('.nk-gold-wrong-row').count() == 3, 'Physiology Chapter 9 Q24 must render exactly three distractor rationales'
            page.screenshot(path=str(output / 'physiology-ch09-q24-opioid-reconstruction.png'), full_page=True)
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print('RECALL_DOCK_BROWSER_OK widths=320,390,768 pre-answer-hidden fixed-placement text-only-pills rating-preserved physiology_ch09_q24=verified')


if __name__ == '__main__':
    main()
