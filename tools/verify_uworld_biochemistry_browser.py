#!/usr/bin/env python3
"""Exercise the source-native UWorld pilot through the shared learner UI."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import hashlib
import json
import threading
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect
from uworld_poisoning_browser_cases import verify_poisoning
from uworld_ophthalmology_browser_cases import verify_ophthalmology
from uworld_imported_browser_cases import verify_imported_collections

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''window.__uworldTest={wrong:()=>nkRevisionDeskData().wrong.map(q=>q.id),questions:()=>nkAllStudyQuestions(),current:()=>nkCurrentQuestion(),presentation:id=>nkQuestionPresentationFor(BY_ID[id]),records:()=>Object.values(BANKS_BY_SUBJECT).flat().map(r=>({subject:r.subject,bank:r.bank,questions:r.questions.length,topics:(r.topics||r.chapters||[]).length}))};\n'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',help='Verify the actual hosted preview and its source media')
    args=parser.parse_args()
    web = ROOT / 'build/web'
    html = urlopen(args.url.rstrip('/')+'/index.html').read().decode() if args.url else (web / 'index.html').read_text()
    html_hash=hashlib.sha256(html.encode()).hexdigest()
    assert 'NK_UWORLD_BIOCHEMISTRY_V1_START' in html
    anchor = '  window.QB={'
    assert html.count(anchor) == 1
    diagnostic = html.replace(anchor, PROBE + anchor, 1).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?', 1)[0] in ('/', '/index.html'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                try:
                    self.wfile.write(diagnostic)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                super().do_GET()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = args.url.rstrip('/') if args.url else f'http://127.0.0.1:{server.server_port}'
    output = ROOT / 'build/uworld-biochemistry-checks'
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height in [(390, 844), (820, 1180), (1194, 900), (1440, 1000)]:
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block', has_touch=width<=820, is_mobile=width<=820)
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.route('**/*', lambda r: r.continue_() if r.request.url.startswith(origin) else r.abort())
                if args.url:
                    page.route(origin+'/',lambda r:r.fulfill(status=200,content_type='text/html',body=diagnostic))
                    page.route(origin+'/index.html',lambda r:r.fulfill(status=200,content_type='text/html',body=diagnostic))
                page.goto(origin, wait_until='domcontentloaded')
                page.wait_for_function('window.QB && window.__uworldTest')
                records = page.evaluate('__uworldTest.records()')
                expected = {('Anatomy', 'PrepLadder'): 1068, ('Physiology', 'PrepLadder'): 899, ('Biochemistry', 'PrepLadder'): 719,
                            ('Anatomy', 'Marrow'): 1115, ('Physiology', 'Marrow'): 1014, ('Biochemistry', 'Marrow'): 582,
                            ('UWorld · Biochemistry', 'UWorld'): 132,
                            ('UWorld · Poisoning & Environmental Exposure', 'UWorld'): 33,
                            ('UWorld · Ophthalmology', 'UWorld'): 30,
                            ('UWorld · Male Reproductive System', 'UWorld'): 52,
                            ('UWorld · Female Reproductive System & Breast', 'UWorld'): 81,
                            ('UWorld · Biostatistics & Epidemiology', 'UWorld'): 60}
                assert {(r['subject'], r['bank']): r['questions'] for r in records} == expected, records
                qs = page.evaluate('__uworldTest.questions().filter(q=>q.bank==="UWorld"&&q.collection==="Biochemistry")')
                assert len(qs) == len({q['id'] for q in qs}) == 132
                assert all(q['subject'] == 'UWorld · Biochemistry' for q in qs)
                eligible=page.evaluate('__uworldTest.questions().filter(q=>q.bank==="UWorld"&&q.collection==="Biochemistry"&&__uworldTest.presentation(q.id).valid).length')
                assert eligible==131, 'Only the known absent-exhibit question should remain unscored'

                def reset_practice():
                    page.evaluate('''() => {const s=QB.getState();s.activeSession=null;s.normalPracticeCheckpoints=[];s.normalPracticeCheckpoint=null;QB.saveState();}''')

                def open_question(qid):
                    reset_practice()
                    page.evaluate('id=>QB.practiceOne(id)', qid)
                    page.wait_for_function('id=>QB.getState().activeSession?.questionIds[QB.getState().activeSession.index]===id', arg=qid)
                    page.evaluate('QB.nav("practice")')
                    page.locator('.option-list button').first.wait_for()

                # Incumbent subjects remain separate from UWorld collections.
                expect(page.locator('.nk-home-subjects button.nk-v3-subject-card')).to_have_count(3)
                page.locator('.nk-home-subjects button.nk-v3-subject-card').filter(has_text='Biochemistry').click()
                expect(page.locator('button.nk-bank-card')).to_have_count(2)
                assert page.locator('button.nk-bank-card').filter(has_text='UWorld').count()==0
                page.evaluate('QB.nav("dashboard")')
                entry = page.locator('.nk-home-uworld').get_by_role('button',name='Open My UWorld',exact=True)
                expect(entry).to_have_count(1)
                expect(page.locator('.nk-home-uworld .nk-uworld-collection')).to_have_count(0)
                assert '6 collections · 388 questions' in entry.inner_text()
                assert entry.bounding_box()['height'] >= 44
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                page.screenshot(path=str(output / f'home-my-uworld-{width}.png'),full_page=True)
                entry.focus()
                expect(entry).to_be_focused()
                entry.press('Enter')
                expect(page.locator('.nk-uworld-library h1')).to_have_text('My UWorld')
                assert page.locator('.nk-uworld-library-note').count()==0
                assert "UWorld's original collections" not in page.locator('.nk-uworld-library').inner_text()
                page.screenshot(path=str(output / f'uworld-collections-{width}.png'))
                expect(page.locator('.nk-uworld-collection')).to_have_count(6)
                page.locator('.nk-uworld-collection').filter(has_text='Biochemistry').click()
                expect(page.locator('button.nk-topic-row')).to_have_count(4)
                assert page.locator('.nk-topic-group>h2').all_inner_texts()==['Blocks']
                page.locator('button.nk-topic-row').first.click()
                expect(page.locator('.nk-chapter-v114 .nk-back-link')).to_have_text('Blocks')
                page.locator('button.nk-library-row').first.click()
                page.locator('.option-list button').first.wait_for()
                first = page.evaluate('__uworldTest.current()')
                assert first['bank'] == 'UWorld'
                page.screenshot(path=str(output / f'question-before-answer-{width}.png'))
                assert page.locator('.nk-uworld-explanation,.nk-uworld-option-percent,.nk-uworld-cohort').count() == 0, 'Practice leaked feedback before answer'
                page.evaluate('window.__uworldStem=document.querySelector(".question-text")')
                option_widths=page.locator('.option-list .option-text').evaluate_all('nodes=>nodes.map(n=>n.getBoundingClientRect().width)')
                page.locator('.option-list button').nth(int(first['correctOption']) - 1).click()
                assert page.evaluate('QB.getState().activeSession.answers[__uworldTest.current().id]===__uworldTest.current().correctOption')
                assert page.evaluate('QB.getState().activeSession.submitted[__uworldTest.current().id]===true')
                assert page.evaluate('__uworldStem.isConnected'), 'Answer replaced the visible question'
                assert page.locator('.option-list .correct').count() == 1
                page.screenshot(path=str(output / f'immediate-answer-stats-{width}.png'))
                explanation = page.locator('.nk-uworld-explanation')
                explanation.wait_for()
                assert not any(x in explanation.inner_text().lower() for x in ('key takeaway', 'why the other options are wrong', 'structured text'))
                reading=explanation.locator('.nk-uworld-reading')
                assert reading.locator('img').count()==0
                typography=reading.evaluate('n=>({size:parseFloat(getComputedStyle(n).fontSize),line:parseFloat(getComputedStyle(n).lineHeight),width:n.getBoundingClientRect().width})')
                assert typography['size']>=16 and typography['line']/typography['size']>=1.6
                assert reading.locator(':scope > p').count()>=4
                expect(reading.locator('.nk-uworld-choice-discussion')).to_have_count(4)
                assert 'Caspases' in reading.inner_text()
                expect(page.locator('.option-list .nk-uworld-option-percent')).to_have_count(5)
                assert page.locator('.option-list .correct .nk-uworld-option-percent').inner_text()=='78%'
                assert page.locator('.option-list .nk-uworld-option-percent').first.inner_text()=='6%'
                assert '78% answered correctly' in page.locator('.nk-uworld-cohort').inner_text()
                assert page.locator('.nk-uworld-statistics').count()==0
                after_widths=page.locator('.option-list .option-text').evaluate_all('nodes=>nodes.map(n=>n.getBoundingClientRect().width)')
                assert all(abs(a-b)<2 for a,b in zip(option_widths,after_widths)), 'Percentages rewrapped option text'
                assert page.locator('.option-list .nk-uworld-option-percent').evaluate_all('nodes=>nodes.every(n=>n.getBoundingClientRect().left>=n.previousElementSibling.getBoundingClientRect().right-1 && n.getBoundingClientRect().right<=n.parentElement.getBoundingClientRect().right)'), 'Percentages are not in the option right column'
                assert not reading.locator('.nk-uworld-original').get_attribute('open')
                explanation.scroll_into_view_if_needed()
                page.screenshot(path=str(output / f'ocr-explanation-{width}.png'))
                reading.locator('.nk-uworld-choices h3').scroll_into_view_if_needed()
                page.screenshot(path=str(output / f'choice-discussions-{width}.png'))
                page.locator('.nk-fsrs-rating').get_by_role('button', name='Good', exact=True).click()
                assert page.evaluate('(id)=>!!QB.getState().reviews[id]', first['id']), 'Rated UWorld answer did not enter shared FSRS'
                page.evaluate('(id)=>QB.toggleBookmark(id)', first['id'])
                assert page.evaluate('(id)=>!!QB.getState().bookmarks[id]', first['id'])

                # Diagram-dependent records open as unscored references, with
                # explanations behind a deliberate disclosure and no session mutation.
                for qid in ('uw2024_biochem_1244',):
                    before=page.evaluate('JSON.stringify(QB.getState())')
                    page.evaluate('id=>QB.practiceOne(id)',qid)
                    reference=page.locator('.nk-uworld-reference')
                    expect(reference).to_be_visible()
                    assert reference.locator('.option-list').count()==0
                    assert not reference.locator('.nk-uworld-reference-explanation').get_attribute('open')
                    reference.get_by_text('Read explanation',exact=True).click()
                    expect(reference.locator('.nk-uworld-reading')).to_be_visible()
                    assert page.evaluate('JSON.stringify(QB.getState())')==before
                    if qid=='uw2024_biochem_1244':page.screenshot(path=str(output/f'diagram-reference-{width}.png'))
                    reference.get_by_role('button',name='Close',exact=True).click()
                    expect(reference).to_have_count(0)
                # Recovered diagram questions and diagram options use native study engines.
                for qid in ('uw2024_biochem_1036','uw2024_biochem_11914','uw2024_biochem_8328','uw2024_biochem_12263'):
                    open_question(qid)
                    expect(page.locator('img[data-uworld-essential="true"]').first).to_be_visible()
                    page.wait_for_function('() => [...document.querySelectorAll(\'img[data-uworld-essential="true"]\')].every(i=>i.complete&&i.naturalWidth>0)')
                    assert page.locator('.nk-uworld-explanation,.nk-uworld-objective,.nk-uworld-statistics').count()==0
                    assert not page.locator('.option-list button').first.is_disabled()
                    if qid=='uw2024_biochem_11914':
                        expect(page.locator('.nk-uworld-option-figure img')).to_have_count(5)
                        assert not any('autosomal' in t.lower() or 'dominant' in t.lower() for t in page.locator('.option-list button').all_inner_texts())
                    if qid=='uw2024_biochem_12263':
                        stem=page.locator('.nk-uworld-stem').inner_text()
                        assert 'β-globin' in stem and 't,..._cAA' not in stem
                        assert 'The base sequence indicated' in stem
                    page.screenshot(path=str(output/f'recovered-diagram-{qid}-{width}.png'))
                    q=page.evaluate('__uworldTest.current()')
                    page.locator('.option-list button').nth(q['correctOption']-1).click()
                    assert page.evaluate('QB.getState().activeSession.submitted[__uworldTest.current().id]===true')
                    page.wait_for_function("() => [...document.querySelectorAll('.nk-uworld-reading img')].every(i=>i.complete&&i.naturalWidth>0)")
                    if qid=='uw2024_biochem_12263':
                        explanation=page.locator('.nk-uworld-explanation').inner_text()
                        assert 'β-globin chain production' in explanation and '13-globin' not in explanation
                    page.screenshot(path=str(output/f'recovered-explanation-{qid}-{width}.png'))
                    if page.locator('.nk-uworld-figure button').count():
                        page.locator('.nk-uworld-figure button').first.click()
                        expect(page.locator('#nk-source-viewer .nk-sv-panel')).to_be_visible()
                        page.locator('#nk-source-viewer .nk-sv-close').click()
                # Actual scientific tables retain cell relationships and local overflow.
                open_question('uw2024_biochem_supp_1382')
                table=page.locator('.nk-uworld-stem table')
                expect(table.locator('tbody tr')).to_have_count(4)
                assert '+125 mV' in table.locator('tbody tr').last.inner_text()
                table.scroll_into_view_if_needed()
                page.screenshot(path=str(output/f'stem-table-{width}.png'))
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert page.locator('.nk-uworld-explanation').count()==0
                open_question('uw2024_biochem_2044')
                q=page.evaluate('__uworldTest.current()')
                page.locator('.option-list button').nth(q['correctOption']-1).click()
                table=page.locator('.nk-uworld-reading table')
                expect(table.locator('tbody tr')).to_have_count(4)
                assert table.locator('tbody tr').nth(2).locator('td').all_inner_texts()==['Protein','Antibody']
                table.scroll_into_view_if_needed()
                page.screenshot(path=str(output/f'explanation-table-{width}.png'))
                assert '[object Object]' not in table.inner_text()
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                # Missing required media fails closed without modifying saved answers.
                reset_practice()
                page.route('**/source_visuals/uworld/*.png*',lambda route:route.abort())
                open_question('uw2024_biochem_8328')
                # Force a real network request even when this exhibit was decoded earlier.
                page.locator('img[data-uworld-essential="true"]').evaluate_all('nodes=>nodes.forEach(n=>n.src=n.src.split("?")[0]+"?network-failure-check")')
                page.wait_for_function("document.querySelector('.nk-uworld-media-status')?.innerText.includes('could not load')")
                assert page.locator('.option-list button').first.is_disabled()
                before=page.evaluate('JSON.stringify(QB.getState())')
                page.evaluate('(q)=>QB.selectPractice(q.id,q.correctOption,QB.getState().activeSession.id)',page.evaluate('__uworldTest.current()'))
                assert page.evaluate('JSON.stringify(QB.getState())')==before
                page.unroute('**/source_visuals/uworld/*.png*')
                page.get_by_role('button',name='Retry figures',exact=True).click()
                page.wait_for_function('() => [...document.querySelectorAll(\'img[data-uworld-essential="true"]\')].every(i=>i.complete&&i.naturalWidth>0)')
                assert not page.locator('.option-list button').first.is_disabled()
                # Timed CBT uses the common builder and withholds every explanation.
                reset_practice()
                page.evaluate('QB.nav("tests")')
                page.get_by_role('button', name='Choose subjects and topics').click()
                page.get_by_role('button', name='Clear all', exact=True).click()
                page.locator('.nk-cbt-builder .nk-module-subject').filter(has_text='Biochemistry').filter(has_text='UWorld').click()
                page.get_by_role('button', name='Continue to topics', exact=True).click()
                expect(page.locator('.nk-cbt-topic-group')).to_have_count(1)
                expect(page.locator('.nk-cbt-topic')).to_have_count(4)
                assert str(eligible)+' questions' in page.locator('#nk-cbt-footer-count').inner_text()
                page.get_by_role('button', name='Continue to questions', exact=True).click()
                page.locator('#nk-cbt-custom-count').fill('10')
                page.get_by_role('button', name='Start timed CBT', exact=True).click()
                page.wait_for_function('QB.getState().activeSession?.mode==="exam"')
                exam = page.evaluate('QB.getState().activeSession')
                assert all(page.evaluate('id=>__uworldTest.presentation(id).valid',qid) for qid in exam['questionIds'])
                assert len(exam['questionIds']) == 10 and all(qid.startswith('uw2024_biochem_') for qid in exam['questionIds'])
                assert 'UWorld' in exam['title'] and 'Biochemistry' in exam['title']
                examq = page.evaluate('__uworldTest.current()')
                page.locator('.option-list button').nth(int(examq['correctOption']) - 1).click()
                assert page.locator('.option-list .correct,.option-list .wrong').count() == 0
                assert page.locator('.nk-uworld-explanation,.nk-uworld-option-percent,.nk-uworld-cohort').count() == 0
                page.evaluate('QB.openSessionReview()')
                page.locator('#nk-session-review').get_by_role('button', name='Submit Test', exact=True).click()
                page.locator('[data-v102-review-cta]').wait_for()
                result = page.evaluate('QB.getState().tests.at(-1)')
                assert result['questionIds'] == exam['questionIds'] and result['correct'] == 1 and result['total'] == 10
                page.locator('[data-v102-review-cta]').click()
                page.wait_for_function('QB.getState().activeSession?.mode==="review"')
                assert page.evaluate('QB.getState().activeSession.questionIds') == exam['questionIds']
                page.locator('.nk-uworld-explanation').wait_for()
                page.get_by_role('button', name='Next', exact=True).click()
                assert page.evaluate('__uworldTest.current().id') == exam['questionIds'][1]
                page.get_by_role('button', name='Previous', exact=True).click()
                assert page.evaluate('__uworldTest.current().id') == exam['questionIds'][0]
                page.screenshot(path=str(output / f'review-solutions-{width}.png'))
                page.evaluate('QB.endReview()')
                assert page.evaluate('QB.getState().tests.at(-1).id') == result['id']

                # Frozen custom modules select this source without a separate engine.
                reset_practice()
                page.evaluate('QB.openStudyModuleBuilder()')
                # Modules deliberately keep at least one bank selected. Add
                # UWorld first, then deselect any other default scope.
                uworld = page.locator('.nk-module-subject').filter(has_text='Biochemistry').filter(has_text='UWorld')
                if 'is-selected' not in (uworld.get_attribute('class') or ''):
                    uworld.click()
                others = page.locator('.nk-module-subject.is-selected').filter(has_not_text='UWorld')
                for _ in range(6):
                    if not others.count():
                        break
                    others.first.click()
                assert page.locator('.nk-module-subject.is-selected').count() == 1
                page.get_by_role('button', name='Continue', exact=True).click()
                page.get_by_role('button', name='Select all', exact=True).click()
                expect(page.locator('.nk-module-topic')).to_have_count(4)
                page.get_by_role('button', name='Continue to questions', exact=True).click()
                page.locator('.nk-module-count-presets button').filter(has_text='10').click()
                page.get_by_role('button', name='Continue', exact=True).click()
                page.locator('.nk-module-name input').fill('UWorld pilot module')
                page.get_by_role('button', name='Start now', exact=True).click()
                page.locator('.option-list button').first.wait_for()
                module = page.evaluate('QB.getState().studyModules.at(-1)')
                assert all(page.evaluate('id=>__uworldTest.presentation(id).valid',qid) for qid in module['questionIds'])
                assert len(module['questionIds']) == 10 and all(qid.startswith('uw2024_biochem_') for qid in module['questionIds'])
                assert page.evaluate('QB.getState().activeSession.studyModuleId') == module['id']
                assert page.evaluate('__uworldTest.current().bank') == 'UWorld'
                page.screenshot(path=str(output / f'module-practice-{width}.png'))
                page.evaluate('QB.exitStudyModule()')
                page.locator('.nk-home-subjects button.nk-v3-subject-card').filter(has_text='Biochemistry').click()
                page.locator('button.nk-bank-card').filter(has_text='PrepLadder').click()
                expect(page.locator('button.nk-topic-row')).to_have_count(28)
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                if width<=820:
                    # Execute a real scheduled-review failure; it changes FSRS only.
                    page.evaluate("id=>{const s=QB.getState(),history=s.attempts[id];s.activeSession=null;s.attempts={[id]:history.filter(a=>a.correct===true)};s.reviews={[id]:{...s.reviews[id],nextReviewAt:Date.now()-1000,due:Date.now()-1000}};s.fsrsReviewEligible={};QB.saveState();QB.nav('quick-revision');}",first['id'])
                    assert page.evaluate('__uworldTest.wrong().length')==0
                    before_review=page.evaluate('(id)=>QB.getState().reviews[id].repetitions',first['id'])
                    page.get_by_role('button',name='Review due',exact=True).click()
                    page.locator('.option-list button').first.wait_for()
                    due_q=page.evaluate('__uworldTest.current()')
                    page.locator('.option-list button').nth(due_q['correctOption']%len(due_q['options'])).click()
                    assert page.evaluate('(id)=>QB.getState().attempts[id].at(-1).source',first['id'])=='fsrs-review'
                    assert page.evaluate('(id)=>QB.getState().reviews[id].repetitions',first['id'])==before_review+1
                    assert page.evaluate('__uworldTest.wrong().length')==0,'FSRS-only lapse entered Practice mistakes'
                    page.evaluate('QB.nkFinishRevisionSession()')
                    assert page.evaluate('__uworldTest.wrong().length')==0
                poisoning = verify_poisoning(page, output, width, reset_practice, open_question)
                ophthalmology = verify_ophthalmology(page, output, width, reset_practice, open_question)
                imported = verify_imported_collections(page, output, width, reset_practice, open_question)
                assert not errors, errors
                reports.append({'width': width, 'origin':origin,'html_sha256':html_hash,'registry': True, 'source_reviewed_reading': True, 'readable_typography': typography,
                                'diagram_reference_unscored': True, 'eligible_questions':eligible, 'immediate_answer': True, 'shared_fsrs': True,
                                'cbt_deferred_feedback': True, 'review_solutions': True, 'frozen_module': True, 'prepladder_preserved': True, 'poisoning': poisoning, 'ophthalmology': ophthalmology, 'imported': imported})
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (output / 'report.json').write_text(json.dumps(reports, indent=2))
    print('UWORLD_BIOCHEMISTRY_BROWSER_OK', json.dumps(reports))


if __name__ == '__main__':
    main()
