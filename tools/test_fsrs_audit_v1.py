#!/usr/bin/env python3
"""Adversarial FSRS audit suite: drives the real scheduler module in Node with
controlled time.

Covers the scheduler contract end to end beyond the milestone tests: legacy
migration, whole-day and learn-ahead due semantics, queue ordering, the daily
cap (including learning repeats), rating revision chains against independent
engine replays, undo semantics, pending recovery, preview==record under fuzz,
per-attempt preferences, eligibility, counts/forecast, cold-rebuild
determinism, damaged-cache healing, preference timestamps, and a queue
performance canary over a heavy due backlog.
"""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "app/src/main/modules/fsrs_scheduler.js"
VENDOR = ROOT / "app/src/main/assets/vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js"

STUBS = """
const assert=require('assert');
global.window=globalThis;window.FSRS=require(VENDOR_PATH);
const store=new Map();global.localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v))};
const LS_KEY='qbank_state_v1';
const RealDate=Date;
const T0=new RealDate('2026-06-15T12:00:00').getTime();
let T=T0;
class FakeDate extends RealDate{constructor(...args){if(args.length===0){super(T);}else{super(...args);}}static now(){return T;}}
global.Date=FakeDate;window.Date=FakeDate;
const DAY=86400000;
const questions=[];for(let i=0;i<60;i++)questions.push({id:'q'+String(i).padStart(2,'0'),subject:'Anatomy',bank:'PrepLadder',chapterId:String(i%3),chapter:'Topic '+(i%3),correctOption:1,options:[{letter:'A',text:'a'},{letter:'B',text:'b'},{letter:'C',text:'c'}]});
const SUBJECTS=[{subject:'Anatomy',topics:[{id:'0',title:'Topic 0'}],questions:questions}];
function nkAllBankQuestions(){return questions;}
function nkQuestionPresentationFor(q){return {valid:q.id!=='q30'};}
let state=null;
let lastRoute='',route={page:'practice'};
let BY_ID=Object.fromEntries(questions.map(q=>[q.id,q]));
let morePage=()=>'<main></main>';const practicePage=()=>'<main></main>';
let practiceActionBar=()=>'<div class="nk-session-footer"><div class="fixed-actions-inner"></div></div>',submitPractice=()=>{},nextQ=()=>{},prevQ=()=>{},goIndex=()=>{},retryCurrent=()=>{},endSession=()=>{},recordAttempt=()=>{},qAttempts=()=>[];
let wrongQuestions=()=>[];
let navigate=page=>{lastRoute=page;},startSession=()=>{},render=()=>{},showToast=()=>{},savePracticeElapsed=()=>{},haptic=()=>{};
const esc=x=>String(x),shell=x=>x,navIcon=()=>'';
function nkRebuildReviews(){}
function saveState(){store.set(LS_KEY,JSON.stringify(state));}
global.document={getElementById:()=>null,querySelector:()=>null,body:{insertAdjacentHTML:()=>{}}};
window.addEventListener=()=>{};
const FAILED=[];
function CHECK(name,fn){try{fn();console.log('ok -',name);}catch(e){FAILED.push(name+': '+e.message);console.log('FAIL -',name,'::',e.message);}}
function freshState(attempts,reviews,prefs,extra){T=T0;state={attempts:attempts||{},reviews:reviews||{},fsrsPreferences:prefs||null,fsrsReviewEligible:{},activeSession:null,tests:[],bookmarks:{},...(extra||{})};store.clear();store.set(LS_KEY,JSON.stringify(state));}
function card(review){return JSON.parse(JSON.stringify(state.reviews[review||'']||null));}
function reviewOf(qid){return state.reviews[qid];}
function chain(qid,ratings,times){const idi=questions.findIndex(q=>q.id===qid);const q=questions[idi<0?0:idi];const hist=times.map((t,i)=>({id:'a'+i,selected:1,correct:ratings[i]!==1,at:t,reviewedAt:t,source:'practice',rating:ratings[i],schedulerVersion:'fsrs6',schedulerPreferences:null}));let c=window.FSRS.createEmptyCard(new Date(times[0]));hist.forEach((a,i)=>{c=nkFsrsEngine(hist[i].schedulerPreferences||NK_FSRS_DEFAULTS).next(c,new Date(times[i]),ratings[i]).card;});return JSON.parse(JSON.stringify(nkFsrsCardSnapshot(c)));}
function mkReview(fields){return {schemaVersion:2,schedulerVersion:'fsrs6',due:0,nextReviewAt:0,stability:0,difficulty:0,state:0,repetitions:1,lapses:0,elapsedDays:0,scheduledDays:0,learningSteps:0,lastReview:null,...fields};}
function mkAttempt(id,at,correct,source,rating){return {id,selected:1,correct,timeSpent:0,at,reviewedAt:at,source:source||'practice',rating:rating||(correct?3:1),schedulerVersion:'fsrs6'};}
"""
STUBS = STUBS.replace("VENDOR_PATH", repr(str(VENDOR)))

SCENARIOS = r"""
// ---------- S0 init: fresh install ----------
freshState();nkFsrsInit();
CHECK('S0 fresh init defaults',()=>{assert.equal(Object.keys(state.reviews).length,0);assert.equal(nkFsrsPreferences().desiredRetention,0.9);assert(state.fsrsMigratedAt>0);});

// ---------- S1 legacy migration ----------
{
const legAt=T0-2*DAY;
const legacyReview={attempts:1,streak:1,intervalDays:1,lastReviewedAt:legAt,nextReviewAt:T0+3*3600000};
freshState({'q00':[mkAttempt('legacy1',legAt,true,'practice',undefined)]},{'q00':legacyReview});
delete state.attempts.q00[0].schedulerVersion;delete state.attempts.q00[0].rating;
nkFsrsInit();
CHECK('S1 legacy migrated to schema2 with due preserved',()=>{const r=state.reviews.q00;assert.equal(r.schemaVersion,2);assert.equal(r.nextReviewAt,T0+3*3600000,'legacy due preserved');assert.equal(r.legacyDueOverride,T0+3*3600000);});
CHECK('S1 replay deterministic (cold x2, override stable)',()=>{nkFsrsReplay('q00',false);const a=JSON.stringify(state.reviews.q00);nkFsrsReplay('q00',false);const b=JSON.stringify(state.reviews.q00);assert.equal(a,b);assert.equal(JSON.parse(a).nextReviewAt,T0+3*3600000,'override survives non-preserve replay');});
nkFsrsRecordAttempt('q00',1,0,'practice',3,T0+1000);
CHECK('S1 first FSRS rating clears legacy override',()=>{const r=state.reviews.q00;assert.equal(r.legacyDueOverride,null);assert.notEqual(r.nextReviewAt,T0+3*3600000);});
CHECK('S1 cache == replay after new attempt',()=>{const cached=JSON.stringify(state.reviews.q00);nkFsrsReplay('q00',false);assert.equal(JSON.stringify(state.reviews.q00),cached);});
}

// ---------- S2 due semantics ----------
{
const yesterdayEnd=nkFsrsDayEnd(T)-DAY, dayEnd=nkFsrsDayEnd(T);
freshState({'q01':[mkAttempt('a',T-3*DAY,true)],'q02':[mkAttempt('a',T-3*DAY,true)],'q03':[mkAttempt('a',T-3*DAY,true)],'q04':[mkAttempt('a',T-3*DAY,true)],'q05':[mkAttempt('a',T-3*DAY,true)],'q06':[mkAttempt('a',T-3*DAY,true)],'q07':[mkAttempt('a',T-3*DAY,true)]},{
'q01':mkReview({due:yesterdayEnd-1,nextReviewAt:yesterdayEnd-1,lastReview:T-3*DAY,stability:2}),
'q02':mkReview({due:dayEnd-1,nextReviewAt:dayEnd-1,lastReview:T-3*DAY,stability:2}),
'q03':mkReview({due:dayEnd,nextReviewAt:dayEnd,lastReview:T-3*DAY,stability:2}),
'q04':mkReview({due:dayEnd+9*3600000,nextReviewAt:dayEnd+9*3600000,lastReview:T-3*DAY,stability:2}),
'q05':mkReview({due:T+20*60000,nextReviewAt:T+20*60000,state:1,lastReview:T-10*60000,stability:0.007}),
'q06':mkReview({due:T+20*60000+1,nextReviewAt:T+20*60000+1,state:1,lastReview:T-10*60000,stability:0.007}),
'q07':mkReview({due:T+1*3600000,nextReviewAt:T+1*3600000,state:3,lastReview:T-10*60000,stability:0.007})});
CHECK('S2a review due yesterday 23:59 -> due',()=>assert(nkFsrsIsDue(state.reviews.q01,T)));
CHECK('S2b review due today 23:59 -> due',()=>assert(nkFsrsIsDue(state.reviews.q02,T)));
CHECK('S2c review due exactly next midnight -> NOT due',()=>assert(!nkFsrsIsDue(state.reviews.q03,T)));
CHECK('S2d review due tomorrow -> NOT due',()=>assert(!nkFsrsIsDue(state.reviews.q04,T)));
CHECK('S2e learning due exactly +20m -> due',()=>assert(nkFsrsIsDue(state.reviews.q05,T)));
CHECK('S2f learning due +20m+1ms -> NOT due',()=>assert(!nkFsrsIsDue(state.reviews.q06,T)));
CHECK('S2g relearning state3 due +1h -> NOT due (learn-ahead only 20m)',()=>assert(!nkFsrsIsDue(state.reviews.q07,T)));
CHECK('S2h missing review -> due',()=>assert(nkFsrsIsDue(undefined,T)));
}

// ---------- S3 queue ordering ----------
{
freshState({},{
'q01':mkReview({due:T+5*60000,state:1,lastReview:T-10*60000,stability:0.007}),
'q02':mkReview({due:T+15*60000,state:3,lastReview:T-30*60000,stability:0.007}),
'q03':mkReview({due:T-DAY,lastReview:T-3*DAY,stability:2}),
'q04':mkReview({due:T-DAY,lastReview:T-DAY,stability:30}),
'q06':mkReview({due:T+2*DAY,lastReview:T-DAY,stability:5})});
state.attempts={q01:[mkAttempt('a',T-10*60000,true)],q02:[mkAttempt('a',T-30*60000,true)],q03:[mkAttempt('a',T-3*DAY,true)],q04:[mkAttempt('a',T-DAY,true)],q06:[mkAttempt('a',T-DAY,true)]};
state.fsrsReviewEligible={q05:{reason:'skipped',at:T-1000}};
CHECK('S3 queue order: learning(by due) -> reviews(retr asc) -> skipped',()=>{
const q=nkFsrsQueue({});const ids=q.cards.map(x=>x.id);
assert.deepEqual(ids,['q01','q02','q03','q04','q05'],'got '+JSON.stringify(ids));
assert.equal(q.totalDue,5);});
CHECK('S3 queue deterministic across calls',()=>{const a=JSON.stringify(nkFsrsQueue({}).cards.map(x=>x.id));const b=JSON.stringify(nkFsrsQueue({}).cards.map(x=>x.id));assert.equal(a,b);});
}

// ---------- S4 daily cap ----------
{
freshState({},{});
// 17 cards already reviewed today inside FSRS sessions (count toward the cap).
for(let i=10;i<=26;i++){const qid='q'+i;state.attempts[qid]=[mkAttempt('a'+i,T-2*DAY,true),mkAttempt('a'+i+'t',T-3600000,true,'fsrs-review')];state.reviews[qid]=mkReview({due:T-DAY,lastReview:T-2*DAY,stability:1<<(i-10)});}
// 1 learning card already seen today (exempt as a repeat).
state.attempts.q27=[mkAttempt('a27',T-2*DAY,true),mkAttempt('a27t',T-3600000,true,'fsrs-review')];state.reviews.q27=mkReview({due:T+5*60000,state:1,lastReview:T-10*60000,stability:0.007});
// 6 unseen review cards; low stability first after sorting by retrievability.
for(let i=28;i<=33;i++){const qid='q'+i;state.attempts[qid]=[mkAttempt('a'+i,T-2*DAY,true)];state.reviews[qid]=mkReview({due:T-DAY,lastReview:T-2*DAY,stability:1<<(i-28)});}
state.fsrsPreferences={desiredRetention:.9,dailyCap:20,maximumInterval:365};
const q=nkFsrsQueue({});
CHECK('S4 cap: 18 seen of 20 -> only 2 new admitted, learning repeat exempt',()=>{
assert.deepEqual(q.cards.map(x=>x.id),['q27','q28','q29'],'got '+JSON.stringify(q.cards.map(x=>x.id)));
assert.equal(q.rolledOver,3);assert.equal(q.totalDue,23);});
state.attempts.q30.push(mkAttempt('a30t',T-1800000,true,'fsrs-review'));
state.attempts.q31.push(mkAttempt('a31t',T-1800000,true,'fsrs-review'));
state.attempts.q32.push(mkAttempt('a32t',T-1800000,true,'fsrs-review'));
const q2=nkFsrsQueue({});
CHECK('S4b seen above cap -> no new admissions, repeat still exempt',()=>{assert.deepEqual(q2.cards.map(x=>x.id),['q27']);assert.equal(q2.rolledOver,3);});
}

// ---------- S4c daily cap after real reviews ----------
// Reviewing a card moves it out of `due`; it must still spend the cap.
{
freshState({},{});
for(let i=0;i<40;i++){const qid='q'+String(i).padStart(2,'0');state.attempts[qid]=[mkAttempt('a'+i,T-5*DAY,true)];state.reviews[qid]=mkReview({due:T-DAY,lastReview:T-5*DAY,stability:2+i,difficulty:5,state:2,scheduledDays:4,elapsedDays:4,repetitions:2});}
state.fsrsPreferences={desiredRetention:.9,dailyCap:20,maximumInterval:365};
const first=nkFsrsQueue({});
first.cards.forEach(c=>{T+=1000;nkFsrsRecordAttempt(c.id,1,5,'fsrs-review',3,T);});
const after=nkFsrsQueue({});
CHECK('S4c reviewed cards leave due but still spend the cap',()=>{assert.equal(first.cards.length,20);assert(first.cards.every(c=>!nkFsrsIsDue(state.reviews[c.id],T)));assert.equal(after.cards.length,0,'admitted '+after.cards.length+' past the cap');assert.equal(after.rolledOver,19);});
T=T0;
}

// ---------- S5 rating revisions ----------
{
const t1=T-3*DAY,t2=T-DAY,t3=T;
freshState({'q20':[mkAttempt('A1',t1,true,'practice',3),mkAttempt('A2',t2,true,'practice',3),mkAttempt('A3',t3,true,'practice',3)]});
nkFsrsReplay('q20',false);
const origDue=state.reviews.q20.due, origStab=state.reviews.q20.stability;
const attempt1=state.attempts.q20[0];
nkFsrsReviseRating('q20',attempt1,2);
CHECK('S5 revise #1 to Hard == independent [2,3,3] chain',()=>{const orc=chain('q20',[2,3,3],[t1,t2,t3]);assert.equal(state.reviews.q20.due,orc.due);assert.equal(state.reviews.q20.stability,orc.stability);assert.notEqual(state.reviews.q20.due,origDue);});
nkFsrsReviseRating('q20',attempt1,4);
CHECK('S5 revise again to Easy == [4,3,3] chain',()=>{const orc=chain('q20',[4,3,3],[t1,t2,t3]);assert.equal(state.reviews.q20.due,orc.due);assert.equal(state.reviews.q20.stability,orc.stability);});
CHECK('S5 revisions kept (2 entries), effective = latest',()=>{assert.equal(state.fsrsRatingRevisions.q20.length,2);const act=nkFsrsActiveAttempts('q20');assert.equal(act.length,3);assert.equal(act[0].rating,4);});
nkFsrsUndo();
CHECK('S5 undo latest revision returns to [2,3,3]',()=>{const orc=chain('q20',[2,3,3],[t1,t2,t3]);assert.equal(state.reviews.q20.due,orc.due);assert.equal(nkFsrsActiveAttempts('q20')[0].rating,2);});
nkFsrsUndo();
CHECK('S5 undo again returns to [3,3,3] original',()=>{const orc=chain('q20',[3,3,3],[t1,t2,t3]);assert.equal(state.reviews.q20.due,orc.due);assert.equal(state.reviews.q20.stability,origStab);});
CHECK('S5 cache == replay after revisions/undo',()=>{const cached=JSON.stringify(state.reviews.q20);nkFsrsReplay('q20',false);assert.equal(JSON.stringify(state.reviews.q20),cached);});
}

// ---------- S6 whole-card undo ----------
{
const t1=T-DAY,t2=T-3600000;
freshState({'q21':[mkAttempt('B1',t1,true,'practice',3),mkAttempt('B2',t2,true,'practice',3)]});
nkFsrsReplay('q21',false);
nkFsrsUndo();
CHECK('S6 undo newest attempt keeps card from B1',()=>{assert.equal(nkFsrsActiveAttempts('q21').length,1);const orc=chain('q21',[3],[t1]);assert.equal(state.reviews.q21.due,orc.due);assert.equal(nkFsrsEligibility(questions.find(q=>q.id==='q21')),'attempted');});
nkFsrsUndo();
CHECK('S6 undo last attempt removes card from FSRS entirely',()=>{assert.equal(state.reviews.q21,undefined);assert.equal(nkFsrsEligibility(questions.find(q=>q.id==='q21')),'');assert.equal(nkFsrsQueue({}).cards.some(x=>x.id==='q21'),false);});
CHECK('S6 third undo: nothing to undo, no crash',()=>{let threw=false;try{nkFsrsUndo();}catch(e){threw=true;}assert(!threw);});
}

// ---------- S7 pending recovery ----------
{
freshState();
state.activeSession={id:'s1',mode:'practice',questionIds:['q22'],index:0,answers:{},submitted:{},questionTimes:{},pendingRating:{q22:{id:'p22',selected:1,timeSpent:100,source:'practice',reviewedAt:T}}};
nkFsrsRecoverPending();
CHECK('S7 recover commits pending as Good with same id',()=>{const a=state.attempts.q22;assert.equal(a.length,1);assert.equal(a[0].id,'p22');assert.equal(a[0].rating,3);assert.equal(state.activeSession.pendingRating.q22,undefined);});
CHECK('S7 commit again no-op',()=>{const n=nkFsrsCommitPending('q22',3);assert.equal(n,false);assert.equal(state.attempts.q22.length,1);});
}

// ---------- S7b undo with a pending rating ----------
{
const t1=T-DAY;
freshState({'q27':[mkAttempt('B1',t1,true,'practice',3)]});
nkFsrsReplay('q27',false);
// A correct answer that has not been committed yet: the rating is pending.
// The question has an older committed rating, so undo must target the pending
// one rather than the older one.
state.activeSession={id:'s2',mode:'practice',questionIds:['q27'],index:0,answers:{},submitted:{},questionTimes:{},
  pendingRating:{q27:{id:'pending-27',selected:1,timeSpent:100,source:'practice',reviewedAt:T}}};
nkFsrsUndo();
CHECK('S7b undo commits the pending rating first',()=>{assert.equal(state.activeSession.pendingRating.q27,undefined,'undo must not leave the pending rating behind');});
CHECK('S7b undo then removes the rating it just committed',()=>{assert.equal(nkFsrsActiveAttempts('q27').length,1,'undo must target the pending rating, not an older one');});
CHECK('S7b the older rating survives',()=>{assert.equal(nkFsrsActiveAttempts('q27')[0].rating,3);});
}

// ---------- S7c undo with a pending rating on a question with no prior attempt ----------
{
freshState();
// The learner's very first correct answer: nothing has been committed yet, so
// state.attempts is empty and the pending rating is the only rating there is.
state.activeSession={id:'s3',mode:'practice',questionIds:['q28'],index:0,answers:{},submitted:{},questionTimes:{},
  pendingRating:{q28:{id:'pending-28',selected:1,timeSpent:100,source:'practice',reviewedAt:T}}};
nkFsrsUndo();
CHECK('S7c undo commits a pending rating on a question with no prior attempt',()=>{assert.equal(state.activeSession.pendingRating.q28,undefined,'undo must not leave the pending rating behind');});
CHECK('S7c undo removes the rating it just committed',()=>{assert.equal(nkFsrsActiveAttempts('q28').length,0,'undo must remove the pending rating it just committed');});
}

// ---------- S8 preview == record (fuzz determinism) ----------
{
freshState();
for(const r of [2,3,4]){
const qid=r===2?'q23':r===3?'q24':'q25';
const pv=nkFsrsPreview(qid,T,'');
nkFsrsRecordAttempt(qid,1,0,'practice',r,T);
CHECK('S8 preview==record grade '+r,()=>{const a=state.attempts[qid][0];assert.equal(a.schedulerAfter.due,new Date(pv[r].card.due).getTime(),'due');assert.equal(a.schedulerAfter.stability,Number(pv[r].card.stability));});}
const qid='q26';
nkFsrsRecordAttempt(qid,2,0,'practice',1,T-10*60000); // wrong -> Again
const pv2=nkFsrsPreview(qid,T,'');
nkFsrsRecordAttempt(qid,1,0,'practice',3,T);
CHECK('S8b relearning preview==record',()=>{const a=state.attempts[qid][1];assert.equal(a.schedulerAfter.due,new Date(pv2[3].card.due).getTime());});
}

// ---------- S9 settings changes don't rewrite history; cache==replay ----------
{
freshState();
nkFsrsRecordAttempt('q27',1,0,'practice',3,T-DAY);
nkFsrsSetPreference('desiredRetention',85);
nkFsrsRecordAttempt('q27',1,0,'practice',3,T);
CHECK('S9 per-attempt preferences stored',()=>{const a=state.attempts.q27;assert.equal(a[0].schedulerPreferences.desiredRetention,0.9);assert.equal(a[1].schedulerPreferences.desiredRetention,0.85);});
CHECK('S9 cache == replay with mixed prefs',()=>{const cached=JSON.stringify(state.reviews.q27);nkFsrsReplay('q27',false);assert.equal(JSON.stringify(state.reviews.q27),cached);});
CHECK('S9 settings clamps',()=>{nkFsrsSetPreference('desiredRetention',99);assert.equal(nkFsrsPreferences().desiredRetention,0.97);nkFsrsSetPreference('desiredRetention',50);assert.equal(nkFsrsPreferences().desiredRetention,0.8);nkFsrsSetPreference('dailyCap',9999);assert.equal(nkFsrsPreferences().dailyCap,300);nkFsrsSetPreference('maximumInterval',5);assert.equal(nkFsrsPreferences().maximumInterval,30);});
CHECK('S9 preference writes stamp per field',()=>{const s=state.fsrsPreferencesAt;assert.equal(s.desiredRetention,T);assert.equal(s.dailyCap,T);assert.equal(s.maximumInterval,T);});
}

// ---------- S10 eligibility ----------
{
freshState();
state.fsrsReviewEligible={};
CHECK('S10 unanswerable excluded',()=>{const q=questions.find(q=>q.id==='q30');assert.equal(nkFsrsEligibility(q),'');state.fsrsReviewEligible.q30={reason:'skipped',at:T};assert.equal(nkFsrsEligibility(q),'');assert.equal(nkFsrsQueue({}).cards.some(x=>x.id==='q30'),false);});
CHECK('S10 wrong > attempted > skipped priority',()=>{state.attempts.q31=[mkAttempt('a',T-DAY,false,'practice',1)];assert.equal(nkFsrsEligibility(questions.find(q=>q.id==='q31')),'wrong');state.attempts.q32=[mkAttempt('a',T-DAY,true)];state.fsrsReviewEligible.q32={reason:'skipped',at:T};assert.equal(nkFsrsEligibility(questions.find(q=>q.id==='q32')),'attempted');});
}

// ---------- S11 counts/forecast basics ----------
{
freshState({},{
'q01':mkReview({due:T-DAY,lastReview:T-3*DAY,stability:2}),
'q02':mkReview({due:nkFsrsDayEnd(T)+DAY+3600000,lastReview:T-DAY,stability:4}),
'q03':mkReview({due:nkFsrsDayEnd(T)-1,lastReview:T-3*DAY,stability:2}),
'q04':mkReview({due:T-DAY,lastReview:T-2*DAY,stability:25,needsAttention:true})});
state.attempts={q01:[mkAttempt('a',T-3*DAY,true)],q02:[mkAttempt('a',T-DAY,true)],q03:[mkAttempt('a',T-3*DAY,true)],q04:[mkAttempt('a',T-2*DAY,true)]};
const c=nkFsrsCounts(T),f=nkFsrsForecast();
CHECK('S11 counts due==3, overdue==2, attention==1',()=>{assert.equal(c.due,3);assert.equal(c.overdue,2);assert.equal(c.attention,1);assert.equal(c.mature,1);});
CHECK('S11 forecast: 3 today, 1 in two days',()=>{assert.equal(f[0],3);assert.equal(f[2],1);assert.equal(f.reduce((a,b)=>a+b,0),4);});
}

// ---------- S12 exam/CBT binary grading + source mapping ----------
{
freshState();
const c1=nkFsrsRecordAttempt('q33',1,0,'exam',undefined,T);
CHECK('S12 exam correct -> Good (3)',()=>{assert.equal(c1,true);assert.equal(state.attempts.q33[0].rating,3);});
nkFsrsRecordAttempt('q34',2,0,'exam',undefined,T);
CHECK('S12 exam wrong -> Again (1)',()=>{assert.equal(state.attempts.q34[0].rating,1);});
CHECK('S12 wrong answer with rating 3 still Again',()=>{nkFsrsRecordAttempt('q35',2,0,'practice',3,T);assert.equal(state.attempts.q35[0].rating,1);});
CHECK('S12 source mapping',()=>{assert.equal(nkFsrsSessionAttemptSource({originRoute:'fsrs'}),'fsrs-review');assert.equal(nkFsrsSessionAttemptSource({context:'spaced-review'}),'fsrs-review');assert.equal(nkFsrsSessionAttemptSource({studyModuleId:'m1'}),'study-module');assert.equal(nkFsrsSessionAttemptSource({}),'practice');});
}

// ---------- S13 skipped -> answered transition ----------
{
freshState();state.fsrsReviewEligible={q36:{reason:'skipped',at:T-1000}};
CHECK('S13 skipped card in queue ranked last, then answered',()=>{const q=nkFsrsQueue({});assert(q.cards.some(x=>x.id==='q36'));nkFsrsRecordAttempt('q36',1,0,'practice',3,T);assert.equal(nkFsrsEligibility(questions.find(q=>q.id==='q36')),'attempted');assert(state.reviews.q36.schemaVersion===2);});
}

// ---------- S14 mistakes: FSRS-only lapse never reopens a Practice mistake ----------
{
freshState();
state.attempts.q37=[mkAttempt('m1',T-2*DAY,false,'practice',1),mkAttempt('m2',T-DAY,true,'practice',3)];
CHECK('S14 resolved practice mistake stays resolved',()=>assert.equal(nkFsrsPracticeMistake('q37'),false));
state.attempts.q37.push(mkAttempt('m3',T-3600000,false,'fsrs-review',1));
CHECK('S14 fsrs-review lapse does not reopen it',()=>assert.equal(nkFsrsPracticeMistake('q37'),false));
state.attempts.q37.push(mkAttempt('m4',T-1800000,false,'practice',1));
CHECK('S14 new practice miss reopens it',()=>assert.equal(nkFsrsPracticeMistake('q37'),true));
}

// ---------- S15 cold determinism across the whole history ----------
{
freshState();
const times=[T-5*DAY,T-4*DAY,T-DAY,T-3600000];
times.forEach((t,i)=>nkFsrsRecordAttempt('q40',i%2?2:1,0,'practice',(i%3)+2,t));
const snap=JSON.stringify(state,Object.keys(state).sort());
const holder=[];
for(let k=0;k<3;k++){const c=JSON.parse(snap);state={...c};nkFsrsRebuildAll(false);holder.push(JSON.stringify(state.reviews));}
CHECK('S15 three cold rebuilds byte-identical',()=>{assert.equal(holder[0],holder[1]);assert.equal(holder[1],holder[2]);});
CHECK('S15 cache==replay after rebuild',()=>{const cached=JSON.stringify(state.reviews.q40);nkFsrsReplay('q40',false);assert.equal(JSON.stringify(state.reviews.q40),cached);});
}

// ---------- S16 damaged cache heals from stored attempts ----------
{
freshState();
state.attempts.q50=[mkAttempt('h1',T-3*DAY,true,'practice',3),mkAttempt('h2',T-DAY,true,'practice',3)];
delete state.reviews.q50;
nkFsrsRecordAttempt('q50',1,0,'practice',3,T);
CHECK('S16 record heals a missing derived cache',()=>{const r=state.reviews.q50;assert(r&&r.schemaVersion===2,'cache rebuilt');const cached=JSON.stringify(r);nkFsrsReplay('q50',false);assert.equal(JSON.stringify(state.reviews.q50),cached,'healed cache equals replay');});
}

// ---------- S17 queue performance canary ----------
{
freshState();
const N=2500;
for(let i=0;i<N;i++){const qid='p'+i;questions.push({id:qid,subject:'Anatomy',bank:'PrepLadder',chapterId:'0',correctOption:1,options:[{letter:'A',text:'a'},{letter:'B',text:'b'}]});BY_ID[qid]=questions[questions.length-1];}
for(let i=0;i<N;i++){const qid='p'+i,at=T-((i%400)+1)*DAY;state.attempts[qid]=[mkAttempt('pa'+i,at,true,'practice',3)];state.reviews[qid]=mkReview({due:T-3600000,lastReview:at,stability:0.8+(i%300),state:2});}
state.fsrsPreferences={desiredRetention:.9,dailyCap:150,maximumInterval:365};
const started=process.hrtime.bigint();
const q=nkFsrsQueue({});
const ms=Number(process.hrtime.bigint()-started)/1e6;
CHECK('S17 queue over '+(N+60)+' questions < 3000ms (got '+ms.toFixed(0)+'ms)',()=>{assert(ms<3000,'queue took '+ms.toFixed(0)+'ms');assert.equal(q.totalDue,N);assert.equal(q.cards.length,150);});
}

console.log(FAILED.length?('FSRS_AUDIT_FAIL '+FAILED.length+' :: '+FAILED.join(' | ')):'FSRS_AUDIT_BATTERY_OK');
process.exit(FAILED.length?1:0);
"""


def main() -> int:
    core = CORE.read_text(encoding="utf-8")
    script = STUBS + core + "\n" + SCENARIOS
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(script)
        test_path = Path(handle.name)
    try:
        proc = subprocess.run(["node", str(test_path)], cwd=ROOT, capture_output=True, text=True)
    finally:
        test_path.unlink(missing_ok=True)
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr[-4000:])
        raise SystemExit("FSRS_AUDIT_V1_TEST_FAIL")
    checks = proc.stdout.count("ok - ")
    print(f"FSRS_AUDIT_V1_TEST_OK: {checks} adversarial scenarios (boundaries, cap, revision chains, undo, fuzz, migration, heal, stamps, perf canary)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
