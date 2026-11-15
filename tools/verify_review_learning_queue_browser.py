#!/usr/bin/env python3
"""Due review in the real app: Again brings the card back in the same session as
Round 2, and Hard/Good/Easy moves on by itself (review_learning_queue.js).

Two due cards: the first is missed (no advance: the explanation waits for Next),
the second is answered and rated Good, which advances after the pressed beat to
the missed card (due inside the 20 min learn-ahead at the end of the set) in its
own row as Round 2; rating it Good opens the end-of-session sheet, whose grid
marks the round; Finish saves each question once.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from app_page import built_page

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''window.__rlq={
 questions:()=>nkFsrsAllQuestions().filter(q=>q.subject==='Biochemistry'&&q.bank==='PrepLadder'&&nkQuestionPresentationFor(q).valid).slice(0,2).map(q=>({id:String(q.id),correctOption:Number(q.correctOption),count:q.options.length}))
};
'''
SEED = '''(qs)=>{
 const s=QB.getState(),now=Date.now();
 Object.assign(s,{attempts:{},bookmarks:{},tests:[],activeSession:null,reviews:{},fsrsReviewEligible:{},fsrsRatingRevisions:{},notStudied:{},normalPracticeCheckpoints:[],normalPracticeCheckpoint:null,
  fsrsPreferences:{desiredRetention:.9,dailyCap:150,maximumInterval:365,learningInSession:'due',advanceAfterRating:true}});
 qs.forEach(q=>{s.attempts[q.id]=[{id:'rlq-seed-'+q.id,selected:q.correctOption%q.count+1,correct:false,at:now-3*86400000,reviewedAt:now-3*86400000,source:'practice',rating:1}];});
 QB.saveState();return QB.nkStartRevisionQueue('due');
}'''


def main():
    web = ROOT/'build/web'
    html = built_page(web)
    assert 'NK_REVIEW_LEARNING_QUEUE_V1_START' in html
    diagnostic = html.replace('  window.QB={', PROBE+'  window.QB={', 1).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            try:
                if self.path.split('?', 1)[0] in ('/', '/index.html'):
                    self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers(); self.wfile.write(diagnostic)
                else:
                    super().do_GET()
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    out = ROOT/'build/ui-checks'; out.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width, height in [(390, 844), (820, 1180)]:
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block', has_touch=True, is_mobile=width < 600)
                page = context.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
                page.route('**/*', lambda r: r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin+'/#dashboard', wait_until='domcontentloaded'); page.wait_for_function('window.QB?.getState && window.__rlq')
                qs = page.evaluate('window.__rlq.questions()'); assert len(qs) == 2
                page.evaluate(SEED, qs); page.wait_for_selector('.option')
                session = page.evaluate('QB.getState().activeSession')
                assert session['revisionQueueKind'] == 'due' and sorted(session['questionIds']) == sorted(q['id'] for q in qs), session
                by_id = {q['id']: q for q in qs}; first, second = session['questionIds']
                active = lambda: page.evaluate('QB.getState().activeSession')

                # 1. Miss the first card: Again, queued; no advance.
                q = by_id[first]; page.locator('.option').nth(q['correctOption'] % q['count']).click()
                page.wait_for_function('id=>QB.getState().activeSession.learningQueue?.[id]', arg=first)
                page.wait_for_timeout(700); assert active()['index'] == 0, 'a wrong answer waits for Next'
                assert page.evaluate('id=>QB.getState().reviews[id].state', first) in (1, 3)
                page.locator('.nk-session-footer').get_by_role('button', name='Next', exact=True).click()
                page.wait_for_function('QB.getState().activeSession.index===1')

                # 2. Answer the second, rate Good: the pressed beat, then the missed card as Round 2.
                q = by_id[second]; page.locator('.option').nth(q['correctOption']-1).click()
                dock = page.locator('.nk-fsrs-rating'); dock.wait_for()
                dock.get_by_role('button', name='Good', exact=True).click()
                page.wait_for_function('id=>{const s=QB.getState().activeSession;return s.index===0&&s.roundHistory?.[id]?.length===1;}', arg=first, timeout=5000)
                badge = page.locator('.nk-rlq-round'); badge.wait_for(); assert badge.inner_text().strip() == 'Round 2'
                s = active(); assert first not in s['answers'] and not s['submitted'].get(first), 'the new round starts unanswered'
                assert s['questionIds'] == session['questionIds'], 'membership unchanged'
                page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
                page.screenshot(path=str(out/f'review-learning-round-{width}.png'))

                # 3. Answer Round 2 and rate Good: nothing left, so the end-of-session sheet opens.
                q = by_id[first]; page.locator('.option').nth(q['correctOption']-1).click()
                dock = page.locator('.nk-fsrs-rating'); dock.wait_for()
                dock.get_by_role('button', name='Good', exact=True).click()
                sheet = page.locator('#nk-session-review'); sheet.wait_for(timeout=5000)
                assert sheet.locator('.nk-rlq-round-dot').count() == 1, 'the grid marks the reopened question'
                page.screenshot(path=str(out/f'review-learning-sheet-{width}.png'))
                rounds = page.evaluate('id=>QB.getState().attempts[id].filter(a=>a.source==="fsrs-review").length', first)
                assert rounds == 2, 'each round is an FSRS attempt'
                sheet.get_by_role('button', name='Finish session', exact=True).click()
                page.wait_for_function("location.hash.startsWith('#result')")
                t = page.evaluate('QB.getState().tests.at(-1)')
                assert sorted(t['questionIds']) == sorted(session['questionIds']) and t['total'] == 2 and t['correct'] == 2, t
                assert not errors, errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print('REVIEW_LEARNING_QUEUE_BROWSER_OK again_returns=true round_badge=true advance=true end_sheet=true counted_once=true')


if __name__ == '__main__':
    main()
