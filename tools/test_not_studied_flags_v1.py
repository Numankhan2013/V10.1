#!/usr/bin/env python3
"""Behavior tests for the "not studied yet" flag (not_studied_flags.js).

The session logic runs in Node against the real FSRS scheduler module, the real
Continue Practice module (finish / pause / resume / checkpoint) and the page's own
submitPractice / selectExam / submitExam / finishPracticeSession /
nkMarkSkippedFromSession / buildReviewSession declarations, with the flag module
installed over them in the page's order. The clock and Math.random are driven
by the test, so a flagged-then-unflagged run can be compared byte for byte with
a run that never touched the flag: FSRS cards, raw attempt events, rating
revisions, skip marks, due queue, counts, statistics, saved results, session
state and the sync payloads of those records.

Every scenario in docs/NOT_STUDIED_FLAGS.md has a case here.
"""

from pathlib import Path
import subprocess
import tempfile

from app_page import app_page, app_css
from js_extract import extract_function

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/not_studied_flags.js"
FSRS = ROOT / "app/src/main/modules/fsrs_scheduler.js"
RESUME = ROOT / "app/src/main/modules/continue_practice_resume.js"
ANALYSIS = ROOT / "app/src/main/modules/refined_analysis.js"
SYNC = ROOT / "app/src/main/modules/cross_device_sync.js"
HTML = ROOT / "app/src/main/assets/index.html"
VENDOR = ROOT / "app/src/main/assets/vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js"

PRELUDE = r'''
const assert=require('assert');global.window=globalThis;window.FSRS=require(%(vendor)s);
// The test owns time and randomness: at(t) sets both, so identical steps give identical ids.
const T0=1800000000000;let NOW=T0,RNG=1;Date.now=()=>NOW;Math.random=()=>{RNG=(RNG*16807)%%2147483647;return RNG/2147483647;};
function at(t){NOW=T0+t;RNG=(t%%2147483000)+7;}
const store=new Map();global.localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
const LS_KEY='qbank_state_v1';
const questions=['q1','q2','q3','q4','q5','q6','q7','q8'].map((id,i)=>({id,subject:'Anatomy',bank:'PrepLadder',chapterId:i<6?'c1':'c2',chapter:i<6?'Upper limb':'Thorax',question:'Stem '+id,correctOption:1,options:[{letter:'A',text:'a'},{letter:'B',text:'b'}]}));
const SUBJECTS=[{subject:'Anatomy',bank:'PrepLadder',topics:[{id:'c1',title:'Upper limb'},{id:'c2',title:'Thorax'}],questions}];
const CHAPTERS=[{id:'c1',title:'Upper limb'},{id:'c2',title:'Thorax'}],CHAPTER_BY_ID={c1:CHAPTERS[0],c2:CHAPTERS[1]};
const activeSubject='Anatomy';
function nkAllBankQuestions(){return questions;}
function chapterQuestions(cid){return questions.filter(q=>q.chapterId===String(cid));}
function nkFindStudyQuestion(id){return questions.find(q=>q.id===String(id))||null;}
function nkBankQuestionById(id){return nkFindStudyQuestion(id);}
function nkBankRecords(subject){return SUBJECTS.filter(r=>r.subject===subject);}
function nkTopicTitleForQuestion(q){return q.chapter;}
let state={};
let route={page:'practice'},routes=[],toasts=[],renders=0,started=null;
let BY_ID=Object.fromEntries(questions.map(q=>[q.id,q])),dashboard=()=>'<main></main>',morePage=()=>'<main></main>',practicePage=()=>'<main></main>',practiceActionBar=()=>'<div class="fixed-actions nk-session-footer"><div class="fixed-actions-inner"></div></div>',nextQ=()=>{},prevQ=()=>{},goIndex=()=>{},retryCurrent=()=>{},endSession=()=>{},navigate=(page,id)=>{routes.push([page,id]);route={page,id};},recordAttempt=()=>{},qAttempts=()=>[],nkRebuildReviews=()=>{};
function nkQuestionPresentationFor(){return {valid:true};}
let saveState=()=>{localStorage.setItem(LS_KEY,JSON.stringify(state));return true;};const render=()=>{renders++;},showToast=m=>toasts.push(m),savePracticeElapsed=()=>{},saveExamElapsed=()=>{},haptic=()=>{},closeQuestionNavigator=()=>{},esc=x=>String(x).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[c]),shell=x=>x,fmtNum=n=>String(n),navIcon=n=>'<svg data-icon="'+n+'"></svg>';
let startSession=(ids,mode,title)=>{started={ids,mode,title};return true;};
let testsPage=()=>'<main class="tests-page"></main>';
function nkCompleteStudyModule(){}
function nkExamSecondsPer(){return 60;} function nkExamTotalSeconds(s){return s.questionIds.length*60;}
const openBank=()=>{},openSubjectTopics=()=>{},nkOpenSubjectChapter=()=>{};
let nkLatestPracticeContext=()=>null,nkContinueRecentPractice=()=>{},continuePractice=()=>{};
window.QB={};window.addEventListener=()=>{};global.setTimeout=fn=>{fn();return 0;};
global.document={getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[],body:{insertAdjacentHTML:()=>{}},addEventListener:()=>{},visibilityState:'visible'};
let nkSessionHeader=(q,s,mode)=>'<header><div class="q-actions"><button class="icon-btn bookmark-toggle"></button></div></header>';
let openSessionReview=()=>{},openQuestionNavigator=()=>{};
let topics=()=>'<div class="nk-topic-list">'+CHAPTERS.map(c=>`<button class="nk-topic-row is-notstarted" onclick="window.QB.openChapter('${c.id}')"><span class="nk-topic-index">1</span><span class="nk-topic-copy"><strong>${c.title}</strong><small>6 questions</small></span></button>`).join('')+'</div>';
let chapterPage=cid=>`<section class="nk-chapter-hero"><div class="nk-chapter-title"><div class="nk-topic-library"><div class="nk-topic-map">${chapterQuestions(cid).map((q,i)=>`<button class="nk-library-row nk-topic-cell is-u" data-s="u" aria-label="Question ${i+1}, not attempted" onclick="window.QB.practiceOne('${q.id}')">${i+1}</button>`).join('')}</div></div></div><div class="nk-chapter-actions"><div class="nk-topic-options"><button class="nk-topic-option">Timed test</button></div></div></section>`;
// The analysis page's "Every answer" block, as refined_analysis.js renders it.
let resultPage=testId=>{const t=state.tests.find(x=>String(x.id)===String(testId));return `<main>${nkResultStrip(t)}<details class="nk-na-card nk-na-answers"><summary>Every answer</summary><div class="nk-result-questions">${t.questionIds.map((id,i)=>`<div><span class="nk-question-index">${i+1}</span></div>`).join('')}</div></details></main>`;};
'''

SCENARIOS = r'''
nkFsrsInit();
const IDS=['q1','q2','q3','q4','q5','q6','q7','q8'];
function reset(){state={attempts:{},reviews:{},tests:[],fsrsPreferences:null,fsrsReviewEligible:{},activeSession:null,bookmarks:{},fsrsMigratedAt:1};routes=[];toasts=[];at(0);}
const practice=(id,ids,t,extra={})=>{at(t);state.activeSession={id,mode:'practice',title:'Upper limb',questionIds:[...ids],sessionQuestionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,lastTick:NOW,elapsedMs:0,questionEnteredAt:NOW,questionTimes:{},context:'normal',originRoute:'topics',lifecycle:'active',...extra};return state.activeSession;};
const exam=(id,ids,t)=>{at(t);state.activeSession={id,mode:'exam',title:'CBT',questionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},timerMode:'global',originRoute:'tests'};return state.activeSession;};
const S=()=>state.activeSession,pos=qid=>S().questionIds.indexOf(qid);
const go=qid=>{S().index=pos(qid);};
function ans(qid,choice,t,ms=20000){at(t);go(qid);const s=S();s.questionTimes[qid]=ms;s.answers[qid]=choice;submitPractice();}
function look(qid,t,ms=30000){at(t);go(qid);S().questionTimes[qid]=ms;} // opened and left blank
function flag(qid,t){at(t);go(qid);return nkToggleNotStudied(qid,S().id);}
function rate(qid,r,t){at(t);go(qid);return nkRateCurrent(r,qid,S().id);}
function next(qid,t){at(t);go(qid);nextQ();}
function pick(qid,choice,t){at(t);go(qid);selectExam(choice);}
function finish(t){at(t);return finishPracticeSession();}
function submit(t){at(t);return submitExam(false);}
function pause(t){at(t);return nkPausePractice();}
// A reload between sessions: only what the state stores survives; the session comes back from its checkpoint.
function reload(t){at(t);state=JSON.parse(JSON.stringify(state));state.activeSession=null;}
function resume(id,t){at(t);return nkResumePracticeById(id);}
const sortObj=o=>o&&typeof o==='object'&&!Array.isArray(o)?Object.fromEntries(Object.keys(o).sort().map(k=>[k,sortObj(o[k])])):Array.isArray(o)?o.map(sortObj):o;
const only=(map,ids)=>Object.fromEntries(ids.filter(id=>map&&map[id]!==undefined).map(id=>[id,map[id]]));
// The sync payloads cross_device_sync.js builds for these records.
function syncPayload(ids){
  const out={attempts:[],notStudied:{},tests:[]};
  ids.forEach(id=>(state.attempts[id]||[]).forEach(a=>out.attempts.push(JSON.stringify({qid:id,attempt:a}))));
  ids.forEach(id=>{const item=nkNsClean(state.notStudied?.[id]);if(item)out.notStudied[id]=JSON.stringify(item);});
  (state.tests||[]).forEach(t=>out.tests.push(JSON.stringify(t)));return out;
}
// Everything that measures learning, read the way the app reads it.
function measures(ids=IDS){
  const keep=NOW;at(40*86400000);
  const queue=nkFsrsQueue({}),counts=nkFsrsCounts();
  const statRows=ids.map(id=>{const h=nkFsrsActiveAttempts(id).filter(a=>typeof a.correct==='boolean');return [id,nkFsrsEligibility(nkFindStudyQuestion(id)),h.length,h.filter(a=>a.correct).length,nkFsrsPracticeMistake(id),[...new Set(h.map(a=>new Date(Number(a.reviewedAt||a.at)).toDateString()))]];});
  NOW=keep;
  return {reviews:sortObj(only(state.reviews,ids)),attempts:only(state.attempts,ids),revisions:only(state.fsrsRatingRevisions||{},ids),eligible:only(state.fsrsReviewEligible,ids),
    due:queue.due.map(q=>q.id),cards:queue.cards.map(q=>q.id),counts,stats:statRows,tests:state.tests,
    session:state.activeSession?{answers:S().answers,submitted:S().submitted,pending:S().pendingRating||{},times:S().questionTimes}:null,
    checkpoints:(state.normalPracticeCheckpoints||[]).map(cp=>({id:cp.sessionId,lifecycle:cp.lifecycle,answers:cp.answers,submitted:cp.submitted,pending:cp.pendingFsrsRatings})),
    sync:{attempts:syncPayload(ids).attempts,tests:syncPayload(ids).tests}};
}
const same=(a,b,msg)=>assert.strictEqual(JSON.stringify(a),JSON.stringify(b),msg);
const run=fn=>{reset();fn();return {m:measures(),notStudied:JSON.parse(JSON.stringify(state.notStudied||{})),held:JSON.parse(JSON.stringify(state.notStudiedHeld||{})),sync:syncPayload(IDS)};};
const cleared=(r,qid)=>{assert.strictEqual(r.notStudied[qid]?.on,false,qid+' ends as a tombstone');assert.strictEqual(r.sync.notStudied[qid],JSON.stringify({on:false,updatedAt:r.notStudied[qid].updatedAt}),'the tombstone is what syncs');assert(!r.held[qid],'nothing stays put aside');};
const results=[];
function scenario(name,fn){fn();results.push(name);}
// An all-flagged session keeps no result, only a hidden shell (never a deleted record that sync could bring back).
function assertShell(t,flagged){
  assert(t.noResult===true,'the shell is marked noResult');same([t.questionIds,t.answers,t.questionTimes],[[],{},{}],'the shell holds no answers');
  same([t.correct,t.incorrect,t.attempted,t.unattempted,t.total,t.totalTimeMs],[0,0,0,0,0,0],'the shell counts nothing');
  same([...t.notStudiedIds].sort(),[...flagged].sort());same([...t.allQuestionIds].sort(),[...flagged].sort());assert(t.updatedAt>t.createdAt,'the shell is newer than any copy saved before cleaning');
  assert(!('practiceContext' in t)&&!('correctionOf' in t)&&!('marking' in t),'nothing that other screens read is kept');
}

// ───────── Flag then unflag before answering: as if never flagged ─────────
scenario('flag→unflag before answering, then skip = normal skip',()=>{
  const base=run(()=>{practice('s1',['q1','q2','q3'],0);ans('q1',2,1000);look('q2',2000);ans('q3',1,3000);rate('q3',3,3500);finish(5000);});
  const flagged=run(()=>{practice('s1',['q1','q2','q3'],0);ans('q1',2,1000);flag('q2',1500);flag('q2',1600);look('q2',2000);ans('q3',1,3000);rate('q3',3,3500);finish(5000);});
  same(flagged.m,base.m,'skip after flag/unflag is byte-identical to a plain skip');
  assert.strictEqual(base.m.eligible.q2.reason,'skipped');cleared(flagged,'q2');
});
scenario('flag→unflag before answering, then answer (wrong and correct+Hard) = normal FSRS',()=>{
  const steps=toggle=>()=>{practice('s1',['q1','q2'],0);if(toggle){flag('q1',500);flag('q1',600);flag('q2',650);flag('q2',660);}ans('q1',2,1000);ans('q2',1,2000);rate('q2',2,2100);next('q2',2200);finish(3000);};
  const base=run(steps(false)),flagged=run(steps(true));
  same(flagged.m,base.m,'answers after flag/unflag count exactly as normal');cleared(flagged,'q1');cleared(flagged,'q2');
});

// ───────── Answer, flag, unflag: the original answer and rating come back once ─────────
scenario('wrong answer → flag withdraws everything → unflag restores byte-identically',()=>{
  const base=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);});
  reset();practice('s1',['q1','q2'],0);ans('q1',2,1000);flag('q1',1500);
  const mid=measures();
  assert.strictEqual(mid.reviews.q1,undefined,'flagging withdraws the FSRS card');
  assert.strictEqual(mid.stats[0][2],0,'no active attempt, so no accuracy, insights, coverage, weak area or streak day');
  assert.strictEqual(mid.eligible.q1,undefined);assert(!mid.due.includes('q1'),'no due review');
  assert.strictEqual(state.attempts.q1.length,1,'no undo event is written for an in-session flag');
  flag('q1',1600);
  same(measures(),base.m,'unflag restores card, attempts, stats and due list exactly');
});
scenario('correct answer waiting for its rating → flag → unflag → rate Hard = baseline',()=>{
  const steps=toggle=>()=>{practice('s1',['q1','q2'],0);ans('q1',1,1000);if(toggle){flag('q1',1200);
      assert.strictEqual(nkFsrsRatingMarkup('q1'),'','flagged: the rating dock is hidden');assert.strictEqual(rate('q1',4,1210),false,'flagged: no rating is taken');}
    next('q1',1250);if(toggle){assert.strictEqual(nkFsrsActiveAttempts('q1').length,0,'moving on commits the default rating hidden: nothing counts');assert(!state.reviews.q1,'no card');flag('q1',1300);}
    rate('q1',2,1400);next('q1',1500);finish(2000);};
  const base=run(steps(false)),flagged=run(steps(true));
  same(flagged.m,base.m,'the withheld answer returns with its original time, default rating and later revision, once');cleared(flagged,'q1');
  const waiting=toggle=>()=>{practice('s1',['q1','q2'],0);ans('q1',1,1000);if(toggle){flag('q1',1200);flag('q1',1300);}rate('q1',2,1400);next('q1',1500);finish(2000);};
  same(run(waiting(true)).m,run(waiting(false)).m,'flag/unflag while the rating waits: the rating chosen after is committed directly, as normal');
});
scenario('correct answer rated Hard (committed) → flag → unflag = baseline rating Hard',()=>{
  const steps=toggle=>()=>{practice('s1',['q1'],0);ans('q1',1,1000);rate('q1',2,1100);if(toggle){flag('q1',1200);assert(!state.reviews.q1);flag('q1',1300);}finish(2000);};
  same(run(steps(true)).m,run(steps(false)).m,'rating Hard survives the flag/unflag');
});
scenario('rating revised Good→Easy, then flag/unflag = baseline',()=>{
  const steps=toggle=>()=>{practice('s1',['q1'],0);ans('q1',1,1000);rate('q1',3,1100);rate('q1',4,1150);if(toggle){flag('q1',1200);flag('q1',1300);}finish(2000);};
  same(run(steps(true)).m,run(steps(false)).m,'rating revisions come back with the answer');
});

// ───────── Repeated toggling never accumulates events ─────────
scenario('25 toggles after a wrong answer, ending unflagged = never flagged',()=>{
  const base=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);finish(9000);});
  const many=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);for(let i=0;i<26;i++)flag('q1',2000+i*10);finish(9000);});
  same(many.m,base.m,'even number of toggles: identical to never flagging');cleared(many,'q1');
});
scenario('25 toggles ending flagged = one flag',()=>{
  const once=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);flag('q1',2000);finish(9000);});
  const many=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);for(let i=0;i<25;i++)flag('q1',2000+i*10);finish(9000);});
  same(many.m,once.m,'odd number of toggles: identical to a single flag');
  assert.strictEqual(many.m.attempts.q1.filter(a=>a.isUndo).length,1,'one settling undo event at the end, however many toggles');
});
scenario('toggling a correct pending answer many times keeps one pending rating',()=>{
  const base=run(()=>{practice('s1',['q1'],0);ans('q1',1,1000);next('q1',3000);finish(4000);});
  const many=run(()=>{practice('s1',['q1'],0);ans('q1',1,1000);for(let i=0;i<10;i++)flag('q1',1100+i);next('q1',3000);finish(4000);});
  same(many.m,base.m,'no duplicate or lost FSRS update');
});

// ───────── Answering while flagged ─────────
scenario('flag, then answer while flagged (hidden), then unflag = baseline',()=>{
  const steps=toggle=>()=>{practice('s1',['q1','q2'],0);if(toggle)flag('q1',500);ans('q1',2,1000);if(toggle){assert.strictEqual(nkFsrsActiveAttempts('q1').length,0,'answer while flagged is withheld');assert(!state.reviews.q1);flag('q1',1500);}ans('q2',1,2000);next('q2',2100);finish(3000);};
  const base=run(steps(false)),flagged=run(steps(true));same(flagged.m,base.m,'unflag gives back the answer made while flagged');cleared(flagged,'q1');
});
scenario('flag, correct answer while flagged, unflag, move on (Good) = baseline',()=>{
  const steps=toggle=>()=>{practice('s1',['q1'],0);if(toggle)flag('q1',500);ans('q1',1,1000);if(toggle)flag('q1',1500);next('q1',1600);finish(3000);};
  same(run(steps(true)).m,run(steps(false)).m);
});
scenario('flag before answering, answer, finish: withheld and settled',()=>{
  const r=run(()=>{practice('s1',['q1','q2','q3'],0);flag('q2',500);ans('q2',2,1000);ans('q1',1,1100);rate('q1',3,1150);look('q3',1300,40000);flag('q3',1350);finish(2000);});
  assert.strictEqual(r.m.reviews.q2,undefined);assert.strictEqual(r.m.eligible.q3,undefined,'flagged and skipped: no skip card');
  const t=r.m.tests.at(-1);same(t.questionIds,['q1']);same([...t.notStudiedIds].sort(),['q2','q3']);same(t.allQuestionIds,['q1','q2','q3']);
  assert(t.total===1&&t.correct===1&&t.attempted===1&&t.unattempted===0,'session record counts exclude flagged');
  assert(r.m.attempts.q2.some(a=>a.isUndo&&a.reason==='not-studied'),'finishing settles the withheld answer with an undo event (older app versions never count it)');
  assert(!r.m.checkpoints.find(c=>c.id==='s1')?.pending?.q2,'the resume checkpoint carries no rating for it');
});

// ───────── Earlier card and earlier sessions ─────────
scenario('question with an earlier FSRS card: flag leaves the card exactly as before this session',()=>{
  reset();practice('s1',['q1'],0);ans('q1',2,1000);finish(2000);
  practice('s2',['q1'],86400000*3);const before=JSON.stringify(sortObj(state.reviews.q1)),eligibleBefore=nkFsrsEligibility(questions[0]);
  ans('q1',1,86400000*3+1000);rate('q1',3,86400000*3+1100);assert.notStrictEqual(JSON.stringify(sortObj(state.reviews.q1)),before);
  flag('q1',86400000*3+1200);
  assert.strictEqual(JSON.stringify(sortObj(state.reviews.q1)),before,'the earlier card is back byte for byte, not deleted');
  assert.strictEqual(nkFsrsActiveAttempts('q1').length,1,'the earlier answer still counts once');
  assert.strictEqual(nkFsrsEligibility(questions[0]),eligibleBefore);
  finish(86400000*3+2000);
  assert.strictEqual(JSON.stringify(sortObj(state.reviews.q1)),before,'and stays so after the session');
  const base=run(()=>{practice('s1',['q1'],0);ans('q1',2,1000);finish(2000);practice('s2',['q1'],86400000*3);ans('q1',1,86400000*3+1000);rate('q1',3,86400000*3+1100);finish(86400000*3+2000);});
  const toggled=run(()=>{practice('s1',['q1'],0);ans('q1',2,1000);finish(2000);practice('s2',['q1'],86400000*3);ans('q1',1,86400000*3+1000);rate('q1',3,86400000*3+1100);flag('q1',86400000*3+1200);flag('q1',86400000*3+1300);finish(86400000*3+2000);});
  same(toggled.m,base.m,'with an earlier card, flag/unflag is byte-identical too');
});
for(const settled of [true,false])scenario(`flag from an earlier session (${settled?'finished':'abandoned'}), answered in a later practice: clears, counts once`,()=>{
  const steps=()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);flag('q1',1100);if(settled)finish(2000);else{state.activeSession=null;}
    practice('s2',['q1','q3'],86400000);ans('q1',1,86400000+1000);rate('q1',3,86400000+1100);finish(86400000+2000);};
  const r=run(steps);
  assert.strictEqual(r.notStudied.q1.on,false,'answering in a later session clears the flag');
  const active=nkFsrsActiveAttempts('q1');assert.strictEqual(active.length,1,'only the later answer counts');assert.strictEqual(active[0].sessionId,'s2');
  assert.strictEqual(r.m.attempts.q1.filter(a=>a.isUndo).length,1,'the earlier withheld answer is withdrawn exactly once, for good');
  const base=run(()=>{practice('s2',['q1','q3'],86400000);ans('q1',1,86400000+1000);rate('q1',3,86400000+1100);finish(86400000+2000);});
  same(r.m.reviews,base.m.reviews,'the card is what a single later answer builds');same(r.m.due,base.m.due);same(r.m.stats.slice(0,1).map(x=>x.slice(1)),base.m.stats.slice(0,1).map(x=>x.slice(1)));
  same(r.m.tests.at(-1),base.m.tests.at(-1),'the later session record is normal');cleared(r,'q1');
});
scenario('re-flagged during the later practice: stays flagged, later answer excluded too',()=>{
  const r=run(()=>{practice('s1',['q1'],0);ans('q1',2,1000);flag('q1',1100);finish(2000);practice('s2',['q1','q2'],86400000);ans('q1',1,86400000+1000);flag('q1',86400000+1100);ans('q2',2,86400000+1200);finish(86400000+2000);});
  assert.strictEqual(r.notStudied.q1.on,true);assert.strictEqual(r.notStudied.q1.session,'s2');
  assert.strictEqual(nkFsrsActiveAttempts('q1').length,0,'neither answer counts');assert.strictEqual(r.m.reviews.q1,undefined);
  same(r.m.tests.at(-1).questionIds,['q2']);
});
scenario('unflag an earlier session\'s flag during a later session: counts normally, tombstone syncs, old answer stays out',()=>{
  const r=run(()=>{practice('s1',['q1'],0);ans('q1',2,1000);flag('q1',1100);state.activeSession=null;
    practice('s2',['q1','q2'],86400000);flag('q1',86400000+500);assert.strictEqual(nkFsrsActiveAttempts('q1').length,0,'the earlier withheld answer does not come back');
    ans('q1',1,86400000+1000);next('q1',86400000+1100);finish(86400000+2000);});
  const base=run(()=>{practice('s2',['q1','q2'],86400000);ans('q1',1,86400000+1000);next('q1',86400000+1100);finish(86400000+2000);});
  same(r.m.reviews,base.m.reviews);same(r.m.due,base.m.due);same(r.m.tests,base.m.tests);cleared(r,'q1');
});
scenario('"Practice flagged (N)" session: answers clear their flags and count; unanswered stay flagged',()=>{
  reset();practice('s1',['q1','q2','q3'],0);flag('q1',100);flag('q2',200);flag('q3',300);finish(1000);
  assert.strictEqual(state.tests.length,1,'all questions flagged: only a hidden shell is kept');assertShell(state.tests[0],['q1','q2','q3']);assert(toasts.at(-1).includes('no result was saved'));
  let captured=null;const keep=startSession;startSession=(ids,mode,title)=>{captured={ids,mode,title};return true;};
  nkPracticeNotStudied('c1');startSession=keep;same(captured.ids,['q1','q2','q3']);assert.strictEqual(captured.mode,'practice');assert(/Not studied/.test(captured.title));
  practice('s2',captured.ids,86400000);ans('q1',2,86400000+1000);ans('q2',1,86400000+1100);next('q2',86400000+1200);finish(86400000+2000);
  assert.strictEqual(state.notStudied.q1.on,false);assert.strictEqual(state.notStudied.q2.on,false);assert.strictEqual(state.notStudied.q3.on,true);
  same(state.tests.at(-1).questionIds,['q1','q2']);assert.strictEqual(nkFsrsActiveAttempts('q1').length+nkFsrsActiveAttempts('q2').length,2);
  same(nkNsTopicIds('c1'),['q3']);
});

// ───────── Pause / resume ─────────
scenario('answer, flag, pause, reload, resume, unflag = baseline',()=>{
  const steps=toggle=>()=>{practice('s1',['q1','q2','q3'],0);ans('q1',2,1000);ans('q2',1,1500);if(toggle){flag('q1',1600);flag('q2',1700);}pause(2000);reload(3000);resume('s1',4000);
    if(toggle){assert.strictEqual(nkFsrsActiveAttempts('q1').length,0,'still withheld after resume');flag('q1',4100);go('q2');flag('q2',4200);}
    rate('q2',2,4300);next('q2',4400);ans('q3',1,4500);next('q3',4600);finish(5000);};
  const base=run(steps(false)),flagged=run(steps(true));
  same(flagged.m,base.m,'the put-aside answer and rating survive pause/reload/resume and come back exactly');cleared(flagged,'q1');cleared(flagged,'q2');
});
scenario('flag before pause, answer after resume while flagged, then unflag = baseline',()=>{
  const steps=toggle=>()=>{practice('s1',['q1','q2'],0);if(toggle)flag('q1',500);pause(1000);reload(1500);resume('s1',2000);ans('q1',2,2500);if(toggle){assert.strictEqual(nkFsrsActiveAttempts('q1').length,0,'the flag made before pause is still this session\'s flag');flag('q1',2600);}finish(3000);};
  same(run(steps(true)).m,run(steps(false)).m);
});
scenario('flag kept through pause: excluded from the result',()=>{
  const r=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);flag('q1',1100);pause(1500);reload(1600);resume('s1',1700);ans('q2',1,1800);next('q2',1900);finish(2000);});
  same(r.m.tests.at(-1).questionIds,['q2']);assert.strictEqual(r.m.reviews.q1,undefined);
});

// ───────── Due review session ─────────
scenario('flagged question in a due-review session: earlier card unchanged and still due; unflag = baseline',()=>{
  const pre=()=>{practice('s1',['q1'],0);ans('q1',2,1000);finish(2000);};
  reset();pre();const card=JSON.stringify(sortObj(state.reviews.q1));
  practice('r1',['q1'],86400000*5,{context:'fsrs',originRoute:'fsrs'});ans('q1',1,86400000*5+1000);rate('q1',3,86400000*5+1050);
  assert.strictEqual(nkFsrsActiveAttempts('q1').at(-1).source,'fsrs-review');flag('q1',86400000*5+1100);
  assert.strictEqual(JSON.stringify(sortObj(state.reviews.q1)),card,'the card is exactly what it was before the review');
  at(86400000*5+1200);assert(nkFsrsQueue({}).due.some(q=>q.id==='q1'),'it is still due: the earlier card is kept, only today\'s answer is withheld');
  const base=run(()=>{pre();practice('r1',['q1'],86400000*5,{context:'fsrs',originRoute:'fsrs'});ans('q1',1,86400000*5+1000);next('q1',86400000*5+1500);finish(86400000*5+2000);});
  const toggled=run(()=>{pre();practice('r1',['q1'],86400000*5,{context:'fsrs',originRoute:'fsrs'});ans('q1',1,86400000*5+1000);flag('q1',86400000*5+1100);flag('q1',86400000*5+1200);next('q1',86400000*5+1500);finish(86400000*5+2000);});
  same(toggled.m,base.m);
});

// ───────── Timed tests / mocks / CBT ─────────
scenario('timed test: flag then submit (answered and unanswered): nothing recorded, result excludes them',()=>{
  const r=run(()=>{exam('e1',['q1','q2','q3','q4'],0);pick('q1',1,100);flag('q1',200);flag('q2',300);pick('q3',2,400);look('q4',500,40000);submit(1000);});
  assert.strictEqual(nkFsrsActiveAttempts('q1').length,0);assert.strictEqual(r.m.eligible.q2,undefined,'flagged unanswered: no skip card');
  const t=r.m.tests.at(-1);same(t.questionIds,['q3','q4']);assert(t.total===2&&t.incorrect===1&&t.attempted===1&&t.unattempted===1);
  same(t.allQuestionIds,['q1','q2','q3','q4']);
});
scenario('timed test: flag→unflag counts exactly as never flagged',()=>{
  const steps=toggle=>()=>{exam('e1',['q1','q2'],0);pick('q1',1,100);if(toggle){flag('q1',200);flag('q1',300);flag('q2',310);flag('q2',320);}look('q2',400,40000);submit(1000);};
  same(run(steps(true)).m,run(steps(false)).m);
});
scenario('timed test: answer, flag, change answer after flagging: excluded',()=>{
  const r=run(()=>{exam('e1',['q1','q2'],0);pick('q1',1,100);flag('q1',200);pick('q1',2,300);pick('q2',1,400);submit(1000);});
  assert.strictEqual(nkFsrsActiveAttempts('q1').length,0);same(r.m.tests.at(-1).questionIds,['q2']);assert.strictEqual(r.notStudied.q1.on,true);
});
scenario('timed test: flag from before the test clears on answering; changing the answer still counts once',()=>{
  const r=run(()=>{practice('s0',['q1'],0);flag('q1',100);state.activeSession=null;exam('e1',['q1','q2'],86400000);pick('q1',2,86400000+100);pick('q1',1,86400000+200);submit(86400000+1000);});
  assert.strictEqual(r.notStudied.q1.on,false);assert.strictEqual(nkFsrsActiveAttempts('q1').length,1);assert.strictEqual(nkFsrsActiveAttempts('q1')[0].correct,true);
});
scenario('timed test: question with an earlier card flagged: card untouched',()=>{
  reset();practice('s1',['q1'],0);ans('q1',2,1000);finish(2000);const card=JSON.stringify(state.reviews.q1);
  exam('e1',['q1','q2'],86400000);pick('q1',1,86400000+100);flag('q1',86400000+200);pick('q2',1,86400000+300);submit(86400000+1000);
  assert.strictEqual(JSON.stringify(state.reviews.q1),card);assert.strictEqual(nkFsrsActiveAttempts('q1').length,1);
});
scenario('timed test: every question flagged saves no result',()=>{
  reset();exam('e1',['q6'],0);flag('q6',100);submit(1000);assert.strictEqual(state.tests.length,1);assertShell(state.tests[0],['q6']);assert.strictEqual(routes.at(-1)[0],'tests');
});

// ───────── Results, analysis grid and Review Solutions ─────────
scenario('result grids and Review Solutions show flagged questions in place as "Not studied"',()=>{
  reset();exam('e1',['q1','q2','q3','q4'],0);pick('q1',1,100);flag('q2',200);look('q3',300,1000);pick('q4',2,400);submit(1000);
  const t=state.tests.at(-1),strip=nkResultStrip(t);
  const cells=[...strip.matchAll(/<button type="button" class="(is-[a-z]+)"[^>]*aria-label="Question (\d+): ([^"]*)"/g)].map(m=>[m[2],m[1],m[3]]);
  same(cells,[['1','is-correct','Correct'],['2','is-ns','Not studied, not scored'],['3','is-omitted','Omitted'],['4','is-incorrect','Incorrect']],'flagged cell is is-ns, distinct from omitted/skipped');
  assert(/class="is-ns"[^>]*><svg class="nk-ns-icon"/.test(strip),'the flagged cell carries the flag glyph');
  assert(strip.includes('1 not studied · left out of the score'),'the strip says what the flag means');
  const page=resultPage(t.id);assert(/<span class="nk-question-index">2<\/span>[\s\S]*?nk-status is-ns/.test(page),'Every answer lists it in place as Not studied');
  assert.strictEqual((page.match(/nk-question-index/g)||[]).length,4);
  const review=buildReviewSession(t);same(review.questionIds,['q1','q2','q3','q4'],'Review Solutions includes it in order');same(review.notStudiedIds,['q2']);assert.strictEqual(review.submitted.q2,false);
  assert(t.total===3,'and the score still leaves it out');
  const old={id:'legacy',kind:'practice',questionIds:['q1'],notStudiedIds:['q2'],answers:{},practiceContext:{questionIds:['q2','q1']},createdAt:1};
  same(nkNsResultOrder(old),['q2','q1'],'a result saved before allQuestionIds keeps the practice order');
});

// ───────── Results already saved are never rewritten ─────────
scenario('older results are never rewritten by a later flag',()=>{
  reset();state.tests.push({id:'old',kind:'practice',questionIds:['q1','q2'],answers:{q2:1},questionTimes:{},correct:1,incorrect:0,attempted:1,total:2,unattempted:1,createdAt:T0-86400000});
  state.notStudied={q1:{on:true,at:T0,updatedAt:T0}};navigate('result','old');same(state.tests[0].questionIds,['q1','q2']);
  state.notStudied={};practice('s1',['q1','q2'],0);ans('q1',2,100);flag('q1',200);ans('q2',2,300);finish(1000);const r=state.tests.at(-1),snap=JSON.stringify(r);navigate('result',r.id);assert.strictEqual(JSON.stringify(r),snap,'a result is cleaned once');
  assert(r.updatedAt>r.createdAt,'the cleaned result is newer, so it wins over any copy synced before cleaning');
});

// ───────── Topic page and header ─────────
scenario('topic list badge, topic grid corner flag, Practice flagged action, header button',()=>{
  reset();state.notStudied={q2:{on:true,at:1,updatedAt:1},q5:{on:true,at:1,updatedAt:1},q7:{on:false,updatedAt:2}};
  const list=topics();
  assert(/openChapter\('c1'\)[\s\S]*?<small>6 questions<span class="nk-ns-badge" aria-label="2 flagged not studied">[\s\S]*?2<\/span><\/small>/.test(list));
  assert(!/openChapter\('c2'\)[\s\S]*?nk-ns-badge/.test(list));
  const page=chapterPage('c1');
  assert.strictEqual((page.match(/nk-topic-cell is-u is-ns/g)||[]).length,2);
  assert(page.includes("aria-label=\"Question 2, not attempted, flagged not studied\" onclick=\"window.QB.practiceOne('q2')\">2<span class=\"nk-ns-corner\">"));
  assert(page.includes('<ul class="nk-topic-legend"><li class="is-ns"><b>2</b> not studied</li></ul>'));
  assert(page.includes("window.QB.nkPracticeNotStudied('c1')")&&page.includes('<span>Practice flagged</span><small>2</small>'));
  assert(!chapterPage('c2').includes('nk-ns'));assert(nkPracticeNotStudied('c2')===false);
  assert(nkSessionHeader({id:'q2'},{id:'s9',mode:'practice'},'practice').includes('nk-ns-toggle is-on" aria-pressed="true"'));
  assert(!nkSessionHeader({id:'q2'},{id:'r',mode:'review'},'review').includes('nk-ns-toggle'),'Review Solutions has no flag');
  practice('s1',['q1','q2'],0);assert.strictEqual(nkToggleNotStudied('q2',S().id),false,'only the current question can be flagged');assert.strictEqual(nkToggleNotStudied('q1','other'),false,'a stale session cannot flag');
});

// ───────── Fixes (2026-11-14 bug report): one case per fix ─────────
// Every write of the state, as storage receives it (sync captures after each write).
function writes(fn){const seen=[],set=localStorage.setItem;localStorage.setItem=(k,v)=>{if(k===LS_KEY)seen.push(JSON.parse(v));return set(k,v);};try{fn();}finally{localStorage.setItem=set;}return seen;}
scenario('fix 1/12: an all-flagged timed test is a hidden shell from its first save, never deleted; mock and make-up links survive',()=>{
  reset();let saves=writes(()=>{const s=exam('e1',['q1','q2'],0);s.scheduledMockId='m1';s.marking={correct:4,wrong:-1,blank:0};pick('q1',1,100);flag('q1',200);flag('q2',300);submit(1000);});
  const id='exam_e1',copies=saves.map(st=>(st.tests||[]).find(t=>t.id===id)).filter(Boolean);
  assert(copies.length>0,'the result was saved');assert(copies.every(t=>t.noResult===true&&t.questionIds.length===0&&!Object.keys(t.answers).length),'no write ever held the unclean result, so sync never queued one');
  assert.strictEqual(state.tests.length,1);const shell=state.tests[0];assertShell(shell,['q1','q2']);
  assert.strictEqual(shell.scheduledMockId,'m1','a scheduled mock still finds its sitting (taken, not missed)');same(shell.allQuestionIds,['q1','q2']);
  assert.strictEqual(nkFsrsActiveAttempts('q1').length,0,'the flagged answers count nowhere');assert(toasts.at(-1).includes('no result was saved'));assert.strictEqual(routes.at(-1)[0],'tests');
  routes=[];navigate('result',id);assert.strictEqual(routes.at(-1)[0],'tests','opening the shell later goes back to its origin');
  assert.strictEqual(resultPage(id),testsPage(),'a direct link to the shell shows the tests page');
  // A practice make-up / revision finish keeps the same shell.
  reset();saves=writes(()=>{practice('s1',['q1','q2'],0,{makeupFor:'m2'});ans('q1',2,1000);flag('q1',1100);flag('q2',1200);finish(2000);});
  assert(saves.map(st=>(st.tests||[]).find(t=>t.id==='practice_s1')).filter(Boolean).every(t=>t.noResult),'Practice: clean from the first write too');
  assertShell(state.tests[0],['q1','q2']);
  // A partly flagged result is clean at its first write as well.
  reset();saves=writes(()=>{exam('e2',['q1','q2','q3'],0);pick('q1',1,100);flag('q2',200);pick('q3',2,300);submit(1000);});
  assert(saves.map(st=>(st.tests||[]).find(t=>t.id==='exam_e2')).filter(Boolean).every(t=>Array.isArray(t.notStudiedIds)&&!t.questionIds.includes('q2')),'never saved with the flagged question in the score');
});
scenario('fix 2: a Practice finish whose save fails does not settle; unflag still restores',()=>{
  const base=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);});
  reset();practice('s1',['q1','q2'],0);ans('q1',2,1000);flag('q1',1100);
  const set=localStorage.setItem;localStorage.setItem=()=>{throw new Error('quota');};let out;try{out=finish(1500);}finally{localStorage.setItem=set;}
  assert.strictEqual(out,false,'the finish failed');assert.strictEqual(S().id,'s1','the session is still active (restored copy)');
  assert(!state.attempts.q1.some(a=>a.isUndo),'no undo event was written');assert(state.notStudiedHeld.q1,'what was kept aside is still there');
  flag('q1',1600);same(measures(),base.m,'unflag gives the answer back exactly');
});
scenario('fix 3: a flagged question with only a skip mark leaves Today\'s Review and its counts; unflag brings it back',()=>{
  reset();practice('s1',['q1','q2'],0);look('q1',500,30000);ans('q2',1,1000);next('q2',1100);finish(2000);
  assert.strictEqual(state.fsrsReviewEligible.q1.reason,'skipped');
  practice('s2',['q1'],86400000);flag('q1',86400000+100);
  at(86400000*4);assert(!nkFsrsQueue({}).cards.some(q=>q.id==='q1'),'not in Today\'s Review three days later');assert.strictEqual(nkFsrsEligibility(questions[0]),'');
  const flaggedCounts=nkFsrsCounts();assert.strictEqual(state.fsrsReviewEligible.q1.reason,'skipped','the skip mark itself is kept');
  flag('q1',86400000*4+100);assert.strictEqual(nkFsrsEligibility(questions[0]),'skipped','unflagged: eligible again');assert(nkFsrsQueue({}).cards.some(q=>q.id==='q1'));assert.strictEqual(nkFsrsCounts().eligible,flaggedCounts.eligible+1);
  reset();practice('s1',['q1'],0);ans('q1',2,1000);finish(2000);practice('s2',['q1'],86400000*3);flag('q1',86400000*3+100);
  at(86400000*3+200);assert(nkFsrsQueue({}).due.some(q=>q.id==='q1'),'with earlier answers it keeps its card and stays due');
});
scenario('fix 4: no flag once a timed question\'s time is up; the timed result shows the score counting flags',()=>{
  reset();const s=exam('e1',['q1','q2'],0);s.timerMode='per-question';s.strictExpired={q1:true};
  assert.strictEqual(flag('q1',100),false,'expired per-question item: refused');assert(!nkNsIsFlagged('q1'));assert(/Time is up/.test(toasts.at(-1)));
  reset();exam('e2',['q1','q2'],0);flag('q1',100);assert(nkNsIsFlagged('q1'));
  assert.strictEqual(flag('q2',200000),false,'test clock ran out: refused');assert(!nkNsIsFlagged('q2'));
  assert.strictEqual(flag('q1',200100),true,'unflagging is still allowed');assert(!nkNsIsFlagged('q1'));
  reset();exam('e3',['q1','q2','q3','q4'],0);pick('q1',1,100);pick('q2',1,150);flag('q2',200);pick('q3',2,300);submit(1000);
  const strip=nkResultStrip(state.tests.at(-1));assert(strip.includes('1 not studied · left out of the score · 25% counting them'),'raw score with the flagged question counted');
  reset();practice('s1',['q1','q2'],0);ans('q1',1,1000);next('q1',1100);flag('q2',1200);finish(2000);assert(!nkResultStrip(state.tests.at(-1)).includes('counting them'),'Practice keeps its line');
});
scenario('fix 5: a flag synced from another session keeps an answer this session counted',()=>{
  const r=run(()=>{practice('s1',['q1','q2','q3'],0);ans('q1',2,1000);nkNsMergeEntry('q1',{on:true,at:500,updatedAt:500,session:'sB'});nkNsMergeEntry('q3',{on:true,at:600,updatedAt:600,session:'sB'});ans('q2',1,1500);next('q2',1600);finish(2000);});
  const t=r.m.tests.at(-1);same(t.questionIds,['q1','q2'],'q1 stays in the result: its answer counts in FSRS');same(t.notStudiedIds,['q3'],'an unanswered question flagged elsewhere is still left out');
  assert(t.total===2&&t.incorrect===1&&t.correct===1);assert.strictEqual(nkFsrsActiveAttempts('q1').length,1);assert(r.m.reviews.q1,'its card is there');assert.strictEqual(r.notStudied.q1.on,true);
});
scenario('fix 6: a resumed session does not score an answer a later session withdrew',()=>{
  const r=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);flag('q1',1100);ans('q2',1,1200);next('q2',1300);pause(1500);
    exam('t1',['q1','q3'],2000);pick('q1',1,2100);pick('q3',1,2200);submit(3000);
    resume('s1',4000);finish(5000);});
  const t=r.m.tests.find(x=>x.id==='practice_s1');same(t.questionIds,['q2'],'q1 is left out of s1');same(t.notStudiedIds,['q1']);same(t.allQuestionIds,['q1','q2']);assert(t.total===1&&t.correct===1);
  const active=nkFsrsActiveAttempts('q1');assert.strictEqual(active.length,1);assert.strictEqual(active[0].sessionId,'t1','FSRS has only the later answer');
  same(r.m.tests.find(x=>x.id==='exam_t1').questionIds,['q1','q3'],'the later test counts it normally');
});
scenario('fix 7: discarding or abandoning a Practice settles its flagged answers; stale kept-aside entries are pruned',()=>{
  reset();practice('s1',['q1','q2'],0);ans('q1',2,1000);flag('q1',1100);pause(1500);
  assert(state.notStudiedHeld.q1);at(2000);nkDiscardNormalPractice('s1');
  assert(!state.notStudiedHeld.q1,'nothing stays kept aside');const a1=state.attempts.q1.find(a=>!a.isUndo);
  assert(state.attempts.q1.some(a=>a.isUndo&&a.undoOf===a1.id&&a.reason==='not-studied'),'the hidden answer is withdrawn for good (older versions never count it)');
  assert.strictEqual(nkFsrsActiveAttempts('q1').length,0);
  reset();practice('r1',['q1','q2'],0,{context:'spaced-review',originRoute:'fsrs'});ans('q1',2,1000);flag('q1',1100);assert(state.notStudiedHeld.q1);
  at(2000);startSession(['q3','q4'],'practice','Upper limb');assert.notStrictEqual(S().id,'r1');
  assert(!state.notStudiedHeld.q1,'abandoned session: nothing kept aside');assert(state.attempts.q1.some(a=>a.isUndo&&a.reason==='not-studied'),'abandoned session settled');
  reset();state.notStudiedHeld={q5:{session:'gone',review:null,sig:'[]'}};practice('s2',['q1'],0);ans('q1',2,1000);next('q1',1100);finish(2000);
  assert(!state.notStudiedHeld.q5,'an entry whose session can no longer run is dropped');
  reset();practice('s3',['q1','q2'],0);ans('q1',2,1000);flag('q1',1100);pause(1500);practice('s4',['q3'],1600);ans('q3',1,1700);next('q3',1800);finish(2000);
  assert(state.notStudiedHeld.q1,'a paused session keeps its entry');
});
scenario('fix 8: choosing an option in a timed test leaves an earlier flag until submit',()=>{
  const r=run(()=>{practice('s0',['q1'],0);flag('q1',100);state.activeSession=null;exam('e1',['q1','q2'],86400000);pick('q1',2,86400000+100);
    assert.strictEqual(nkNsIsFlagged('q1'),true,'answers are provisional: the flag is still there');pick('q1',1,86400000+200);submit(86400000+1000);});
  assert.strictEqual(r.notStudied.q1.on,false,'cleared at submit');assert.strictEqual(nkFsrsActiveAttempts('q1').length,1);same(r.m.tests.at(-1).questionIds,['q1','q2']);
});
scenario('fix 9: a refused Practice submit puts back the undo events, the kept-aside card and the flag',()=>{
  reset();practice('s0',['q1'],0);ans('q1',2,1000);flag('q1',1100);state.activeSession=null;
  practice('s2',['q1','q2'],86400000);go('q1');S().answers.q1=1;
  const before=JSON.stringify({attempts:state.attempts.q1,held:state.notStudiedHeld.q1,flag:state.notStudied.q1});
  const byId=BY_ID,all=nkAllBankQuestions;BY_ID={};nkAllBankQuestions=()=>[];at(86400000+1000);
  try{submitPractice();}finally{BY_ID=byId;nkAllBankQuestions=all;}
  assert(!S().submitted.q1,'the submit was refused');same(JSON.parse(before),{attempts:state.attempts.q1,held:state.notStudiedHeld.q1,flag:state.notStudied.q1},'everything is back as it was');
  ans('q1',1,86400000+2000);assert.strictEqual(state.notStudied.q1.on,false,'a real submit then clears it');assert.strictEqual(state.attempts.q1.filter(a=>a.isUndo).length,1,'the earlier answer is withdrawn once');
});
scenario('fix 10: unflag rebuilds a card whose cache was missing instead of deleting it',()=>{
  const base=run(()=>{practice('s1',['q1','q2'],0);ans('q1',2,1000);});
  reset();practice('s1',['q1','q2'],0);ans('q1',2,1000);delete state.reviews.q1;flag('q1',1100);assert.strictEqual(state.notStudiedHeld.q1.review,null);
  flag('q1',1200);assert(state.reviews.q1,'the card is rebuilt from the answers');
  const strip=r=>{const x=JSON.parse(JSON.stringify(r));delete x.migratedAt;return sortObj(x);};same(strip(state.reviews.q1),strip(base.m.reviews.q1),'the same card the answers build');
});
console.log('NOT_STUDIED_SCENARIOS_OK '+results.length);
results.forEach(name=>console.log('  ok · '+name));
'''

SYNC_PRELUDE = r'''
const assert=require('assert');
const storage={};
const localStorage={getItem:k=>Object.prototype.hasOwnProperty.call(storage,k)?storage[k]:null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]};
const window={NK_QBANK_FIREBASE_CONFIG:{}};const navigator={onLine:true};const location={hostname:'qbank.local'};
const document={querySelector:()=>null,getElementById:()=>null};
globalThis.setTimeout=()=>0;globalThis.clearTimeout=()=>{};
const LS_KEY='qbank_state_v1';let state={};let activeSubject='Anatomy';const SUBJECT_BY_NAME={Anatomy:{}};
function render(){} function showToast(){} function saveState(){return true} function fmtDate(v){return String(v)}
function esc(v){return String(v)} function defaultState(){return {attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,questionNotes:{},fsrsReviewEligible:{}}}
function applySubject(v){activeSubject=v} function nkNormalizeState(v){return v} function nkDurablePersist(){return true}
let BY_ID={q9:{id:'q9',correctOption:1}},CHAPTERS=[],CHAPTER_BY_ID={};
// Device B's FSRS view: replay counts the attempts nkFsrsActiveAttempts returns.
let replays=[];
let nkFsrsActiveAttempts=qid=>{const list=state.attempts?.[qid]||[],undone=new Set(list.filter(a=>a.isUndo).map(a=>a.undoOf));return list.filter(a=>!a.isUndo&&!undone.has(a.id));};
let nkFsrsReplay=qid=>{replays.push(qid);const n=nkFsrsActiveAttempts(qid).length;if(n)state.reviews[qid]={n};else delete state.reviews[qid];};
function nkFsrsSessionRating(){return null;}
let nkFsrsRatingMarkup=()=>'',nkRateCurrent=()=>false;
let nkFsrsRecordAttempt=()=>true,recordAttempt=nkFsrsRecordAttempt,submitPractice=()=>{},selectExam=()=>{},nkMarkSkippedFromSession=()=>{},finishPracticeSession=()=>{},buildReviewSession=t=>t,navigate=()=>{},nkSessionHeader=()=>'',openSessionReview=()=>{},openQuestionNavigator=()=>{},topics=()=>'',chapterPage=()=>'';
'''

SYNC_CASES = r'''
nkAuth={uid:'owner'};nkSyncMeta.needsInitialPull=false;nkSyncMeta.outbox={};nkSyncMeta.localHashes={};
assert(NK_SYNC_KINDS.includes('notStudied'),'flags are a synced kind, so account reset tombstones them too');
assert(!NK_SYNC_KINDS.some(kind=>/held/i.test(kind)),'what an unflag would restore stays on this device');
state={...defaultState(),notStudied:{},notStudiedHeld:{'anatomy-1-1':{session:'s1',review:{x:1},sig:'[]',pending:null}}};
nkNsSet('anatomy-1-1',true,'s1');nkCaptureCloudChanges();
const env=nkSyncMeta.outbox['notStudied/anatomy-1-1'];
assert(env&&env.kind==='notStudied'&&!env.deleted,'a flag queues one envelope per question');
const sent=JSON.parse(env.payload);assert.strictEqual(sent.on,true);assert.strictEqual(sent.session,'s1','the session that withholds answers travels with the flag');
assert(!('held' in sent)&&!('review' in sent)&&!Object.keys(nkSyncMeta.outbox).some(k=>/held/i.test(k)),'nothing put aside is uploaded');
nkSyncMeta.outbox={};nkCaptureCloudChanges();assert(!nkSyncMeta.outbox['notStudied/anatomy-1-1'],'unchanged flags do not upload again');
nkNsSet('anatomy-1-1',false);nkCaptureCloudChanges();
assert.strictEqual(nkSyncMeta.outbox['notStudied/anatomy-1-1'].payload,JSON.stringify({on:false,updatedAt:state.notStudied['anatomy-1-1'].updatedAt}),'clearing uploads a plain tombstone');
// Merge: newest edit wins regardless of arrival order; ties resolve to cleared; junk is refused.
state={...defaultState(),notStudied:{}};
assert(nkNsMergeEntry('qa',{on:true,at:10,updatedAt:10}));
assert(!nkNsMergeEntry('qa',{on:false,updatedAt:5}),'an older clear does not win');
assert(nkNsMergeEntry('qa',{on:false,updatedAt:10})&&state.notStudied.qa.on===false,'a tie resolves to cleared');
assert(!nkNsMergeEntry('qa',{on:true,at:9,updatedAt:10}),'and stays cleared');
assert(!nkNsMergeEntry('qb',{on:true})&&!nkNsMergeEntry('qb','x')&&!state.notStudied.qb,'entries without a time are refused');
nkNsMergeEntry('qc',{on:true,at:1,updatedAt:1,session:"x'><script>"});assert(!('session' in state.notStudied.qc),'an unsafe session id is dropped');
// Device B: a flag made in session s1 on device A hides s1's answers here too, and the unflag shows them again.
state={...defaultState(),notStudied:{q9:{on:true,at:100,updatedAt:100}},attempts:{q9:[{id:'a0',sessionId:'s0',correct:false,at:50},{id:'a1',sessionId:'s1',correct:false,at:150}]},reviews:{q9:{n:2}}};
const doc=(device,payload,at)=>({kind:'notStudied',entityId:'q9',ownerDevice:device,updatedAt:at,deleted:false,payload:JSON.stringify(payload),schemaVersion:1});
replays=[];nkApplyCloudEnvelope(doc('web',{on:true,at:160,updatedAt:160,session:'s1'},160));
assert.strictEqual(state.notStudied.q9.session,'s1');assert.deepStrictEqual(nkFsrsActiveAttempts('q9').map(a=>a.id),['a0'],'device B hides the s1 answer');assert.deepStrictEqual(state.reviews.q9,{n:1},'and its card is replayed without it');
nkApplyCloudEnvelope(doc('web',{on:false,updatedAt:170},170));assert.deepStrictEqual(nkFsrsActiveAttempts('q9').map(a=>a.id),['a0','a1'],'an unflag on device A gives the answer back on device B');assert.deepStrictEqual(state.reviews.q9,{n:2});
nkApplyCloudEnvelope(doc('phone',{on:true,at:160,updatedAt:160,session:'s1'},160));assert.strictEqual(state.notStudied.q9.on,false,'an older device copy does not bring the flag back');
nkApplyCloudEnvelope(doc('web',{on:true,at:200,updatedAt:200,session:'s1'},200));assert.strictEqual(state.notStudied.q9.on,true,'a newer flag arrives');
nkApplyCloudEnvelope({kind:'notStudied',entityId:"q9');x('",ownerDevice:'web',updatedAt:300,deleted:false,payload:JSON.stringify({on:true,at:300,updatedAt:300}),schemaVersion:1});
assert(!state.notStudied["q9');x('"],'unsafe ids are refused');
nkApplyCloudEnvelope({kind:'notStudied',entityId:'q9',ownerDevice:'web',updatedAt:999,deleted:true,payload:'',schemaVersion:1});
assert.strictEqual(state.notStudied.q9.on,true,'an account-reset tombstone document is not read as data');
// Many toggles on two devices converge on the newest edit, with no extra documents.
for(let i=0;i<20;i++)nkApplyCloudEnvelope(doc(i%2?'web':'phone',i%2?{on:true,at:400+i,updatedAt:400+i,session:'s1'}:{on:false,updatedAt:400+i},400+i));
assert.strictEqual(state.notStudied.q9.on,true,'the newest of many toggles wins');
nkSyncMeta.outbox={};nkCaptureCloudChanges();nkSyncMeta.outbox={};nkCaptureCloudChanges();
assert(!nkSyncMeta.outbox['notStudied/q9'],'merged state settles without repeated uploads');
// Fix 11: a cleared flag that has synced leaves state.notStudied (and the capture walk); its time still wins the merge.
nkSyncMeta.outbox={};nkSyncMeta.localHashes={};state={...defaultState(),notStudied:{}};
nkNsSet('qp',true,'s1');nkCaptureCloudChanges();nkNsSet('qp',false);nkCaptureCloudChanges();
assert(state.notStudied.qp&&nkSyncMeta.outbox['notStudied/qp'],'a tombstone still waiting to upload stays');
const clearedAt=state.notStudied.qp.updatedAt;nkCaptureCloudChanges();assert('qp' in state.notStudied,'still waiting: kept');
nkSyncMeta.outbox={};nkCaptureCloudChanges();
assert(!('qp' in state.notStudied),'once synced it leaves the walk');assert.strictEqual(state.notStudiedCleared.qp,clearedAt);assert(!nkSyncMeta.outbox['notStudied/qp'],'and is not uploaded again');
assert(!nkNsMergeEntry('qp',{on:true,at:clearedAt-1,updatedAt:clearedAt-1,session:'s9'})&&!nkNsIsFlagged('qp'),'an older remote flag is still refused');
assert(!nkNsMergeEntry('qp',{on:true,at:clearedAt,updatedAt:clearedAt})&&!nkNsIsFlagged('qp'),'a tie still resolves to cleared');
nkNsSet('qp',true,'s2');assert(state.notStudied.qp.updatedAt>clearedAt&&!('qp' in state.notStudiedCleared),'a new flag is stamped after the cleared one');
nkNsSet('qp',false);nkCaptureCloudChanges();nkSyncMeta.outbox={};nkCaptureCloudChanges();const again=state.notStudiedCleared.qp;
assert(nkNsMergeEntry('qp',{on:true,at:again+5,updatedAt:again+5,session:'s3'})&&nkNsIsFlagged('qp')&&!('qp' in state.notStudiedCleared),'a newer remote flag is accepted');
// Fix 1: the hidden shell of an all-flagged result is newer than any copy saved before it, so a stale copy never comes back.
state={...defaultState()};nkSyncMeta.outbox={};nkSyncMeta.winners={};nkSyncMeta.localHashes={};
const staleTest={id:'exam_e1',questionIds:['q9'],answers:{q9:1},correct:1,incorrect:0,attempted:1,unattempted:0,total:1,createdAt:1000};
const shellTest={id:'exam_e1',noResult:true,questionIds:[],answers:{},questionTimes:{},notStudiedIds:['q9'],allQuestionIds:['q9'],correct:0,incorrect:0,attempted:0,unattempted:0,total:0,totalTimeMs:0,createdAt:1000,updatedAt:1001};
const tdoc=(payload,at,device)=>({kind:'tests',entityId:'exam_e1',ownerDevice:device,updatedAt:at,deleted:false,payload:JSON.stringify(payload),schemaVersion:1});
nkApplyCloudEnvelope(tdoc(staleTest,1000,'phone'));assert.strictEqual(state.tests[0].total,1);
nkApplyCloudEnvelope(tdoc(shellTest,1001,'web'));assert(state.tests[0].noResult&&state.tests.length===1,'the shell replaces a stale copy a device already had');
nkApplyCloudEnvelope(tdoc(staleTest,1000,'phone'));assert(state.tests[0].noResult,'the stale copy never comes back');
nkSyncMeta.outbox={};nkSyncMeta.localHashes={};nkCaptureCloudChanges();assert(JSON.parse(nkSyncMeta.outbox['tests/exam_e1'].payload).noResult,'what uploads is the shell');
console.log('NOT_STUDIED_SYNC_OK');
'''


def run(script: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "not-studied-test.js"
        path.write_text(script, encoding="utf-8")
        result = subprocess.run(["node", str(path)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
        return result.stdout.strip()


def page_functions() -> str:
    html = HTML.read_text(encoding="utf-8")
    names = ["nkMarkSkippedFromSession", "submitPractice", "selectExam", "submitExam", "finishPracticeSession", "buildReviewSession"]
    return "\n".join("let " + name + "=" + extract_function(html, name).strip() + ";" for name in names)


def result_strip() -> str:
    return "let nkResultStrip=" + extract_function(ANALYSIS.read_text(encoding="utf-8"), "nkResultStrip").strip() + ";"


def test_install_contract() -> None:
    page = app_page()
    module = MODULE.read_text(encoding="utf-8")
    assert page.count("NK_NOT_STUDIED_V1_START") == 1, "module must be assembled once"
    start = page.index("NK_NOT_STUDIED_V1_START")
    for owner in ("NK_FSRS_V6_START", "NK_CONTINUE_PRACTICE_RESUME_V1_START", "NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START", "NK_EXAM_REVIEW_FLAGS_V1_START", "NK_TIMED_ABANDON_GRID_V1_START", "NK_QUESTION_HIGHLIGHTS_V1_START"):
        assert page.index(owner) < start, f"flags must wrap after {owner}"
    assert page.index("function nkResultStrip") < start, "result strip is wrapped after refined analysis defines it"
    assert start < page.index("window.QB={nkToggleNotStudied,nkPracticeNotStudied,"), "actions are exported"
    for hook in ("nkFsrsActiveAttempts=function", "nkFsrsRecordAttempt=function", "recordAttempt=nkFsrsRecordAttempt", "finishPracticeSession=function", "buildReviewSession=function", "nkResultStrip=function"):
        assert hook in module, hook
    sync = SYNC.read_text(encoding="utf-8")
    assert "NK_SYNC_KINDS.push('notStudied')" in sync and "nkEnvelope('notStudied'" in sync and "nkNsMergeEntry(id,payload)" in sync
    assert "nkNsPruneSynced(nkSyncMeta)" in sync and sync.index("nkNsPruneSynced(nkSyncMeta)") < sync.index("nkEnvelope('notStudied'"), "synced tombstones are pruned before the walk"
    html = HTML.read_text(encoding="utf-8")
    assert "t.kind!=='practice'&&!t.noResult" in html, "the Tests list skips a hidden shell"
    assert "!t.isDeleted&&!t.noResult" in (ROOT / "app/src/main/modules/learning_insights.js").read_text(encoding="utf-8"), "Insights skip a hidden shell"
    sched = (ROOT / "app/src/main/modules/scheduled_mocks.js").read_text(encoding="utf-8")
    assert "status==='taken'&&test&&!test.noResult" in sched and "makeup&&!makeup.noResult" in sched, "a mock ticket never links to a shell"
    assert "selectExam=function" not in module, "choosing a timed-test option never clears a flag"
    css = app_css()
    assert css.count("/* ── nk-not-studied-v1") == 1
    assert css.index("/* ── nk-not-studied-v1") < css.index("/* ── nk-visual-refinement-v1"), "flag CSS sits before the visual refinement layer"
    for selector in (".nk-ns-toggle.is-on", ".nk-ns-corner", ".nk-ns-badge", ".nk-topic-legend li.is-ns", ".nk-rs-strip > button.is-ns", ":is(.nk-session-review-q, .qb-nav-q).is-ns", ".nk-status.is-ns"):
        assert selector in css, selector
    print("NOT_STUDIED_INSTALL_OK")


def main() -> None:
    module = MODULE.read_text(encoding="utf-8")
    prelude = PRELUDE % {"vendor": repr(str(VENDOR))}
    script = (prelude + page_functions() + "\n" + result_strip() + "\n" + RESUME.read_text(encoding="utf-8") + "\n"
              + FSRS.read_text(encoding="utf-8") + "\n" + module + SCENARIOS)
    print(run(script))
    print(run(SYNC_PRELUDE + SYNC.read_text(encoding="utf-8") + "\n" + module + SYNC_CASES))
    test_install_contract()


if __name__ == "__main__":
    main()
