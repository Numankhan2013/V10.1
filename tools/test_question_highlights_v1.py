#!/usr/bin/env python3
"""Behavior tests for explanation highlights: anchoring, edits, and cross-device merge.

The anchoring and state functions run in Node against the module source; the
sync checks load cross_device_sync.js beside it, the way the page assembles them.
DOM wrapping and the toolbar are covered in a real browser by
verify_question_highlights_browser.py.
"""

from pathlib import Path
import subprocess
import tempfile

from app_page import app_page, app_css

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/question_highlights.js"
SYNC = ROOT / "app/src/main/modules/cross_device_sync.js"

PRELUDE = r'''
const assert=(c,m)=>{if(!c)throw new Error(m);};
const storage={};
const localStorage={getItem:k=>Object.prototype.hasOwnProperty.call(storage,k)?storage[k]:null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]};
const window={NK_QBANK_FIREBASE_CONFIG:{}};
const navigator={onLine:true};
const location={hostname:'qbank.local'};
const document={querySelector:()=>null,getElementById:()=>null};
globalThis.setTimeout=()=>0;globalThis.clearTimeout=()=>{};
const LS_KEY='qbank_state_v1';
let state={questionHighlights:{}};let activeSubject='Biochemistry';
const SUBJECT_BY_NAME={Biochemistry:{}};
let saves=0;
function render(){} function showToast(){} function saveState(){saves++;return true} function fmtDate(v){return String(v)}
function esc(v){return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[c]);}
function defaultState(){return {attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,questionNotes:{},fsrsReviewEligible:{}}}
function applySubject(v){activeSubject=v}
function nkNormalizeState(v){return v}
function nkDurablePersist(v){return true}
let nkStudySupport=function(q){return '<div class="nk-study-support"><section class="nk-source-section">x</section></div>';};
'''

LOGIC = r'''
// Exact offsets win when the text is unchanged.
const text='Insulin acts on GLUT4. Insulin also acts on the liver.';
let d=nkHlDescribe(text,23,30);
assert(d.quote==='Insulin'&&d.prefix==='Insulin acts on GLUT4. '&&d.suffix.startsWith(' also'),'describe keeps quote and context');
assert.deepEqual=undefined;
let r=nkHlResolve(text,{...d});
assert(r[0]===23&&r[1]===30,'exact range resolves');
// A re-render that inserts text earlier shifts offsets: context picks the right occurrence, not the first.
const shifted='Note: Insulin acts on GLUT4. Insulin also acts on the liver.';
r=nkHlResolve(shifted,{...d});
assert(r[0]===29&&shifted.slice(r[0],r[1])==='Insulin','shifted highlight re-anchors on its own occurrence');
const first=nkHlDescribe(text,0,7);r=nkHlResolve(shifted,first);
assert(r[0]===6,'first occurrence re-anchors by its suffix');
assert(nkHlResolve('Glucagon only.',d)===null,'missing quote stays hidden rather than landing on wrong text');
// Touch selections often grab surrounding spaces.
d=nkHlDescribe('  alpha beta  ',0,14);
assert(d.quote==='alpha beta'&&d.start===2&&d.end===12,'edge whitespace is trimmed');
assert(nkHlDescribe('   ',0,3)===null,'blank selection is ignored');

// Add, recolor, remove, clear: every edit is newer than the one before.
const a=nkHlAdd('q1','explanation',nkHlDescribe(text,0,7),'green');
const b=nkHlAdd('q1','takeaway',nkHlDescribe(text,16,21),'not-a-colour');
assert(a.color==='green'&&b.color==='yellow'&&b.zone==='takeaway','colour and zone are validated');
assert(nkHlActive(state.questionHighlights.q1.items).length===2,'two active highlights');
const before=state.questionHighlights.q1.items[a.id].updatedAt;
assert(nkHlRecolor('q1',a.id,'blue')&&state.questionHighlights.q1.items[a.id].color==='blue','recolor');
assert(state.questionHighlights.q1.items[a.id].updatedAt>before,'recolor stamps a newer edit');
assert(!nkHlRecolor('q1',a.id,'blue'),'same colour is not an edit');
assert(nkHlRemove('q1',a.id),'remove');
const tomb=state.questionHighlights.q1.items[a.id];
assert(tomb.deleted&&!tomb.quote&&tomb.updatedAt>before,'removal leaves a newer tombstone without text');
assert(nkHlActive(state.questionHighlights.q1.items).length===1,'removed highlight is inactive');
nkHlAdd('q1','explanation',nkHlDescribe(text,40,45),'pink');
const live=nkHlActive(state.questionHighlights.q1.items).map(i=>i.id);
const clearSnap=nkHlSnapshot('q1',live);
assert(nkHlClear('q1')===2&&nkHlActive(state.questionHighlights.q1.items).length===0,'clear all removes every active highlight');

// Undo: a clear, a removal, a recolour and a new highlight each go back, always as a newer edit.
assert(nkHlRestore('q1',clearSnap)===2&&nkHlActive(state.questionHighlights.q1.items).length===2,'undo clear-all brings both back');
const u1=nkHlActive(state.questionHighlights.q1.items)[0],stampBefore=u1.updatedAt;
let snap=nkHlSnapshot('q1',[u1.id]);nkHlRemove('q1',u1.id);
assert(nkHlRestore('q1',snap)===1,'undo remove');
const back=state.questionHighlights.q1.items[u1.id];
assert(!back.deleted&&back.quote===u1.quote&&back.color===u1.color&&back.updatedAt>stampBefore,'restored highlight keeps its text and colour and is newer than its tombstone');
snap=nkHlSnapshot('q1',[u1.id]);nkHlRecolor('q1',u1.id,u1.color==='purple'?'green':'purple');
nkHlRestore('q1',snap);assert(state.questionHighlights.q1.items[u1.id].color===u1.color,'undo recolour');
const fresh=nkHlAdd('q1','explanation',nkHlDescribe(text,0,7),'blue');
assert(nkHlRestore('q1',{[fresh.id]:null})===1&&state.questionHighlights.q1.items[fresh.id].deleted,'undo a new highlight removes it (tombstone)');
assert(nkHlRestore('q1',{[fresh.id]:null})===0,'undo twice is a no-op');
const merged=nkHlMergeItems({[u1.id]:{...u1,deleted:true,quote:'',updatedAt:stampBefore+1}},[state.questionHighlights.q1.items[u1.id]]);
assert(!merged[u1.id].deleted,'an undone removal wins over the older tombstone on another device');
nkHlClear('q1');

// Merge: newest edit per highlight wins, tombstones are not resurrected, bad input is dropped.
const base={id:'hl_a',zone:'explanation',color:'yellow',start:0,end:7,quote:'Insulin',prefix:'',suffix:' acts',createdAt:10,updatedAt:10};
let m=nkHlMergeItems({hl_a:base},[{...base,color:'pink',updatedAt:20}]);
assert(m.hl_a.color==='pink','newer remote colour wins');
m=nkHlMergeItems(m,[{...base,color:'green',updatedAt:15}]);
assert(m.hl_a.color==='pink','older remote copy does not overwrite');
m=nkHlMergeItems(m,[{id:'hl_a',deleted:true,createdAt:10,updatedAt:30}]);
assert(m.hl_a.deleted,'newer tombstone removes');
m=nkHlMergeItems(m,[{...base,color:'blue',updatedAt:25}]);
assert(m.hl_a.deleted,'a stale device does not resurrect a removed highlight');
m=nkHlMergeItems({hl_b:{...base,id:'hl_b',updatedAt:40}},[{id:'hl_b',deleted:true,createdAt:10,updatedAt:40}]);
assert(m.hl_b.deleted,'a tie between edit and removal resolves to removal on every device');
m=nkHlMergeItems({},[{...base,id:"x');alert(1);('"},{...base,id:'hl_c',start:5,end:2},{...base,id:'hl_d',quote:''},{...base,id:'hl_e',color:'<b>'}]);
assert(!Object.keys(m).some(k=>k!=='hl_e')&&m.hl_e.color==='yellow','unsafe ids and broken ranges are dropped, unknown colours coerced');
assert(nkHlMergeItems({},[{...base,quote:'q'.repeat(9000)}]).hl_a.quote.length===4000,'quotes are bounded');

// The explanation markup carries its question id, escaped.
const html=nkStudySupport({id:'a"b'});
assert(html.startsWith('<div data-nk-hl-qid="a&quot;b" class="nk-study-support'),'support markup is tagged with the question id');
assert(nkStudySupport(null).startsWith('<div class="nk-study-support'),'no question, no tag');
console.log('QUESTION_HIGHLIGHTS_LOGIC_OK');
'''

SYNC_CASES = r'''
nkAuth={uid:'owner'};nkSyncMeta.needsInitialPull=false;nkSyncMeta.outbox={};nkSyncMeta.localHashes={};
assert(NK_SYNC_KINDS.includes('highlights'),'highlights are a synced kind, so account reset tombstones them too');
state={...defaultState(),questionHighlights:{}};
const item=nkHlAdd('anatomy-1-1','explanation',nkHlDescribe('Brachial plexus roots C5-T1',0,15),'yellow');
nkCaptureCloudChanges();
const env=nkSyncMeta.outbox['highlights/anatomy-1-1'];
assert(env&&env.kind==='highlights'&&env.entityId==='anatomy-1-1'&&!env.deleted,'a highlight queues one envelope per question');
const sent=JSON.parse(env.payload);
assert(sent.items.length===1&&sent.items[0].quote==='Brachial plexus'&&sent.items[0].color==='yellow','payload carries the anchor');
nkSyncMeta.outbox={};nkCaptureCloudChanges();
assert(!nkSyncMeta.outbox['highlights/anatomy-1-1'],'an unchanged question does not upload again');
nkHlRemove('anatomy-1-1',item.id);nkCaptureCloudChanges();
const removal=JSON.parse(nkSyncMeta.outbox['highlights/anatomy-1-1'].payload);
assert(removal.items[0].deleted===true,'removal uploads as a tombstone');

// Two devices: each writes its own document; pulling both converges to the union with tombstones honoured.
const phone={id:'hl_phone',zone:'explanation',color:'green',start:0,end:4,quote:'Root',prefix:'',suffix:'',createdAt:100,updatedAt:100};
const web={id:'hl_web',zone:'takeaway',color:'blue',start:2,end:9,quote:'Plexus!',prefix:'',suffix:'',createdAt:110,updatedAt:110};
state={...defaultState(),questionHighlights:{q9:{items:{hl_phone:phone}}}};
const doc=(device,items,at)=>({kind:'highlights',entityId:'q9',ownerDevice:device,updatedAt:at,deleted:false,payload:JSON.stringify({items}),schemaVersion:1});
nkApplyCloudEnvelope(doc('web',[web],110));
assert(nkHlActive(state.questionHighlights.q9.items).map(i=>i.id).join()==='hl_phone,hl_web','a highlight from another device is added, local one kept');
nkApplyCloudEnvelope(doc('web',[web,{id:'hl_phone',deleted:true,createdAt:100,updatedAt:150}],150));
assert(state.questionHighlights.q9.items.hl_phone.deleted,'a removal made on the web reaches the phone');
nkApplyCloudEnvelope(doc('phone',[phone],100));
assert(state.questionHighlights.q9.items.hl_phone.deleted,'the phone document still holding it does not bring it back');
nkApplyCloudEnvelope(doc('web',[{...web,color:'purple',updatedAt:160}],160));
assert(state.questionHighlights.q9.items.hl_web.color==='purple','a newer colour change syncs');
nkApplyCloudEnvelope({kind:'highlights',entityId:"q9');x('",ownerDevice:'web',updatedAt:170,deleted:false,payload:JSON.stringify({items:[web]}),schemaVersion:1});
assert(!state.questionHighlights["q9');x('"],'unsafe question ids are refused');
nkApplyCloudEnvelope({kind:'highlights',entityId:'q9',ownerDevice:'web',updatedAt:999,deleted:true,payload:'',schemaVersion:1});
assert(state.questionHighlights.q9.items.hl_web.color==='purple','an account-reset tombstone document is not read as data');
// Echo control: after applying, the merged result uploads at most once and then settles.
nkSyncMeta.outbox={};nkCaptureCloudChanges();nkSyncMeta.outbox={};nkCaptureCloudChanges();
assert(!nkSyncMeta.outbox['highlights/q9'],'merged state settles without repeated uploads');
console.log('QUESTION_HIGHLIGHTS_SYNC_OK');
'''


def run(script: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "highlights-test.js"
        path.write_text(script, encoding="utf-8")
        return subprocess.run(["node", str(path)], check=True, capture_output=True, text=True).stdout.strip()


def test_install_contract() -> None:
    page = app_page()
    module = MODULE.read_text(encoding="utf-8")
    assert page.count("NK_QUESTION_HIGHLIGHTS_V1_START") == 1, "highlights module must be assembled once"
    # It wraps nkStudySupport after the UWorld override so every bank's explanation is tagged.
    assert page.index("NK_QUESTION_HIGHLIGHTS_V1_START") > page.index("nkStudySupport=function(q,timeMs,unattempted=false,renderedSource=''){\n    if(q?.bank!=='UWorld')"), "highlights must wrap the UWorld study support"
    assert "render()" not in module, "a highlight edit must not re-render the question"
    assert "innerHTML" not in module.split("function nkHlEnsureBar")[0], "anchoring must never rewrite explanation markup"
    css = app_css()
    assert "/* ── nk-question-highlights-v1" in css
    for color in ("yellow", "green", "blue", "pink", "purple"):
        assert f'mark.nk-hl[data-nk-hl-color="{color}"]' in css or color == "yellow", color
        assert f"--nk-hl-{color}:" in css, color
    assert 'html[data-nk-theme="dark"]' in css.split("nk-question-highlights-v1")[1], "dark tints are defined"
    assert "html.nk-android-shell :is(.nk-source-section, .nk-key-takeaway p)" in css, "Android shell must allow selection in explanations"
    print("QUESTION_HIGHLIGHTS_INSTALL_OK")


def main() -> None:
    module = MODULE.read_text(encoding="utf-8")
    print(run(PRELUDE + module + LOGIC))
    print(run(PRELUDE + SYNC.read_text(encoding="utf-8") + "\n" + module + SYNC_CASES))
    test_install_contract()


if __name__ == "__main__":
    main()
