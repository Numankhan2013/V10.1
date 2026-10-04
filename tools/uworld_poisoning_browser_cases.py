"""Second-collection checks run inside the real four-width UWorld learner audit."""
from playwright.sync_api import expect


def verify_poisoning(page, output, width, reset_practice, open_question):
    collection = 'Poisoning & Environmental Exposure'
    page.evaluate('QB.nav("uworld")')
    page.locator('.nk-uworld-collection').filter(has_text=collection).click()
    expect(page.locator('button.nk-topic-row')).to_have_count(1)
    assert collection in page.locator('h1').first.inner_text()
    page.locator('button.nk-topic-row').click()
    expect(page.locator('button.nk-library-row')).to_have_count(33)
    reset_practice()
    page.locator('.nk-chapter-actions').get_by_role('button', name='Practice', exact=False).click()
    page.locator('#modal').get_by_role('button', name='Start Practice', exact=True).click()
    page.locator('.option-list button').first.wait_for()
    original = page.evaluate('QB.getState().activeSession')
    assert len(original['questionIds']) == 33
    for _ in range(2):
        q = page.evaluate('__uworldTest.current()')
        page.locator('.option-list button').nth(q['correctOption'] - 1).click()
        page.get_by_role('button', name='Next', exact=True).click()
    unanswered = page.evaluate('__uworldTest.current().id')
    before = page.evaluate('QB.getState().activeSession')
    page.evaluate('QB.openSessionReview()')
    page.locator('#nk-session-review').get_by_role('button', name='Pause', exact=True).click()
    page.wait_for_function('QB.getState().activeSession?.lifecycle==="paused"')
    page.locator('button.nk-home-focus-action').click()
    page.locator('.option-list button').first.wait_for()
    resumed = page.evaluate('QB.getState().activeSession')
    assert resumed['id'] == original['id'] and resumed['questionIds'] == original['questionIds']
    assert resumed['index'] == 2 and resumed['answers'] == before['answers']
    assert page.evaluate('__uworldTest.current().id') == unanswered
    assert not page.evaluate('id=>QB.getState().activeSession.submitted[id]', unanswered)
    reset_practice()
    page.evaluate('QB.openChapter("uworld_poisoning_block_1")')
    page.locator('button.nk-library-row').first.click()
    page.locator('.option-list button').first.wait_for()
    assert page.evaluate('__uworldTest.current().id') == 'UWORLD_16052'
    assert page.locator('.nk-uworld-option-percent,.nk-uworld-objective').count() == 0
    page.locator('.option-list button').nth(4).click()
    expect(page.locator('.option-list .correct .nk-uworld-option-percent')).to_have_text('78%')
    assert 'short half-life' in page.locator('.nk-uworld-objective').inner_text().lower()
    assert page.locator('.nk-uworld-reading table,.nk-uworld-reading img').count() > 0
    page.screenshot(path=str(output / f'poisoning-answer-{width}.png'))

    # Every source letter is interactive; I is a real wrong answer, never truncated.
    open_question('UWORLD_1321')
    expect(page.locator('.option-list button')).to_have_count(9)
    page.locator('.option-list button').nth(8).click()
    assert page.evaluate('QB.getState().activeSession.answers.UWORLD_1321') == 9
    expect(page.locator('.option-list .wrong .nk-uworld-option-percent')).to_have_text('0%')
    assert 'Physostigmine' in page.locator('.option-list .correct').inner_text()
    expect(page.locator('.option-list .nk-uworld-option-percent')).to_have_count(9)
    page.screenshot(path=str(output / f'poisoning-nine-options-{width}.png'))

    # Item 2 is independently answerable in random/revision/bookmark sessions.
    open_question('UWORLD_2089')
    stem = page.locator('.nk-uworld-stem').inner_text()
    assert 'ankle clonus' in stem.lower() and 'antidote' in stem.lower()
    assert 'Proceed to Next Item' not in stem and 'serotonin syndrome' not in stem.lower()
    assert page.locator('.nk-uworld-objective,.nk-uworld-option-percent').count() == 0
    page.screenshot(path=str(output / f'poisoning-linked-context-{width}.png'))

    open_question('UWORLD_15235')
    table = page.locator('.nk-uworld-stem table')
    expect(table).to_be_visible()
    text = table.inner_text()
    assert '[object Object]' not in text and ('PCO' in text or 'Pco' in text or 'PaCO' in text)
    assert table.locator('tbody tr').count() >= 5
    table.scroll_into_view_if_needed()
    page.screenshot(path=str(output / f'poisoning-labs-{width}.png'))
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')

    # Real graph images must load before answering; missing percentages stay blank.
    open_question('UWORLD_18021')
    expect(page.locator('.nk-uworld-option-figure img')).to_have_count(5)
    page.wait_for_function("() => [...document.querySelectorAll('img[data-uworld-essential=\"true\"]')].every(i=>i.complete&&i.naturalWidth>0)")
    assert page.locator('.nk-uworld-option-percent').count() == 0
    page.screenshot(path=str(output / f'poisoning-graphs-{width}.png'))
    q = page.evaluate('__uworldTest.current()')
    page.locator('.option-list button').nth(q['correctOption'] - 1).click()
    expect(page.locator('.nk-uworld-option-percent')).to_have_count(3)
    assert page.evaluate('QB.getState().activeSession.submitted.UWORLD_18021') is True
    page.get_by_text('Enlarge option diagrams', exact=True).click()
    page.get_by_role('button', name='Enlarge option E', exact=True).click()
    expect(page.locator('#nk-source-viewer .nk-sv-panel')).to_be_visible()
    page.locator('#nk-source-viewer .nk-sv-close').click()

    # The real common CBT builder selects only this namespace and conceals feedback.
    reset_practice()
    page.evaluate('QB.nav("tests")')
    page.get_by_role('button', name='Choose subjects and topics').click()
    page.get_by_role('button', name='Clear all', exact=True).click()
    page.locator('.nk-cbt-builder .nk-module-subject').filter(has_text=collection).click()
    page.get_by_role('button', name='Continue to topics', exact=True).click()
    expect(page.locator('.nk-cbt-topic')).to_have_count(1)
    assert '33 questions' in page.locator('#nk-cbt-footer-count').inner_text()
    page.get_by_role('button', name='Continue to questions', exact=True).click()
    page.locator('#nk-cbt-custom-count').fill('10')
    page.get_by_role('button', name='Start timed CBT', exact=True).click()
    page.wait_for_function('QB.getState().activeSession?.mode==="exam"')
    exam = page.evaluate('QB.getState().activeSession')
    assert len(exam['questionIds']) == 10 and all(qid.startswith('UWORLD_') for qid in exam['questionIds'])
    page.wait_for_function("() => [...document.querySelectorAll('img[data-uworld-essential=\"true\"]')].every(i=>i.complete&&i.naturalWidth>0)")
    q = page.evaluate('__uworldTest.current()')
    page.locator('.option-list button').nth(q['correctOption'] - 1).click()
    assert page.locator('.nk-uworld-explanation,.nk-uworld-option-percent,.nk-uworld-objective').count() == 0
    page.evaluate('QB.openSessionReview()')
    page.locator('#nk-session-review').get_by_role('button', name='Submit Test', exact=True).click()
    page.locator('[data-v102-review-cta]').click()
    page.wait_for_function('QB.getState().activeSession?.mode==="review"')
    assert page.evaluate('QB.getState().activeSession.questionIds') == exam['questionIds']
    expect(page.locator('.nk-uworld-explanation')).to_be_visible()
    assert page.locator('.nk-uworld-option-percent').count() > 0
    page.evaluate('QB.endReview()')
    # A frozen module uses this namespace without disturbing the earlier Biochemistry module.
    reset_practice()
    page.evaluate('QB.openStudyModuleBuilder()')
    chosen = page.locator('.nk-module-subject').filter(has_text=collection)
    if 'is-selected' not in (chosen.get_attribute('class') or ''):
        chosen.click()
    others = page.locator('.nk-module-subject.is-selected').filter(has_not_text=collection)
    while others.count():
        others.first.click()
    page.get_by_role('button', name='Continue', exact=True).click()
    page.get_by_role('button', name='Select all', exact=True).click()
    expect(page.locator('.nk-module-topic')).to_have_count(1)
    page.get_by_role('button', name='Continue to questions', exact=True).click()
    page.locator('.nk-module-count-presets button').filter(has_text='10').click()
    page.get_by_role('button', name='Continue', exact=True).click()
    page.locator('.nk-module-name input').fill('Poisoning reference module')
    page.get_by_role('button', name='Start now', exact=True).click()
    page.locator('.option-list button').first.wait_for()
    module = page.evaluate('QB.getState().studyModules.at(-1)')
    assert len(module['questionIds']) == 10 and all(qid.startswith('UWORLD_') for qid in module['questionIds'])
    assert page.evaluate('QB.getState().activeSession.studyModuleId') == module['id']
    assert page.evaluate('QB.getState().studyModules.some(m=>m.name==="UWorld pilot module")')
    page.evaluate('QB.exitStudyModule()')
    return {'questions': 33, 'nine_options': True, 'linked_context': True, 'native_labs': True,
            'graph_options': True, 'missing_stats_blank': True, 'shared_cbt_review': True,
            'full_block_pause_resume': True, 'frozen_module': True}
