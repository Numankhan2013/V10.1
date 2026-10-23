# BUG-01-006 — A corrupt state save announces revision -1 and can mark other tabs stale

- **Area:** 01 persistence & sync
- **Severity:** low
- **Confidence:** high
- **Status:** fix applied — commit 986cad56
- **Files:** `app/src/main/assets/nk-store.js:35`, `app/src/main/assets/nk-store.js:130`, `app/src/main/assets/nk-store.js:131`
- **Introduced by:** unknown

## What happens

`revisionOf` returns `-1` when the JSON cannot be parsed. `announce()` broadcasts that value to other tabs, which receive a truthy `"-1"` newValue and mark themselves stale even though no valid newer progress exists.

## Evidence

```js
function revisionOf(raw) { try { return Number(JSON.parse(raw).stateRevision) || 0; } catch (_) { return -1; } }
...
function announce(raw) {
  try { if (channel) channel.postMessage({ type: 'state', revision: revisionOf(raw) }); } catch (_) {}
}
```

Other tab:

```js
channel.onmessage = function (event) {
  if (!event.data || event.data.type !== 'state') return;
  try { window.dispatchEvent(new StorageEvent('storage', { key: PRIMARY, newValue: String(event.data.revision) })); } catch (_) {}
  ...
};
```

And the stale-tab guard treats any truthy newValue as newer:

```js
window.addEventListener('storage', event => { if (event.key === LS_KEY && event.newValue) { nkOtherTabNewer = true; nkStorageStaleTab(); } });
```

## Learner impact

Tabs can be told to reload for a save that never produced valid progress.

## Root cause

`revisionOf` conflates "unreadable" with a numeric revision by returning `-1`, and the cross-tab announcement does not filter that sentinel.

## Proposed fix

```diff
--- a/app/src/main/assets/nk-store.js
+++ b/app/src/main/assets/nk-store.js
@@ -128,7 +128,7 @@
     catch (_) { try { nativeRemove.call(local, PRIMARY); } catch (__) {} }
   }
   function announce(raw) {
-    try { if (channel) channel.postMessage({ type: 'state', revision: revisionOf(raw) }); } catch (_) {}
+    try { var revision = revisionOf(raw); if (channel && revision >= 0) channel.postMessage({ type: 'state', revision: revision }); } catch (_) {}
   }
   function flushNow() { if (frozen || !dirty.size) return; flush(); }
   window.addEventListener('pagehide', flushNow);
```

## Verification

- Save a corrupt primary value; confirm no BroadcastChannel message is posted and other tabs are not marked stale.
- Run `python3 tools/test_cross_device_sync_v1.py`.

## Alternatives considered

Changing `revisionOf` to return 0 on parse failure would also work, but 0 is a legitimate revision for a fresh state; guarding in `announce` preserves the existing recovery semantics.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified nk-store.js:35 (revisionOf returns -1 on a parse failure), the announce() post at line 130, the channel onmessage handler at line 271 (which re-dispatches a StorageEvent with the revision as newValue) and the stale-tab guard in durable_persistence.js:150 (any truthy newValue marks the tab stale). The diff filters the sentinel at the announce site, the single place the value enters the cross-tab channel. Approved.
