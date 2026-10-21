# BUG-02-004 — Timed-test expiry is rolled back when triggered by manual navigation

- **Area:** 02 study engines
- **Severity:** medium
- **Confidence:** medium
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/assets/index.html:873`
- **Introduced by:** unknown

## What happens

`nkStrictBeforeNavigation()` returns `false` after calling `nkExpireTopicQuestion()` when the current question's 60 seconds have elapsed. The strict `nextQ`/`prevQ`/`goIndex` wrappers call it inside a `nkQuestionTransaction` (question_interaction). When the wrapped action returns `false`, the transaction restores `state` to its pre-action clone, discarding the expiry's in-memory state changes. Although `nkExpireTopicQuestion()` schedules its own save/render, the transaction's restore and subsequent render can revert the expired state, so a learner clicking Next/Previous/Go at expiry may see no expiry.

## Evidence

```js
function nkStrictBeforeNavigation(){const s=state.activeSession;if(s?.mode!=='exam'||s.timerMode!=='per-question')return true;if(nkStrictSpent(s,String(s.questionIds[s.index]))>=60000){nkExpireTopicQuestion();return false;}nkStrictCommitCurrent();return true;}
```

and the wrappers:

```js
nextQ=nkQuestionAction(nextQ); // nkQuestionAction wraps in nkQuestionTransaction
```

`nkQuestionTransaction` does `if(result===false){state=before;return false;}`.

## Learner impact

A timed topic test may not advance/expire on a manual tap at the 60-second boundary; the timer can appear stuck. Automatic expiry (the 250 ms ticker) still works, so this is a recoverable edge case.

## Root cause

Expiry side effects are executed synchronously inside a transaction that reverts state on `false`.

## Proposed fix

```diff
--- a/app/src/main/assets/index.html
+++ b/app/src/main/assets/index.html
@@ -870,6 +870,6 @@
     if(remaining<0){saveState();submitExam(true);return true;}
     s.index=remaining;s.questionEnteredAt=Date.now();s.strictQuestionStartedAt=s.questionEnteredAt;saveState();render();return true;
   }
-  function nkStrictBeforeNavigation(){const s=state.activeSession;if(s?.mode!=='exam'||s.timerMode!=='per-question')return true;if(nkStrictSpent(s,String(s.questionIds[s.index]))>=60000){nkExpireTopicQuestion();return false;}nkStrictCommitCurrent();return true;}
+  function nkStrictBeforeNavigation(){const s=state.activeSession;if(s?.mode!=='exam'||s.timerMode!=='per-question')return true;if(nkStrictSpent(s,String(s.questionIds[s.index]))>=60000){setTimeout(()=>nkExpireTopicQuestion(),0);return false;}nkStrictCommitCurrent();return true;}
   const nkHomeNextQ=nextQ;nextQ=function(){if(!nkStrictBeforeNavigation())return false;const out=nkHomeNextQ.apply(this,arguments);nkStrictResetClock();return out;};
   const nkHomePrevQ=prevQ;prevQ=function(){if(!nkStrictBeforeNavigation())return false;const out=nkHomePrevQ.apply(this,arguments);nkStrictResetClock();return out;};
   const nkHomeGoIndex=goIndex;goIndex=function(){if(!nkStrictBeforeNavigation())return false;const out=nkHomeGoIndex.apply(this,arguments);nkStrictResetClock();return out;};```

## Verification

- In a per-question timed test, wait until the current question reaches 60 s, then tap Next. Confirm the question expires and advances instead of reverting.
- Existing tests: `test_timed_resume_card_v1.py`, `test_timed_abandon_grid_v1.py`.

## Alternatives considered

Removing the transaction wrapper from strict navigation would also fix the revert but risks losing the durable-save guarantee; deferring expiry is the smaller containment.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** The mechanism is real and correctly identified: nkStrictBeforeNavigation (index.html:873) calls nkExpireTopicQuestion() and returns false, and the three wrappers that call it (index.html:874-876) are each wrapped by nkQuestionAction in question_interaction.js:122-124, so the expiry runs inside nkQuestionTransaction, whose if(result===false){state=before;return false;} at question_interaction.js:88 discards the expiry's state changes. The patch was reworked during review to name the exact call site and to state that the automatic ticker path (index.html:1948) and the other three expiry call sites are outside a transaction and unaffected; the setTimeout containment moves the expiry past the transaction restore. Approved. Severity medium and confidence medium are right: the window is a single tap at the 60-second boundary and the automatic expiry still works.
