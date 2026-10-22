# BUG-01-005 — A manual or pagehide flush after restore can still commit stale writes

- **Area:** 01 persistence & sync
- **Severity:** medium
- **Confidence:** medium
- **Status:** fix applied — commit 986cad56
- **Files:** `app/src/main/assets/nk-store.js:106`, `app/src/main/assets/nk-store.js:133`, `app/src/main/assets/nk-store.js:190`, `app/src/main/assets/nk-store.js:200`
- **Introduced by:** unknown

## What happens

After a restore commits, `frozen` is set to `true` so that `setItem`/`removeItem` stop recording new edits. However, `flush()` and `flushNow()` never check `frozen`. A pagehide or an explicit `NKStore.flush()` during the restore window can therefore commit a dirty batch that is older than the restored state, overwriting it.

## Evidence

```js
function flush() {
  flushQueued = false;
  if (!db || !dirty.size) return Promise.resolve();
  ...
}
function flushNow() { if (dirty.size) flush(); }
...
function restore(id) {
  ...
  return flush().then(function () { frozen = true; return true; });
}
```

`proto.setItem`/`proto.removeItem` guard with `if (frozen) return;`, but the flush paths do not, and `restore()` only sets `frozen` after `flush()` resolves. Any write queued before that point can still be committed by a concurrent `flushNow()`.

## Learner impact

A restored point can be immediately overwritten by the stale in-memory edits that existed before the restore, defeating undo.

## Root cause

The frozen flag is consulted only at the storage-mutation entry points, not at the commit entry points.

## Proposed fix

```diff
--- a/app/src/main/assets/nk-store.js
+++ b/app/src/main/assets/nk-store.js
@@ -105,7 +105,7 @@
   }
   function flush() {
     flushQueued = false;
-    if (!db || !dirty.size) return Promise.resolve();
+    if (frozen || !db || !dirty.size) return Promise.resolve();
     var batch = dirty; dirty = new Map();
     var tx = db.transaction(['kv', 'snapshotMeta', 'snapshotData'], 'readwrite'), kv = tx.objectStore('kv');
     batch.forEach(function (value, key) { if (value === null) kv.delete(key); else kv.put(value, key); });
@@ -130,6 +130,6 @@
   function announce(raw) {
     try { if (channel) channel.postMessage({ type: 'state', revision: revisionOf(raw) }); } catch (_) {}
   }
-  function flushNow() { if (dirty.size) flush(); }
+  function flushNow() { if (frozen || !dirty.size) return; flush(); }
   window.addEventListener('pagehide', flushNow);
   document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') flushNow(); });
 ```

## Verification

- Restore a point, then immediately call `NKStore.flush()` / fire `pagehide`; confirm the restored revision remains in IndexedDB.
- Run `python3 tools/test_cross_device_sync_v1.py`.

## Alternatives considered

Setting `frozen = true` before calling `flush()` in `restore()` would be simpler, but it would also block the restore's own commit because that commit goes through the same `flush()` path.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified nk-store.js: the frozen flag is consulted in setItem (line 86) and removeItem (line 94) but not in flush (line 107) or flushNow (line 133), and restore() sets frozen only after flush() resolves (line 200). The diff adds the guard to both commit paths. Approved, with one caveat recorded below.
