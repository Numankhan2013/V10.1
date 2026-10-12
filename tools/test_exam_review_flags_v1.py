#!/usr/bin/env python3
"""Verify timed-test marks survive the saved-test boundary and target follow-up."""
from pathlib import Path
import json
import re
import subprocess
from app_page import app_source

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'app/src/main/modules/exam_review_flags.js'
HTML=ROOT/'app/src/main/assets/index.html'

def main():
    page=app_source()
    assert page.count(CORE.read_text(encoding='utf-8').strip())==1,'review flag core ships verbatim once'
    for marker in ('NK_EXAM_REVIEW_FLAGS_V1_START','/* ── nk-exam-review-flags-v1 ── */',
                   '<div class="option-list">${options}</div>${nkExamReviewButton(q,s)}</section>',
                   'questionTimes:qt,markedForReview:{...(s.markedForReview||{})},correct,incorrect,unattempted,total:s.questionIds.length,attempted,totalTimeMs,createdAt:now'):
        assert page.count(marker)==1,marker
    qb=page[page.index('  window.QB={'):]
    assert 'nkToggleExamReviewFlag,nkCbtPracticeMarked,' in qb[:qb.index('};')]
    for match in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>',page):
        inline=page[match.end():page.index('</script>',match.end())]
        if inline.strip():subprocess.run(['node','--check'],input=inline,text=True,check=True)

    script='''
const assert=require('node:assert/strict'),vm=require('node:vm');
const questions=[{id:'a',subject:'Anatomy'},{id:'b',subject:'Physiology'}];
const state={activeSession:{id:'exam1',mode:'exam',questionIds:['a','b'],index:0,answers:{}},tests:[]};
let saves=0,renders=0,started=null;
const context={state,BY_ID:{},Date,JSON,Map,String,Math,
  nkQuestionTransaction:fn=>fn(),saveState:()=>{saves++;return true},render:()=>{renders++},
  openSessionReview:()=>{},openQuestionNavigator:()=>{},nkCbtResultSection:()=>'<section>topic analysis</section>',
  nkAllStudyQuestions:()=>questions,startSession:(ids,mode,title,kind)=>{started={ids:Array.from(ids),mode,title,kind};return true},
  showToast:()=>{},esc:String,navIcon:()=>'',document:{getElementById:()=>null}};
vm.createContext(context);vm.runInContext(SOURCE,context);
assert.equal(vm.runInContext('nkToggleExamReviewFlag("b","exam1")',context),false,'stale question cannot be marked');
assert.equal(vm.runInContext('nkToggleExamReviewFlag("a","other")',context),false,'stale test cannot be marked');
assert.equal(vm.runInContext('nkToggleExamReviewFlag("a","exam1")',context),true);
assert.equal(state.activeSession.markedForReview.a,true);
assert.equal(vm.runInContext('nkToggleExamReviewFlag("a","exam1")',context),true);
assert.equal(state.activeSession.markedForReview.a,undefined,'mark is a two-way toggle');
assert.equal(vm.runInContext('nkToggleExamReviewFlag("a","exam1")',context),true);
assert.equal(saves,3);assert.equal(renders,3);
const test={id:'saved1',title:'Mixed CBT',questionIds:['a','b'],markedForReview:{a:true,missing:true},createdAt:0};
state.tests.push(test);
assert.deepEqual(Array.from(vm.runInContext('nkMarkedTestIds(state.tests[0])',context)),['a']);
assert(vm.runInContext('nkCbtResultSection(state.tests[0])',context).includes('Practise marked questions'));
assert.equal(vm.runInContext('nkCbtPracticeMarked("saved1",{detail:2})',context),false,'carried-over double tap cannot launch Practice');
test.createdAt=Date.now();
assert.equal(vm.runInContext('nkCbtPracticeMarked("saved1",{detail:1})',context),true);
assert.deepEqual(started.ids,['a']);assert.equal(started.mode,'practice');assert.equal(started.kind,'cbt-marked-followup');
assert.equal(state.activeSession.answers.a,undefined,'marking cannot submit or change an answer');
console.log('EXAM_REVIEW_FLAGS_BEHAVIOR_OK toggle=true snapshot=true followup=true');
'''.replace('SOURCE',json.dumps(CORE.read_text(encoding='utf-8')),1)
    subprocess.run(['node','-e',script],cwd=ROOT,check=True)
    print('EXAM_REVIEW_FLAGS_INSTALL_OK')

if __name__=='__main__':main()
