#!/usr/bin/env python3
"""Exercise period-aware analytics in the real generated six-bank app."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PROBE = 'window.__nkLearningTest={model:()=>nkLearningModel(),questions:()=>nkAllStudyQuestions().filter(q=>nkQuestionPresentationFor(q).valid)};\n'
SEED = r'''() => {
 const state=window.QB.getState(),qs=window.__nkLearningTest.questions(),now=new Date(),today=new Date(now);today.setHours(0,0,0,0);
 const groups=['Anatomy','Physiology','Biochemistry'].map(subject=>{const a=qs.filter(q=>q.subject===subject&&q.bank==='PrepLadder').slice(0,80),b=qs.filter(q=>q.subject===subject&&q.bank==='Marrow').slice(0,80);return a.flatMap((q,i)=>[q,b[i]]).filter(Boolean);});
 state.attempts={};state.tests=[];state.fsrsRatingRevisions={};state.reviews={};state.studyModules=[];
 let count=0;
 for(let day=0;day<75;day++){
  const date=new Date(today);date.setDate(date.getDate()-day);date.setHours(day===0?Math.max(0,now.getHours()-1):11,0,0,0);
  if(day===0&&date>now)continue;
  const n=day%7===6?5:day<7?36:day<14?25:12;
  for(let i=0;i<n;i++){
   const q=groups[i%3][(day*5+i)%120],id=String(q.id),at=+date+i*1000,correct=(i+day)%5!==0,source=i%4===0?'spaced-review':'practice';
   (state.attempts[id]??=[]).push({id:'fixture-'+count++,selected:correct?q.correctOption:q.correctOption%q.options.length+1,correct,at,reviewedAt:at,timeSpent:(55+i%8*13)*1000,source,sessionId:'fixture-'+day,rating:correct?3:1});
   state.reviews[id]={schemaVersion:2,schedulerVersion:'fsrs6',state:2,stability:8,difficulty:4,repetitions:3,lapses:1,due:+today+(i%8-2)*86400000,nextReviewAt:+today+(i%8-2)*86400000,lastReview:at};
  }
 }
 const sample=groups[0].slice(0,12),ids=sample.map(q=>String(q.id)),answers=Object.fromEntries(sample.map(q=>[q.id,q.correctOption]));
 state.studyModules=Array.from({length:4},(_,i)=>({id:'module-'+i,name:['Thorax essentials','Respiratory revision','Biochemistry recall','Weekend PYQs'][i],subjectIds:['Anatomy'],scopeIds:[],topicIds:[],questionPoolType:'all',collectionFilter:'all',questionIds:ids,totalQuestions:ids.length,completedQuestionIds:i<2?ids:ids.slice(0,4),currentPosition:3,answers,submitted:Object.fromEntries(ids.map(id=>[id,true])),questionTimes:{},createdAt:+today-21*86400000,lastOpenedAt:+today,isCompleted:i<2,completedAt:i<2?+today-i*86400000:null,resultTestId:i<2?'module-result-'+i:null}));
 for(let i=0;i<2;i++)state.tests.push({id:'module-result-'+i,title:state.studyModules[i].name,kind:'practice',studyModuleId:'module-'+i,sessionId:'module-session-'+i,questionIds:ids,answers,questionTimes:Object.fromEntries(ids.map(id=>[id,60000])),correct:10,incorrect:2,total:12,attempted:12,unattempted:0,totalTimeMs:720000,createdAt:+today-i*86400000});
 // Distinct missed IDs, cross-bank evidence and an explicit undo/rating edit.
 const q=groups[0][0];(state.attempts[q.id]??=[]).push({id:'recalled',correct:true,selected:q.correctOption,source:'spaced-review',at:+today+1000,timeSpent:60000});
 state.fsrsRatingRevisions[q.id]=[{id:'edited',isRatingRevision:true,ratingOf:'recalled',rating:4,at:Date.now()}];
 window.QB.saveState();window.QB.nav('analytics');
}'''


def main():
    web = ROOT / 'build/web'
    html = (web / 'index.html').read_text()
    assert 'NK_LEARNING_INSIGHTS_V1_START' in html
    diagnostic = html.replace('  window.QB={', PROBE + '  window.QB={', 1).encode()
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?', 1)[0] in ('/', '/index.html'):
                self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers(); self.wfile.write(diagnostic)
            else:
                super().do_GET()
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    output = ROOT / 'build/ui-checks'; output.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for width, height in [(320, 760), (390, 844), (820, 1180), (1194, 834)]:
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block', reduced_motion='reduce')
                page = context.new_page(); errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.route('**/*', lambda r: r.continue_() if r.request.url.startswith(origin) else r.abort())
                page.goto(origin + '/#analytics', wait_until='domcontentloaded')
                page.wait_for_function('window.__nkLearningTest && window.QB')
                expect(page.get_by_role('heading', name='Insights', exact=True)).to_be_visible()
                assert page.locator('.nk-li-stats article').count() == 5
                assert page.locator('[data-metric="Accuracy"]>b').inner_text() == '—'
                assert page.get_by_role('heading', name='Your study map').count() == 0
                assert page.get_by_role('heading', name='Topics to revisit').count() == 0
                expect(page.get_by_role('heading', name='Activity', exact=True)).to_be_visible()
                assert page.locator('.nk-li-year-grid button').count() >= 365
                page.screenshot(path=str(output / f'learning-insights-empty-{width}.png'), full_page=True)
                page.evaluate(SEED)
                model = page.evaluate('window.__nkLearningTest.model()')
                assert model['current']['attempts'] > 0
                assert page.locator('[data-metric="Questions practised"]>b').inner_text().replace(',', '') == str(model['current']['attempts'])
                assert model['current']['reviews'] < model['current']['attempts']
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), f'Horizontal overflow at {width}'
                assert page.locator('.nk-li-card').count() == 9
                assert page.locator('.nk-li-year-activity').bounding_box()['y'] < page.locator('.nk-li-stats').bounding_box()['y']
                page.get_by_label('Activity year', exact=True).select_option(str(__import__('datetime').datetime.now().year))
                assert page.locator('.nk-li-year-grid button').count() >= 365
                page.get_by_label('Activity year', exact=True).select_option('rolling')
                page.screenshot(path=str(output / f'learning-insights-week-{width}.png'), full_page=True)
                page.locator('.nk-li-year-activity').screenshot(path=str(output / f'learning-insights-heatmap-{width}.png'))
                page.screenshot(path=str(output / f'learning-insights-top-{width}.png'))
                tile = page.locator('.nk-li-year-grid .is-today')
                assert tile.bounding_box()['height'] <= 22, 'Calendar tiles must override generic 44px button height'
                original_style = tile.get_attribute('style')
                page.evaluate("""() => {const state=window.QB.getState(),q=window.__nkLearningTest.questions()[0],d=new Date();d.setDate(d.getDate()-7);d.setHours(10,0,0,0);for(let i=0;i<200;i++)(state.attempts[q.id]??=[]).push({id:'peak-'+i,correct:true,selected:q.correctOption,at:+d+i,timeSpent:0});window.QB.saveState();window.QB.nav('analytics');}""")
                assert page.locator('.nk-li-year-grid .is-today').get_attribute('style') != original_style, 'A new high day must rescale earlier days'
                assert '30+' not in page.locator('.nk-li-year-key').inner_text()

                page.locator('.nk-li-bars button:not(:disabled)').first.click()
                assert 'Previous:' in page.locator('.nk-li-bin-readout').inner_text()
                page.locator('.nk-li-year-grid button:not(:disabled)').last.click()
                assert 'correct' in page.locator('#nk-li-year-detail').inner_text()
                page.get_by_role('button', name='Top performing', exact=True).click()
                assert page.get_by_role('button', name='Top performing', exact=True).get_attribute('aria-pressed') == 'true'
                for period, bars in [('month', 5), ('year', 12), ('week', 7)]:
                    page.locator('#nk-li-period').select_option(period)
                    model = page.evaluate('window.__nkLearningTest.model()')
                    assert page.locator('.nk-li-bars button').count() == len(model['bins'])
                    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                    assert 'NaN' not in page.locator('#nk-li-content').inner_text()
                    page.get_by_role('button', name=f'Previous {period}', exact=True).click()
                    assert not page.get_by_role('button', name=f'Next {period}', exact=True).is_disabled()
                    page.get_by_role('button', name='Today', exact=True).click()
                    assert page.get_by_role('button', name=f'Next {period}', exact=True).is_disabled()
                page.get_by_label('Insights subject', exact=True).select_option('Anatomy')
                page.get_by_label('Insights bank', exact=True).select_option('Marrow')
                scoped = page.evaluate('window.__nkLearningTest.model()')
                assert scoped['current']['attempts'] < model['current']['attempts']
                assert all(t['subject'] == 'Anatomy' and t['bank'] == 'Marrow' for t in scoped['topicRows'])
                page.locator('.nk-li-topic').first.click()
                page.wait_for_function("location.hash.startsWith('#chapter/')")
                page.evaluate("window.QB.nav('analytics')")
                page.get_by_role('button', name='Explore FSRS', exact=False).click()
                expect(page.get_by_role('heading', name='FSRS Review', exact=True)).to_be_visible()
                page.evaluate("window.QB.nav('analytics')")
                page.get_by_label('Insights subject', exact=True).select_option('')
                page.reload(wait_until='domcontentloaded')
                page.wait_for_function('window.__nkLearningTest && window.QB')
                assert page.evaluate('window.__nkLearningTest.model().current.attempts') == model['current']['attempts']
                assert page.locator('.bottom-nav button').count() == 5
                assert not errors, errors
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print('LEARNING_INSIGHTS_BROWSER_OK viewports=320,390,820,1194 periods=true comparisons=true scopes=true charts=true drilldowns=true reload=true empty=true no_overflow=true full_year=true relative_intensity=true')


if __name__ == '__main__':
    main()
