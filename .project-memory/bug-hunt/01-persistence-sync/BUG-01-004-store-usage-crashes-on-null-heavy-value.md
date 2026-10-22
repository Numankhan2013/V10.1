# BUG-01-004 — NKStore.usage() throws when a heavy value is null

- **Area:** 01 persistence & sync
- **Severity:** low
- **Confidence:** high
- **Status:** fix applied — commit 986cad56
- **Files:** `app/src/main/assets/nk-store.js:203`, `app/src/main/assets/nk-store.js:205`
- **Introduced by:** unknown

## What happens

`usage()` sums `value.length` over every in-memory heavy value. If any heavy key holds `null` (for example a migrated localStorage entry whose value was `null`), the call throws and the restore-points dialog fails to show storage usage.

## Evidence

```js
function usage() {
  var bytes = 0;
  mem.forEach(function (value) { bytes += value.length; });  // throws if value is null
  ...
}
```

`migrateFromLocal` copies values verbatim:

```js
if (local) for (var i = 0; i < local.length; i++) { var key = local.key(i); if (HEAVY.test(key)) moved[key] = nativeGet.call(local, key); }
...
mem.forEach(function (value, key) { moved[key] = value; });
```

A heavy key with a `null` localStorage value therefore becomes a `null` in-memory value.

## Learner impact

The restore-points sheet's storage line fails to render; no study data is lost.

## Root cause

`usage()` assumes every heavy value is a string. Migration does not coerce or skip null values.

## Proposed fix

```diff
--- a/app/src/main/assets/nk-store.js
+++ b/app/src/main/assets/nk-store.js
@@ -202,6 +202,6 @@
   }
   function usage() {
     var bytes = 0;
-    mem.forEach(function (value) { bytes += value.length; });
+    mem.forEach(function (value) { bytes += String(value == null ? '' : value).length; });
     var estimate = navigator.storage && navigator.storage.estimate ? navigator.storage.estimate() : Promise.resolve({});
     return estimate.then(function (e) { return { progressBytes: bytes, usage: e.usage || 0, quota: e.quota || 0 }; }, function () { return { progressBytes: bytes }; });
   }```

## Verification

- Seed localStorage with a heavy key whose value is `null`, reload, open Restore points; usage line should render.
- Run `python3 tools/test_cross_device_sync_v1.py`.

## Alternatives considered

Skipping null entries in `usage()` would also work, but coercing matches how `setItem` already stringifies values.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified nk-store.js:203-205: usage() sums value.length over every heavy value with no null guard, and migrateFromLocal copies localStorage values verbatim, so a null heavy value throws. The coercion fix is minimal and matches setItem own stringification. Approved. Severity low is right: it only affects the storage-usage line in the restore-points sheet.
