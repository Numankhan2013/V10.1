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
    "dailyCap:150", "needsAttention", "nkFsrsUndo", "function nkFsrsEligibility(q)",
    "if(history.length)return 'attempted'", "reason==='skipped'", "function nkFsrsQueueDialog(){navigate('fsrs');}",
    "function nkFsrsSessionAttemptSource(s)", "return'fsrs-review'",
    "['fsrs-review','spaced-review'].includes(a.source)",
    "typeof nkAllBankQuestions==='function'?nkAllBankQuestions()",
    "repeatIds=new Set", "[1,3].includes(Number(state.reviews?.[q.id]?.state))",
]
missing = [marker for marker in required if marker not in core]
if missing:
    raise SystemExit(f"FSRS core contract missing: {missing}")
for forbidden in ("newCardLimit", "newCards", "New cards each day", "const nkFsrsOriginalDashboard=dashboard"):
    if forbidden in core:
        raise SystemExit(f"FSRS review-only contract regressed: {forbidden}")

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
const LS_KEY='qbank_state_v1',now=Date.now(),questions=Array.from({{length:190}},(_,i)=>({{id:'q'+i,subject:i<95?'Anatomy':'Physiology',bank:'PrepLadder',chapterId:String(i%4),chapter:'Topic '+(i%4),correctOption:1}}));
const bankExtra={{id:'marrow-extra',subject:'Physiology',bank:'Marrow',chapterId:'9',chapter:'Expanded Marrow Topic',correctOption:1}};
const SUBJECTS=[{{subject:'Anatomy',topics:[{{id:'0',title:'Topic 0'}}],questions:questions.slice(0,95)}},{{subject:'Physiology',topics:[{{id:'0',title:'Topic 0'}}],questions:questions.slice(95)}}];
function nkAllBankQuestions(){{return [...questions,bankExtra];}}
let state={{attempts:{{q0:[{{id:'legacy',selected:1,correct:true,at:now-86400000}}]}},reviews:{{q0:{{nextReviewAt:now+123456}}}},fsrsPreferences:null,fsrsReviewEligible:{{}},activeSession:null}};
let lastRoute='',route={{page:'practice'}};let BY_ID=Object.fromEntries(questions.map(q=>[q.id,q])),dashboard=()=>'<main></main>',morePage=()=>'<main></main>',practicePage=()=>'<main></main>',practiceActionBar=()=>'<div class="fixed-actions nk-session-footer"><div class="fixed-actions-inner"><button>Previous</button><button>Next</button></div></div>',submitPractice=()=>{{}},nextQ=()=>{{}},prevQ=()=>{{}},goIndex=()=>{{}},retryCurrent=()=>{{}},endSession=()=>{{}},navigate=page=>{{lastRoute=page;}},recordAttempt=()=>{{}},qAttempts=()=>[],nkRebuildReviews=()=>{{}};
const saveState=()=>localStorage.setItem(LS_KEY,JSON.stringify(state)),startSession=()=>{{}},render=()=>{{}},showToast=()=>{{}},savePracticeElapsed=()=>{{}},haptic=()=>{{}},esc=x=>String(x),shell=x=>x,navIcon=()=>'',windowQB={{}};window.QB=windowQB;global.document={{getElementById:()=>null,querySelector:()=>null,body:{{insertAdjacentHTML:()=>{{}}}}}};window.addEventListener=()=>{{}};
{core}
nkFsrsInit();assert.equal(state.reviews.q0.schemaVersion,2);assert.equal(state.reviews.q0.nextReviewAt,now+123456,'legacy due date preserved');assert(nkFsrsAllQuestions().some(q=>q.id==='marrow-extra'),'FSRS question universe must include dynamically integrated bank questions');
const before=JSON.stringify(state.reviews.q0);nkFsrsReplay('q0',true);assert.equal(JSON.stringify(state.reviews.q0),before,'replay deterministic');
nkFsrsRecordAttempt('q0',1,1000,'practice',4);const latest=state.attempts.q0.at(-1);assert.equal(latest.rating,4);assert.equal(latest.schedulerVersion,'fsrs6');assert(latest.schedulerBefore&&latest.schedulerAfter);assert.equal(state.reviews.q0.legacyDueOverride,null);assert.equal(nkFsrsEligibility(questions[0]),'attempted','correct-only attempts must remain in the FSRS pool');
state.attempts.q1=[{{id:'binary-wrong',selected:2,correct:false,at:now-2000}},{{id:'binary-good',selected:1,correct:true,at:now-1000}}];nkFsrsReplay('q1');assert.equal(state.reviews.q1.repetitions,2,'legacy binary attempts replay');assert.equal(nkFsrsEligibility(questions[1]),'wrong');
const empty=window.FSRS.createEmptyCard(new Date(now)),preview=nkFsrsEngine().repeat(empty,new Date(now));[1,2,3,4].forEach(r=>assert(preview[r].card.due instanceof Date));
for(let i=2;i<162;i++){{state.attempts['q'+i]=[{{id:'a'+i,selected:2,correct:false,at:now-i}}];state.reviews['q'+i]={{schemaVersion:2,due:now-1,nextReviewAt:now-1,state:i===2?1:2,stability:2,difficulty:5,repetitions:1,lapses:1,elapsedDays:0,scheduledDays:1,lastReview:now-86400000}};}}
const queue=nkFsrsQueue();assert.equal(queue.cards.length,150,'ordinary practice must not consume the FSRS daily review cap');assert.equal(queue.cards[0].id,'q2','learning reviews first');assert.equal(queue.rolledOver,10);assert(queue.cards.every(q=>nkFsrsEligibility(q)),'queue may contain only review-eligible questions');assert(!queue.cards.some(q=>q.id==='q188'),'unseen questions must never enter FSRS');
state.attempts['marrow-extra']=[{{id:'marrow-wrong',selected:2,correct:false,at:now-3000}}];state.reviews['marrow-extra']={{schemaVersion:2,due:now-1,nextReviewAt:now-1,state:2,stability:1,difficulty:5,repetitions:1,lapses:1,elapsedDays:0,scheduledDays:1,lastReview:now-86400000}};assert(nkFsrsQueue({{subject:'Physiology'}}).due.some(q=>q.id==='marrow-extra'),'expanded Marrow question must participate in FSRS review queue');const marrowOnly=nkFsrsQueue({{subject:'Physiology',bank:'Marrow'}});assert.deepEqual(marrowOnly.due.map(q=>q.id),['marrow-extra'],'bank focus excludes PrepLadder due cards');assert.deepEqual(marrowOnly.cards.map(q=>q.id),['marrow-extra'],'bank focus enters the selected FSRS queue before the daily cap');delete state.attempts['marrow-extra'];delete state.reviews['marrow-extra'];
state.attempts.q2.push({{id:'today-learning-review',selected:1,correct:true,at:now,reviewedAt:now,source:'fsrs-review',rating:3,schedulerVersion:NK_FSRS_VERSION}});state.attempts.q3.push({{id:'today-normal-review',selected:1,correct:true,at:now,reviewedAt:now,source:'fsrs-review',rating:3,schedulerVersion:NK_FSRS_VERSION}});const afterReviewCap=nkFsrsQueue();assert.equal(afterReviewCap.cards.length,149,'two reviewed IDs consume distinct-card slots while a due learning repeat remains admissible');assert(afterReviewCap.cards.some(q=>q.id==='q2'),'due same-day learning/relearning step must remain reviewable');assert(!afterReviewCap.cards.some(q=>q.id==='q3'),'ordinary review completed today must not be immediately repeated');assert.equal(afterReviewCap.rolledOver,10);state.attempts.q2.pop();state.attempts.q3.pop();
const beforeSkip=nkFsrsQueue({{subject:'Physiology',topic:'1'}});assert(!beforeSkip.cards.some(q=>q.id==='q189'),'unseen topic question must stay out before session submission');state.fsrsReviewEligible.q189={{reason:'skipped',at:now}};delete state.reviews.q189;const filtered=nkFsrsQueue({{subject:'Physiology',topic:'1'}});assert(filtered.cards.every(q=>q.subject==='Physiology'&&q.chapterId==='1'));assert(filtered.cards.some(q=>q.id==='q189'),'session-submitted skipped question must be eligible');assert.equal(nkFsrsEligibility(questions[189]),'skipped');
nkFsrsSetPreference('desiredRetention',99);assert.equal(state.fsrsPreferences.desiredRetention,.97);nkFsrsSetPreference('newCardLimit',30);assert(!Object.prototype.hasOwnProperty.call(state.fsrsPreferences,'newCardLimit'),'new-card preference must not exist');
const countBefore=nkFsrsActiveAttempts('q0').length;nkFsrsUndo();assert.equal(nkFsrsActiveAttempts('q0').length,countBefore-1,'undo removes latest active rating through an event');
const dueBefore=state.reviews.q1.due;nkFsrsSetPreference('desiredRetention',80);nkFsrsReplay('q1');assert.equal(state.reviews.q1.due,dueBefore,'settings must not reschedule past ratings on replay');
assert.equal(dashboard(),'<main></main>','FSRS must not append a second Home review card');nkFsrsQueueDialog();assert.equal(lastRoute,'fsrs','legacy queue entry must route to full FSRS page, not a popup');
state.activeSession={{mode:'practice',questionIds:['q188'],index:0,answers:{{q188:1}},submitted:{{}},questionTimes:{{q188:900}}}};
assert(!practiceActionBar().includes('nk-fsrs-rating'),'no recall dock before answer submission');assert.equal(typeof nkFsrsSaveSettings,'function');const settings=nkFsrsSettingsMarkup();assert(settings.includes('Save changes')&&settings.includes('nk-fsrs-customization'));assert(!settings.includes('New cards each day'));assert(settings.includes('FSRS schedules every answered question.'));
submitPractice();assert(state.activeSession.pendingRating.q188);
const dock=practiceActionBar();assert(dock.includes('nk-fsrs-docked'));assert(dock.indexOf('nk-fsrs-rating')<dock.indexOf('fixed-actions-inner'),'recall dock must be inside the fixed footer immediately above navigation');assert(dock.includes('Rate recall')&&dock.includes('Default: Good')&&dock.includes('nk-fsrs-medallion'));assert(!practicePage().includes('nk-fsrs-rating'),'no duplicate in content');nextQ();assert.equal(nkFsrsActiveAttempts('q188').at(-1).rating,3);assert.equal(nkFsrsActiveAttempts('q188').at(-1).source,'practice','ordinary practice remains ordinary practice');assert.equal(nkFsrsEligibility(questions[188]),'attempted');nkFsrsRecoverPending();assert.equal(nkFsrsActiveAttempts('q188').length,1);
state.activeSession={{mode:'practice',originRoute:'fsrs',questionIds:['q186'],index:0,answers:{{q186:1}},submitted:{{}},questionTimes:{{q186:1200}}}};submitPractice();nextQ();assert.equal(nkFsrsActiveAttempts('q186').at(-1).source,'fsrs-review','FSRS-origin review attempts must be tagged distinctly for the daily cap');
state.activeSession={{mode:'practice',questionIds:['q187'],index:0,answers:{{q187:2}},submitted:{{}},questionTimes:{{}}}};submitPractice();assert.equal(nkFsrsActiveAttempts('q187').at(-1).rating,1);assert(!practiceActionBar().includes('nk-fsrs-rating'),'incorrect answer retains automatic Again without manual dock');
const longId='q185';state.attempts[longId]=[{{id:'long-wrong',selected:2,correct:false,at:now-30*86400000,reviewedAt:now-30*86400000}}];nkFsrsReplay(longId);assert.equal(nkFsrsEligibility(questions[185]),'wrong');let reviewAt=Math.max(now,Number(state.reviews[longId].due||now)),firstStability=0;for(let step=0;step<4;step++){{nkFsrsRecordAttempt(longId,1,800,'fsrs-review',3,reviewAt,'long-good-'+step);const r=state.reviews[longId];assert(Number(r.nextReviewAt)>reviewAt,'Good review must schedule a future review');if(step===0)firstStability=Number(r.stability);reviewAt=Number(r.nextReviewAt);}}assert(Number(state.reviews[longId].stability)>=firstStability,'repeated successful reviews must not erase learned stability');assert.equal(nkFsrsEligibility(questions[185]),'wrong','a formerly wrong question stays in the review lane but sleeps until due');assert(!nkFsrsQueue().cards.some(q=>q.id===longId),'successfully scheduled review must disappear from the due queue until its future date');
const savedRetention=state.fsrsPreferences.desiredRetention;
nkFsrsEditSetting('desiredRetention','86');assert.equal(state.fsrsPreferences.desiredRetention,savedRetention);assert(nkFsrsDirty());
nkFsrsSaveSettings();assert.equal(state.fsrsPreferences.desiredRetention,.86);assert(!nkFsrsDirty());
const dueAtSave=state.reviews.q1.due;nkFsrsEditSetting('desiredRetention','999');assert.equal(nkFsrsSaveSettings(),false);assert.equal(state.fsrsPreferences.desiredRetention,.86);assert.equal(state.reviews.q1.due,dueAtSave);
nkFsrsDraft=null;assert(!nkFsrsDirty());
// An amendment changes the grade of one retrieval, not its count or timestamp.
state.activeSession={{id:'rating-session',startedAt:now,mode:'practice',questionIds:['q184'],index:0,answers:{{q184:1}},submitted:{{}},questionTimes:{{q184:500}}}};
submitPractice();nkRateCurrent(2,'q184','rating-session');
const rated=state.attempts.q184[0],ratedAt=rated.reviewedAt;
assert(nkFsrsRatingMarkup('q184').includes('Saved: Hard'),'saved dock remains visible');
assert.equal(nkFsrsRating(nkFsrsActiveAttempts('q184')[0]),2);
nkRateCurrent(3,'q184','rating-session');nkRateCurrent(4,'q184','rating-session');
assert.equal(state.attempts.q184.length,1,'rating edits do not add attempts');
assert.equal(state.reviews.q184.repetitions,1,'rating edits do not inflate FSRS reviews');
assert.equal(nkFsrsActiveAttempts('q184')[0].reviewedAt,ratedAt);
assert.equal(nkFsrsActiveAttempts('q184')[0].rating,4);
const expected=nkFsrsEngine(rated.schedulerPreferences).next(nkFsrsCardFromReview(rated.schedulerBefore,ratedAt),new Date(ratedAt),4).card;
assert.equal(state.reviews.q184.due,new Date(expected.due).getTime(),'amended schedule is computed from the original pre-review card');
const revisionCount=state.fsrsRatingRevisions.q184.length;nkRateCurrent(4,'q184','rating-session');
assert.equal(state.fsrsRatingRevisions.q184.length,revisionCount,'repeated grade is idempotent');
const amendedDue=state.reviews.q184.due;state.fsrsRatingRevisions.q184.reverse();nkFsrsReplay('q184');
assert.equal(state.reviews.q184.due,amendedDue,'revision arrival order cannot change replay');
state.activeSession.pendingRating={{q184:{{id:rated.id,selected:1}}}};nkFsrsPruneCommittedPending();
assert(!state.activeSession.pendingRating.q184,'special-session sync also removes committed pending IDs');
nkRateCurrent(2,'other-question','rating-session');nkRateCurrent(2,'q184','other-session');
assert.equal(state.reviews.q184.due,amendedDue,'stale rating callbacks cannot edit another question/session');
const savedAttempts=state.attempts;state.attempts={{q184:savedAttempts.q184}};
nkFsrsUndo();assert.equal(nkFsrsActiveAttempts('q184')[0].rating,3,'undo latest edit restores the previous grade');
assert.equal(state.reviews.q184.repetitions,1,'undoing a grade edit retains its original retrieval');
nkFsrsUndo();assert.equal(nkFsrsActiveAttempts('q184')[0].rating,2);state.attempts=savedAttempts;
assert.equal(nkFsrsUnresolvedMistake('q1'),false,'a correct retry resolves an earlier miss');
assert.equal(nkFsrsEligibility(questions[1]),'wrong','FSRS history eligibility remains independent of unresolved mistakes');
state.attempts.q1.push({{id:'later-wrong',correct:false,at:now+100,reviewedAt:now+100}});
assert.equal(nkFsrsUnresolvedMistake('q1'),true,'a later miss returns to Mistakes');
const savedTest={{createdAt:now-1500}};
assert.deepEqual(nkFsrsUnresolvedResultMisses(savedTest,['q184','q1']),['q1'],'saved-result follow-up only retains unresolved misses');
// Scheduled lapses stay in FSRS; ordinary misses resolve on any correct answer.
state.attempts.q1=[{{id:'initial-good',correct:true,at:now,source:'practice'}},{{id:'review-lapse',correct:false,at:now+1,source:'fsrs-review'}}];
assert.equal(nkFsrsPracticeMistake('q1'),false);
assert.equal(nkFsrsUnresolvedMistake('q1'),true,'FSRS lapse classification is unchanged');
state.attempts.q1=[{{id:'initial-miss',correct:false,at:now,source:'practice'}},{{id:'review-lapse',correct:false,at:now+1,source:'fsrs-review'}}];
assert.equal(nkFsrsPracticeMistake('q1'),true,'an unresolved initial miss is not erased by another lapse');
state.attempts.q1.push({{id:'review-good',correct:true,at:now+2,source:'fsrs-review'}});
assert.equal(nkFsrsPracticeMistake('q1'),false,'a correct scheduled review resolves the initial miss');
state.attempts.q1.push({{id:'review-lapse-again',correct:false,at:now+3,source:'fsrs-review'}});
assert.equal(nkFsrsPracticeMistake('q1'),false,'a later FSRS lapse must not resurrect the practice mistake');
state.attempts.q1.push({{id:'new-test-miss',correct:false,at:now+4,source:'exam'}});
assert.equal(nkFsrsPracticeMistake('q1'),true);
const untouchedSchedule=JSON.stringify(state.reviews.q1);
nkFsrsPracticeMistake('q1');assert.equal(JSON.stringify(state.reviews.q1),untouchedSchedule);
state.attempts.q1.push({{id:'undo-test',isUndo:true,undoOf:'new-test-miss',at:now+5}});
assert.equal(nkFsrsPracticeMistake('q1'),false,'undone mistakes do not enter the queue');
console.log('FSRS_BEHAVIOR_OK');
"""

with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
    handle.write(harness)
    test_path = Path(handle.name)
try:
    subprocess.run(["node", str(test_path)], cwd=ROOT, check=True)
finally:
    test_path.unlink(missing_ok=True)

print("FSRS_V1_TEST_OK: migration, deterministic replay, all-attempt eligibility, submit-only skips, same-day relearning, daily cap, scheduling, filters, settings and undo")
