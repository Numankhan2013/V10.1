#!/usr/bin/env python3
"""Check real visual roles, study/footer alignment and responsive long content."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import threading
from playwright.sync_api import sync_playwright
from verify_learning_insights_browser import PROBE, SEED

ROOT = Path(__file__).resolve().parents[1]


def contrast(a, b):
    def luminance(color):
        rgb = [int(v)/255 for v in re.findall(r'[\d.]+', color)[:3]]
        linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        return sum(v*w for v, w in zip(linear, [.2126,.7152,.0722]))
    a, b = sorted([luminance(a), luminance(b)])
    return (b+.05)/(a+.05)


PAIRS = '''selector => [...document.querySelectorAll(selector)].filter(n=>n.getClientRects().length).map(n=>{
 const c=getComputedStyle(n);let parent=n,bg=c.backgroundColor;
 while(bg==='rgba(0, 0, 0, 0)'&&parent.parentElement){parent=parent.parentElement;bg=getComputedStyle(parent).backgroundColor;}
 return {text:n.textContent.trim().slice(0,65),color:c.color,bg};
})'''


def main():
    web = ROOT/'build/web'
    html = (web/'index.html').read_text()
    assert 'id="nk-visual-refinement-v1"' in html
    probe = PROBE+'window.__visualQuestion=()=>nkCurrentQuestion();\n'
    diagnostic = html.replace('  window.QB={', probe+'  window.QB={', 1).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?',1)[0] in ('/','/index.html'):
                self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers()
                try:
                    self.wfile.write(diagnostic)
                except (BrokenPipeError,ConnectionResetError):
                    pass
            else:
                super().do_GET()

        def log_message(self,*_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(web)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    output = ROOT/'build/ui-checks';output.mkdir(exist_ok=True)
    report = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width,height in [(320,844),(390,844),(820,1180),(1194,834)]:
                context = browser.new_context(viewport={'width':width,'height':height},has_touch=True,is_mobile=True,service_workers='block')
                page = context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin,wait_until='domcontentloaded');page.wait_for_function('QB?.getState');page.evaluate(SEED)
                saved = page.evaluate('JSON.stringify(QB.getState())')
                min_ratio = 21
                for route,selectors in [
                    ('dashboard','.nk-home-focus-action,.nk-home-focus-card p,.nk-study-set-main small'),
                    ('topics','.nk-topic-copy strong,.nk-topic-copy small'),
                    ('fsrs','.nk-fsrs-subject-card small,.nk-v3-primary'),
                    ('tests','.nk-page-head h1,.nk-v3-primary'),
                    ('analytics','.nk-li-period-note,.nk-li-stats article>small,.nk-li-topic small'),
                    ('more','.nk-page-head h1')]:
                    page.evaluate('(r)=>QB.nav(r)',route)
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(route,width)
                    pairs=page.evaluate(PAIRS,selectors);assert pairs,(route,selectors)
                    assert page.locator('.bottom-nav .nk-product-icon').count()==5,('shared navigation glyphs missing',route)
                    assert page.locator('.bottom-nav svg:not([aria-hidden="true"])').count()==0
                    for pair in pairs:
                        ratio=contrast(pair['color'],pair['bg']);min_ratio=min(min_ratio,ratio)
                        assert ratio>=4.5,(route,width,ratio,pair)
                    page.screenshot(path=str(output/f'visual-{route}-{width}.png'))
                assert page.evaluate('JSON.stringify(QB.getState())') == saved,'visual navigation changed study data'
                page.evaluate('QB.startAllPractice()');page.wait_for_selector('.option-list button')
                geometry=page.evaluate('''()=>{
                  const q=document.querySelector('.question-text').getBoundingClientRect(),f=document.querySelector('.fixed-actions-inner').getBoundingClientRect();
                  return {q:{x:q.x,w:q.width},f:{x:f.x,w:f.width},background:getComputedStyle(document.body).backgroundColor};
                }''')
                assert geometry['q']['w']<=740.5,geometry
                assert abs(geometry['q']['x']-geometry['f']['x'])<=1,geometry
                assert abs(geometry['q']['w']-geometry['f']['w'])<=1,geometry
                assert geometry['background']=='rgb(255, 254, 253)',geometry
                for pair in page.evaluate(PAIRS,'.question-text,.option-text,.nk-session-footer .primary-btn'):
                    assert contrast(pair['color'],pair['bg'])>=4.5,pair
                q=page.evaluate('__visualQuestion()');correct=int(q['correctOption'])
                assert page.locator('.nk-grid-trigger .nk-icon-tone rect').count()==4
                assert page.locator('.bookmark-toggle .nk-icon-tone path').count()==2
                page.locator('.option-list button').nth(correct-1).click()
                assert page.locator('.option.correct').count()==1
                dock=page.locator('.nk-fsrs-rating');assert dock.count()==1
                d=dock.bounding_box();assert abs(d['x']-geometry['q']['x'])<=1,(d,geometry)
                assert abs(d['width']-geometry['q']['w'])<=1,(d,geometry)
                page.screenshot(path=str(output/f'visual-practice-{width}.png'))
                # Diagnostic DOM-only long copy and larger text expose footer or
                # option clipping without mutating the stored question bank.
                page.locator('.option-text').first.evaluate("n=>n.textContent='A long scientific answer with multiple qualifiers and clinically relevant details. '.repeat(8)")
                page.add_style_tag(content='.nk-v114-session .option-text{font-size:24px!important}')
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                page.locator('.nk-study-support').evaluate("n=>n.insertAdjacentHTML('beforeend','<p id=visual-end>End of long explanation</p>')")
                page.locator('#visual-end').scroll_into_view_if_needed()
                page.evaluate('scrollTo(0,document.documentElement.scrollHeight)')
                end=page.locator('#visual-end').bounding_box();footer=page.locator('.nk-session-footer').bounding_box()
                assert end['y']+end['height'] <= footer['y'], ('footer obscures explanation',width,end,footer)
                assert not errors,errors
                report.append({'width':width,'min_secondary_contrast':round(min_ratio,2),'reading_footer_aligned':True,'long_copy_clear':True})
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print('VISUAL_REFINEMENT_BROWSER_OK '+json.dumps(report))


if __name__ == '__main__':
    main()
