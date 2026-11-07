#!/usr/bin/env python3
"""Study plan release: Today on Home, exam settings, scheduled mocks (doors, missed = 0, make-up,
attendance, schedule a saved mock), the result question strip, mock insights, and the submit skeleton."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, expect
from app_page import built_page

ROOT = Path(__file__).resolve().parents[1]
PROBE = 'window.__nkPlan={questions:()=>nkAllStudyQuestions().filter(q=>nkQuestionPresentationFor(q).valid)};\n'
SEED = r'''() => {
 const state=window.QB.getState(),qs=window.__nkPlan.questions().filter(q=>q.subject==='Physiology').slice(0,12),ids=qs.map(q=>String(q.id)),now=Date.now();
 const answers=Object.fromEntries(qs.slice(0,9).map((q,i)=>[q.id,i<6?Number(q.correctOption):Number(q.correctOption)%q.options.length+1]));
 const test={id:'plan-test',title:'Physiology timed test',questionIds:ids,answers,questionTimes:Object.fromEntries(ids.map(id=>[id,30000])),correct:6,incorrect:3,unattempted:3,total:12,attempted:9,totalTimeMs:360000,createdAt:now-3600e3,originRoute:'tests',marking:{correct:4,wrong:-1,blank:0},secondsPerQuestion:63};
 state.tests=[test];state.savedMocks=[{id:'saved-1',name:'Saved physiology mock',questionIds:ids,createdAt:now,updatedAt:now}];
 state.scheduledMocks=[
  {id:'missed-1',name:'Missed mock',questionIds:ids,at:now-3*3600e3,createdAt:now-86400e3,marking:{correct:4,wrong:-1,blank:0},seconds:63},
  {id:'open-1',name:'Doors open mock',questionIds:ids,at:now-5*60e3,createdAt:now-86400e3,marking:{correct:1,wrong:0,blank:0},seconds:60},
  {id:'late-1',name:'Too late mock',questionIds:ids,at:now-20*60e3,createdAt:now-86400e3,marking:{correct:1,wrong:0,blank:0},seconds:60}];
 window.QB.saveState();return ids;
}'''


def main():
    web = ROOT / 'build/web'
    html = built_page(web).replace('  window.QB={', PROBE + '  window.QB={', 1).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?', 1)[0] in ('/', '/index.html'):
                self.send_response(200); self.send_header('Content-Type', 'text/html'); self.end_headers(); self.wfile.write(html)
            else:
                super().do_GET()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for width, height in [(390, 844), (1194, 834)]:
                context = browser.new_context(viewport={'width': width, 'height': height}, service_workers='block', reduced_motion='reduce')
                page = context.new_page(); errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(origin + '/index.html#dashboard', wait_until='domcontentloaded')
                page.wait_for_function('window.QB && window.__nkPlan')
                ids = page.evaluate(SEED)
                page.evaluate("window.QB.nav('tests')")
                # Doors: 5 minutes late is still open; 20 minutes late is missed and scored 0, like the 3-hour miss.
                expect(page.locator('.nk-sched-ticket.is-open')).to_have_count(1)
                expect(page.locator('.nk-sched-ticket.is-open')).to_contain_text('Doors close')
                expect(page.locator('.nk-sched-ticket.is-missed')).to_have_count(2)
                missed = page.evaluate("window.QB.getState().tests.filter(t=>t.missed).map(t=>[t.scheduledMockId,t.correct,t.total])")
                assert sorted(m[0] for m in missed) == ['late-1', 'missed-1'], missed
                assert all(m[1] == 0 and m[2] == len(ids) for m in missed), missed
                # Recording is idempotent across renders.
                page.evaluate("window.QB.nav('dashboard')"); page.evaluate("window.QB.nav('tests')")
                assert page.evaluate("window.QB.getState().tests.filter(t=>t.missed).length") == 2
                expect(page.locator('.nk-sched-attend')).to_contain_text('Kept 0 of 2')
                # Save a booked paper as a mock from its ticket.
                # This paper is already a saved mock, so its ticket shows it as saved instead of saving a duplicate.
                expect(page.locator('.nk-sched-ticket.is-open .nk-sched-save')).to_be_disabled()
                page.evaluate("window.QB.getState().savedMocks=[];window.QB.saveState();window.QB.nav('dashboard');window.QB.nav('tests')")
                page.locator('.nk-sched-ticket.is-open .nk-sched-save').click()
                assert page.evaluate("window.QB.getState().savedMocks.map(m=>m.questionIds.length)") == [len(ids)]
                page.evaluate("(()=>{const m=window.QB.getState().savedMocks[0];m.name='Saved physiology mock';window.QB.saveState()})()")
                # Home carries the make-up until it is sat.
                page.evaluate("window.QB.nav('dashboard')")
                expect(page.locator('.nk-sched-makeup')).to_have_count(1)
                page.locator('.nk-sched-makeup button').click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                session = page.evaluate("(()=>{const s=window.QB.getState().activeSession;return {makeup:s.makeupFor,n:s.questionIds.length,marking:s.marking}})()")
                assert session['makeup'] in ('late-1', 'missed-1') and session['n'] == len(ids), session
                page.evaluate("window.QB.submitExam(false)")
                page.wait_for_function("location.hash.startsWith('#result/')")
                made = page.evaluate("window.QB.getState().tests.filter(t=>t.makeupFor).length")
                assert made == 1, made
                # The result strip: one cell per question, a tap opens that question's solution.
                page.evaluate("window.QB.nav('result','plan-test')")
                expect(page.get_by_role('heading', name='Test analysis', exact=True)).to_be_visible()
                cells = page.locator('.nk-rs-strip button')
                expect(cells).to_have_count(len(ids))
                assert page.locator('.nk-rs-strip button.is-correct').count() == 6
                assert page.locator('.nk-rs-strip button.is-incorrect').count() == 3
                cells.nth(4).click()
                page.wait_for_function("window.QB.getState().activeSession?.mode==='review'")
                assert page.evaluate("(()=>{const s=window.QB.getState().activeSession;return String(s.questionIds[s.index])})()") == ids[4]
                page.evaluate("window.QB.endReview?window.QB.endReview():window.QB.nav('tests')")
                # Mock insights: a point per timed test (missed ones included), readable by keyboard.
                page.evaluate("window.QB.nav('analytics')")
                chart = page.locator('.nk-mock-in-chart')
                expect(chart).to_be_visible()
                n = page.evaluate("document.querySelectorAll('.nk-mock-in-dots i').length")
                assert n == page.evaluate("window.QB.getState().tests.filter(t=>t.kind!=='practice'&&t.total>0).length"), n
                assert page.locator('.nk-mock-in-dots i.is-missed').count() == 2
                chart.focus(); page.keyboard.press('ArrowLeft')
                expect(page.locator('.nk-mock-in-tip')).to_contain_text('%')
                page.locator('.nk-mock-in-toggle button', has_text='Marks').click()
                expect(page.locator('.nk-mock-in-toggle button[aria-pressed="true"]')).to_have_text('Marks')
                # Schedule a saved mock from its details sheet.
                page.evaluate("window.QB.nav('tests')")
                page.evaluate("window.QB.nkMockOpen(window.QB.getState().savedMocks[0].id)")
                page.locator('#nk-mock-sheet .nk-sched-open').click()
                expect(page.locator('#nk-sched-sheet')).to_be_visible()
                expect(page.locator('#nk-sched-sheet')).to_contain_text('Saved physiology mock')
                page.locator('#nk-sched-confirm').click()
                booked = page.evaluate("window.QB.getState().scheduledMocks.filter(m=>m.name==='Saved physiology mock').map(m=>m.questionIds.length)")
                assert booked == [len(ids)], booked
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), f'overflow at {width}'
                assert not errors, errors
                context.close()
            # Submit opens a skeleton of the result in the next frame, never a busy label.
            context = browser.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
            page = context.new_page()
            page.goto(origin + '/index.html#dashboard', wait_until='domcontentloaded')
            page.wait_for_function('window.QB && window.__nkPlan')
            page.evaluate("""()=>{const qs=window.__nkPlan.questions().filter(q=>q.subject==='Anatomy').slice(0,3);window.QB.getState().tests=[];window.QB.saveState();window.QB.openMultiSubjectTestBuilder();window.QB.nkCbtSetStep(2);window.QB.nkCbtSetStep(3);window.QB.nkCbtSetCount(3);window.QB.nkCbtStart();}""")
            page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
            page.evaluate("window.QB.selectExam(1)")
            page.evaluate("window.QB.openSessionReview()")
            page.evaluate("""()=>{window.__skel=false;new MutationObserver(()=>{if(document.getElementById('nkg-result-skel'))window.__skel=true}).observe(document.body,{childList:true})}""")
            page.locator('#nk-session-review button[onclick*="__sessionReviewSubmit"]').click()
            page.wait_for_function("location.hash.startsWith('#result/')")
            assert page.evaluate('window.__skel'), 'submit must show the result skeleton'
            page.wait_for_function("!document.getElementById('nkg-result-skel')")
            assert page.locator('button[data-nkg-busy]').count() == 0
            context.close()
            browser.close()
    finally:
        server.shutdown()
    print('STUDY_PLAN_BROWSER_OK')


if __name__ == '__main__':
    main()
