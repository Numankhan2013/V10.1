#!/usr/bin/env python3
"""Check saved-test recovery on Home, Tests, and builder without restarting."""
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
function nkCbtBuilderPage(){const step=1,titles=['Banks'],description='Build';return `<main>${nkAppPageHead(titles[step-1],description)}<div class="nk-module-stepper">${[1,2,3].join('')}</div></main>`;}
  window.QB={nav:()=>{}};
</script></html>'''
    generated=transform(fixture)
    assert transform(generated)==generated
    for marker in ('NK_TIMED_RESUME_CARD_V1_START',"nkTimedResumeCard('home')",
                   "nkTimedResumeCard('tests')","nkTimedResumeCard('builder')",'nkResumeTimedTest,nkDiscardTimedTest,','nk-timed-resume-card-v1'):
        assert marker in generated,marker
    subprocess.run(['node','--check'],input=generated.split('<script>',1)[1].split('</script>',1)[0],text=True,check=True)

    script='''
const assert=require('node:assert/strict'),vm=require('node:vm');
const state={activeSession:null,timedSessions:[]};let route='',submitted=0,strictExpired=0,toast='',switches=0,rendered=0;
const context={state,esc:value=>String(value).replace(/"/g,'&quot;'),navIcon:()=>'',showToast:msg=>{toast=msg},
  nkTimedSessions:()=>[...state.timedSessions,...(state.activeSession?[state.activeSession]:[])].filter(s=>!['submitted','discarded'].includes(s.lifecycle)),
  nkActivateTimedSession:id=>{const found=state.timedSessions.find(s=>s.id===id);if(!found)return false;state.activeSession=found;switches++;return true},
  nkTimedStoreSession:(s,lifecycle)=>{state.timedSessions=state.timedSessions.filter(item=>item.id!==s.id).concat({...s,lifecycle});return true},
  saveState:()=>true,render:()=>{rendered++},confirm:()=>true,route:{page:'dashboard'},
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
state.activeSession=null;state.timedSessions=[{...active,id:'exam-1',lifecycle:'paused'},{...active,id:'exam-2',title:'Topic Test',lifecycle:'paused'}];
const choices=vm.runInContext('nkTimedResumeCard("tests")',context);
assert.equal((choices.match(/class="nk-timed-resume is-tests"/g)||[]).length,2);
assert(choices.includes('nkResumeTimedTest(&quot;exam-1&quot;)')&&choices.includes('nkResumeTimedTest(&quot;exam-2&quot;)'));
assert.equal(vm.runInContext('nkResumeTimedTest("exam-2")',context),true);assert.equal(switches,1);assert.equal(state.activeSession.id,'exam-2');
state.activeSession=null;
assert.equal(vm.runInContext('nkDiscardTimedTest("exam-1")',context),true);
assert.equal(state.timedSessions.find(s=>s.id==='exam-1').lifecycle,'discarded');assert.equal(rendered,1);
state.timedSessions=[];state.activeSession=active;
active.expired=true;route='';
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(submitted,1);assert.equal(route,'');
state.activeSession={...active,id:'topic-1',timerMode:'per-question',expired:true};
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(strictExpired,1);assert.equal(route,'exam');
console.log('TIMED_RESUME_CARD_BEHAVIOR_OK home=true tests=true sameSession=true expiry=true');
'''.replace('SOURCE',json.dumps(CORE.read_text(encoding='utf-8')),1)
    subprocess.run(['node','-e',script],cwd=ROOT,check=True)
    print('TIMED_RESUME_CARD_INSTALL_OK')

if __name__=='__main__':main()
