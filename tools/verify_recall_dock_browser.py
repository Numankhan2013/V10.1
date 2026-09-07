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
            browser.close()
    finally:
        server.shutdown()
    print('RECALL_DOCK_BROWSER_OK widths=320,390,768 pre-answer-hidden fixed-placement text-only-pills rating-preserved')


if __name__ == '__main__':
    main()
