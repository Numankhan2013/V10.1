#!/usr/bin/env python3
"""Check personal note behavior and additive generated-app installation."""

from pathlib import Path
import subprocess

from apply_question_notes_v1 import transform


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/question_notes_core.js"
HTML = ROOT / "app/src/main/assets/index.html"


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    generated = transform(source)
    assert transform(generated) == generated
    for marker in (
        "NK_QUESTION_NOTES_V1_START",
        "nkMountQuestionNote();",
        "questionNotes: {}",
        'id="nk-question-notes-v1"',
        "NK_NOTE_MEDIA_V1_START",
        "function nkNoteImportPdf(",
        ".nk-note-viewer-stage",
    ):
        assert marker in generated, marker

    script = r'''
const assert=require('node:assert/strict');
const vm=require('node:vm');
const state={questionNotes:{}};
const BY_ID={'marrow-anat-1':{id:'marrow-anat-1'},'prepladder-bio-1':{id:'prepladder-bio-1'}};
let saves=0,shouldFail=false;
const context={state,BY_ID,Date,Math,route:{page:'dashboard'},document:{querySelector:()=>null},
  saveState:()=>{saves++;return !shouldFail;},showToast:()=>{},esc:String};
vm.createContext(context);vm.runInContext(SOURCE,context);
const call=code=>vm.runInContext(code,context);
assert.equal(call("nkSaveQuestionNote('marrow-anat-1','  My own memory point  ')"),true);
assert.equal(state.questionNotes['marrow-anat-1'].text,'My own memory point');
assert.equal(call("nkQuestionNote('marrow-anat-1').text"),'My own memory point');
assert.equal(call("nkSaveQuestionNote('prepladder-bio-1','Second bank note')"),true);
assert.equal(state.questionNotes['marrow-anat-1'].text,'My own memory point');
assert.equal(call("nkSaveQuestionNote('missing','do not save')"),false);
assert.equal(call("nkSaveQuestionNote('marrow-anat-1','x'.repeat(2001))"),false);
const before=saves;assert.equal(call("nkSaveQuestionNote('marrow-anat-1','My own memory point')"),true);
assert.equal(saves,before,'unchanged note must not write');
shouldFail=true;
assert.equal(call("nkSaveQuestionNote('marrow-anat-1','Failed edit')"),false);
assert.equal(state.questionNotes['marrow-anat-1'].text,'My own memory point','failed storage must roll back');
shouldFail=false;
const img={type:'image',source:'pdf',label:'Atlas · page 2',asset:{id:'na_test123abc',mime:'image/jpeg',w:2400,h:3200,bytes:900000}};
let committed=null;context.nkNoteAssetsCommit=(kept,removed)=>{committed={kept,removed};};context.img=img;
assert.equal(call("nkSaveQuestionNoteBlocks('marrow-anat-1',[{type:'text',text:' First cue '},img,{type:'text',text:'After the page'}])"),true);
const rich=state.questionNotes['marrow-anat-1'];
assert.equal(rich.text,'First cue\n\nAfter the page','plain text summary stays readable by older app versions');
assert.equal(rich.blocksAt,rich.updatedAt);
assert.equal(call("nkNoteBlocks(state.questionNotes['marrow-anat-1']).map(b=>b.type).join()"),'text,image,text');
assert.equal(JSON.stringify(committed),JSON.stringify({kept:['na_test123abc'],removed:[]}));
assert.equal(call("nkSaveQuestionNoteBlocks('marrow-anat-1',[{type:'image',asset:{id:'bad id'}}])"),true,'invalid image references are dropped, leaving an empty note');
assert.equal(committed.removed.map(a=>a.id).join(),'na_test123abc','removed images are released');
assert.equal(state.questionNotes['marrow-anat-1'].deleted,true);
assert.equal(JSON.stringify(state.questionNotes['marrow-anat-1'].blocks),'[]','a note that had images keeps writing parts so removals sync');
assert.equal(call("nkSaveQuestionNoteBlocks('marrow-anat-1',Array.from({length:12},()=>img))"),true);
assert.equal(call("nkNoteBlocks(state.questionNotes['marrow-anat-1']).length"),10,'a note holds at most ten images or pages');
assert.equal(call("nkSaveQuestionNoteBlocks('marrow-anat-1',[{type:'text',text:'y'.repeat(2001)}])"),false);
assert.equal(call("nkSaveQuestionNote('marrow-anat-1','My own memory point')"),true);
assert.equal(call("nkSaveQuestionNote('marrow-anat-1','')"),true);
assert.equal(state.questionNotes['marrow-anat-1'].deleted,true,'removal must leave a sync tombstone');
assert.equal(call("nkQuestionNote('marrow-anat-1')"),null);
call("nkMountQuestionNote();nkNoteDrafts.set('marrow-anat-1','temporary')");
call("nkMountQuestionNote()");assert.equal(call("nkNoteDrafts.size"),1);
state.activeSession={id:'different-session'};call("nkMountQuestionNote()");assert.equal(call("nkNoteDrafts.size"),0);
call("nkNotesQuery='private search';nkNoteDrafts.set('marrow-anat-1','private');var nkAuth={uid:'other-account'};nkMountQuestionNote()");
assert.equal(call("nkNoteDrafts.size"),0,'account change must clear drafts');
assert.equal(call("nkNotesQuery"),'','account change must clear notes search');
console.log('QUESTION_NOTES_BEHAVIOR_OK');
'''
    script = script.replace("SOURCE", repr(CORE.read_text(encoding="utf-8")), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("QUESTION_NOTES_INSTALL_OK")


if __name__ == "__main__":
    main()
