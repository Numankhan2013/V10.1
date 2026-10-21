# BUG-01-001 — Restore-point pruning drops manual points after 12 even within two weeks

- **Area:** 01 persistence & sync
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/assets/nk-store.js:156`, `app/src/main/assets/nk-store.js:163`
- **Introduced by:** unknown

## What happens

Automatic pruning keeps manual/before-restore/before-reset/migration restore points only if there are fewer than 12 of them, even when they are all younger than the two-week retention window. A learner who creates 13 restore points in two weeks silently loses the oldest one.

## Evidence

```js
// nk-store.js
var SNAPSHOT_EVERY = 30 * 60 * 1000, RECENT_KEEP = 12, DAILY_KEEP = 14;
...
function prune(tx) {
  ...
  all.forEach(function (item) {
    // Points taken before a reset, restore or migration stay for two weeks.
    if (item.reason !== 'auto') { if (item.at > Date.now() - DAILY_KEEP * 864e5 && marked < RECENT_KEEP) { marked++; keep.add(item.id); } return; }
    ...
```

`marked` is a shared counter across all non-auto reasons and is capped by `RECENT_KEEP` (12). The comment promises two-week retention (`DAILY_KEEP * 864e5`), so the count cap contradicts the stated policy.

## Learner impact

A safety net meant to allow undoing a reset/restore/migration can be missing when needed. Data loss of a restore point, not of study progress itself.

## Root cause

The non-auto branch reuses `RECENT_KEEP` as a count limit in addition to the 14-day age limit. The age check alone implements the documented two-week retention.

## Proposed fix

```diff
--- a/app/src/main/assets/nk-store.js
+++ b/app/src/main/assets/nk-store.js
@@ -160,6 +160,6 @@
       var dayAgo = Date.now() - 864e5, recent = 0, marked = 0;
       all.forEach(function (item) {
         // Points taken before a reset, restore or migration stay for two weeks.
-        if (item.reason !== 'auto') { if (item.at > Date.now() - DAILY_KEEP * 864e5 && marked < RECENT_KEEP) { marked++; keep.add(item.id); } return; }
+        if (item.reason !== 'auto') { if (item.at > Date.now() - DAILY_KEEP * 864e5) keep.add(item.id); return; }
         if (item.at > dayAgo && recent < RECENT_KEEP) { recent++; keep.add(item.id); return; }
         var day = new Date(item.at).toDateString();
         if (!days.has(day) && days.size < DAILY_KEEP) { days.add(day); keep.add(item.id); }```

## Verification

- Create 15 restore points (snapshot('manual')) within 14 days; reopen restore sheet; all 15 should list.
- Existing `tools/test_cross_device_sync_v1.py` and `verify_progress_store_browser.py` should remain green.

## Alternatives considered

Keeping the 12 cap but raising it would still drop points eventually; the documented policy is time-based, so removing the count cap matches intent.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Evidence re-checked at nk-store.js:156-163: the non-auto branch caps on a shared `marked < RECENT_KEEP` counter on top of the 14-day age test, so the 13th manual point inside the window is dropped. The proposed diff removes only the count cap and keeps the age test, which matches the code comment (points taken before a reset, restore or migration stay for two weeks). Approved.
