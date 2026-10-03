#!/usr/bin/env python3
"""Exercise generated result UI, named mocks, repetition and aligned Insights."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PROBE = '''window.__nkAnalysisTest={questions:()=>nkAllStudyQuestions().filter(q=>nkQuestionPresentationFor(q).valid),model:()=>nkLearningModel(),labels:()=>nkLearningPeriodLabels(nkLearningModel())};\n'''
SEED = r'''() => {
 const state=window.QB.getState(),qs=window.__nkAnalysisTest.questions(),groups=['Anatomy','Biochemistry','Physiology'].map(s=>qs.filter(q=>q.subject===s&&q.bank==='Marrow').slice(0,7));
 const chosen=groups.flat().slice(0,20),ids=chosen.map(q=>String(q.id));
 const make=(id,correct,wrong,kind)=>({id,kind,title:'Mixed subjects mock 01',questionIds:ids,answers:Object.fromEntries(chosen.slice(0,correct+wrong).map((q,i)=>[q.id,i<correct?Number(q.correctOption):Number(q.correctOption)%q.options.length+1])),correct,incorrect:wrong,unattempted:20-correct-wrong,total:20,attempted:correct+wrong,totalTimeMs:1694000,questionTimes:Object.fromEntries(chosen.map((q,i)=>[q.id,[18000,42000,84000,144000,185000][i%5]])),createdAt:Date.now()-10000,originRoute:'tests'});
 const test=make('analysis-fixture',15,4,'exam'),low=make('analysis-low',2,1,'exam');
 const q=chosen[0],practice={...make('analysis-practice',2,1,'practice'),title:q.chapter||'Practice',questionIds:ids.slice(0,3),answers:{[ids[0]]:Number(chosen[0].correctOption),[ids[1]]:Number(chosen[1].correctOption),[ids[2]]:Number(chosen[2].correctOption)%chosen[2].options.length+1},total:3,unattempted:0,originRoute:'topics'};
 state.tests=[test,low,practice];state.attempts={};state.savedMocks=[];
 const at=Date.now()-15000;for(let i=0;i<40;i++){const x=chosen[i%20];(state.attempts[x.id]??=[]).push({id:'align-'+i,selected:x.correctOption,correct:true,at:at-i*50,timeSpent:60000});}
 window.QB.saveState();window.QB.nav('result',test.id);return ids;
}'''


def main():
    baseline = '--capture-baseline' in sys.argv
    web = ROOT / 'build/web'
    html = (web / 'index.html').read_text()
    diagnostic = html.replace('  window.QB={', PROBE + '  window.QB={', 1).encode()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?', 1)[0] in ('/', '/index.html'):
                self.send_response(200);self.send_header('Content-Type', 'text/html');self.end_headers();self.wfile.write(diagnostic)
            else:
                super().do_GET()
        def log_message(self, *args):
            pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(web)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    output=ROOT/'build/ui-checks';output.mkdir(parents=True,exist_ok=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            for width,height in [(320,760),(390,844),(820,1180),(1194,834)]:
                context=browser.new_context(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
                page=context.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin,wait_until='domcontentloaded');page.wait_for_function('window.QB && window.__nkAnalysisTest')
                ids=page.evaluate(SEED)
                if not baseline:
                    assert page.locator('.nk-global-subject').count()==0
                    assert page.locator('.nk-global-header-v114').count()==0
                if baseline:
                    page.screenshot(path=str(output/f'analysis-before-{width}.png'),full_page=True)
                    page.evaluate("window.QB.nav('analytics')")
                    page.locator('.nk-li-donut-pair').screenshot(path=str(output/f'donuts-before-{width}.png'))
                    page.locator('.nk-li-bars').screenshot(path=str(output/f'bars-before-{width}.png'))
                    context.close();continue
                expect(page.get_by_role('heading',name='Test analysis',exact=True)).to_be_visible()
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),f'Result overflow at {width}'
                assert page.locator('.nk-result-percentages').inner_text().startswith('15 / 20')
                assert '79%' in page.locator('.nk-na-accuracy').inner_text()
                assert page.locator('.nk-na-outcome-counts .is-omitted').inner_text().endswith('Omitted')
                assert page.locator('.nk-na-summary').bounding_box()['y']<270
                page.screenshot(path=str(output/f'analysis-refined-{width}.png'),full_page=True)
                page.screenshot(path=str(output/f'analysis-refined-top-{width}.png'))
                totals=page.evaluate("[...document.querySelectorAll('.nk-na-row header b')].map(n=>n.innerText)")
                assert totals
                outcome_colors={'is-correct':'rgb(21, 153, 117)','is-incorrect':'rgb(212, 72, 99)','is-omitted':'rgb(219, 163, 58)'}
                for tone,color in outcome_colors.items():
                    for segment in page.locator(f'.nk-na-row-bar .{tone}').all():
                        assert segment.evaluate('(n)=>getComputedStyle(n).backgroundColor')==color
                        assert segment.evaluate('(n)=>getComputedStyle(n).opacity')=='1'
                assert page.locator('.nk-na-row-counts').count()==page.locator('.nk-na-row').count()
                # Read the final cascade: legacy gradient rules caused the unreadable CTA.
                review=page.get_by_role('button',name='Review Solutions',exact=True)
                assert review.evaluate('(n)=>getComputedStyle(n).color')=='rgb(255, 255, 255)'
                assert review.evaluate('(n)=>getComputedStyle(n).backgroundColor')=='rgb(73, 51, 148)'
                assert review.evaluate('(n)=>getComputedStyle(n).backgroundImage')=='none'
                page.get_by_role('button',name='Subject-wise',exact=True).click()
                expect(page.get_by_role('heading',name='Subject breakdown')).to_be_visible()
                assert page.locator('.nk-na-row').count()==3
                page.get_by_role('button',name='Topic-wise',exact=True).click()
                page.get_by_role('button',name='Within time',exact=True).click()
                assert page.locator('.nk-na-time-bars>div>b').all_text_contents()==['4','8','12','16','20']
                assert 'Running total' in page.locator('.nk-na-time-explanation').inner_text()
                page.get_by_role('button',name='Time ranges',exact=True).click()
                assert page.locator('.nk-na-time-bars>div>b').all_text_contents()==['4']*5
                assert 'Timing saved for 20 of 20' in page.locator('.nk-na-time-coverage').inner_text()
                page.evaluate("window.QB.nav('result','analysis-low')")
                assert '67%' in page.locator('.nk-na-accuracy').inner_text()
                assert '10%' in page.locator('.nk-na-summary .nk-na-ring').inner_text()
                assert page.locator('.nk-na-row-bar .is-omitted[style="width:100%"] ').count()>0
                page.screenshot(path=str(output/f'analysis-low-{width}.png'),full_page=True)
                page.evaluate("window.QB.nav('result','analysis-practice')")
                expect(page.get_by_role('heading',name='Practice analysis',exact=True)).to_be_visible()
                assert page.locator('.nk-global-subject').count()==0
                assert page.locator('.nk-global-header-v114').count()==0
                assert page.locator('.nk-cbt-analysis').count()==0
                assert page.get_by_role('button',name='Correct my misses').count()==1
                page.screenshot(path=str(output/f'analysis-practice-{width}.png'),full_page=True)
                page.evaluate("window.QB.nav('analytics')")
                for period in ['week','month','year']:
                    page.locator('#nk-li-period').select_option(period)
                    assert page.locator('.nk-li-outcomes h3').all_text_contents()==[f'This {period}',f'Previous {period}']
                    for key in page.locator('.nk-li-key').all_text_contents():
                        assert f'This {period}' in key and f'Previous {period}' in key
                    a,b=page.locator('.nk-li-donut').all()
                    assert abs(a.bounding_box()['y']-b.bounding_box()['y'])<1,'Donuts must align, including an empty prior period'
                    for button in page.locator('.nk-li-bars button').all():
                        pair=button.locator('.nk-li-bar-pair');bars=pair.locator('i:not([hidden])').all()
                        if not bars:continue
                        left=min(x.bounding_box()['x'] for x in bars);right=max(x.bounding_box()['x']+x.bounding_box()['width'] for x in bars)
                        label=button.locator('small').bounding_box()
                        assert abs((left+right)/2-(label['x']+label['width']/2))<1,'Visible bars must centre on labels'
                page.locator('#nk-li-period').select_option('week')
                page.locator('.nk-li-donut-pair').evaluate("n=>n.scrollIntoView({block:'center'})")
                page.locator('.nk-li-donut-pair').screenshot(path=str(output/f'donuts-refined-{width}.png'))
                page.locator('.nk-li-bars').evaluate("n=>n.scrollIntoView({block:'center'})")
                page.locator('.nk-li-bars').screenshot(path=str(output/f'bars-refined-{width}.png'))
                page.get_by_label('Previous week',exact=True).click()
                assert 'This week' not in page.locator('.nk-li-outcomes h3').first.inner_text()
                assert page.locator('.nk-li-outcomes h3').all_text_contents()==list(page.evaluate('window.__nkAnalysisTest.labels()').values())
                page.evaluate("window.QB.nav('result','analysis-fixture')")
                page.get_by_label('Rename test',exact=True).click();page.get_by_label('Test name',exact=True).fill('Biochemistry mock 01')
                page.get_by_role('button',name='Save name',exact=True).click()
                assert page.locator('.nk-na-name strong').inner_text()=='Biochemistry mock 01'
                page.get_by_role('button',name='Save as mock',exact=True).click()
                page.evaluate("window.QB.nav('tests')")
                expect(page.get_by_role('heading',name='Saved mocks')).to_be_visible()
                page.reload(wait_until='domcontentloaded');page.wait_for_function('window.QB')
                assert page.evaluate('window.QB.getState().savedMocks[0].questionIds')==ids
                page.locator('.nk-na-mock-row>button').first.click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                session=page.evaluate('window.QB.getState().activeSession')
                assert session['questionIds']==ids and not session['answers']
                page.evaluate('window.QB.getState().activeSession.startedAt-=1000')
                before=page.evaluate('JSON.stringify(window.QB.getState().activeSession)')
                assert page.evaluate('id=>window.QB.nkMockStart(id)',page.evaluate('window.QB.getState().savedMocks[0].id')) is False
                expect(page.get_by_role('heading',name='Timed test in progress',exact=True)).to_be_visible()
                assert page.evaluate('JSON.stringify(window.QB.getState().activeSession)')==before
                page.get_by_role('button',name='Cancel',exact=True).click()
                # Saved result remains intact while a repeat starts with a fresh timer.
                assert page.evaluate("window.QB.getState().tests.find(t=>t.id==='analysis-fixture').correct")==15
                page.evaluate("window.QB.submitExam(false)")
                page.wait_for_function("location.hash.startsWith('#result')")
                assert page.get_by_role('heading',name='Initial test vs retake').count()==1
                # A named builder draft can be saved without starting a session.
                page.evaluate("window.QB.nav('tests');window.QB.openTestBuilder();window.QB.nkCbtSetStep(3)")
                page.get_by_label('Mock name Optional',exact=True).fill('Weekend mock')
                page.get_by_role('button',name='Save mock',exact=True).click()
                expect(page.get_by_role('heading',name='Saved mocks')).to_be_visible()
                assert page.evaluate('window.QB.getState().activeSession') is None
                assert page.evaluate('window.QB.getState().savedMocks.at(-1).name')=='Weekend mock'
                page.screenshot(path=str(output/f'named-mocks-{width}.png'))
                page.evaluate("window.QB.nav('dashboard')")
                assert page.locator('.nk-global-header-v114').count()==1
                assert not errors,errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print('REFINED_ANALYSIS_BROWSER_OK widths=320,390,820,1194 score=true accuracy=true tabs=true omitted=true timing=true named_mocks=true exact_repeat=true aligned_charts=true' if not baseline else 'ANALYSIS_BASELINE_CAPTURED')


if __name__=='__main__':
    main()
