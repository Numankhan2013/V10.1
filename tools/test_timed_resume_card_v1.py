#!/usr/bin/env python3
"""Check saved-test recovery on Home and Tests without restarting the session."""
from pathlib import Path
import json
import subprocess

from apply_timed_resume_card_v1 import transform

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'tools/timed_resume_card_core.js'

def main():
    fixture='''<html><head></head><script>
/* NK_EXAM_REVIEW_FLAGS_V1_START */
function dashboard(){return `<section class="nk-home-focus-card"></section>`;}
function testsPage(){return `<section class="nk-v3-section nk-test-main-action"></section>`;}
  window.QB={nav:()=>{}};
</script></html>'''
    generated=transform(fixture)
    assert transform(generated)==generated
    for marker in ('NK_TIMED_RESUME_CARD_V1_START',"nkTimedResumeCard('home')",
                   "nkTimedResumeCard('tests')",'nkResumeTimedTest,','nk-timed-resume-card-v1'):
        assert marker in generated,marker
    subprocess.run(['node','--check'],input=generated.split('<script>',1)[1].split('</script>',1)[0],text=True,check=True)

    script='''
const assert=require('node:assert/strict'),vm=require('node:vm');
const state={activeSession:null};let route='',submitted=0,strictExpired=0,toast='';
const context={state,esc:String,navIcon:()=>'',showToast:msg=>{toast=msg},
  nkTimedSessionExpired:s=>Boolean(s.expired),nkExpireTopicQuestion:()=>{strictExpired++;state.activeSession.expired=false},
  submitExam:()=>{submitted++;state.activeSession=null},navigate:p=>{route=p}};
vm.createContext(context);vm.runInContext(SOURCE,context);
assert.equal(vm.runInContext('nkTimedResumeCard("home")',context),'');
assert.equal(vm.runInContext('nkResumeTimedTest()',context),false);assert(toast.includes('no timed test'));
const active={id:'exam-1',mode:'exam',title:'PYQ CBT',questionIds:['a','b','c'],answers:{a:1},markedForReview:{b:true},expired:false};
state.activeSession=active;
const home=vm.runInContext('nkTimedResumeCard("home")',context);
assert(home.includes('1 of 3 answered')&&home.includes('1 marked for review')&&home.includes('timer keeps running'));
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(route,'exam');assert.equal(state.activeSession,active);
active.expired=true;route='';
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(submitted,1);assert.equal(route,'');
state.activeSession={...active,id:'topic-1',timerMode:'per-question',expired:true};
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(strictExpired,1);assert.equal(route,'exam');
console.log('TIMED_RESUME_CARD_BEHAVIOR_OK home=true tests=true sameSession=true expiry=true');
'''.replace('SOURCE',json.dumps(CORE.read_text(encoding='utf-8')),1)
    subprocess.run(['node','-e',script],cwd=ROOT,check=True)
    print('TIMED_RESUME_CARD_INSTALL_OK')

if __name__=='__main__':main()
