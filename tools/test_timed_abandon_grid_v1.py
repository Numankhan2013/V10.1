#!/usr/bin/env python3
"""Verify abandonment stays in timed-test grids and saves before leaving."""
from pathlib import Path
import json
import subprocess

from apply_timed_abandon_grid_v1 import transform

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'tools/timed_abandon_grid_core.js'


def main():
    fixture='''<html><head></head><script>
/* NK_EXAM_REVIEW_FLAGS_V1_START */
function openQuestionNavigator(){}function openSessionReview(){}
function closeQuestionNavigator(){}function closeSessionReview(){}
function saveState(){}function navigate(){}function showToast(){}
  window.QB={openQuestionNavigator,openSessionReview};
</script></html>'''
    generated=transform(fixture)
    assert transform(generated)==generated
    assert 'nkAbandonTimedTest,' in generated
    assert 'nk-timed-abandon-grid-v1' in generated
    assert 'examPage' not in CORE.read_text(encoding='utf-8')
    subprocess.run(['node','--check'],input=generated.split('<script>',1)[1].split('</script>',1)[0],text=True,check=True)

    script=r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
let state={activeSession:{id:'exam-1',mode:'exam',questionIds:['q1'],answers:{q1:2}},tests:[],attempts:{}};
let fail=false,allow=false,saves=0,closedNav=0,closedReview=0,route='',toast='',navAdded=0,reviewAdded=0;
const submit={insertAdjacentHTML:(where,html)=>{assert.equal(where,'afterend');assert(html.includes('Abandon test'));navAdded++}};
const actions={querySelector:()=>reviewAdded?{}:null,insertAdjacentHTML:(where,html)=>{assert.equal(where,'beforeend');assert(html.includes('Abandon test'));reviewAdded++}};
const nav={classList:{add:()=>{}},querySelector:selector=>selector==='.qb-nav-submit'?submit:selector==='.nk-abandon-test'&&navAdded?{}:null};
const review={classList:{add:()=>{}},querySelector:selector=>selector==='.nk-session-review-actions'?actions:null};
const context={JSON,state,document:{getElementById:id=>id==='qb-question-navigator'?nav:id==='nk-session-review'?review:null},
  confirm:()=>allow,nkStateClone:value=>JSON.parse(JSON.stringify(value)),saveState:()=>{saves++;return !fail},
  closeQuestionNavigator:()=>{closedNav++},closeSessionReview:()=>{closedReview++},navigate:value=>{route=value},showToast:value=>{toast=value},
  openQuestionNavigator:()=>{},openSessionReview:()=>{},window:{QB:{}}};
vm.createContext(context);vm.runInContext(SOURCE,context);
vm.runInContext('openQuestionNavigator();openSessionReview();openQuestionNavigator();openSessionReview()',context);
assert.equal(navAdded,1);assert.equal(reviewAdded,1);
assert.equal(vm.runInContext('nkAbandonTimedTest()',context),false);
assert.equal(state.activeSession.id,'exam-1');assert.equal(saves,0);
allow=true;fail=true;
assert.equal(vm.runInContext('nkAbandonTimedTest()',context),false);
state=context.state;assert.equal(state.activeSession.id,'exam-1');assert.equal(route,'');assert.equal(closedNav,0);
fail=false;
assert.equal(vm.runInContext('nkAbandonTimedTest()',context),true);
state=context.state;assert.equal(state.activeSession,null);assert.equal(route,'tests');assert.equal(closedNav,1);assert.equal(closedReview,1);
assert.equal(state.tests.length,0);assert.equal(Object.keys(state.attempts).length,0);assert(toast.includes('abandoned'));
assert.equal(vm.runInContext('nkAbandonTimedTest()',context),false);
context.state={activeSession:{mode:'practice'},tests:[],attempts:{}};navAdded=0;reviewAdded=0;
vm.runInContext('openQuestionNavigator();openSessionReview()',context);
assert.equal(navAdded,0);assert.equal(reviewAdded,0);
console.log('TIMED_ABANDON_GRID_BEHAVIOR_OK cancel=true failedSave=true abandon=true practiceIsolation=true');
'''.replace('SOURCE',json.dumps(CORE.read_text(encoding='utf-8')),1)
    subprocess.run(['node','-e',script],cwd=ROOT,check=True)
    print('TIMED_ABANDON_GRID_INSTALL_OK')


if __name__=='__main__':main()
