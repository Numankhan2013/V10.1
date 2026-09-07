#!/usr/bin/env python3
"""Behavior and packaging contracts for the offline FSRS v6 milestone."""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/fsrs_scheduler_core.js"
VENDOR = ROOT / "app/src/main/assets/vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js"
LICENSE = ROOT / "app/src/main/assets/vendor/ts-fsrs/LICENSE"
HTML = ROOT / "app/src/main/assets/index.html"

for path in (CORE, VENDOR, LICENSE):
    if not path.exists() or path.stat().st_size < (500 if path == LICENSE else 1000):
        raise SystemExit(f"Missing pinned offline FSRS asset: {path}")

core = CORE.read_text(encoding="utf-8")
required = [
    "request_retention:p.desiredRetention", "maximum_interval:p.maximumInterval",
    "enable_fuzz:false", "learning_steps:['10m']", "relearning_steps:['10m']",
    "legacyDueOverride", "schedulerVersion:NK_FSRS_VERSION", "nkFsrsRecoverPending",
    "dailyCap:150", "newCardLimit:30", "needsAttention", "nkFsrsUndo",
]
missing = [marker for marker in required if marker not in core]
if missing:
    raise SystemExit(f"FSRS core contract missing: {missing}")

html = HTML.read_text(encoding="utf-8")
if "NK_FSRS_V6_START" not in html:
    from apply_fsrs_v1 import transform
    html = transform(html)
for marker in ["ts-fsrs-5.4.2.umd.js", "NK_FSRS_V6_START", "nkFsrsInit();"]:
    if marker not in html:
        raise SystemExit(f"Generated app missing FSRS marker: {marker}")

vendor_path = str(VENDOR).replace("\\", "\\\\").replace("'", "\\'")
harness = f"""
const assert=require('assert');global.window=globalThis;window.FSRS=require('{vendor_path}');
const store=new Map();global.localStorage={{getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v))}};
const LS_KEY='qbank_state_v1',now=Date.now(),questions=Array.from({{length:190}},(_,i)=>({{id:'q'+i,subject:i<95?'Anatomy':'Physiology',chapterId:String(i%4),chapter:'Topic '+(i%4),correctOption:1}}));
const SUBJECTS=[{{subject:'Anatomy',topics:[{{id:'0',title:'Topic 0'}}],questions:questions.slice(0,95)}},{{subject:'Physiology',topics:[{{id:'0',title:'Topic 0'}}],questions:questions.slice(95)}}];
let state={{attempts:{{q0:[{{id:'legacy',selected:1,correct:true,at:now-86400000}}]}},reviews:{{q0:{{nextReviewAt:now+123456}}}},fsrsPreferences:null,activeSession:null}};
let BY_ID=Object.fromEntries(questions.map(q=>[q.id,q])),dashboard=()=>'<main></main>',morePage=()=>'<main></main>',practicePage=()=>'<main></main>',practiceActionBar=()=>'<div class="fixed-actions nk-session-footer"><div class="fixed-actions-inner"><button>Previous</button><button>Next</button></div></div>',submitPractice=()=>{{}},nextQ=()=>{{}},prevQ=()=>{{}},goIndex=()=>{{}},retryCurrent=()=>{{}},endSession=()=>{{}},navigate=()=>{{}},recordAttempt=()=>{{}},qAttempts=()=>[],nkRebuildReviews=()=>{{}};
const saveState=()=>localStorage.setItem(LS_KEY,JSON.stringify(state)),startSession=()=>{{}},render=()=>{{}},showToast=()=>{{}},savePracticeElapsed=()=>{{}},haptic=()=>{{}},esc=x=>String(x),windowQB={{}};window.QB=windowQB;global.document={{getElementById:()=>null,body:{{insertAdjacentHTML:()=>{{}}}}}};window.addEventListener=()=>{{}};
{core}
nkFsrsInit();assert.equal(state.reviews.q0.schemaVersion,2);assert.equal(state.reviews.q0.nextReviewAt,now+123456,'legacy due date preserved');
const before=JSON.stringify(state.reviews.q0);nkFsrsReplay('q0',true);assert.equal(JSON.stringify(state.reviews.q0),before,'replay deterministic');
nkFsrsRecordAttempt('q0',1,1000,'practice',4);const latest=state.attempts.q0.at(-1);assert.equal(latest.rating,4);assert.equal(latest.schedulerVersion,'fsrs6');assert(latest.schedulerBefore&&latest.schedulerAfter);assert.equal(state.reviews.q0.legacyDueOverride,null);
state.attempts.q1=[{{id:'binary-wrong',selected:2,correct:false,at:now-2000}},{{id:'binary-good',selected:1,correct:true,at:now-1000}}];nkFsrsReplay('q1');assert.equal(state.reviews.q1.repetitions,2,'legacy binary attempts replay');
const empty=window.FSRS.createEmptyCard(new Date(now)),preview=nkFsrsEngine().repeat(empty,new Date(now));[1,2,3,4].forEach(r=>assert(preview[r].card.due instanceof Date));
for(let i=2;i<162;i++){{state.attempts['q'+i]=[{{id:'a'+i,selected:1,correct:true,at:now-i}}];state.reviews['q'+i]={{schemaVersion:2,due:now-1,nextReviewAt:now-1,state:i===2?1:2,stability:2,difficulty:5,repetitions:1,lapses:0,elapsedDays:0,scheduledDays:1,lastReview:now-86400000}};}}
const queue=nkFsrsQueue();assert.equal(queue.cards.length,149,'one card already reviewed today consumes a daily slot');assert.equal(queue.cards[0].id,'q2','learning cards first');assert(queue.rolledOver>=10);
state.attempts.q189=[];delete state.reviews.q189;const filtered=nkFsrsQueue({{subject:'Physiology',topic:'1'}});assert(filtered.cards.every(q=>q.subject==='Physiology'&&q.chapterId==='1'));
nkFsrsSetPreference('desiredRetention',99);assert.equal(state.fsrsPreferences.desiredRetention,.97);nkFsrsSetPreference('newCardLimit',-1);assert.equal(state.fsrsPreferences.newCardLimit,0);
const countBefore=nkFsrsActiveAttempts('q0').length;nkFsrsUndo();assert.equal(nkFsrsActiveAttempts('q0').length,countBefore-1,'undo removes latest active rating through an event');
const dueBefore=state.reviews.q1.due;nkFsrsSetPreference('desiredRetention',80);nkFsrsReplay('q1');assert.equal(state.reviews.q1.due,dueBefore,'settings must not reschedule past ratings on replay');
state.activeSession={{mode:'practice',questionIds:['q188'],index:0,answers:{{q188:1}},submitted:{{}},questionTimes:{{q188:900}}}};
assert(!practiceActionBar().includes('nk-fsrs-rating'),'no recall dock before answer submission');
submitPractice();assert(state.activeSession.pendingRating.q188);
const dock=practiceActionBar();assert(dock.includes('nk-fsrs-docked'));assert(dock.indexOf('nk-fsrs-rating')<dock.indexOf('fixed-actions-inner'),'recall dock must be inside the fixed footer immediately above navigation');assert(dock.includes('Rate recall')&&dock.includes('Default: Good')&&dock.includes('nk-fsrs-medallion'));assert(!practicePage().includes('nk-fsrs-rating'),'no duplicate in content');nextQ();assert.equal(nkFsrsActiveAttempts('q188').at(-1).rating,3);nkFsrsRecoverPending();assert.equal(nkFsrsActiveAttempts('q188').length,1);
state.activeSession={{mode:'practice',questionIds:['q187'],index:0,answers:{{q187:2}},submitted:{{}},questionTimes:{{}}}};submitPractice();assert.equal(nkFsrsActiveAttempts('q187').at(-1).rating,1);assert(!practiceActionBar().includes('nk-fsrs-rating'),'incorrect answer retains automatic Again without manual dock');
console.log('FSRS_BEHAVIOR_OK');
"""

with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
    handle.write(harness)
    test_path = Path(handle.name)
try:
    subprocess.run(["node", str(test_path)], cwd=ROOT, check=True)
finally:
    test_path.unlink(missing_ok=True)

print("FSRS_V1_TEST_OK: migration, deterministic replay, ratings, queue caps, filters, settings, undo and offline assets")
