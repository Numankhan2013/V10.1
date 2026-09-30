#!/usr/bin/env python3
"""Check source-reviewed final images in the real learner flow on phone/tablet."""
import functools
import http.server
import json
import socketserver
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from marrow_images import ROOT, DATA, questions

WEB = ROOT / 'build/web'
OUT = ROOT / 'build/marrow-ui-checks'


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    qmap = questions()
    request = json.loads((DATA / 'images/review_requests/FINAL_PHYS_SOURCE_REVIEW_20260930.json').read_text())
    owners = sorted({entry['questionId'] for entry in request['entries']})
    metadata = json.loads((WEB / 'marrow_visual_metadata.js').read_text().split('=', 1)[1].rstrip(';\n'))
    OUT.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(Quiet, directory=str(WEB))
    with socketserver.TCPServer(('127.0.0.1', 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            results = []
            for size, viewport in [('phone', {'width': 390, 'height': 844}),
                                   ('tablet', {'width': 820, 'height': 1180})]:
                for qid in owners:
                    q = qmap[qid]
                    context = browser.new_context(viewport=viewport)
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.goto(f'http://127.0.0.1:{server.server_address[1]}/index.html', wait_until='networkidle')
                    page.evaluate("window.QB.nkOpenSubjectLibrary('Physiology')")
                    page.locator('button.nk-bank-card').filter(has_text='Marrow').click()
                    # Exact chapter identity avoids the I / II title prefix collision.
                    chapter = str(q['chapterId'])
                    assert chapter.isdigit()
                    page.locator(f'button.nk-topic-row[onclick="window.QB.openChapter(\'{chapter}\')"]').click()
                    page.locator('button.nk-library-row').nth(int(q['questionNumber']) - 1).click()
                    page.locator(f'[data-marrow-question="{qid}"]').wait_for(state='visible')
                    expected_question = [row['src'] for row in metadata[qid] if row['role'] == 'question']
                    expected_explanation = [row['src'] for row in metadata[qid] if row['role'] == 'explanation']
                    images = page.locator('.nk-marrow-figure-button img')
                    assert images.count() == len(expected_question), f'{qid}: explanation figure leaked before answering'
                    actual = images.evaluate_all(r'(nodes)=>nodes.map(n=>n.getAttribute("src").replace(/^\.\//,""))')
                    assert sorted(actual) == sorted(expected_question), f'{qid}: wrong question source image'
                    if expected_question:
                        page.wait_for_function('Array.from(document.querySelectorAll(".nk-marrow-figure-button img")).every(i=>i.complete&&i.naturalWidth>0)')
                        assert all(alt == 'Source figure' for alt in images.evaluate_all(r'(nodes)=>nodes.map(n=>n.alt)')), f'{qid}: question alt text is identifying'
                        page.screenshot(path=str(OUT / f'final-images-{size}-{qid}-unanswered.png'), full_page=True)
                    page.locator('.option-list button').nth(int(q['correctOption']) - 1).click()
                    page.locator(f'[data-marrow-explanation="{qid}"]').wait_for(state='visible')
                    for i in range(images.count()):
                        images.nth(i).scroll_into_view_if_needed()
                        page.wait_for_function('(i)=>{const image=document.querySelectorAll(".nk-marrow-figure-button img")[i];return image?.complete&&image.naturalWidth>0}', arg=i)
                    page.wait_for_function('Array.from(document.querySelectorAll(".nk-marrow-figure-button img")).every(i=>i.complete&&i.naturalWidth>0)')
                    actual = images.evaluate_all(r'(nodes)=>nodes.map(n=>n.getAttribute("src").replace(/^\.\//,""))')
                    assert sorted(actual) == sorted(expected_question + expected_explanation), f'{qid}: missing/wrong answered source image'
                    for e in [e for e in request['entries'] if e['questionId'] == qid]:
                        assert any(row['role'] == e['role'] and row['order'] == e['order'] for row in metadata[qid]), f'{e["referenceId"]}: reviewed binding absent'
                    page.screenshot(path=str(OUT / f'final-images-{size}-{qid}-answered.png'), full_page=True)
                    # The source-native masked micrograph and tiled question graph
                    # exercise the same real fullscreen viewer, including zoom.
                    if qid in {'marrow__PHYS_CH07_Q009', 'marrow__PHYS_CH06_Q007'}:
                        page.locator('.nk-marrow-figure-button').last.click()
                        page.wait_for_function('document.querySelector("#nk-source-viewer img")?.naturalWidth>0')
                        page.locator('#nk-source-viewer [data-z="+"]').click()
                        page.screenshot(path=str(OUT / f'final-images-{size}-{qid}-zoom.png'))
                        page.locator('#nk-source-viewer .nk-sv-close').click()
                    assert not errors, f'{qid}: browser errors {errors}'
                    results.append({'questionId': qid, 'viewport': size,
                                    'questionFigures': len(expected_question),
                                    'explanationFigures': len(expected_explanation)})
                    context.close()
            browser.close()
        server.shutdown()
    (OUT / 'final-physiology-image-report.json').write_text(json.dumps(results, indent=2) + '\n')
    print('FINAL_PHYSIOLOGY_IMAGES_BROWSER_OK', len(results))


if __name__ == '__main__':
    main()
