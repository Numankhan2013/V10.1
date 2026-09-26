#!/usr/bin/env python3
"""Exercise cumulative topic-test time, reload recovery, and final expiry."""

from pathlib import Path
import subprocess

from apply_home_command_center_v1 import HELPERS


def main() -> None:
    timer = "function nkStartTopicTimedTest" + HELPERS.split("function nkStartTopicTimedTest", 1)[1].split("/* NK_HOME_FLOW_V3_END */", 1)[0]
    script = r'''
const assert=require('node:assert/strict');
let now=1000000,submitted=null,saves=0,renders=0;
Date.now=()=>now;
const ids=['p1','p2','p3'];
const CHAPTER_BY_ID={topic:{title:'Topic'}},chapterQuestions=()=>ids.map(id=>({id}));
let state={activeSession:null};
const startSession=(questionIds,mode,title)=>{state.activeSession={id:'topic-test',questionIds:[...questionIds],mode,title,index:0,answers:{},questionTimes:{},startedAt:now,questionEnteredAt:now};};
const saveState=()=>{saves++;return true},render=()=>{renders++},showToast=()=>{};
const saveExamElapsed=()=>{const s=state.activeSession,id=s.questionIds[s.index];s.questionTimes[id]=(s.questionTimes[id]||0)+now-s.questionEnteredAt;s.questionEnteredAt=now;};
const submitExam=auto=>{submitted={auto,session:JSON.parse(JSON.stringify(state.activeSession))};state.activeSession=null;return true;};
let nextQ=()=>{const s=state.activeSession;saveExamElapsed();s.index=Math.min(s.index+1,s.questionIds.length-1);s.questionEnteredAt=now;saveState();render();};
let prevQ=()=>{const s=state.activeSession;saveExamElapsed();s.index=Math.max(0,s.index-1);s.questionEnteredAt=now;saveState();render();};
let goIndex=i=>{const s=state.activeSession;saveExamElapsed();s.index=i;s.questionEnteredAt=now;saveState();render();};
''' + timer + r'''
nkStartTopicTimedTest('topic');
assert.equal(state.activeSession.timerMode,'per-question');
now+=20000;nextQ();assert.equal(state.activeSession.strictQuestionTime.p1,20000);
now+=5000;prevQ();assert.equal(state.activeSession.strictQuestionTime.p2,5000);
// A persisted session restores its absolute entry time, so a reload cannot grant a fresh minute.
state=JSON.parse(JSON.stringify(state));
now+=39999;assert.equal(nkStrictSpent(state.activeSession,'p1'),59999);
now+=2;nkExpireTopicQuestion();
assert.equal(state.activeSession.strictExpired.p1,true);
assert.equal(state.activeSession.index,1);
assert.equal(state.activeSession.strictQuestionTime.p1,60000);
now+=55000;nkExpireTopicQuestion();assert.equal(state.activeSession.index,2);
assert.equal(state.activeSession.strictExpired.p2,true);
// A locked question cannot trap navigation after a jump.
goIndex(0);assert.equal(state.activeSession.index,2);
now+=60000;nkExpireTopicQuestion();
assert.equal(submitted.auto,true);
assert.equal(submitted.session.strictExpired.p3,true);
assert.equal(submitted.session.strictQuestionTime.p3,60000);
assert.equal(submitted.session.questionTimes.p3,60000);
assert(saves>3&&renders>3);
console.log('TOPIC_TIMER_OK cumulative=true reload=true lock=true final=true');
'''
    subprocess.run(['node', '-e', script], check=True, cwd=Path(__file__).resolve().parents[1])


if __name__ == '__main__':
    main()
