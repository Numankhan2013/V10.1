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
nkSessionHeader=(q,s,mode)=>`<header><div class="nk-session-count"><strong>${s.index+1}</strong> / ${s.questionIds.length}</div><div class="q-actions"><button class="icon-btn bookmark-toggle"></button></div></header>`;
document.body.insertAdjacentHTML=(where,html)=>{dialogs.push(html);};
let nkStartRevisionQueue=()=>{},nkRevisionScope={subject:'',bank:'',topic:''};
function nkQuestionAction(fn){return fn;}
function nkValidQuestionOption(q,n){return Boolean(q)&&[1,2].includes(Number(n));}
function defaultState(){return {attempts:{},reviews:{},tests:[],bookmarks:{},questionNotes:{},studyModules:[],savedMocks:[],fsrsReviewEligible:{},activeSession:null};}
'''

SCENARIOS = r'''
nkFsrsInit();
const MIN=60000,DAY=86400000;
const IDS=['q1','q2','q3','q4'];
const S=()=>state.activeSession,pos=qid=>S().questionIds.indexOf(qid),go=qid=>{S().index=pos(qid);};
function reset(prefs){state={attempts:{},reviews:{},tests:[],fsrsPreferences:prefs||null,fsrsReviewEligible:{},activeSession:null,bookmarks:{},fsrsMigratedAt:1};routes=[];toasts=[];TIMERS=[];reviewSheets=0;dialogs=[];route={page:'practice'};at(0);}
// Earlier study: every question answered correctly once on day 0, so all are review cards due on day 5.
function history(ids=IDS){at(0);state.activeSession={id:'s0',mode:'practice',title:'Upper limb',questionIds:[...ids],sessionQuestionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:'normal',originRoute:'topics',lifecycle:'active'};
  ids.forEach((q,i)=>{at(1000+i*100);go(q);S().answers[q]=1;submitPractice();});nkFsrsRecoverPending();state.activeSession=null;}
// A due review exactly as revision_desk.js starts it (startSession + nkRevisionTagSession('due')).
function dueSession(id,ids,t){at(t);state.activeSession={id,mode:'practice',title:'Quick Revision · Due Review',questionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,lastTick:NOW,elapsedMs:0,questionEnteredAt:NOW,questionTimes:{},context:'fsrs'};
  assert(nkRevisionTagSession('due',null,ids),'tagged as a due review');return S();}
function ans(qid,choice,t,ms=20000){at(t);go(qid);S().questionTimes[qid]=ms;S().answers[qid]=choice;submitPractice();}
function rate(qid,r,t){at(t);return nkRateCurrent(r,qid,S().id);}
function next(t){at(t);return nextQ();}
const cur=()=>S().questionIds[S().index];
const round=qid=>(S().roundHistory?.[qid]?.length||0)+1;
const same=(a,b,msg)=>assert.strictEqual(JSON.stringify(a),JSON.stringify(b),msg);
const results=[];function scenario(name,fn){fn();results.push(name);}
const D5=5*DAY;
function setPrefs(p){Object.entries(p).forEach(([k,v])=>assert(nkFsrsSetSessionPreference(k,v),k));}

scenario('settings: defaults are Show when due + advance on; per-field stamps; schedulers ignore them',()=>{
  reset();const p=nkFsrsPreferences();assert.strictEqual(p.learningInSession,'due');assert.strictEqual(p.advanceAfterRating,true);
  at(500);setPrefs({learningInSession:'end'});at(600);setPrefs({advanceAfterRating:'0'});
  assert.strictEqual(nkFsrsPreferences().learningInSession,'end');assert.strictEqual(nkFsrsPreferences().advanceAfterRating,false);
  same([state.fsrsPreferencesAt.learningInSession,state.fsrsPreferencesAt.advanceAfterRating],[T0+500,T0+600],'each field has its own stamp for sync');
  assert(!nkFsrsSetSessionPreference('learningInSession','sometimes'),'unknown modes are refused');
  state.fsrsPreferences.learningInSession='bogus';assert.strictEqual(nkFsrsPreferences().learningInSession,'due','a damaged value falls back to the default');
  history(['q1']);const a=state.attempts.q1[0];same(Object.keys(a.schedulerPreferences).sort(),['dailyCap','desiredRetention','maximumInterval'],'attempts record only scheduling values');
  // Settings page: the section, the select and the switch, saved through the draft.
  nkFsrsDraft=null;const html=nkFsrsSettingsMarkup();
  assert(html.includes('Learning cards in a review session')&&html.includes('<option value="due"')&&html.includes('Show at the end')&&html.includes('>Off</option>'),'mode select');
  assert(html.includes('Advance after rating')&&html.includes('type="checkbox"')&&html.includes('role="switch"'),'advance switch');
  nkFsrsEditSetting('learningInSession','off');nkFsrsEditSetting('advanceAfterRating','1');at(900);assert(nkFsrsSaveSettings());
  assert.strictEqual(nkFsrsPreferences().learningInSession,'off');assert.strictEqual(nkFsrsPreferences().advanceAfterRating,true);assert.strictEqual(state.fsrsPreferencesAt.learningInSession,T0+900);
});

scenario('Show when due: a missed card comes back in its own row as Round 2 once its step is due, ahead of the rest',()=>{
  reset();history();setPrefs({advanceAfterRating:false});const s=dueSession('r1',IDS,D5);const hash=nkPracticeFindCheckpoint('r1').membershipHash;
  ans('q1',2,D5+1000);
  const card=state.reviews.q1;assert.strictEqual(card.state,3,'Again on a review card relearns');assert.strictEqual(card.due,T0+D5+1000+10*MIN,'10 minute relearning step');
  same(S().learningQueue.q1,{due:T0+D5+1000+10*MIN,round:1},'queued with its FSRS due time');
  assert.strictEqual(state.attempts.q1.at(-1).source,'fsrs-review');
  next(D5+2000);assert.strictEqual(cur(),'q2','not due yet: the set continues');
  ans('q2',1,D5+3000);next(D5+11*MIN);assert.strictEqual(cur(),'q1','due now: the learning card comes before q3');
  assert.strictEqual(round('q1'),2);assert(!S().answers.q1&&!S().submitted.q1,'the live answer is cleared for a new round');
  const r1=S().roundHistory.q1[0];same([r1.round,r1.answer,r1.submitted,r1.correct,r1.rating,r1.timeMs],[1,2,true,false,1,20000],'round 1 archived');
  assert(!S().learningQueue.q1,'reopened: no longer waiting');
  same(S().questionIds,IDS,'membership is unchanged (no duplicate ids)');same(S().sessionQuestionIds,IDS);
  assert(nkSessionHeader(questions[0],S(),'practice').includes('Round 2'),'header badge');
  ans('q1',1,D5+11*MIN+5000);assert(S().pendingRating.q1,'a correct round waits for its rating');assert.strictEqual(nkFsrsSessionRating('q1'),null,'round 1 is not this round\'s saved rating');
  rate('q1',3,D5+11*MIN+6000);assert.strictEqual(state.reviews.q1.state,2,'Good graduates the card');assert(!S().learningQueue.q1);
  const last=state.attempts.q1.at(-1);same([last.source,last.learningRound,last.rating],['fsrs-review',2,3],'every round is a normal FSRS attempt');
  next(D5+12*MIN);assert.strictEqual(cur(),'q3','the set resumes after the card it interrupted');assert.strictEqual(S().learningReturnIndex,undefined);
  nkPracticeStoreCheckpoint(nkPracticeBuildCheckpoint(S(),'active'));assert.strictEqual(nkPracticeFindCheckpoint('r1').membershipHash,hash,'checkpoint membershipHash unchanged');
  const cached=JSON.stringify(state.reviews.q1);nkFsrsReplay('q1');assert.strictEqual(JSON.stringify(state.reviews.q1),cached,'cache equals a replay of every round');
});

'''

SCENARIOS_2 = r'''
scenario('Hard on a relearning card keeps it queued; Good graduates it; revising a saved rating only saves',()=>{
  reset();history();setPrefs({advanceAfterRating:false});dueSession('r2',['q1','q2','q3'],D5);
  ans('q1',2,D5+1000);next(D5+2000);ans('q2',1,D5+3000);next(D5+11*MIN);assert.strictEqual(cur(),'q1');
  ans('q1',1,D5+11*MIN+1000);rate('q1',2,D5+11*MIN+2000);
  assert.strictEqual(state.reviews.q1.state,3,'Hard on a relearning step stays relearning');assert(S().learningQueue.q1,'so it waits for round 3');
  assert.strictEqual(S().learningQueue.q1.round,2);
  // Revisit by hand and change Hard to Good: saved, card graduates, leaves the queue, no jump.
  at(D5+11*MIN+3000);const idx=S().index;assert(nkRateCurrent(3,'q1',S().id));assert.strictEqual(S().index,idx,'no jump');assert.strictEqual(TIMERS.length,0,'no advance for a revision');
  assert.strictEqual(state.reviews.q1.state,2);assert(!S().learningQueue.q1,'graduated: out of the queue');
  next(D5+12*MIN);assert.strictEqual(cur(),'q3','continues after the interrupted card');
});

scenario('learn-ahead at the end: a card due within 20 min shows at once; a later one offers Study now / Finish',()=>{
  reset();history(['q1']);setPrefs({advanceAfterRating:false});dueSession('r3',['q1'],D5);
  ans('q1',2,D5+1000);next(D5+2000);assert.strictEqual(round('q1'),2,'10 min step is inside the 20 min learn-ahead: shown immediately');assert.strictEqual(reviewSheets,0);
  ans('q1',1,D5+3000);rate('q1',3,D5+4000);next(D5+5000);assert.strictEqual(reviewSheets,1,'nothing left: the end-of-session sheet opens');
  // A card due later than the learn-ahead (pushed out to 34 min) gets the wait line instead.
  reset();history(['q1','q2']);setPrefs({advanceAfterRating:false});dueSession('r4',['q1','q2'],D5);
  ans('q1',2,D5+1000);next(D5+2000);assert.strictEqual(cur(),'q2');S().learningQueue.q1.due=T0+D5+35*MIN;ans('q2',1,D5+MIN);rate('q2',3,D5+MIN+100);
  next(D5+MIN+200);assert.strictEqual(cur(),'q2','stays put');assert.strictEqual(reviewSheets,0);
  assert(dialogs.at(-1).includes('1 learning card due in 34 min')&&dialogs.at(-1).includes('Study now')&&dialogs.at(-1).includes('Finish'),'the wait line');
  nkRlqFinish();assert.strictEqual(reviewSheets,1,'Finish opens the end-of-session sheet');
  at(D5+2*MIN);nkRlqStudyNow();assert.strictEqual(cur(),'q1');assert.strictEqual(round('q1'),2,'Study now opens the next round at once');
});

scenario('Show at the end: learning cards wait for the rest of the set, then follow the learn-ahead',()=>{
  reset();history();setPrefs({learningInSession:'end',advanceAfterRating:false});dueSession('r5',IDS,D5);
  ans('q1',2,D5+1000);next(D5+2000);ans('q2',1,D5+11*MIN);next(D5+11*MIN+100);assert.strictEqual(cur(),'q3','due, but held for the end');
  ans('q3',1,D5+12*MIN);next(D5+12*MIN+100);assert.strictEqual(cur(),'q4');ans('q4',1,D5+13*MIN);next(D5+13*MIN+100);
  assert.strictEqual(cur(),'q1');assert.strictEqual(round('q1'),2,'after the set it comes back');
});

scenario('Off: one pass as before (no queue, no rounds, last Next opens the sheet)',()=>{
  reset();history();setPrefs({learningInSession:'off',advanceAfterRating:false});dueSession('r6',['q1','q2'],D5);
  ans('q1',2,D5+1000);assert.deepStrictEqual(S().learningQueue||{},{});next(D5+11*MIN);assert.strictEqual(cur(),'q2');ans('q2',1,D5+12*MIN);rate('q2',3,D5+12*MIN+1);
  next(D5+30*MIN);assert.strictEqual(reviewSheets,1);assert(!S().roundHistory,'no rounds');
});

scenario('the saved result counts each question once, by its latest round; times add up; attempts stay complete',()=>{
  reset();history();setPrefs({advanceAfterRating:false});dueSession('r7',['q1','q2'],D5);
  ans('q1',2,D5+1000,10000);next(D5+2000);ans('q2',1,D5+3000,5000);next(D5+11*MIN);ans('q1',1,D5+11*MIN+1000,7000);rate('q1',3,D5+11*MIN+2000);
  at(D5+12*MIN);assert(nkFinishRevisionSession());const t=state.tests.at(-1);
  same(t.questionIds,['q1','q2'],'each question once');same([t.correct,t.incorrect,t.total,t.attempted],[2,0,2,2],'q1 counts by its latest (correct) round');
  same(t.answers,{q1:1,q2:1});assert.strictEqual(t.questionTimes.q1,17000,'both rounds\' time');
  const rounds=state.attempts.q1.filter(a=>a.sessionId==='r7');assert.strictEqual(rounds.length,2,'FSRS history keeps both rounds');
  assert.strictEqual(nkPracticeFindCheckpoint('r7').lifecycle,'submitted');
  // A round reopened and left unanswered gives way to the round before it.
  reset();history();setPrefs({advanceAfterRating:false});dueSession('r8',['q1','q2'],D5);
  ans('q1',2,D5+1000,10000);next(D5+2000);ans('q2',1,D5+3000);next(D5+11*MIN);assert.strictEqual(round('q1'),2);
  at(D5+12*MIN);assert(nkFinishRevisionSession());const u=state.tests.at(-1);
  same(u.questionIds,['q1','q2']);same([u.correct,u.incorrect],[1,1],'the unanswered round 2 falls back to round 1 (wrong)');
});

scenario('pause / reload / resume keeps the queue, the rounds and the return point; checkpoint membership unchanged',()=>{
  reset();history();setPrefs({advanceAfterRating:false});dueSession('r9',IDS,D5);const hash=nkPracticeFindCheckpoint('r9').membershipHash;
  ans('q1',2,D5+1000);ans('q2',2,D5+2000);go('q2');next(D5+3000);ans('q3',1,D5+11*MIN);next(D5+11*MIN+100);assert.strictEqual(cur(),'q1');
  at(D5+11*MIN+200);assert(nkPausePractice());const cp=nkPracticeFindCheckpoint('r9');
  assert.strictEqual(cp.membershipHash,hash);same(cp.sessionQuestionIds,IDS);same(Object.keys(cp.learningQueue),['q2']);assert.strictEqual(cp.roundHistory.q1.length,1);assert.strictEqual(cp.learningReturnIndex,2);
  assert(cp.questionUpdates.q1.signature.endsWith(',1]'),'a reopened round is a new edit of that question');
  state=JSON.parse(JSON.stringify(state));state.activeSession=null;at(D5+20*MIN);assert(nkResumePracticeById('r9'));
  const s=S();assert.strictEqual(s.revisionQueueKind,'due');assert.strictEqual(cur(),'q1');assert.strictEqual(round('q1'),2);same(Object.keys(s.learningQueue),['q2']);assert.strictEqual(s.learningReturnIndex,2);
  ans('q1',1,D5+21*MIN);rate('q1',3,D5+21*MIN+100);next(D5+22*MIN);assert.strictEqual(cur(),'q2','the other queued card is due: shown next');assert.strictEqual(round('q2'),2);
  // An older checkpoint (no learning fields) still normalises and resumes.
  const old=JSON.parse(JSON.stringify(cp));delete old.learningQueue;delete old.roundHistory;delete old.learningReturnIndex;old.sessionId='old1';old.lifecycle='paused';
  const norm=nkNormalizeCheckpoint(old);assert(norm&&!('learningQueue' in norm)&&!('roundHistory' in norm),'no learning keys invented');
  const back=nkPracticeSessionFromCheckpoint(norm);assert(back&&!back.learningQueue&&!back.roundHistory,'resumes as an ordinary session');
  // Damaged learning fields are dropped, not trusted.
  const bad=nkNormalizeCheckpoint({...cp,learningQueue:{zz:{due:5},q3:{due:'x'}},roundHistory:{q9:[{answer:1}],q4:'x'},learningReturnIndex:99});
  assert(!bad.learningQueue&&!bad.roundHistory&&!('learningReturnIndex' in bad),'foreign ids, bad times and out-of-range indexes are dropped');
});

scenario('advance after rating: first Hard/Good/Easy moves on after the pressed beat; never after a wrong answer',()=>{
  reset();history();dueSession('a1',['q1','q2','q3'],D5);
  ans('q1',1,D5+1000);rate('q1',3,D5+2000);assert.strictEqual(cur(),'q1','not yet: the pressed beat');assert.strictEqual(TIMERS.length,1);assert.strictEqual(TIMERS[0].ms,250);
  assert.strictEqual(rate('q1',4,D5+2100),false,'a double tap while the advance waits saves nothing');assert.strictEqual(nkFsrsSessionRating('q1').rating,3);
  at(D5+2250);flushTimers();assert.strictEqual(cur(),'q2','moved on');
  ans('q2',2,D5+3000);assert.strictEqual(TIMERS.length,0,'a wrong answer waits for Next');assert.strictEqual(cur(),'q2');
  // Revisit q1 and change its saved rating: saves, no jump.
  at(D5+4000);goIndex(0);assert.strictEqual(cur(),'q1');assert(rate('q1',2,D5+4100));assert.strictEqual(TIMERS.length,0);assert.strictEqual(cur(),'q1');
  // Setting off: no advance.
  setPrefs({advanceAfterRating:false});goIndex(2);ans('q3',1,D5+5000);rate('q3',3,D5+5100);assert.strictEqual(TIMERS.length,0);
});

scenario('advance: stale timers never fire (moved, flagged, paused, session replaced); last card opens the sheet; due card first',()=>{
  const start=()=>{reset();history();dueSession('a2',['q1','q2','q3'],D5);};
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);at(D5+1200);prevQ();goIndex(2);flushTimers();assert.strictEqual(cur(),'q3','moving by hand cancels the advance');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);const t=TIMERS[0];S().index=2;t.fn();assert.strictEqual(cur(),'q3','a timer that outlived its question does nothing');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);nkToggleNotStudied('q1',S().id);flushTimers();assert.strictEqual(cur(),'q1','flag toggled: no advance');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);const timer=TIMERS[0];at(D5+1200);nkPausePractice();assert.strictEqual(TIMERS.length,0,'pause clears it');timer.fn();assert.strictEqual(S().index,0,'a paused session never moves');assert.strictEqual(S().lifecycle,'paused');
  start();ans('q1',1,D5+1000);rate('q1',3,D5+1100);const t2=TIMERS[0];state.activeSession={...S(),id:'other'};t2.fn();assert.strictEqual(S().index,0,'another session: nothing');
  // Last card, nothing queued: the end-of-session sheet.
  start();go('q3');ans('q3',1,D5+1000);rate('q3',3,D5+1100);flushTimers();assert.strictEqual(reviewSheets,1);
  // A due learning card comes before the next card.
  start();ans('q1',2,D5+1000);next(D5+2000);ans('q2',1,D5+11*MIN);rate('q2',3,D5+11*MIN+100);flushTimers();assert.strictEqual(cur(),'q1','the advance shows the due learning card first');assert.strictEqual(round('q1'),2);
});

scenario('not-studied flag: a flagged question never enters or stays in the learning queue; unflag puts it back',()=>{
  reset();history();setPrefs({advanceAfterRating:false});dueSession('f1',['q1','q2','q3'],D5);
  ans('q1',2,D5+1000);assert(S().learningQueue.q1);at(D5+1100);nkToggleNotStudied('q1',S().id);assert(!S().learningQueue.q1,'flag removes it');
  next(D5+2000);ans('q2',1,D5+11*MIN);next(D5+11*MIN+100);assert.strictEqual(cur(),'q3','the flagged card does not come back');
  at(D5+11*MIN+200);go('q1');nkToggleNotStudied('q1',S().id);assert(S().learningQueue.q1,'unflag: back in the queue');
  assert(!nkFsrsQueue({}).due.some(q=>q.id==='q2'),'answered today');
});

scenario('normal Practice, mistakes and spaced review are untouched (no queue, no advance)',()=>{
  reset();history();
  state.activeSession={id:'p1',mode:'practice',title:'Upper limb',questionIds:['q1','q2'],sessionQuestionIds:['q1','q2'],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:'normal',originRoute:'topics',lifecycle:'active'};
  ans('q1',2,D5+1000);ans('q2',1,D5+2000);rate('q2',3,D5+2100);assert(!S().learningQueue,'no queue');assert.strictEqual(TIMERS.length,0,'no advance');
  for(const kind of ['wrong','bookmarks']){reset();history();state.activeSession={id:'w'+kind,mode:'practice',title:'Revision',questionIds:['q1','q2'],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:kind==='wrong'?'wrong':'bookmarked'};nkRevisionTagSession(kind,null,['q1','q2']);
    ans('q1',2,D5+1000);ans('q2',1,D5+2000);rate('q2',3,D5+2100);assert(!S().learningQueue);assert.strictEqual(TIMERS.length,0);}
  reset();history();state.activeSession={id:'tr',mode:'practice',title:"Today's Review",questionIds:['q1'],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},context:'spaced-review'};
  ans('q1',2,D5+1000);assert(!S().learningQueue);
});

scenario('daily cap: in-session learning repeats stay exempt',()=>{
  reset({desiredRetention:.9,dailyCap:20,maximumInterval:365});
  const extra=Array.from({length:22},(_,i)=>({id:'x'+i,subject:'Anatomy',bank:'PrepLadder',chapterId:'c2',chapter:'Thorax',question:'Stem x'+i,correctOption:1,options:[{letter:'A',text:'a'},{letter:'B',text:'b'}]}));
  questions.push(...extra);extra.forEach(q=>{BY_ID[q.id]=q;});
  try{
    history(['q1','q2',...extra.map(q=>q.id)]);setPrefs({advanceAfterRating:false});
    // 19 other cards already reviewed today, then the due review: q1 missed (relearning).
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
    for hook in ("nextQ=function", "nkRateCurrent=function", "nkFsrsCommitPending=function", "submitPractice=function", "finishPracticeSession=function", "nkSessionHeader=function", "openSessionReview=function"):
        assert hook in module, hook
    assert "questionIds.push" not in module and "sessionQuestionIds=" not in module, "rounds never change session membership"
    assert "!a.learningRound" in (MODULES / "learning_insights.js").read_text(encoding="utf-8"), "Insights count a relearning repeat once"
    css = app_css()
    assert css.count("/* ── nk-review-learning-queue-v1 ── */") == 1
    assert css.index("/* ── nk-review-learning-queue-v1 ── */") < css.index("/* ── nk-visual-refinement-v1"), "sits before the visual refinement layer"
    for selector in (".nk-rlq-round", ".nk-rlq-round-dot", ".nk-rlq-wait-actions", ".nk-fsrs-rating.is-advancing"):
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
    declared = ["nkMarkSkippedFromSession", "submitPractice", "selectExam", "submitExam", "finishPracticeSession", "buildReviewSession"]
    assigned = ["nextQ", "prevQ", "goIndex"]
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
