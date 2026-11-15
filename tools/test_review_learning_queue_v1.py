#!/usr/bin/env python3
"""Behavior tests for the due-review learning queue and advance-after-rating
(review_learning_queue.js), see docs/FSRS.md "Learning cards in a due review".

The session logic runs in Node against the real FSRS scheduler (ts-fsrs 5.4.2),
the real durable checkpoint code, Continue Practice (pause / resume / finish),
the Revision session module (due kind, answered-only finish), the not-studied
flag module and the page's own submitPractice / nextQ / prevQ / goIndex /
finishPracticeSession declarations, installed in the page's order. The clock,
Math.random and timers are driven by the test.

A second run drives the checkpoint merge of cross_device_sync.js and the
durable checkpoint normaliser directly: round history and the learning queue
round-trip, the copy with more rounds wins, and payloads without them load.
"""

from pathlib import Path
import subprocess
import tempfile

from app_page import app_page, app_css
from js_extract import extract_function
from test_not_studied_flags_v1 import PRELUDE

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "app/src/main/modules"
MODULE = MODULES / "review_learning_queue.js"
HTML = ROOT / "app/src/main/assets/index.html"
VENDOR = ROOT / "app/src/main/assets/vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js"

EXTRA = r'''
// Timers are queued and flushed by the test (the advance waits ~250 ms).
let TIMERS=[],TIMER_ID=0;global.setTimeout=(fn,ms)=>{const id=++TIMER_ID;TIMERS.push({id,fn,ms});return id;};global.clearTimeout=id=>{TIMERS=TIMERS.filter(t=>t.id!==id);};
function flushTimers(){const run=TIMERS;TIMERS=[];run.forEach(t=>t.fn());}
let reviewSheets=0,dialogs=[];
openSessionReview=()=>{reviewSheets++;};
// The page's own header (nkSessionHeader below) with a bookmark stub; the action bar keeps the page's Previous button.
function bookmarkButton(qid){return `<button class="icon-btn bookmark-toggle" aria-pressed="${Boolean(state.bookmarks?.[qid])}"></button>`;}
practiceActionBar=s=>`<div class="fixed-actions nk-session-footer"><div class="fixed-actions-inner"><button class="ghost-btn" onclick="window.QB.prevQ()" ${s.index===0?'disabled':''}>Previous</button><button class="primary-btn" onclick="window.QB.nextQ()">Next</button></div></div>`;
qAttempts=id=>Array.isArray(state.attempts?.[id])?state.attempts[id]:[];
document.body.insertAdjacentHTML=(where,html)=>{dialogs.push(html);};
let nkStartRevisionQueue=()=>{},nkRevisionScope={subject:'',bank:'',topic:''};
function nkQuestionAction(fn){return fn;}
function nkValidQuestionOption(q,n){return Boolean(q)&&[1,2].includes(Number(n));}
function defaultState(){return {attempts:{},reviews:{},tests:[],bookmarks:{},questionNotes:{},studyModules:[],savedMocks:[],fsrsReviewEligible:{},activeSession:null};}
'''

SCENARIOS = r'''
nkFsrsInit();
const MIN=60000,DAY=86400000;
const IDS=['q1','q2','q3','q4'],SIX=['q1','q2','q3','q4','q5','q6'];
const S=()=>state.activeSession,pos=qid=>S().questionIds.indexOf(qid),go=qid=>{S().index=pos(qid);};
function reset(prefs){state={attempts:{},reviews:{},tests:[],fsrsPreferences:prefs||null,fsrsReviewEligible:{},activeSession:null,bookmarks:{},fsrsMigratedAt:1};routes=[];toasts=[];TIMERS=[];reviewSheets=0;dialogs=[];route={page:'practice'};at(0);}
// Earlier study: every question answered correctly once on day 0, so all are review cards due on day 5.
function history(ids=IDS){at(0);state.activeSession={id:'s0',mode:'practice',title:'Upper limb',questionIds:[...ids],sessionQuestionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:'normal',originRoute:'topics',lifecycle:'active'};
  ids.forEach((q,i)=>{at(1000+i*100);go(q);S().answers[q]=1;submitPractice();});nkFsrsRecoverPending();state.activeSession=null;}
// A due review exactly as revision_desk.js starts it (startSession + nkRevisionTagSession('due')).
function dueSession(id,ids,t){at(t);state.activeSession={id,mode:'practice',title:'Quick Revision · Due Review',questionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,lastTick:NOW,elapsedMs:0,questionEnteredAt:NOW,questionTimes:{},context:'fsrs'};
  assert(nkRevisionTagSession('due',null,ids),'tagged as a due review');return S();}
function ans(qid,choice,t,ms=20000){at(t);go(qid);S().questionTimes[qid]=ms;S().answers[qid]=choice;submitPractice();}
// Answer the card on screen (round 2+ moves by Next/Previous, never by row).
function here(choice,t,ms=20000){at(t);const qid=cur();S().questionTimes[qid]=ms;S().answers[qid]=choice;submitPractice();return qid;}
function rate(qid,r,t){at(t);return nkRateCurrent(r,qid,S().id);}
function next(t){at(t);return nextQ();}
const cur=()=>S().questionIds[S().index];
const round=qid=>(S().roundHistory?.[qid]?.length||0)+1;
const same=(a,b,msg)=>assert.strictEqual(JSON.stringify(a),JSON.stringify(b),msg);
const results=[];function scenario(name,fn){fn();results.push(name);}
const D5=5*DAY;
function setPrefs(p){Object.entries(p).forEach(([k,v])=>assert(nkFsrsSetSessionPreference(k,v),k));}
const header=()=>nkSessionHeader(BY_ID[cur()],S(),'practice');
const counter=()=>{const m=header().match(/<div class="nk-session-count[^"]*"[^>]*><strong>(\d+)<\/strong> \/ (\d+)/);return m?`${m[1]} / ${m[2]}`:null;};

scenario('settings: Round 2 at the end (default) or Off; the older "due" value means the end; per-field stamps; schedulers ignore them',()=>{
  reset();const p=nkFsrsPreferences();assert.strictEqual(p.learningInSession,'end');assert.strictEqual(p.advanceAfterRating,true);
  state.fsrsPreferences.learningInSession='due';assert.strictEqual(nkFsrsPreferences().learningInSession,'end','a value saved by an older build reads as the end');
  at(500);setPrefs({learningInSession:'off'});at(600);setPrefs({advanceAfterRating:'0'});
  assert.strictEqual(nkFsrsPreferences().learningInSession,'off');assert.strictEqual(nkFsrsPreferences().advanceAfterRating,false);
  same([state.fsrsPreferencesAt.learningInSession,state.fsrsPreferencesAt.advanceAfterRating],[T0+500,T0+600],'each field has its own stamp for sync');
  assert(!nkFsrsSetSessionPreference('learningInSession','sometimes'),'unknown modes are refused');
  state.fsrsPreferences.learningInSession='bogus';assert.strictEqual(nkFsrsPreferences().learningInSession,'end','a damaged value falls back to the default');
  history(['q1']);const a=state.attempts.q1[0];same(Object.keys(a.schedulerPreferences).sort(),['dailyCap','desiredRetention','maximumInterval'],'attempts record only scheduling values');
  nkFsrsDraft=null;const html=nkFsrsSettingsMarkup();
  assert(html.includes('Learning cards in a review session')&&html.includes('<option value="end"')&&html.includes('Round 2 at the end')&&html.includes('>Off</option>')&&!html.includes('value="due"'),'mode select');
  assert(html.includes('Advance after rating')&&html.includes('type="checkbox"')&&html.includes('role="switch"'),'advance switch');
  nkFsrsEditSetting('learningInSession','off');nkFsrsEditSetting('advanceAfterRating','1');at(900);assert(nkFsrsSaveSettings());
  assert.strictEqual(nkFsrsPreferences().learningInSession,'off');assert.strictEqual(nkFsrsPreferences().advanceAfterRating,true);assert.strictEqual(state.fsrsPreferencesAt.learningInSession,T0+900);
});

scenario('Round 2 holds only the cards that came due again: fresh, counted alone (1 / 2), Next/Previous/jumps stay inside it; Round 3 follows; then the sheet',()=>{
  reset();history(SIX);setPrefs({advanceAfterRating:false});dueSession('b2',SIX,D5);const hash=nkPracticeFindCheckpoint('b2').membershipHash;
  ans('q1',2,D5+1000);ans('q2',1,D5+2000);rate('q2',3,D5+2100);ans('q3',2,D5+3000);
  ['q4','q5','q6'].forEach((q,i)=>{ans(q,1,D5+4000+i*1000);rate(q,3,D5+4100+i*1000);});
  same(Object.keys(S().learningQueue).sort(),['q1','q3'],'the two misses wait for Round 2');
  assert.strictEqual(counter(),'6 / 6','round 1 counts the whole set');assert(!header().includes('nk-rlq-round'),'no badge in round 1');
  go('q2');next(D5+MIN);assert.strictEqual(cur(),'q3','round 1 goes on through the set');
  go('q6');next(D5+2*MIN);
  same(S().roundPass,{round:2,ids:['q1','q3']},'Round 2 is only the cards due again, earliest first');
  assert.strictEqual(cur(),'q1');assert(!S().answers.q1&&!S().submitted.q1&&!S().answers.q3&&!S().submitted.q3,'fresh and unanswered');
  ['q2','q4','q5','q6'].forEach(q=>assert(S().submitted[q]&&S().answers[q]===1,q+' keeps its round 1 answer and is not in Round 2'));
  same([S().roundHistory.q1[0].answer,S().roundHistory.q1[0].submitted,S().roundHistory.q1[0].correct],[2,true,false],'round 1 archived');
  same(S().questionIds,SIX,'membership is unchanged (no duplicate ids)');same(S().sessionQuestionIds,SIX);
  assert.strictEqual(counter(),'1 / 2','the counter counts only Round 2');
  const h=header();
  assert(/<div class="nk-session-count has-round"[^>]*><strong>1<\/strong> \/ 2<span class="nk-rlq-round">Round 2<\/span><\/div><div class="q-actions">/.test(h),'the badge sits inside the counter, right before the header actions: '+h);
  assert(h.includes('nk-ns-toggle')&&h.includes('bookmark-toggle')&&h.includes('nk-grid-trigger'),'flag, bookmark and grid stay in the header');
  assert(/aria-valuenow="50"><i style="width:50%"><\/i>/.test(h),'progress is the round position');
  assert(toasts.includes('Round 2 · 2 cards to relearn'));
  assert.strictEqual(prevQ(),false,'Previous does nothing on the first card of a round');assert.strictEqual(cur(),'q1');
  assert(/onclick="window\.QB\.prevQ\(\)" disabled/.test(practiceActionBar(S(),BY_ID.q1)),'and is disabled');
  assert.strictEqual(goIndex(pos('q2')),false,'a jump to a card outside the round is refused');assert.strictEqual(cur(),'q1');
  here(1,D5+3*MIN);assert(S().pendingRating.q1,'a correct round waits for its rating');assert.strictEqual(nkFsrsSessionRating('q1'),null,'round 1 is not this round\'s rating');
  rate('q1',3,D5+3*MIN+100);assert.strictEqual(state.reviews.q1.state,2,'Good graduates');assert(!S().learningQueue.q1);
  same([state.attempts.q1.at(-1).source,state.attempts.q1.at(-1).learningRound],['fsrs-review',2],'a normal FSRS attempt tagged as a repeat');
  next(D5+4*MIN);assert.strictEqual(cur(),'q3');assert.strictEqual(counter(),'2 / 2');
  assert(!/onclick="window\.QB\.prevQ\(\)" disabled/.test(practiceActionBar(S(),BY_ID.q3)),'Previous works after the first card');
  prevQ();assert.strictEqual(cur(),'q1');next(D5+4*MIN+100);assert.strictEqual(cur(),'q3');
  here(2,D5+5*MIN);assert(S().learningQueue.q3,'missed again');
  next(D5+6*MIN);same(S().roundPass,{round:3,ids:['q3']},'Round 3 is the one card still relearning');assert.strictEqual(counter(),'1 / 1');assert(header().includes('Round 3'));
  same(S().roundHistory.q3.map(r=>r.answer),[2,2],'both earlier rounds archived');
  here(1,D5+7*MIN);rate('q3',3,D5+7*MIN+100);next(D5+8*MIN);
  assert.strictEqual(reviewSheets,1,'nothing left: the session sheet');assert.strictEqual(S().roundPass.round,3,'no round 4');assert(!Object.keys(S().learningQueue).length);
  nkPracticeStoreCheckpoint(nkPracticeBuildCheckpoint(S(),'active'));assert.strictEqual(nkPracticeFindCheckpoint('b2').membershipHash,hash,'membershipHash unchanged');
  const cached=JSON.stringify(state.reviews.q3);nkFsrsReplay('q3');assert.strictEqual(JSON.stringify(state.reviews.q3),cached,'cache equals a replay of every round');
  // Finish: round 1 answers are the result; every round is in FSRS history; time adds up.
  at(D5+9*MIN);assert(nkFinishRevisionSession());const t=state.tests.at(-1);
  same(t.questionIds,SIX,'each question once');same([t.correct,t.incorrect,t.total],[4,2,6],'counted by round 1 (two misses)');
  same([t.answers.q1,t.answers.q3],[2,2],'round 1 answers intact');same([t.questionTimes.q1,t.questionTimes.q3],[40000,60000],'every round\'s time');
  same(state.attempts.q1.filter(a=>a.sessionId==='b2').map(a=>a.learningRound||1),[1,2]);same(state.attempts.q3.filter(a=>a.sessionId==='b2').map(a=>a.learningRound||1),[1,2,3]);
  assert.strictEqual(S(),null,'the session ended');same(nkFsrsQueue({}).due.map(q=>q.id).filter(id=>SIX.includes(id)),[],'nothing from the session is due again today: every relearning card graduated');assert(!('roundPass' in t)&&!('roundHistory' in t),'the result carries no round state');
  // Stats: accuracy counts one answer per question per session; study time keeps every round.
  const cs=chapterStats('c1'),expect=SIX.flatMap(id=>state.attempts[id]).filter(a=>!a.isUndo&&typeof a.correct==='boolean'&&!a.learningRound);
  same([cs.correct+cs.incorrect,cs.correct],[expect.length,expect.filter(a=>a.correct).length],'chapter accuracy skips the repeats');
  const hp=nkHomeProgressStats('year'),firsts=SIX.flatMap(id=>state.attempts[id]).filter(a=>typeof a.correct==='boolean'&&!a.learningRound);
  assert.strictEqual(Math.round(hp.accuracy*100),Math.round(firsts.filter(a=>a.correct).length/firsts.length*10000),'Home accuracy skips the repeats');
  assert.strictEqual(hp.studyMs,SIX.flatMap(id=>state.attempts[id]).reduce((n,a)=>n+Number(a.timeSpent||0),0),'Home study time keeps every round');
});
'''

SCENARIOS_2 = r'''
scenario('a round starts only when every card of the current one is answered (or flagged); an unanswered card opens the sheet instead',()=>{
  reset();history();setPrefs({advanceAfterRating:false});dueSession('u1',IDS,D5);
  ans('q1',2,D5+1000);ans('q3',1,D5+2000);rate('q3',3,D5+2100);ans('q4',1,D5+3000);rate('q4',3,D5+3100);
  go('q4');next(D5+MIN);assert.strictEqual(reviewSheets,1,'q2 unanswered: the sheet');assert(!S().roundPass,'no Round 2 yet');assert(S().submitted.q1,'q1 keeps its answer');
  ans('q2',1,D5+2*MIN);rate('q2',3,D5+2*MIN+100);go('q4');next(D5+3*MIN);same(S().roundPass,{round:2,ids:['q1']},'now Round 2');
  // In round 2 an unanswered card at the end also opens the sheet (no Round 3 over it).
  next(D5+4*MIN);assert.strictEqual(reviewSheets,2);assert.strictEqual(S().roundPass.round,2);
});

scenario('Hard on a relearning card keeps it for the next round; revising Hard to Good graduates it and only saves',()=>{
  reset();history(['q1','q2']);setPrefs({advanceAfterRating:false});dueSession('h1',['q1','q2'],D5);
  ans('q1',2,D5+1000);ans('q2',1,D5+2000);rate('q2',3,D5+2100);go('q2');next(D5+MIN);assert.strictEqual(cur(),'q1');
  here(1,D5+2*MIN);rate('q1',2,D5+2*MIN+100);assert.strictEqual(state.reviews.q1.state,3,'Hard on a relearning step stays relearning');assert(S().learningQueue.q1,'so it waits for round 3');
  const idx=S().index;at(D5+2*MIN+200);assert(nkRateCurrent(3,'q1',S().id));assert.strictEqual(S().index,idx,'no jump');assert.strictEqual(TIMERS.length,0,'no advance for a revision');
  assert.strictEqual(state.reviews.q1.state,2);assert(!S().learningQueue.q1,'graduated: out of the queue');
  next(D5+3*MIN);assert.strictEqual(reviewSheets,1,'no Round 3');assert.strictEqual(S().roundPass.round,2);
});

scenario('cards due later than the learn-ahead are never pulled in: a wait line offers Study now / Finish; Finish leaves them out',()=>{
  reset();history(['q1','q2']);setPrefs({advanceAfterRating:false});dueSession('w1',['q1','q2'],D5);
  ans('q1',2,D5+1000);S().learningQueue.q1.due=T0+D5+36*MIN;ans('q2',1,D5+MIN);rate('q2',3,D5+MIN+100);
  next(D5+2*MIN);assert.strictEqual(cur(),'q2','stays put');assert(!S().roundPass,'not pulled in');assert.strictEqual(reviewSheets,0);assert(S().submitted.q1,'q1 keeps round 1');
  assert(dialogs.at(-1).includes('1 learning card due in 34 min')&&dialogs.at(-1).includes('Study now')&&dialogs.at(-1).includes('Finish'),'the wait line');
  nkRlqFinish();assert.strictEqual(reviewSheets,1,'Finish opens the end-of-session sheet');
  at(D5+3*MIN);assert(nkFinishRevisionSession());const t=state.tests.at(-1);same([t.correct,t.incorrect],[1,1]);
  assert.strictEqual(state.attempts.q1.filter(a=>a.sessionId==='w1').length,1,'no extra FSRS review for the later card');
  // Study now pulls it in on request, as Round 2.
  reset();history(['q1','q2']);setPrefs({advanceAfterRating:false});dueSession('w2',['q1','q2'],D5);
  ans('q1',2,D5+1000);S().learningQueue.q1.due=T0+D5+36*MIN;ans('q2',1,D5+MIN);rate('q2',3,D5+MIN+100);next(D5+2*MIN);
  at(D5+3*MIN);nkRlqStudyNow();same(S().roundPass,{round:2,ids:['q1']});assert.strictEqual(cur(),'q1');
});

scenario('Off: one pass as before (no queue, no rounds, last Next opens the sheet)',()=>{
  reset();history();setPrefs({learningInSession:'off',advanceAfterRating:false});dueSession('o1',['q1','q2'],D5);
  ans('q1',2,D5+1000);assert.deepStrictEqual(S().learningQueue||{},{});ans('q2',1,D5+12*MIN);rate('q2',3,D5+12*MIN+1);
  go('q2');next(D5+30*MIN);assert.strictEqual(reviewSheets,1);assert(!S().roundHistory&&!S().roundPass,'no rounds');
});

scenario('pause / reload / resume in Round 2 keeps the round, its cards and the position; older or damaged checkpoints load safely',()=>{
  reset();history();setPrefs({advanceAfterRating:false});dueSession('p1',IDS,D5);const hash=nkPracticeFindCheckpoint('p1').membershipHash;
  ans('q1',2,D5+1000);ans('q2',2,D5+2000);ans('q3',1,D5+3000);rate('q3',3,D5+3100);ans('q4',1,D5+4000);rate('q4',3,D5+4100);go('q4');next(D5+MIN);
  same(S().roundPass,{round:2,ids:['q1','q2']});here(1,D5+2*MIN);rate('q1',3,D5+2*MIN+100);next(D5+3*MIN);assert.strictEqual(cur(),'q2');
  at(D5+3*MIN+100);assert(nkPausePractice());const cp=nkPracticeFindCheckpoint('p1');
  assert.strictEqual(cp.membershipHash,hash);same(cp.sessionQuestionIds,IDS);same(cp.roundPass,{round:2,ids:['q1','q2']});assert.strictEqual(cp.roundHistory.q1.length,1);
  assert(cp.questionUpdates.q2.signature.endsWith(',1]'),'a reopened round is a new edit of that question');
  state=JSON.parse(JSON.stringify(state));state.activeSession=null;at(D5+20*MIN);assert(nkResumePracticeById('p1'));
  assert.strictEqual(S().revisionQueueKind,'due');assert.strictEqual(cur(),'q2');same(S().roundPass,{round:2,ids:['q1','q2']});assert.strictEqual(counter(),'2 / 2');
  prevQ();assert.strictEqual(cur(),'q1','Previous stays in the round after resume');
  // A reload without pausing keeps the live session as saved.
  const raw=JSON.parse(localStorage.getItem(LS_KEY));same(raw.activeSession.roundPass,{round:2,ids:['q1','q2']},'saved with the session');
  const old=JSON.parse(JSON.stringify(cp));delete old.learningQueue;delete old.roundHistory;delete old.roundPass;old.sessionId='old1';old.lifecycle='paused';
  const norm=nkNormalizeCheckpoint(old);assert(norm&&!('learningQueue' in norm)&&!('roundHistory' in norm)&&!('roundPass' in norm),'no learning keys invented');
  const back=nkPracticeSessionFromCheckpoint(norm);assert(back&&!back.learningQueue&&!back.roundHistory&&!back.roundPass,'resumes as an ordinary session');
  const bad=nkNormalizeCheckpoint({...cp,learningQueue:{zz:{due:5},q3:{due:'x'}},roundHistory:{q9:[{answer:1}],q4:'x'},roundPass:{round:1,ids:['q1']},learningReturnIndex:99});
  assert(!bad.learningQueue&&!bad.roundHistory&&!bad.roundPass&&!('learningReturnIndex' in bad),'foreign ids, bad times, round 1 passes and out-of-range indexes are dropped');
  assert(!nkNormalizeCheckpoint({...cp,roundPass:{round:2,ids:['zz']}}).roundPass,'a pass of foreign cards is dropped');
  same(nkNormalizeCheckpoint({...cp,roundPass:{round:3,ids:['q2','q2','zz','q1']}}).roundPass,{round:3,ids:['q2','q1']},'repeats and foreign ids are cleaned');
  // A session saved by the earlier build (card reopened in its own row, return index) carries on.
  reset();history();setPrefs({advanceAfterRating:false});dueSession('l1',IDS,D5);ans('q1',2,D5+1000);
  S().roundHistory={q1:[{round:1,answer:2,submitted:true,timeMs:20000,reopenedAt:T0+D5+11*MIN}]};delete S().answers.q1;delete S().submitted.q1;delete S().learningQueue.q1;S().learningReturnIndex=1;go('q1');
  next(D5+12*MIN);assert.strictEqual(cur(),'q2','continues through the set');assert(!('learningReturnIndex' in S()));
});

scenario('advance after rating: first Hard/Good/Easy moves on after the pressed beat; never after a wrong answer',()=>{
  reset();history();dueSession('a1',['q1','q2','q3'],D5);
  ans('q1',1,D5+1000);rate('q1',3,D5+2000);assert.strictEqual(cur(),'q1','not yet: the pressed beat');assert.strictEqual(TIMERS.length,1);assert.strictEqual(TIMERS[0].ms,250);
  assert.strictEqual(rate('q1',4,D5+2100),false,'a double tap while the advance waits saves nothing');assert.strictEqual(nkFsrsSessionRating('q1').rating,3);
  at(D5+2250);flushTimers();assert.strictEqual(cur(),'q2','moved on');
  ans('q2',2,D5+3000);assert.strictEqual(TIMERS.length,0,'a wrong answer waits for Next');assert.strictEqual(cur(),'q2');
  at(D5+4000);goIndex(0);assert.strictEqual(cur(),'q1');assert(rate('q1',2,D5+4100));assert.strictEqual(TIMERS.length,0);assert.strictEqual(cur(),'q1');
  setPrefs({advanceAfterRating:false});goIndex(2);ans('q3',1,D5+5000);rate('q3',3,D5+5100);assert.strictEqual(TIMERS.length,0);
});

scenario('advance: stale timers never fire (moved, flagged, paused, session replaced); the last card ends the round',()=>{
  const start=()=>{reset();history();dueSession('a2',['q1','q2','q3'],D5);};
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);at(D5+1200);prevQ();goIndex(2);flushTimers();assert.strictEqual(cur(),'q3','moving by hand cancels the advance');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);const t=TIMERS[0];S().index=2;t.fn();assert.strictEqual(cur(),'q3','a timer that outlived its question does nothing');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);nkToggleNotStudied('q1',S().id);flushTimers();assert.strictEqual(cur(),'q1','flag toggled: no advance');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);const timer=TIMERS[0];at(D5+1200);nkPausePractice();assert.strictEqual(TIMERS.length,0,'pause clears it');timer.fn();assert.strictEqual(S().index,0,'a paused session never moves');assert.strictEqual(S().lifecycle,'paused');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);const t2=TIMERS[0];state.activeSession={...S(),id:'other'};t2.fn();assert.strictEqual(S().index,0,'another session: nothing');
  start();['q1','q2'].forEach((q,i)=>{ans(q,1,D5+1000+i*100);rate(q,3,D5+1050+i*100);flushTimers();});go('q3');ans('q3',1,D5+2000);rate('q3',3,D5+2100);flushTimers();assert.strictEqual(reviewSheets,1,'last card, nothing queued: the sheet');
  // A miss earlier in the set: the advance from the last card opens Round 2.
  start();ans('q1',2,D5+1000);ans('q2',1,D5+2000);rate('q2',3,D5+2100);flushTimers();ans('q3',1,D5+3000);rate('q3',3,D5+3100);flushTimers();
  same(S().roundPass,{round:2,ids:['q1']},'Round 2 after the last rating');assert.strictEqual(cur(),'q1');
  here(1,D5+4000);rate('q1',3,D5+4100);flushTimers();assert.strictEqual(reviewSheets,1,'the last card of Round 2 advances to the sheet');
});

scenario('not-studied flag: never queued; a card flagged in Round 2 leaves it without blocking the end; bookmarks work in Round 2',()=>{
  reset();history();setPrefs({advanceAfterRating:false});dueSession('f1',['q1','q2','q3'],D5);
  ans('q1',2,D5+1000);assert(S().learningQueue.q1);at(D5+1100);go('q1');nkToggleNotStudied('q1',S().id);assert(!S().learningQueue.q1,'flag removes it');
  ans('q2',1,D5+2000);rate('q2',3,D5+2100);ans('q3',2,D5+3000);go('q3');next(D5+MIN);same(S().roundPass,{round:2,ids:['q3']},'the flagged card does not come back');
  at(D5+MIN+100);go('q1');assert.strictEqual(S().index,0);
  // Back in Round 2 (q3): flag it, then the round ends with nothing open.
  go('q3');at(D5+2*MIN);nkToggleNotStudied('q3',S().id);assert(header().includes('nk-ns-toggle is-on'),'the flag shows in the Round 2 header');
  next(D5+3*MIN);assert.strictEqual(reviewSheets,1,'a flagged card counts as done for the round');
  at(D5+4*MIN);assert(nkFinishRevisionSession());const t=state.tests.at(-1);
  assert(!t.questionIds.includes('q3')&&!t.questionIds.includes('q1'),'flagged questions are not scored');
  assert(!nkFsrsActiveAttempts('q3').some(a=>a.sessionId==='f1'),'and none of their rounds reach FSRS');
});

scenario('normal Practice, mistakes and spaced review are untouched (no queue, no rounds, no advance)',()=>{
  reset();history();
  state.activeSession={id:'p1',mode:'practice',title:'Upper limb',questionIds:['q1','q2'],sessionQuestionIds:['q1','q2'],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:'normal',originRoute:'topics',lifecycle:'active'};
  ans('q1',2,D5+1000);ans('q2',1,D5+2000);rate('q2',3,D5+2100);assert(!S().learningQueue,'no queue');assert.strictEqual(TIMERS.length,0,'no advance');go('q2');next(D5+3000);assert(!S().roundPass);
  for(const kind of ['wrong','bookmarks']){reset();history();state.activeSession={id:'w'+kind,mode:'practice',title:'Revision',questionIds:['q1','q2'],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:kind==='wrong'?'wrong':'bookmarked'};nkRevisionTagSession(kind,null,['q1','q2']);
    ans('q1',2,D5+1000);ans('q2',1,D5+2000);rate('q2',3,D5+2100);assert(!S().learningQueue);assert.strictEqual(TIMERS.length,0);go('q2');next(D5+3000);assert(!S().roundPass);}
  reset();history();state.activeSession={id:'tr',mode:'practice',title:"Today's Review",questionIds:['q1'],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:'spaced-review'};
  ans('q1',2,D5+1000);assert(!S().learningQueue);next(D5+2000);assert(!S().roundPass);
});

scenario('daily cap: in-session learning repeats stay exempt',()=>{
  reset({desiredRetention:.9,dailyCap:20,maximumInterval:365});
  const extra=Array.from({length:22},(_,i)=>({id:'x'+i,subject:'Anatomy',bank:'PrepLadder',chapterId:'c2',chapter:'Thorax',question:'Stem x'+i,correctOption:1,options:[{letter:'A',text:'a'},{letter:'B',text:'b'}]}));
  questions.push(...extra);extra.forEach(q=>{BY_ID[q.id]=q;});
  try{
    history(['q1','q2',...extra.map(q=>q.id)]);setPrefs({advanceAfterRating:false});
    extra.slice(0,19).forEach((q,i)=>{at(D5+i);nkFsrsRecordAttempt(q.id,1,1000,'fsrs-review',3);});
    dueSession('c1',['q1','q2'],D5+100);ans('q1',2,D5+1000);
    at(D5+11*MIN);const queue=nkFsrsQueue({});
    assert(queue.cards.some(q=>q.id==='q1'),'the same-day learning repeat is admitted although the cap (20) is spent');
    assert(!queue.cards.some(q=>q.id==='q2'),'a first review today is held by the cap');
  }finally{questions.splice(8);extra.forEach(q=>delete BY_ID[q.id]);}
});
console.log('REVIEW_LEARNING_QUEUE_OK '+results.length);
results.forEach(name=>console.log('  ok · '+name));
'''


SYNC_CASES = r"""
const assert=require('assert');
let state={},nkSyncMeta={lastError:''};
const NK_PRACTICE_CHECKPOINT_VERSION=1,NK_PRACTICE_LIFECYCLES=new Set(['active','paused','suspended','submitted','completed','discarded']),NK_PRACTICE_TERMINAL=new Set(['submitted','completed','discarded']);
let NOW=1000;Date.now=()=>NOW;
function nkNormalPracticeSession(s){return Boolean(s)&&s.mode==='practice';}
FUNCTIONS
const same=(a,b,m)=>assert.strictEqual(JSON.stringify(a),JSON.stringify(b),m);
const ids=['q1','q2','q3'];
const base={id:'r1',mode:'practice',questionIds:ids,sessionQuestionIds:ids,index:1,startedAt:1,practiceContext:{revisionQueueKind:'due'},originRoute:'quick-revision'};
// Phone: q1 answered wrong (round 1), waiting in the learning queue.
NOW=2000;const phone=nkCheckpointFromSession({...base,answers:{q1:2,q2:1},submitted:{q1:true,q2:true},questionTimes:{q1:9000,q2:4000},learningQueue:{q1:{due:600000,round:1}}},null,'paused');
// Web (same session, later): q1 reopened as round 2, answered right; the queue is empty.
NOW=5000;const web=nkCheckpointFromSession({...base,index:0,answers:{q1:1,q2:1},submitted:{q1:true,q2:true},questionTimes:{q1:3000,q2:4000},roundHistory:{q1:[{round:1,answer:2,submitted:true,timeMs:9000,correct:false,rating:1,attemptId:'a1',reopenedAt:4000}]},learningReturnIndex:1},phone,'paused');
assert.strictEqual(web.membershipHash,phone.membershipHash,'rounds never change membership');
assert(web.questionUpdates.q1.revision>phone.questionUpdates.q1.revision,'round 2 is a newer edit of q1');
same(phone.questionUpdates.q2,web.questionUpdates.q2,'untouched questions keep their update');
for(const [first,second,label] of [[phone,web,'phone then web'],[web,phone,'web then phone']]){
  state={normalPracticeCheckpoints:[JSON.parse(JSON.stringify(first))],normalPracticeCheckpoint:null,activeSession:null};
  const m=nkMergePracticeCheckpoint(JSON.parse(JSON.stringify(second)));
  same(m.answers.q1,1,label+': the copy with more rounds owns the live answer');assert.strictEqual(m.questionTimes.q1,3000,label+': and its time');
  assert.strictEqual(m.roundHistory.q1.length,1,label+': round history kept');assert(!m.learningQueue,label+': the stale queue entry is gone');
  same(m.sessionQuestionIds,ids);
}
// Round 2 reopened but not yet answered: an older submitted copy never re-submits it.
NOW=6000;const open=nkCheckpointFromSession({...base,index:0,answers:{q2:1},submitted:{q2:true},questionTimes:{q2:4000},roundHistory:{q1:[{round:1,answer:2,submitted:true,timeMs:9000}]}},phone,'paused');
state={normalPracticeCheckpoints:[JSON.parse(JSON.stringify(open))],activeSession:{...base,index:0,answers:{q2:1},submitted:{q2:true},questionTimes:{q2:4000},roundHistory:open.roundHistory}};
let m=nkMergePracticeCheckpoint(JSON.parse(JSON.stringify(phone)));
assert(!m.submitted.q1&&m.answers.q1==null,'the reopened round stays open');assert(!m.learningQueue);
assert.strictEqual(state.activeSession.roundHistory.q1.length,1,'the live session takes the merged rounds');same(state.activeSession.learningQueue,{});
// Equal rounds: per-question rule as before, the queue entry travels with the preferred copy.
state={normalPracticeCheckpoints:[JSON.parse(JSON.stringify(phone))],activeSession:null};
const phone2={...JSON.parse(JSON.stringify(phone)),updatedAt:phone.updatedAt+1};phone2.questionUpdates.q1={...phone2.questionUpdates.q1,revision:phone2.questionUpdates.q1.revision+1};
m=nkMergePracticeCheckpoint(phone2);same(m.learningQueue,{q1:{due:600000,round:1}},'queue entry kept');
// Payloads from before this feature: no learning keys anywhere.
const legacy=JSON.parse(JSON.stringify(phone));delete legacy.learningQueue;
const plain=nkNormalizeCheckpoint(legacy);assert(!('learningQueue' in plain)&&!('roundHistory' in plain)&&!('learningReturnIndex' in plain),'older payloads load as they are');
state={normalPracticeCheckpoints:[plain],activeSession:null};m=nkMergePracticeCheckpoint(JSON.parse(JSON.stringify(plain)));assert(!('learningQueue' in m)&&!('roundHistory' in m),'and merge without inventing fields');
// The live round 2+ (roundPass) travels with the checkpoint: the copy further along owns it.
NOW=7000;const r2=nkCheckpointFromSession({...base,index:0,answers:{q2:1},submitted:{q2:true},questionTimes:{q2:4000},roundHistory:{q1:[{round:1,answer:2,submitted:true,timeMs:9000}]},roundPass:{round:2,ids:['q1','zz']}},phone,'paused');
same(r2.roundPass,{round:2,ids:['q1']},'only member cards are kept');
for(const [first,second,label] of [[phone,r2,'round 1 then round 2'],[r2,phone,'round 2 then round 1']]){
  state={normalPracticeCheckpoints:[JSON.parse(JSON.stringify(first))],activeSession:{...base,index:0,answers:{},submitted:{},questionTimes:{}}};
  m=nkMergePracticeCheckpoint(JSON.parse(JSON.stringify(second)));
  same(m.roundPass,{round:2,ids:['q1']},label+': the round 2 copy owns the pass');same(state.activeSession.roundPass,{round:2,ids:['q1']},label+': the live session takes it');
}
NOW=8000;const r3=nkCheckpointFromSession({...base,index:0,answers:{q2:1},submitted:{q2:true},questionTimes:{q2:4000},roundHistory:{q1:[{round:1,answer:2,submitted:true},{round:2,answer:2,submitted:true}]},roundPass:{round:3,ids:['q1']}},r2,'paused');
state={normalPracticeCheckpoints:[JSON.parse(JSON.stringify(r3))],activeSession:null};m=nkMergePracticeCheckpoint(JSON.parse(JSON.stringify(r2)));
same(m.roundPass,{round:3,ids:['q1']},'a later round wins over an earlier one');assert.strictEqual(m.roundHistory.q1.length,2);
state={normalPracticeCheckpoints:[JSON.parse(JSON.stringify(phone))],activeSession:{...base,roundPass:{round:2,ids:['q1']}}};m=nkMergePracticeCheckpoint(JSON.parse(JSON.stringify(phone)));
assert(!('roundPass' in m)&&!('roundPass' in state.activeSession),'two round 1 copies have no pass, and a stale one leaves the live session');
// FSRS preferences sync per field (fsrsPreferences + fsrsPreferencesAt).
state={fsrsPreferences:{desiredRetention:.9,dailyCap:150,maximumInterval:365,learningInSession:'due',advanceAfterRating:true},fsrsPreferencesAt:{learningInSession:100,advanceAfterRating:300}};
nkMergeFsrsPreferences({desiredRetention:.9,dailyCap:150,maximumInterval:365,learningInSession:'end',advanceAfterRating:false},{learningInSession:200,advanceAfterRating:250});
same([state.fsrsPreferences.learningInSession,state.fsrsPreferences.advanceAfterRating],['end',true],'newer field wins, older field loses');
nkMergeFsrsPreferences({desiredRetention:.85,dailyCap:150,maximumInterval:365},{desiredRetention:400});
same([state.fsrsPreferences.learningInSession,state.fsrsPreferences.desiredRetention],['end',.85],'an older client without the fields leaves them alone');
console.log('REVIEW_LEARNING_QUEUE_SYNC_OK');
"""


def sync_script() -> str:
    durable = (MODULES / "durable_persistence.js").read_text(encoding="utf-8")
    sync = (MODULES / "cross_device_sync.js").read_text(encoding="utf-8")
    names = [(durable, n) for n in ("nkStateObject", "nkCheckpointMembership", "nkCheckpointLearning", "nkCheckpointRounds", "nkNormalizeCheckpoint", "nkNormalizePracticeCheckpoints", "nkLatestPracticeCheckpoint", "nkCheckpointQuestionUpdate", "nkCheckpointFromSession")]
    names += [(sync, n) for n in ("nkSyncPracticeCheckpoint", "nkSyncTerminalLifecycle", "nkSyncMembership", "nkPracticeConflict", "nkMergePracticeCheckpoint", "nkMergeFsrsPreferences")]
    return SYNC_CASES.replace("FUNCTIONS", "\n".join(extract_function(text, name).strip() for text, name in names))


def test_install_contract() -> None:
    page = app_page()
    assert page.count("NK_REVIEW_LEARNING_QUEUE_V1_START") == 1
    start = page.index("NK_REVIEW_LEARNING_QUEUE_V1_START")
    for owner in ("NK_FSRS_V6_START", "NK_REVISION_SESSION_V1_START", "NK_NOT_STUDIED_V1_START", "NK_QUESTION_INTERACTION_INTEGRITY_V1_START", "NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START"):
        assert page.index(owner) < start, f"the learning queue wraps after {owner}"
    assert start < page.index("  window.QB={") and "nkRlqStudyNow,nkRlqFinish," in page[page.index("  window.QB={"):], "actions exported"
    module = MODULE.read_text(encoding="utf-8")
    for hook in ("nextQ=function", "prevQ=function", "goIndex=function", "practiceActionBar=function", "nkRateCurrent=function", "nkFsrsCommitPending=function", "submitPractice=function", "finishPracticeSession=function", "nkSessionHeader=function", "openSessionReview=function"):
        assert hook in module, hook
    assert "questionIds.push" not in module and "sessionQuestionIds=" not in module, "rounds never change session membership"
    # The round badge lives inside the counter, never as a fourth header item (it pushed the actions out).
    assert "<\\/div>)/,`$1${nkRlqBadge" not in module and "${nkRlqBadge(pass.round)}</div>" in module, "badge inside the counter"
    assert "!a.learningRound" in (MODULES / "learning_insights.js").read_text(encoding="utf-8"), "Insights count a relearning repeat once"
    html = HTML.read_text(encoding="utf-8")
    assert "!a.isRatingRevision&&!a.learningRound&&typeof a.correct" in html and "if(a.learningRound)repeats.push(a)" in html, "chapter and Home accuracy skip relearning repeats"
    css = app_css()
    assert css.count("/* ── nk-review-learning-queue-v1 ── */") == 1
    assert css.index("/* ── nk-review-learning-queue-v1 ── */") < css.index("/* ── nk-visual-refinement-v1"), "sits before the visual refinement layer"
    for selector in (".nk-rlq-round{", ".nk-session-count.has-round", ".nk-rlq-wait-actions", ".nk-fsrs-rating.is-advancing"):
        assert selector in css, selector
    print("REVIEW_LEARNING_QUEUE_INSTALL_OK")


def run(script: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "review-learning-queue-test.js"
        path.write_text(script, encoding="utf-8")
        result = subprocess.run(["node", str(path)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
        return result.stdout.strip()


def page_functions() -> str:
    html = HTML.read_text(encoding="utf-8")
    declared = ["nkMarkSkippedFromSession", "submitPractice", "selectExam", "submitExam", "finishPracticeSession", "buildReviewSession", "chapterStats", "nkHomeRangeStart", "nkHomeProgressStats"]
    assigned = ["nextQ", "prevQ", "goIndex", "nkSessionHeader"]
    return ("\n".join("let " + n + "=" + extract_function(html, n).strip() + ";" for n in declared) + "\n"
            + "\n".join(n + "=" + extract_function(html, n).strip() + ";" for n in assigned))


def main() -> None:
    read = lambda name: (MODULES / name).read_text(encoding="utf-8")
    prelude = PRELUDE % {"vendor": repr(str(VENDOR))}
    script = (prelude + EXTRA + page_functions() + "\n" + read("durable_persistence.js") + "\n" + read("continue_practice_resume.js") + "\n"
              + read("fsrs_scheduler.js") + "\n" + read("revision_session.js") + "\n" + read("not_studied_flags.js") + "\n"
              + MODULE.read_text(encoding="utf-8") + SCENARIOS + SCENARIOS_2)
    print(run(script))
    print(run(sync_script()))
    test_install_contract()


if __name__ == "__main__":
    main()
