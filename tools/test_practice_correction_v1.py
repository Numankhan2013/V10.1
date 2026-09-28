#!/usr/bin/env python3
"""Check exact saved-result selection and install the correction action."""

import json
from pathlib import Path
import subprocess

from apply_practice_correction_v1 import CORE, REVIEW_ANCHOR, transform


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    fixture = ('<html><head></head><script>/* NK_CONTINUE_PRACTICE_RESUME_V1_START '
               'NK_QUESTION_SEARCH_V1_START */function resultPage(t){return `'
               + REVIEW_ANCHOR + '</div>`;}  window.QB={};</script></html>')
    installed = transform(fixture)
    assert transform(installed) == installed
    assert installed.count('${nkCorrectionResultSection(t)}') == 1
    assert 'window.QB={nkCorrectionStart,' in installed
    inline = installed.split('<script>', 1)[1].split('</script>', 1)[0]
    subprocess.run(['node', '--check'], input=inline, text=True, check=True)

    source = json.dumps(CORE.read_text(encoding='utf-8'))
    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const questions=[
 {id:'marrow__ANAT_CH01_Q001',correctOption:2,question:'Anatomy',subject:'Anatomy',bank:'Marrow'},
 {id:'biochemistry-1-1',correctOption:3,question:'Biochemistry',subject:'Biochemistry',bank:'PrepLadder'},
 {id:'physiology-9-6',correctOption:1,question:'Physiology',subject:'Physiology',bank:'PrepLadder'}
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
console.log('PRACTICE_CORRECTION_BEHAVIOR_OK exact=true linked=true repeat=true missingGuard=true');
'''.replace('SOURCE', source, 1)
    subprocess.run(['node', '-e', script], cwd=ROOT, check=True)
    print('PRACTICE_CORRECTION_INSTALL_OK')


if __name__ == '__main__':
    main()
