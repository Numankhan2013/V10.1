#!/usr/bin/env python3
"""Check every released wave ID and representative real learner interactions."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright
from test_marrow_explanation_refinement_wave import load_wave

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def cell_text(value):
    if value is None:
        return ''
    if isinstance(value, list):
        return ' · '.join(filter(None, map(cell_text, value)))
    if isinstance(value, dict):
        for key in ('text', 'label', 'value', 'title', 'name', 'content'):
            if key in value and cell_text(value[key]):
                return cell_text(value[key])
        return ' · '.join(filter(None, map(cell_text, value.values())))
    return str(value).strip()


def table_cells(table):
    columns = table.get('columns', [])
    labels = [cell_text(c.get('label', c.get('title', c.get('key', ''))))
              if isinstance(c, dict) else cell_text(c) for c in columns]
    rows = []
    for row in table.get('rows', []):
        if isinstance(row, list):
            rows += [cell_text(c) for c in row]
        elif isinstance(row, dict):
            rows += [cell_text(row.get(c.get('key', str(i)) if isinstance(c, dict) else str(i), ''))
                     for i, c in enumerate(columns)]
    return labels, rows


def main():
    manifest, sources, wave = load_wave()
    web = ROOT / 'build/web'
    html = (web / 'index.html').read_text()
    marker = 'getState:()=>state,'
    require(html.count(marker) == 1, 'Read-only runtime probe insertion point changed')
    probe = """__explanationWave:id=>{const q=BY_ID[id];if(!q)return null;return {id:q.id,cfg:NK_MARROW_EXPLANATION_GOLD_V1[id],blocked:!nkQuestionPresentationFor(q).valid,tables:q.structuredExplanation?.tables||[]};},__wavePlain:t=>{const d=document.createElement('div');d.innerHTML=nkScientificMarkup(t);return d.textContent;},"""
    html = html.replace(marker, marker + probe, 1)
    output = ROOT / 'build/ui-checks/explanation-refinement'
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    report = {'new': manifest['newEnhancedCount'], 'audited': len(wave), 'runtime': [], 'rendered': []}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width, height in ((390, 844), (820, 1180)):
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))

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
                for subject in sorted({sources[qid]['subject'] for qid in wave}):
                    page.evaluate('subject=>window.QB.nkOpenSubjectLibrary(subject)', subject)
                    page.locator('button.nk-bank-card').filter(has_text='Marrow').click()
                    page.locator('button.nk-topic-row').first.wait_for(state='visible')
                    ids = [qid for qid in wave if sources[qid]['subject'] == subject]
                    actuals = page.evaluate('ids=>ids.map(id=>window.QB.__explanationWave(id))', ids)
                    blocked = set()
                    for qid, actual in zip(ids, actuals):
                        require(actual and actual['id'] == qid, f'{qid}: missing active-bank record')
                        require(actual['cfg'] == wave[qid], f'{qid}: reviewed augmentation missing or altered in runtime')
                        if actual['blocked']:
                            blocked.add(qid)
                        report['runtime'].append({'id': qid, 'width': width, 'blocked': actual['blocked']})
                    representatives = {spec['browserId'] for spec in manifest['batches'] + manifest.get('existingRepairs', []) if sources[spec['browserId']]['subject'] == subject}
                    representatives |= {qid for qid in ids if sources[qid].get('structuredExplanation', {}).get('tables')}
                    representatives |= blocked
                    for qid in sorted(representatives):
                        print('EXPLANATION_WAVE_BROWSER_CASE', width, qid, flush=True)
                        page.evaluate('()=>{const s=window.QB.getState();s.activeSession=null;s.normalPracticeCheckpoints=[];s.normalPracticeCheckpoint=null;}')
                        page.evaluate('id=>window.QB.practiceOne(id)', qid)
                        replacement = page.locator('#nk-practice-replacement')
                        if replacement.count() and replacement.is_visible():
                            replacement.get_by_role('button', name='Discard and start new', exact=True).click()
                        page.wait_for_function('id=>{const s=window.QB.getState().activeSession;return s?.questionIds?.[s.index]===id;}', arg=qid)
                        page.evaluate("window.QB.nav('practice')")
                        page.locator('.question-text').wait_for(state='visible')
                        require(page.locator('.nk-study-support:visible').count() == 0, f'{qid}: explanation leaked before answering')
                        if qid in blocked:
                            require(page.locator('.nk-question-unavailable').is_visible() and page.locator('.option-list button').count() == 0, f'{qid}: source gate bypassed')
                        else:
                            page.locator('.option-list button').nth(int(sources[qid]['correctOption']) - 1).click()
                            support = page.locator('.nk-study-support')
                            support.wait_for(state='visible')
                            text = support.inner_text()
                            require('[object Object]' not in text and 'undefined' not in text, f'{qid}: broken explanation')
                            for label in ('Key Takeaway', 'Detailed explanation', 'Structured text', 'Why the other options are wrong'):
                                require(label.lower() in text.lower(), f'{qid}: missing {label}')
                            rows = page.locator('.nk-gold-wrong-row')
                            require(rows.count() == 3, f'{qid}: distractor row count')
                            for reason in wave[qid]['rationales'].values():
                                expected = page.evaluate('t=>window.QB.__wavePlain(t)', reason)
                                require(' '.join(expected.split()) in ' '.join(text.split()), f'{qid}: missing rationale {reason}')
                            require(page.locator('.nk-gold-em').count() > 0, f'{qid}: selective emphasis missing')
                            require(page.locator('.nk-fsrs-rating').is_visible(), f'{qid}: FSRS dock missing')
                            native_tables = wave[qid].get('displayTables', sources[qid].get('structuredExplanation', {}).get('tables', []))
                            native_tables = [table for table in native_tables if table.get('columns') and table.get('rows')]
                            tables = page.locator('.nk-gold-explanation .nk-marrow-table')
                            require(tables.count() == len(native_tables), f'{qid}: native table lost')
                            for i, native in enumerate(native_tables):
                                labels, cells = table_cells(native)
                                headers = tables.nth(i).locator('th').all_inner_texts()
                                body = tables.nth(i).locator('td').all_inner_texts()
                                expected_headers = [page.evaluate('t=>window.QB.__wavePlain(t)', v) for v in labels]
                                expected_cells = [page.evaluate('t=>window.QB.__wavePlain(t)', v) for v in cells]
                                norm = lambda values: [' '.join(v.split()) for v in values]
                                require(norm(headers) == norm(expected_headers), f'{qid}: table header content/order changed')
                                require(norm(body) == norm(expected_cells), f'{qid}: table cell content/order changed')
                        report['rendered'].append({'id': qid, 'width': width, 'blocked': qid in blocked})
                        page.screenshot(path=str(output / f'{qid}-{width}.png'), full_page=True)
                    require(not errors, 'Explanation browser errors: ' + ' | '.join(errors))
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'MARROW_EXPLANATION_REFINEMENT_BROWSER_OK new={report["new"]} audited={len(wave)} runtime={len(report["runtime"])} rendered={len(report["rendered"])} phone_tablet=true')


if __name__ == '__main__':
    main()
