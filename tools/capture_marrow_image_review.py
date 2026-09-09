#!/usr/bin/env python3
"""Render source/production comparisons in Ubuntu CI."""
import functools
import http.server
import json
import socketserver
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    output=ROOT/'build/marrow-image-review';output.mkdir(parents=True,exist_ok=True)
    registry=json.loads((ROOT/'data/marrow/images/registry.json').read_text())
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    with socketserver.TCPServer(('127.0.0.1',0),handler) as server:
        threading.Thread(target=server.serve_forever,daemon=True).start()
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page(viewport={'width':1400,'height':1100})
            for a in registry['assets']:
                source=f'http://127.0.0.1:{server.server_address[1]}/'
                page.set_content('<body style="margin:20px;font-family:Arial"><h1>Source / production</h1><main style="display:grid;grid-template-columns:1fr 1fr;gap:20px"><img style="width:100%;height:auto" src="'+source+a['original']['path']+'"><img style="width:100%;height:auto" src="'+source+a['production']['path']+'"></main></body>')
                page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
                page.screenshot(path=str(output/(a['id']+'.png')),full_page=True)
            browser.close()
        server.shutdown()
if __name__=='__main__':main()
