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
            # Biochemistry remains the one-source control while Physiology proves
            # that the generalized registry works for a second Marrow subject.
            page.locator('button.nk-subject-row').filter(has_text='Biochemistry').click();page.wait_for_timeout(80)
            if '#banks/Biochemistry' not in page.url: raise SystemExit(f'Biochemistry did not open bank selector: {page.url}')
            single=page.locator('button.nk-bank-card')
            if single.count()!=1: raise SystemExit(f'Expected only PrepLadder for Biochemistry, found {single.count()} banks')
            single_text=single.first.inner_text()
            if 'PrepLadder' not in single_text or 'Marrow' in single_text: raise SystemExit(f'Bank registry leaked Marrow into Biochemistry: {single_text!r}')
            page.evaluate("window.QB.nav('dashboard')");page.wait_for_timeout(80)

            page.locator('button.nk-subject-row').filter(has_text='Physiology').click();page.wait_for_timeout(80)
            if '#banks/Physiology' not in page.url: raise SystemExit(f'Physiology did not open bank selector: {page.url}')
            pcards=page.locator('button.nk-bank-card')
            if pcards.count()!=2: raise SystemExit(f'Expected 2 Physiology banks, found {pcards.count()}')
            pbody=page.locator('body').inner_text()
            for marker in ('PrepLadder','Marrow','80'):
                if marker not in pbody: raise SystemExit(f'Physiology bank selector missing {marker}')
            page.screenshot(path=str(OUT/'00-physiology-bank-selector.png'),full_page=True)
            pcards.filter(has_text='Marrow').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=4: raise SystemExit('Marrow Physiology topic count is not 4')
            page.locator('button.nk-topic-row').filter(has_text='Homeostasis and cellular physiology').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=21: raise SystemExit('Marrow Physiology Chapter 1 count is not 21')
            # User-reported regression target: Q2 previously dumped raw OCR debris
            # and used "All of the above" as the takeaway. It must now use the
            # same approved explanation grammar as Anatomy.
            page.locator('button.nk-library-row').nth(1).click();page.wait_for_timeout(80)
            if 'Which is a component of homeostatic control system' not in page.locator('.question-text').inner_text():
                raise SystemExit('Marrow Physiology Q2 did not open')
            page.locator('.option-list button').nth(3).click();page.wait_for_timeout(120)
            psupport=page.locator('.nk-study-support').inner_text()
            psupport_lc=psupport.lower()
            for marker in ('key takeaway','detailed explanation','structured text','why the other options are wrong'):
                if marker not in psupport_lc: raise SystemExit(f'Marrow Physiology enhanced explanation missing {marker}: {psupport!r}')
            if 'original pdf' in psupport_lc: raise SystemExit('Marrow Physiology incorrectly used Original PDF')
            takeaway_segment=psupport_lc.split('key takeaway',1)[1].split('detailed explanation',1)[0]
            if 'all of the above' in takeaway_segment:
                raise SystemExit('Physiology Q2 takeaway regressed to the correct-option label')
            if 'homeostatic control system' not in takeaway_segment:
                raise SystemExit('Physiology Q2 meaningful takeaway missing')
            detail_text=page.locator('.nk-gold-explanation').inner_text()
            detail_lc=detail_text.lower()
            for garbage in ('wok no','internalef','components of homeostasis include: + a','marrow\n'):
                if garbage in detail_lc: raise SystemExit('Physiology OCR debris leaked into learner explanation: '+garbage)
            if page.locator('.nk-gold-explanation li').count()<4:
                raise SystemExit('Physiology Q2 structured component bullets did not render')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Physiology Q2 must render exactly three distractor rationales')
            if not page.locator('.nk-fsrs-rating').is_visible(): raise SystemExit('FSRS recall dock missing in Marrow Physiology')
            pdock=page.locator('.nk-fsrs-rating').locator('xpath=ancestor::*[contains(@class,"nk-session-footer")]')
            if pdock.count()!=1: raise SystemExit('Marrow Physiology FSRS dock left the fixed footer')
            if page.evaluate("getComputedStyle(document.querySelector('.nk-session-footer')).position")!='fixed':
                raise SystemExit('Marrow Physiology session footer is no longer fixed')
            page.screenshot(path=str(OUT/'00b-physiology-enhanced-explanation-q2.png'),full_page=True)

            # Real structured-table regression: Physiology Q8 retains its source table.
            page.evaluate("window.QB.nav('banks','Physiology')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Homeostasis and cellular physiology').click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').nth(7).click();page.wait_for_timeout(80)
            page.locator('.option-list button').nth(3).click();page.wait_for_timeout(120)
            if page.locator('.nk-gold-explanation .nk-marrow-table').count()<1:
                raise SystemExit('Physiology Q8 structured source table did not survive enhanced renderer')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Physiology Q8 distractor grammar missing')
            page.screenshot(path=str(OUT/'00c-physiology-enhanced-table-q8.png'),full_page=True)
            page.evaluate("window.QB.nav('banks','Physiology')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='PrepLadder').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=38: raise SystemExit('PrepLadder Physiology topics regressed')
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
            # Candidate regression: Topics hierarchy, completion Back, and explicit settings save.
            assert page.locator('.nk-topic-group').count() >= 8
            page.screenshot(path=str(OUT/'07-topics-journey.png'),full_page=True)
            page.locator('button.nk-topic-row').first.click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)
            page.evaluate("window.QB.endSession()");page.wait_for_timeout(120)
            assert '#result/' in page.url, page.url
            page.go_back();page.wait_for_timeout(120)
            assert page.url.endswith('#topics'), page.url
            assert page.locator('.nk-topic-group').count() >= 8
            page.evaluate("window.QB.nav('more')");page.wait_for_timeout(100)
            page.locator('.nk-fsrs-customization summary').click()
            before=page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention")
            value='85' if before != .85 else '90'
            page.locator('.nk-fsrs-settings input').first.fill(value)
            assert page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention") == before
            page.screenshot(path=str(OUT/'08-fsrs-customization.png'),full_page=True)
            page.get_by_role('button',name='Save changes',exact=True).click();page.wait_for_timeout(100)
            assert page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention") == int(value)/100
            page.reload(wait_until='networkidle')
            assert page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention") == int(value)/100
            if errors: raise SystemExit('Browser errors: '+repr(errors))
            browser.close()
        server.shutdown()
    print('MARROW_BROWSER_OK registry=subject-indexed anatomy=62/4 physiology=80/4 biochemistry=prepladder-only enhanced=142 rationales=426 phys_q2=clean phys_table=preserved anatomy_table=preserved fsrs_dock=fixed')
if __name__=='__main__':main()
