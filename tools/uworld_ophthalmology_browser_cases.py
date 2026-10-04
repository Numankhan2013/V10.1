"""PDF-only collection exercises through the existing shared learner controls."""
from playwright.sync_api import expect


def verify_ophthalmology(page, output, width, reset_practice, open_question):
    collection = 'Ophthalmology'
    page.evaluate('QB.nav("uworld")')
    page.locator('.nk-uworld-collection').filter(has_text=collection).click()
    expect(page.locator('button.nk-topic-row')).to_have_count(1)
    assert page.locator('.nk-topic-group>h2').all_inner_texts() == ['Blocks']
    page.locator('button.nk-topic-row').click()
    expect(page.locator('.nk-chapter-v114 .nk-back-link')).to_have_text('Blocks')
    expect(page.locator('button.nk-library-row')).to_have_count(30)
    reset_practice()
    page.locator('.nk-chapter-actions').get_by_role('button', name='Practice', exact=False).click()
    page.locator('#modal').get_by_role('button', name='Start Practice', exact=True).click()
    page.locator('.option-list button').first.wait_for()
    original = page.evaluate('QB.getState().activeSession')
    assert len(original['questionIds']) == 30
    for _ in range(2):
        page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
        q = page.evaluate('__uworldTest.current()')
        page.locator('.option-list button').nth(q['correctOption'] - 1).click()
        page.get_by_role('button', name='Next', exact=True).click()
    before = page.evaluate('QB.getState().activeSession')
    page.evaluate('QB.openSessionReview()')
    page.locator('#nk-session-review').get_by_role('button', name='Pause', exact=True).click()
    page.wait_for_function('QB.getState().activeSession?.lifecycle==="paused"')
    page.locator('button.nk-home-focus-action').click()
    page.locator('.option-list button').first.wait_for()
    resumed = page.evaluate('QB.getState().activeSession')
    assert resumed['id'] == original['id'] and resumed['questionIds'] == original['questionIds']
    assert resumed['index'] == 2 and resumed['answers'] == before['answers']
    assert not resumed['submitted'].get(resumed['questionIds'][2])

    open_question('UWORLD_18804')
    assert page.locator('.nk-uworld-option-percent,.nk-uworld-objective,.nk-uworld-explanation').count() == 0
    page.locator('.option-list button').nth(2).click()
    expect(page.locator('.option-list .correct .nk-uworld-option-percent')).to_have_text('47%')
    assert 'cataract' in page.locator('.nk-uworld-objective').inner_text().lower()
    expect(page.locator('.nk-uworld-reading table')).to_have_count(1)
    assert page.locator('.nk-uworld-reading img').count() > 0
    page.screenshot(path=str(output / f'ophthalmology-answer-{width}.png'))

    open_question('UWORLD_106294')
    expect(page.locator('.option-list button')).to_have_count(6)
    expect(page.locator('.nk-uworld-stem img').first).to_be_visible()
    page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
    stem = page.locator('.nk-uworld-stem').inner_text()
    assert stem.lower().count('defect in which of the following pathways') == 1
    assert page.locator('.nk-uworld-option-percent,.nk-uworld-objective').count() == 0
    page.screenshot(path=str(output / f'ophthalmology-pupil-exhibit-{width}.png'))
    page.locator('.nk-uworld-stem .nk-uworld-figure button').first.click()
    expect(page.locator('#nk-source-viewer .nk-sv-panel')).to_be_visible()
    page.locator('#nk-source-viewer .nk-sv-close').click()

    open_question('UWORLD_8594')
    expect(page.locator('.nk-uworld-option-figure img')).to_have_count(5)
    page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
    assert page.locator('.nk-uworld-option-percent').count() == 0
    assert 'Left / Right' in page.locator('.nk-uworld-stem').inner_text()
    page.screenshot(path=str(output / f'ophthalmology-visual-fields-{width}.png'))
    page.locator('.option-list button').nth(3).click()
    expect(page.locator('.option-list .correct .nk-uworld-option-percent')).to_have_text('57%')
    page.get_by_text('Enlarge option diagrams', exact=True).click()
    page.get_by_role('button', name='Enlarge option E', exact=True).click()
    expect(page.locator('#nk-source-viewer .nk-sv-panel')).to_be_visible()
    page.locator('#nk-source-viewer .nk-sv-close').click()

    # A new collection enters the same timed builder and deferred-feedback path.
    reset_practice()
    page.evaluate('QB.nav("tests")')
    page.get_by_role('button', name='Choose subjects and topics').click()
    page.get_by_role('button', name='Clear all', exact=True).click()
    page.locator('.nk-cbt-builder .nk-module-subject').filter(has_text=collection).click()
    page.get_by_role('button', name='Continue to topics', exact=True).click()
    expect(page.locator('.nk-cbt-topic')).to_have_count(1)
    page.get_by_role('button', name='Continue to questions', exact=True).click()
    page.locator('#nk-cbt-custom-count').fill('10')
    page.get_by_role('button', name='Start timed CBT', exact=True).click()
    page.wait_for_function('QB.getState().activeSession?.mode==="exam"')
    exam = page.evaluate('QB.getState().activeSession')
    members = page.evaluate('__uworldTest.questions().filter(q=>q.collection==="Ophthalmology").map(q=>q.id)')
    assert len(exam['questionIds']) == 10 and set(exam['questionIds']) <= set(members)
    page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
    q = page.evaluate('__uworldTest.current()')
    page.locator('.option-list button').nth(q['correctOption'] - 1).click()
    assert page.locator('.nk-uworld-explanation,.nk-uworld-option-percent,.nk-uworld-objective').count() == 0
    page.evaluate('QB.openSessionReview()')
    page.locator('#nk-session-review').get_by_role('button', name='Submit Test', exact=True).click()
    page.locator('[data-v102-review-cta]').click()
    page.wait_for_function('QB.getState().activeSession?.mode==="review"')
    assert page.evaluate('QB.getState().activeSession.questionIds') == exam['questionIds']
    expect(page.locator('.nk-uworld-explanation')).to_be_visible()
    page.evaluate('QB.endReview()')

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
    page.locator('.nk-module-name input').fill('Ophthalmology PDF module')
    page.get_by_role('button', name='Start now', exact=True).click()
    page.locator('.option-list button').first.wait_for()
    module = page.evaluate('QB.getState().studyModules.at(-1)')
    assert len(module['questionIds']) == 10 and set(module['questionIds']) <= set(members)
    assert page.evaluate('QB.getState().activeSession.studyModuleId') == module['id']
    assert page.evaluate('QB.getState().studyModules.some(m=>m.name==="Poisoning reference module")')
    page.evaluate('QB.exitStudyModule()')

    # Inspect every imported question in the running presentation at each width.
    nodes = {'tables': 0, 'figures': 0}
    for qid in members:
        open_question(qid)
        page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
        q = page.evaluate('__uworldTest.current()')
        page.locator('.option-list button').nth(q['correctOption'] - 1).click()
        page.wait_for_function('''() => [...document.querySelectorAll('.nk-uworld-stem img,.nk-uworld-reading img')].every(i=>i.complete&&i.naturalWidth>0)''')
        assert '[object Object]' not in ' '.join(page.locator('.nk-uworld-stem,.nk-uworld-reading').all_inner_texts())
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), qid
        nodes['tables'] += page.locator('.nk-uworld-stem table,.nk-uworld-reading table').count()
        nodes['figures'] += page.locator('.nk-uworld-stem img,.nk-uworld-reading img').count()
    page.screenshot(path=str(output / f'ophthalmology-last-answer-{width}.png'))
    reset_practice()
    page.evaluate('QB.nav("question-search")')
    page.locator('.nk-question-search-filters select').nth(0).select_option('UWorld · Ophthalmology')
    expect(page.locator('.nk-question-search-item')).to_have_count(30)
    return {'questions': 30, 'pdf_only_extraction': True, 'full_block_pause_resume': True,
            'essential_exhibit': True, 'six_options': True, 'graphical_options': True, 'immediate_percentages': True,
            'shared_cbt_review': True, 'frozen_module': True, 'search': True, 'all_rendered': nodes}
