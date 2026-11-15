#!/usr/bin/env python3
"""Due review in the real app: learning rounds (review_learning_queue.js).

Three due cards: the first is missed (Again; no advance, the explanation waits for
Next), the other two are answered and rated Good, which advances. After the last
card, Round 2 opens with only the missed card, fresh: the counter reads 1 / 1 with a
"Round 2" badge inside it, and the back button, flag, bookmark and grid stay on the
header row (checked by layout at 360, 390, 430 px and the run width, light and dark).
The session sheet lists only the Round 2 card. Bookmark and flag work in Round 2; a
reload keeps the round. Rating Round 2 Good opens the sheet; Finish saves each
question once, by its round 1 answer, and FSRS keeps both rounds.
Runs at 390 px and 1280 px, light and dark; screenshots go to build/ui-checks.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from app_page import built_page

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''window.__rlq={
 questions:()=>nkFsrsAllQuestions().filter(q=>q.subject==='Biochemistry'&&q.bank==='PrepLadder'&&nkQuestionPresentationFor(q).valid).slice(0,3).map(q=>({id:String(q.id),correctOption:Number(q.correctOption),count:q.options.length}))
};
'''
SEED = '''(qs)=>{
 const s=QB.getState(),now=Date.now();
 Object.assign(s,{attempts:{},bookmarks:{},tests:[],activeSession:null,reviews:{},fsrsReviewEligible:{},fsrsRatingRevisions:{},notStudied:{},normalPracticeCheckpoints:[],normalPracticeCheckpoint:null,
  fsrsPreferences:{desiredRetention:.9,dailyCap:150,maximumInterval:365,learningInSession:'end',advanceAfterRating:true}});
 qs.forEach(q=>{s.attempts[q.id]=[{id:'rlq-seed-'+q.id,selected:q.correctOption%q.count+1,correct:false,at:now-3*86400000,reviewedAt:now-3*86400000,source:'practice',rating:1}];});
 QB.saveState();return QB.nkStartRevisionQueue('due');
}'''
# Every header control on one row, inside the viewport, none overlapping another or the counter.
LAYOUT = '''()=>{
 const head=document.querySelector('.nk-v114-session > .nk-session-head');if(!head)return {ok:false,why:'no header'};
 const box=e=>{const r=e.getBoundingClientRect();return {l:r.left,r:r.right,t:r.top,b:r.bottom,cy:(r.top+r.bottom)/2};};
 const h=box(head),back=head.querySelector('.nk-session-back'),count=head.querySelector('.nk-session-count'),badge=count?.querySelector('.nk-rlq-round');
 const acts=[...head.querySelectorAll('.q-actions > button')];
 const items=[back,count,...acts].filter(Boolean).map(box),why=[];
 if(!badge)why.push('no badge in the counter');
 if(acts.length<3)why.push('expected flag, bookmark and grid, got '+acts.length);
 items.forEach((b,i)=>{if(b.t<h.t-1||b.b>h.b+1)why.push('item '+i+' outside the header row');if(Math.abs(b.cy-items[0].cy)>4)why.push('item '+i+' not on the back button row');if(b.l<-1||b.r>innerWidth+1)why.push('item '+i+' off screen');});
 for(let i=0;i<items.length;i++)for(let j=i+1;j<items.length;j++){const a=items[i],c=items[j];if(a.l<c.r-1&&c.l<a.r-1&&a.t<c.b-1&&c.t<a.b-1)why.push('items '+i+' and '+j+' overlap');}
 if(badge){const b=box(badge),c=box(count);if(b.r>c.r+1||b.l<c.l-1)why.push('badge spills out of the counter');}
 const eyebrow=document.querySelector('.question-card > .nkg-q-eyebrow');
 if(eyebrow){const e=box(eyebrow);if(e.t<h.b-1)why.push('the question eyebrow sits under the header');}
 return {ok:!why.length,why,count:count?.textContent.replace(/\\s+/g,' ').trim(),eyebrow:eyebrow?.textContent||''};
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
            for width, height in [(390, 844), (1280, 900)]:
                for scheme in ('light', 'dark'):
                    tag = f'{width}-{scheme}'
                    context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block', has_touch=True, is_mobile=width < 600, color_scheme=scheme)
                    page = context.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
                    page.route('**/*', lambda r: r.continue_() if r.request.url.startswith(origin) else r.abort())
                    page.goto(origin+'/#dashboard', wait_until='domcontentloaded'); page.wait_for_function('window.QB?.getState && window.__rlq')
                    assert page.evaluate('document.documentElement.getAttribute("data-nk-theme")') == scheme
                    qs = page.evaluate('window.__rlq.questions()'); assert len(qs) == 3
                    page.evaluate(SEED, qs); page.wait_for_selector('.option')
                    session = page.evaluate('QB.getState().activeSession')
                    assert session['revisionQueueKind'] == 'due' and sorted(session['questionIds']) == sorted(q['id'] for q in qs), session
                    by_id = {q['id']: q for q in qs}; first, second, third = session['questionIds']
                    active = lambda: page.evaluate('QB.getState().activeSession')
                    footer = page.locator('.nk-session-footer')

                    # 1. Miss the first card: Again, queued; no advance; Next moves on.
                    q = by_id[first]; page.locator('.option').nth(q['correctOption'] % q['count']).click()
                    page.wait_for_function('id=>QB.getState().activeSession.learningQueue?.[id]', arg=first)
                    page.wait_for_timeout(600); assert active()['index'] == 0, 'a wrong answer waits for Next'
                    footer.get_by_role('button', name='Next', exact=True).click()
                    page.wait_for_function('QB.getState().activeSession.index===1')

                    # 2. Answer the other two and rate Good: each advances; after the last, Round 2.
                    for qid, index in ((second, 1), (third, 2)):
                        page.wait_for_function('i=>QB.getState().activeSession.index===i', arg=index)
                        q = by_id[qid]; page.locator('.option').nth(q['correctOption']-1).click()
                        dock = page.locator('.nk-fsrs-rating'); dock.wait_for()
                        dock.get_by_role('button', name='Good', exact=True).click()
                    page.wait_for_function('id=>{const s=QB.getState().activeSession;return s.roundPass?.round===2&&s.questionIds[s.index]===id;}', arg=first, timeout=5000)
                    s = active()
                    assert s['roundPass'] == {'round': 2, 'ids': [first]}, s.get('roundPass')
                    assert first not in s['answers'] and not s['submitted'].get(first), 'Round 2 starts unanswered'
                    assert s['submitted'].get(second) and s['submitted'].get(third), 'round 1 answers stay'
                    assert s['questionIds'] == session['questionIds'], 'membership unchanged'
                    page.wait_for_function("getComputedStyle(document.querySelector('.page')).opacity==='1'")
                    page.wait_for_function("(document.querySelector('.question-card > .nkg-q-eyebrow')?.textContent||'').startsWith('Question 1 of 1')")
                    layout = page.evaluate(LAYOUT)
                    assert layout['ok'] and layout['count'] == '1 / 1Round 2', (tag, layout)
                    page.screenshot(path=str(out/f'review-learning-round2-{tag}.png'))
                    if width == 390:
                        for narrow in (360, 430):
                            page.set_viewport_size({'width': narrow, 'height': height}); page.wait_for_timeout(250)
                            layout = page.evaluate(LAYOUT); assert layout['ok'], (narrow, scheme, layout)
                            page.screenshot(path=str(out/f'review-learning-round2-{narrow}-{scheme}.png'))
                        page.set_viewport_size({'width': width, 'height': height}); page.wait_for_timeout(250)
                    assert footer.get_by_role('button', name='Previous').is_disabled(), 'first card of the round'

                    # 3. Bookmark and flag work in Round 2 (flag on, then off again).
                    page.locator('.nk-session-head .bookmark-toggle').first.click()
                    page.wait_for_function('id=>Boolean(QB.getState().bookmarks[id])', arg=first)
                    page.locator('.nk-session-head .nk-ns-toggle').first.click()
                    page.wait_for_function("document.querySelector('.nk-session-head .nk-ns-toggle')?.getAttribute('aria-pressed')==='true'")
                    page.locator('.nk-session-head .nk-ns-toggle').first.click()
                    page.wait_for_function("document.querySelector('.nk-session-head .nk-ns-toggle')?.getAttribute('aria-pressed')==='false'")
                    assert page.evaluate(LAYOUT)['ok'], 'header still in place after toggles'

                    # 4. The session sheet (grid button) lists only the Round 2 card.
                    page.locator('.nk-session-head .nk-grid-trigger').click()
                    sheet = page.locator('#nk-session-review'); sheet.wait_for()
                    assert sheet.locator('.nk-session-review-q').count() == 1, 'only the Round 2 card'
                    assert sheet.locator('.nk-session-review-summary span').inner_text().strip() == 'Round 2 · 1 card'
                    page.screenshot(path=str(out/f'review-learning-round2-sheet-{tag}.png'))
                    sheet.locator('.nk-session-review-q').first.click(); sheet.wait_for(state='detached')

                    # 5. A reload keeps Round 2.
                    page.reload(wait_until='domcontentloaded'); page.wait_for_function('window.QB?.getState && window.__rlq')
                    s = active(); assert s and s['roundPass'] == {'round': 2, 'ids': [first]}, s
                    if not page.locator('.nk-session-head').count():
                        page.evaluate('id=>QB.nkResumePracticeById(id)', s['id'])
                    page.wait_for_selector('.nk-session-head .nk-rlq-round')
                    assert page.evaluate(LAYOUT)['ok']

                    # 6. Answer Round 2 and rate Good: nothing left, so the sheet opens; Finish.
                    q = by_id[first]; page.locator('.option').nth(q['correctOption']-1).click()
                    dock = page.locator('.nk-fsrs-rating'); dock.wait_for()
                    dock.get_by_role('button', name='Good', exact=True).click()
                    sheet = page.locator('#nk-session-review'); sheet.wait_for(timeout=5000)
                    assert sheet.locator('.nk-session-review-q').count() == 1
                    rounds = page.evaluate('id=>QB.getState().attempts[id].filter(a=>a.source==="fsrs-review").length', first)
                    assert rounds == 2, 'each round is an FSRS attempt'
                    sheet.get_by_role('button', name='Finish session', exact=True).click()
                    page.wait_for_function("location.hash.startsWith('#result')")
                    t = page.evaluate('QB.getState().tests.at(-1)')
                    assert sorted(t['questionIds']) == sorted(session['questionIds']) and t['total'] == 3 and t['correct'] == 2, t
                    assert not errors, errors
                    context.close()
            browser.close()
    finally:
        server.shutdown()
    print('REVIEW_LEARNING_QUEUE_BROWSER_OK round2_only_due=true counter=1/1 header_row=true sheet=round_only bookmark_flag=true reload=true counted_by_round1=true widths=360,390,430,1280 themes=light,dark')


if __name__ == '__main__':
    main()
