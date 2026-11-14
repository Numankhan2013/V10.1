#!/usr/bin/env python3
"""Behavior tests for Abandon session (session_abandon.js).

Runs in Node against the real FSRS scheduler, the real Continue Practice module
(pause / resume / checkpoints), the real not-studied flag module and the page's
own submitPractice / selectExam / submitExam / finishPracticeSession /
nkMarkSkippedFromSession / nkLatestPracticeContext declarations, with the
abandon module installed over them in the page's order. The clock and
Math.random are driven by the test (the not-studied harness), so a run where a
session was abandoned is compared with a run where that session never
happened: FSRS cards, active attempts, rating revisions, skip marks, due queue,
counts, per-question stats (mistakes, accuracy, study days), saved results and
Continue Practice.

Every rule in docs/SESSION_ABANDON.md has a case here.
"""

from pathlib import Path
import re

from app_page import app_page, app_css
from js_extract import extract_function
import test_not_studied_flags_v1 as ns

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/session_abandon.js"
HTML = ROOT / "app/src/main/assets/index.html"
SYNC = ROOT / "app/src/main/modules/cross_device_sync.js"
JAVA = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"
FEEL = ROOT / "app/src/main/assets/redesign/nk-feel.js"
INSIGHTS = ROOT / "app/src/main/modules/learning_insights.js"
STUDY = ROOT / "app/src/main/modules/study_modules.js"

EXTRA = r'''
const fmtDate=v=>'D'+v;let testRow=t=>'<button class="nk-test-row">'+t.id+'</button>';
// Study modules: the real start / mirror functions (saveState mirrors the session into its module).
let studyModuleDraft=null;
%(study)s
'''

SCENARIOS = r'''
nkFsrsInit();
nkLatestPracticeContext=%(latest)s;
const IDS=['q1','q2','q3','q4','q5','q6','q7','q8'];
function reset(){state={attempts:{},reviews:{},tests:[],fsrsPreferences:null,fsrsReviewEligible:{},activeSession:null,bookmarks:{},fsrsMigratedAt:1,studyModules:[]};routes=[];toasts=[];at(0);}
const practice=(id,ids,t,extra={})=>{at(t);state.activeSession={id,mode:'practice',title:'Upper limb',questionIds:[...ids],sessionQuestionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,lastTick:NOW,elapsedMs:0,questionEnteredAt:NOW,questionTimes:{},context:'normal',originRoute:'topics',lifecycle:'active',...extra};saveState();return state.activeSession;};
const exam=(id,ids,t,extra={})=>{at(t);state.activeSession={id,mode:'exam',title:'CBT',questionIds:[...ids],index:0,answers:{},submitted:{},startedAt:NOW,questionTimes:{},timerMode:'global',originRoute:'tests',...extra};return state.activeSession;};
const S=()=>state.activeSession,pos=qid=>S().questionIds.indexOf(qid),go=qid=>{S().index=pos(qid);};
function ans(qid,choice,t,ms=20000){at(t);go(qid);const s=S();s.questionTimes[qid]=ms;s.answers[qid]=choice;submitPractice();if(typeof nkSyncModuleFromSession==='function')nkSyncModuleFromSession();}
function look(qid,t,ms=30000){at(t);go(qid);S().questionTimes[qid]=ms;}
function rate(qid,r,t){at(t);go(qid);return nkRateCurrent(r,qid,S().id);}
function next(qid,t){at(t);go(qid);nextQ();}
function pick(qid,choice,t){at(t);go(qid);selectExam(choice);}
function finish(t){at(t);return finishPracticeSession();}
function submit(t){at(t);return submitExam(false);}
function pause(t){at(t);return nkPausePractice();}
function resume(id,t){at(t);return nkResumePracticeById(id);}
function reload(t){at(t);state=JSON.parse(JSON.stringify(state));state.activeSession=null;}
// Abandon the way the learner does: the sheet asks, the answer confirms (or cancels).
function abandon(t,confirmed=true){at(t);assert.strictEqual(nkAbandonSession(),true,'the confirmation opens');const id=nkAbPending.requestId;return nkAbandonAnswer(id,confirmed);}
const sortObj=o=>o&&typeof o==='object'&&!Array.isArray(o)?Object.fromEntries(Object.keys(o).sort().map(k=>[k,sortObj(o[k])])):Array.isArray(o)?o.map(sortObj):o;
const only=(map,ids)=>Object.fromEntries(ids.filter(id=>map&&map[id]!==undefined).map(id=>[id,map[id]]));
// What every measure sees: cards, active attempts (FSRS, mistakes, accuracy, Insights,
// coverage, streak, heatmap and Today all read nkFsrsActiveAttempts), skip marks, the due
// queue, counts, saved results, Continue Practice and the Home "continue" topic.
function effect(ids=IDS){
  const keep=NOW;at(40*86400000);
  const queue=nkFsrsQueue({}),counts=nkFsrsCounts();
  const statRows=ids.map(id=>{const h=nkFsrsActiveAttempts(id).filter(a=>typeof a.correct==='boolean');return [id,nkFsrsEligibility(nkFindStudyQuestion(id)),h.length,h.filter(a=>a.correct).length,nkFsrsPracticeMistake(id),h.map(a=>a.id),[...new Set(h.map(a=>new Date(Number(a.reviewedAt||a.at)).toDateString()))],h.reduce((n,a)=>n+Number(a.timeSpent||0),0)];});
  NOW=keep;
  const latest=nkLatestPracticeContext();
  return {reviews:sortObj(only(state.reviews,ids)),eligible:only(state.fsrsReviewEligible,ids),due:queue.due.map(q=>q.id),cards:queue.cards.map(q=>q.id),counts,stats:statRows,
    tests:state.tests,resumable:nkPracticeCheckpoints(false).map(cp=>cp.sessionId),latest:latest?latest.q.id:null,
    revisions:Object.fromEntries(Object.entries(state.fsrsRatingRevisions||{}).map(([k,v])=>[k,v.filter(r=>nkFsrsActiveAttempts(k).some(a=>a.ratingRevisionId===r.id))]).filter(([,v])=>v.length))};
}
const same=(a,b,msg)=>assert.strictEqual(JSON.stringify(a),JSON.stringify(b),msg);
const results=[];function scenario(name,fn){fn();results.push(name);}
function undoneBy(sessionId){
  const all=Object.values(state.attempts).flat(),undone=new Map(all.filter(a=>a.isUndo).map(a=>[String(a.undoOf),a]));
  const mine=all.filter(a=>!a.isUndo&&!a.isRatingRevision&&a.sessionId===sessionId);
  mine.forEach(a=>{assert(undone.has(String(a.id)),'attempt '+a.id+' has an undo event');assert.strictEqual(undone.get(String(a.id)).reason,'abandoned');});
  return mine.length;
}

scenario('Practice: wrong, correct rated Hard, correct waiting for its rating, revised rating, a skip → abandon = the session never happened',()=>{
  reset();practice('s0',['q1','q2'],0);ans('q1',1,1000);rate('q1',3,1100);ans('q2',2,2000);finish(3000);
  const base=effect();
  practice('s1',['q3','q4','q5','q6','q1'],10000);ans('q3',2,11000);ans('q4',1,12000);rate('q4',2,12100);rate('q4',4,12200);next('q4',12300);look('q5',13000);ans('q6',1,14000);ans('q1',2,15000);
  assert(state.reviews.q3&&state.reviews.q4&&nkFsrsActiveAttempts('q1').length===2,'answers counted the moment they were made');
  assert.strictEqual(abandon(16000),true);
  assert.strictEqual(state.activeSession,null);
  assert.strictEqual(undoneBy('s1'),3,'every recorded answer (q3, q4, q1) is withdrawn');
  assert(!(state.attempts.q6||[]).length,'the correct answer still waiting for its rating is dropped, never committed');
  same(effect(),base,'cards, mistakes, stats, due, skip marks, results and Continue Practice are as if the session never happened');
  assert.strictEqual(state.abandonedSessions.length,1);const e=state.abandonedSessions[0];
  assert.deepStrictEqual([e.sessionId,e.mode,e.kind,e.total,e.answered,e.title],['s1','practice','practice',5,4,'Upper limb']);
  assert.deepStrictEqual(routes.at(-1),['topics',undefined],'back to where the session started');
  assert(toasts.at(-1).includes('abandoned'));
});
scenario('Practice: an earlier card is byte-identical to before the session (and its due date)',()=>{
  reset();practice('s0',['q1'],0);ans('q1',2,1000);finish(2000);const before=JSON.stringify(state.reviews.q1),base=effect();
  practice('s1',['q1','q2'],5*86400000);ans('q1',1,5*86400000+1000);rate('q1',4,5*86400000+1100);next('q1',5*86400000+1200);ans('q2',2,5*86400000+2000);
  assert.notStrictEqual(JSON.stringify(state.reviews.q1),before);
  abandon(5*86400000+3000);
  assert.strictEqual(JSON.stringify(state.reviews.q1),before,'the card is the one from before the session');same(effect(),base);
});
scenario('Skipped and unanswered questions leave no skip mark; a session with no answers leaves nothing but the entry',()=>{
  reset();const base=effect();practice('s1',['q1','q2','q3'],0);look('q1',1000,40000);look('q2',2000,40000);abandon(3000);
  same(effect(),base);assert.deepStrictEqual(state.fsrsReviewEligible,{});assert.strictEqual(undoneBy('s1'),0);assert.strictEqual(state.abandonedSessions[0].answered,0);
});
scenario('Cancel keeps the session exactly as it was',()=>{
  reset();practice('s1',['q1','q2'],0);ans('q1',2,1000);const snap=JSON.stringify(state);
  assert.strictEqual(abandon(2000,false),false);assert.strictEqual(JSON.stringify(state),snap,'nothing changed');assert.strictEqual(S().id,'s1');
  assert.strictEqual(nkAbandonAnswer('stale',true),false,'an old or unknown confirmation does nothing');
});
scenario('Paused, resumed, then abandoned: not resumable, not on Home, not in Continue Practice',()=>{
  reset();const base=effect();practice('s1',['q1','q2','q3'],0);ans('q1',2,1000);pause(2000);reload(3000);
  assert.deepStrictEqual(nkPracticeCheckpoints(false).map(c=>c.sessionId),['s1']);
  resume('s1',4000);assert.strictEqual(S().id,'s1');ans('q2',1,5000);abandon(6000);
  same(effect(),base);
  const cp=nkPracticeFindCheckpoint('s1');assert.strictEqual(cp.lifecycle,'discarded');assert(cp.abandonedAt);
  assert.strictEqual(nkResumePracticeById('s1'),false,'the abandoned session cannot be resumed');assert.strictEqual(state.activeSession,null);
  assert.strictEqual(nkPracticeSessionFromCheckpoint({...cp,lifecycle:'paused'}),null,'not even from a stale paused copy');
  assert.notStrictEqual(nkPracticeContinuation().session?.id,'s1');
});
scenario('Timed test: answered, changed, marked and unanswered → abandon records nothing',()=>{
  reset();practice('s0',['q1'],0);ans('q1',2,1000);finish(2000);const base=effect();
  exam('e1',['q1','q2','q3'],10000);pick('q1',1,11000);pick('q2',2,12000);pick('q2',1,13000);
  assert.strictEqual(abandon(14000),true);
  same(effect(),base);assert.strictEqual(Object.values(state.attempts).flat().filter(a=>a.sessionId==='e1').length,0,'a timed test records nothing before Submit');
  assert.deepStrictEqual(routes.at(-1),['tests',undefined]);assert.strictEqual(state.abandonedSessions[0].mode,'exam');assert.strictEqual(state.abandonedSessions[0].answered,2);
  assert(toasts.at(-1).startsWith('Test abandoned'));
});
scenario('A scheduled mock cannot be abandoned; review and finished sessions have no Abandon',()=>{
  reset();exam('m1',['q1','q2'],0,{scheduledMockId:'sm1'});assert.strictEqual(nkAbandonSession(),false);assert(toasts.at(-1).includes('scheduled mock'));assert.strictEqual(S().id,'m1');
  state.activeSession={id:'r1',mode:'review',questionIds:['q1'],index:0,answers:{},submitted:{}};assert.strictEqual(nkAbandonSession(),false);
  state.activeSession=null;assert.strictEqual(nkAbandonSession(),false);
});
scenario('"Timed test in progress" → Abandon test records the entry and starts the new session',()=>{
  reset();exam('e1',['q1','q2'],0);pick('q1',1,500);nkOfferTimedSessionDecision({questionIds:['q3'],mode:'practice',title:'Next',context:'normal'});
  at(1000);nkResolveTimedSession('abandon');
  assert.strictEqual(state.abandonedSessions[0].sessionId,'e1');assert.notStrictEqual(state.activeSession?.id,'e1');
});
scenario('An answer from the abandoned session that arrives later (another device) never counts',()=>{
  reset();const base=effect();practice('s1',['q1','q2'],0);ans('q1',2,1000);abandon(2000);
  // Device B was still in s1 and answered q2 before it heard of the abandon; its attempt syncs in.
  state.attempts.q2=[{id:'late1',sessionId:'s1',selected:1,correct:true,timeSpent:9000,at:1500,reviewedAt:1500,source:'practice',rating:3,schedulerVersion:NK_FSRS_VERSION}];
  nkFsrsRebuildAll(false);
  same(effect(),base,'the late answer is dropped by session, without an undo event of its own');
});
scenario('Not-studied: a flag from an earlier session that answering cleared comes back; a flag set now stays; a manual unflag stays',()=>{
  reset();practice('s0',['q1','q2','q3'],0);nkToggleNotStudied('q1','s0');go('q2');nkToggleNotStudied('q2','s0');go('q3');nkToggleNotStudied('q3','s0');finish(1000);
  const flags=JSON.parse(JSON.stringify(state.notStudied));
  practice('s1',['q1','q2','q3','q4'],5000);ans('q1',2,6000);assert.strictEqual(state.notStudied.q1.on,false,'answering cleared the earlier flag');
  at(6500);go('q2');nkToggleNotStudied('q2','s1');assert.strictEqual(state.notStudied.q2.on,false,'unflagged by hand');
  at(6600);go('q4');nkToggleNotStudied('q4','s1');
  abandon(7000);
  assert.strictEqual(state.notStudied.q1.on,true,'the cleared flag is back');assert.strictEqual(state.notStudied.q1.session,flags.q1.session);assert(state.notStudied.q1.updatedAt>=NOW,'newer, so it wins sync');
  assert.strictEqual(state.notStudied.q2.on,false,'a manual unflag stays');assert.strictEqual(state.notStudied.q4.on,true,'a flag set in the session stays');
  assert(!Object.values(state.notStudiedHeld||{}).some(h=>h.session==='s1'),'nothing kept aside for s1');
  assert.strictEqual(nkFsrsActiveAttempts('q1').length,0);
});
scenario('Study module: progress from before the session comes back under a new sync epoch',()=>{
  reset();state.studyModules=[nkNormalizeStudyModule({id:'m1',name:'Limb set',questionIds:['q1','q2','q3'],totalQuestions:3,completedQuestionIds:[],currentPosition:0,answers:{},submitted:{},questionTimes:{},createdAt:1,lastOpenedAt:1,syncEpoch:'epoch_1',updatedAt:1})];
  at(100);startStudyModule('m1');ans('q1',2,1000);ans('q2',2,2000);
  const before=JSON.parse(JSON.stringify(S().abandonBase.module));assert.deepStrictEqual(before.answers,{});
  assert.deepStrictEqual(state.studyModules[0].completedQuestionIds,['q1','q2'],'the module mirrors the session');
  at(3000);startStudyModule('m1');const sid=S().id;ans('q3',2,3500);abandon(4000);
  const m=state.studyModules[0];
  assert.deepStrictEqual(m.completedQuestionIds,['q1','q2']);assert.deepStrictEqual(Object.keys(m.answers),['q1','q2'],'only this session is undone');
  assert.notStrictEqual(m.syncEpoch,'epoch_1');assert.strictEqual(m.updatedAt,NOW,'a newer copy, so it wins sync');
  assert.strictEqual(nkFsrsActiveAttempts('q3').length,0);assert.strictEqual(state.abandonedSessions.at(-1).kind,'module');assert.strictEqual(state.abandonedSessions.at(-1).sessionId,sid);
});
scenario('History rows: entries merge with saved results newest first, with the Abandoned badge',()=>{
  reset();practice('s0',['q1'],0);ans('q1',2,1000);finish(2000);practice('s1',['q2'],3000);ans('q2',1,3500);abandon(4000);
  const rows=nkSessionHistoryRows(state.tests,nkAbandonedEntries());assert.strictEqual(rows.length,2);
  const first=rows[0].html();assert(first.includes('is-abandoned')&&first.includes('nk-abandoned-badge">Abandoned<')&&first.includes('1 of 1 answered'));
  assert(!first.includes('onclick'),'an abandoned row opens nothing');assert(rows[1].html().includes('nk-test-row'));
});
scenario('Entries are cleaned and capped; repeated abandon of the same id keeps one',()=>{
  reset();for(let i=0;i<205;i++)nkAbAddEntry(nkAbClean({sessionId:'x'+i,title:'T',mode:'practice',abandonedAt:1000+i}));
  assert.strictEqual(state.abandonedSessions.length,200);assert.strictEqual(state.abandonedSessions[0].sessionId,'x5');
  assert.strictEqual(nkAbClean({sessionId:"x'><script>",abandonedAt:1}),null);assert.strictEqual(nkAbClean({sessionId:'ok'}),null,'no time, no entry');
  assert.strictEqual(nkAbAddEntry(nkAbClean({sessionId:'x9',abandonedAt:5})),false,'an older copy does not replace');
});
console.log('SESSION_ABANDON_SCENARIOS_OK '+results.length);
results.forEach(name=>console.log('  ok · '+name));
'''

SYNC_CASES = r'''
nkAuth={uid:'owner'};nkSyncMeta.needsInitialPull=false;nkSyncMeta.outbox={};nkSyncMeta.localHashes={};
assert(NK_SYNC_KINDS.includes('abandoned'),'abandoned sessions are a synced kind, so account reset tombstones them too');
state={...defaultState(),abandonedSessions:[{sessionId:'s1',title:'Upper limb',mode:'practice',kind:'practice',total:3,answered:1,startedAt:5,abandonedAt:10,updatedAt:10}]};
nkCaptureCloudChanges();
const env=nkSyncMeta.outbox['abandoned/s1'];assert(env&&!env.deleted,'one envelope per abandoned session');
assert.strictEqual(JSON.parse(env.payload).sessionId,'s1');
nkSyncMeta.outbox={};nkCaptureCloudChanges();assert(!nkSyncMeta.outbox['abandoned/s1'],'no repeated uploads');
// Device B: still in s1 with an answer recorded; device A's entry arrives.
state={...defaultState(),attempts:{q9:[{id:'a0',sessionId:'s0',correct:false,at:1},{id:'a1',sessionId:'s1',correct:true,at:2}]},reviews:{q9:{n:2}},
  activeSession:{id:'s1',mode:'practice',questionIds:['q9'],index:0,answers:{q9:1},submitted:{q9:true}},abandonedSessions:[]};
const doc=(payload,at,kind='abandoned',id='s1')=>({kind,entityId:id,ownerDevice:'web',updatedAt:at,deleted:false,payload:JSON.stringify(payload),schemaVersion:1});
nkApplyCloudEnvelope(doc({sessionId:'s1',title:'Upper limb',mode:'practice',kind:'practice',total:1,answered:1,startedAt:1,abandonedAt:20,updatedAt:20},20));
assert.strictEqual(state.activeSession,null,'the session ends on device B');
assert.deepStrictEqual(nkFsrsActiveAttempts('q9').map(a=>a.id),['a0'],'its answers stop counting on device B');
// A newer copy of the special session (or an old outbox) cannot reopen it.
nkApplyCloudEnvelope(doc({id:'s1',mode:'practice',questionIds:['q9'],index:0,answers:{}},30,'sessions','active'));
assert.strictEqual(state.activeSession,null,'a synced session copy cannot bring an abandoned session back');
assert(!nkApplyCloudEnvelope(doc({sessionId:"s1');x('",abandonedAt:40},40,'abandoned',"s1');x('"))||!state.abandonedSessions.some(e=>e.sessionId.includes("'")),'unsafe ids are refused');
console.log('SESSION_ABANDON_SYNC_OK');
'''


def latest_context() -> str:
    return extract_function(HTML.read_text(encoding="utf-8"), "nkLatestPracticeContext").strip()


def study_functions() -> str:
    src = STUDY.read_text(encoding="utf-8")
    names = ["nkStudyModuleList", "nkFindStudyModule", "nkModuleValidQuestionIds", "nkModuleCompletedSet", "nkNormalizeStudyModule", "nkSyncModuleFromSession", "startStudyModule"]
    return "\n".join(extract_function(src, name).strip() for name in names)


def test_install_contract() -> None:
    page = app_page()
    module = MODULE.read_text(encoding="utf-8")
    assert page.count("NK_SESSION_ABANDON_V1_START") == 1, "module must be assembled once"
    assert "NK_TIMED_ABANDON_GRID_V1_START" not in page, "the timed-only grid action is superseded"
    start = page.index("NK_SESSION_ABANDON_V1_START")
    for owner in ("NK_FSRS_V6_START", "NK_CONTINUE_PRACTICE_RESUME_V1_START", "NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START", "NK_EXAM_REVIEW_FLAGS_V1_START", "NK_REVISION_SESSION_V1_START", "NK_NOT_STUDIED_V1_START", "NK_CROSS_DEVICE_SYNC_V1_START"):
        assert page.index(owner) < start, f"abandon wraps after {owner}"
    qb = page[page.index("  window.QB={"):]
    qb = qb[:qb.index("};")]
    for name in ("nkAbandonSession,", "nkAbandonAnswer,", "nkAbandonTimedTest,"):
        assert name in qb, name
    for hook in ("nkFsrsActiveAttempts=function", "openSessionReview=function", "openQuestionNavigator=function", "nkResolveTimedSession=function", "nkPracticeSessionFromCheckpoint=function", "nkApplyCloudEnvelope=function", "nkNsClearEarlier=function"):
        assert hook in module, hook
    assert "confirm(" not in module.replace("confirmAction(", "").replace("confirmed", ""), "no browser confirm(): it is swallowed by WebViews and cannot be styled"
    sync = SYNC.read_text(encoding="utf-8")
    assert "NK_SYNC_KINDS.push('abandoned')" in sync and "nkEnvelope('abandoned'" in sync and "nkAbMergeEntry(payload)" in sync
    html = HTML.read_text(encoding="utf-8")
    assert "nkSessionHistoryRows(recent,nkAbandonedEntries(e=>e.mode==='exam'))" in html, "Tests > Recent lists abandoned tests"
    assert "nkAbandonedEntries(" in INSIGHTS.read_text(encoding="utf-8"), "Insights > Study sessions lists abandoned sessions"
    java = JAVA.read_text(encoding="utf-8")
    assert "@JavascriptInterface public boolean confirmAction(" in java and "window.QB.nkAbandonAnswer" in java and "if (!onAppOrigin()) return false;" in java
    assert "haptics: function (kind) { Haptics.play(kind); }" in FEEL.read_text(encoding="utf-8")
    css = app_css()
    assert css.count("/* ── nk-session-abandon-v1") == 1 and "nk-timed-abandon-grid" not in css
    assert css.index("/* ── nk-session-abandon-v1") < css.index("/* ── nk-visual-refinement-v1"), "abandon CSS sits before the visual refinement layer"
    for selector in (".nk-abandon-row .nk-abandon-trigger", ".nk-abandon-dialog", ".nk-abandon-actions .nk-abandon-go", ".nk-test-row.is-abandoned", ".nk-abandoned-badge", "prefers-reduced-motion"):
        assert selector in css, selector
    print("SESSION_ABANDON_INSTALL_OK")


def main() -> None:
    module = MODULE.read_text(encoding="utf-8")
    flags = ns.MODULE.read_text(encoding="utf-8")
    prelude = ns.PRELUDE % {"vendor": repr(str(ns.VENDOR))}
    script = (prelude + EXTRA % {"study": study_functions()} + ns.page_functions() + "\n" + ns.result_strip() + "\n"
              + ns.RESUME.read_text(encoding="utf-8") + "\n" + ns.FSRS.read_text(encoding="utf-8") + "\n" + flags + "\n" + module
              + SCENARIOS % {"latest": latest_context()})
    print(ns.run(script))
    print(ns.run(ns.SYNC_PRELUDE + "let nkResumePracticeById=()=>false;\n" + SYNC.read_text(encoding="utf-8") + "\n" + flags + "\n" + module + SYNC_CASES))
    test_install_contract()


if __name__ == "__main__":
    main()
