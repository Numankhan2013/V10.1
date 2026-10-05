"""New source collections exercise the incumbent study lifecycle and presenter."""
from playwright.sync_api import expect
import re
from uworld_content_hygiene import CHROME


def verify_imported_collections(page, output, width, reset_practice, open_question):
    reports = []
    for name, key, counts in [('Male Reproductive System', 'male-reproductive', [39, 13]),
                              ('Female Reproductive System & Breast', 'female-reproductive', [41, 40]),
                              ('Biostatistics & Epidemiology', 'biostatistics', [40, 20])]:
        page.evaluate('QB.nav("uworld")')
        card = page.locator('.nk-uworld-collection').filter(has_text=re.compile(re.escape(name)))
        assert card.locator('.nk-v3-subject-icon svg').get_attribute('data-nk-icon') == key
        card.click()
        expect(page.locator('.nk-topic-row')).to_have_count(len(counts))
        assert page.locator('.nk-topic-path').count() == 0
        expect(page.locator('.nk-uworld-topic-icon')).to_have_count(len(counts))
        page.screenshot(path=str(output / f'{key}-blocks-{width}.png'))
        for index, count in enumerate(counts):
            page.locator('.nk-topic-row').nth(index).click()
            expect(page.locator('.nk-library-row')).to_have_count(count)
            expect(page.locator('.nk-chapter-v114 .nk-back-link')).to_have_text('Blocks')
            page.locator('.nk-chapter-v114 .nk-back-link').click()

        members = page.evaluate('name=>__uworldTest.questions().filter(q=>q.collection===name)', name)
        eligible = [q for q in members if not q['uworldPilot']['requiresVisual']]
        # Complete multi-question snapshot, Pause and rendered Continue keep IDs,
        # position and answered progress. Pausing never creates a skipped answer.
        for block_index in range(len(counts)):
            page.evaluate('QB.nav("uworld")')
            page.locator('.nk-uworld-collection').filter(has_text=re.compile(re.escape(name))).click()
            page.locator('.nk-topic-row').nth(block_index).click()
            reset_practice()
            page.locator('.nk-chapter-actions').get_by_role('button', name='Practice', exact=False).click()
            page.locator('#modal').get_by_role('button', name='Start Practice', exact=True).click()
            page.locator('.option-list button').first.wait_for()
            original = page.evaluate('QB.getState().activeSession')
            assert len(original['questionIds']) == sum(q['chapterId'] == members[sum(counts[:block_index])]['chapterId'] for q in eligible)
            page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
            q = page.evaluate('__uworldTest.current()')
            page.locator('.option-list button').nth(q['correctOption'] - 1).click()
            page.get_by_role('button', name='Next', exact=True).click()
            before = page.evaluate('QB.getState().activeSession')
            page.evaluate('QB.openSessionReview()')
            page.locator('#nk-session-review').get_by_role('button', name='Pause', exact=True).click()
            page.wait_for_function('QB.getState().activeSession?.lifecycle==="paused"')
            page.locator('.nk-home-focus-action').click()
            resumed = page.evaluate('QB.getState().activeSession')
            assert resumed['id'] == original['id'] and resumed['questionIds'] == original['questionIds']
            assert resumed['index'] == before['index'] and resumed['answers'] == before['answers']
            assert not resumed['submitted'].get(resumed['questionIds'][resumed['index']])
        tables = figures = 0
        for q in eligible:
            open_question(q['id'])
            page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
            assert page.locator('.nk-uworld-option-percent,.nk-uworld-explanation,.nk-uworld-objective').count() == 0
            stem = page.locator('.nk-uworld-stem').inner_text()
            assert 'Exhibit Display' not in stem and 'Answered correctly' not in stem
            # Confirm the source's labeled diagnostic matrix, not a blank table.
            if q['id'] == 'UWORLD_1902':
                assert all(text in stem for text in ['Testosterone', 'Inhibin', 'FSH', 'LH'])
                expect(page.locator('.nk-uworld-stem table')).to_have_count(1)
            if q['id'] in ['UWORLD_15800', 'UWORLD_16001', 'UWORLD_14853', 'UWORLD_1187', 'UWORLD_1285', 'UWORLD_20250', 'UWORLD_20088']:
                expect(page.locator('.nk-uworld-stem img')).to_have_count(1)
            if q['id'] == 'UWORLD_19691':
                assert 'hepatitis C (HCV)' in stem and 'HGV' not in stem
            if q['id'] == 'UWORLD_1272':
                assert 'β' in page.locator('.option-list').inner_text()
            page.locator('.option-list button').nth(q['correctOption'] - 1).click()
            expect(page.locator('.nk-uworld-objective')).to_be_visible()
            for option in q['options']:
                percent = page.locator('.option-list').get_by_text(f"{option['selection_percent']}%", exact=True)
                if option['selection_percent'] is not None:
                    assert percent.count() > 0, (q['id'], option)
            explanation = page.locator('.nk-uworld-explanation').inner_text()
            assert not CHROME.search(explanation), q['id']
            assert page.get_by_text('Original OCR explanation', exact=True).count() == 0
            assert 'uworldTranscript' not in q and 'source_page_ocr' not in q['uworldSource']
            if q['id'] == 'UWORLD_869':
                assert 'douching-induced epithelial injury' in explanation
                assert 'often caused by infection with HPV types 1-4' in explanation
            if q['id'] == 'UWORLD_1027':
                assert '≥35' in explanation and '≥12 months' in explanation
            if q['id'] == 'UWORLD_19445':
                assert all(text in stem for text in ['Present','Not Present','45','120','125'])
                assert '0.96' in explanation
            if q['id'] == 'UWORLD_19806':
                assert all(text in stem for text in ['Low','High','82','60','41','66','249'])
                assert '0.45' in explanation and '66/60' in explanation
            if q['id'] == 'UWORLD_14853':
                expect(page.locator('.nk-uworld-stem img')).to_have_count(1)
            if q['id'] == 'UWORLD_1299':
                assert '√n' in explanation
            if q['id'] == 'UWORLD_19262':
                assert 'α' in explanation and 'β' in explanation
                assert 'Type I' in explanation and 'Type II' in explanation
                expect(page.locator('.nk-uworld-reading table')).to_have_count(1)
            if q['id'] == 'UWORLD_12854':
                assert all(value in stem for value in ['9.1','10.4','13.5'])
                assert '0.705' in explanation
            if q['id'] == 'UWORLD_11835':
                assert 'q²' in explanation and '1/400' in explanation
            if q['id'] == 'UWORLD_19810':
                assert '1.5' in explanation and 'equivalent' in explanation
            assert all(p.inner_text().strip() for p in page.locator('.nk-uworld-choice-discussion p').all())
            page.wait_for_function('''() => [...document.querySelectorAll('.nk-uworld-reading img')].every(i=>i.complete&&i.naturalWidth>0)''')
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), q['id']
            tables += page.locator('.nk-uworld-reading table,.nk-uworld-stem table').count()
            figures += page.locator('.nk-uworld-reading img,.nk-uworld-stem img').count()
            if q['id'] == eligible[0]['id'] or q['id'] in ['UWORLD_16001','UWORLD_8519','UWORLD_1299','UWORLD_1187','UWORLD_1169','UWORLD_1285','UWORLD_1284','UWORLD_19262','UWORLD_12854','UWORLD_11835','UWORLD_19810','UWORLD_20088','UWORLD_19431','UWORLD_19741','UWORLD_1233','UWORLD_108026','UWORLD_1279','UWORLD_1283']:
                page.locator('.nk-uworld-objective').scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                page.screenshot(path=str(output / f'{key}-{q["id"]}-{width}.png'), full_page=True)

        reset_practice()
        page.evaluate('QB.nav("tests")')
        page.get_by_role('button', name='Choose subjects and topics').click()
        page.get_by_role('button', name='Clear all', exact=True).click()
        page.locator('.nk-cbt-builder .nk-module-subject').filter(has_text=re.compile(re.escape(name))).click()
        page.get_by_role('button', name='Continue to topics', exact=True).click()
        expect(page.locator('.nk-cbt-topic')).to_have_count(len(counts))
        page.get_by_role('button', name='Continue to questions', exact=True).click()
        page.locator('#nk-cbt-custom-count').fill('10')
        page.get_by_role('button', name='Start timed CBT', exact=True).click()
        page.wait_for_function('QB.getState().activeSession?.mode==="exam"')
        exam = page.evaluate('QB.getState().activeSession')
        assert len(exam['questionIds']) == 10 and set(exam['questionIds']) <= {q['id'] for q in eligible}
        page.wait_for_function('''() => [...document.querySelectorAll('img[data-uworld-essential="true"]')].every(i=>i.complete&&i.naturalWidth>0)''')
        q = page.evaluate('__uworldTest.current()')
        page.locator('.option-list button').nth(q['correctOption'] - 1).click()
        assert page.locator('.nk-uworld-option-percent,.nk-uworld-explanation,.nk-uworld-objective').count() == 0
        page.evaluate('QB.openSessionReview()')
        page.locator('#nk-session-review').get_by_role('button', name='Submit Test', exact=True).click()
        page.locator('[data-v102-review-cta]').click()
        page.wait_for_function('QB.getState().activeSession?.mode==="review"')
        assert page.evaluate('QB.getState().activeSession.questionIds') == exam['questionIds']
        expect(page.locator('.nk-uworld-explanation')).to_be_visible()
        page.evaluate('QB.endReview()')
        reports.append({'collection': name, 'records': len(members), 'eligible': len(eligible),
                        'blocks': len(counts), 'tables': tables, 'figures': figures,
                        'pause_continue': True, 'cbt_review': True, 'option_stats': True})
    return reports
