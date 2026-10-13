#!/usr/bin/env python3
"""Progress lives in IndexedDB: migration from localStorage, atomic saves,
saves that survive an immediate reload, restore points and the two-tap restore."""
import json, sys, threading, time
from functools import partial
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = str(ROOT / 'build/web')
OUT = ROOT / 'build/ui-checks/progress-store'
OUT.mkdir(parents=True, exist_ok=True)
class Q(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = ThreadingHTTPServer(('127.0.0.1', 0), partial(Q, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}/index.html?ui=geist'

SEED = {'stateSchemaVersion': 2, 'stateRevision': 5, 'bookmarks': {'seed-q': True}, 'attempts': {}, 'tests': []}
IDB_DUMP = """async () => {
  const db = await new Promise((ok, no) => { const r = indexedDB.open('nk-qbank'); r.onsuccess = () => ok(r.result); r.onerror = () => no(r.error); });
  const all = (store, method) => new Promise(ok => { const r = db.transaction(store).objectStore(store)[method](); r.onsuccess = () => ok(r.result); });
  const keys = await all('kv', 'getAllKeys'), metas = await all('snapshotMeta', 'getAll');
  const primary = await new Promise(ok => { const r = db.transaction('kv').objectStore('kv').get('qbank_state_v1'); r.onsuccess = () => ok(r.result); });
  db.close();
  return { keys, metas, primary: primary ? JSON.parse(primary) : null };
}"""
fail = []
def check(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond: fail.append(msg)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844})
    errors = []
    ctx.add_init_script("""if (!sessionStorage.getItem('seeded')) { sessionStorage.setItem('seeded','1');
      localStorage.setItem('qbank_state_v1', %s); localStorage.setItem('qbank_pre_fsrs_backup_v1', '{"old":1}'); }""" % json.dumps(json.dumps(SEED)))
    page = ctx.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: m.type == 'error' and errors.append(m.text))
    t0 = time.time()
    page.goto(URL, wait_until='load')
    page.wait_for_function('window.NKStore && window.NKStore.backend !== "starting"', timeout=10000)
    check(page.evaluate('NKStore.backend') == 'indexeddb', 'backend is indexeddb')
    check(page.evaluate("!!(window.QB && QB.getState().bookmarks['seed-q'])"), 'app booted with migrated progress')
    page.wait_for_timeout(300)
    d = page.evaluate(IDB_DUMP)
    check('qbank_state_v1' in d['keys'] and 'qbank_pre_fsrs_backup_v1' in d['keys'], f'kv holds migrated keys {d["keys"]}')
    check(any(m['reason'] == 'migration' for m in d['metas']), 'migration restore point exists')
    check(page.evaluate("localStorage['qbank_pre_fsrs_backup_v1'] === undefined"), 'backup copy freed from localStorage')
    check(page.evaluate("localStorage.getItem('qbank_pre_fsrs_backup_v1')") == '{"old":1}', 'backup still readable through the store')
    rev0 = d['primary']['stateRevision']
    # A save lands in IndexedDB atomically and is mirrored later.
    page.evaluate("() => { const s = QB.getState(); s.bookmarks['after-q'] = true; QB.saveState(); }")
    page.wait_for_timeout(200)
    d = page.evaluate(IDB_DUMP)
    check(d['primary']['bookmarks'].get('after-q') is True and d['primary']['stateRevision'] > rev0, f'save committed to IndexedDB (rev {rev0} -> {d["primary"]["stateRevision"]})')
    check('qbank_state_pending_v2' not in d['keys'], 'pending journal cleared in the same transaction')
    page.wait_for_timeout(1700)
    mirror = page.evaluate("JSON.parse(localStorage['qbank_state_v1'] || 'null')")
    check(mirror and mirror['bookmarks'].get('after-q') is True, 'primary mirrored to localStorage')
    page.reload(wait_until='load')
    page.wait_for_function('window.NKStore && NKStore.backend === "indexeddb"', timeout=10000)
    check(page.evaluate("!!QB.getState().bookmarks['after-q']"), 'progress survives reload from IndexedDB')
    # IndexedDB commits asynchronously: a save followed at once by a reload must still land.
    page.evaluate("() => { const s = QB.getState(); s.bookmarks['instant-q'] = true; QB.saveState(); location.reload(); }")
    page.wait_for_function('window.NKStore && NKStore.backend === "indexeddb" && window.QB', timeout=15000)
    check(page.evaluate("!!QB.getState().bookmarks['instant-q']"), 'a save right before reload is not lost')
    page.evaluate("() => { const s = QB.getState(); delete s.bookmarks['instant-q']; QB.saveState(); }")
    # Restore UI: open, list, two-tap restore of the migration point.
    page.evaluate("location.hash = 'more'")
    page.wait_for_selector('[data-nkg-act="restore"]', timeout=8000)
    page.click('[data-nkg-act="restore"]')
    page.wait_for_selector('#nk-restore-sheet .nkg-restore-list li', timeout=8000)
    rows = page.locator('#nk-restore-sheet .nkg-restore-list li')
    check(rows.count() >= 1, f'restore page lists {rows.count()} point(s)')
    check(page.evaluate("document.documentElement.classList.contains('nkg-screen-open')"), 'restore page opens as a full screen')
    page.screenshot(path=str(OUT / 'restore-light.png'))
    page.evaluate("document.documentElement.setAttribute('data-nk-theme','dark')")
    page.emulate_media(color_scheme='dark')
    page.screenshot(path=str(OUT / 'restore-dark.png'))
    last = rows.last.locator('button')
    last.click(); check(last.inner_text() == 'Tap to confirm', 'first tap arms the restore')
    with page.expect_navigation(timeout=10000):
        last.click()
    page.wait_for_function('window.NKStore && NKStore.backend === "indexeddb" && window.QB', timeout=10000)
    page.wait_for_timeout(300)
    st = page.evaluate("QB.getState().bookmarks")
    check('seed-q' in st and 'after-q' not in st, f'restored to the migration point {st}')
    d = page.evaluate(IDB_DUMP)
    check(any(m['reason'] == 'before-restore' for m in d['metas']), 'current progress kept as a point before restoring')
    check(not errors, 'no page errors ' + json.dumps(errors[:5]))
    print('boot+tests', round(time.time() - t0, 1), 's')
    b.close()
print('PROGRESS_STORE_BROWSER_FAILED' if fail else 'PROGRESS_STORE_BROWSER_OK')
sys.exit(1 if fail else 0)
