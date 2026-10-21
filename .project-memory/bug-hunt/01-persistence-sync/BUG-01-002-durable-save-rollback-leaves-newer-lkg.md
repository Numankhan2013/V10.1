# BUG-01-002 — A failed state save can leave last-known-good newer than the restored primary

- **Area:** 01 persistence & sync
- **Severity:** high
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/modules/durable_persistence.js:150`, `app/src/main/modules/durable_persistence.js:163`, `app/src/main/modules/durable_persistence.js:169`
- **Introduced by:** unknown

## What happens

When a save fails after the last-known-good (LKG) copy has already been written, or when the pending-key removal fails, the rollback does not restore LKG and can stop halfway. The LKG copy can then keep the failed revision, so the next load recovers the write that was supposed to have failed.

## Evidence

Reproduced with a storage adapter whose `removeItem` throws for `qbank_state_pending_v2`:

```js
// adapter: removeItem throws only for qbank_state_pending_v2
const ok = nkDurablePersist(state, 'test'); // => false
// primary rev: 6 (should be 5), lkg rev: 6 (should be 5), pending exists: true
```

Relevant code:

```js
const previousPrimary = store.getItem(LS_KEY);
...
store.setItem(NK_STATE_PENDING_KEY, raw);
store.setItem(LS_KEY, raw);
const check = store.getItem(LS_KEY); if (check !== raw) throw new Error('primary verification failed');
store.setItem(NK_STATE_LKG_KEY, raw);
store.removeItem(NK_STATE_PENDING_KEY);
...
} catch (error) {
  try { store.removeItem(NK_STATE_PENDING_KEY); if (previousPrimary == null) store.removeItem(LS_KEY); else store.setItem(LS_KEY, previousPrimary); } catch (_) {}
  ...
}
```

If `store.removeItem(NK_STATE_PENDING_KEY)` throws, the inner `try/catch` swallows it and skips restoring the primary. LKG is never restored at all. Even in the success path for LKG, a later failure leaves LKG at the new revision.

## Learner impact

A save reported as failed can still become durable progress, and a partially failed transaction can leave pending/primary/LKG inconsistent. This is data-integrity corruption, not just a failed save.

## Root cause

Rollback captures only `previousPrimary`, not the previous LKG, and performs all rollback steps in one `try` whose first failing operation aborts the rest. There is no per-step isolation and no restoration of LKG.

## Proposed fix

```diff
--- a/app/src/main/modules/durable_persistence.js
+++ b/app/src/main/modules/durable_persistence.js
@@ -150,6 +150,7 @@
   function nkDurablePersist(candidate,reason='state save'){
     if(nkOtherTabNewer){nkStorageStaleTab();return false;}
     const store=nkStorageAdapter(),previousPrimary=store.getItem(LS_KEY);
+    const previousLkg=store.getItem(NK_STATE_LKG_KEY);
     try{
       nkMirrorNormalPracticeCheckpoint(candidate);nkPrepareTimedSession(candidate);
       // Normalize makes a new root object and never mutates its input. Avoid a
@@ -166,7 +167,9 @@
       candidate.stateSchemaVersion=next.stateSchemaVersion;candidate.stateRevision=next.stateRevision;candidate.normalPracticeCheckpoints=next.normalPracticeCheckpoints;candidate.normalPracticeCheckpoint=next.normalPracticeCheckpoint;
       nkStorageClearError();return true;
     }catch(error){
-      try{store.removeItem(NK_STATE_PENDING_KEY);if(previousPrimary==null)store.removeItem(LS_KEY);else store.setItem(LS_KEY,previousPrimary);}catch(_){}
+      try{store.removeItem(NK_STATE_PENDING_KEY);}catch(_){}
+      try{if(previousPrimary==null)store.removeItem(LS_KEY);else store.setItem(LS_KEY,previousPrimary);}catch(_){}
+      try{if(previousLkg==null)store.removeItem(NK_STATE_LKG_KEY);else store.setItem(NK_STATE_LKG_KEY,previousLkg);}catch(_){}
       nkStorageError(`Progress was not saved during ${reason}. Nothing destructive was completed`,error);return false;
     }
   }
```

## Verification

- Re-run the reproduction adapter above; result should still be `false`, but primary, LKG, and pending should all return to their pre-save values.
- Run `python3 tools/test_cross_device_sync_v1.py` (durable persistence scenario).

## Alternatives considered

Aborting the whole save earlier (validating before any write) already happens for normalization, but storage writes can still fail; per-step rollback is the smallest robust containment.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Re-read durable_persistence.js:152-170. The catch block restores the primary inside one try, so a throwing removeItem aborts the primary restore as well, and the LKG written at line 165 is never rolled back. The diff isolates each rollback step and adds the missing LKG restore. Approved. Implementer note: capture previousLkg before the try block, as the diff does.
