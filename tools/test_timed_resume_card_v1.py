#!/usr/bin/env python3
"""Check saved-test recovery on Home, Tests, and builder without restarting."""
from pathlib import Path
import json
import re
import subprocess
from app_page import app_page

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/'app/src/main/modules/timed_resume_card.js'
HTML=ROOT/'app/src/main/assets/index.html'

def main():
    page=app_page()
    assert page.count(CORE.read_text(encoding='utf-8').strip())==1,'resume card core ships verbatim once'
    for marker in ('NK_TIMED_RESUME_CARD_V1_START','id="nk-timed-resume-card-v1"',
                   "${nkTimedResumeCard('tests')}<section class=\"nk-v3-section nk-test-main-action\">",
                   "titles[step-1],description)}${nkTimedResumeCard('builder')}<div class=\"nk-module-stepper\">${[1,2,3]",
                   "${nkHomeFocusSection(focus,focusModule)}",
                   "if(state.activeSession?.mode==='exam'&&typeof nkTimedFocusCard==='function')return nkTimedFocusCard();"):
        assert page.count(marker)==1,marker
    qb=page[page.index('  window.QB={'):]
    assert 'nkResumeTimedTest,' in qb[:qb.index('};')]
    assert "nkTimedResumeCard('home')" not in page
    for match in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>',page):
        inline=page[match.end():page.index('</script>',match.end())]
        if inline.strip():subprocess.run(['node','--check'],input=inline,text=True,check=True)

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
const focus=vm.runInContext('nkTimedFocusCard()',context);
assert(focus.includes("TODAY'S FOCUS")&&focus.includes('PYQ CBT')&&focus.includes('1 of 3 answered · 1 marked for review'));
assert(focus.includes('Resume timed test')&&!focus.includes('nk-timed-resume is-home'));
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(route,'exam');assert.equal(state.activeSession,active);
active.expired=true;route='';
assert(vm.runInContext('nkTimedFocusCard()',context).includes('Finish timed test'));
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(submitted,1);assert.equal(route,'');
state.activeSession={...active,id:'topic-1',timerMode:'per-question',expired:true};
assert.equal(vm.runInContext('nkResumeTimedTest()',context),true);assert.equal(strictExpired,1);assert.equal(route,'exam');
console.log('TIMED_RESUME_CARD_BEHAVIOR_OK home=true tests=true sameSession=true expiry=true');
'''.replace('SOURCE',json.dumps(CORE.read_text(encoding='utf-8')),1)
    subprocess.run(['node','-e',script],cwd=ROOT,check=True)
    print('TIMED_RESUME_CARD_INSTALL_OK')

if __name__=='__main__':main()
