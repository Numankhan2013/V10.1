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
            for subject in ('Physiology','Biochemistry'):
                page.locator('button.nk-subject-row').filter(has_text=subject).click();page.wait_for_timeout(80)
                if f'#banks/{subject}' not in page.url: raise SystemExit(f'{subject} did not open bank selector: {page.url}')
                single=page.locator('button.nk-bank-card')
                if single.count()!=1: raise SystemExit(f'Expected only PrepLadder for {subject}, found {single.count()} banks')
                single_text=single.first.inner_text()
                if 'PrepLadder' not in single_text or 'Marrow' in single_text: raise SystemExit(f'Bank registry leaked Marrow into {subject}: {single_text!r}')
                page.evaluate("window.QB.nav('dashboard')");page.wait_for_timeout(80)
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
            support_lc=support.lower()
            if 'key takeaway' not in support_lc or 'detailed explanation' not in support_lc or 'structured text' not in support_lc: raise SystemExit('Structured Marrow explanation surface did not render: '+repr(support))
            if 'original pdf' in support_lc: raise SystemExit('Marrow explanation incorrectly fell back to Original PDF')
            if 'why the other options are wrong' not in support_lc: raise SystemExit('Gold pilot distractor section did not render')
            if page.locator('.nk-gold-wrong-row').count()!=3: raise SystemExit('Gold pilot must render exactly three wrong-option rationales')
            if 'compaction before cleavage' not in support_lc or 'implantation before cavitation' not in support_lc: raise SystemExit('Gold pilot Q10 distractor discriminators missing')
            if not page.locator('.nk-fsrs-rating').is_visible(): raise SystemExit('FSRS recall dock disappeared after Marrow explanation enhancement')
            dock_parent=page.locator('.nk-fsrs-rating').locator('xpath=ancestor::*[contains(@class,"nk-session-footer")]')
            if dock_parent.count()!=1: raise SystemExit('FSRS rating is no longer inside the floating session footer')
            footer_position=page.evaluate("getComputedStyle(document.querySelector('.nk-session-footer')).position")
            if footer_position!='fixed': raise SystemExit('FSRS/session footer is no longer floating/fixed: '+str(footer_position))
            page.screenshot(path=str(OUT/'03-marrow-gold-explanation.png'),full_page=True)

            # Verify an originally non-pilot question now uses the approved full-bank grammar.
            page.evaluate("window.QB.nav('banks','Anatomy')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Gametogenesis').click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').nth(1).click();page.wait_for_timeout(80)
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            rollout=page.locator('.nk-gold-explanation').inner_text().lower()
            if 'why the other options are wrong' not in rollout: raise SystemExit('Full-bank rollout missing from Gametogenesis Q2')
            if page.locator('.nk-gold-wrong-row').count()!=3: raise SystemExit('Full-bank Q2 must render three distractor rationales')
            if 'totipotent' not in rollout or 'oligopotent' not in rollout: raise SystemExit('Full-bank Q2 high-yield sequence missing')
            page.screenshot(path=str(OUT/'04-marrow-full-rollout-q2.png'),full_page=True)

            # Verify the micro-concision rule removes only the redundant lead repeat.
            page.evaluate("window.QB.nav('banks','Anatomy')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Gametogenesis').click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').nth(0).click();page.wait_for_timeout(80)
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            detail=page.locator('.nk-gold-explanation').inner_text()
            repeated='Primordial germ cells originate in the epiblast, during the 2nd week of development.'
            if repeated in detail: raise SystemExit('Micro-concision failed to remove duplicate takeaway paragraph')
            if 'Primordial germ cells (PGCs) are also known as primitive sex cells.' not in detail: raise SystemExit('Micro-concision removed useful source explanation content')
            if 'reach the developing gonads by the end of the 5th week' not in detail: raise SystemExit('Micro-concision removed source migration nuance')
            page.screenshot(path=str(OUT/'05-marrow-micro-concision.png'),full_page=True)

            # Verify a real source table survives the presentation layer.
            page.evaluate("window.QB.nav('banks','Anatomy')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Gametogenesis').click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').nth(4).click();page.wait_for_timeout(80)
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            if page.locator('.nk-gold-explanation .nk-marrow-table').count()!=1: raise SystemExit('Gold pilot source table did not survive')
            table_text=page.locator('.nk-gold-explanation .nk-marrow-table').inner_text()
            if 'Stages of prenatal development' not in table_text or 'Embryonic period (3-8 weeks)' not in table_text or 'Fetal period (9 weeks to birth)' not in table_text: raise SystemExit('Prenatal-development table content regressed')
            page.screenshot(path=str(OUT/'06-marrow-full-table.png'),full_page=True)

            page.evaluate("window.QB.nav('banks','Anatomy')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='PrepLadder').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=50: raise SystemExit('PrepLadder Anatomy topics regressed')
            if page.locator('body').get_by_text('Gametogenesis',exact=True).count(): raise SystemExit('Marrow topic leaked into PrepLadder')
            if errors: raise SystemExit('Browser errors: '+repr(errors))
            browser.close()
        server.shutdown()
    print('MARROW_BROWSER_OK registry=subject-indexed selector=2 marrow_topics=4 prepladder_topics=50 enhanced=62 rationales=186 micro_concision=verified table=preserved fsrs_dock=fixed')
if __name__=='__main__':main()
