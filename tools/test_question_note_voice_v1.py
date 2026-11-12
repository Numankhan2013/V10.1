#!/usr/bin/env python3
"""Voice clips in My notes: block model, limits, sync separation and older-version safety.

Older app versions keep only text and image blocks and re-upload what they keep, so voice
clips travel in their own `noteVoice` kind and `noteBlocks` never carries them.
"""

from pathlib import Path
import subprocess
import tempfile
from app_page import app_source


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "app/src/main/modules/question_notes.js"
MEDIA = ROOT / "app/src/main/modules/question_note_media.js"
SYNC = ROOT / "app/src/main/modules/cross_device_sync.js"
POLICY = ROOT / "tools/web_security_policy.py"
FEEL = ROOT / "app/src/main/assets/redesign/nk-feel.js"
ICONS = ROOT / "app/src/main/assets/redesign/nk-icons.js"


def run_node(script: str) -> None:
    # Run from a file so a failure prints the assertion, not the whole module.
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "voice.js"
        path.write_text(script, encoding="utf-8")
        result = subprocess.run(["node", str(path)], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr[-3000:])
    print(result.stdout.strip())


def test_install() -> None:
    page = app_source()
    for marker in (
        "/* ── nk-note-voice-v1 ── */",
        "data-act=\"add-voice\"",
        "accept=\"audio/*\"",
        "function nkNoteVoiceStart(",
        "audioBitsPerSecond:NK_NOTE_VOICE_BITRATE",
        "'audio/webm;codecs=opus','audio/mp4;codecs=mp4a.40.2','audio/mp4'",
        "NK_NOTE_VOICE_MAX_MS=180000",
        "Rename caption",
        "nk-notes-item-voice",
        "NK_SYNC_KINDS.push('noteVoice')",
    ):
        assert marker in page, marker
    assert "microphone=(self)" in POLICY.read_text(encoding="utf-8"), "the PWA must allow its own origin to use the microphone"
    assert "'add-voice': 'microphone'" in FEEL.read_text(encoding="utf-8") and "4: [[" in FEEL.read_text(encoding="utf-8")
    assert '"microphone":"<path' in ICONS.read_text(encoding="utf-8")
    # Bytes never go into the note record or localStorage; voice reuses the existing store and chunks.
    media = MEDIA.read_text(encoding="utf-8")
    assert "{full:{mime,data}}" in media and "kind:'audio'" in media and "NK_NOTE_CHUNK_CHARS=800000" in media


def test_behavior() -> None:
    script = r'''
const assert=require('node:assert/strict');
const vm=require('node:vm');
const J=v=>JSON.parse(JSON.stringify(v)),deq=(a,b,m)=>assert.deepEqual(J(a),J(b),m);
const state={questionNotes:{}};
const BY_ID={'q1':{id:'q1'}};
let committed=null;
const context={state,BY_ID,Date,Math,JSON,route:{page:'dashboard'},document:{querySelector:()=>null},
  saveState:()=>true,showToast:()=>{},esc:String,nkNoteAssetsCommit:(kept,removed)=>{committed={kept,removed};}};
vm.createContext(context);vm.runInContext(NOTES,context);
const call=code=>vm.runInContext(code,context);
const clip=(id,extra={})=>({type:'audio',assetId:id,durationMs:42000,mime:'audio/webm;codecs=opus',caption:'  Murmur   cue ',bytes:126000,...extra});
context.clip=clip;
assert.equal(call("nkSaveQuestionNoteBlocks('q1',[{type:'text',text:'Cue'},clip('na_voice000001'),{type:'image',asset:{id:'na_image000001',w:10,h:10,bytes:5}}])"),true);
const saved=state.questionNotes.q1;
deq(saved.blocks.map(b=>b.type),['text','audio','image']);
deq(JSON.parse(JSON.stringify(saved.blocks[1])),{type:'audio',assetId:'na_voice000001',durationMs:42000,mime:'audio/webm',caption:'Murmur cue',bytes:126000},'clips keep container mime, trimmed caption');
assert.equal(saved.text,'Cue','older versions still read the text summary');
deq(committed.kept,['na_image000001','na_voice000001'],'clip assets are kept like images');
// A voice-only note still writes parts and is a live note.
assert.equal(call("nkSaveQuestionNoteBlocks('q1',[clip('na_voice000001')])"),true);
assert.equal(state.questionNotes.q1.deleted,false);
assert.ok(call("nkQuestionNote('q1')"),'a note with only a clip is a note');
deq(committed.removed.map(a=>a.id),['na_image000001']);
// Removing a clip releases its asset (tombstoned in the cloud like images).
assert.equal(call("nkSaveQuestionNoteBlocks('q1',[{type:'text',text:'Cue'}])"),true);
deq(JSON.parse(JSON.stringify(committed.removed)),[{id:'na_voice000001',bytes:126000}]);
// Limits: five clips; images and text keep their own limits.
call("var many=[...Array.from({length:7},(_,i)=>clip('na_voice00000'+i)),...Array.from({length:12},(_,i)=>({type:'image',asset:{id:'na_image00000'+i,w:1,h:1}}))]");
assert.equal(call("nkNoteSanitizeBlocks(many).filter(nkNoteAudioBlock).length"),5);
assert.equal(call("nkNoteSanitizeBlocks(many).filter(nkNoteMediaBlock).length"),10);
assert.equal(call("nkNoteSanitizeBlocks([{type:'audio',assetId:'../../x'},{type:'audio',assetId:'na_ok1234567',mime:'text/html',durationMs:-5}]).map(b=>b.mime+':'+b.durationMs).join()"),'audio/webm:0','unsafe ids drop, mime and duration are clamped');
assert.equal(call("nkNoteCounts([{type:'text',text:'a'},clip('na_voice000001'),clip('na_voice000002')])"),'1 text · 2 voice clips');
// Sync separation: noteBlocks never carries clips; noteVoice carries them with their place.
assert.equal(call("nkSaveQuestionNoteBlocks('q1',[{type:'text',text:'A'},clip('na_voice000001'),{type:'text',text:'B'},clip('na_voice000002')])"),true);
deq(call("nkNoteSyncNotes(state.questionNotes).q1.blocks.map(b=>b.type)"),['text','text']);
deq(state.questionNotes.q1.blocks.map(b=>b.type),['text','audio','text','audio'],'the view does not touch state');
const env=call("nkNoteVoiceEnvelopes(()=>false)");
assert.equal(env.length,1);assert.equal(env[0][0],'q1');
deq(env[0][1].clips.map(c=>[c.assetId,c.at]),[['na_voice000001',1],['na_voice000002',3]]);
assert.equal(env[0][2],state.questionNotes.q1.blocksAt);
assert.equal(call("nkNoteVoiceEnvelopes(()=>false).filter(e=>e[0]==='none').length"),0);
// An older version re-uploads noteBlocks without clips (and maybe with edited text): clips return to their places.
const prior=state.questionNotes.q1;
deq(call("nkNoteKeepVoice(state.questionNotes.q1,[{type:'text',text:'A edited'},{type:'text',text:'B'}])").map(b=>b.text||b.assetId),['A edited','na_voice000001','B','na_voice000002']);
deq(call("nkNoteKeepVoice(state.questionNotes.q1,[{type:'text',text:'only'}])").map(b=>b.text||b.assetId),['only','na_voice000001','na_voice000002'],'a shorter list keeps every clip');
// noteVoice from another device replaces this device's clips, keeping the other parts.
assert.equal(call("nkNoteApplyVoice('q1',{clips:[{...clip('na_voice000009'),at:0}],deleted:false},"+(prior.blocksAt+10)+")"),true);
deq(state.questionNotes.q1.blocks.map(b=>b.text||b.assetId),['na_voice000009','A','B']);
assert.equal(state.questionNotes.q1.blocksAt,prior.blocksAt+10);
assert.equal(call("nkNoteApplyVoice('q1',{clips:[],deleted:false},1)"),true);
deq(state.questionNotes.q1.blocks.map(b=>b.type),['text','text'],'an empty clip list removes clips');
assert.equal(call("nkNoteApplyVoice('missing',{clips:[clip('na_voice000001')]},1)"),false,'clips never create a note on their own');
// Removals travel: once synced, an empty list is still sent.
assert.equal(call("nkNoteVoiceEnvelopes(()=>false).length"),0);
deq(call("nkNoteVoiceEnvelopes(key=>key==='noteVoice/q1')")[0][1].clips,[]);
// An older version edited only the text (notes newer than parts): clips stay visible.
state.questionNotes.q2={text:'old edit',updatedAt:50,deleted:false,blocks:[{type:'text',text:'x'},clip('na_voice000003')],blocksAt:40};
deq(call("nkNoteBlocks(state.questionNotes.q2).map(b=>b.type)"),['text','audio']);
console.log('QUESTION_NOTE_VOICE_BEHAVIOR_OK');
'''
    script = script.replace("NOTES", repr(NOTES.read_text(encoding="utf-8")), 1)
    run_node(script)


def test_sync_round_trip() -> None:
    """Two new devices and an older one through nkApplyCloudEnvelope and nkCaptureCloudChanges."""
    harness = r'''
const assert=(c,m)=>{if(!c)throw new Error(m);};
var window={NK_QBANK_FIREBASE_CONFIG:{},addEventListener(){},QB:{}},navigator={onLine:false},document={querySelector:()=>null,addEventListener(){}};
var localStorage={d:{},getItem(k){return this.d[k]??null},setItem(k,v){this.d[k]=String(v)},removeItem(k){delete this.d[k]}};
var state={attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,questionNotes:{},fsrsReviewEligible:{}};
var activeSubject='Physiology',BY_ID={q1:{id:'q1'}},route={page:'dashboard'};
function render(){} function showToast(){} function saveState(){return true} function esc(v){return String(v)} function fmtDate(v){return String(v)}
function defaultState(){return {attempts:{},bookmarks:{},reviews:{},tests:[],studyModules:[],activeSession:null,questionNotes:{},fsrsReviewEligible:{}}}
function nkNormalizeState(v){return v}
'''
    checks = r'''
assert(NK_SYNC_KINDS.includes('noteVoice')&&NK_SYNC_KINDS.indexOf('noteVoice')>NK_SYNC_KINDS.indexOf('notes'),'noteVoice is pulled after notes and noteBlocks');
nkAuth={uid:'learner'};
const clip={type:'audio',assetId:'na_voice000001',durationMs:9000,mime:'audio/webm',caption:'',bytes:30000};
state.questionNotes.q1={text:'Cue',updatedAt:100,deleted:false,blocks:[{type:'text',text:'Cue'},clip],blocksAt:100};
nkCaptureCloudChanges();
const out=nkSyncMeta.outbox;
const blocks=JSON.parse(out['noteBlocks/q1'].payload),voice=JSON.parse(out['noteVoice/q1'].payload);
assert(blocks.blocks.length===1&&blocks.blocks[0].type==='text','noteBlocks excludes clips: '+out['noteBlocks/q1'].payload);
assert(voice.clips.length===1&&voice.clips[0].at===1,'noteVoice carries the clip and its place');
// Device B receives both.
const sent={notes:out['notes/q1'],noteBlocks:out['noteBlocks/q1'],noteVoice:out['noteVoice/q1']};
state=defaultState();nkSyncMeta.outbox={};nkSyncMeta.localHashes={};nkSyncMeta.winners={};
['notes','noteBlocks','noteVoice'].forEach(k=>nkApplyCloudEnvelope({...sent[k],ownerDevice:'ipad'}));
assert(state.questionNotes.q1.blocks.map(b=>b.type).join()==='text,audio','the clip arrives in place');
nkCaptureCloudChanges();
assert(!nkSyncMeta.outbox['noteBlocks/q1']&&!nkSyncMeta.outbox['noteVoice/q1'],'received parts are not echoed: '+Object.keys(nkSyncMeta.outbox));
// An older device edits the text; its noteBlocks (newer, no clips) must not drop the clip.
const later=Date.now()+60000;
nkApplyCloudEnvelope({kind:'notes',entityId:'q1',ownerDevice:'old',updatedAt:later,deleted:false,payload:JSON.stringify({text:'Old edit',deleted:false}),schemaVersion:1});
nkApplyCloudEnvelope({kind:'noteBlocks',entityId:'q1',ownerDevice:'old',updatedAt:later,deleted:false,payload:JSON.stringify({blocks:[{type:'text',text:'Old edit'}],deleted:false}),schemaVersion:1});
assert(nkNoteBlocks(state.questionNotes.q1).map(b=>b.text||b.assetId).join('|')==='Old edit|na_voice000001','an older edit keeps the clip');
nkCaptureCloudChanges();
assert(!nkSyncMeta.outbox['noteBlocks/q1'],'the older device and this one agree on noteBlocks, so nothing ping-pongs');
// A clip removed elsewhere is removed here.
nkApplyCloudEnvelope({kind:'noteVoice',entityId:'q1',ownerDevice:'ipad',updatedAt:later+1,deleted:false,payload:JSON.stringify({clips:[],deleted:false}),schemaVersion:1});
assert(state.questionNotes.q1.blocks.map(b=>b.type).join()==='text','clip removal syncs');
console.log('QUESTION_NOTE_VOICE_SYNC_OK');
'''
    source = harness + NOTES.read_text(encoding="utf-8") + "\n" + SYNC.read_text(encoding="utf-8") + "\n" + checks
    run_node(source)


def main() -> None:
    test_install()
    test_behavior()
    test_sync_round_trip()
    print("QUESTION_NOTE_VOICE_OK")


if __name__ == "__main__":
    main()
