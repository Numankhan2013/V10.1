#!/usr/bin/env python3
"""Owner report 2026-11-21: Android Home rows and iPad Safari bars.

1. Android Home, My Progress: with a long label ("Unique questions answered") and a
   change chip ("+611% vs last week") the figure fell under the label. The figure
   and its chip must stay on the right of the label at 360 and 412 px.
2. Android Home, Today's plan: "· Goal 20" sat on a line by itself. Once the goal
   is met, "goal of N met" is the goal control; nothing wraps onto its own line.
3. iPad (iPadOS Safari reports a Mac with touch): the page is marked nk-ios, the
   session header is solid and its colour reaches above it, the session dock's
   colour reaches below it (Safari 26 shows the page under its toolbars).

  python3 tools/verify_device_ui_fixes_browser.py            # build/web (CI)
  python3 tools/verify_device_ui_fixes_browser.py --fixture  # source page, bundled First Prof data
"""
import sys
import time
from playwright.sync_api import sync_playwright
from verify_scheduled_mock_ipad_browser import serve, SEED

PHONE_UA = 'Mozilla/5.0 (Linux; Android 14; 23078PND5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
IPAD_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15'
ATTEMPTS = r'''ids => {const s=window.QB.getState(),now=Date.now();s.attempts=s.attempts||{};const P=(id,a)=>(s.attempts[id]=s.attempts[id]||[]).push(a);
 ids.slice(0,30).forEach((id,i)=>P(id,{id:'r'+i+id,at:now-60e3*(i+1),correct:i%20!==0,selected:1,source:'practice',timeMs:28000}));
 ids.slice(30,34).forEach((id,i)=>P(id,{id:'r'+i+id,at:now-7*86400e3-3600e3,correct:i%2===0,selected:1,source:'practice',timeMs:28000}));
 window.QB.saveState();}'''
ROWS = r'''()=>[...document.querySelectorAll('.nk-home-progress-copy')].map(row=>{const l=row.querySelector('strong').getBoundingClientRect(),v=(row.querySelector('.nkg-val')||row.querySelector('b')).getBoundingClientRect();return {label:l.right,value:v.left,lt:l.top,lb:l.bottom,vt:v.top,vb:v.bottom};})'''
GOAL = r'''()=>{const b=document.querySelector('.nk-today-step.is-new .nk-today-goal-edit');if(!b)return null;const s=b.closest('small'),r=document.createRange();r.selectNodeContents(s);const lines=new Set([...r.getClientRects()].map(x=>Math.round(x.top)));const first=s.firstChild,fr=document.createRange();fr.selectNodeContents(first.nodeType===3?first:s);return {lines:lines.size,btnTop:Math.round(b.getBoundingClientRect().top),textTop:Math.round(fr.getClientRects()[0].top),text:s.textContent};}'''


def open_app(browser, origin, viewport, ua, dark):
    ctx = browser.new_context(viewport=viewport, user_agent=ua, has_touch=True, service_workers='block', reduced_motion='reduce', color_scheme='dark' if dark else 'light')
    if ua == IPAD_UA:  # iPadOS Safari: a Mac platform with touch points
        ctx.add_init_script("Object.defineProperty(navigator,'platform',{get:()=>'MacIntel'});Object.defineProperty(navigator,'maxTouchPoints',{get:()=>5});")
    page = ctx.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(origin + '/index.html#dashboard', wait_until='domcontentloaded')
    page.wait_for_function('window.QB && window.__nkSchedSync')
    return ctx, page, errors


def main():
    server, origin = serve('--fixture' in sys.argv)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for dark in (False, True):
                for width in (360, 412):
                    ctx, page, errors = open_app(browser, origin, {'width': width, 'height': 915}, PHONE_UA, dark)
                    ids = page.evaluate('window.__nkSchedSync.questions()')
                    page.evaluate(SEED, ids); page.evaluate(ATTEMPTS, ids)
                    page.evaluate("window.QB.nav('tests')"); page.evaluate("window.QB.nav('dashboard')"); time.sleep(0.6)
                    page.evaluate("()=>{const s=document.querySelector('.nk-home-range select');if(s){s.value='week';s.dispatchEvent(new Event('change',{bubbles:true}));}}"); time.sleep(0.6)
                    assert not page.evaluate("document.documentElement.classList.contains('nk-ios')"), 'Android must not get the iPad rules'
                    rows = page.evaluate(ROWS)
                    assert len(rows) == 3, rows
                    for row in rows:
                        assert row['value'] >= row['label'] - 1, ('figure fell under its label', width, dark, row)
                        assert row['vt'] < row['lb'] and row['vb'] > row['lt'], ('figure not beside its label', width, dark, row)
                    assert page.locator('.nk-home-progress-copy .nkg-delta').count() >= 1, 'no change chip to test against'
                    goal = page.evaluate(GOAL)
                    assert goal and goal['lines'] == 1 and abs(goal['btnTop'] - goal['textTop']) <= 3, ('goal control on its own line', width, dark, goal)
                    assert 'goal of 20 met' in goal['text'] and 'Goal 20' not in goal['text'], goal
                    assert not errors, errors
                    ctx.close()
                    print(f'ANDROID_HOME_OK width={width} dark={dark}')

            # Safari's engine when CI could install it, else Chromium with an iPadOS user agent.
            try:
                ipad_browser = p.webkit.launch(proxy={'server': 'http://127.0.0.1:9', 'bypass': '127.0.0.1,localhost,<-loopback>'}); engine = 'webkit'
            except Exception:
                ipad_browser = browser; engine = 'chromium'
            ctx, page, errors = open_app(ipad_browser, origin, {'width': 1180, 'height': 820}, IPAD_UA, True)
            assert page.evaluate("document.documentElement.classList.contains('nk-ios')"), 'iPad not marked nk-ios'
            page.evaluate('window.QB.startAllPractice()'); time.sleep(0.8)
            page.evaluate("()=>{const o=document.querySelector('.option');o&&o.click();}"); time.sleep(0.6)
            first = page.evaluate("()=>{const h=document.querySelector('.nk-v114-session > .nk-session-head').getBoundingClientRect(),q=document.querySelector('.nk-v114-session .question-shell').getBoundingClientRect();return {hb:h.bottom,qt:q.top}}")
            assert first['qt'] >= first['hb'], ('question starts under the fixed header', first)
            page.evaluate("()=>{const d=document.createElement('div');d.style.height='1800px';document.querySelector('.nk-v114-session').appendChild(d);}")
            page.evaluate('window.scrollTo(0, 900)'); time.sleep(0.6)
            head = page.evaluate("""()=>{const h=document.querySelector('.nk-v114-session > .nk-session-head'),cs=getComputedStyle(h),b=getComputedStyle(h,'::before'),r=h.getBoundingClientRect();return {top:Math.round(r.top),pos:cs.position,bg:cs.backgroundColor,before:b.content,bh:parseFloat(b.height),bbg:b.backgroundColor,scroll:window.scrollY};}""")
            assert head['scroll'] > 300 and head['top'] == 0 and head['pos'] == 'fixed', head
            assert head['before'] not in ('none', 'normal') and head['bh'] >= 200 and head['bbg'] == head['bg'], head
            assert not head['bg'].startswith('rgba') or head['bg'].endswith(', 1)'), ('session header must be solid on iPad', head)
            foot = page.evaluate("""()=>{const f=document.querySelector('.nk-session-footer'),a=getComputedStyle(f,'::after'),r=f.getBoundingClientRect();return {bottom:Math.round(r.bottom),h:innerHeight,after:a.content,ah:parseFloat(a.height),abg:a.backgroundColor,bg:getComputedStyle(f).backgroundColor};}""")
            assert foot['bottom'] == foot['h'] and foot['after'] not in ('none', 'normal') and foot['ah'] >= 200 and foot['abg'] == foot['bg'], foot
            # The redraw nudge leaves nothing behind once scrolling settles.
            time.sleep(0.5)
            assert page.evaluate("[...document.querySelectorAll('.nk-session-footer,.nk-session-head')].every(e=>!e.style.translate)"), 'nudge left a translate behind'
            assert not errors, errors
            ctx.close()
            if ipad_browser is not browser: ipad_browser.close()
            print(f'IPAD_SESSION_BARS_OK engine={engine}')
            browser.close()
    finally:
        server.shutdown()
    print('DEVICE_UI_FIXES_OK')


if __name__ == '__main__':
    main()
