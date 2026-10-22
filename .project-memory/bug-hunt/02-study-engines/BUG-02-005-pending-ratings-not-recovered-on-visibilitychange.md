# BUG-02-005 — Pending FSRS ratings are not recovered when the tab is hidden

- **Area:** 02 study engines
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit pending (this commit)
- **Files:** `app/src/main/modules/continue_practice_resume.js:419`
- **Introduced by:** unknown

## What happens

The `visibilitychange` handler flushes elapsed time and saves state when the tab is hidden, but it does not commit pending FSRS ratings. The `pagehide` handler does commit them via `nkFsrsRecoverPending()`. If the browser discards the hidden tab without firing `pagehide`, any pending correct-answer rating is lost.

## Evidence

```js
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&typeof nkFlushLifecycleState==='function')nkFlushLifecycleState();});
window.addEventListener('pagehide',()=>{if(typeof nkFlushLifecycleState==='function')nkFlushLifecycleState();});
```

Elsewhere the fsrs scheduler explicitly commits pending ratings on pagehide:

```js
window.addEventListener('pagehide',()=>nkFsrsRecoverPending());
```

`nkFlushLifecycleState` (durable_persistence.js) only saves elapsed time and state; it never calls `nkFsrsRecoverPending`.

## Learner impact

Data loss: a correct answer whose rating was still pending can be missing from FSRS if the tab is killed while hidden, so it will not be scheduled for review.

## Root cause

Inconsistent lifecycle handling: `pagehide` commits pending ratings, `visibilitychange` does not.

## Proposed fix

```diff
--- a/app/src/main/modules/continue_practice_resume.js
+++ b/app/src/main/modules/continue_practice_resume.js
@@ -416,6 +416,6 @@
       else{route={page:'exam',id:null};try{history.replaceState(null,'','#exam');}catch(_){}}
     }
     if(typeof nkStorageBootNotice!=='undefined'&&nkStorageBootNotice)setTimeout(()=>nkStorageError(nkStorageBootNotice),0);
-    document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&typeof nkFlushLifecycleState==='function')nkFlushLifecycleState();});
+    document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'){if(typeof nkFsrsRecoverPending==='function')nkFsrsRecoverPending();if(typeof nkFlushLifecycleState==='function')nkFlushLifecycleState();}});
     window.addEventListener('pagehide',()=>{if(typeof nkFlushLifecycleState==='function')nkFlushLifecycleState();});
     nkPracticeCheckpoints(true).forEach(saved=>{if(!state.activeSession&&saved.lifecycle==='active'){nkPracticeStoreCheckpoint({...saved,lifecycle:'paused',updatedAt:Date.now()});changed=true;}});
     if(changed)saveState();```

## Verification

- Answer a question correctly, switch tabs or background the app, then kill the process. Confirm the pending rating was committed and the question appears in FSRS.
- Existing tests: `test_fsrs_v1.py`, `test_question_interaction_integrity.py`.

## Alternatives considered

Committing pending ratings inside `nkFlushLifecycleState` would also fix `pagehide`, but that risks double-commit ordering; keeping the explicit call matches the existing pagehide behavior.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified continue_practice_resume.js:419 (visibilitychange calls only nkFlushLifecycleState) against fsrs_scheduler.js:256 (pagehide calls nkFsrsRecoverPending) and durable_persistence.js nkFlushLifecycleState (which saves elapsed time and state but never commits pending ratings). The diff adds the recovery call to the hidden branch. Approved. Note that visibilitychange also fires before pagehide on a normal close, so the fix is idempotent with the existing pagehide handler.
