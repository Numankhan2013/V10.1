#!/usr/bin/env python3
"""Behavior tests for the "not studied yet" flag (not_studied_flags.js).

The session logic runs in Node against the real FSRS scheduler module and the
page's own submitPractice / selectExam / submitExam / finishPracticeSession /
nkMarkSkippedFromSession declarations, with the flag module installed over them
the way the page assembles it. The sync checks load cross_device_sync.js beside
the module. Topic and header markup are checked on the strings the page renders.
"""

from pathlib import Path
import subprocess
import tempfile

from app_page import app_page, app_css
from js_extract import extract_function

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/not_studied_flags.js"
FSRS = ROOT / "app/src/main/modules/fsrs_scheduler.js"
SYNC = ROOT / "app/src/main/modules/cross_device_sync.js"
HTML = ROOT / "app/src/main/assets/index.html"
VENDOR = ROOT / "app/src/main/assets/vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js"

PRELUDE = r'''
const assert=require('assert');global.window=globalThis;window.FSRS=require(%(vendor)s);
const store=new Map();global.localStorage={getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)};
const LS_KEY='qbank_state_v1';
const questions=['q1','q2','q3','q4','q5','q6','q7','q8'].map((id,i)=>({id,subject:'Anatomy',bank:'PrepLadder',chapterId:i<6?'c1':'c2',chapter:'Topic',question:'Stem '+id,correctOption:1,options:[{letter:'A',text:'a'},{letter:'B',text:'b'}]}));
const SUBJECTS=[{subject:'Anatomy',topics:[{id:'c1',title:'Upper limb'},{id:'c2',title:'Thorax'}],questions}];
const CHAPTERS=[{id:'c1',title:'Upper limb'},{id:'c2',title:'Thorax'}],CHAPTER_BY_ID={c1:CHAPTERS[0],c2:CHAPTERS[1]};
function nkAllBankQuestions(){return questions;}
function chapterQuestions(cid){return questions.filter(q=>q.chapterId===String(cid));}
function nkFindStudyQuestion(id){return questions.find(q=>q.id===String(id))||null;}
let state={attempts:{},reviews:{},tests:[],fsrsPreferences:null,fsrsReviewEligible:{},activeSession:null,bookmarks:{}};
let route={page:'practice'},routes=[],toasts=[],renders=0,started=null;
let BY_ID=Object.fromEntries(questions.map(q=>[q.id,q])),dashboard=()=>'<main></main>',morePage=()=>'<main></main>',practicePage=()=>'<main></main>',practiceActionBar=()=>'<div class="fixed-actions nk-session-footer"><div class="fixed-actions-inner"></div></div>',nextQ=()=>{},prevQ=()=>{},goIndex=()=>{},retryCurrent=()=>{},endSession=()=>{},navigate=(page,id)=>{routes.push([page,id]);},recordAttempt=()=>{},qAttempts=()=>[],nkRebuildReviews=()=>{};
function nkQuestionPresentationFor(){return {valid:true};}
const saveState=()=>{localStorage.setItem(LS_KEY,JSON.stringify(state));return true;},render=()=>{renders++;},showToast=m=>toasts.push(m),savePracticeElapsed=()=>{},saveExamElapsed=()=>{},haptic=()=>{},closeQuestionNavigator=()=>{},esc=x=>String(x).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[c]),shell=x=>x,fmtNum=n=>String(n),navIcon=n=>'<svg data-icon="'+n+'"></svg>';
function startSession(ids,mode,title){started={ids,mode,title};return true;}
function nkCompleteStudyModule(){}
function nkExamSecondsPer(){return 60;} function nkExamTotalSeconds(s){return s.questionIds.length*60;}
window.QB={};global.document={getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[],body:{insertAdjacentHTML:()=>{}}};window.addEventListener=()=>{};
let nkSessionHeader=(q,s,mode)=>'<header><div class="q-actions"><button class="icon-btn bookmark-toggle"></button></div></header>';
let openSessionReview=()=>{},openQuestionNavigator=()=>{};
let topics=()=>'<div class="nk-topic-list">'+CHAPTERS.map(c=>`<button class="nk-topic-row is-notstarted" onclick="window.QB.openChapter('${c.id}')"><span class="nk-topic-index">1</span><span class="nk-topic-copy"><strong>${c.title}</strong><small>6 questions</small></span></button>`).join('')+'</div>';
let chapterPage=cid=>`<section class="nk-chapter-hero"><div class="nk-chapter-title"><div class="nk-topic-library"><div class="nk-topic-map">${chapterQuestions(cid).map((q,i)=>`<button class="nk-library-row nk-topic-cell is-u" data-s="u" aria-label="Question ${i+1}, not attempted" onclick="window.QB.practiceOne('${q.id}')">${i+1}</button>`).join('')}</div></div></div><div class="nk-chapter-actions"><div class="nk-topic-options"><button class="nk-topic-option">Timed test</button></div></div></section>`;
'''

SESSION_CASES = r'''
nkFsrsInit();
const T0=Date.now();const wait=ms=>{const end=Date.now()+ms;while(Date.now()<end);};const fresh=()=>{wait(3);const at=Date.now();wait(3);return at;};
const practice=(ids,startedAt)=>({id:'s_'+startedAt,mode:'practice',title:'Upper limb',questionIds:ids,index:0,answers:{},submitted:{},startedAt,lastTick:startedAt,elapsedMs:0,questionEnteredAt:startedAt,questionTimes:{},context:'normal'});
const answer=(i,choice)=>{const s=state.activeSession;s.index=i;const id=s.questionIds[i];s.questionTimes[id]=20000;s.answers[id]=choice;submitPractice();};
const flag=i=>{const s=state.activeSession;s.index=i;return nkToggleNotStudied(s.questionIds[i],s.id);};
const active=id=>nkFsrsActiveAttempts(id);

// ── Session 1 (Practice) ──
state.activeSession=practice(['q1','q2','q3','q4','q5'],T0-60000);
answer(0,2); // q1 wrong: recorded at once, as today
assert.equal(active('q1').length,1,'an unflagged miss is recorded');
assert(flag(1),'flag an unanswered question');
assert.equal(state.notStudied.q2.on,true,'flag is stored per question');
assert(Number(state.notStudied.q2.at)>=state.activeSession.startedAt,'flag time is recorded');
// Toggling a question that is not the current one is refused.
assert.equal(nkToggleNotStudied('q5',state.activeSession.id),false,'only the current question can be flagged');
assert.equal(nkToggleNotStudied('q2','other-session'),false,'a stale session cannot flag');
answer(2,2); // q3 wrong, then flagged: the attempt is withdrawn and FSRS replayed without it
assert.equal(active('q3').length,1);
assert(state.reviews.q3,'miss created a card');
flag(2);
assert.equal(active('q3').length,0,'flagging an answered question withdraws this session\'s attempt');
assert(!state.reviews.q3,'its FSRS card is gone');
assert(state.attempts.q3.some(a=>a.isUndo&&a.reason==='not-studied'),'withdrawal is an undo event that syncs like any attempt');
flag(2); // unflag in the same session gives the answer back
assert.equal(active('q3').length,1,'unflagging restores the withheld miss');
assert(state.reviews.q3,'and its card');
flag(2); // flagged again: stays out
assert.equal(active('q3').length,0,'re-flagging withdraws it again');
flag(3); answer(3,1); // q4 flagged during this session, then answered correctly
assert(!state.activeSession.pendingRating?.q4,'no recall rating is pending for a flagged answer');
assert.equal(active('q4').length,0,'a flagged answer is never recorded');
assert.equal(state.notStudied.q4.on,true,'a flag made in this session stays when the question is answered');
assert(nkFsrsCommitPending('q4',3)===false&&active('q4').length===0,'nothing to commit');
// Session review grid: skip marking leaves flagged questions out of FSRS.
state.activeSession.index=4;state.activeSession.questionTimes.q5=0;state.activeSession.questionTimes.q2=30000;
nkMarkSkippedFromSession(state.activeSession);
assert(!state.fsrsReviewEligible.q2,'a flagged unanswered question is not submitted-as-skipped');
finishPracticeSession();
const r1=state.tests.at(-1);
assert.deepEqual(r1.questionIds,['q1','q5'],'flagged questions leave the saved result');
assert.deepEqual(r1.notStudiedIds.sort(),['q2','q3','q4'],'the result notes what it left out');
assert(r1.total===2&&r1.attempted===1&&r1.correct===0&&r1.incorrect===1&&r1.unattempted===1,'counts are recomputed without them');
assert(!('q4' in r1.answers)&&!('q3' in r1.questionTimes),'answers and timings of flagged questions are dropped');
assert.equal(r1.totalTimeMs,20000,'practice time excludes flagged questions');
const snapshot=JSON.stringify(r1);
navigate('result',r1.id);assert.equal(JSON.stringify(state.tests.at(-1)),snapshot,'a result is cleaned once, never again');
// Old results are never rewritten when a flag is added later.
state.tests.push({id:'old',kind:'practice',questionIds:['q1','q2'],answers:{q2:1},questionTimes:{},correct:1,incorrect:0,attempted:1,total:2,unattempted:1,createdAt:T0-86400000});
navigate('result','old');assert.deepEqual(state.tests.at(-1).questionIds,['q1','q2'],'older results stay as they were saved');
state.tests.pop();

// ── Session 2 (later Practice): flags from before the session clear when answered ──
state.activeSession=practice(['q2','q3','q4','q6'],fresh());
answer(0,1); // q2 correct
assert.equal(state.notStudied.q2.on,false,'answering clears an earlier flag (tombstone)');
assert(state.activeSession.pendingRating.q2,'the answer waits for its recall rating like any correct answer');
nkFsrsCommitPending('q2',3);
assert.equal(active('q2').length,1,'and then enters FSRS');
answer(2,2); // q4 wrong, earlier flag clears, recorded
assert.equal(state.notStudied.q4.on,false);assert.equal(active('q4').length,1,'a cleared question records its miss');
flag(2); // re-flagged in this practice: stays flagged and out
assert.equal(state.notStudied.q4.on,true);assert.equal(active('q4').length,0,'re-flagged in the same practice stays out');
// q3 still flagged, left unanswered: excluded, and the topic still shows it.
assert.deepEqual(nkNsTopicIds('c1').sort(),['q3','q4']);
finishPracticeSession();
assert.deepEqual(state.tests.at(-1).questionIds,['q2','q6'],'second result keeps only counted questions');

// ── Timed test ──
const exam=(ids,startedAt)=>({id:'e_'+startedAt,mode:'exam',title:'CBT',questionIds:ids,index:0,answers:{},submitted:{},startedAt,questionTimes:{},timerMode:'global'});
state.notStudied.q7={on:true,at:Date.now()-1000,updatedAt:Date.now()-1000}; // flagged before the test
state.activeSession=exam(['q7','q8','q1','q5'],fresh());
selectExam(1);
assert.equal(state.notStudied.q7.on,false,'choosing an answer clears an earlier flag');
state.activeSession.index=1;flag(1);selectExam(1); // q8 flagged during the test, then answered
assert.equal(state.notStudied.q8.on,true,'a flag made during the test stays when answered');
state.activeSession.index=2;state.activeSession.answers.q1=1;
const q5Before=JSON.stringify(state.reviews.q5||null);
submitExam(false);
const r3=state.tests.at(-1);
assert.equal(active('q8').length,0,'a flagged test answer never enters FSRS');
assert.equal(active('q7').length,1,'an answer that cleared an earlier flag is recorded');
assert.deepEqual(r3.questionIds,['q7','q1','q5'],'the test result leaves the flagged question out');
assert(r3.total===3&&r3.correct===2&&r3.attempted===2&&r3.unattempted===1,'test counts are recomputed');
assert(!state.fsrsReviewEligible.q8,'no skip card for a flagged test question');

// All questions flagged: no result is saved.
const savedCount=state.tests.length;state.activeSession=exam(['q6'],fresh());flag(0);submitExam(false);
assert.equal(state.tests.length,savedCount,'a test whose every question is flagged saves no result');
assert.equal(routes.at(-1)[0],'tests','returns to where the test came from');
assert(toasts.at(-1).includes('no result was saved'));

// Merge rules: newest edit per question wins; tie resolves to cleared; junk is refused.
state.notStudied={};
assert(nkNsMergeEntry('qa',{on:true,at:10,updatedAt:10}));
assert(!nkNsMergeEntry('qa',{on:false,updatedAt:5}),'an older clear does not win');
assert(nkNsMergeEntry('qa',{on:false,updatedAt:10})&&state.notStudied.qa.on===false,'a tie resolves to cleared');
assert(!nkNsMergeEntry('qa',{on:true,at:9,updatedAt:10}),'and stays cleared');
assert(!nkNsMergeEntry('qb',{on:true})&&!nkNsMergeEntry('qb','x')&&!state.notStudied.qb,'entries without a time are refused');

// Topic list badge, topic grid cell flag and Practice flagged.
state.notStudied={q2:{on:true,at:1,updatedAt:1},q5:{on:true,at:1,updatedAt:1},q7:{on:false,updatedAt:2}};
const list=topics();
assert(/openChapter\('c1'\)[\s\S]*?<small>6 questions<span class="nk-ns-badge" aria-label="2 flagged not studied">[\s\S]*?2<\/span><\/small>/.test(list),'topic row shows a flag badge with its count');
assert(!/openChapter\('c2'\)[\s\S]*?nk-ns-badge/.test(list),'a topic without flags has no badge');
const page=chapterPage('c1');
assert.equal((page.match(/nk-topic-cell is-u is-ns/g)||[]).length,2,'flagged cells are marked');
assert(page.includes("aria-label=\"Question 2, not attempted, flagged not studied\" onclick=\"window.QB.practiceOne('q2')\">2<span class=\"nk-ns-corner\">"),'cell keeps its practice-one action and gains the flag');
assert(page.includes('<ul class="nk-topic-legend"><li class="is-ns"><b>2</b> not studied</li></ul>'),'legend counts flagged questions');
assert(page.includes("window.QB.nkPracticeNotStudied('c1')")&&page.includes('<span>Practice flagged</span><small>2</small>'),'Practice flagged (N) action');
assert(!chapterPage('c2').includes('nk-ns'),'no flag UI on a topic without flags');
nkPracticeNotStudied('c1');
assert.deepEqual(started.ids,['q2','q5']);assert.equal(started.mode,'practice');
assert(nkPracticeNotStudied('c2')===false,'nothing to practise');
// Header button: Practice and tests only.
const hs={id:'s9',mode:'practice'};
assert(nkSessionHeader({id:'q2'},hs,'practice').includes('nk-ns-toggle is-on" aria-pressed="true"'),'header flag shows its state');
assert(!nkSessionHeader({id:'q2'},{id:'r',mode:'review'},'review').includes('nk-ns-toggle'),'Review Solutions has no flag');
console.log('NOT_STUDIED_SESSION_OK');
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
let BY_ID={},CHAPTERS=[],CHAPTER_BY_ID={};
let nkFsrsRecordAttempt=()=>true,recordAttempt=nkFsrsRecordAttempt,submitPractice=()=>{},selectExam=()=>{},nkMarkSkippedFromSession=()=>{},navigate=()=>{},nkSessionHeader=()=>'',openSessionReview=()=>{},openQuestionNavigator=()=>{},topics=()=>'',chapterPage=()=>'';
'''

SYNC_CASES = r'''
nkAuth={uid:'owner'};nkSyncMeta.needsInitialPull=false;nkSyncMeta.outbox={};nkSyncMeta.localHashes={};
assert(NK_SYNC_KINDS.includes('notStudied'),'flags are a synced kind, so account reset tombstones them too');
state={...defaultState(),notStudied:{}};
nkNsSet('anatomy-1-1',true);nkCaptureCloudChanges();
const env=nkSyncMeta.outbox['notStudied/anatomy-1-1'];
assert(env&&env.kind==='notStudied'&&!env.deleted,'a flag queues one envelope per question');
assert.equal(JSON.parse(env.payload).on,true);
nkSyncMeta.outbox={};nkCaptureCloudChanges();assert(!nkSyncMeta.outbox['notStudied/anatomy-1-1'],'unchanged flags do not upload again');
nkNsSet('anatomy-1-1',false);nkCaptureCloudChanges();
assert.equal(JSON.parse(nkSyncMeta.outbox['notStudied/anatomy-1-1'].payload).on,false,'clearing uploads a tombstone');
// Two devices converge: newest edit wins regardless of arrival order.
state={...defaultState(),notStudied:{q9:{on:true,at:100,updatedAt:100}}};
const doc=(device,payload,at)=>({kind:'notStudied',entityId:'q9',ownerDevice:device,updatedAt:at,deleted:false,payload:JSON.stringify(payload),schemaVersion:1});
nkApplyCloudEnvelope(doc('web',{on:false,updatedAt:150},150));assert.equal(state.notStudied.q9.on,false,'a clear made on another device arrives');
nkApplyCloudEnvelope(doc('phone',{on:true,at:100,updatedAt:100},100));assert.equal(state.notStudied.q9.on,false,'an older device copy does not bring it back');
nkApplyCloudEnvelope(doc('web',{on:true,at:200,updatedAt:200},200));assert.equal(state.notStudied.q9.on,true,'a newer flag arrives');
nkApplyCloudEnvelope({kind:'notStudied',entityId:"q9');x('",ownerDevice:'web',updatedAt:300,deleted:false,payload:JSON.stringify({on:true,at:300,updatedAt:300}),schemaVersion:1});
assert(!state.notStudied["q9');x('"],'unsafe ids are refused');
nkApplyCloudEnvelope({kind:'notStudied',entityId:'q9',ownerDevice:'web',updatedAt:999,deleted:true,payload:'',schemaVersion:1});
assert.equal(state.notStudied.q9.on,true,'an account-reset tombstone document is not read as data');
nkSyncMeta.outbox={};nkCaptureCloudChanges();nkSyncMeta.outbox={};nkCaptureCloudChanges();
assert(!nkSyncMeta.outbox['notStudied/q9'],'merged state settles without repeated uploads');
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
    names = ["nkMarkSkippedFromSession", "submitPractice", "selectExam", "submitExam", "finishPracticeSession"]
    return "\n".join("let " + name + "=" + extract_function(html, name).strip() + ";" for name in names)


def test_install_contract() -> None:
    page = app_page()
    module = MODULE.read_text(encoding="utf-8")
    assert page.count("NK_NOT_STUDIED_V1_START") == 1, "module must be assembled once"
    start = page.index("NK_NOT_STUDIED_V1_START")
    for owner in ("NK_FSRS_V6_START", "NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START", "NK_EXAM_REVIEW_FLAGS_V1_START", "NK_TIMED_ABANDON_GRID_V1_START", "NK_QUESTION_HIGHLIGHTS_V1_START"):
        assert page.index(owner) < start, f"flags must wrap after {owner}"
    assert start < page.index("window.QB={nkToggleNotStudied,nkPracticeNotStudied,"), "actions are exported"
    assert "nkFsrsRecordAttempt=function" in module and "recordAttempt=nkFsrsRecordAttempt" in module
    sync = SYNC.read_text(encoding="utf-8")
    assert "NK_SYNC_KINDS.push('notStudied')" in sync and "nkEnvelope('notStudied'" in sync and "nkNsMergeEntry(id,payload)" in sync
    css = app_css()
    assert css.count("/* ── nk-not-studied-v1") == 1
    for selector in (".nk-ns-toggle.is-on", ".nk-ns-corner", ".nk-ns-badge", ".nk-topic-legend li.is-ns"):
        assert selector in css, selector
    print("NOT_STUDIED_INSTALL_OK")


def main() -> None:
    module = MODULE.read_text(encoding="utf-8")
    prelude = PRELUDE % {"vendor": repr(str(VENDOR))}
    print(run(prelude + page_functions() + "\n" + FSRS.read_text(encoding="utf-8") + "\n" + module + SESSION_CASES))
    print(run(SYNC_PRELUDE + SYNC.read_text(encoding="utf-8") + "\n" + module + SYNC_CASES))
    test_install_contract()


if __name__ == "__main__":
    main()
