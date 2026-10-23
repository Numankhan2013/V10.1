# BUG-02-001 — Practice "topic remaining" start mutates an in-progress timed test

- **Area:** 02 study engines
- **Severity:** high
- **Confidence:** high
- **Status:** fix applied — commit 4c3ae32f
- **Files:** `app/src/main/modules/continue_practice_resume.js:172-184`
- **Introduced by:** unknown

## What happens

When a learner has a timed CBT in progress and Home/Topics offers a "practice remaining questions" continuation, `nkPracticeOpenContext(..., true)` calls `startSession(...)`. `startSession` refuses to replace the timed test and opens the timed-test conflict modal, but the code then unconditionally writes `lifecycle`, `sessionQuestionIds`, and `practiceContext` onto whatever `state.activeSession` currently is — the timed exam session — and saves it. The timed test's identity and question list are corrupted in persisted state.

## Evidence

```js
startSession(ids,'practice',context.title||`${context.subject} Practice`);
const s=state.activeSession;if(s){s.lifecycle='active';s.sessionQuestionIds=[...ids];s.practiceContext={subject:context.subject,bank:context.bank,topicId:context.topicId,title:context.title,questionIds:[...ids]};saveState();}
```

`startSession` (replaced by `nkStartSessionReliably`) returns `false` and leaves the exam session in place when a timed test is active (`nkOfferTimedSessionDecision`), but the return value is never checked here, unlike `nkStartTopicTimedTest`, `nkCbtStart`, and `nkQuestionSearchStart`, which all guard on `started===false`.

## Learner impact

Data loss/corruption: an in-progress timed test can have its question list and lifecycle overwritten by a Practice session that never started, and the corruption is saved. The test may become unresumable or submit the wrong questions.

## Root cause

Missing return-value check before mutating `state.activeSession`; the code assumes `startSession` always succeeds.

## Proposed fix

```diff
--- a/app/src/main/modules/continue_practice_resume.js
+++ b/app/src/main/modules/continue_practice_resume.js
@@ -174,7 +174,8 @@
     if(start){
       const ids=[...(context.questionIds||[])];if(!ids.length)return navigate('study-library');
       if(typeof openBank==='function'&&context.bank)openBank(context.subject,context.bank);else if(typeof openSubjectTopics==='function')openSubjectTopics(context.subject);
-      startSession(ids,'practice',context.title||`${context.subject} Practice`);
-      const s=state.activeSession;if(s){s.lifecycle='active';s.sessionQuestionIds=[...ids];s.practiceContext={subject:context.subject,bank:context.bank,topicId:context.topicId,title:context.title,questionIds:[...ids]};saveState();}
+      const started=startSession(ids,'practice',context.title||`${context.subject} Practice`);
+      if(started===false)return false;
+      const s=state.activeSession;if(s&&s.mode==='practice'){s.lifecycle='active';s.sessionQuestionIds=[...ids];s.practiceContext={subject:context.subject,bank:context.bank,topicId:context.topicId,title:context.title,questionIds:[...ids]};if(saveState()===false)return false;}
       return;
     }
     if(typeof nkOpenSubjectChapter==='function')return nkOpenSubjectChapter(context.subject,context.bank,context.topicId);```

## Verification

- Start a timed CBT, then trigger a "practice remaining" continuation (Home focus / Topics). Confirm the conflict modal appears and the exam session's `questionIds`/`lifecycle` are unchanged after save/reload.
- Existing tests: `test_continue_practice_resume_v1.py`, `test_timed_resume_card_v1.py`.

## Alternatives considered

Pausing the timed test automatically would change the accepted abandon/resume contract; guarding the mutation is the smallest safe fix.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified continue_practice_resume.js:177-178: startSession is nkStartSessionReliably (assigned at line 328), which returns false and leaves the exam session in place when an exam is live (lines 312-315), and the call site then writes lifecycle/sessionQuestionIds/practiceContext onto whatever activeSession is and saves. The diff checks the return value and also requires mode==='practice' before mutating. Approved: this is a real corruption path and the fix is minimal.
