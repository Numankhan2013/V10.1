# BUG-02-003 — FSRS "Undo most recent rating" ignores an uncommitted pending rating

- **Area:** 02 study engines
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/modules/fsrs_scheduler.js:195-205`, `app/src/main/modules/question_interaction.js:128`
- **Introduced by:** unknown

## What happens

A correct Practice answer is not committed to FSRS immediately; it is held in `state.activeSession.pendingRating` and committed on navigation, Pause, or session finish. `nkFsrsUndo()` searches only committed attempts (`state.attempts` / `state.fsrsRatingRevisions`), so while a pending rating exists it undoes an older committed rating instead, and leaves the pending rating in place. After the next navigation the pending rating is committed, overwriting the undo's effect.

## Evidence

`nkFsrsUndo()` loops over `state.attempts` and `state.fsrsRatingRevisions` only:

```js
Object.keys(state.attempts||{}).forEach(id=>{
  const active=nkFsrsActiveAttempts(id), ...
```

By contrast `nkPausePractice` is explicitly wrapped to call `nkFsrsRecoverPending()` first:

```js
nkPausePractice=nkQuestionAction(function(){nkFsrsRecoverPending(); ...});
```

`nkFsrsUndo` has no such recovery, even though it is wrapped by `nkQuestionAction(nkFsrsUndo)`.

## Learner impact

Wrong scored answer / wrong schedule: Undo can target the wrong rating, and the pending rating is committed afterwards, so the learner's intended undo is lost.

## Root cause

Pending FSRS ratings are not flushed before selecting the undo target.

## Proposed fix

```diff
--- a/app/src/main/modules/fsrs_scheduler.js
+++ b/app/src/main/modules/fsrs_scheduler.js
@@ -194,5 +194,6 @@
   function nkFsrsQueueDialog(){navigate('fsrs');}
   function nkFsrsUndo(){
     let hit=null,qid=null;Object.keys(state.attempts||{}).forEach(id=>{
+    nkFsrsRecoverPending();
       const active=nkFsrsActiveAttempts(id),ids=new Set(active.map(a=>String(a.id))),edits=state.fsrsRatingRevisions?.[id]||[],undone=new Set(edits.filter(a=>a.isUndo).map(a=>String(a.undoOf)));
       [...active,...edits.filter(a=>!a.isUndo&&!undone.has(String(a.id))&&ids.has(String(a.ratingOf)))].forEach(a=>{if(!hit||Number(a.at)>Number(hit.at)||(Number(a.at)===Number(hit.at)&&String(a.id)>String(hit.id))){hit=a;qid=id;}});
     });if(!hit){showToast('Nothing to undo.');return;}```

## Verification

- Answer a question correctly (creating a pending rating), then invoke Undo without navigating. Confirm the pending rating is committed first and then undone, leaving no pending rating.
- Existing tests: `test_fsrs_v1.py`, `test_fsrs_audit_v1.py`, `test_question_interaction_integrity.py`.

## Alternatives considered

Disabling Undo while pending ratings exist would hide the action unnecessarily; flushing first matches the Pause behavior.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified fsrs_scheduler.js:195 (nkFsrsUndo iterates only state.attempts and state.fsrsRatingRevisions), :158 (nkFsrsRecoverPending commits state.activeSession.pendingRating), and question_interaction.js:131 (nkPausePractice calls nkFsrsRecoverPending first). The Undo control is exposed on the FSRS settings page (fsrs_scheduler.js:235) and is reachable while a practice session is still live, so a pending rating can exist at that moment. The diff flushes first, matching the Pause behaviour. Approved.
