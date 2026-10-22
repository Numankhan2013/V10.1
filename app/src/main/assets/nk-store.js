/* NK QBank progress store.
 *
 * IndexedDB is the source of truth for progress and its state-sized backups.
 * The app's storage code is synchronous, so those keys are served from an
 * in-memory copy that is hydrated before the app boots and committed to
 * IndexedDB in one transaction per task (pending, primary and last-known-good
 * writes of a save land atomically). IndexedDB commits asynchronously, so a
 * reload or close right after a save could drop that transaction: the primary
 * record is also written to localStorage synchronously (one write, where the
 * old scheme made three) and boot adopts it when its revision is newer. An
 * older build can open that copy too.
 *
 * Automatic restore points are taken while you study and before destructive
 * actions; window.NKStore lists and restores them.
 */
(function () {
  'use strict';
  if (window.NKStore) return;
  var DB_NAME = 'nk-qbank', DB_VERSION = 1, PRIMARY = 'qbank_state_v1';
  // Keys whose values are whole copies of the progress state.
  var HEAVY = /^(qbank_state_|qbank_pre_fsrs_backup_v1$|qbank_account_snapshot_v1_)/;
  var SNAPSHOT_EVERY = 30 * 60 * 1000, RECENT_KEEP = 12, DAILY_KEEP = 14;
  var proto = Storage.prototype, nativeGet = proto.getItem, nativeSet = proto.setItem, nativeRemove = proto.removeItem;
  var local = null;
  try { local = window.localStorage; } catch (_) {}

  var mem = new Map(), dirty = new Map(), ready = false, failed = false, db = null, bootRead = false;
  // Set once a restore commits: the page is about to reload and its in-memory
  // state is older than the restored copy, so its unload save must not land.
  var frozen = false;
  var flushQueued = false, lastSnapshotAt = 0, lastError = '', channel = null;
  var listeners = [];

  function heavy(store, key) { return store === local && HEAVY.test(String(key)); }
  function revisionOf(raw) { try { return Number(JSON.parse(raw).stateRevision) || 0; } catch (_) { return -1; } }
  function note(message, error) {
    lastError = message + (error && error.message ? ': ' + error.message : '');
    try { console.warn('[NKStore]', lastError); } catch (_) {}
  }

  // Each IndexedDB version upgrades from the previous one, in order.
  var MIGRATIONS = [
    function v1(database) {
      database.createObjectStore('kv');
      database.createObjectStore('snapshotMeta', { keyPath: 'id', autoIncrement: true }).createIndex('at', 'at');
      database.createObjectStore('snapshotData');
    }
  ];
  function open() {
    return new Promise(function (resolve, reject) {
      if (!window.indexedDB) return reject(new Error('IndexedDB unavailable'));
      var request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = function (event) {
        for (var v = event.oldVersion; v < DB_VERSION; v++) MIGRATIONS[v](request.result, request.transaction);
      };
      request.onsuccess = function () {
        var database = request.result;
        database.onversionchange = function () { database.close(); };
        resolve(database);
      };
      request.onerror = function () { reject(request.error); };
      request.onblocked = function () { reject(new Error('IndexedDB upgrade blocked by another tab')); };
    });
  }
  function done(tx) {
    return new Promise(function (resolve, reject) {
      tx.oncomplete = function () { resolve(); };
      tx.onerror = tx.onabort = function () { reject(tx.error || new Error('transaction aborted')); };
    });
  }
  function req(request) {
    return new Promise(function (resolve, reject) {
      request.onsuccess = function () { resolve(request.result); };
      request.onerror = function () { reject(request.error); };
    });
  }

  /* ------------------------------------------------------------ Storage */
  proto.getItem = function (key) {
    if (!heavy(this, key)) return nativeGet.call(this, key);
    if (!ready) { if (String(key) === PRIMARY) bootRead = true; return mem.has(key) ? mem.get(key) : nativeGet.call(this, key); }
    return mem.has(key) ? mem.get(key) : null;
  };
  proto.setItem = function (key, value) {
    if (!heavy(this, key)) return nativeSet.call(this, key, value);
    if (frozen) return;
    key = String(key); value = String(value);
    if (!ready) { nativeSet.call(this, key, value); mem.set(key, value); return; }
    mem.set(key, value); dirty.set(key, value); schedule();
    if (key === PRIMARY) journal(value);
  };
  proto.removeItem = function (key) {
    if (!heavy(this, key)) return nativeRemove.call(this, key);
    if (frozen) return;
    key = String(key);
    if (!ready) { nativeRemove.call(this, key); mem.delete(key); return; }
    mem.delete(key); dirty.set(key, null); schedule();
  };

  function schedule() {
    if (flushQueued) return;
    flushQueued = true;
    // Coalesce every write of the current task (a save writes three keys).
    Promise.resolve().then(flush);
  }
  function flush() {
    flushQueued = false;
    if (frozen || !db || !dirty.size) return Promise.resolve();
    var batch = dirty; dirty = new Map();
    var tx = db.transaction(['kv', 'snapshotMeta', 'snapshotData'], 'readwrite'), kv = tx.objectStore('kv');
    batch.forEach(function (value, key) { if (value === null) kv.delete(key); else kv.put(value, key); });
    var primary = batch.get(PRIMARY);
    if (primary && Date.now() - lastSnapshotAt >= SNAPSHOT_EVERY) addSnapshot(tx, primary, 'auto');
    return done(tx).then(function () {
      if (primary) announce(primary);
      if (lastError) lastError = '';
    }, function (error) {
      // Put the batch back so the next save retries it, and surface the failure.
      batch.forEach(function (value, key) { if (!dirty.has(key)) dirty.set(key, value); });
      note('Progress could not be written to on-device storage', error);
      try { window.dispatchEvent(new CustomEvent('nk-store-error', { detail: lastError })); } catch (_) {}
    });
  }
  // Over quota the stale copy is dropped rather than left behind; IndexedDB still has the save.
  function journal(raw) {
    if (!local) return;
    try { nativeSet.call(local, PRIMARY, raw); }
    catch (_) { try { nativeRemove.call(local, PRIMARY); } catch (__) {} }
  }
  function announce(raw) {
    try { var revision = revisionOf(raw); if (channel && revision >= 0) channel.postMessage({ type: 'state', revision: revision }); } catch (_) {}
  }
  function flushNow() { if (frozen || !dirty.size) return; flush(); }
  window.addEventListener('pagehide', flushNow);
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') flushNow(); });

  /* ---------------------------------------------------------- Snapshots */
  function summarize(raw) {
    try {
      var state = JSON.parse(raw);
      return { revision: Number(state.stateRevision) || 0, answered: Object.keys(state.attempts || {}).length,
        notes: Object.keys(state.questionNotes || {}).length, tests: (state.tests || []).length };
    } catch (_) { return { revision: 0, answered: 0, notes: 0, tests: 0 }; }
  }
  function addSnapshot(tx, raw, reason) {
    var now = Date.now(), meta = summarize(raw);
    meta.at = now; meta.reason = reason; meta.bytes = raw.length;
    lastSnapshotAt = now;
    var metaStore = tx.objectStore('snapshotMeta');
    metaStore.add(meta).onsuccess = function (event) {
      tx.objectStore('snapshotData').put(raw, event.target.result);
      prune(tx);
    };
  }
  // Keep every point from the last day (up to RECENT_KEEP), then one per day.
  function prune(tx) {
    var metaStore = tx.objectStore('snapshotMeta'), dataStore = tx.objectStore('snapshotData');
    metaStore.getAll().onsuccess = function (event) {
      var all = event.target.result.sort(function (a, b) { return b.at - a.at; }), keep = new Set(), days = new Set();
      var dayAgo = Date.now() - 864e5, recent = 0, marked = 0;
      all.forEach(function (item) {
        // Points taken before a reset, restore or migration stay for two weeks.
        if (item.reason !== 'auto') { if (item.at > Date.now() - DAILY_KEEP * 864e5) keep.add(item.id); return; }
        if (item.at > dayAgo && recent < RECENT_KEEP) { recent++; keep.add(item.id); return; }
        var day = new Date(item.at).toDateString();
        if (!days.has(day) && days.size < DAILY_KEEP) { days.add(day); keep.add(item.id); }
      });
      all.forEach(function (item) { if (!keep.has(item.id)) { metaStore.delete(item.id); dataStore.delete(item.id); } });
    };
  }
  function snapshot(reason) {
    // Capture now: a reset that follows this call in the same task must not be what gets saved.
    var captured = ready ? mem.get(PRIMARY) : null;
    return api.ready.then(function () {
      var raw = captured != null ? captured : mem.get(PRIMARY);
      if (!db || raw == null) return null;
      var tx = db.transaction(['snapshotMeta', 'snapshotData'], 'readwrite');
      addSnapshot(tx, raw, reason || 'manual');
      return done(tx).then(function () { return true; });
    });
  }
  function snapshots() {
    return api.ready.then(function () {
      if (!db) return [];
      return req(db.transaction('snapshotMeta').objectStore('snapshotMeta').getAll()).then(function (all) {
        return all.sort(function (a, b) { return b.at - a.at; });
      });
    });
  }
  function restore(id) {
    return snapshot('before-restore').then(function () {
      return req(db.transaction('snapshotData').objectStore('snapshotData').get(Number(id)));
    }).then(function (raw) {
      if (raw == null) throw new Error('That restore point no longer exists');
      var state = JSON.parse(raw), current = revisionOf(mem.get(PRIMARY) || '{}');
      // A newer revision so this copy wins over the backups at the next boot.
      state.stateRevision = Math.max(current, Number(state.stateRevision) || 0) + 1;
      var next = JSON.stringify(state);
      local.setItem(PRIMARY, next); local.setItem('qbank_state_lkg_v2', next); local.removeItem('qbank_state_pending_v2');
      return flush().then(function () { frozen = true; return true; });
    });
  }
  function usage() {
    var bytes = 0;
    mem.forEach(function (value) { bytes += String(value == null ? '' : value).length; });
    var estimate = navigator.storage && navigator.storage.estimate ? navigator.storage.estimate() : Promise.resolve({});
    return estimate.then(function (e) { return { progressBytes: bytes, usage: e.usage || 0, quota: e.quota || 0 }; }, function () { return { progressBytes: bytes }; });
  }

  /* ----------------------------------------------------------- Hydrate */
  function hydrate() {
    return open().then(function (database) {
      db = database;
      return req(db.transaction('kv').objectStore('kv').getAllKeys()).then(function (keys) {
        var tx = db.transaction('kv'), store = tx.objectStore('kv'), values = {};
        keys.forEach(function (key) { store.get(key).onsuccess = function (event) { values[key] = event.target.result; }; });
        return done(tx).then(function () { return values; });
      });
    }).then(function (stored) {
      var keys = Object.keys(stored);
      if (!keys.length) return migrateFromLocal();
      var early = mem.get(PRIMARY) != null ? mem.get(PRIMARY) : nativeGet.call(local, PRIMARY);
      mem.clear();
      keys.forEach(function (key) { mem.set(key, stored[key]); });
      // The app booted from the localStorage mirror before IndexedDB answered
      // and IndexedDB holds newer progress: reload once to show it.
      if (bootRead && early !== stored[PRIMARY] && revisionOf(stored[PRIMARY]) > revisionOf(early || '{}')) {
        var flag = 'nk.store.reloaded';
        try { if (!sessionStorage.getItem(flag)) { sessionStorage.setItem(flag, '1'); location.reload(); return; } } catch (_) {}
        // Already reloaded once: stop this copy from overwriting the newer progress.
        try { window.dispatchEvent(new StorageEvent('storage', { key: PRIMARY, newValue: stored[PRIMARY] })); } catch (_) {}
        return;
      }
      // Writes made from the mirror before hydration finished but newer than IndexedDB still count.
      if (early != null && revisionOf(early) > revisionOf(stored[PRIMARY] || '{}')) { mem.set(PRIMARY, early); dirty.set(PRIMARY, early); }
    }).then(function () {
      return req(db.transaction('snapshotMeta').objectStore('snapshotMeta').index('at').openCursor(null, 'prev')).then(function (cursor) {
        lastSnapshotAt = cursor ? cursor.value.at : 0;
      });
    });
  }
  // First run on IndexedDB: copy every state-sized key over in one transaction,
  // then free localStorage of everything but the primary mirror.
  function migrateFromLocal() {
    var moved = {};
    if (local) for (var i = 0; i < local.length; i++) { var key = local.key(i); if (HEAVY.test(key)) moved[key] = nativeGet.call(local, key); }
    Object.keys(moved).forEach(function (key) { mem.set(key, moved[key]); });
    mem.forEach(function (value, key) { moved[key] = value; });
    var tx = db.transaction(['kv', 'snapshotMeta', 'snapshotData'], 'readwrite'), kv = tx.objectStore('kv');
    Object.keys(moved).forEach(function (key) { kv.put(moved[key], key); });
    if (moved[PRIMARY]) addSnapshot(tx, moved[PRIMARY], 'migration');
    return done(tx).then(function () {
      Object.keys(moved).forEach(function (key) { if (key !== PRIMARY) try { nativeRemove.call(local, key); } catch (_) {} });
    });
  }

  var api = {
    ready: null,
    get backend() { return failed ? 'localStorage' : (ready ? 'indexeddb' : 'starting'); },
    get lastError() { return lastError; },
    snapshot: snapshot,
    snapshots: snapshots,
    restore: restore,
    usage: usage,
    flush: function () { flushNow(); return flush(); },
    onChange: function (fn) { listeners.push(fn); }
  };
  api.ready = hydrate().then(function () {
    ready = true;
    if (dirty.size) schedule();
    try {
      channel = new BroadcastChannel('nk-qbank-store');
      channel.onmessage = function (event) {
        if (!event.data || event.data.type !== 'state') return;
        // Another tab committed newer progress; the app's stale-tab guard listens for this.
        try { window.dispatchEvent(new StorageEvent('storage', { key: PRIMARY, newValue: String(event.data.revision) })); } catch (_) {}
        listeners.forEach(function (fn) { try { fn(event.data); } catch (_) {} });
      };
    } catch (_) {}
  }, function (error) {
    // No IndexedDB (or it failed): keep using localStorage exactly as before.
    failed = true;
    proto.getItem = nativeGet; proto.setItem = nativeSet; proto.removeItem = nativeRemove;
    note('Using localStorage because IndexedDB is unavailable', error);
  });
  window.NKStore = api;
})();
