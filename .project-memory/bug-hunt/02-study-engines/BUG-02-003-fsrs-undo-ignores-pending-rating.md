# BUG-02-003 — FSRS "Undo most recent rating" ignores an uncommitted pending rating

- **Area:** 02 study engines
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit pending (this commit)
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
@@ -193,7 +193,7 @@
   function nkFsrsTopicOptions(subject){const item=SUBJECTS.find(s=>s.subject===subject),select=document.getElementById('nk-fsrs-topic');if(!select)return;select.innerHTML='<option value="">All topics</option>'+((item?.topics||[]).map(t=>`<option value="${esc(t.id)}">${esc(t.title||t.name)}</option>`).join(''));}
   function nkFsrsQueueDialog(){navigate('fsrs');}
   function nkFsrsUndo(){
-    let hit=null,qid=null;Object.keys(state.attempts||{}).forEach(id=>{
+    nkFsrsRecoverPending();
    let hit=null,qid=null;Object.keys(state.attempts||{}).forEach(id=>{
       const active=nkFsrsActiveAttempts(id),ids=new Set(active.map(a=>String(a.id))),edits=state.fsrsRatingRevisions?.[id]||[],undone=new Set(edits.filter(a=>a.isUndo).map(a=>String(a.undoOf)));
       [...active,...edits.filter(a=>!a.isUndo&&!undone.has(String(a.id))&&ids.has(String(a.ratingOf)))].forEach(a=>{if(!hit||Number(a.at)>Number(hit.at)||(Number(a.at)===Number(hit.at)&&String(a.id)>String(hit.id))){hit=a;qid=id;}});
     });if(!hit){showToast('Nothing to undo.');return;}
```

## Verification

- Answer a question correctly (creating a pending rating), then invoke Undo without navigating. Confirm the pending rating is committed first and then undone, leaving no pending rating.
- Existing tests: `test_fsrs_v1.py`, `test_fsrs_audit_v1.py`, `test_question_interaction_integrity.py`.

## Alternatives considered

Disabling Undo while pending ratings exist would hide the action unnecessarily; flushing first matches the Pause behavior.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** The finding is correct and the patch was reworked during review, because the version first proposed did not work.

The finding: `nkFsrsUndo` iterates only `state.attempts` and `state.fsrsRatingRevisions`, while a correct Practice answer sits in `state.activeSession.pendingRating` until it is committed on navigation, Pause or session end. `nkPausePractice` already calls `nkFsrsRecoverPending()` first (`question_interaction.js:131`); `nkFsrsUndo` did not.

The first proposed patch put `nkFsrsRecoverPending()` as the first statement *inside* the `Object.keys(state.attempts||{}).forEach(...)` callback. That is wrong in a way the original evidence did not show: the key list is snapshotted when the callback is created, so when `state.attempts` is empty the callback never runs and the pending rating is never committed at all. The learner's very first correct answer — the case with no prior attempt — would still lose the undo. `tools/test_fsrs_audit_v1.py` now carries two scenarios for this, and the in-loop version fails the first:

```
FAIL - S7c undo commits a pending rating on a question with no prior attempt ::
  undo must not leave the pending rating behind
```

The approved patch calls `nkFsrsRecoverPending()` before the key list is taken, so the pending rating is committed and then visible to the same undo pass. Both new scenarios pass with it (S7b: undo removes the rating it just committed and leaves the older one; S7c: undo removes a pending rating on a question with no prior attempt), and the 58 existing audit scenarios still pass.

Approved. The bug file carries the corrected diff.
