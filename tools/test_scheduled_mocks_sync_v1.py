#!/usr/bin/env python3
"""Scheduled mocks travel between devices (cross_device_sync.js kind `scheduledMocks`).

Root cause of "the scheduled-mock card shows on my phone but not on my iPad":
bookings live in `state.scheduledMocks`, which no sync kind carried. The miss
(a `missed_<id>` zero) and the make-up result travelled as `tests`, but the
booking itself stayed on the device that made it, so every other device had
no ticket, no MAKE-UP OWED card and no attendance streak.

Two devices run here in separate Node contexts with the real sync module and
the real scheduled-mocks module. Envelopes go from one device's outbox into
the other's pull path (nkApplyCloudEnvelope) and back, so the test covers:
booking A -> B, outcome stamps both ways, no duplicate and no lost bookings,
stable hashes (no echo loop), a zero withdrawn when the sitting syncs in,
unsafe ids refused, Abandon still refused for a scheduled mock, and the Home
markup (ticket, MAKE-UP OWED, attendance) on the receiving device. It also
checks the booking-sheet time parser, which no longer relies on
`new Date("YYYY-MM-DDTHH:MM")` (engine-dependent on older WebKit).
"""

from pathlib import Path
import json
import subprocess
import tempfile

from app_page import app_page

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "app/src/main/modules/cross_device_sync.js"
SCHED = ROOT / "app/src/main/modules/scheduled_mocks.js"

PRELUDE = r'''
const storage={};
var localStorage={getItem:k=>Object.prototype.hasOwnProperty.call(storage,k)?storage[k]:null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]};
var window={NK_QBANK_FIREBASE_CONFIG:{}};var navigator={onLine:true};var location={hostname:'qbank.local'};
var document={querySelector:()=>null,getElementById:()=>null,querySelectorAll:()=>[]};
var setTimeout=()=>0,clearTimeout=()=>{};
const T0=Date.UTC(2026,10,21,6,30);let NOW=T0;Date.now=()=>NOW;
const LS_KEY='qbank_state_v1';let state={};let activeSubject='Anatomy';const SUBJECT_BY_NAME={Anatomy:{}};
let toasts=[];
function render(){} function showToast(m){toasts.push(m)} function saveState(){return true} function fmtDate(v){return String(v)}
function fmtNum(n){return String(n)} function navIcon(n){return '<i data-icon="'+n+'"></i>'}
function esc(v){return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[c])}
function nkExamIsPlain(m){return !m||(Number(m.correct)===1&&Number(m.wrong)===0&&Number(m.blank||0)===0)}
function nkMarkingLabel(m){return '+'+m.correct+'/'+m.wrong}
function nkMockList(){return []}
function defaultState(){return {attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,questionNotes:{},fsrsReviewEligible:{}}}
function applySubject(v){activeSubject=v} function nkNormalizeState(v){return v} function nkDurablePersist(){return true}
let BY_ID={},CHAPTERS=[],CHAPTER_BY_ID={};
let nkFsrsActiveAttempts=qid=>state.attempts?.[qid]||[];
let nkAbandonTimedTest=()=>'abandoned';
let dashboard=()=>'<main><section class="nk-home-revision nk-today"></section><section class="nk-section nk-study-sets"></section></main>';
let testsPage=()=>'<main><section class="nk-v3-section nk-na-saved-mocks"></section></main>';
'''

SCENARIO = r'''
const vm=require('vm'),assert=require('assert');
const src=%(src)s;
function device(name){const ctx=vm.createContext({console,require,JSON,Math,Date,Object,Array,String,Number,Boolean,Set,Map,RegExp,Error,Promise,encodeURIComponent,URLSearchParams});vm.runInContext(src,ctx,{filename:name});const run=code=>vm.runInContext(code,ctx);run("nkAuth={uid:'owner'};nkSyncMeta.needsInitialPull=false;nkSyncMeta.outbox={};nkSyncMeta.localHashes={};nkSyncMeta.deviceId='"+name+"';");return run;}
const phone=device('phone'),ipad=device('ipad');
const NOW=Date.UTC(2026,10,21,6,30),H=3600e3,ids=JSON.stringify(Array.from({length:100},(_,i)=>'q'+i));
// Capture on one device, then hand its outbox to the other device's pull path, like a push then a pull.
function push(from){from('nkCaptureCloudChanges()');const out=JSON.parse(from("JSON.stringify(Object.values(nkSyncMeta.outbox))"));from('nkSyncMeta.outbox={}');return out;}
function pull(to,envs){to('var __in='+JSON.stringify(envs)+';__in.forEach(e=>nkApplyCloudEnvelope(e));');}
const results=[];function scenario(name,fn){fn();results.push(name);}

scenario('the sync kind exists and every pull reads it',()=>{
  assert(phone("NK_SYNC_KINDS.includes('scheduledMocks')"),'scheduledMocks is a synced kind (pull and account reset walk NK_SYNC_KINDS)');
  assert.strictEqual(phone("NK_SYNC_KINDS.filter(k=>k==='scheduledMocks').length"),1);
});

scenario('a booking made on the phone reaches the iPad with the same frozen paper',()=>{
  phone(`state={...defaultState(),scheduledMocks:[{id:'sm_1',name:'Mixed Subjects CBT',questionIds:${ids},at:NOW+20*${H},createdAt:NOW,marking:{correct:4,wrong:-1,blank:0},seconds:60}]};`);
  const envs=push(phone);
  const mine=envs.filter(e=>e.kind==='scheduledMocks');assert.strictEqual(mine.length,1,'one envelope per booking');
  assert.strictEqual(mine[0].entityId,'sm_1');assert(!mine[0].deleted);
  ipad('state={...defaultState(),scheduledMocks:[]};');pull(ipad,envs);
  const got=JSON.parse(ipad('JSON.stringify(state.scheduledMocks)'));
  assert.strictEqual(got.length,1);assert.strictEqual(got[0].id,'sm_1');assert.strictEqual(got[0].questionIds.length,100);
  assert.strictEqual(got[0].at,JSON.parse(phone('JSON.stringify(state.scheduledMocks)'))[0].at,'the booked instant is an epoch number: no date-string parsing, no timezone shift');
  assert.deepStrictEqual(got[0].marking,{correct:4,wrong:-1,blank:0});
  // Upcoming within 36 h: Home shows the ticket on the iPad too.
  const home=ipad('dashboard()');
  assert(home.includes('nk-sched-ticket is-upcoming'),'iPad Home shows the upcoming ticket');
  assert(home.indexOf('nk-sched-home')<home.indexOf('nk-study-sets'),'the ticket sits above My study sets, as on the phone');
  assert(ipad("testsPage()").includes('Scheduled mocks'),'iPad Tests lists the booking');
});

scenario('pulling again or echoing back adds nothing (no duplicates, no ping-pong)',()=>{
  const back=push(ipad).filter(e=>e.kind==='scheduledMocks');
  assert.strictEqual(back.length,0,'an unchanged received booking is not uploaded again');
  const again=JSON.parse(phone("JSON.stringify([nkEnvelope('scheduledMocks','sm_1',nkSchedSyncEntries()[0],NOW)])"));
  pull(ipad,again);pull(ipad,again);
  assert.strictEqual(ipad('state.scheduledMocks.length'),1,'the same booking twice is still one booking');
});

scenario('a missed sitting: the iPad shows MAKE-UP OWED, the zero and the broken streak',()=>{
  // Wed 10:00 sitting, never started; the phone records the miss.
  phone(`state.scheduledMocks.push({id:'sm_wed',name:'Mixed Subjects CBT',questionIds:${ids},at:NOW-72*${H},createdAt:NOW-96*${H},marking:{correct:1,wrong:0,blank:0},seconds:60});`);
  phone('dashboard()');
  assert(phone("state.tests.some(t=>t.id==='missed_sm_wed'&&t.missed)"),'phone recorded the zero');
  const envs=push(phone);pull(ipad,envs);
  const booking=JSON.parse(ipad("JSON.stringify(state.scheduledMocks.find(m=>m.id==='sm_wed'))"));
  assert(booking&&booking.missedAt>0,'the miss stamp travels with the booking');
  assert.strictEqual(ipad("state.tests.filter(t=>t.id==='missed_sm_wed').length"),1,'one zero, not two');
  const home=ipad('dashboard()');
  assert(home.includes('nk-sched-makeup')&&home.includes('Make-up owed')&&home.includes('Mixed Subjects CBT')&&home.includes('Sit it'),'iPad Home shows the MAKE-UP OWED card');
  assert.strictEqual(ipad("state.tests.filter(t=>t.id==='missed_sm_wed').length"),1,'rendering does not add a second zero');
  const tests=ipad('testsPage()');
  assert(tests.includes('nk-sched-attend')&&tests.includes('Kept 0 of 1')&&tests.includes('Streak broken'),'attendance and streak match the phone');
  assert.strictEqual(ipad('JSON.stringify(nkSchedAttendance())'),phone('JSON.stringify(nkSchedAttendance())'),'both devices compute the same attendance');
});

scenario('a make-up sat on the iPad clears the card on the phone',()=>{
  ipad("state.tests.push({id:'t_mk',title:'Make-up · Mixed Subjects CBT',questionIds:['q1'],answers:{},correct:60,total:100,createdAt:NOW,makeupFor:'sm_wed'});nkSchedNoteTaken({makeupFor:'sm_wed'},{id:'t_mk'});");
  assert.strictEqual(ipad("state.scheduledMocks.find(m=>m.id==='sm_wed').makeupTestId"),'t_mk');
  const envs=push(ipad);
  assert(envs.some(e=>e.kind==='scheduledMocks'&&e.entityId==='sm_wed'&&JSON.parse(e.payload).makeupTestId==='t_mk'),'the outcome stamp is uploaded');
  pull(phone,envs);
  assert.strictEqual(phone("state.scheduledMocks.find(m=>m.id==='sm_wed').makeupTestId"),'t_mk','the stamp merges in on the phone');
  assert(!phone('dashboard()').includes('nk-sched-makeup'),'no MAKE-UP OWED once it is made up');
  assert.strictEqual(phone('state.scheduledMocks.length'),2,'nothing lost, nothing duplicated');
});

scenario('streak: kept sittings count the same on both devices',()=>{
  phone(`state.scheduledMocks.push({id:'sm_k1',name:'Kept 1',questionIds:['q1','q2'],at:NOW-48*${H},createdAt:NOW-50*${H},marking:{correct:1,wrong:0,blank:0},seconds:60,takenTestId:'t_k1'},{id:'sm_k2',name:'Kept 2',questionIds:['q1','q2'],at:NOW-24*${H},createdAt:NOW-26*${H},marking:{correct:1,wrong:0,blank:0},seconds:60,takenTestId:'t_k2'});state.tests.push({id:'t_k1',scheduledMockId:'sm_k1',correct:1,total:2,createdAt:NOW-47*${H}},{id:'t_k2',scheduledMockId:'sm_k2',correct:2,total:2,createdAt:NOW-23*${H}});`);
  pull(ipad,push(phone));
  const a=JSON.parse(ipad('JSON.stringify(nkSchedAttendance())'));
  assert.strictEqual(a.streak,2);assert.strictEqual(a.kept,2);assert.strictEqual(a.missed,1);
  assert(ipad('testsPage()').includes('2 in a row'),'the streak is shown on the iPad');
});

scenario('both devices book at once: both bookings survive on both',()=>{
  ipad(`state.scheduledMocks.push({id:'sm_ipad',name:'iPad booking',questionIds:['q3'],at:NOW+5*${H},createdAt:NOW,marking:{correct:1,wrong:0,blank:0},seconds:60});`);
  phone(`state.scheduledMocks.push({id:'sm_phone',name:'Phone booking',questionIds:['q4'],at:NOW+6*${H},createdAt:NOW,marking:{correct:1,wrong:0,blank:0},seconds:60});`);
  const fromIpad=push(ipad),fromPhone=push(phone);pull(phone,fromIpad);pull(ipad,fromPhone);
  const p=JSON.parse(phone("JSON.stringify(state.scheduledMocks.map(m=>m.id).sort())")),i=JSON.parse(ipad("JSON.stringify(state.scheduledMocks.map(m=>m.id).sort())"));
  assert.deepStrictEqual(p,i,'same bookings on both devices');assert.strictEqual(p.length,new Set(p).size,'no duplicates');
  assert(p.includes('sm_ipad')&&p.includes('sm_phone'));
  // Each device ends with nothing new to send after merging (converged).
  assert.strictEqual(push(phone).filter(e=>e.kind==='scheduledMocks').length,0);
  assert.strictEqual(push(ipad).filter(e=>e.kind==='scheduledMocks').length,0);
});

scenario('a zero recorded before the sitting synced in is withdrawn; the sitting wins',()=>{
  // The iPad, offline during the sitting, records a miss; the phone actually sat it.
  ipad(`state.scheduledMocks.push({id:'sm_race',name:'Race',questionIds:['q5'],at:NOW-2*${H},createdAt:NOW-30*${H},marking:{correct:1,wrong:0,blank:0},seconds:600});`);
  phone(`state.scheduledMocks.push({id:'sm_race',name:'Race',questionIds:['q5'],at:NOW-2*${H},createdAt:NOW-30*${H},marking:{correct:1,wrong:0,blank:0},seconds:600,takenTestId:'t_race'});state.tests.push({id:'t_race',scheduledMockId:'sm_race',correct:1,total:1,createdAt:NOW-${H}});`);
  ipad('dashboard()');assert(ipad("state.tests.some(t=>t.id==='missed_sm_race')"),'iPad recorded a zero');
  pull(ipad,push(phone).filter(e=>e.kind!=='tests'||JSON.parse(e.payload).id==='t_race'));
  ipad('dashboard()');
  assert.strictEqual(ipad("nkSchedStatus(state.scheduledMocks.find(m=>m.id==='sm_race'))"),'taken','the sitting wins over the stale miss');
  assert(!ipad("state.tests.some(t=>t.id==='missed_sm_race')"),'the stale zero is withdrawn');
  assert.strictEqual(ipad("nkSchedTest(state.scheduledMocks.find(m=>m.id==='sm_race')).id"),'t_race');
});

scenario('a sitting without the stamp still beats a stale miss stamp',()=>{
  ipad(`state.scheduledMocks.push({id:'sm_old',name:'Old client',questionIds:['q6'],at:NOW-5*${H},createdAt:NOW-30*${H},marking:{correct:1,wrong:0,blank:0},seconds:600,missedAt:NOW-4*${H}});state.tests.push({id:'missed_sm_old',scheduledMockId:'sm_old',missed:true,correct:0,total:1,createdAt:NOW-4*${H}},{id:'exam_x',scheduledMockId:'sm_old',correct:1,total:1,createdAt:NOW-4.5*${H}});`);
  ipad('dashboard()');
  assert.strictEqual(ipad("nkSchedStatus(state.scheduledMocks.find(m=>m.id==='sm_old'))"),'taken');
  assert(!ipad("state.tests.some(t=>t.id==='missed_sm_old')"),'the stale zero is withdrawn');
});

scenario('unsafe or malformed bookings are refused',()=>{
  const n=ipad('state.scheduledMocks.length');
  pull(ipad,[{kind:'scheduledMocks',entityId:"x');alert('",ownerDevice:'evil',updatedAt:NOW,deleted:false,payload:JSON.stringify({id:"x');alert('",questionIds:['q1'],at:NOW}),schemaVersion:1},
    {kind:'scheduledMocks',entityId:'bad',ownerDevice:'evil',updatedAt:NOW,deleted:false,payload:JSON.stringify({id:'bad',questionIds:[],at:NOW}),schemaVersion:1},
    {kind:'scheduledMocks',entityId:'sm_1',ownerDevice:'evil',updatedAt:NOW+1,deleted:true,payload:'',schemaVersion:1}]);
  assert.strictEqual(ipad('state.scheduledMocks.length'),n,'nothing added, and a tombstone never deletes a booking (bookings cannot be cancelled)');
});

scenario('a scheduled mock still refuses Abandon',()=>{
  ipad("state.activeSession={id:'s',mode:'exam',scheduledMockId:'sm_1',questionIds:['q1']};");
  assert.strictEqual(ipad('nkAbandonTimedTest()'),false);
  ipad("state.activeSession={id:'s2',mode:'exam',questionIds:['q1']};");
  assert.strictEqual(ipad('nkAbandonTimedTest()'),'abandoned','ordinary tests keep Abandon');
  ipad('state.activeSession=null');
});

scenario('booking-sheet time is read as local time without engine-specific Date parsing',()=>{
  const want=ipad('new Date(2026,10,18,10,0,0,0).getTime()');
  assert.strictEqual(ipad("nkSchedParseLocal('2026-11-18T10:00')"),want);
  assert.strictEqual(ipad("nkSchedParseLocal('2026-11-18 10:00')"),want,'the space form WebKit rejects in new Date() also works');
  assert.strictEqual(ipad("nkSchedParseLocal('2026-11-18T10:00:00')"),want);
  assert(ipad("Number.isNaN(nkSchedParseLocal(''))&&Number.isNaN(nkSchedParseLocal('2026-02-31T10:00'))&&Number.isNaN(nkSchedParseLocal('soon'))"));
});

console.log('SCHEDULED_MOCKS_SYNC_OK '+results.length);results.forEach(r=>console.log('  ok · '+r));
'''


def run(script: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "scheduled-mocks-sync-test.js"
        path.write_text(script, encoding="utf-8")
        result = subprocess.run(["node", str(path)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
        return result.stdout.strip()


def test_install_contract() -> None:
    page = app_page()
    assert page.count("NK_SCHEDULED_MOCKS_V1_START") == 1 and page.count("NK_CROSS_DEVICE_SYNC_V1_START") == 1
    sync = SYNC.read_text(encoding="utf-8")
    assert "NK_SYNC_KINDS.push('scheduledMocks')" in sync
    assert "nkEnvelope('scheduledMocks'" in sync and "nkSchedMergeEntry(payload)" in sync
    assert "'notStudied','scheduledMocks'].includes(remote.kind)" in sync, "every device's copy merges (no last-writer-wins)"
    sched = SCHED.read_text(encoding="utf-8")
    assert "new Date(input" not in sched, "booking times go through nkSchedParseLocal"
    print("SCHEDULED_MOCKS_INSTALL_OK")


def main() -> None:
    src = PRELUDE + SYNC.read_text(encoding="utf-8") + "\n" + SCHED.read_text(encoding="utf-8")
    print(run(SCENARIO % {"src": json.dumps(src)}))
    test_install_contract()


if __name__ == "__main__":
    main()
