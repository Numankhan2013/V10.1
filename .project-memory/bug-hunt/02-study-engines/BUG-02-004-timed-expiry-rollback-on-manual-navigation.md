# BUG-02-004 — Timed-test expiry is rolled back when triggered by manual navigation

- **Area:** 02 study engines
- **Severity:** medium
- **Confidence:** medium
- **Status:** fix applied — commit pending (this commit)
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
@@ -870,7 +870,7 @@
     if(remaining<0){saveState();submitExam(true);return true;}
     s.index=remaining;s.questionEnteredAt=Date.now();s.strictQuestionStartedAt=s.questionEnteredAt;saveState();render();return true;
   }
-  function nkStrictBeforeNavigation(){const s=state.activeSession;if(s?.mode!=='exam'||s.timerMode!=='per-question')return true;if(nkStrictSpent(s,String(s.questionIds[s.index]))>=60000){nkExpireTopicQuestion();return false;}nkStrictCommitCurrent();return true;}
+  function nkStrictBeforeNavigation(){const s=state.activeSession;if(s?.mode!=='exam'||s.timerMode!=='per-question')return true;if(nkStrictSpent(s,String(s.questionIds[s.index]))>=60000){setTimeout(()=>nkExpireTopicQuestion(),0);return false;}nkStrictCommitCurrent();return true;}
   const nkHomeNextQ=nextQ;nextQ=function(){if(!nkStrictBeforeNavigation())return false;const out=nkHomeNextQ.apply(this,arguments);nkStrictResetClock();return out;};
   const nkHomePrevQ=prevQ;prevQ=function(){if(!nkStrictBeforeNavigation())return false;const out=nkHomePrevQ.apply(this,arguments);nkStrictResetClock();return out;};
   const nkHomeGoIndex=goIndex;goIndex=function(){if(!nkStrictBeforeNavigation())return false;const out=nkHomeGoIndex.apply(this,arguments);nkStrictResetClock();return out;};
--- a/tools/test_topic_timer_v1.py
+++ b/tools/test_topic_timer_v1.py
@@ -50,7 +50,25 @@
 assert.equal(submitted.session.strictQuestionTime.p3,60000);
 assert.equal(submitted.session.questionTimes.p3,60000);
 assert(saves>3&&renders>3);
-console.log('TOPIC_TIMER_OK cumulative=true reload=true lock=true final=true');
+// A manual navigation at expiry must not lose the expiry. The interaction
+// transaction restores the state when the action returns false, so the expiry
+// has to run after that restore, not before it.
+const timers=[];
+const realSetTimeout=globalThis.setTimeout;
+globalThis.setTimeout=(fn,ms)=>{timers.push(fn);return timers.length;};
+const nkInnerNextQ=nextQ;
+nextQ=function(){const before=JSON.parse(JSON.stringify(state));const out=nkInnerNextQ.apply(this,arguments);if(out===false)state=before;return out;};
+state.activeSession={id:'topic-test',questionIds:[...ids],mode:'exam',title:'Topic Test',index:0,answers:{},questionTimes:{},startedAt:now,questionEnteredAt:now,timerMode:'per-question',strictExpired:{},strictQuestionTime:{}};
+now+=60000;
+const navResult=nextQ();
+assert.equal(navResult,false,'navigation at expiry must be refused');
+assert.equal(timers.length,1,'the expiry must be deferred past the transaction restore');
+timers.forEach(fn=>fn());
+assert.equal(state.activeSession.strictExpired.p1,true,'the expiry must survive the navigation transaction');
+assert.equal(state.activeSession.index,1,'the expired question must be left behind');
+globalThis.setTimeout=realSetTimeout;
+
+console.log('TOPIC_TIMER_OK cumulative=true reload=true lock=true final=true expiry_survives_navigation=true');
 '''
     subprocess.run(['node', '-e', script], check=True, cwd=ROOT)
 
```

## Verification

- In a per-question timed test, wait until the current question reaches 60 s, then tap Next. Confirm the question expires and advances instead of reverting.
- Existing tests: `test_timed_resume_card_v1.py`, `test_timed_abandon_grid_v1.py`.

## Alternatives considered

Removing the transaction wrapper from strict navigation would also fix the revert but risks losing the durable-save guarantee; deferring expiry is the smaller containment.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** The finding is correct and the proposed patch is right.

`nkStrictBeforeNavigation` (index.html:873) calls `nkExpireTopicQuestion()` and then returns `false`. The strict `nextQ`/`prevQ`/`goIndex` wrappers run inside `nkQuestionTransaction` (question_interaction.js:82), and a `false` result makes the transaction restore the state to its pre-action clone (line 88). The expiry's in-memory changes — the expired flag, the 60-second time and the move to the next question — are therefore thrown away, and the subsequent render shows the un-expired question. The learner clicks Next at expiry and nothing happens.

The applied patch defers the expiry by one task, so it runs after the transaction has restored the state:

```js
if(nkStrictSpent(s,String(s.questionIds[s.index]))>=60000){setTimeout(()=>nkExpireTopicQuestion(),0);return false;}
```

The expiry then does its own save and render on the restored state, which is the state the learner should be in.

`tools/test_topic_timer_v1.py` now models the transaction: it wraps the timer's `nextQ` so that a `false` result restores a pre-action clone, makes the question's 60 seconds elapse, and asserts that the navigation is refused, that the expiry was deferred rather than run inline, and that the expired question is left behind once the deferred expiry runs. On the pre-fix page the assertion "the expiry must be deferred past the transaction restore" fails.
