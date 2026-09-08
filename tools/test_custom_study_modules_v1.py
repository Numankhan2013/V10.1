#!/usr/bin/env python3
"""Behavior and integration checks for Custom Study Modules."""

from pathlib import Path
import json
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / "tools/study_modules_core.js").read_text(encoding="utf-8")
HTML = ROOT / "app/src/main/assets/index.html"


NODE_TEST = r'''
const assert=require('node:assert/strict');
const vm=require('node:vm');

const biochemQuestions=[];
for(let i=1;i<=35;i++)biochemQuestions.push({id:`bio-gly-${i}`,subject:'Biochemistry',chapterId:'gly',chapter:'Glycolysis',question:`Glycolysis ${i}`,options:[],correctOption:1});
biochemQuestions.push({id:'bio-carb-1',subject:'Biochemistry',chapterId:'carb',chapter:'Carbohydrate Metabolism',question:'Carbohydrate 1',options:[],correctOption:1});
const anatomyQuestions=[{id:'anat-1',subject:'Anatomy',chapterId:'upper',chapter:'Upper Limb',question:'Anatomy',options:[],correctOption:1}];
const SUBJECTS=[
  {subject:'Biochemistry',topics:[{id:'gly',title:'Glycolysis',questionCount:35},{id:'carb',title:'Carbohydrate Metabolism',questionCount:1}],questions:biochemQuestions},
  {subject:'Anatomy',topics:[{id:'upper',title:'Upper Limb',questionCount:1}],questions:anatomyQuestions}
];
const all=SUBJECTS.flatMap(x=>x.questions),BY_ID=Object.fromEntries(all.map(q=>[q.id,q]));
const state={attempts:{},bookmarks:{},studyModules:[],tests:[],activeSession:null};
state.attempts['bio-gly-1']=[{correct:false}];
state.attempts['bio-gly-2']=[{correct:false},{correct:true}];
state.bookmarks['bio-gly-2']={addedAt:1};
state.attempts['bio-gly-35']=[{correct:true}];
const ctx={SUBJECTS,BY_ID,state,activeSubject:'Biochemistry',Date,Math,Set,Map,console,
  qAttempts:id=>state.attempts[id]||[],fmtNum:String,fmtPct:x=>`${Math.round(x)}%`,esc:String,
  navIcon:()=>'',nkAppSubjectStats:()=>({questions:1,topics:1}),nkAppSubjectMeta:()=>({key:'x'}),nkAppSubjectIcon:()=>'',
  document:{getElementById:()=>null},window:{QB:{}},showToast:()=>{},render:()=>{},navigate:()=>{},saveState:()=>{},confirm:()=>true,prompt:()=>null,
  closeSessionReview:()=>{},finishPracticeSession:()=>{},shell:x=>x,nkAppPageHead:()=>''};
vm.createContext(ctx);vm.runInContext(CORE,ctx);
const run=code=>vm.runInContext(code,ctx);

// A: wrong questions are scoped to the selected Biochemistry topics.
run(`studyModuleDraft={subjectIds:['Biochemistry'],topicIds:['Biochemistry::gly','Biochemistry::carb'],questionPoolType:'wrong',questionCount:20}`);
assert.deepEqual([...run(`nkSelectModuleQuestionIds(studyModuleDraft,'a')`)].sort(),['bio-gly-1','bio-gly-2']);

// C: a request for 30 unattempted questions safely contracts to the 17 available.
for(let i=3;i<=17;i++)state.attempts[`bio-gly-${i}`]=[{correct:true}];
run(`studyModuleDraft={subjectIds:['Biochemistry'],topicIds:['Biochemistry::gly'],questionPoolType:'unattempted',questionCount:30}`);
const contracted=[...run(`nkSelectModuleQuestionIds(studyModuleDraft,'c')`)];
assert.equal(contracted.length,17);

// D: overlap between Wrong and Bookmarked never duplicates a question in Mixed.
run(`studyModuleDraft={subjectIds:['Biochemistry'],topicIds:['Biochemistry::gly'],questionPoolType:'mixed',questionCount:30}`);
const mixed=[...run(`nkSelectModuleQuestionIds(studyModuleDraft,'d')`)];
assert.equal(new Set(mixed).size,mixed.length);
assert.equal(mixed.filter(id=>id==='bio-gly-2').length,1);
assert.ok(mixed.indexOf('bio-gly-1')<mixed.length-1);

// B/G: the frozen set and a 12/30 session snapshot survive serialization and resume math.
const stable=biochemQuestions.slice(0,30).map(q=>q.id);
state.studyModules=[run(`nkNormalizeStudyModule(${JSON.stringify({id:'m1',name:'Carbohydrates revision — Sunday',subjectIds:['Biochemistry'],topicIds:['Biochemistry::gly'],questionPoolType:'mixed',questionIds:stable,totalQuestions:30,createdAt:10,lastOpenedAt:10})})`)];
const submitted=Object.fromEntries(stable.slice(0,12).map(id=>[id,true]));
state.activeSession={studyModuleId:'m1',questionIds:stable,index:12,answers:{},submitted,questionTimes:{}};
run('nkSyncModuleFromSession()');
assert.equal(run(`nkModuleProgress(nkFindStudyModule('m1')).remaining`),18);
const frozen=JSON.stringify(state.studyModules[0].questionIds);
state.attempts={};state.bookmarks={};
assert.equal(JSON.stringify(state.studyModules[0].questionIds),frozen);
const saved=JSON.parse(JSON.stringify(state.studyModules));state.studyModules=saved;run('nkNormalizeStudyModules()');
assert.equal(run(`nkModuleProgress(nkFindStudyModule('m1')).remaining`),18);

// F: Home chooses the most recently opened unfinished module.
state.activeSession=null;
state.studyModules.push(run(`nkNormalizeStudyModule(${JSON.stringify({id:'m2',name:'Older',subjectIds:['Anatomy'],topicIds:['Anatomy::upper'],questionPoolType:'mixed',questionIds:['anat-1'],createdAt:5,lastOpenedAt:5})})`));
assert.equal(run('nkPriorityStudyModule().id'),'m1');
state.studyModules[0].isCompleted=true;
assert.equal(run('nkPriorityStudyModule().id'),'m2');

console.log('CUSTOM_STUDY_MODULE_BEHAVIOR_OK: filters, caps, deduplication, stable IDs, 12/30 resume, persistence, and Home priority');
'''


def main() -> None:
    subprocess.run(
        ["node", "-"],
        input="const CORE=" + json.dumps(CORE) + ";\n" + NODE_TEST,
        text=True,
        check=True,
    )
    if HTML.exists():
        html = HTML.read_text(encoding="utf-8")
        if 'id="nk-custom-study-modules-v1"' in html:
            required = [
                "studyModules: []",
                "route.page==='module-builder'",
                "studyModuleId:s.studyModuleId||null",
                "s.studyModuleId?'study-module':'practice'",
                "nkStudySetsSection()",
                "Review Solutions",
                "Save & exit",
                "Finish with ${unanswered} omitted",
            ]
            missing = [marker for marker in required if marker not in html]
            if missing:
                raise SystemExit(f"Generated module integration missing: {missing}")
            print("CUSTOM_STUDY_MODULE_INTEGRATION_OK: session, Home, completion, review, and unified-history hooks present")


if __name__ == "__main__":
    main()
