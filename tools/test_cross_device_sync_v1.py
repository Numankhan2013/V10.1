#!/usr/bin/env python3
"""Behavior tests for merge safety and PWA/sync source contracts."""

from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/cross_device_sync_core.js"
STORAGE_CORE = ROOT / "tools/durable_persistence_core.js"


def test_durable_persistence() -> None:
    harness = r'''
const assert=require('assert');
const data={};let failKey='';
const adapter={getItem:key=>Object.prototype.hasOwnProperty.call(data,key)?data[key]:null,setItem:(key,value)=>{if(key===failKey)throw new Error('quota');data[key]=String(value);},removeItem:key=>delete data[key]};
const nodes={};
global.window={__NK_STORAGE_ADAPTER:adapter,QB:{}};
global.localStorage=adapter;
global.document={getElementById:id=>nodes[id]||null,createElement:()=>({id:'',className:'',setAttribute(){},querySelector:()=>({textContent:''}),innerHTML:''}),body:{appendChild:node=>{nodes[node.id]=node}}};
const LS_KEY='qbank_state_v1';
const defaultState=()=>({attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,studyStartedAt:null});
''' + STORAGE_CORE.read_text(encoding="utf-8") + r'''
const valid={...defaultState(),savedMocks:[{id:'saved-mock',name:'Biochemistry 01',questionIds:['q1','q2'],createdAt:6,updatedAt:7}],stateSchemaVersion:2,stateRevision:7,bookmarks:{q1:{addedAt:1}},questionNotes:{q1:{text:'My clue',updatedAt:7,deleted:false}}};
data[NK_STATE_LKG_KEY]=JSON.stringify(valid);data[LS_KEY]='{broken';
let recovered=nkDurableLoadState();
assert(recovered.savedMocks[0].name==='Biochemistry 01'&&recovered.savedMocks[0].questionIds.join(',')==='q1,q2','named exact mocks must survive snapshot recovery');
assert(recovered.stateRevision===7&&recovered.bookmarks.q1&&recovered.questionNotes.q1.text==='My clue','corrupt primary must recover notes from LKG');
assert(nkStorageBootNotice.includes('last valid snapshot'),'recovery must be visible');
const pending={...valid,stateRevision:8,bookmarks:{q2:{addedAt:2}}};data[NK_STATE_PENDING_KEY]=JSON.stringify(pending);
recovered=nkDurableLoadState();assert(recovered.stateRevision===8&&recovered.bookmarks.q2,'interrupted higher revision must recover');
let state={...recovered,activeSession:{id:'practice-1',mode:'practice',title:'Topic',questionIds:['q1','q2'],sessionQuestionIds:['q1','q2'],index:1,answers:{q1:2},submitted:{q1:true},questionTimes:{q1:50},pendingRating:{q1:{rating:3}},startedAt:10,lifecycle:'active',practiceContext:{subject:'Anatomy',bank:'Marrow',topicId:'t1',title:'Topic'}}};
assert(nkDurablePersist(state,'test save'),'valid state must save');
assert(state.normalPracticeCheckpoint.sessionId==='practice-1','normal Practice checkpoint missing');
assert.deepStrictEqual(state.normalPracticeCheckpoints.map(x=>x.sessionId),['practice-1'],'legacy single checkpoint must migrate into the sessions collection');
assert.deepStrictEqual(state.normalPracticeCheckpoint.sessionQuestionIds,['q1','q2']);
assert(state.normalPracticeCheckpoint.position.index===1&&state.normalPracticeCheckpoint.answers.q1===2&&state.normalPracticeCheckpoint.submitted.q1,'checkpoint progress missing');
assert(state.normalPracticeCheckpoint.pendingFsrsRatings.q1.rating===3,'pending FSRS rating missing');
assert(!Object.hasOwn(state.normalPracticeCheckpoint.context,'originRoute'),'ordinary chapter checkpoints gain no navigation field');
const hintSession={...state.activeSession,originRoute:'question-search'};
const hintCheckpoint=nkCheckpointFromSession(hintSession,state.normalPracticeCheckpoint,'paused');
assert(hintCheckpoint.context.originRoute==='question-search');
const hintRecovery=nkNormalizeCheckpoint(JSON.parse(JSON.stringify(hintCheckpoint)));
assert(hintRecovery.context.originRoute==='question-search','return hint must survive durable normalization');
assert.deepStrictEqual(hintRecovery.sessionQuestionIds,state.normalPracticeCheckpoint.sessionQuestionIds);
assert.deepStrictEqual(hintRecovery.answers,state.normalPracticeCheckpoint.answers);
assert.deepStrictEqual(hintRecovery.pendingFsrsRatings,state.normalPracticeCheckpoint.pendingFsrsRatings);

const legacyOnly={...defaultState(),normalPracticeCheckpoint:{...state.normalPracticeCheckpoint,answers:{q1:2},submitted:{q1:true},pendingFsrsRatings:{q1:{rating:3}}}};
const migrated=nkNormalizeState(legacyOnly);
assert.deepStrictEqual(migrated.normalPracticeCheckpoints.map(x=>x.sessionId),['practice-1'],'legacy-only checkpoint must migrate by identity');
assert(migrated.normalPracticeCheckpoints[0].answers.q1===2&&migrated.normalPracticeCheckpoints[0].pendingFsrsRatings.q1.rating===3,'migration must keep answers and pending recall');
const newerAlias={...migrated.normalPracticeCheckpoint,updatedAt:migrated.normalPracticeCheckpoint.updatedAt+1,answers:{q1:4}};
assert(nkNormalizeState({...migrated,normalPracticeCheckpoint:newerAlias}).normalPracticeCheckpoints[0].answers.q1===4,'newer legacy alias must not be discarded when its ID already exists');
const terminalRecords=Array.from({length:101},(_,i)=>({...migrated.normalPracticeCheckpoint,sessionId:`old-${i}`,lifecycle:'discarded',updatedAt:i+1}));
assert(nkNormalizePracticeCheckpoints(terminalRecords,null).length===101,'terminal sync tombstones must survive beyond 100 sessions');
const before=state.stateRevision;failKey=LS_KEY;state.bookmarks.q3={addedAt:3};
assert(nkDurablePersist(state,'quota simulation')===false,'quota failure must be reported');
assert(state.stateRevision===before,'failed writes must not claim a new revision');
failKey='';
const primaryBeforeInterrupted=data[LS_KEY];failKey=NK_STATE_LKG_KEY;state.bookmarks.q4={addedAt:4};
assert(nkDurablePersist(state,'interrupted snapshot')===false,'interrupted snapshot write must fail closed');
assert(data[LS_KEY]===primaryBeforeInterrupted&&!data[NK_STATE_PENDING_KEY],'failed transaction must restore the old primary and remove its journal');
failKey='';
assert.throws(()=>nkNormalizeState({...valid,stateSchemaVersion:99}),/unsupported state schema/);
state.activeSession={id:'exam',mode:'exam',questionIds:['q1'],startedAt:100};assert(nkDurablePersist(state,'suspend normal Practice'));
assert(state.normalPracticeCheckpoint.lifecycle==='suspended','special session must suspend, not replace, normal Practice');
for(const title of ['Bookmarked Questions','Wrong Questions','FSRS Review']){
  state.activeSession={id:'special-'+title,mode:'practice',context:'normal',title,questionIds:['q2'],answers:{q2:1},submitted:{q2:true},index:0};
  assert(nkDurablePersist(state,'special-mode isolation'));
  assert(state.normalPracticeCheckpoint.sessionId==='practice-1','default normal context must not hide a special-mode title');
  assert.deepStrictEqual(state.normalPracticeCheckpoint.answers,{q1:2});
}
const prior=state.normalPracticeCheckpoint;state.activeSession={id:'practice-2',mode:'practice',title:'Next Topic',questionIds:['q2'],sessionQuestionIds:['q2'],index:0,answers:{},submitted:{},questionTimes:{},startedAt:20,lifecycle:'active',practiceContext:{subject:'Anatomy',bank:'Marrow',topicId:'t2',title:'Next Topic'}};
const realNow=Date.now,frozenNow=realNow();Date.now=()=>frozenNow;
assert(nkDurablePersist(state,'second paused chapter'));
Date.now=realNow;
assert.deepStrictEqual(state.normalPracticeCheckpoints.map(x=>x.sessionId).sort(),['practice-1','practice-2']);
assert(state.normalPracticeCheckpoint.sessionId==='practice-2'&&prior.sessionId==='practice-1','latest alias and older saved checkpoint must coexist');
const firstCopy=JSON.stringify(state.normalPracticeCheckpoints.find(x=>x.sessionId==='practice-1'));
state.activeSession={id:'module',mode:'practice',studyModuleId:'saved-set',title:'Saved set',questionIds:['q2'],answers:{},submitted:{}};
assert(nkDurablePersist(state,'module isolation'));
assert(JSON.stringify(state.normalPracticeCheckpoints.find(x=>x.sessionId==='practice-1'))===firstCopy,'saved study set must not mutate an unrelated paused Practice');
state.activeSession=null;
assert(nkDurablePersist(state,'restart snapshot'));
const restarted=nkDurableLoadState();
assert(restarted.normalPracticeCheckpoints.length===2&&restarted.normalPracticeCheckpoints.some(x=>x.sessionId==='practice-1'&&x.answers.q1===2),'restart must retain both independent checkpoints');
const pausedCopy=JSON.stringify(state.normalPracticeCheckpoints);
let elapsedCalls=0;global.savePracticeElapsed=()=>{elapsedCalls++;};global.saveState=()=>nkDurablePersist(state,'pagehide');
state.activeSession={id:'practice-2',mode:'practice',title:'Next Topic',questionIds:['q2'],sessionQuestionIds:['q2'],index:0,answers:{},submitted:{},questionTimes:{},startedAt:20,lifecycle:'paused'};
assert(nkFlushLifecycleState());
assert(elapsedCalls===0&&JSON.stringify(state.normalPracticeCheckpoints)===pausedCopy,'pagehide must not accrue time or rewrite an already paused checkpoint');
const unrelated=JSON.stringify(state.normalPracticeCheckpoints);
state.activeSession={id:'practice-3',mode:'practice',title:'Third Topic',questionIds:['q1'],sessionQuestionIds:['q1'],index:0,answers:{q1:1},submitted:{q1:true},questionTimes:{q1:5},startedAt:30,lifecycle:'active',practiceContext:{subject:'Anatomy',bank:'Marrow',topicId:'t3',title:'Third Topic'}};
assert(nkFlushLifecycleState());
assert(elapsedCalls===1&&state.normalPracticeCheckpoints.length===3,'pagehide must persist only the intended live Practice');
assert(state.normalPracticeCheckpoints.filter(x=>x.sessionId!=='practice-3').every(x=>unrelated.includes(JSON.stringify(x))),'pagehide must retain unrelated paused checkpoints byte for byte');
console.log('DURABLE_PERSISTENCE_BEHAVIOR_OK');
'''
    with tempfile.TemporaryDirectory() as directory:
        script = Path(directory) / "durable-test.js"
        script.write_text(harness, encoding="utf-8")
        subprocess.run(["node", str(script)], check=True)


def main() -> None:
    test_durable_persistence()
    core = CORE.read_text(encoding="utf-8")
    harness = r'''
const assert=(condition,message)=>{if(!condition)throw new Error(message);};
state={attempts:{q1:[{id:'a1',at:10,correct:false,selected:1,timeSpent:5}]},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,fsrsReviewEligible:{}};
nkApplyCloudEnvelope({kind:'attempts',entityId:'a2',ownerDevice:'ipad',updatedAt:20,deleted:false,payload:JSON.stringify({qid:'q1',attempt:{id:'a2',at:20,correct:true,selected:2,timeSpent:7}}),schemaVersion:1});
assert(state.attempts.q1.length===2,'immutable attempts must merge');
const remoteMock={id:'mock-sync',name:'Renal 01',questionIds:['q1','q2'],createdAt:1,updatedAt:21};
nkApplyCloudEnvelope({kind:'savedMocks',entityId:remoteMock.id,ownerDevice:'ipad',updatedAt:21,deleted:false,payload:JSON.stringify(remoteMock),schemaVersion:1});
assert(state.savedMocks.length===1&&state.savedMocks[0].questionIds.join(',')==='q1,q2','mock sync must preserve the exact ordered set and name');
nkApplyCloudEnvelope({kind:'savedMocks',entityId:remoteMock.id,ownerDevice:'android',updatedAt:23,deleted:true,payload:'',schemaVersion:1});
nkApplyCloudEnvelope({kind:'savedMocks',entityId:remoteMock.id,ownerDevice:'ipad',updatedAt:22,deleted:false,payload:JSON.stringify(remoteMock),schemaVersion:1});
assert(state.savedMocks.length===0,'a stale device must not resurrect a removed mock');

nkApplyCloudEnvelope({kind:'attempts',entityId:'a2',ownerDevice:'ipad',updatedAt:20,deleted:false,payload:JSON.stringify({qid:'q1',attempt:{id:'a2',at:20,correct:true,selected:2,timeSpent:7}}),schemaVersion:1});
assert(state.attempts.q1.length===2,'duplicate attempt must be deduplicated');
const ratingEvent={id:'rating-a2',isRatingRevision:true,ratingOf:'a2',rating:2,at:25,revisedAt:25};
const ratingEnvelope={kind:'attempts',entityId:ratingEvent.id,ownerDevice:'ipad',updatedAt:25,deleted:false,payload:JSON.stringify({qid:'q1',attempt:ratingEvent}),schemaVersion:1};
nkApplyCloudEnvelope(ratingEnvelope);nkApplyCloudEnvelope(ratingEnvelope);
assert(state.attempts.q1.length===2&&state.fsrsRatingRevisions.q1.length===1,'rating events sync idempotently without entering answer counts');
nkApplyCloudEnvelope({kind:'bookmarks',entityId:'q1',ownerDevice:'android',updatedAt:100,deleted:false,payload:JSON.stringify({qid:'q1',active:true}),schemaVersion:1});
nkApplyCloudEnvelope({kind:'bookmarks',entityId:'q1',ownerDevice:'ipad',updatedAt:90,deleted:true,payload:'',schemaVersion:1});
assert(Boolean(state.bookmarks.q1),'older bookmark tombstone must not erase newer state');
nkApplyCloudEnvelope({kind:'bookmarks',entityId:'q1',ownerDevice:'ipad',updatedAt:110,deleted:true,payload:'',schemaVersion:1});
assert(!state.bookmarks.q1,'newer bookmark tombstone must win');
nkApplyCloudEnvelope({kind:'notes',entityId:'q1',ownerDevice:'android',updatedAt:120,deleted:false,payload:JSON.stringify({text:'Recall clue',deleted:false}),schemaVersion:1});
assert(state.questionNotes.q1.text==='Recall clue','question note must sync by question ID');
nkApplyCloudEnvelope({kind:'notes',entityId:'q1',ownerDevice:'ipad',updatedAt:121,deleted:false,payload:JSON.stringify({text:'',deleted:true}),schemaVersion:1});
assert(state.questionNotes.q1.deleted,'newer note removal must sync as a tombstone');
nkApplyCloudEnvelope({kind:'notes',entityId:'q1',ownerDevice:'android',updatedAt:120,deleted:false,payload:JSON.stringify({text:'Recall clue',deleted:false}),schemaVersion:1});
assert(state.questionNotes.q1.deleted,'older note copy must not resurrect a removed note');
nkApplyCloudEnvelope({kind:'sessions',entityId:'active',ownerDevice:'android',updatedAt:200,deleted:false,payload:JSON.stringify({id:'new',index:4}),schemaVersion:1});
nkApplyCloudEnvelope({kind:'sessions',entityId:'active',ownerDevice:'ipad',updatedAt:150,deleted:false,payload:JSON.stringify({id:'old',index:1}),schemaVersion:1});
assert(state.activeSession.id==='new'&&state.activeSession.index===4,'opening an older device must not replace newer session progress');
const checkpoint=(id,ids,answers,submitted,updates,lifecycle='paused',updatedAt=200)=>({version:1,sessionId:id,sessionQuestionIds:ids,membershipHash:ids.join('\u001f'),context:{subject:'Anatomy',bank:'Marrow',topicId:'t1',title:'Topic'},position:{index:0,currentQuestionId:ids[0]},answers,submitted,questionTimes:{},pendingFsrsRatings:{},questionUpdates:updates,lifecycle,updatedAt});
const pendingOld=checkpoint('rating-session',['q1'],{q1:2},{q1:true},{q1:{revision:1,updatedAt:20}},'active',20);
pendingOld.pendingFsrsRatings.q1={id:'a2',selected:2};
const committed=checkpoint('rating-session',['q1'],{q1:2},{q1:true},{q1:{revision:2,updatedAt:30}},'active',30);
state.normalPracticeCheckpoints=[committed];state.normalPracticeCheckpoint=committed;
nkMergePracticeCheckpoint(pendingOld);
assert(!state.normalPracticeCheckpoint.pendingFsrsRatings.q1,'older pending rating cannot survive a newer explicit removal');
const pendingNew={...pendingOld,questionUpdates:{q1:{revision:3,updatedAt:40}},updatedAt:40};
nkMergePracticeCheckpoint(pendingNew);
assert(!state.normalPracticeCheckpoint.pendingFsrsRatings.q1,'even a newer stale checkpoint cannot resurrect an already committed attempt ID');
state.normalPracticeCheckpoints=[];state.normalPracticeCheckpoint=null;
state.activeSession=null;
state.normalPracticeCheckpoint=checkpoint('same',['q1','q2'],{q1:1},{q1:true},{q1:{revision:1,updatedAt:100}},'paused',200);
nkApplyCloudEnvelope({kind:'practiceSessions',entityId:'normal',ownerDevice:'ipad',updatedAt:210,deleted:false,payload:JSON.stringify(checkpoint('same',['q1','q2'],{q2:2},{q2:true},{q2:{revision:1,updatedAt:210}},'active',210)),schemaVersion:1});
assert(state.normalPracticeCheckpoint.submitted.q1&&state.normalPracticeCheckpoint.submitted.q2,'concurrent same-session answers must union');
assert(state.normalPracticeCheckpoint.answers.q1===1&&state.normalPracticeCheckpoint.answers.q2===2,'per-question revisions must preserve both devices');
nkApplyCloudEnvelope({kind:'practiceSessions',entityId:'normal',ownerDevice:'android',updatedAt:220,deleted:false,payload:JSON.stringify(checkpoint('same',['q1','q2'],{}, {},{},'submitted',220)),schemaVersion:1});
nkApplyCloudEnvelope({kind:'practiceSessions',entityId:'normal',ownerDevice:'ipad',updatedAt:230,deleted:false,payload:JSON.stringify(checkpoint('same',['q1','q2'],{}, {},{},'active',230)),schemaVersion:1});
assert(state.normalPracticeCheckpoint.lifecycle==='submitted','terminal Practice state must not regress');
nkApplyCloudEnvelope({kind:'practiceSessions',entityId:'normal',ownerDevice:'ipad',updatedAt:240,deleted:false,payload:JSON.stringify(checkpoint('different',['q1'],{}, {},{},'paused',240)),schemaVersion:1});
assert(!state.normalPracticeConflict&&state.normalPracticeCheckpoints.some(cp=>cp.sessionId==='same')&&state.normalPracticeCheckpoints.some(cp=>cp.sessionId==='different'),'independent paused Practice sessions must merge without conflicting');
state.normalPracticeCheckpoints=[checkpoint('A',['q1'],{q1:1},{q1:true},{q1:{revision:1,updatedAt:10}},'paused',10),checkpoint('B',['q2'],{q2:2},{q2:true},{q2:{revision:1,updatedAt:20}},'paused',20),checkpoint('C',['q3'],{q3:3},{q3:true},{q3:{revision:1,updatedAt:30}},'paused',30)];
state.normalPracticeCheckpoint=state.normalPracticeCheckpoints[2];
const aBefore=JSON.stringify(state.normalPracticeCheckpoints[0]),cBefore=JSON.stringify(state.normalPracticeCheckpoints[2]);
nkApplyCloudEnvelope({kind:'practiceSessions',entityId:'B',ownerDevice:'ipad',updatedAt:40,deleted:false,payload:JSON.stringify(checkpoint('B',['q2'],{q2:4},{q2:true},{q2:{revision:2,updatedAt:40}},'paused',40)),schemaVersion:1});
assert(state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='B').answers.q2===4,'remote B progress must merge by session ID');
assert(JSON.stringify(state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='A'))===aBefore&&JSON.stringify(state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='C'))===cBefore,'remote B must leave A and C intact');
nkApplyCloudEnvelope({kind:'practiceSessions',entityId:'A',ownerDevice:'ipad',updatedAt:50,deleted:false,payload:JSON.stringify(checkpoint('A',['q1'],{}, {},{},'submitted',50)),schemaVersion:1});
assert(state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='A').lifecycle==='submitted'&&state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='B').answers.q2===4&&JSON.stringify(state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='C'))===cBefore,'completion of A must leave B and C intact');
const bMembership=state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='B');
const forged=checkpoint('B',['q3'],{}, {},{},'paused',60);forged.membershipHash=bMembership.membershipHash;
nkApplyCloudEnvelope({kind:'practiceSessions',entityId:'B',ownerDevice:'ipad',updatedAt:60,deleted:false,payload:JSON.stringify(forged),schemaVersion:1});
assert(state.normalPracticeConflict?.type==='membership-mismatch'&&state.normalPracticeCheckpoints.find(cp=>cp.sessionId==='B').answers.q2===4,'ordered membership must be compared exactly, even if a hash agrees');
delete state.normalPracticeConflict;
state.studyModules=[{id:'m1',syncEpoch:'e1',submitted:{q1:true},answers:{q1:1},completedQuestionIds:['q1'],questionTimes:{q1:10}}];
nkApplyCloudEnvelope({kind:'modules',entityId:'m1',ownerDevice:'ipad',updatedAt:300,deleted:false,payload:JSON.stringify({id:'m1',syncEpoch:'e1',submitted:{q2:true},answers:{q2:2},completedQuestionIds:['q2'],questionTimes:{q2:20}}),schemaVersion:1});
assert(state.studyModules[0].submitted.q1&&state.studyModules[0].submitted.q2,'same-generation module progress must merge across devices');
state.fsrsReviewEligible={qLocal:{reason:'skipped',at:310}};
nkApplyCloudEnvelope({kind:'preferences',entityId:'main',ownerDevice:'ipad',updatedAt:400,deleted:false,payload:JSON.stringify({fsrsReviewEligible:{qRemote:{reason:'skipped',at:390}}}),schemaVersion:1});
assert(state.fsrsReviewEligible.qLocal&&state.fsrsReviewEligible.qRemote,'FSRS skipped-review eligibility must union across devices instead of replacing local entries');
nkApplyCloudEnvelope({kind:'preferences',entityId:'main',ownerDevice:'android',updatedAt:410,deleted:false,payload:JSON.stringify({fsrsReviewEligible:{qRemote:{reason:'skipped',at:405},qIgnored:{reason:'new',at:405}}}),schemaVersion:1});
assert(state.fsrsReviewEligible.qRemote.at===405&&!state.fsrsReviewEligible.qIgnored,'skip eligibility merge must keep newest skip timestamp and reject non-review-only reasons');
nkRebuildReviews();
assert(state.reviews.q1.attempts===2&&state.reviews.q1.streak===1,'review schedule must derive from merged attempts');
const encoded=nkFirestoreDocument(nkEnvelope('tests','t1',{id:'t1'},300),'/x');
const decoded=nkDecodeDocument(encoded);
assert(decoded.kind==='tests'&&decoded.entityId==='t1'&&decoded.updatedAt===300,'Firestore envelope round trip failed');
const jwtPayload=Buffer.from(JSON.stringify({aud:'nk-qbank',iss:'https://securetoken.google.com/nk-qbank'})).toString('base64url');
assert(nkProjectIdFromToken(`header.${jwtPayload}.signature`)==='nk-qbank','Firebase project ID must come from authenticated token claims');
async function testRequests(){
  nkAuth={uid:'test-user'};
  nkSyncMeta.outbox={};
  const original=nkEnvelope('bookmarks','q1',{active:true},100);
  nkSyncMeta.outbox['bookmarks/q1']=original;
  let release;
  globalThis.fetch=()=>new Promise(resolve=>release=()=>resolve({ok:true,text:async()=>'{}'}));
  const upload=nkPushOutbox('test-token');
  const newer=nkEnvelope('bookmarks','q1',null,200,true);
  nkSyncMeta.outbox['bookmarks/q1']=newer;
  release();await upload;
  assert(nkSyncMeta.outbox['bookmarks/q1']===newer,'in-flight upload must retain a newer local revision');
  globalThis.fetch=async()=>({ok:true,text:async()=>'{}'});
  await nkPushOutbox('test-token');
  assert(!nkSyncMeta.outbox['bookmarks/q1'],'acknowledged revision must leave outbox');
  nkSyncMeta.cursors.attempts=999999;
  globalThis.fetch=async(url,options)=>{
    assert(!JSON.parse(options.body).structuredQuery.where,'client timestamps must not hide late offline uploads');
    return {ok:true,text:async()=>JSON.stringify([{document:nkFirestoreDocument(nkEnvelope('attempts','offline',{qid:'q1',attempt:{id:'offline',at:1}},1))}])};
  };
  const late=await nkPullKind('attempts','test-token');
  assert(late.length===1&&late[0].updatedAt===1,'old offline revisions must be downloaded');
  globalThis.fetch=async()=>({ok:false,status:403,text:async()=>JSON.stringify({error:{message:'Forbidden',details:[{reason:'API_KEY_HTTP_REFERRER_BLOCKED'}]}})});
  nkSyncMeta.outbox['bookmarks/q1']=newer;
  try{await nkPushOutbox('test-token');throw new Error('expected HTTP failure');}
  catch(error){assert(error.message.includes('bookmarks PATCH')&&error.message.includes('HTTP 403')&&error.message.includes('API_KEY_HTTP_REFERRER_BLOCKED'),'diagnostics must preserve request and backend reason');}
  assert(nkSyncMeta.outbox['bookmarks/q1']===newer,'failed upload must remain pending');
  try{await nkPullKind('attempts','test-token');throw new Error('expected download failure');}
  catch(error){assert(error.message.includes('attempts runQuery')&&error.message.includes('HTTP 403'),'download diagnostic must identify collection and request');}
  const longError='download: '+('detail '.repeat(40))+'API_KEY_HTTP_REFERRER_BLOCKED';
  nkSyncMeta.lastError=longError;
  window.NK_QBANK_FIREBASE_CONFIG={apiKey:'public-test-key',projectId:'test-project'};
  assert(nkCloudAccountCard().includes(longError),'expanded diagnostics must preserve the untruncated backend reason');

  nkSyncMeta.outbox['bookmarks/q2']=nkEnvelope('bookmarks','q2',{active:true},201);
  let releaseSuccess,settled=false;
  globalThis.fetch=async url=>{
    if(url.endsWith('--q1'))return {ok:false,status:403,text:async()=>'{}'};
    return new Promise(resolve=>releaseSuccess=()=>resolve({ok:true,text:async()=>'{}'}));
  };
  const partial=nkPushOutbox('test-token').catch(()=>{settled=true;});
  await new Promise(resolve=>setImmediate(resolve));
  assert(!settled,'failed batch must wait for remaining in-flight writes before retry');
  releaseSuccess();await partial;
  assert(nkSyncMeta.outbox['bookmarks/q1']&&!nkSyncMeta.outbox['bookmarks/q2'],'partial batch must retain failures and acknowledge successes');
  // Reproduce the original echo loop: legacy remote preferences without review eligibility must not create an echo.
  state={attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null};
  nkSyncMeta={deviceId:'local',outbox:{},localHashes:{},known:{},winners:{},cursors:{}};
  nkAuth={uid:'user',idToken:'valid-token',refreshToken:'refresh',expiresAt:Date.now()+3600000};
  let scheduled=0,renders=0,writes=0;
  globalThis.setTimeout=()=>{scheduled++;return 1;};globalThis.clearTimeout=()=>{};
  render=()=>{renders++;};
  SUBJECT_BY_NAME.Anatomy={};
  applySubject=value=>{activeSubject=value;nkScheduleCloudSync();};
  const remote=nkEnvelope('preferences','main',{activeSubject:'Anatomy',studyStartedAt:null,fsrsPreferences:null},Date.now()+10000);
  remote.ownerDevice='remote';
  globalThis.fetch=async(url,options={})=>{
    if(String(url).includes('/control/accountReset'))return {ok:false,status:404,text:async()=>JSON.stringify({error:{message:'NOT_FOUND'}})};
    if(options.method==='PATCH'){writes++;return {ok:true,text:async()=>'{}'};}
    const kind=JSON.parse(options.body).structuredQuery.from[0].collectionId;
    return {ok:true,text:async()=>JSON.stringify(kind==='preferences'?[{document:nkFirestoreDocument(remote)}]:[])};
  };
  await nkCloudSync(false,true);
  assert(activeSubject==='Anatomy','remote preferences must still merge');
  scheduled=0;renders=0;writes=0;
  await nkCloudSync(false,true);await nkCloudSync(false,true);nkCaptureCloudChanges();
  assert(scheduled===0,'unchanged remote sync must never schedule another sync');
  assert(renders===0,'unchanged background sync must not rebuild the screen');
  assert(writes===0,'remote preferences must not echo back as local writes');
  state.normalPracticeCheckpoints=[checkpoint('saved-one',['q1'],{}, {},{},'paused',500),checkpoint('saved-two',['q2'],{}, {},{},'paused',501)];state.normalPracticeCheckpoint=state.normalPracticeCheckpoints[1];nkCaptureCloudChanges();
  assert(nkSyncMeta.outbox['practiceSessions/saved-one']&&nkSyncMeta.outbox['practiceSessions/saved-two']&&nkSyncMeta.outbox['practiceSessions/normal'],'each paused Practice session must sync under its own ID with the legacy latest-session alias');
  state.normalPracticeCheckpoints=[];state.normalPracticeCheckpoint=null;nkSyncMeta.outbox={};nkSyncMeta.localHashes={};nkCloudRevision=0;scheduled=0;
  state.bookmarks.q9={addedAt:Date.now()};nkCaptureCloudChanges();
  assert(scheduled===1&&nkSyncMeta.outbox['bookmarks/q9'],'real local edits must still schedule upload');
  const resetUser='reset-user',resetDocName=`projects/test-project/databases/(default)/documents/users/${resetUser}/attempts/android--old-attempt`;
  let resetMarker=null,remoteAttempt=nkFirestoreDocument(nkEnvelope('attempts','old-attempt',{qid:'q1',attempt:{id:'old-attempt'}},10),resetDocName),resetLists=[];
  nkAuth={uid:resetUser,idToken:'token',refreshToken:'refresh',expiresAt:Date.now()+3600000};nkSyncMeta={deviceId:'android',boundUid:resetUser,accountGeneration:'legacy',outbox:{'attempts/local':nkEnvelope('attempts','local',{qid:'q1'},20)},localHashes:{x:'y'},known:{bookmarks:['q1']},winners:{x:{}},cursors:{attempts:10}};
  state={attempts:{q1:[{id:'old-attempt',at:10}]},bookmarks:{q1:{addedAt:1}},reviews:{q1:{attempts:1}},tests:[{id:'test'}],studyModules:[{id:'module'}],activeSession:{id:'session'}};
  localStorage.setItem('qbank_state_pre_cloud_v1','backup');
  globalThis.fetch=async(url,options={})=>{
    if(String(url).includes('/control/accountReset')){
      if(options.method==='PATCH'){resetMarker=nkDecodeDocument(JSON.parse(options.body));return {ok:true,text:async()=>'{}'};}
      if(!resetMarker)return {ok:false,status:404,text:async()=>JSON.stringify({error:{message:'NOT_FOUND'}})};
      return {ok:true,text:async()=>JSON.stringify(nkFirestoreDocument(resetMarker,`projects/test-project/databases/(default)/documents/users/${resetUser}/control/accountReset`))};
    }
    if(options.method==='PATCH'){
      assert(String(url).includes('/attempts/android--old-attempt'),'reset must patch the existing document path');
      remoteAttempt=JSON.parse(options.body);return {ok:true,text:async()=>'{}'};
    }
    if(String(url).includes('/users/reset-user/')){const kind=String(url).split('/users/reset-user/')[1].split('?')[0];resetLists.push(kind);return {ok:true,text:async()=>JSON.stringify(kind==='attempts'?{documents:[remoteAttempt]}:{})};}
    throw new Error(`unexpected reset request ${url}`);
  };
  await nkCompleteRemoteReset('test-token','generation-test');
  assert(JSON.parse(resetMarker.payload).phase==='complete'&&JSON.parse(resetMarker.payload).generation==='generation-test','account reset marker must be finalized with the new generation');
  assert(remoteAttempt.fields.deleted.booleanValue===true&&remoteAttempt.fields.payload.stringValue===''&&remoteAttempt.fields.entityId.stringValue==='old-attempt','reset must clear the remote progress payload while retaining its tombstone');
  assert(NK_SYNC_KINDS.every(kind=>resetLists.includes(kind)),'reset must inspect every synchronized progress collection');
  assert(Object.keys(state.attempts).length===0&&state.tests.length===0&&state.studyModules.length===0&&!state.activeSession,'account reset must clear local learning state');
  assert(nkSyncMeta.accountGeneration==='generation-test'&&!Object.keys(nkSyncMeta.outbox).length&&!Object.keys(nkSyncMeta.localHashes).length,'account reset must clear queued local revisions and advance the generation');
  assert(!localStorage.getItem('qbank_state_pre_cloud_v1')&&!localStorage.getItem('qbank_account_reset_pending_v1'),'account reset must clear its local backup and pending flag');
  nkSyncMeta.accountGeneration='legacy';state.attempts={q1:[{id:'stale',at:1}]};
  await nkEnsureAccountGeneration('test-token');
  assert(nkSyncMeta.accountGeneration==='generation-test'&&!Object.keys(state.attempts).length,'a returning older device must clear stale progress before syncing');
  // A signed-out account must keep its own local work, including queued edits.
  state={...defaultState(),bookmarks:{accountA:{addedAt:1}}};
  nkSyncMeta=nkNormalizeSyncMeta({deviceId:'android',boundUid:'account-a',outbox:{'bookmarks/accountA':nkEnvelope('bookmarks','accountA',{active:true},1)},accountGeneration:'generation-a'});
  nkAuth=null;activeSubject='Anatomy';
  const loginFields={'nk-cloud-email':{value:'second@example.com'},'nk-cloud-password':{value:'password123'}};
  document.getElementById=id=>loginFields[id]||null;document.querySelector=()=>null;
  let loginUid='account-b';
  globalThis.fetch=async()=>({ok:true,text:async()=>JSON.stringify({localId:loginUid,email:'second@example.com',idToken:'token',refreshToken:'refresh',expiresIn:'3600'})});
  nkInitialCloudSync=async()=>{};
  await nkCloudAuthenticate('signin');
  assert(nkAuth?.uid==='account-b'&&!state.bookmarks.accountA&&!nkSyncMeta.outbox['bookmarks/accountA']&&activeSubject==='Biochemistry','second-account sign-in must start with isolated local progress and preferences');
  assert(nkSyncMeta.needsInitialPull,'a newly opened account must download before sending empty singleton state');
  const remoteExam=nkEnvelope('sessions','active',{id:'account-b-exam',mode:'exam',questionIds:['q1'],startedAt:100},100);
  remoteExam.ownerDevice='ipad';let emptySessionSent=false;
  globalThis.fetch=async(url,options={})=>{
    if(String(url).includes('/control/accountReset'))return {ok:false,status:404,text:async()=>JSON.stringify({error:{message:'NOT_FOUND'}})};
    if(options.method==='POST'){
      const kind=JSON.parse(options.body).structuredQuery.from[0].collectionId;
      if(kind==='sessions')emptySessionSent=Boolean(nkSyncMeta.outbox['sessions/active']?.deleted);
      return {ok:true,text:async()=>JSON.stringify(kind==='sessions'?[{document:nkFirestoreDocument(remoteExam,'remote-exam')}]:[])};
    }
    return {ok:true,text:async()=>'{}'};
  };
  await nkCloudSync(true,true);
  assert(!emptySessionSent&&state.activeSession?.id==='account-b-exam'&&!nkSyncMeta.needsInitialPull,'opening the second account must preserve its remote active test');
  globalThis.fetch=async()=>({ok:true,text:async()=>JSON.stringify({localId:loginUid,email:'second@example.com',idToken:'token',refreshToken:'refresh',expiresIn:'3600'})});
  state.bookmarks.accountB={addedAt:2};nkSyncMeta.outbox['bookmarks/accountB']=nkEnvelope('bookmarks','accountB',{active:true},2);
  await nkCloudSignOut();
  loginUid='account-a';await nkCloudAuthenticate('signin');
  assert(nkAuth?.uid==='account-a'&&state.bookmarks.accountA&&!state.bookmarks.accountB&&nkSyncMeta.outbox['bookmarks/accountA']&&!nkSyncMeta.outbox['bookmarks/accountB']&&activeSubject==='Anatomy',`returning to the first account must restore its own local state and unsynced outbox: ${JSON.stringify({uid:nkAuth?.uid,bookmarks:state.bookmarks,outbox:Object.keys(nkSyncMeta.outbox),subject:activeSubject})}`);
  await nkCloudSignOut();loginUid='account-b';await nkCloudAuthenticate('signin');
  assert(nkAuth?.uid==='account-b'&&state.bookmarks.accountB&&!state.bookmarks.accountA&&nkSyncMeta.outbox['bookmarks/accountB'],'returning to the second account must restore only its progress');
  await nkCloudSignOut();
  const originalSetItem=localStorage.setItem;
  localStorage.setItem=(key,value)=>{if(key===nkAccountSnapshotKey('account-b'))throw new Error('quota');return originalSetItem(key,value);};
  loginUid='account-a';await nkCloudAuthenticate('signin');
  assert(!nkAuth&&nkSyncMeta.boundUid==='account-b'&&state.bookmarks.accountB,'snapshot storage failure must leave the signed-out account intact');
  localStorage.setItem=originalSetItem;
  localStorage.setItem(NK_RESET_PENDING_KEY,'unfinished');
  loginUid='account-a';await nkCloudAuthenticate('signin');
  assert(!nkAuth&&nkSyncMeta.boundUid==='account-b'&&state.bookmarks.accountB,'an unfinished account reset must block switching without changing local state');
  loginUid='account-b';await nkCloudAuthenticate('signin');
  assert(nkAuth?.uid==='account-b','the original account must be allowed to sign in and finish an interrupted reset');
  await nkCloudSignOut();
  localStorage.removeItem(NK_RESET_PENDING_KEY);
  localStorage.setItem(NK_ACCOUNT_SWITCH_PENDING_KEY,JSON.stringify({fromUid:'account-b',toUid:'account-a'}));
  state=defaultState();nkSyncMeta=nkNormalizeSyncMeta({deviceId:'android',boundUid:'account-a'});
  nkRecoverAccountSwitch();
  assert(state.bookmarks.accountB&&nkSyncMeta.boundUid==='account-b'&&!localStorage.getItem(NK_ACCOUNT_SWITCH_PENDING_KEY),'interrupted switch must recover the previous account before sign-in');
  nkAuth=null;nkAuthView='signin';window.NK_QBANK_FIREBASE_CONFIG={apiKey:'public-test-key',projectId:'test-project'};
  const signedOutCard=nkCloudAccountCard();
  assert(signedOutCard.includes('Sign in to QBank')&&signedOutCard.includes('Create account')&&!signedOutCard.includes("nkCloudAuthenticate('create')"),'auth card must present one sign-in action and a separate create-account entry');
  const authFields={'nk-cloud-create-email':{value:'new@example.com',checkValidity:()=>true,focus(){}},'nk-cloud-create-password':{value:'strong-password',focus(){}},'nk-cloud-confirm-password':{value:'strong-password',focus(){}}};document.getElementById=id=>authFields[id]||null;document.querySelector=()=>null;
  nkCloudAuthStartCreate();nkCloudAuthNext();assert(nkAuthView==='create-password'&&nkPendingCreateEmail==='new@example.com','create-account flow must advance from email to password');
  globalThis.fetch=async(url,options)=>({ok:true,text:async()=>JSON.stringify({localId:'new-user',email:'new@example.com',idToken:'not-saved',refreshToken:'not-saved',expiresIn:'3600'})});
  await nkCloudAuthenticate('create');
  assert(nkAuthView==='signin'&&nkSignInEmail==='new@example.com'&&!nkAuth&&!localStorage.getItem('qbank_firebase_auth_v1'),'creating an account must return to the sign-in step without auto-signing in');
  console.log('CROSS_DEVICE_SYNC_BEHAVIOR_OK');
}
testRequests().catch(error=>{console.error(error);process.exitCode=1;});
'''
    prelude = r'''
const storage={};
const localStorage={getItem:k=>Object.prototype.hasOwnProperty.call(storage,k)?storage[k]:null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]};
const window={NK_QBANK_FIREBASE_CONFIG:{}};
const navigator={onLine:true};
const location={hostname:'qbank.local'};
const document={querySelector:()=>null,getElementById:()=>null};
const LS_KEY='qbank_state_v1';
let state={};let activeSubject='Biochemistry';
const SUBJECT_BY_NAME={Biochemistry:{}};
function render(){} function showToast(){} function saveState(){return true} function fmtDate(v){return String(v)} function esc(v){return String(v)} function defaultState(){return {attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,questionNotes:{},fsrsReviewEligible:{}}}
function applySubject(v){activeSubject=v}
function nkNormalizeState(v){if(!v||typeof v!=='object'||Array.isArray(v))throw new Error('invalid state');return v}
function nkDurablePersist(v){localStorage.setItem(LS_KEY,JSON.stringify(v));return true}
'''
    with tempfile.TemporaryDirectory() as directory:
        script = Path(directory) / "sync-test.js"
        script.write_text(prelude + "\n" + core + "\n" + harness, encoding="utf-8")
        subprocess.run(["node", str(script)], check=True)

    required = [
        ROOT / "firestore.rules",
        ROOT / "app/src/main/assets/manifest.webmanifest",
        ROOT / "app/src/main/assets/sw.js",
        ROOT / "app/src/main/assets/web_pdf_renderer.mjs",
        ROOT / "tools/build_web_dist.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"Missing cross-device/PWA files: {missing}")
    manifest = json.loads((ROOT / "app/src/main/assets/manifest.webmanifest").read_text(encoding="utf-8"))
    if manifest.get("display") != "standalone" or manifest.get("start_url") != "/#dashboard":
        raise SystemExit("PWA manifest is not installable with the dashboard start route")
    worker = (ROOT / "app/src/main/assets/sw.js").read_text(encoding="utf-8")
    for marker in ("biochemistry_source_solution_map.js", "web_pdf_renderer.mjs", "SKIP_WAITING", "googleapis"):
        if marker not in worker:
            raise SystemExit(f"Service-worker contract missing: {marker}")
    install = worker.split("self.addEventListener('install'", 1)[1].split("self.addEventListener('activate'", 1)[0]
    if "skipWaiting" in install:
        raise SystemExit("PWA installation must wait for an explicit update action")
    transform_source = (ROOT / "tools/apply_cross_device_pwa_v1.py").read_text(encoding="utf-8")
    if "tools/pwa_update_core.js" not in transform_source or "NK_QBANK_VERSION" not in worker:
        raise SystemExit("PWA updates must compare the waiting build with the running page")
    sync_core = CORE.read_text(encoding="utf-8")
    pull_at = sync_core.find("pulled=await nkPullCloud(token)")
    push_at = sync_core.find("pushed=await nkPushOutbox(token)")
    if pull_at < 0 or push_at < 0 or pull_at > push_at:
        raise SystemExit("Synchronization must pull/merge before uploading local revisions")
    if "function nkScheduleCloudSync(){if(!nkAuth)return;nkCaptureCloudChanges();}" not in sync_core:
        raise SystemExit("Local outbox capture must be synchronous with state saves")
    for marker in ("nkResolveFirebaseProjectId", "nkProjectIdFromToken", "nkEnsureAccountGeneration", "nkTombstoneAccountCollections", "nkResetProgress", "NK_RESET_PENDING_KEY", "nkCloudAuthNext", "CREATE ACCOUNT · 2 OF 2", "stage='download'", "HTTP ${response.status}", "method:'PATCH'", "setInterval(nkCloudAutoSync,300000)", "visibilitychange", "fsrsReviewEligible", "nkMergeFsrsReviewEligible", "practiceSessions", "nkMergePracticeCheckpoint", "NK_SYNC_META_LKG_KEY"):
        if marker not in sync_core:
            raise SystemExit(f"Cross-device sync diagnostic/project-resolution/review-eligibility contract missing: {marker}")
    if ":batchWrite" in sync_core:
        raise SystemExit("Firebase ID-token clients must not use the IAM-oriented batchWrite endpoint")
    transform = (ROOT / "tools/apply_cross_device_pwa_v1.py").read_text(encoding="utf-8")
    for marker in ("@media (min-width:768px) and (min-height:600px)", "min-width:1024px", "nk-pwa-update", "location.hostname !== 'qbank.local'"):
        if marker not in transform:
            raise SystemExit(f"Responsive/update transform contract missing: {marker}")
    generated = (ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8")
    transform_path = ROOT / "tools/apply_cross_device_pwa_v1.py"
    spec = importlib.util.spec_from_file_location("cross_device_transform", transform_path)
    transform_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transform_module)
    installed = transform_module.transform(generated)
    for marker in ("nkCloudAuthStartCreate", "nkResetProgress", "Reset account progress", "NK_CROSS_DEVICE_SYNC_V1_START"):
        if marker not in installed:
            raise SystemExit(f"Cross-device transform did not install account UI/reset integration: {marker}")
    if "NK_DURABLE_PERSISTENCE_V2_START" in generated:
        forbidden = ("localStorage.setItem(LS_KEY, JSON.stringify(state))", "localStorage.setItem(LS_KEY,JSON.stringify(state))", "localStorage.setItem(STORAGE_KEY,JSON.stringify(state))", "localStorage.setItem('qbank_state_v1',JSON.stringify(st))")
        hits = [item for item in forbidden if item in generated]
        if hits:
            raise SystemExit(f"Generated app bypasses durable state persistence: {hits}")
    android = (ROOT / "tools/apply_android_secure_origin_v1.py").read_text(encoding="utf-8")
    for marker in ("APP_ORIGIN", "migrate_local_state.html", "QBankMigration", "\\u003c"):
        if marker not in android:
            raise SystemExit(f"Android migration contract missing: {marker}")
    rules = (ROOT / "firestore.rules").read_text(encoding="utf-8")
    if "request.auth.uid == userId" not in rules or "allow delete: if false" not in rules:
        raise SystemExit("Firestore ownership/tombstone rules are not protected")
    print("CROSS_DEVICE_PWA_CONTRACT_OK")


if __name__ == "__main__":
    main()
