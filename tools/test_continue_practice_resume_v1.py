#!/usr/bin/env python3
"""Behavior and transformation contracts for durable Continue Practice."""

from pathlib import Path
import subprocess
import tempfile

from apply_continue_practice_resume_v1 import END, START, STYLE_ID, transform

ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / "tools/continue_practice_resume_core.js").read_text(encoding="utf-8")


def run_node_behavior() -> None:
    runtime = r'''
const assert=require('assert');
global.window={QB:{}};global.document={getElementById:()=>null};global.setTimeout=fn=>fn();
let route={page:'practice'},saved=0,oldContinueCalls=0,opened=null,started=null;
const make=(topic,count,start=1)=>Array.from({length:count},(_,i)=>({id:`q${start+i}`,subject:'Anatomy',bank:'Marrow',chapterId:topic,chapter:topic==='t1'?'Topic One':'Topic Two'}));
const questions=[...make('t1',20),...make('t2',3,21)],BY_ID=Object.fromEntries(questions.map(q=>[q.id,q]));
const SUBJECTS=[{subject:'Anatomy',bank:'Marrow',topics:[{id:'t1',title:'Topic One'},{id:'t2',title:'Topic Two'}],questions}];
let state={attempts:{},tests:[],activeSession:null,fsrsReviewEligible:{}};
const activeSubject='Anatomy',nkFindStudyQuestion=id=>BY_ID[id]||null,nkTopicTitleForQuestion=q=>q.chapter;
const nkBankRecords=subject=>SUBJECTS.filter(r=>r.subject===subject),qAttempts=id=>state.attempts[id]||[];
const saveState=()=>{saved++},navigate=page=>{route.page=page},openBank=()=>{},openSubjectTopics=()=>{};
const nkOpenSubjectChapter=(subject,bank,topicId)=>{opened={subject,bank,topicId}};
const startSession=(ids,mode,title)=>{started={ids:[...ids],mode,title};state.activeSession={id:'new',mode,title,questionIds:[...ids],index:0,answers:{},submitted:{},questionTimes:{}}};
const savePracticeElapsed=()=>{},nkMarkSkippedFromSession=s=>{const id=s.questionIds[s.index];if(!s.submitted[id])state.fsrsReviewEligible[id]={reason:'skipped'}};
const endSession=()=>finishPracticeSession();
let finishPracticeSession=()=>{const s=state.activeSession;state.tests.push({id:'done',kind:'practice',questionIds:[...s.questionIds],createdAt:99});state.activeSession=null;};
let practiceActionBar=()=>'<div class="fixed-actions nk-session-footer"><div class="fixed-actions-inner"><button>Previous</button><button>Next</button></div></div>';
let openSessionReview=()=>{};
let nkLatestPracticeContext=()=>null;
let nkContinueRecentPractice=()=>{oldContinueCalls++};
''' + CORE + r'''
window.QB={nkPausePractice,nkSubmitPracticeSession,openSessionReview};

const full=Array.from({length:20},(_,i)=>`q${i+1}`);
state.activeSession={id:'same-session',mode:'practice',title:'Topic One',questionIds:[...full],index:4,
  answers:{q1:1,q2:1,q3:1,q4:2},submitted:{q1:true,q2:true,q3:true,q4:true},questionTimes:{q5:25}};
assert.equal(nkPausePractice(),true);assert.equal(route.page,'dashboard');assert.equal(state.activeSession.lifecycle,'paused');
assert.equal(state.fsrsReviewEligible.q5,undefined);assert.equal(state.activeSession.id,'same-session');
assert.deepEqual(state.activeSession.sessionQuestionIds,full);assert.equal(state.activeSession.pausedIndex,4);
nkContinueRecentPractice();
assert.equal(route.page,'practice');assert.equal(state.activeSession.id,'same-session');assert.equal(state.activeSession.lifecycle,'active');
assert.deepEqual(state.activeSession.questionIds,full);
assert.equal(state.activeSession.index,4);assert.equal(state.activeSession.questionIds[state.activeSession.index],'q5');
assert.equal(state.activeSession.submitted.q1,true);assert.equal(Boolean(state.activeSession.submitted.q5),false);assert.equal(oldContinueCalls,0);

// Regression: even if an older buggy build persisted only one visible question,
// sessionQuestionIds remains the canonical test and Continue Practice must restore it.
state.activeSession.lifecycle='paused';state.activeSession.questionIds=['q5'];state.activeSession.index=0;state.activeSession.pausedIndex=4;
nkContinueRecentPractice();
assert.deepEqual(state.activeSession.questionIds,full);assert.equal(state.activeSession.index,4);assert.equal(state.activeSession.questionIds[4],'q5');

for(const id of state.activeSession.questionIds)state.activeSession.submitted[id]=true;
nkSubmitPracticeSession();
assert.equal(state.activeSession,null);assert.equal(state.tests.at(-1).questionIds.length,20);
assert.equal(state.tests.at(-1).practiceContext.topicId,'t1');assert.equal(state.tests.at(-1).practiceContext.completed,true);

for(let i=1;i<=20;i++)state.attempts[`q${i}`]=[{at:i,correct:true}];
started=null;opened=null;nkContinueRecentPractice();
assert.deepEqual(opened,{subject:'Anatomy',bank:'Marrow',topicId:'t2'});assert.equal(started,null);

state.tests=[{id:'partial',kind:'practice',createdAt:100,practiceContext:{subject:'Anatomy',bank:'Marrow',topicId:'t1',title:'Topic One'}}];
delete state.attempts.q18;delete state.attempts.q19;delete state.attempts.q20;started=null;opened=null;
nkContinueRecentPractice();assert.deepEqual(started.ids,['q18','q19','q20']);assert.equal(started.mode,'practice');

state.activeSession={mode:'practice',studyModuleId:'module-1',questionIds:['q1'],index:0,answers:{},submitted:{}};
assert.equal(nkPausePractice(),false);assert.equal(practiceActionBar().includes('nk-practice-session-controls'),false);

state.activeSession={mode:'practice',title:'Wrong Questions',questionIds:['q1'],index:0,answers:{},submitted:{}};
assert.equal(nkPausePractice(),false);assert.equal(practiceActionBar().includes('nk-practice-session-controls'),false);

state.activeSession={mode:'practice',questionIds:['q1'],index:0,answers:{},submitted:{}};
const bar=practiceActionBar();assert(bar.includes('>Pause<')&&bar.includes('>Submit<'));assert(bar.indexOf('>Pause<')<bar.indexOf('>Submit<'));
console.log('CONTINUE_PRACTICE_BEHAVIOR_OK full_session=20 saved_index=4 single_question_regression=covered');
'''
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "continue-practice-test.js"
        path.write_text(runtime, encoding="utf-8")
        subprocess.run(["node", str(path)], check=True, cwd=ROOT)


def test_transform() -> None:
    fixture = '''<html><head></head><body><script>
<style id="v102-practice-layer">button.v102-practice-submit-hidden{display:none}</style>
<script id="v102-practice-layer-script">legacy submit hider</script>
function nkLatestPracticeContext(){return null;} function nkContinueRecentPractice(){return null;}
function finishPracticeSession(){} function practiceActionBar(){return '<div class="fixed-actions-inner"></div>';}
function openSessionReview(){} function endSession(){} function saveState(){} function navigate(){}
/* NK_HOME_FLOW_V3_END */
window.QB={};
</script></body></html>'''
    updated = transform(fixture)
    assert transform(updated) == updated
    for marker in (START, END, STYLE_ID, "nkPausePractice,nkSubmitPracticeSession,", "sessionQuestionIds", "practiceContext", ">Pause<", ">Submit<"):
        assert marker in updated, marker
    assert "v102-practice-submit-hidden" not in updated
    assert "v102-practice-layer-script" not in updated


def main() -> None:
    test_transform()
    run_node_behavior()
    workflow = (ROOT / ".github/workflows/build-apk.yml").read_text(encoding="utf-8")
    gate = (ROOT / ".github/workflows/engineering-gate.yml").read_text(encoding="utf-8")
    assert workflow.index("tools/apply_home_command_center_v1.py") < workflow.index("tools/apply_continue_practice_resume_v1.py") < workflow.index("tools/apply_cross_device_pwa_v1.py")
    assert "tools/test_continue_practice_resume_v1.py" in workflow and "tools/test_continue_practice_resume_v1.py" in gate
    print("CONTINUE_PRACTICE_CONTRACT_OK durable_pause=true full_session_resume=true canonical_next_topic=true")


if __name__ == "__main__":
    main()
