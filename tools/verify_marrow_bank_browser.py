#!/usr/bin/env python3
"""Browser smoke test and screenshots for the Marrow source-selection pilot."""
from __future__ import annotations
import contextlib,http.server,socketserver,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'build/web'; OUT=ROOT/'build/marrow-ui-checks'; OUT.mkdir(parents=True,exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def main():
    handler=lambda *a,**k: Quiet(*a,directory=str(WEB),**k)
    with socketserver.TCPServer(('127.0.0.1',0),handler) as server:
        port=server.server_address[1];thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={'width':390,'height':844})
            errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{port}/index.html',wait_until='networkidle')
            page.locator('button.nk-subject-row').filter(has_text='Anatomy').click()
            page.wait_for_timeout(100)
            if '#banks/Anatomy' not in page.url: raise SystemExit(f'Anatomy did not open bank selector: {page.url}')
            cards=page.locator('button.nk-bank-card')
            if cards.count()!=2: raise SystemExit(f'Expected 2 Anatomy banks, found {cards.count()}')
            body=page.locator('body').inner_text()
            for marker in ('PrepLadder','Marrow','1,068','62'):
                if marker not in body: raise SystemExit(f'Bank selector missing {marker}')
            page.screenshot(path=str(OUT/'01-anatomy-bank-selector.png'),full_page=True)
            cards.filter(has_text='Marrow').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=4: raise SystemExit('Marrow Anatomy topic count is not 4')
            if 'Marrow' not in page.locator('body').inner_text(): raise SystemExit('Marrow bank context is missing')
            page.screenshot(path=str(OUT/'02-marrow-topics.png'),full_page=True)
            page.locator('button.nk-topic-row').filter(has_text='Pre-Embryonic Phase of Development').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=13: raise SystemExit('Pre-Embryonic topic count is not 13')
            page.locator('button.nk-library-row').nth(9).click();page.wait_for_timeout(80)
            qtext=page.locator('.question-text').inner_text()
            for marker in ('1. Cavitation','2. Compaction','3. Implantation','4. Cleavage'):
                if marker not in qtext: raise SystemExit(f'Reconstructed Q10 list missing {marker}')
            page.locator('.option-list button').nth(3).click();page.wait_for_timeout(120)
            support=page.locator('.nk-study-support').inner_text()
            if 'Key takeaway' not in support or 'Detailed explanation' not in support or 'Structured text' not in support: raise SystemExit('Structured Marrow explanation surface did not render')
            if 'Original PDF' in support: raise SystemExit('Marrow explanation incorrectly fell back to Original PDF')
            page.screenshot(path=str(OUT/'03-marrow-structured-explanation.png'),full_page=True)
            page.evaluate("window.QB.nav('banks','Anatomy')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='PrepLadder').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=50: raise SystemExit('PrepLadder Anatomy topics regressed')
            if page.locator('body').get_by_text('Gametogenesis',exact=True).count(): raise SystemExit('Marrow topic leaked into PrepLadder')
            if errors: raise SystemExit('Browser errors: '+repr(errors))
            browser.close()
        server.shutdown()
    print('MARROW_BROWSER_OK selector=2 marrow_topics=4 prepladder_topics=50 structured_explanation=ok')
if __name__=='__main__':main()
