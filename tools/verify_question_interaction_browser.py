#!/usr/bin/env python3
"""BC4 generated-app interaction matrix; no question data is modified."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/ui-checks'


def snapshot(page):
    return page.evaluate('JSON.stringify(window.QB.getState())')


def session(page):
    return page.evaluate('window.QB.getState().activeSession')


def settle(page):
    page.wait_for_function("document.querySelector('.nk-session-count')?.innerText.trim().startsWith(String(window.QB.getState().activeSession.index+1))")
    page.wait_for_function("""() => {
      const s=window.QB.getState().activeSession;
      return s.mode!=='practice'||Array.from(document.querySelectorAll('.option-list [onclick]')).some(el=>el.getAttribute('onclick').includes("'"+s.questionIds[s.index]+"'"));
    }""")


def fail_storage(page, enabled):
    page.evaluate('''enabled => {
      if(enabled)window.__NK_STORAGE_ADAPTER={getItem:k=>localStorage.getItem(k),removeItem:k=>localStorage.removeItem(k),setItem:()=>{throw new Error('BC4 quota injection')}};
      else delete window.__NK_STORAGE_ADAPTER;
    }''', enabled)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    web = ROOT / 'build/web'
    assert 'NK_QUESTION_INTERACTION_INTEGRITY_V1_START' in (web / 'index.html').read_text()
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    reports = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height in ((390, 844), (820, 1180)):
                context = browser.new_context(viewport={'width': width, 'height': height}, is_mobile=True, has_touch=True, service_workers='block')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + '/#dashboard', wait_until='domcontentloaded')
                page.wait_for_function('window.QB && window.QB.getState')
                page.evaluate('window.QB.startAllPractice()')
                page.wait_for_function('window.QB.getState().activeSession?.questionIds.length>5')
                settle(page)
                original = session(page)
                ids = original['questionIds']
                def answer(number, wrong=False):
                    page.evaluate('i=>window.QB.goIndex(i)', number)
                    settle(page)
                    correct = page.evaluate('''id=>[...(window.QBANK_DATA?.questions||[]),...(window.SUBJECT_QBANK_DATA?.subjects||[]).flatMap(s=>s.questions||[])].find(q=>q.id===id).correctOption''', ids[number])
                    choice = correct % 4 + 1 if wrong else correct
                    page.locator('.option-list button').nth(choice - 1).click()
                    page.wait_for_function('id=>window.QB.getState().activeSession.submitted[id]', arg=ids[number])
                    assert page.locator('.option-list .correct').count() == 1
                    assert page.locator('.option-list .wrong').count() == int(wrong)
                    assert page.locator('.option-list button').count() == 0
                    return choice

                # Real quota failure: state and visual selection must stay untouched.
                before = snapshot(page)
                fail_storage(page, True)
                page.locator('.option-list button').nth(1).click()
                assert snapshot(page) == before, 'failed answer mutated state'
                assert page.locator('.option-list button').count() == 4
                assert page.locator('#nk-storage-error').is_visible()
                fail_storage(page, False)
                answer(0, wrong=True)
                answer(1)
                submitted = session(page)
                page.evaluate('id=>{window.QB.selectPractice(id,4);window.QB.submitPractice();window.QB.submitPractice();}', ids[1])
                assert session(page)['answers'] == submitted['answers'], 'submitted answer changed'
                # Stale callback from q1 while q2 is current must do nothing.
                before = snapshot(page)
                page.evaluate('id=>window.QB.selectPractice(id,3)', ids[2])
                assert snapshot(page) == before
                # Failed navigation must retain pending Good and current position.
                fail_storage(page, True)
                before = snapshot(page)
                page.get_by_role('button', name='Next', exact=True).click()
                assert snapshot(page) == before
                fail_storage(page, False)
                page.get_by_role('button', name='Next', exact=True).dblclick()
                settle(page)
                assert session(page)['index'] == 2, 'double Next skipped a question'
                page.get_by_role('button', name='Previous', exact=True).dblclick()
                settle(page)
                assert session(page)['index'] == 1, 'double Previous skipped a question'
                assert page.locator('.option-list .correct').count() == 1
                page.evaluate('id=>window.QB.toggleBookmark(id)', ids[1])
                page.evaluate('id=>window.QB.toggleBookmark(id)', ids[1])
                assert not page.evaluate('id=>Boolean(window.QB.getState().bookmarks[id])', ids[1])
                page.evaluate('id=>window.QB.toggleBookmark(id)', ids[1])

                # Pause each supported state; selected-unsubmitted is an older
                # saved-state fixture because current Practice is tap-to-submit.
                for position, selected in ((2, False), (3, True), (1, False), (0, False)):
                    page.evaluate('i=>window.QB.goIndex(i)', position)
                    settle(page)
                    if selected:
                        page.evaluate('''id=>{const s=window.QB.getState().activeSession;s.answers[id]=2;s.submitted[id]=false;window.QB.saveState();}''', ids[position])
                    page.evaluate('window.QB.openSessionReview()')
                    page.locator('#nk-session-review').get_by_role('button', name='Pause', exact=True).dblclick()
                    page.wait_for_url('**/#dashboard')
                    assert session(page)['lifecycle'] == 'paused'
                    page.reload(wait_until='domcontentloaded')
                    page.locator('button.nk-home-focus-action').click()
                    page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")
                    settle(page)
                    assert session(page)['id'] == original['id']
                    assert session(page)['questionIds'] == ids
                    assert session(page)['index'] == position
                    if selected:
                        assert page.locator('.option-list .selected').count() == 1
                        assert page.locator('.option-list .correct,.option-list .wrong').count() == 0
                        assert page.evaluate('id=>(window.QB.getState().attempts[id]||[]).length', ids[position]) == 0, 'Pause submitted a pending selection'
                # Wrong/Bookmarks/FSRS must suspend and preserve normal Practice.
                saved = page.evaluate('window.QB.getState().normalPracticeCheckpoint')
                for mode in ('wrong', 'bookmarks'):
                    page.evaluate('kind=>window.QB.startLibrary(kind)', mode)
                    page.wait_for_function('id=>window.QB.getState().activeSession?.id!==id', arg=original['id'])
                    settle(page)
                    assert page.locator('#nk-practice-replacement').count() == 0
                    cp = page.evaluate('window.QB.getState().normalPracticeCheckpoint')
                    assert cp['sessionId'] == original['id'] and cp['answers'] == saved['answers']
                # Due skipped fixture, with no invented attempt, enters real FSRS.
                page.evaluate('''ids=>{const st=window.QB.getState();st.fsrsReviewEligible=st.fsrsReviewEligible||{};ids.forEach(id=>st.fsrsReviewEligible[id]={reason:'skipped',at:Date.now()});window.QB.saveState();window.QB.nkStartTodaysReview();}''', ids[4:7])
                page.wait_for_function("window.QB.getState().activeSession?.context==='spaced-review'")
                settle(page)
                assert page.evaluate('window.QB.getState().normalPracticeCheckpoint.sessionId') == original['id']
                fsrsid = session(page)['questionIds'][0]
                page.locator('.option-list button').first.click()
                page.evaluate('window.QB.nextQ()')
                assert page.evaluate('id=>window.QB.getState().attempts[id].at(-1).source', fsrsid) == 'fsrs-review'
                # End special session via its existing final review control.
                page.evaluate('window.QB.openSessionReview()')
                page.evaluate('window.QB.endSession()')
                page.wait_for_function('!window.QB.getState().activeSession')
                assert page.locator('#nk-session-review,#qb-question-navigator').count() == 0, 'completed special session left a blocking overlay'
                page.get_by_role('button', name='Review Solutions', exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='review'")
                review_before = page.evaluate('JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews,window.QB.getState().tests])')
                page.get_by_role('button', name='Next', exact=True).click()
                page.get_by_role('button', name='Previous', exact=True).click()
                page.locator('#cr-grid').click()
                page.locator('#qb-question-navigator').get_by_role('button', name='End Review', exact=True).click()
                assert page.evaluate('JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews,window.QB.getState().tests])') == review_before
                page.evaluate("window.QB.nav('dashboard')")
                page.locator('button.nk-home-focus-action').click()
                page.wait_for_function('id=>window.QB.getState().activeSession?.id===id', arg=original['id'])
                settle(page)
                # Browser/PWA Back must ask before leaving the live question.
                with page.expect_event('dialog') as warning:
                    page.evaluate('history.back()')
                assert 'Do you want to exit?' in warning.value.message
                warning.value.dismiss()
                page.wait_for_timeout(100)
                assert page.evaluate('location.hash') == '#practice'
                assert session(page)['id'] == original['id']
                page.evaluate("window.QB.nkOpenSubjectLibrary('Biochemistry')")
                page.wait_for_function("document.querySelectorAll('button.nk-bank-card').length===2")
                assert session(page)['id'] == original['id']
                page.evaluate("window.QB.nav('dashboard')")
                page.wait_for_url('**/#dashboard')
                page.locator('button.nk-home-focus-action').click()
                settle(page)
                with page.expect_event('dialog') as warning:
                    page.evaluate('history.back()')
                warning.value.accept()
                page.wait_for_url('**/#dashboard')
                assert page.locator('#nk-session-review,#qb-question-navigator').count() == 0
                page.locator('button.nk-home-focus-action').click()
                settle(page)
                page.screenshot(path=str(OUT / f'bc4-practice-{width}.png'), full_page=True)
                page.evaluate('window.QB.openSessionReview()')
                page.locator('#nk-session-review').get_by_role('button', name='Submit', exact=True).dblclick()
                page.wait_for_function('!window.QB.getState().activeSession')
                assert page.evaluate('id=>window.QB.getState().tests.filter(t=>t.id===`practice_${id}`).length', original['id']) == 1
                result = page.evaluate('id=>window.QB.getState().tests.find(t=>t.id===`practice_${id}`)', original['id'])
                assert result['attempted'] == 3 and result['unattempted'] == len(ids) - 3
                assert result['correct'] + result['incorrect'] == 3
                assert page.evaluate('id=>(window.QB.getState().attempts[id]||[]).length===1 && Boolean(window.QB.getState().reviews[id])', ids[3]), 'legacy selected answer counted without attempt/FSRS'
                assert page.evaluate('ids=>ids.every(id=>window.QB.getState().fsrsReviewEligible[id]?.reason==="skipped")', ids[5:])
                assert page.evaluate('id=>Boolean(window.QB.getState().bookmarks[id])', ids[1])
                # Actual CBT builder: changes remain private until final Submit.
                page.evaluate('window.QB.openSessionBuilder(null,"exam")')
                page.locator('#modal').get_by_role('button', name='Start Exam', exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                settle(page)
                cbt = session(page)
                cbt_qid = cbt['questionIds'][0]
                mark=page.locator('.nk-exam-review-toggle')
                mark.click()
                assert mark.get_attribute('aria-pressed') == 'true'
                assert session(page)['markedForReview'][cbt_qid] is True
                page.reload(wait_until='domcontentloaded')
                settle(page)
                assert page.locator('.nk-exam-review-toggle').get_attribute('aria-pressed') == 'true'
                page.evaluate('window.QB.openQuestionNavigator()')
                assert page.locator('#qb-question-navigator .qb-nav-q.is-marked').count() == 1
                assert page.locator('#qb-question-navigator').get_by_role('button', name='Abandon test').count() == 1
                assert page.locator('.nk-v114-session.is-exam').get_by_role('button', name='Abandon test').count() == 0
                abandon_messages = []
                page.once('dialog', lambda dialog: (abandon_messages.append(dialog.message), dialog.dismiss()))
                page.locator('#qb-question-navigator').get_by_role('button', name='Abandon test').click()
                assert abandon_messages and 'no test result will be saved' in abandon_messages[0]
                assert session(page)['id'] == cbt['id'], 'canceling Abandon must keep the timed test'
                page.evaluate('window.QB.closeQuestionNavigator()')
                page.evaluate('window.QB.openSessionReview()')
                assert page.locator('#nk-session-review .nk-session-review-q.is-marked').count() == 1
                assert page.locator('#nk-session-review').get_by_role('button', name='Abandon test').count() == 1
                page.evaluate('window.QB.__sessionReviewClose()')
                with page.expect_event('dialog') as warning:
                    page.evaluate('history.back()')
                assert 'timed test will keep running' in warning.value.message
                warning.value.dismiss()
                page.wait_for_timeout(100)
                assert page.evaluate('location.hash') == '#exam'
                assert session(page)['id'] == cbt['id']
                page.evaluate("window.QB.nav('dashboard')")
                page.wait_for_url('**/#dashboard')
                assert page.locator('.nk-timed-resume.is-home').is_visible()
                assert 'timer keeps running' in page.locator('.nk-timed-resume.is-home').inner_text()
                page.locator('.nk-timed-resume.is-home button').click()
                page.wait_for_url('**/#exam')
                assert session(page)['id'] == cbt['id']
                assert session(page)['markedForReview'][cbt_qid] is True
                page.evaluate("window.QB.nav('tests')")
                page.wait_for_url('**/#tests')
                assert page.locator('.nk-timed-resume.is-tests').is_visible()
                page.locator('.nk-timed-resume.is-tests button').click()
                page.wait_for_url('**/#exam')
                assert session(page)['id'] == cbt['id']
                page.evaluate("window.QB.nav('test-builder')")
                page.wait_for_url('**/#test-builder')
                assert page.locator('.nk-timed-resume.is-builder').is_visible()
                page.locator('.nk-timed-resume.is-builder button').click()
                page.wait_for_url('**/#exam')
                assert session(page)['id'] == cbt['id']
                page.evaluate('''() => {
                  const state=window.QB.getState(),id=state.activeSession.questionIds[0];
                  state.studyModules.push({id:'timed-module-guard',name:'Saved review set',questionIds:[id],createdAt:Date.now(),lastOpenedAt:Date.now()});
                  window.QB.startStudyModule('timed-module-guard');
                }''')
                conflict=page.locator('#nk-timed-session-conflict')
                assert conflict.is_visible()
                assert session(page)['id'] == cbt['id'], 'saved module replaced an unfinished CBT'
                conflict.get_by_role('button', name='Cancel', exact=True).click()
                assert session(page)['id'] == cbt['id']
                page.evaluate("window.QB.startStudyModule('timed-module-guard')")
                conflict.get_by_role('button', name='Resume test', exact=True).click()
                page.wait_for_url('**/#exam')
                assert session(page)['id'] == cbt['id']
                baseline = page.evaluate('JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews])')
                page.locator('.option-list button').nth(0).click()
                page.locator('.option-list button').nth(1).click()
                assert session(page)['answers'][cbt_qid] == 2
                assert page.locator('.option-list .selected').count() == 1
                assert page.locator('.option-list .correct,.option-list .wrong').count() == 0
                page.screenshot(path=str(OUT / f'bc4-cbt-selected-{width}.png'), full_page=True)
                assert page.evaluate('JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews])') == baseline
                page.get_by_role('button', name='Next', exact=True).click()
                page.get_by_role('button', name='Previous', exact=True).click()
                assert session(page)['answers'][cbt_qid] == 2
                page.evaluate('window.QB.openSessionReview()')
                page.locator('.nk-session-review-q').nth(2).click()
                settle(page)
                assert session(page)['index'] == 2
                page.evaluate('window.QB.openSessionReview()')
                before = snapshot(page)
                fail_storage(page, True)
                page.locator('#nk-session-review').get_by_role('button', name='Submit Test', exact=True).click()
                assert snapshot(page) == before
                assert page.locator('#nk-session-review').is_visible()
                fail_storage(page, False)
                page.locator('#nk-session-review').get_by_role('button', name='Submit Test', exact=True).dblclick()
                page.wait_for_function('!window.QB.getState().activeSession')
                assert page.evaluate('id=>window.QB.getState().tests.filter(t=>t.id===`exam_${id}`).length', cbt['id']) == 1
                assert page.evaluate('id=>window.QB.getState().attempts[id].at(-1).source', cbt_qid) == 'exam'
                assert page.evaluate('id=>window.QB.getState().tests.find(t=>t.id===`exam_${id}`).markedForReview', cbt['id']) == {cbt_qid: True}
                assert page.get_by_role('button', name='Practise marked questions').count() == 1
                page.wait_for_timeout(950)
                page.get_by_role('button', name='Practise marked questions').click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='practice'")
                assert session(page)['questionIds'] == [cbt_qid]
                assert not errors, errors
                reports.append({'viewport': f'{width}x{height}', 'touch': True, 'practice': 'PASS', 'mode_isolation': 'PASS', 'back': 'PASS', 'durability': 'PASS'})
                context.close()
                abandon_context = browser.new_context(viewport={'width': width, 'height': height}, is_mobile=True, has_touch=True, service_workers='block')
                abandon_page = abandon_context.new_page()
                abandon_page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                abandon_page.goto(origin + '/#tests', wait_until='domcontentloaded')
                abandon_page.wait_for_function('window.QB?.getState')
                abandon_page.evaluate('window.QB.openSessionBuilder(null,"exam")')
                abandon_page.locator('#modal').get_by_role('button', name='Start Exam', exact=True).click()
                abandon_page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                abandon_page.evaluate('window.QB.openSessionReview()')
                abandon_page.once('dialog', lambda dialog: dialog.accept())
                abandon_page.locator('#nk-session-review').get_by_role('button', name='Abandon test').click()
                abandon_page.wait_for_function("!window.QB.getState().activeSession && location.hash==='#tests'")
                assert abandon_page.evaluate('window.QB.getState().tests.length') == 0, 'abandoned test created a result'
                assert abandon_page.evaluate('Object.values(window.QB.getState().attempts).flat().length') == 0, 'abandoned test recorded attempts'
                assert abandon_page.locator('.nk-timed-resume.is-tests').count() == 0, 'abandoned test remains resumable'
                abandon_context.close()
            browser.close()
    finally:
        server.shutdown()
    (OUT / 'bc4-interaction-report.json').write_text(json.dumps(reports, indent=2))
    print('QUESTION_INTERACTION_BROWSER_OK ' + json.dumps(reports))


if __name__ == '__main__':
    main()
