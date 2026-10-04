#!/usr/bin/env python3
"""Verify all-bank question search selection, safety, and transform anchors."""

from pathlib import Path
import json
import subprocess

from apply_question_search_v1 import CORE, NOTES_ROW, transform


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    fixture = (
        '<html><head></head><script>/* NK_QBANK_COVERAGE_V1_START NK_REVISION_DESK_V1_START */'
        "let route={page:'question-search'};function render(){let out='';if(false){} "
        "else if(route.page==='quick-revision') out=nkRevisionDeskPage();}"
        "function morePage(){return `<div>" + NOTES_ROW + "</div>`;}"
        "  window.QB={};</script></html>"
    )
    installed = transform(fixture)
    assert transform(installed) == installed
    for marker in ("NK_QUESTION_SEARCH_V1_START", "route.page==='question-search'",
                   "window.QB.nav('question-search')", "nkQuestionSearchPracticeMatches",
                   "Search every subject and bank", "nk-question-search-v1"):
        assert marker in installed, marker
    inline = installed.split("<script>", 1)[1].split("</script>", 1)[0]
    subprocess.run(["node", "--check"], input=inline, text=True, check=True)

    source = json.dumps(CORE.read_text(encoding="utf-8"))
    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const questions=[
 {id:'physiology-9-6',subject:'Physiology',bank:'PrepLadder',chapter:'Kidney physiology',chapterId:'9',questionNumber:6,question:'Which renal vessel carries blood?',options:[{text:'Afferent arteriole'},{text:'Efferent arteriole'}]},
 {id:'marrow__PHYS_CH01_Q001',subject:'Physiology',bank:'Marrow',chapter:'Kidney physiology',chapterId:'P1',questionNumber:1,question:'Glomerular filtration depends on pressure',options:[{text:'Hydrostatic pressure'}]},
 {id:'marrow__ANAT_CH01_Q001',subject:'Anatomy',bank:'Marrow',chapter:'Bones',chapterId:'A1',questionNumber:1,question:'Identify this bone',options:[{text:'Scapula'}]},
 {id:'biochemistry-1-1',subject:'Biochemistry',bank:'PrepLadder',chapter:'Metabolism',chapterId:'B1',questionNumber:1,question:'A rare enzyme deficit',options:[{text:'Glucose oxidase'}]}
];
for(let i=0;i<35;i++)questions.push({id:'bulk-'+i,subject:'Anatomy',bank:'PrepLadder',chapter:'Muscles',chapterId:'A2',questionNumber:i+1,question:'Muscle action '+i,options:[{text:'Flexion'}]});
questions.push({...questions[0]});
const state={attempts:{'physiology-9-6':[{id:'a',correct:false,at:1}],
 'marrow__PHYS_CH01_Q001':[{id:'b',correct:true,at:2}]},bookmarks:{'marrow__PHYS_CH01_Q001':{addedAt:3}},activeSession:null};
let opened=null,started=null,saved=0,toasts=[],referenceRead=null;const BY_ID={};
const context={state,BY_ID,Math,Date,window:{},document:{querySelector:()=>null},
 nkAllStudyQuestions:()=>questions,nkFsrsActiveAttempts:id=>state.attempts[id]||[],qAttempts:id=>state.attempts[id]||[],
 fmtNum:n=>String(n),esc:value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),
 navIcon:()=>'',shell:value=>value,showToast:message=>toasts.push(message),openBank:(subject,bank)=>opened=[subject,bank],
 startSession:(ids,mode,title,kind)=>{started={ids,mode,title,kind};state.activeSession={id:'new-session',mode,questionIds:ids,originRoute:'topics'};return true;},
 saveState:()=>{saved++;return true;}};
context.nkUworldEligible=q=>!q.blocked;
context.nkUworldReference=id=>{referenceRead=id;return true;};
vm.createContext(context);vm.runInContext(SOURCE,context);
const run=code=>vm.runInContext(code,context);
assert.equal(run('nkQuestionSearchIndex().length'),39,'duplicate bank IDs must not appear twice');
run("nkQuestionSearchQuery('kidney')");
assert.deepEqual(Array.from(run('nkQuestionSearchMatches().rows'),row=>row.id),['physiology-9-6','marrow__PHYS_CH01_Q001'],'topic text searches both banks');
run("nkQuestionSearchQuery('marrow__PHYS_CH01_Q001')");
assert.deepEqual(Array.from(run('nkQuestionSearchMatches().rows'),row=>row.id),['marrow__PHYS_CH01_Q001'],'exact question ID resolves');
run("nkQuestionSearchQuery('oxidase')");
assert.deepEqual(Array.from(run('nkQuestionSearchMatches().rows'),row=>row.id),['biochemistry-1-1'],'answer-option text is searchable without showing the answer');
run("nkQuestionSearchQuery('kidney')");run("nkQuestionSearchSetFilter('bank','Marrow')");
assert.deepEqual(Array.from(run('nkQuestionSearchMatches().rows'),row=>row.id),['marrow__PHYS_CH01_Q001'],'bank scope is exact');
run("nkQuestionSearchSetFilter('bank','')");run("nkQuestionSearchSetFilter('status','missed')");
assert.deepEqual(Array.from(run('nkQuestionSearchMatches().rows'),row=>row.id),['physiology-9-6'],'missed filter uses actual attempts');
run("nkQuestionSearchSetFilter('status','bookmarked')");
assert.deepEqual(Array.from(run('nkQuestionSearchMatches().rows'),row=>row.id),['marrow__PHYS_CH01_Q001'],'bookmark filter uses learner state');
run("nkQuestionSearchSetFilter('status','')");run("nkQuestionSearchQuery('')");
assert(run('nkQuestionSearchMatches().idle'),'blank search does not render thousands of questions');
run("nkQuestionSearchQuery('muscle')");
assert.equal(run('nkQuestionSearchMatches().rows.length'),35);
assert.equal((run('nkQuestionSearchResultsMarkup()').match(/nk-question-search-item/g)||[]).length,30,'result list is bounded');
run('nkQuestionSearchMore()');
assert.equal((run('nkQuestionSearchResultsMarkup()').match(/nk-question-search-item/g)||[]).length,35,'Show more reveals the remaining matches');
run('nkQuestionSearchPracticeMatches()');
assert.equal(started.ids.length,20,'batch Practice is bounded to 20 exact matches');
assert.equal(state.activeSession.originRoute,'question-search');
assert(saved>0,'search Practice route is persisted');
state.activeSession=null;run("nkQuestionSearchQuery('physiology-9-6')");
run("nkQuestionSearchOpen('physiology-9-6')");
assert.deepEqual(opened,['Physiology','PrepLadder']);
assert.deepEqual(Array.from(started.ids),['physiology-9-6'],'one result opens the exact question');
const previous=state.activeSession;state.activeSession={id:'exam',mode:'exam',questionIds:['exam-q']};
run("nkQuestionSearchOpen('marrow__PHYS_CH01_Q001')");run('nkQuestionSearchPracticeMatches()');
assert.equal(state.activeSession.id,'exam','search cannot replace an active timed test');
assert.equal(started.ids[0],'physiology-9-6','blocked search does not start Practice');
assert(toasts.some(message=>message.includes('timed test')));
assert(previous.id==='new-session');
// References remain findable without entering scored Practice, and a stale
// bank choice cannot hide a newly selected source collection.
state.activeSession=null;
for(let i=0;i<25;i++)questions.push({id:'uw-'+i,subject:'UWorld · Test collection',bank:'UWorld',chapter:'Block 1',question:'Source question '+i,options:[],blocked:i===0});
run("nkQuestionSearchCache=null;nkQuestionSearchQuery('');nkQuestionSearchSetFilter('bank','Marrow');nkQuestionSearchSetFilter('subject','UWorld · Test collection')");
assert.equal(run('nkQuestionSearchState.bank'),'');
assert.deepEqual(Array.from(run('nkQuestionSearchBanks()')),['UWorld']);
assert.equal(run('nkQuestionSearchMatches().rows.length'),25);
assert(!run('nkQuestionSearchPage()').includes('value="Marrow"'));
run("nkQuestionSearchQuery('uw-0')");
assert(run('nkQuestionSearchResultsMarkup()').includes('Read reference'));
assert(!run('nkQuestionSearchResultsMarkup()').includes('Practice first'));
const savedBefore=saved,openedBefore=opened,startedBefore=started;
run("nkQuestionSearchOpen('uw-0')");
assert.equal(referenceRead,'uw-0');assert.equal(state.activeSession,null);
assert.equal(opened,openedBefore);assert.equal(started,startedBefore);assert.equal(saved,savedBefore);
run("nkQuestionSearchQuery('');nkQuestionSearchPracticeMatches()");
assert.deepEqual(Array.from(started.ids),Array.from({length:20},(_,i)=>'uw-'+(i+1)));
assert.equal(state.activeSession.originRoute,'question-search');
run("nkQuestionSearchSetFilter('bank','UWorld');nkQuestionSearchSetFilter('subject','Physiology')");
assert.equal(run('nkQuestionSearchState.bank'),'');
assert.deepEqual(Array.from(run('nkQuestionSearchBanks()')),['Marrow','PrepLadder']);
run("nkQuestionSearchSetFilter('bank','Marrow');nkQuestionSearchSetFilter('subject','Anatomy')");
assert.equal(run('nkQuestionSearchState.bank'),'Marrow','valid bank selection survives a subject change');
console.log('QUESTION_SEARCH_BEHAVIOR_OK banks=true text=true id=true filters=true paging=true practice=true testGuard=true');
'''.replace("SOURCE", source, 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("QUESTION_SEARCH_INSTALL_OK")


if __name__ == "__main__":
    main()
