#!/usr/bin/env python3
"""Check exact saved-result selection and the shipped correction action."""

import json
from pathlib import Path
import re
import subprocess
from app_page import app_source


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "app/src/main/modules/practice_correction.js"
REVIEW_ANCHOR = '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">QUESTION REVIEW</div>'


def main() -> None:
    page = app_source()
    assert page.count(CORE.read_text(encoding='utf-8').strip()) == 1, 'correction core ships verbatim once'
    for marker in ('NK_PRACTICE_CORRECTION_V1_START', '/* ── nk-practice-correction-v1 ── */',
                   '      ${nkCorrectionResultSection(t)}\n' + REVIEW_ANCHOR):
        assert page.count(marker) == 1, marker
    qb = page[page.index('  window.QB={'):]
    assert 'nkCorrectionStart,' in qb[:qb.index('};')]
    for match in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>', page):
        inline = page[match.end():page.index('</script>', match.end())]
        if inline.strip():
            subprocess.run(['node', '--check'], input=inline, text=True, check=True)

    source = json.dumps(CORE.read_text(encoding='utf-8'))
    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const questions=[
 {id:'marrow__ANAT_CH01_Q001',correctOption:2,question:'Anatomy',subject:'Anatomy',bank:'Marrow'},
 {id:'biochemistry-1-1',correctOption:3,question:'Biochemistry',subject:'Biochemistry',bank:'PrepLadder'},
 {id:'physiology-9-6',correctOption:1,question:'Physiology',subject:'Physiology',bank:'PrepLadder'},
 {id:'physiology-23-38',correctOption:null,question:'Source answer unavailable',subject:'Physiology',bank:'PrepLadder'}
];
const initial={id:'first',kind:'practice',questionIds:questions.map(q=>q.id),answers:{'marrow__ANAT_CH01_Q001':1,'biochemistry-1-1':3},createdAt:1};
const state={tests:[initial],activeSession:null},BY_ID={};let started=null,toasts=[];
const context={state,BY_ID,window:{},Date,Math,
 nkAllStudyQuestions:()=>questions,esc:value=>String(value),navIcon:()=>'',
 showToast:value=>toasts.push(value),startSession:(ids,mode,title,context)=>{started={ids,mode,title,context};return true;}};
vm.createContext(context);vm.runInContext(SOURCE,context);
const run=code=>vm.runInContext(code,context);
assert.deepEqual(Array.from(run('nkCorrectionMisses(state.tests[0]).ids')),['marrow__ANAT_CH01_Q001','physiology-9-6']);
assert.match(run('nkCorrectionResultSection(state.tests[0])'),/2 questions need another pass/);
initial.createdAt=Date.now();
assert.equal(run("nkCorrectionStart('first')"),true);
assert.deepEqual(Array.from(started.ids),['marrow__ANAT_CH01_Q001','physiology-9-6']);
assert.equal(started.context,'correction:first');
assert.equal(started.mode,'practice');
assert.equal(context.BY_ID['marrow__ANAT_CH01_Q001'].bank,'Marrow');
const followup={id:'second',kind:'practice',correctionOf:'first',questionIds:started.ids,answers:{'marrow__ANAT_CH01_Q001':2,'physiology-9-6':2},createdAt:2};
state.tests.push(followup);
const markup=run('nkCorrectionResultSection(state.tests[1])');
assert.match(markup,/1 corrected/);assert.match(markup,/1 still missed or unattempted/);
assert.match(markup,/Correct my misses/);
assert.match(run('nkCorrectionResultSection(state.tests[0])'),/View latest correction pass/);
followup.answers['physiology-9-6']=1;
assert.match(run('nkCorrectionResultSection(state.tests[1])'),/2 corrected/);
assert.doesNotMatch(run('nkCorrectionResultSection(state.tests[1])'),/Correct my misses/);
initial.questionIds.push('missing-id');
assert.equal(run("nkCorrectionStart('first')"),false);
assert.equal(started.context,'correction:first','missing source must not launch a partial pass');
assert(toasts.some(value=>value.includes('unavailable')));
assert.equal(run("nkCorrectionStart('unknown')"),false);
initial.questionIds.pop();
assert.deepEqual(Array.from(run('nkCorrectionMisses(state.tests[0]).unanswerable')),['physiology-23-38']);
assert.match(run('nkCorrectionResultSection(state.tests[0])'),/lacks a reliable answer key/);
assert.equal(run("nkCorrectionStart('first')"),true);
assert.deepEqual(Array.from(started.ids),['marrow__ANAT_CH01_Q001','physiology-9-6'],'no-answer-key question is excluded');
context.nkFsrsUnresolvedResultMisses=(test,ids)=>ids.filter(id=>id!=='marrow__ANAT_CH01_Q001');
assert.equal(run("nkCorrectionStart('first')"),true);
assert.deepEqual(Array.from(started.ids),['physiology-9-6'],'resolved misses must be excluded from another correction pass');
assert.match(run('nkCorrectionResultSection(state.tests[0])'),/1 corrected since this result/);
context.nkFsrsUnresolvedResultMisses=()=>[];
assert.equal(run("nkCorrectionStart('first')"),false);
assert.match(run('nkCorrectionResultSection(state.tests[0])'),/All 2 original misses have been corrected/);
console.log('PRACTICE_CORRECTION_BEHAVIOR_OK exact=true linked=true repeat=true missingGuard=true');
'''.replace('SOURCE', source, 1)
    subprocess.run(['node', '-e', script], cwd=ROOT, check=True)
    print('PRACTICE_CORRECTION_INSTALL_OK')


if __name__ == '__main__':
    main()
