#!/usr/bin/env python3
"""Behavior tests for merge safety and PWA/sync source contracts."""

from pathlib import Path
import ast
import json
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/cross_device_sync_core.js"


def main() -> None:
    core = CORE.read_text(encoding="utf-8")
    harness = r'''
const assert=(condition,message)=>{if(!condition)throw new Error(message);};
state={attempts:{q1:[{id:'a1',at:10,correct:false,selected:1,timeSpent:5}]},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null};
nkApplyCloudEnvelope({kind:'attempts',entityId:'a2',ownerDevice:'ipad',updatedAt:20,deleted:false,payload:JSON.stringify({qid:'q1',attempt:{id:'a2',at:20,correct:true,selected:2,timeSpent:7}}),schemaVersion:1});
assert(state.attempts.q1.length===2,'immutable attempts must merge');
nkApplyCloudEnvelope({kind:'attempts',entityId:'a2',ownerDevice:'ipad',updatedAt:20,deleted:false,payload:JSON.stringify({qid:'q1',attempt:{id:'a2',at:20,correct:true,selected:2,timeSpent:7}}),schemaVersion:1});
assert(state.attempts.q1.length===2,'duplicate attempt must be deduplicated');
nkApplyCloudEnvelope({kind:'bookmarks',entityId:'q1',ownerDevice:'android',updatedAt:100,deleted:false,payload:JSON.stringify({qid:'q1',active:true}),schemaVersion:1});
nkApplyCloudEnvelope({kind:'bookmarks',entityId:'q1',ownerDevice:'ipad',updatedAt:90,deleted:true,payload:'',schemaVersion:1});
assert(Boolean(state.bookmarks.q1),'older bookmark tombstone must not erase newer state');
nkApplyCloudEnvelope({kind:'bookmarks',entityId:'q1',ownerDevice:'ipad',updatedAt:110,deleted:true,payload:'',schemaVersion:1});
assert(!state.bookmarks.q1,'newer bookmark tombstone must win');
nkApplyCloudEnvelope({kind:'sessions',entityId:'active',ownerDevice:'android',updatedAt:200,deleted:false,payload:JSON.stringify({id:'new',index:4}),schemaVersion:1});
nkApplyCloudEnvelope({kind:'sessions',entityId:'active',ownerDevice:'ipad',updatedAt:150,deleted:false,payload:JSON.stringify({id:'old',index:1}),schemaVersion:1});
assert(state.activeSession.id==='new'&&state.activeSession.index===4,'opening an older device must not replace newer session progress');
state.studyModules=[{id:'m1',syncEpoch:'e1',submitted:{q1:true},answers:{q1:1},completedQuestionIds:['q1'],questionTimes:{q1:10}}];
nkApplyCloudEnvelope({kind:'modules',entityId:'m1',ownerDevice:'ipad',updatedAt:300,deleted:false,payload:JSON.stringify({id:'m1',syncEpoch:'e1',submitted:{q2:true},answers:{q2:2},completedQuestionIds:['q2'],questionTimes:{q2:20}}),schemaVersion:1});
assert(state.studyModules[0].submitted.q1&&state.studyModules[0].submitted.q2,'same-generation module progress must merge across devices');
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
  // Reproduce the original echo loop: remote preferences call the real save hook.
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
  globalThis.fetch=async(url,options)=>{
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
  state.bookmarks.q9={addedAt:Date.now()};nkCaptureCloudChanges();
  assert(scheduled===1&&nkSyncMeta.outbox['bookmarks/q9'],'real local edits must still schedule upload');
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
const document={querySelector:()=>null};
const LS_KEY='qbank_state_v1';
let state={};let activeSubject='Biochemistry';
const SUBJECT_BY_NAME={Biochemistry:{}};
function render(){} function showToast(){} function fmtDate(v){return String(v)} function esc(v){return String(v)}
function applySubject(v){activeSubject=v}
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
    update_sw = next(ast.literal_eval(node.value) for node in ast.walk(ast.parse(transform_source))
                     if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "update_sw" for t in node.targets))
    lifecycle = r'''
const assert=(v,m)=>{if(!v)throw new Error(m)};
const events={},swEvents={};let reloads=0,click;
const worker={postMessage:message=>{assert(message==='SKIP_WAITING','update message');swEvents.controllerchange();swEvents.controllerchange();}};
const registration={waiting:worker,addEventListener:()=>{}};
const navigator={serviceWorker:{controller:{},addEventListener:(name,fn)=>swEvents[name]=fn,register:async()=>registration}};
const window={addEventListener:(name,fn)=>events[name]=fn};
const location={hostname:'example.test',reload:()=>reloads++};
const document={querySelector:()=>null,createElement:()=>({querySelector:()=>({set onclick(fn){click=fn}})}),body:{appendChild:()=>{}}};
'''
    lifecycle += update_sw + "\n" + r'''
(async()=>{await events.load();swEvents.controllerchange();assert(reloads===0,'unrequested controller changes must not reload');click();assert(reloads===1,'explicit update must reload only once');console.log('PWA_UPDATE_LIFECYCLE_OK');})().catch(error=>{console.error(error);process.exitCode=1});
'''
    with tempfile.TemporaryDirectory() as directory:
        script = Path(directory) / "pwa-test.js"
        script.write_text(lifecycle, encoding="utf-8")
        subprocess.run(["node", str(script)], check=True)
    sync_core = CORE.read_text(encoding="utf-8")
    pull_at = sync_core.find("pulled=await nkPullCloud(token)")
    push_at = sync_core.find("pushed=await nkPushOutbox(token)")
    if pull_at < 0 or push_at < 0 or pull_at > push_at:
        raise SystemExit("Synchronization must pull/merge before uploading local revisions")
    if "function nkScheduleCloudSync(){if(!nkAuth)return;nkCaptureCloudChanges();}" not in sync_core:
        raise SystemExit("Local outbox capture must be synchronous with state saves")
    for marker in ("nkResolveFirebaseProjectId", "nkProjectIdFromToken", "stage='download'", "HTTP ${response.status}", "method:'PATCH'", "setInterval(nkCloudAutoSync,300000)", "visibilitychange"):
        if marker not in sync_core:
            raise SystemExit(f"Cross-device sync diagnostic/project-resolution contract missing: {marker}")
    if ":batchWrite" in sync_core:
        raise SystemExit("Firebase ID-token clients must not use the IAM-oriented batchWrite endpoint")
    transform = (ROOT / "tools/apply_cross_device_pwa_v1.py").read_text(encoding="utf-8")
    for marker in ("@media (min-width:768px) and (min-height:600px)", "min-width:1024px", "nk-pwa-update", "location.hostname !== 'qbank.local'"):
        if marker not in transform:
            raise SystemExit(f"Responsive/update transform contract missing: {marker}")
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
