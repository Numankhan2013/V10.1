#!/usr/bin/env python3
"""Submit attempted in the real app (practice_submit_attempted.js).

A topic Practice: Q1 correct, Q2 left blank, Q3 wrong, Q4 correct, Q5 left blank,
Q6 correct, Q7 opened for 20 s and left (after the last answer). The session sheet
shows the grid language (correct = solid green, wrong = solid red, skipped = hollow
yellow, not attempted = hollow) and a "Submit attempted" action for questions 1-6.
Submitting it: the result covers 6 questions (3 correct, 1 incorrect, 2 skipped,
labelled Skipped), Q7 is not in the result, not marked skipped and not in FSRS; the
topic page shows "Continue where you left off" (from question 7) beside "Practice
entire topic", every other topic option unchanged; Continue starts the 18 left-out
questions. Runs at 390 px and 1280 px, light and dark; screenshots go to build/ui-checks.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''window.__sa={
 pick:()=>{const ok=q=>nkQuestionPresentationFor(q).valid&&(typeof nkFsrsAnswerable!=='function'||nkFsrsAnswerable(q));const c=CHAPTERS.find(c=>{const qs=chapterQuestions(c.id);return qs.length>=12&&qs.length<=60&&qs.every(ok);});return c?{id:String(c.id),n:chapterQuestions(c.id).length}:null;},
 go:(i)=>goIndex(i),
 cur:()=>{const s=state.activeSession,id=s.questionIds[s.index],q=BY_ID[id]||nkFindStudyQuestion(id);return {i:s.index,id:String(q.id),correct:Number(q.correctOption),count:q.options.length};},
 dwell:(ms)=>{state.activeSession.questionEnteredAt=Date.now()-ms;}
};
'''
RESET = '''()=>{const s=QB.getState();Object.assign(s,{attempts:{},tests:[],activeSession:null,reviews:{},fsrsReviewEligible:{},notStudied:{},normalPracticeCheckpoints:[],normalPracticeCheckpoint:null});QB.saveState();}'''
CELLS = '''()=>[...document.querySelectorAll('#nk-session-review .nk-session-review-q')].slice(0,8).map(e=>{const cs=getComputedStyle(e);return {cls:e.className,bg:cs.backgroundColor,border:cs.borderTopColor,bw:parseFloat(cs.borderTopWidth)};})'''


def transparent(color):
    return color in ('transparent', 'rgba(0, 0, 0, 0)')


def run(origin, out):
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, height in [(390, 844), (1280, 900)]:
            for scheme in ('light', 'dark'):
                tag = f'{width}-{scheme}'
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block', has_touch=True, is_mobile=width < 600, color_scheme=scheme)
                page = context.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
                page.route('**/*', lambda r: r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin+'/#dashboard', wait_until='domcontentloaded'); page.wait_for_function('window.QB?.getState && window.__sa')
                page.evaluate(RESET)
                chapter = page.evaluate('window.__sa.pick()'); assert chapter, 'no topic with 12+ answerable questions'
                cid, total = chapter['id'], chapter['n']
                page.evaluate(f"QB.nav('chapter',{cid!r})"); page.wait_for_selector('.nk-chapter-actions .is-primary')
                options_before = page.locator('.nk-topic-options').inner_text()
                page.click('.nk-chapter-actions .is-primary')
                if page.locator('#modal .is-primary').count(): page.click('#modal .is-primary')
                page.wait_for_selector('.option')
                plan = ['c', 'k', 'w', 'c', 'k', 'c', 't']
                for i, step in enumerate(plan):
                    page.evaluate(f'window.__sa.go({i})'); page.wait_for_function('i=>QB.getState().activeSession?.index===i', arg=i)
                    cur = page.evaluate('window.__sa.cur()')
                    if step == 'c':
                        page.locator('.option').nth(cur['correct']-1).click()
                        good = page.locator('.nk-fsrs-rating').get_by_role('button', name='Good', exact=True)
                        if good.count(): good.click()
                    elif step == 'w':
                        page.locator('.option').nth(cur['correct'] % cur['count']).click()
                    else:
                        page.evaluate('window.__sa.dwell(20000)')
                    page.wait_for_timeout(120)
                tail_id = page.evaluate('window.__sa.cur().id')
                page.evaluate('QB.openSessionReview()'); page.wait_for_selector('#nk-session-review .nk-practice-submit-attempted')
                cells = page.evaluate(CELLS)
                for i in (0, 3, 5): assert 'is-correct' in cells[i]['cls'] and not transparent(cells[i]['bg']), (i, cells[i])
                assert 'is-wrong' in cells[2]['cls'] and not transparent(cells[2]['bg']), cells[2]
                for i in (1, 4): assert 'is-skipped' in cells[i]['cls'] and transparent(cells[i]['bg']) and cells[i]['bw'] >= 2, (i, cells[i])
                assert transparent(cells[7]['bg']) and 'is-skipped' not in cells[7]['cls'], cells[7]
                button = page.locator('.nk-practice-submit-attempted')
                label = button.inner_text()
                assert 'Submit attempted' in label and 'Questions 1–6' in label and '2 skipped' in label and f'{total-6} left for later' in label, label
                box = button.bounding_box(); assert box['x'] >= 0 and box['x'] + box['width'] <= width + 1, box
                page.wait_for_timeout(300); page.screenshot(path=str(out/f'submit-attempted-sheet-{tag}.png'))
                button.click(); page.wait_for_function("location.hash.startsWith('#result')")
                t = page.evaluate('QB.getState().tests.at(-1)')
                assert t['partial'] is True and len(t['questionIds']) == 6 and t['correct'] == 3 and t['incorrect'] == 1 and t['unattempted'] == 2 and t['skipped'] == 2, t
                assert tail_id not in t['questionIds'] and tail_id not in t['questionTimes'] and len(t['practiceContext']['remainingIds']) == total-6, t
                state = page.evaluate('QB.getState()')
                assert tail_id not in (state.get('fsrsReviewEligible') or {}) and not state['attempts'].get(tail_id), 'the left-out question must stay out of FSRS'
                assert len(state.get('fsrsReviewEligible') or {}) == 2, state.get('fsrsReviewEligible')
                assert state['activeSession'] is None
                body = page.locator('#app').inner_text()
                assert 'Questions 1–6 of' in body and 'not counted' in body and 'Skipped' in body and 'Omitted' not in body, body[:600]
                page.wait_for_timeout(300); page.screenshot(path=str(out/f'submit-attempted-result-{tag}.png'), full_page=True)
                page.evaluate(f"QB.nav('chapter',{cid!r})"); page.wait_for_selector('.nk-topic-leftoff')
                leftoff = page.locator('.nk-topic-leftoff').inner_text()
                assert 'Continue where you left off' in leftoff and f'From question 7 of {total}' in leftoff, leftoff
                assert 'Practice entire topic' in page.locator('.nk-chapter-actions .is-primary').inner_text()
                after = page.locator('.nk-topic-options').inner_text()
                assert all(line in after for line in options_before.split('\n') if line.strip() and not line.strip().isdigit() and line.strip() not in ('Only unanswered',)), (options_before, after)
                states = page.evaluate("[...document.querySelectorAll('.nk-topic-cell')].slice(0,8).map(e=>e.dataset.s).join('')")
                assert states == 'ckwckcuu', states
                page.wait_for_timeout(300); page.screenshot(path=str(out/f'submit-attempted-topic-{tag}.png'), full_page=True)
                page.click('.nk-topic-leftoff'); page.wait_for_selector('.option')
                s = page.evaluate('QB.getState().activeSession')
                assert len(s['questionIds']) == total-6 and s['questionIds'][0] == tail_id and s['index'] == 0, s
                assert not errors, errors
                context.close()
        browser.close()
    print('SUBMIT_ATTEMPTED_BROWSER_OK cut=last_answer skipped=hollow_yellow tail_out_of_fsrs=true result=partial topic_continue=true widths=390,1280 themes=light,dark')


def main():
    from app_page import built_page
    web = ROOT/'build/web'
    html = built_page(web)
    assert 'NK_PRACTICE_SUBMIT_ATTEMPTED_V1_START' in html
    page = html.replace('  window.QB={', PROBE+'  window.QB={', 1).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            try:
                if self.path.split('?', 1)[0] in ('/', '/index.html'):
                    self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers(); self.wfile.write(page)
                else:
                    super().do_GET()
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    out = ROOT/'build/ui-checks'; out.mkdir(parents=True, exist_ok=True)
    try:
        run(f'http://127.0.0.1:{server.server_port}', out)
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
