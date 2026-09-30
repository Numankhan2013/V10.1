#!/usr/bin/env python3
"""Certify reviewed completeness contracts in the generated shared learner app."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPRESENTATIVES = {
    'marrow__ANAT_CH10_Q004', 'marrow__ANAT_CH13_Q005', 'marrow__ANAT_CH43_Q005',
    'anatomy-9-1', 'anatomy-47-2', '7-53', 'physiology-23-38', 'physiology-33-33',
    'marrow__BIOCHEM_CH14_Q013', 'marrow__ANAT_CH45_Q004', 'marrow__BIOCHEM_CH17_Q014',
}


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    web = ROOT / 'build/web'
    ledger = json.loads((ROOT / 'data/question_completeness_reviews_v1.json').read_text())
    discoveries = json.loads((ROOT / 'data/marrow/images/source_visual_discoveries.json').read_text())['entries']
    entries = ledger['entries']
    html = (web / 'index.html').read_text()
    marker = 'getState:()=>state,'
    require(html.count(marker) == 1, 'Expected one QB read-only probe insertion point')
    require('NK_QUESTION_COMPLETENESS_REVIEWS_START' in html, 'Generated completeness compiler block missing')
    probe = """__completeness:id=>{const q=BY_ID[id];if(!q)return null;const p=nkQuestionPresentationFor(q);return {id:q.id,valid:p.valid,decision:p.completenessDecision,stem:p.stem,table:p.table,options:p.options,correctOption:q.correctOption};},"""
    html = html.replace(marker, marker + probe, 1)
    output = ROOT / 'build/ui-checks/question-completeness'
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    groups = {}
    for entry in entries:
        groups.setdefault((entry['subject'], entry['bank']), []).append(entry)
    image_groups = {}
    for image in discoveries:
        image_groups.setdefault((image['subject'], 'Marrow'), []).append(image)
    report = {'reviewed': len(entries), 'discoveredImages': len(discoveries), 'runtime': [], 'rendered': []}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for viewport in ({'width': 390, 'height': 844}, {'width': 820, 'height': 1180}):
                context = browser.new_context(viewport=viewport, service_workers='block', reduced_motion='reduce')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))

                def serve(route):
                    if route.request.url == origin + '/':
                        route.fulfill(status=200, content_type='text/html', body=html)
                    elif route.request.url.startswith(origin):
                        route.continue_()
                    else:
                        route.abort()

                page.route('**/*', serve)
                page.goto(origin + '/#dashboard', wait_until='domcontentloaded')
                page.wait_for_function('window.QB && window.QB.getState')

                def open_practice(qid):
                    print('COMPLETENESS_BROWSER_CASE', viewport['width'], qid, flush=True)
                    page.evaluate("""() => {const s=window.QB.getState();s.activeSession=null;s.normalPracticeCheckpoints=[];s.normalPracticeCheckpoint=null;}""")
                    page.evaluate('id=>window.QB.practiceOne(id)', qid)
                    replacement = page.locator('#nk-practice-replacement')
                    if replacement.count() and replacement.is_visible():
                        replacement.get_by_role('button', name='Discard and start new', exact=True).click()
                    page.wait_for_function('id=>{const s=window.QB.getState().activeSession;return s?.questionIds?.[s.index]===id;}', arg=qid, timeout=5000)
                    page.evaluate("window.QB.nav('practice')")
                    page.locator('.question-text').wait_for(state='visible')

                def require_unanswered(qid):
                    require(page.locator('.option-list .correct, .option-list .wrong').count() == 0, f'{qid} correctness leaked before answering')
                    require(page.locator('.nk-study-support:visible').count() == 0, f'{qid} explanation visible before answering')

                def answer_correct(qid):
                    require_unanswered(qid)
                    key = int(page.evaluate('id=>window.QB.__completeness(id).correctOption', qid))
                    page.locator('.option-list button').nth(key - 1).click()
                    page.locator('.option-list .correct').wait_for(state='visible')
                    saved = page.evaluate('id=>{const s=window.QB.getState().activeSession;return {answer:s.answers[id],submitted:s.submitted[id]};}', qid)
                    require(saved['answer'] == key and saved['submitted'] is True, f'{qid} correct DOM answer was not saved: {saved}')
                    correct_indices = page.locator('.option-list .option').evaluate_all(
                        "nodes=>nodes.flatMap((node,index)=>node.classList.contains('correct')?[index+1]:[])")
                    require(correct_indices == [key], f'{qid} correct answer feedback missing: {correct_indices}')

                for subject, bank in sorted(set(groups) | set(image_groups)):
                    page.evaluate('subject=>window.QB.nkOpenSubjectLibrary(subject)', subject)
                    page.locator('button.nk-bank-card').filter(has_text=bank).click()
                    page.locator('button.nk-topic-row').first.wait_for(state='visible')
                    group = groups.get((subject, bank), [])
                    # Every accepted review is checked against actual runtime objects;
                    # DOM checks below cover every blocked item and representative repairs.
                    runtime = page.evaluate('ids=>ids.map(id=>window.QB.__completeness(id))', [e['id'] for e in group])
                    for entry, actual in zip(group, runtime):
                        qid, display = entry['id'], entry['display']
                        require(actual and actual['id'] == qid, f'{qid} missing from active bank runtime')
                        require(actual.get('decision') == entry['decision'], f'{qid} runtime review rejected/source fingerprint drift: {actual}')
                        blocked = bool(display.get('blocked'))
                        require(actual['valid'] == (not blocked), f'{qid} runtime completeness validity wrong')
                        if display.get('question') and not blocked:
                            require(actual['stem'] == display['question'], f'{qid} reviewed stem changed')
                        if display.get('table') and not blocked:
                            require(actual['table']['groups'] == display['table']['groups'], f'{qid} required table cells lost')
                        if display.get('options'):
                            require(actual['options'] == display['options'], f'{qid} reviewed choices changed')
                        if display.get('correctOption'):
                            require(actual['correctOption'] == display['correctOption'], f'{qid} reviewed answer key missing')
                        report['runtime'].append({'id': qid, 'width': viewport['width'], 'blocked': blocked})
                    blocked_entries = [e for e in group if e['display'].get('blocked')]
                    complete_entries = [e for e in group if not e['display'].get('blocked')]
                    # Phone certifies all omission controls; tablet repeats each bank's
                    # omission representative plus matching/list and notation surfaces.
                    selected = blocked_entries if viewport['width'] == 390 else blocked_entries[:1]
                    selected += complete_entries[:1]
                    for has_table in (True, False):
                        representative = next((e for e in complete_entries if bool(e['display'].get('table')) == has_table), None)
                        if representative and representative not in selected:
                            selected.append(representative)
                    selected += [e for e in complete_entries if e['id'] in REPRESENTATIVES and e not in selected]
                    for entry in selected:
                        qid, display = entry['id'], entry['display']
                        open_practice(qid)
                        if display.get('blocked'):
                            notice = page.locator('.nk-question-unavailable')
                            require(notice.is_visible() and 'Question content incomplete' in notice.inner_text(), f'{qid} missing source-omission notice')
                            require(page.locator('.option-list button').count() == 0, f'{qid} incomplete question remains answerable')
                            before = page.evaluate('()=>{const s=window.QB.getState().activeSession;return JSON.stringify({answers:s.answers,submitted:s.submitted});}')
                            page.evaluate('id=>{if(typeof window.QB.selectPractice === "function")window.QB.selectPractice(id,1);}', qid)
                            after = page.evaluate('()=>{const s=window.QB.getState().activeSession;return JSON.stringify({answers:s.answers,submitted:s.submitted});}')
                            require(before == after, f'{qid} direct practice API bypassed omission guard')
                            session = page.evaluate('window.QB.getState().activeSession')
                            require(not (session.get('answers') or {}).get(qid), f'{qid} incomplete source recorded an answer')
                        else:
                            require(page.locator('.option-list button').count() > 0, f'{qid} repaired question has no choices')
                            require_unanswered(qid)
                            text = page.locator('.question-text').inner_text()
                            require('[object Object]' not in text and 'undefined' not in text, f'{qid} broken learner markup')
                            if display.get('table'):
                                table = page.locator('.question-text table.nk-match-table')
                                require(table.is_visible(), f'{qid} required table invisible')
                                table_text = ' '.join(table.inner_text().split())
                                for cells in display['table']['groups']:
                                    for cell in cells:
                                        require(' '.join(cell['value'].split()) in table_text, f'{qid} missing visible table cell {cell}')
                        report['rendered'].append({'id': qid, 'width': viewport['width'], 'kind': 'blocked' if display.get('blocked') else 'repair'})
                        if entry == selected[0] or not display.get('blocked'):
                            page.screenshot(path=str(output / f'{qid}-{viewport["width"]}.png'), full_page=True)
                        if not display.get('blocked'):
                            answer_correct(qid)
                    for image in image_groups.get((subject, bank), []):
                        qid = image['questionId']
                        open_practice(qid)
                        page.locator(f'[data-marrow-question="{qid}"]').wait_for(state='visible')
                        images = page.locator('.nk-marrow-figure-button img')
                        expected_sha = image.get('expectedAssetSha256') or image['expectedStreamSha256']
                        expected = expected_sha + ('.png' if image.get('existingAssetId') else '.jpg')
                        require(images.count() > 0, f'{qid} missing question-owned image')
                        matches = [images.nth(i) for i in range(images.count()) if expected in (images.nth(i).get_attribute('src') or '')]
                        require(len(matches) == 1, f'{qid} exact reviewed question image missing/duplicated')
                        matches[0].scroll_into_view_if_needed()
                        page.wait_for_function('sha=>Array.from(document.querySelectorAll(".nk-marrow-figure-button img")).some(i=>i.src.includes(sha)&&i.complete&&i.naturalWidth>0)', arg=expected)
                        require(matches[0].get_attribute('alt') == 'Source figure', f'{qid} non-neutral image alt')
                        require_unanswered(qid)
                        page.screenshot(path=str(output / f'{qid}-image-{viewport["width"]}.png'), full_page=True)
                        report['rendered'].append({'id': qid, 'width': viewport['width'], 'kind': 'source-image', 'sha256': expected_sha})
                        answer_correct(qid)
                require(not errors, 'Completeness browser JavaScript errors: ' + ' | '.join(errors))
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'QUESTION_COMPLETENESS_BROWSER_OK reviews={len(entries)} runtime_checks={len(report["runtime"])} source_images={len(discoveries)} phone_tablet=true omissions_fail_closed=true')


if __name__ == '__main__':
    main()
