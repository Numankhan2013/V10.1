#!/usr/bin/env python3
"""Exercise the generated updater with real waiting service workers and idle time."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main():
    generated = (ROOT / 'build/web/index.html').read_text()
    core = re.search(r'/\* NK_PWA_UPDATE_V2_START \*/.*?/\* NK_PWA_UPDATE_V2_END \*/', generated, re.S).group()
    assert 'meta name="nk-qbank-build"' in generated, 'Web builds must identify the running page'
    worker = (ROOT / 'build/web/sw.js').read_text()
    worker = re.sub(r'const SHELL=\[.*?\];', "const SHELL=['./','./index.html'];", worker, count=1, flags=re.S)
    versions = {'page': 'first', 'worker': 'first'}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?', 1)[0] == '/sw.js':
                body = re.sub(r'const BUILD_VERSION=.*?;', f"const BUILD_VERSION='{versions['worker']}';", worker, count=1).encode()
                content_type = 'application/javascript'
            else:
                body = (f'<meta name="nk-qbank-build" content="{versions["page"]}"><h1>Study screen</h1><script>window.QB={{getState:()=>({{activeSession:null}})}};{core}</script>').encode()
                content_type = 'text/html'
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(origin)
            page.wait_for_function('navigator.serviceWorker.controller')
            # The reported 10–15 second inactivity window must remain quiet.
            page.wait_for_timeout(16000)
            assert page.locator('.nk-pwa-update').count() == 0
            versions['worker'] = 'second'
            page.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update();}')
            expect(page.locator('.nk-pwa-update')).to_be_visible()
            page.get_by_role('button', name='Dismiss update for now').click()
            assert page.locator('.nk-pwa-update').count() == 0
            page.reload()
            page.wait_for_timeout(2500)
            assert page.locator('.nk-pwa-update').count() == 0, 'Dismissal must survive reload'
            versions['page'] = 'second'
            same = context.new_page()
            same.goto(origin)
            same.wait_for_function('navigator.serviceWorker.controller')
            same.wait_for_timeout(2500)
            assert same.locator('.nk-pwa-update').count() == 0, 'A waiting build already on screen must stay quiet'
            versions['page'] = 'first'
            other = context.new_page()
            other.goto(origin)
            expect(other.locator('.nk-pwa-update')).to_be_visible()
            versions['page'] = 'second'
            other.get_by_role('button', name='Update', exact=True).click()
            other.wait_for_function('document.querySelector("meta[name=nk-qbank-build]").content==="second"')
            other.wait_for_timeout(2500)
            assert other.locator('.nk-pwa-update').count() == 0
            assert not errors, errors
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print('PWA_UPDATE_BROWSER_OK idle16s=true same_build_quiet=true real_update=true dismissal_reload=true explicit_update=true')


if __name__ == '__main__':
    main()
