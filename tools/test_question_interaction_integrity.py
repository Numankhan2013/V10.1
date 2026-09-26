#!/usr/bin/env python3
"""Execute real question handlers and FSRS under failed persistence/stale input."""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    html = (ROOT / 'app/src/main/assets/index.html').read_text()
    names = ('selectPractice', 'selectExam', 'submitPractice', 'retryCurrent', 'nextQ', 'prevQ', 'goIndex', 'toggleBookmark')
    handlers = '\n'.join(re.search(r'  function ' + name + r'\([^\n]+', html)[0] for name in names)
    fsrs = (ROOT / 'tools/fsrs_scheduler_core.js').read_text()
    integrity = ROOT / 'tools/question_interaction_core.js'
    runtime = r'''
const assert=require('assert');global.window=globalThis;
const events={},windowEvents={};window.FSRS=require(process.argv[2]);window.addEventListener=(name,fn)=>{windowEvents[name]=fn};
global.document={addEventListener:(name,fn)=>{events[name]=fn},getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[],body:{insertAdjacentHTML:()=>{}}};
let historyTarget='',confirmed=false,lastPrompt='';global.location={hostname:'preview.example',hash:'#dashboard'};
global.history={replaceState:(a,b,target)=>{historyTarget=target;location.hash=target},pushState:(a,b,target)=>{historyTarget=target;location.hash=target}};
global.confirm=message=>{lastPrompt=message;return confirmed};
function parseHash(){return {page:location.hash.replace(/^#/,'')||'dashboard'};}
const questions=['q1','q2','q3'].map(id=>({id,correctOption:1,options:['A','B','C','D'].map(letter=>({letter,text:letter}))}));
const SUBJECTS=[{subject:'Biochemistry',questions}],BY_ID=Object.fromEntries(questions.map(q=>[q.id,q]));
let state,failed=false,writes=0,renders=0;const LS_KEY='state';let persisted='';
global.localStorage={getItem:()=>persisted,setItem:(k,v)=>{persisted=v}};
let route={page:'practice'},morePage=()=>'',practiceActionBar=()=>'',endSession=()=>{},navigate=p=>{route.page=p},recordAttempt=()=>{},qAttempts=()=>[];
function saveState(){if(failed)return false;writes++;persisted=JSON.stringify(state);return true;}
function render(){renders++;}function haptic(){}function showToast(){}function savePracticeElapsed(){}function saveExamElapsed(){}
function openSessionReview(){}function submitExam(){}function nkPausePractice(){}function nkSubmitPracticeSession(){}function finishPracticeSession(){}
function nkStorageError(){}function nkStateClone(v){return JSON.parse(JSON.stringify(v));}
function startSession(){}function nkStartSessionReliably(){}function nkResolvePracticeReplacement(){}function nkResolveTimedSession(){}
function nkPracticeResumeQuestion(id){return BY_ID[id];}
function reset(mode='practice'){
 state={attempts:{},reviews:{},bookmarks:{},tests:[],fsrsPreferences:null,activeSession:{id:'session',mode,context:'normal',questionIds:['q1','q2','q3'],index:0,answers:{},submitted:{},questionTimes:{},pendingRating:{}}};
 failed=false;writes=0;renders=0;saveState();
 route.page=mode==='exam'?'exam':'practice';location.hash='#dashboard';location.hostname='preview.example';confirmed=false;lastPrompt='';historyTarget='';
}
''' + handlers + '\n' + fsrs + '\n' + (integrity.read_text() if integrity.exists() else '') + r'''
let failures=[];function check(name,test){reset();try{test();console.log('PASS '+name)}catch(e){failures.push(name+': '+e.message);}}
check('stale question selection cannot write another question',()=>{state.activeSession.index=1;selectPractice('q1',2);assert.deepEqual(state.activeSession.answers,{});});
check('out-of-range option rejected',()=>{selectPractice('q1',99);assert.deepEqual(state.activeSession.answers,{});});
check('old-session option callback rejected',()=>{selectPractice('q1',2,'old-session');assert.deepEqual(state.activeSession.answers,{});});
check('stale CBT option callback rejected',()=>{reset('exam');state.activeSession.index=1;selectExam(2,'q1','session');assert.deepEqual(state.activeSession.answers,{});});
check('failed correct answer rolls back selection and submitted state',()=>{const before=JSON.stringify(state);failed=true;selectPractice('q1',1);assert.equal(JSON.stringify(state),before);assert.equal(renders,0);});
check('failed wrong answer rolls back attempt and FSRS',()=>{const before=JSON.stringify(state);failed=true;selectPractice('q1',2);assert.equal(JSON.stringify(state),before);assert.equal(renders,0);});
check('failed Next preserves position and pending rating',()=>{selectPractice('q1',1);const before=JSON.stringify(state);failed=true;nextQ();assert.equal(JSON.stringify(state),before);});
check('bookmark failure does not claim success',()=>{const before=JSON.stringify(state);failed=true;toggleBookmark('q1');assert.equal(JSON.stringify(state),before);});
check('expired timed question cannot be changed',()=>{reset('exam');state.activeSession.strictExpired={q1:true};selectExam(2);assert.deepEqual(state.activeSession.answers,{});});
check('Review retry cannot mutate saved answers',()=>{reset('review');state.activeSession.answers.q1=2;state.activeSession.submitted.q1=true;const before=JSON.stringify(state);retryCurrent();assert.equal(JSON.stringify(state),before);});
check('submitted Practice cannot be retried in place',()=>{selectPractice('q1',2);const before=JSON.stringify(state);retryCurrent();assert.equal(JSON.stringify(state),before);});
check('FSRS context remains FSRS for the daily cap',()=>{state.activeSession.context='fsrs';assert.equal(nkFsrsSessionAttemptSource(state.activeSession),'fsrs-review');});
check('legacy FSRS origin does not hide its context',()=>{state.activeSession.context='fsrs';state.activeSession.originRoute='topics';assert.equal(nkFsrsSessionAttemptSource(state.activeSession),'fsrs-review');});
check('double submission and rating produce one attempt',()=>{selectPractice('q1',1);selectPractice('q1',2);submitPractice();nkRateCurrent(3);nkRateCurrent(3);assert.equal(state.attempts.q1.length,1);assert.equal(state.attempts.q1[0].selected,1);assert.equal(state.reviews.q1.repetitions,1);});
check('CBT selection changes before submission without FSRS',()=>{reset('exam');selectExam(1);selectExam(2);assert.equal(state.activeSession.answers.q1,2);assert.deepEqual(state.attempts,{});assert.deepEqual(state.reviews,{});});
check('one wrong-answer action has one durable commit',()=>{writes=0;selectPractice('q1',2);assert.equal(writes,1);assert.equal(state.attempts.q1.length,1);});
check('final submission commits a legacy selected answer to FSRS',()=>{state.activeSession.answers.q2=1;finishPracticeSession();assert.equal(state.attempts.q2?.length,1);assert.equal(state.reviews.q2.repetitions,1);});
check('history Back commits pending FSRS exactly once',()=>{selectPractice('q1',1);windowEvents.hashchange();assert.equal(state.attempts.q1.length,1);windowEvents.hashchange();assert.equal(state.attempts.q1.length,1);});
check('failed history Back restores route and pending work',()=>{selectPractice('q1',1);const before=JSON.stringify(state);failed=true;windowEvents.hashchange();assert.equal(JSON.stringify(state),before);assert.equal(historyTarget,'#practice');});
check('in-app subject navigation does not ask to exit Practice',()=>{navigate('banks','Biochemistry');route.page='practice';location.hash='#banks/Biochemistry';windowEvents.popstate();assert.equal(lastPrompt,'');assert.equal(route.page,'practice');});
check('browser Back Stay keeps Practice question and state',()=>{const before=JSON.stringify(state);windowEvents.popstate();assert.equal(location.hash,'#practice');assert.equal(JSON.stringify(state),before);assert(lastPrompt.includes('Do you want to exit?'));});
check('browser Back Exit leaves Practice route available',()=>{confirmed=true;windowEvents.popstate();assert.equal(location.hash,'#dashboard');assert.equal(state.activeSession.id,'session');});
check('browser Back warns during CBT',()=>{reset('exam');windowEvents.popstate();assert.equal(location.hash,'#exam');assert(lastPrompt.includes('timed test will keep running'));});
check('packaged Android uses native Back dialog only',()=>{location.hostname='qbank.local';windowEvents.popstate();assert.equal(location.hash,'#dashboard');assert.equal(lastPrompt,'');});
check('stale pointer and double-click are rejected',()=>{
 let stopped=0;const target={isConnected:true};const event={target:{closest:()=>target},detail:1,preventDefault:()=>{},stopImmediatePropagation:()=>stopped++};
 events.pointerdown(event);state.activeSession.index=1;events.click(event);assert.equal(stopped,1);
 events.click({...event,detail:2});assert.equal(stopped,2);
 events.pointerdown(event);events.click(event);assert.equal(stopped,2,'fresh distinct tap must work');
});
if(failures.length){console.error(failures.join('\n'));process.exit(1);}
console.log('QUESTION_INTERACTION_INTEGRITY_OK');
'''
    with tempfile.TemporaryDirectory() as tmp:
        test = Path(tmp) / 'interaction.js'
        test.write_text(runtime)
        subprocess.run(['node', str(test), str(ROOT / 'app/src/main/assets/vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js')], check=True)


if __name__ == '__main__':
    main()
