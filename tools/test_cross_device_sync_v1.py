#!/usr/bin/env python3
"""Behavior tests for merge safety and PWA/sync source contracts."""

from pathlib import Path
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
console.log('CROSS_DEVICE_SYNC_BEHAVIOR_OK');
'''
    prelude = r'''
const storage={};
const localStorage={getItem:k=>Object.prototype.hasOwnProperty.call(storage,k)?storage[k]:null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]};
const window={NK_QBANK_FIREBASE_CONFIG:{}};
const navigator={onLine:true};
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
    transform = (ROOT / "tools/apply_cross_device_pwa_v1.py").read_text(encoding="utf-8")
    for marker in ("@media (min-width:768px)", "min-width:1024px", "nk-pwa-update", "location.hostname !== 'qbank.local'"):
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
