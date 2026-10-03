#!/usr/bin/env python3
"""Exercise the source-native UWorld pilot through the shared learner UI."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''window.__uworldTest={questions:()=>nkAllStudyQuestions(),current:()=>nkCurrentQuestion(),presentation:id=>nkQuestionPresentationFor(BY_ID[id]),records:()=>Object.values(BANKS_BY_SUBJECT).flat().map(r=>({subject:r.subject,bank:r.bank,questions:r.questions.length,topics:(r.topics||r.chapters||[]).length}))};\n'''


def main():
    web = ROOT / 'build/web'
    html = (web / 'index.html').read_text()
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
    origin = f'http://127.0.0.1:{server.server_port}'
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
                page.goto(origin, wait_until='domcontentloaded')
                page.wait_for_function('window.QB && window.__uworldTest')
                records = page.evaluate('__uworldTest.records()')
                expected = {('Anatomy', 'PrepLadder'): 1068, ('Physiology', 'PrepLadder'): 899, ('Biochemistry', 'PrepLadder'): 719,
                            ('Anatomy', 'Marrow'): 1115, ('Physiology', 'Marrow'): 1014, ('Biochemistry', 'Marrow'): 582,
                            ('Biochemistry', 'UWorld'): 132}
                assert {(r['subject'], r['bank']): r['questions'] for r in records} == expected, records
                qs = page.evaluate('__uworldTest.questions().filter(q=>q.bank==="UWorld")')
                assert len(qs) == len({q['id'] for q in qs}) == 132
                assert all(q['subject'] == 'Biochemistry' for q in qs)
                assert page.evaluate('__uworldTest.questions().filter(q=>q.bank==="UWorld"&&__uworldTest.presentation(q.id).valid).length') == 105

                def reset_practice():
                    page.evaluate('''() => {const s=QB.getState();s.activeSession=null;s.normalPracticeCheckpoints=[];s.normalPracticeCheckpoint=null;QB.saveState();}''')

                def open_question(qid):
                    reset_practice()
                    page.evaluate('id=>QB.practiceOne(id)', qid)
                    page.wait_for_function('id=>QB.getState().activeSession?.questionIds[QB.getState().activeSession.index]===id', arg=qid)
                    page.evaluate('QB.nav("practice")')
                    page.locator('.option-list button').first.wait_for()

                # Start with the actual subject -> source -> topic -> question journey.
                page.locator('button.nk-v3-subject-card').filter(has_text='Biochemistry').click()
                expect(page.locator('button.nk-bank-card')).to_have_count(3)
                for bank, count in [('PrepLadder', '719'), ('Marrow', '582'), ('UWorld', '132')]:
                    card = page.locator('button.nk-bank-card').filter(has_text=bank)
                    assert card.count() == 1 and count in card.inner_text()
                page.screenshot(path=str(output / f'bank-chooser-{width}.png'))
                page.locator('button.nk-bank-card').filter(has_text='UWorld').click()
                expect(page.locator('button.nk-topic-row')).to_have_count(4)
                page.locator('button.nk-topic-row').first.click()
                page.locator('button.nk-library-row').first.click()
                page.locator('.option-list button').first.wait_for()
                first = page.evaluate('__uworldTest.current()')
                assert first['bank'] == 'UWorld'
                page.screenshot(path=str(output / f'question-before-answer-{width}.png'))
                assert page.locator('.nk-uworld-explanation').count() == 0, 'Practice leaked explanation before answer'
                page.evaluate('window.__uworldStem=document.querySelector(".question-text")')
                page.locator('.option-list button').nth(int(first['correctOption']) - 1).click()
                assert page.evaluate('QB.getState().activeSession.answers[__uworldTest.current().id]===__uworldTest.current().correctOption')
                assert page.evaluate('QB.getState().activeSession.submitted[__uworldTest.current().id]===true')
                assert page.evaluate('__uworldStem.isConnected'), 'Answer replaced the visible question'
                assert page.locator('.option-list .correct').count() == 1
                explanation = page.locator('.nk-uworld-explanation')
                explanation.wait_for()
                assert not any(x in explanation.inner_text().lower() for x in ('key takeaway', 'why the other options are wrong', 'structured text'))
                reading=explanation.locator('.nk-uworld-reading')
                assert reading.locator('img').count()==0
                typography=reading.evaluate('n=>({size:parseFloat(getComputedStyle(n).fontSize),line:parseFloat(getComputedStyle(n).lineHeight),width:n.getBoundingClientRect().width})')
                assert typography['size']>=16 and typography['line']/typography['size']>=1.6
                assert reading.locator(':scope > p').count()>=8
                assert not reading.locator('.nk-uworld-original').get_attribute('open')
                explanation.scroll_into_view_if_needed()
                page.screenshot(path=str(output / f'ocr-explanation-{width}.png'))
                page.locator('.nk-fsrs-rating').get_by_role('button', name='Good', exact=True).click()
                assert page.evaluate('(id)=>!!QB.getState().reviews[id]', first['id']), 'Rated UWorld answer did not enter shared FSRS'
                page.evaluate('(id)=>QB.toggleBookmark(id)', first['id'])
                assert page.evaluate('(id)=>!!QB.getState().bookmarks[id]', first['id'])

                # Diagram-dependent records open as unscored references, with
                # explanations behind a deliberate disclosure and no session mutation.
                for qid in ('uw2024_biochem_1022','uw2024_biochem_11914','uw2024_biochem_1032','uw2024_biochem_1036','uw2024_biochem_1473'):
                    before=page.evaluate('JSON.stringify(QB.getState())')
                    page.evaluate('id=>QB.practiceOne(id)',qid)
                    reference=page.locator('.nk-uworld-reference')
                    expect(reference).to_be_visible()
                    assert reference.locator('.option-list').count()==0
                    assert not reference.locator('.nk-uworld-reference-explanation').get_attribute('open')
                    reference.get_by_text('Read explanation',exact=True).click()
                    expect(reference.locator('.nk-uworld-reading')).to_be_visible()
                    assert page.evaluate('JSON.stringify(QB.getState())')==before
                    if qid=='uw2024_biochem_11914':page.screenshot(path=str(output/f'diagram-reference-{width}.png'))
                    reference.get_by_role('button',name='Close',exact=True).click()
                    expect(reference).to_have_count(0)
                # Timed CBT uses the common builder and withholds every explanation.
                reset_practice()
                page.evaluate('QB.nav("tests")')
                page.get_by_role('button', name='Choose subjects and topics').click()
                page.get_by_role('button', name='Clear all', exact=True).click()
                page.locator('.nk-cbt-builder .nk-module-subject').filter(has_text='Biochemistry').filter(has_text='UWorld').click()
                page.get_by_role('button', name='Continue to topics', exact=True).click()
                expect(page.locator('.nk-cbt-topic-group')).to_have_count(1)
                expect(page.locator('.nk-cbt-topic')).to_have_count(4)
                assert '105 questions' in page.locator('#nk-cbt-footer-count').inner_text()
                page.get_by_role('button', name='Continue to questions', exact=True).click()
                page.locator('#nk-cbt-custom-count').fill('10')
                page.get_by_role('button', name='Start timed CBT', exact=True).click()
                page.wait_for_function('QB.getState().activeSession?.mode==="exam"')
                exam = page.evaluate('QB.getState().activeSession')
                assert all(page.evaluate('id=>__uworldTest.presentation(id).valid',qid) for qid in exam['questionIds'])
                assert len(exam['questionIds']) == 10 and all(qid.startswith('uw2024_biochem_') for qid in exam['questionIds'])
                assert exam['title'] == 'Biochemistry · UWorld CBT'
                examq = page.evaluate('__uworldTest.current()')
                page.locator('.option-list button').nth(int(examq['correctOption']) - 1).click()
                assert page.locator('.option-list .correct,.option-list .wrong').count() == 0
                assert page.locator('.nk-uworld-explanation').count() == 0
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
                page.locator('button.nk-v3-subject-card').filter(has_text='Biochemistry').click()
                page.locator('button.nk-bank-card').filter(has_text='PrepLadder').click()
                expect(page.locator('button.nk-topic-row')).to_have_count(28)
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert not errors, errors
                reports.append({'width': width, 'registry': True, 'native_ocr_reading': True, 'readable_typography': typography,
                                'diagram_reference_unscored': True, 'eligible_questions':105, 'immediate_answer': True, 'shared_fsrs': True,
                                'cbt_deferred_feedback': True, 'review_solutions': True, 'frozen_module': True, 'prepladder_preserved': True})
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (output / 'report.json').write_text(json.dumps(reports, indent=2))
    print('UWORLD_BIOCHEMISTRY_BROWSER_OK', json.dumps(reports))


if __name__ == '__main__':
    main()
