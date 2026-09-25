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
assert.equal(call("nkSaveQuestionNote('marrow-anat-1','')"),true);
assert.equal(state.questionNotes['marrow-anat-1'].deleted,true,'removal must leave a sync tombstone');
assert.equal(call("nkQuestionNote('marrow-anat-1')"),null);
console.log('QUESTION_NOTES_BEHAVIOR_OK');
'''
    script = script.replace("SOURCE", repr(CORE.read_text(encoding="utf-8")), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("QUESTION_NOTES_INSTALL_OK")


if __name__ == "__main__":
    main()
