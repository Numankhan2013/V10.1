#!/usr/bin/env python3
"""Exercise source-labelled PYQ and mixed CBT journeys in the generated PWA."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    web = ROOT / 'build/web'
    assert 'NK_BANK_AWARE_CBT_BUILDER_V1_START' in (web / 'index.html').read_text(encoding='utf-8')
    output = ROOT / 'build/ui-checks'
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width, height in ((390, 844), (820, 1180)):
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + '/#tests', wait_until='domcontentloaded')
                page.wait_for_function('window.QB?.getState')

                def open_builder():
                    page.evaluate("window.QB.nav('tests')")
                    page.get_by_role('button', name='Choose subjects and topics').click()
                    page.wait_for_url('**/#test-builder')

                def choose_prep(subject):
                    page.get_by_role('button', name='Clear all').click()
                    page.locator('.nk-cbt-builder .nk-module-subject').filter(has_text=subject).filter(has_text='PrepLadder').click()
                    page.get_by_role('button', name='Continue to topics').click()

                for subject, topics, questions in (('Anatomy', 10, 410), ('Physiology', 9, 362), ('Biochemistry', 8, 346)):
                    open_builder()
                    choose_prep(subject)
                    toggle = page.locator('#nk-cbt-pyq-toggle')
                    tool_tops = page.locator('.nk-cbt-topic-tools button').evaluate_all('(nodes)=>nodes.map(node=>node.getBoundingClientRect().top)')
                    assert len(tool_tops) == 3 and max(tool_tops) - min(tool_tops) < 3, tool_tops
                    expect(toggle.locator('small')).to_have_text(f'{topics} topics · {questions} Q')
                    toggle.click()
                    expect(toggle).to_have_attribute('aria-pressed', 'true')
                    expect(page.locator('#nk-cbt-footer-count')).to_have_text(f'{topics} topics · {questions} questions')
                    toggle.click()
                    expect(toggle).to_have_attribute('aria-pressed', 'false')
                    expect(page.locator('#nk-cbt-footer-count')).to_have_text('0 topics · 0 questions')

                open_builder()
                page.get_by_role('button', name='Clear all').click()
                page.locator('.nk-cbt-builder .nk-module-subject').filter(has_text='Anatomy').filter(has_text='Marrow').click()
                page.get_by_role('button', name='Continue to topics').click()
                before_empty = page.locator('#nk-cbt-footer-count').inner_text()
                expect(page.locator('#nk-cbt-pyq-toggle')).to_be_disabled()
                expect(page.locator('#nk-cbt-footer-count')).to_have_text(before_empty)
                expect(page.locator('.nk-cbt-pyq-empty')).to_contain_text('Your draft is unchanged')

                open_builder()
                page.get_by_role('button', name='Continue to topics').click()
                expect(page.locator('#nk-cbt-pyq-toggle small')).to_have_text('27 topics · 1,118 Q')
                page.locator('#nk-cbt-pyq-toggle').click()
                expect(page.locator('#nk-cbt-pyq-toggle')).to_have_attribute('aria-pressed', 'true')
                expect(page.locator('#nk-cbt-footer-count')).to_have_text('27 topics · 1,118 questions')
                page.screenshot(path=str(output / f'pyq-topics-{width}.png'), full_page=True)
                page.get_by_role('button', name='Continue to questions').click()
                page.locator('#nk-cbt-custom-count').fill('2')
                page.get_by_role('button', name='Start timed CBT').click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                session = page.evaluate('window.QB.getState().activeSession')
                assert session['title'] == 'PYQ CBT' and len(session['questionIds']) == 2, session
                assert page.locator('.option-list .correct').count() == 0
                first = session['questionIds'][0]
                wrong = page.evaluate('''id=>{
                  const q=[...(window.QBANK_DATA?.questions||[]),...(window.SUBJECT_QBANK_DATA.subjects||[]).flatMap(r=>r.questions||[])].find(q=>String(q.id)===String(id));
                  return Number(q.correctOption)%4+1;
                }''', first)
                page.locator('.option-list button').nth(wrong - 1).click()
                assert page.evaluate('window.QB.getState().activeSession.answers',)[first] == wrong
                assert page.locator('.option-list .correct').count() == 0
                page.evaluate('window.QB.submitExam(false)')
                page.wait_for_function("location.hash.startsWith('#result') && !window.QB.getState().activeSession")
                test = page.evaluate('window.QB.getState().tests.at(-1)')
                assert test['title'] == 'PYQ CBT' and test['answers'][first] == wrong
                expect(page.get_by_role('heading', name='Topic breakdown')).to_be_visible()
                page.get_by_role('button', name='Review Solutions', exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='review'")
                page.locator('#cr-grid').click()
                page.locator('#qb-question-navigator').get_by_role('button', name='End Review', exact=True).click()
                expect(page.get_by_role('heading', name='Topic breakdown')).to_be_visible()
                page.evaluate("window.QB.nav('tests')")
                expect(page.locator('.nk-test-history')).to_contain_text('PYQ CBT')
                page.evaluate('id=>window.QB.nav(\'result\',id)', test['id'])
                page.get_by_role('button', name='Practise missed questions').click()
                page.wait_for_function("window.QB.getState().activeSession?.context==='cbt-followup'")
                followup = page.evaluate('window.QB.getState().activeSession')
                assert first in followup['questionIds']

                # A regular topic added after the PYQ action creates a mixed source set.
                page.evaluate("()=>{window.QB.endSession();window.QB.nav('tests');}")
                open_builder()
                choose_prep('Anatomy')
                page.locator('#nk-cbt-pyq-toggle').click()
                regular = page.locator('.nk-cbt-topic-group .nk-cbt-topic').filter(has_not_text='· PYQs').first
                regular.click()
                selected_count = int(page.locator('#nk-cbt-footer-count').inner_text().split(' topics')[0])
                assert selected_count == 11
                expect(page.locator('#nk-cbt-pyq-toggle')).to_have_attribute('aria-pressed', 'true')
                page.get_by_role('button', name='Continue to questions').click()
                pool = int(page.locator('.nk-cbt-summary > div').nth(1).locator('strong').inner_text().split()[0].replace(',', ''))
                page.locator('#nk-cbt-custom-count').fill(str(pool))
                page.get_by_role('button', name='Start timed CBT').click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                mixed = page.evaluate('window.QB.getState().activeSession')
                assert mixed['title'] != 'PYQ CBT' and len(mixed['questionIds']) == pool
                page.evaluate('window.QB.submitExam(false)')
                expect(page.get_by_role('heading', name='Topic breakdown')).to_be_visible()
                saved = page.evaluate('window.QB.getState().tests.at(-1)')
                assert saved['title'] != 'PYQ CBT' and saved['total'] == pool
                assert page.locator('.nk-cbt-analysis-row').count() >= 2
                page.screenshot(path=str(output / f'pyq-mixed-result-{width}.png'), full_page=True)

                for bank in ('PrepLadder', 'Marrow'):
                    topic = page.evaluate("""bank=>bank==='PrepLadder'
                      ?window.SUBJECT_QBANK_DATA.subjects.find(r=>r.subject==='Anatomy').topics[0].id:'1'""", bank)
                    page.evaluate('''({bank,topic})=>window.QB.nkOpenSubjectChapter('Anatomy',bank,topic)''', {'bank': bank, 'topic': topic})
                    page.wait_for_function("location.hash.startsWith('#chapter')")
                    page.evaluate('topic=>window.QB.nkStartTopicTimedTest(topic)', topic)
                    page.wait_for_function("window.QB.getState().activeSession?.timerMode==='per-question'")
                    strict = page.evaluate('window.QB.getState().activeSession')
                    assert len(strict['questionIds']) > 1
                    page.evaluate('''()=>{const s=window.QB.getState().activeSession;
                      s.strictQuestionStartedAt=Date.now()-61000;window.QB.saveState();}''')
                    page.reload(wait_until='domcontentloaded')
                    page.wait_for_function("window.QB.getState().activeSession?.index===1")
                    after_reload = page.evaluate('window.QB.getState().activeSession')
                    assert after_reload['strictExpired'][strict['questionIds'][0]] is True
                    assert page.locator('.option-list .correct').count() == 0
                    page.evaluate('''()=>{const s=window.QB.getState().activeSession;
                      s.index=s.questionIds.length-1;
                      for(const id of s.questionIds.slice(0,-1)){s.strictExpired[id]=true;s.strictQuestionTime[id]=60000;}
                      s.questionEnteredAt=Date.now()-61000;s.strictQuestionStartedAt=s.questionEnteredAt;
                      window.QB.saveState();}''')
                    page.reload(wait_until='domcontentloaded')
                    page.wait_for_function("!window.QB.getState().activeSession && location.hash.startsWith('#result')")
                    completed = page.evaluate('window.QB.getState().tests.at(-1)')
                    assert completed['timerMode'] == 'per-question' and completed['autoSubmitted'] is True
                assert not errors, errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print('PYQ_EXAM_JOURNEY_BROWSER_OK verified=1118/27 subsets=true pyq=true mixed=true history=true review=true followup=true phone_tablet=true')


if __name__ == '__main__':
    main()
