#!/usr/bin/env python3
"""Browsing to a subject must not pick a bank for the learner.

Two Home paths used to choose a bank on the learner's behalf:

- tapping a subject card called `applySubject(subject)`, which loads that
  subject's first bank, persists `qbank_active_bank_v1` and schedules a cloud
  sync, all before the learner reached the bank chooser;
- opening a topic chapter without a bank fell back to the currently cached
  chapter data, so a chapter could be opened from a stale bank.

The two functions are taken out of the assembled page and driven directly.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from app_page import app_page  # noqa: E402
from js_extract import extract_function  # noqa: E402

RUNTIME = r"""
const assert=require('assert');

const applied=[];
const openedBank=[];
const openedChapter=[];
const openedTopics=[];
const navigated=[];
const stored={};
const synced=[];

global.SUBJECTS=[{subject:'Anatomy'},{subject:'Biochemistry'}];
global.activeSubject='Biochemistry';
global.activeBank='PrepLadder';
global.localStorage={getItem:k=>(k in stored?stored[k]:null),setItem:(k,v)=>{stored[k]=String(v);},removeItem:k=>{delete stored[k];}};
global.showToast=()=>{};
global.navigate=(page,id)=>{navigated.push([page,id]);};
global.applySubject=(name,bank)=>{applied.push([name,bank]);global.activeSubject=name;global.activeBank=bank||global.activeBank;};
global.openBank=(name,bank)=>{openedBank.push([name,bank]);};
global.openSubjectTopics=name=>{openedTopics.push(name);};
global.openChapter=id=>{openedChapter.push(id);};
global.nkScheduleCloudSync=()=>{synced.push(true);};
global.nkBankRecords=subject=>{
  if(subject==='Anatomy')return [{bank:'Marrow',questions:[],topics:[]}];
  if(subject==='Biochemistry')return [{bank:'PrepLadder',questions:[],topics:[]}];
  return [];
};
global.setTimeout=fn=>fn();
global.nkPreferredRecord=subject=>{
  const records=nkBankRecords(subject);
  if(records.length)return records.find(r=>r.bank==='Marrow')||records[0];
  return (SUBJECTS||[]).find(r=>r.subject===subject)||null;
};

__FUNCTIONS__

// --- Home subject card: open the chooser, do not pick a bank --------------
nkOpenSubjectLibrary('Anatomy');
assert.equal(applied.length,0,'tapping a subject card must not load a bank: '+JSON.stringify(applied));
assert.equal(activeSubject,'Anatomy','tapping a subject card must select the subject');
assert.equal(stored['qbank_active_subject_v1'],'Anatomy','the chosen subject must be remembered');
assert.equal(stored['qbank_active_bank_v1'],undefined,'browsing a subject must not remember a bank');
assert.deepEqual(navigated.pop(),['banks','Anatomy'],'the learner must land on the bank chooser');
assert.equal(synced.length,0,'browsing a subject must not schedule a cloud sync');

// A subject that does not exist must still be refused.
const before=applied.length;
nkOpenSubjectLibrary('Nowhere');
assert.equal(applied.length,before,'an unavailable subject must not be applied');

// --- Topic chapter without a bank: resolve the bank, then open the chapter -
nkOpenSubjectChapter('Anatomy',undefined,'anat-topic');
assert.deepEqual(openedBank.pop(),['Anatomy','Marrow'],'a bankless chapter must open the subject bank first');
assert.deepEqual(openedChapter.pop(),'anat-topic','the chapter must open once the bank is known');

// With an explicit bank, that bank is used.
nkOpenSubjectChapter('Anatomy','Marrow','anat-topic-2');
assert.deepEqual(openedBank.pop(),['Anatomy','Marrow'],'an explicit bank must be used');
assert.deepEqual(openedChapter.pop(),'anat-topic-2','the chapter must open for the explicit bank');

// A subject with no resolvable bank must not open a chapter from stale data.
const chaptersBefore=openedChapter.length;
nkOpenSubjectChapter('Nowhere',undefined,'ghost-topic');
assert.equal(openedChapter.length,chaptersBefore,'a chapter must not open when no bank can be resolved');
assert.deepEqual(openedTopics.pop(),'Nowhere','the learner must still be taken to the subject topics');

console.log('SUBJECT_NAVIGATION_OK subject_card=no_eager_bank chapter=bank_resolved');
"""


def main() -> None:
    page = app_page()
    pieces = [
        extract_function(page, "nkOpenSubjectLibrary"),
        extract_function(page, "nkOpenSubjectChapter"),
    ]
    script_text = RUNTIME.replace("__FUNCTIONS__", "\n".join(pieces))
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(script_text)
        script = Path(handle.name)
    try:
        subprocess.run(["node", str(script)], check=True, cwd=ROOT)
    finally:
        script.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
