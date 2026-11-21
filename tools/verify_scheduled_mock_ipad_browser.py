#!/usr/bin/env python3
"""Scheduled mocks on an iPad: the phone's bookings sync in and Home shows the same cards.

Owner report (2026-11-21): on the Android phone Home shows the scheduled-mock
ticket, the MAKE-UP OWED card and the attendance streak; on the iPad (same
account) none of it appears. Cause: bookings (`state.scheduledMocks`) were not
a sync kind, so they never left the phone (cross_device_sync.js now carries
kind `scheduledMocks`; docs in tools/test_scheduled_mocks_sync_v1.py).

This verifier drives the real sync envelopes between two browsers:
  phone  - Chromium, Android Chrome user agent, 390x844 (unchanged behaviour)
  iPad   - WebKit (Playwright's Safari engine) with the iPadOS Safari user agent,
           which reports a Mac, touch enabled, at 820x1180 and 1180x820.
The phone books an upcoming mock, misses one and keeps two; its outbox
envelopes (scheduledMocks + tests) are applied on the iPad through
nkApplyCloudEnvelope. The iPad must then show the upcoming ticket, MAKE-UP OWED
with the same text as the phone, the same attendance/streak on Tests, open the
make-up from "Sit it", refuse Abandon on a live scheduled mock, and book a mock
from the WebKit datetime-local input at the local time typed. The iPad's own
make-up stamp travels back and clears the phone's card.

  python3 tools/verify_scheduled_mock_ipad_browser.py            # build/web (CI)
  python3 tools/verify_scheduled_mock_ipad_browser.py --fixture  # source page with the bundled First Prof data only (local)
  --engine=chromium forces the iPad run onto Chromium when WebKit is not installed.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import sys
import threading
from playwright.sync_api import sync_playwright, expect
from app_page import built_page, app_page

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'app/src/main/assets'
IPAD_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15'
PHONE_UA = 'Mozilla/5.0 (Linux; Android 14; 23078PND5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
# Exposes the sync envelope path to the test (inside the app's scope, like the other verifiers' probes).
PROBE = r'''window.__nkSchedSync={
  out:()=>[...nkSchedSyncEntries().map(m=>nkEnvelope('scheduledMocks',m.id,m,nkSchedEntryAt(m))),...(state.tests||[]).filter(t=>t&&t.id).map(t=>nkEnvelope('tests',t.id,t,nkEntityTimestamp(t)))].map(e=>JSON.parse(JSON.stringify(e))),
  apply:list=>{nkCloudApplying=true;try{list.forEach(e=>nkApplyCloudEnvelope(e));}finally{nkCloudApplying=false;}saveState();render();return (state.scheduledMocks||[]).length;},
  changed:()=>nkSchedSyncEntries().filter(m=>{const e=nkEnvelope('scheduledMocks',m.id,m,1);return nkSyncMeta.localHashes['scheduledMocks/'+m.id]!==nkHash({deleted:false,payload:e.payload});}).map(m=>m.id),
  parse:v=>nkSchedParseLocal(v),
  questions:()=>nkAllStudyQuestions().filter(q=>nkQuestionPresentationFor(q).valid).slice(0,40).map(q=>String(q.id))};
'''
SEED = r'''ids => {
 const state=window.QB.getState(),now=Date.now(),H=3600e3,mk={correct:1,wrong:0,blank:0};
 state.tests=[{id:'t_k1',title:'Kept 1',questionIds:ids.slice(0,10),answers:{},correct:7,incorrect:3,unattempted:0,total:10,attempted:10,totalTimeMs:6e5,createdAt:now-119*H,originRoute:'tests',scheduledMockId:'sm_k1'},
  {id:'t_k2',title:'Kept 2',questionIds:ids.slice(0,10),answers:{},correct:8,incorrect:2,unattempted:0,total:10,attempted:10,totalTimeMs:6e5,createdAt:now-95*H,originRoute:'tests',scheduledMockId:'sm_k2'}];
 state.savedMocks=[{id:'saved-ipad',name:'Saved iPad mock',questionIds:ids.slice(0,10),createdAt:now,updatedAt:now}];
 state.scheduledMocks=[
  {id:'sm_k1',name:'Kept 1',questionIds:ids.slice(0,10),at:now-120*H,createdAt:now-140*H,marking:mk,seconds:60,takenTestId:'t_k1'},
  {id:'sm_k2',name:'Kept 2',questionIds:ids.slice(0,10),at:now-96*H,createdAt:now-110*H,marking:mk,seconds:60,takenTestId:'t_k2'},
  {id:'sm_wed',name:'Mixed Subjects CBT',questionIds:ids.slice(0,30),at:now-72*H,createdAt:now-90*H,marking:mk,seconds:60},
  {id:'sm_up',name:'Upcoming physiology mock',questionIds:ids.slice(10,30),at:now+20*H,createdAt:now,marking:mk,seconds:60}];
 window.QB.saveState();
}'''


def fixture_page() -> str:
    """The source page with the bundled First Prof banks and empty multi-bank tokens (enough for scheduled mocks)."""
    page = app_page()
    values = {'QBANK_DATA': (ASSETS / 'qbank_data.js').read_text(encoding='utf-8'),
              'SUBJECT_QBANK_DATA': (ASSETS / 'subjects_qbank_data.js').read_text(encoding='utf-8'),
              'MARROW_DATA': '{"records":[]}', 'MARROW_EXPLANATION_GOLD': '{}', 'MARROW_TOPIC_TAXONOMY': '{}',
              'MARROW_VISIBLE_TOPIC_ORDER': '{}', 'TOPIC_SECTIONS': '{}',
              'UWORLD_SCRIPTS': '<script>window.NK_UWORLD_DATA=[{subject:"UWorld Biochemistry",bank:"UWorld",collection:"biochemistry",topics:[],questions:[]}];</script>\n'}
    page = re.sub(r'__NK_DATA_([A-Z_]+?)__', lambda m: values[m.group(1)], page)
    css = (ASSETS / 'app.css').read_text(encoding='utf-8')
    return re.sub(r'<link rel="stylesheet" href="app\.css(?:\?v=[0-9A-Za-z]+)?">', lambda m: '<style>\n' + css + '\n</style>', page, count=1)


def serve(fixture: bool):
    web = ASSETS if fixture else ROOT / 'build/web'
    page = fixture_page() if fixture else built_page(web)
    html = page.replace('  window.QB={', PROBE + '  window.QB={', 1).encode()

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
    return server, f'http://127.0.0.1:{server.server_port}'


def open_app(browser, origin, viewport, ua, touch):
    context = browser.new_context(viewport=viewport, user_agent=ua, has_touch=touch, service_workers='block', reduced_motion='reduce', locale='en-US')
    page = context.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(origin + '/index.html#dashboard', wait_until='domcontentloaded')
    page.wait_for_function('window.QB && window.__nkSchedSync')
    return context, page, errors


def visible_card(page, selector, width):
    loc = page.locator(selector).first
    expect(loc).to_be_visible()
    # Home re-renders on the live countdown tick; a box read mid-render comes back None. Re-read briefly.
    box = None
    for _ in range(10):
        box = loc.bounding_box()
        if box:
            break
        page.wait_for_timeout(200)
    assert box and box['width'] > 200 and box['height'] > 40 and box['x'] >= 0 and box['x'] + box['width'] <= width + 1, (selector, box, width)
    return loc


def phone_home(page):
    """The phone's Home order and texts (the reference the iPad must match)."""
    order = page.evaluate("""(()=>{const all=[...document.querySelectorAll('.nk-sched-makeup,.nk-sched-home,.nk-study-sets')].map(e=>e.classList.contains('nk-sched-makeup')?'makeup':e.classList.contains('nk-sched-home')?'tickets':'sets');return all;})()""")
    return {'order': order, 'makeup': page.locator('.nk-sched-makeup').inner_text(), 'ticket': page.locator('.nk-sched-home .nk-sched-ticket').first.inner_text()}


def main():
    fixture = '--fixture' in sys.argv
    forced = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--engine=')), '')
    server, origin = serve(fixture)
    try:
        with sync_playwright() as p:
            chromium = p.chromium.launch()
            engine = forced or 'webkit'
            try:
                ipad_browser = chromium if engine == 'chromium' else p.webkit.launch()
            except Exception as error:  # WebKit not installed here: say so, and run the iPad pass on Chromium.
                print(f'WEBKIT_UNAVAILABLE {str(error).splitlines()[0][:160]}')
                engine, ipad_browser = 'chromium', chromium

            # Phone: book, miss, keep. Its Home is the reference and must be as before.
            ctx, phone, perr = open_app(chromium, origin, {'width': 390, 'height': 844}, PHONE_UA, True)
            ids = phone.evaluate('window.__nkSchedSync.questions()')
            assert len(ids) >= 30, len(ids)
            phone.evaluate(SEED, ids)
            phone.evaluate("window.QB.nav('tests')"); phone.evaluate("window.QB.nav('dashboard')")
            visible_card(phone, '.nk-sched-makeup', 390)
            expect(phone.locator('.nk-sched-makeup')).to_contain_text('Make-up owed', ignore_case=True)
            expect(phone.locator('.nk-sched-makeup')).to_contain_text('Mixed Subjects CBT')
            expect(phone.locator('.nk-sched-makeup')).to_contain_text('30 Qs · 30 min')
            visible_card(phone, '.nk-sched-home .nk-sched-ticket.is-upcoming', 390)
            ref = phone_home(phone)
            assert ref['order'] == ['makeup', 'tickets', 'sets'], ref['order']
            phone.evaluate("window.QB.nav('tests')")
            expect(phone.locator('.nk-sched-attend')).to_contain_text('Kept 2 of 3')
            ref_attend = phone.locator('.nk-sched-attend').inner_text()
            assert 'Streak broken' in ref_attend, ref_attend
            assert not phone.evaluate('document.documentElement.scrollWidth>innerWidth'), 'phone overflow'
            outbox = phone.evaluate('window.__nkSchedSync.out()')
            assert sum(1 for e in outbox if e['kind'] == 'scheduledMocks') == 4, [e['entityId'] for e in outbox if e['kind'] == 'scheduledMocks']
            assert any(e['kind'] == 'tests' and e['entityId'] == 'missed_sm_wed' for e in outbox), 'the miss is recorded on the phone'

            back = None
            for width, height in [(820, 1180), (1180, 820)]:
                ictx, ipad, ierr = open_app(ipad_browser, origin, {'width': width, 'height': height}, IPAD_UA, True)
                ua = ipad.evaluate('navigator.userAgent')
                assert 'Macintosh' in ua and 'Mobile' not in ua, ua
                # Before sync: the owner's symptom (no bookings on this device, so no card).
                ipad.evaluate("(()=>{const s=window.QB.getState();s.scheduledMocks=[];s.tests=[];s.savedMocks=[];window.QB.saveState();window.QB.nav('tests');window.QB.nav('dashboard')})()")
                expect(ipad.locator('.nk-sched-makeup')).to_have_count(0)
                # The phone's envelopes arrive through the real merge path.
                assert ipad.evaluate('list=>window.__nkSchedSync.apply(list)', outbox) == 4
                assert ipad.evaluate('list=>window.__nkSchedSync.apply(list)', outbox) == 4, 'a second pull adds no duplicate'
                ipad.evaluate("window.QB.nav('tests')"); ipad.evaluate("window.QB.nav('dashboard')")
                assert ipad.evaluate("window.QB.getState().tests.filter(t=>t.id==='missed_sm_wed').length") == 1, 'one zero, not two'
                assert ipad.evaluate('window.__nkSchedSync.changed()') == [], 'received bookings are not re-uploaded'
                card = visible_card(ipad, '.nk-sched-makeup', width)
                assert card.inner_text() == ref['makeup'], (card.inner_text(), ref['makeup'])
                ticket = visible_card(ipad, '.nk-sched-home .nk-sched-ticket.is-upcoming', width)
                # The live countdown ("in 19 h 59 min") can tick between the two reads; compare without it.
                same = lambda t: re.sub(r' · in [^\n]*', '', t)
                assert same(ticket.inner_text()) == same(ref['ticket']), (ticket.inner_text(), ref['ticket'])
                assert phone_home(ipad)['order'] == ref['order']
                expect(card.locator('button', has_text='Sit it')).to_be_visible()
                ipad.evaluate("window.QB.nav('tests')")
                expect(ipad.locator('.nk-sched-attend')).to_be_visible()
                assert ipad.locator('.nk-sched-attend').inner_text() == ref_attend
                expect(ipad.locator('.nk-sched-ticket.is-missed')).to_have_count(1)
                expect(ipad.locator('.nk-sched-ticket.is-taken')).to_have_count(2)
                assert not ipad.evaluate('document.documentElement.scrollWidth>innerWidth'), f'iPad overflow at {width}'
                # Booking from the WebKit datetime-local input keeps the local time typed.
                ipad.evaluate("(()=>{const s=window.QB.getState();s.savedMocks=[{id:'saved-ipad',name:'Saved iPad mock',questionIds:s.scheduledMocks[0].questionIds,createdAt:Date.now(),updatedAt:Date.now()}];window.QB.saveState();window.QB.nkSchedOpen('saved-ipad')})()")
                expect(ipad.locator('#nk-sched-sheet')).to_be_visible()
                when = ipad.evaluate("(()=>{const d=new Date(Date.now()+2*86400e3);d.setHours(9,30,0,0);const p=n=>String(n).padStart(2,'0');return {value:`${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T09:30`,at:d.getTime()}})()")
                ipad.locator('#nk-sched-at').fill(when['value'])
                expect(ipad.locator('#nk-sched-confirm')).to_be_enabled()
                ipad.locator('#nk-sched-confirm').click()
                booked = ipad.evaluate("window.QB.getState().scheduledMocks.filter(m=>m.name==='Saved iPad mock').map(m=>m.at)")
                assert booked == [when['at']], (booked, when)
                assert ipad.evaluate("window.__nkSchedSync.parse('2026-11-18 10:00')") == ipad.evaluate('new Date(2026,10,18,10,0).getTime()')
                # Sit the make-up from Home; its stamp travels back to the phone.
                ipad.evaluate("window.QB.nav('dashboard')")
                ipad.locator('.nk-sched-makeup button', has_text='Sit it').click()
                ipad.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
                assert ipad.evaluate('window.QB.getState().activeSession.makeupFor') == 'sm_wed'
                ipad.evaluate('window.QB.submitExam(false)')
                ipad.wait_for_function("location.hash.startsWith('#result/')")
                made = ipad.evaluate("(()=>{const s=window.QB.getState();return [s.scheduledMocks.find(m=>m.id==='sm_wed').makeupTestId,s.tests.find(t=>t.makeupFor==='sm_wed')?.id]})()")
                assert made[0] and made[0] == made[1], made
                ipad.evaluate("window.QB.nav('dashboard')")
                expect(ipad.locator('.nk-sched-makeup')).to_have_count(0)
                # A live scheduled mock still refuses Abandon.
                ipad.evaluate("(()=>{const s=window.QB.getState();s.activeSession={id:'live-sm',mode:'exam',title:'Live',questionIds:s.scheduledMocks[0].questionIds,index:0,answers:{},startedAt:Date.now(),questionTimes:{},timerMode:'global',scheduledMockId:'sm_up',originRoute:'tests'};})()")
                assert ipad.evaluate('window.QB.nkAbandonTimedTest()') is False
                ipad.evaluate("(()=>{window.QB.getState().activeSession=null;window.QB.saveState();})()")
                back = [e for e in ipad.evaluate('window.__nkSchedSync.out()') if e['kind'] in ('scheduledMocks', 'tests')]
                assert not ierr, ierr
                ictx.close()

            # The phone receives the iPad's make-up and bookings; its card clears, nothing is duplicated or lost.
            phone.evaluate('list=>window.__nkSchedSync.apply(list)', back)
            phone.evaluate("window.QB.nav('dashboard')")
            expect(phone.locator('.nk-sched-makeup')).to_have_count(0)
            assert phone.evaluate("window.QB.getState().scheduledMocks.find(m=>m.id==='sm_wed').makeupTestId"), 'make-up stamp merged on the phone'
            names = phone.evaluate("window.QB.getState().scheduledMocks.map(m=>m.id)")
            assert len(names) == len(set(names)) and {'sm_k1', 'sm_k2', 'sm_wed', 'sm_up'} <= set(names), names
            assert not perr, perr
            ctx.close()
            print(f'SCHEDULED_MOCK_IPAD_BROWSER_OK ipad_engine={engine} ipad=820x1180,1180x820 phone=390x844(chromium) source={"fixture" if fixture else "build/web"}')
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
