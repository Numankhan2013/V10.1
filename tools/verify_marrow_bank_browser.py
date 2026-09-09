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
    def translate_path(self,path):
        # Cloudflare Pages serves this route through _worker.js. The CI smoke
        # test intentionally uses a plain local static server, so map the same
        # public route to the exact committed Anatomy source PDF here.
        if path.split('?',1)[0].split('#',1)[0]=='/anatomy-source.pdf':
            return str(ROOT/'app/src/main/assets/Anatomy_QBank_Source.pdf')
        return super().translate_path(path)

def main():
    handler=lambda *a,**k: Quiet(*a,directory=str(WEB),**k)
    with socketserver.TCPServer(('127.0.0.1',0),handler) as server:
        port=server.server_address[1];thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={'width':390,'height':844})
            # The CI static server does not execute the Pages streaming worker.
            # Serve the identical committed Anatomy PDF for deterministic raster checks.
            page.route('**/*.pdf*',lambda route: route.fulfill(path=str(ROOT/'app/src/main/assets/Anatomy_QBank_Source.pdf'),content_type='application/pdf',headers={'Access-Control-Allow-Origin':'*'}) if 'anatomy' in route.request.url.lower() else route.continue_())
            errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{port}/index.html',wait_until='networkidle')
            def assert_sections(expected):
                actual=page.locator('.nk-topic-group>h2').all_inner_texts()
                if actual!=expected: raise SystemExit(f'Marrow topic sections/order mismatch: {actual!r}')
            # All three supplied subjects now use the same shared bank registry.
            # Biochemistry is the new-subject smoke test and deliberately checks
            # the source-faithful base Marrow renderer, not explanation polish.
            page.locator('button.nk-subject-row').filter(has_text='Biochemistry').click();page.wait_for_timeout(80)
            if '#banks/Biochemistry' not in page.url: raise SystemExit(f'Biochemistry did not open bank selector: {page.url}')
            bcards=page.locator('button.nk-bank-card')
            if bcards.count()!=2: raise SystemExit(f'Expected 2 Biochemistry banks, found {bcards.count()}')
            bbody=page.locator('body').inner_text()
            for marker in ('PrepLadder','Marrow','543'):
                if marker not in bbody: raise SystemExit(f'Biochemistry bank selector missing {marker}')
            page.screenshot(path=str(OUT/'00-biochemistry-bank-selector.png'),full_page=True)
            bcards.filter(has_text='Marrow').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=26: raise SystemExit('Marrow Biochemistry topic count is not 26')
            assert_sections(['Carbohydrate Chemistry','Lipid Chemistry','Amino Acid & Protein Chemistry','Heme Synthesis','Enzymes','Free Radicals, Antioxidants, Trace Elements & Miscellaneous','Genetics','Vitamins'])
            page.locator('button.nk-topic-row').filter(has_text='Chemistry of Carbohydrates, Amino sugars and Mucopolysaccharides').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=23: raise SystemExit('Marrow Biochemistry Chapter 1 count is not 23')
            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)
            page.locator('.option-list button').first.click();page.wait_for_timeout(120)
            bsupport=page.locator('.nk-study-support').inner_text().lower()
            for marker in ('key takeaway','detailed explanation','structured text','why the other options are wrong','erythrose','ketose'):
                if marker not in bsupport: raise SystemExit(f'Marrow Biochemistry Chapter 1 rollout explanation missing {marker}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Marrow Biochemistry Chapter 1 Q1 must render exactly three distractor rationales')
            if 'original pdf' in bsupport: raise SystemExit('Marrow Biochemistry incorrectly used Original PDF')
            # FSRS footer placement is exercised below on the approved Q23 gold
            # sample and on Physiology/Anatomy; keep this Q1 assertion focused on
            # the new Chapter 1 explanation rollout itself.
            page.screenshot(path=str(OUT/'00a-biochemistry-ch01-rollout-q1.png'),full_page=True)

            # The next bounded rollout completes Chapter 4 without changing the
            # raw Marrow record or the fixed explanation/session layout.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='HMP shunt pathway, Fructose , Galactose metabolism').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=11: raise SystemExit('Marrow Biochemistry Chapter 4 count is not 11')
            page.locator('button.nk-library-row').nth(10).click();page.wait_for_timeout(80)
            if 'newborn baby refuses breast milk' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 4 Q11 did not open')
            page.locator('.option-list button').nth(2).click();page.wait_for_timeout(120)
            bchapter4=page.locator('.nk-study-support').inner_text().lower()
            for marker in ('classic galactosemia','galactose-1-phosphate uridyltransferase','oil-drop cataract','why the other options are wrong'):
                if marker not in bchapter4: raise SystemExit(f'Biochemistry Chapter 4 explanation missing {marker}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Marrow Biochemistry Chapter 4 Q11 must render exactly three distractor rationales')
            if page.locator('.nk-fsrs-rating').locator('xpath=ancestor::*[contains(@class,"nk-session-footer")]').count()!=1:
                raise SystemExit('Biochemistry Chapter 4 work moved FSRS out of the fixed footer')
            page.screenshot(path=str(OUT/'00aaa-biochemistry-ch04-rollout-q11.png'),full_page=True)

            # Chapter 2 rollout regression: Q1 must use the same approved
            # grammar while remaining in the original source topic.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Glycolysis and gluconeogenesis').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=30:
                raise SystemExit('Marrow Biochemistry Chapter 2 count is not 30')
            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)
            if 'glucose transporter' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 2 rollout Q1 did not open')
            page.locator('.option-list button').nth(3).click();page.wait_for_timeout(120)
            ch2=page.locator('.nk-study-support').inner_text().lower()
            for marker in ('key takeaway','detailed explanation','structured text','why the other options are wrong','glut4','insulin-responsive'):
                if marker not in ch2:
                    raise SystemExit(f'Biochemistry Chapter 2 rollout missing {marker}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 2 Q1 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aab-biochemistry-ch02-rollout-q1.png'),full_page=True)

            # Chapter 3 OCR-cleanup regression: Q12 has raw source spillover into
            # later solutions. The learner-facing augmentation must isolate the
            # debranching explanation without mutating the source record.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Glycogen metabolism and glycogen storage disorders').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=20:
                raise SystemExit('Marrow Biochemistry Chapter 3 count is not 20')
            page.locator('button.nk-library-row').nth(11).click();page.wait_for_timeout(80)
            if 'debranching enzyme' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 3 rollout Q12 did not open')
            page.locator('.option-list button').first.click();page.wait_for_timeout(120)
            ch3=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','amylo-1,6-glucosidase','α(1→6)'):
                if required not in ch3:
                    raise SystemExit(f'Biochemistry Chapter 3 rollout missing {required}')
            for leaked in ('solution to question 13','solution to question 20','pompe disease is the glycogen'):
                if leaked in ch3:
                    raise SystemExit(f'Biochemistry Chapter 3 Q12 leaked raw spillover: {leaked}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 3 Q12 must render exactly three distractor rationales')
            # FSRS placement is protected by the dedicated recall-dock browser
            # gate and the existing Biochemistry gold-sample regression. Keep this
            # check scoped to Chapter 3 explanation content and spillover isolation.
            page.screenshot(path=str(OUT/'00aac-biochemistry-ch03-rollout-q12.png'),full_page=True)

            # Chapter 5 rollout regression: Q18 is a clean calculation item
            # outside the fixed gold sample and must render the approved grammar.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='ETC and bioenergetics').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=18:
                raise SystemExit('Marrow Biochemistry Chapter 5 count is not 18')
            page.locator('button.nk-library-row').nth(17).click();page.wait_for_timeout(80)
            if 'tpn bag' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 5 rollout Q18 did not open')
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            ch5=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','880 kcal','400 + 120 + 360'):
                if required not in ch5:
                    raise SystemExit(f'Biochemistry Chapter 5 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 5 Q18 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aad-biochemistry-ch05-rollout-q18.png'),full_page=True)

            # Chapter 6 rollout regression: Q11 tests a source-faithful ATP
            # yield calculation outside the fixed gold sample.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Krebs Cycle').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=20:
                raise SystemExit('Marrow Biochemistry Chapter 6 count is not 20')
            page.locator('button.nk-library-row').nth(10).click();page.wait_for_timeout(80)
            if 'atps are generated per turn' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 6 rollout Q11 did not open')
            page.locator('.option-list button').first.click();page.wait_for_timeout(120)
            ch6=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','10 atp','3 nadh','1 fadh₂','1 gtp'):
                if required not in ch6:
                    raise SystemExit(f'Biochemistry Chapter 6 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 6 Q11 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aae-biochemistry-ch06-rollout-q11.png'),full_page=True)

            # Chapter 7 rollout regression: Q18 checks the distinction between
            # isoelectric pH and the pKa region of maximum buffering.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Amino acids: Basics').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=27:
                raise SystemExit('Marrow Biochemistry Chapter 7 count is not 27')
            page.locator('button.nk-library-row').nth(17).click();page.wait_for_timeout(80)
            if 'isoelectric ph' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 7 rollout Q18 did not open')
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            ch7=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','no net charge','maximum buffering occurs around a pka','minimum solubility'):
                if required not in ch7:
                    raise SystemExit(f'Biochemistry Chapter 7 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 7 Q18 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aaf-biochemistry-ch07-rollout-q18.png'),full_page=True)

            # Chapter 8 rollout regression: Q19 preserves the source-keyed
            # glutathione answer while making the duplicate-component option explicit.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Amino acid: Metabolism').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=23:
                raise SystemExit('Marrow Biochemistry Chapter 8 count is not 23')
            page.locator('button.nk-library-row').nth(18).click();page.wait_for_timeout(80)
            if 'glutathione' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 8 rollout Q19 did not open')
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            ch8=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','glutamate, cysteine and glycine','same three amino-acid components'):
                if required not in ch8:
                    raise SystemExit(f'Biochemistry Chapter 8 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 8 Q19 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aag-biochemistry-ch08-rollout-q19.png'),full_page=True)

            # Chapter 9 rollout regression: Q15 checks the high-yield
            # homocystinuria lens-direction and thrombosis distinction.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Amino acid: Metabolic disorder').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=28:
                raise SystemExit('Marrow Biochemistry Chapter 9 count is not 28')
            page.locator('button.nk-library-row').nth(14).click();page.wait_for_timeout(80)
            if 'left side of the body' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 9 rollout Q15 did not open')
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            ch9=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','cystathionine β-synthase deficiency','downward/nasal subluxation','thrombotic'):
                if required not in ch9:
                    raise SystemExit(f'Biochemistry Chapter 9 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 9 Q15 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aah-biochemistry-ch09-rollout-q15.png'),full_page=True)

            # Chapter 10 rollout regression: Q20 checks the collagen
            # Gly-X-Y explanation through the real learner-facing surface.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Protein structure and function').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=33:
                raise SystemExit('Marrow Biochemistry Chapter 10 count is not 33')
            page.locator('button.nk-library-row').nth(19).click();page.wait_for_timeout(80)
            if 'all are true about collagen' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 10 rollout Q20 did not open')
            page.locator('.option-list button').nth(2).click();page.wait_for_timeout(120)
            ch10=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','gly-x-y','glycine occurs at every third position','type iv collagen','procollagen'):
                if required not in ch10:
                    raise SystemExit(f'Biochemistry Chapter 10 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 10 Q20 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aai-biochemistry-ch10-rollout-q20.png'),full_page=True)

            # Chapter 11 rollout regression: Q3 checks OTC deficiency as
            # the X-linked urea-cycle disorder with orotic-acid excess.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Urea cycle and its disorders').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=14:
                raise SystemExit('Marrow Biochemistry Chapter 11 count is not 14')
            page.locator('button.nk-library-row').nth(2).click();page.wait_for_timeout(80)
            if 'x-linked recessive' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Chapter 11 rollout Q3 did not open')
            page.locator('.option-list button').nth(2).click();page.wait_for_timeout(120)
            ch11=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','ornithine transcarbamylase','hyperammonemia type ii','urinary orotic acid'):
                if required not in ch11:
                    raise SystemExit(f'Biochemistry Chapter 11 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry Chapter 11 Q3 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aaj-biochemistry-ch11-rollout-q03.png'),full_page=True)

            # Physiology Chapter 5 rollout regression: Q17 distinguishes
            # iso-osmotic permeant urea from effective tonicity.
            page.evaluate("window.QB.nav('banks','Physiology')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Body Fluids').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=28:
                raise SystemExit('Marrow Physiology Chapter 5 count is not 28')
            page.locator('button.nk-library-row').nth(16).click();page.wait_for_timeout(80)
            if 'rapid lysis of the rbcs' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Physiology Chapter 5 rollout Q17 did not open')
            page.locator('.option-list button').nth(3).click();page.wait_for_timeout(120)
            ph5=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','urea rapidly crosses the red-cell membrane','water follows','tonicity'):
                if required not in ph5:
                    raise SystemExit(f'Physiology Chapter 5 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Physiology Chapter 5 Q17 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aak-physiology-ch05-rollout-q17.png'),full_page=True)

            # Physiology Chapter 6 reconstruction regression: Q23 must
            # teach correct EPP physiology while preserving the source-key defect.
            page.evaluate("window.QB.nav('banks','Physiology')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Physiology of Nerve').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=34:
                raise SystemExit('Marrow Physiology Chapter 6 count is not 34')
            page.locator('button.nk-library-row').nth(22).click();page.wait_for_timeout(80)
            if 'end plate potential' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Physiology Chapter 6 rollout Q23 did not open')
            page.locator('.option-list button').nth(0).click();page.wait_for_timeout(120)
            ph6=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','graded depolarization','not an all-or-none event','option c','internally inconsistent'):
                if required not in ph6:
                    raise SystemExit(f'Physiology Chapter 6 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Physiology Chapter 6 Q23 must render exactly three option rationales')
            page.screenshot(path=str(OUT/'00aal-physiology-ch06-rollout-q23.png'),full_page=True)

            # Physiology Chapter 7 reconstruction regression: Q35 must
            # recover standard skeletal-muscle EC coupling without inventing
            # the missing verbatim numbered statements.
            page.evaluate("window.QB.nav('banks','Physiology')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Muscle Physiology I 35 questions').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=35:
                raise SystemExit('Marrow Physiology Chapter 7 count is not 35')
            page.locator('button.nk-library-row').nth(34).click();page.wait_for_timeout(80)
            if 'skeletal muscle contraction' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Physiology Chapter 7 rollout Q35 did not open')
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            ph7=page.locator('.nk-study-support').inner_text().lower()
            for required in ('key takeaway','detailed explanation','structured text','why the other options are wrong','ca2+ release from the sarcoplasmic reticulum','dhpr voltage sensors','extracellular ca2+ influx is not required'):
                if required not in ph7:
                    raise SystemExit(f'Physiology Chapter 7 rollout missing {required}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Physiology Chapter 7 Q35 must render exactly three distractor rationales')
            page.screenshot(path=str(OUT/'00aam-physiology-ch07-rollout-q35.png'),full_page=True)

            # Explanation-quality candidate regression: Chapter 1 Q23 is one of
            # the deterministic 20-question Biochemistry sample entries and must
            # use the exact approved 142-question presentation grammar.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Chemistry of Carbohydrates, Amino sugars and Mucopolysaccharides').click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').nth(22).click();page.wait_for_timeout(80)
            q23_text=page.locator('.question-text').inner_text().lower()
            if '5-year-old boy' not in q23_text or 'bone marrow aspiration' not in q23_text:
                raise SystemExit('Biochemistry gold-sample Q23 did not open')
            figure=page.locator('.nk-marrow-figure-button')
            assert figure.count()==1, 'Question microscopy figure missing or duplicated'
            page.wait_for_function('document.querySelector(".nk-marrow-figure-button img")?.naturalWidth===720')
            figure.click()
            page.wait_for_function('document.querySelector("#nk-source-viewer img")?.naturalWidth===720')
            page.locator('#nk-source-viewer [data-z="+"]').click()
            page.screenshot(path=str(OUT/'00b-marrow-microscopy-zoom.png'))
            page.locator('#nk-source-viewer .nk-sv-close').click()
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            bgold=page.locator('.nk-study-support').inner_text()
            bgold_lc=bgold.lower()
            for marker in ('key takeaway','detailed explanation','structured text','why the other options are wrong','glucocerebrosidase','crumpled tissue paper'):
                if marker not in bgold_lc:
                    raise SystemExit(f'Biochemistry gold-sample explanation missing {marker}: {bgold!r}')
            if page.locator('.nk-gold-wrong-row').count()!=3:
                raise SystemExit('Biochemistry gold-sample Q23 must render exactly three distractor rationales')
            if not page.locator('.nk-fsrs-rating').is_visible():
                raise SystemExit('FSRS recall dock missing in Biochemistry gold-sample question')
            bfooter=page.locator('.nk-fsrs-rating').locator('xpath=ancestor::*[contains(@class,"nk-session-footer")]')
            if bfooter.count()!=1 or page.evaluate("getComputedStyle(document.querySelector('.nk-session-footer')).position")!='fixed':
                raise SystemExit('Biochemistry gold-sample work moved FSRS out of the fixed footer')
            page.screenshot(path=str(OUT/'00aa-biochemistry-gold-sample-q23.png'),full_page=True)

            # Reconstructed explanation diagrams must remain hidden until the
            # learner answers, then use the same fullscreen source viewer.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Glycolysis and gluconeogenesis').click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').nth(7).click();page.wait_for_timeout(80)
            if page.locator('.nk-marrow-figure-button').count()!=0:
                raise SystemExit('Explanation-only glycolysis figure leaked before answering')
            page.locator('.option-list button').nth(2).click();page.wait_for_timeout(120)
            glycolysis=page.locator('.nk-marrow-figure-button')
            if glycolysis.count()!=1: raise SystemExit('Reconstructed glycolysis figure missing or duplicated')
            page.wait_for_function('document.querySelector(".nk-marrow-figure-button img")?.naturalWidth===900')
            glycolysis.click();page.wait_for_timeout(60)
            page.wait_for_function('document.querySelector("#nk-source-viewer img")?.naturalWidth===900')
            page.screenshot(path=str(OUT/'00ab-marrow-glycolysis-reconstruction.png'))
            page.locator('#nk-source-viewer .nk-sv-close').click()

            # Authentic microscopy required by a stem is visible before answer,
            # retains native pixels, and uses neutral non-answering alt text.
            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Glycogen metabolism and glycogen storage disorders').click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').nth(15).click();page.wait_for_timeout(80)
            if '6-month-old baby' not in page.locator('.question-text').inner_text():
                raise SystemExit('Biochemistry glycogen-storage Q16 did not open')
            biopsy=page.locator('.nk-marrow-figure-button')
            if biopsy.count()!=1: raise SystemExit('Question-critical muscle biopsy missing or duplicated')
            page.wait_for_function('document.querySelector(".nk-marrow-figure-button img")?.naturalWidth===720')
            biopsy_alt=biopsy.locator('img').get_attribute('alt').lower()
            if 'pompe' in biopsy_alt: raise SystemExit('Question-critical image alt text reveals the diagnosis')
            page.screenshot(path=str(OUT/'00ac-marrow-question-biopsy.png'),full_page=True)

            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='PrepLadder').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()<1: raise SystemExit('PrepLadder Biochemistry topics regressed')
            page.evaluate("window.QB.nav('dashboard')");page.wait_for_timeout(80)

            page.locator('button.nk-subject-row').filter(has_text='Physiology').click();page.wait_for_timeout(80)
            if '#banks/Physiology' not in page.url: raise SystemExit(f'Physiology did not open bank selector: {page.url}')
            pcards=page.locator('button.nk-bank-card')
            if pcards.count()!=2: raise SystemExit(f'Expected 2 Physiology banks, found {pcards.count()}')
            pbody=page.locator('body').inner_text()
            for marker in ('PrepLadder','Marrow','753'):
                if marker not in pbody: raise SystemExit(f'Physiology bank selector missing {marker}')
            page.screenshot(path=str(OUT/'00-physiology-bank-selector.png'),full_page=True)
            pcards.filter(has_text='Marrow').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=33: raise SystemExit('Marrow Physiology topic count is not 33')
            assert_sections(['CNS Physiology','General Physiology','Cellular Physiology','Neuromuscular Physiology','Cardiovascular System','Respiratory System','Gastrointestinal System'])
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
            for marker in ('PrepLadder','Marrow','1,068','819'):
                if marker not in body: raise SystemExit(f'Bank selector missing {marker}')
            page.screenshot(path=str(OUT/'01-anatomy-bank-selector.png'),full_page=True)
            cards.filter(has_text='Marrow').click();page.wait_for_timeout(100)
            if page.locator('button.nk-topic-row').count()!=48: raise SystemExit('Marrow Anatomy topic count is not 48')
            assert_sections(['General Embryology','Histology','Neuroanatomy','Head & Neck','Upper Limb','Thorax','Abdomen','Systemic Embryology'])
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
            for fraction in (0,.5,1):
                page.evaluate('(f)=>window.scrollTo(0,(document.documentElement.scrollHeight-innerHeight)*f)',fraction)
                page.wait_for_timeout(100)
                box=page.locator('.nk-continue-learning').bounding_box()
                assert box and box['y']>=0 and box['y']+box['height']<844-76, box
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(OUT/'07a-topics-first-viewport.png'))
            page.get_by_role('button',name='Topic index',exact=True).click()
            page.locator('.nk-index-link').filter(has_text='General Embryology').click()
            page.screenshot(path=str(OUT/'07b-topics-reference-section.png'))
            page.evaluate('window.scrollTo(0,0)')
            page.locator('button.nk-topic-row').first.click();page.wait_for_timeout(80)
            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)
            page.evaluate("window.QB.endSession()");page.wait_for_timeout(120)
            assert '#result/' in page.url, page.url
            page.go_back();page.wait_for_timeout(120)
            assert page.url.endswith('#topics'), page.url
            assert page.locator('.nk-topic-group').count() >= 8
            page.evaluate("window.QB.nav('more')");page.wait_for_timeout(100)
            page.locator('.nk-fsrs-settings-entry').click();page.wait_for_timeout(100)
            assert page.url.endswith('#fsrs-settings')
            before=page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention")
            value='85' if before != .85 else '90'
            page.locator('.nk-fsrs-settings input').first.fill(value)
            assert page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention") == before
            page.screenshot(path=str(OUT/'08-fsrs-customization.png'),full_page=True)
            print('SETTINGS_SAVE_POSITION',page.locator('.nk-fsrs-settings-save').evaluate('(n)=>({position:getComputedStyle(n).position,rect:n.getBoundingClientRect().toJSON()})'),flush=True)
            box=page.locator('.nk-fsrs-settings-save').bounding_box()
            assert box and box['y']>=0 and box['y']+box['height']<768,box
            page.screenshot(path=str(OUT/'08a-fsrs-first-viewport.png'))
            page.evaluate("window.QB.nav('more')")
            page.get_by_role('button',name='Keep editing',exact=True).click()
            assert page.locator('.nk-fsrs-settings input').first.input_value()==value
            page.go_back();page.wait_for_timeout(100)
            page.get_by_role('button',name='Keep editing',exact=True).click()
            assert page.url.endswith('#fsrs-settings')
            page.get_by_role('button',name='Save changes',exact=True).click();page.wait_for_timeout(100)
            assert page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention") == int(value)/100
            page.reload(wait_until='networkidle')
            assert page.evaluate("window.QB.getState().fsrsPreferences.desiredRetention") == int(value)/100
            # Cancel discards drafts, Save persists across route changes and reload.
            page.locator('.nk-fsrs-settings input').first.fill('91')
            page.get_by_role('button',name='Cancel',exact=True).click();page.wait_for_timeout(100)
            assert page.url.endswith('#more')
            page.locator('.nk-fsrs-settings-entry').click();page.wait_for_timeout(100)
            assert page.locator('.nk-fsrs-settings input').first.input_value()==value
            page.set_viewport_size({'width':1024,'height':768})
            page.screenshot(path=str(OUT/'08b-fsrs-tablet.png'))
            page.evaluate("window.QB.nav('topics')");page.wait_for_timeout(100)
            page.screenshot(path=str(OUT/'07c-topics-tablet.png'))
            page.set_viewport_size({'width':390,'height':844})
            # Exercise authoritative source PDFs in real question explanations.
            for subject in ('Biochemistry','Physiology','Anatomy'):
                page.evaluate('(subject)=>window.QB.nav(\'banks\',subject)',subject);page.wait_for_timeout(100)
                page.locator('button.nk-bank-card').filter(has_text='PrepLadder').click();page.wait_for_timeout(100)
                page.locator('button.nk-topic-row').first.click();page.wait_for_timeout(100)
                page.locator('button.nk-library-row').first.click();page.wait_for_timeout(100)
                page.locator('.option-list button').first.click();page.wait_for_timeout(100)
                print('PDF_CHECK',subject,flush=True)
                segment=page.locator('.nk-web-pdf-segment').first
                segment.scroll_into_view_if_needed()
                page.wait_for_function("['true','error'].includes(document.querySelector('.nk-web-pdf-segment')?.dataset.rendered)",timeout=90000)
                assert segment.get_attribute('data-rendered')=='true',segment.inner_text()
                metrics=segment.evaluate('(n)=>({width:n.clientWidth,pixels:n.querySelector(\'canvas\').width,height:n.querySelector(\'canvas\').height})')
                assert metrics['pixels']>=metrics['width']*1.95,metrics
                segment.screenshot(path=str(OUT/f'09-{subject}-pdf-inline.png'))
                segment.click()
                zoom=page.locator('.source-pdf-zoomimg')
                zoom.wait_for(state='visible',timeout=90000)
                page.wait_for_function("document.querySelector('.source-pdf-zoomimg')?.naturalWidth>0")
                assert zoom.evaluate('(n)=>n.naturalWidth')>metrics['pixels']
                page.locator('#spz-plus').click();page.locator('#spz-plus').click()
                page.screenshot(path=str(OUT/f'10-{subject}-pdf-zoom.png'))
                page.locator('#spz-close').click()
                page.set_viewport_size({'width':1024,'height':768})
                page.wait_for_timeout(1500)
                page.wait_for_function("['true','error'].includes(document.querySelector('.nk-web-pdf-segment')?.dataset.rendered)",timeout=90000)
                assert segment.get_attribute('data-rendered')=='true',segment.inner_text()
                assert segment.evaluate('(n)=>n.querySelector(\'canvas\').width')>metrics['pixels']
                segment.screenshot(path=str(OUT/f'11-{subject}-pdf-tablet.png'))
                page.set_viewport_size({'width':390,'height':844})
            if errors: raise SystemExit('Browser errors: '+repr(errors))
            browser.close()
        server.shutdown()
    print('MARROW_BROWSER_OK registry=subject-indexed anatomy=819/48 biochemistry=543/26 physiology=753/33 total=2115 anatomy_phys_reference=142 biochemistry=52 enhanced=194 rationales=582 phys_q2=clean biochem_q23=gold phys_table=preserved anatomy_table=preserved fsrs_dock=fixed')
if __name__=='__main__':main()
