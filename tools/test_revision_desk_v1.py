#!/usr/bin/env python3
"""Check all-bank revision pools and their install points in the shipped page."""

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/revision_desk_core.js"
SESSION_CORE = ROOT / "tools/revision_session_core.js"
HTML = ROOT / "app/src/main/assets/index.html"


def main() -> None:
    page = HTML.read_text(encoding="utf-8")
    start = page.index("function bottomNav(active){")
    bottom_nav = page[start:page.index("\n  }\n", start) + 4]
    assert page.count('class="bottom-nav ') == 1
    assert "['fsrs','FSRS','refresh']" not in page
    assert "const bm=bookmarkedQuestions().length,wrong=wrongQuestions().length;" not in page
    assert "${row('refresh','Wrong questions'" not in page, "More keeps only notes; Revision owns the queues"
    for core in (CORE, SESSION_CORE):
        assert page.count(core.read_text(encoding="utf-8").strip()) == 1, core.name
    qb = page[page.index("  window.QB={"):]
    qb = qb[:qb.index("};")]
    for action in ('nkFinishRevisionSession', 'nkStartRevisionQueue', 'nkFilterRevisionBrowse',
                   'nkOpenRevisionQuestion', 'nkToggleRevisionFocus', 'nkSetRevisionScope', 'nkOpenRevisionHub'):
        assert action + ',' in qb, action
    for marker in ('NK_REVISION_DESK_V1_START', 'id="nk-revision-desk-v1"',
                   "else if(route.page==='quick-revision') out=nkRevisionDeskPage();",
                   "else if(route.page==='revision-browse') out=nkRevisionBrowsePage(route.id);",
                   "${row('book','My notes',`${fmtNum(nkSavedQuestionNotes().length)} recall cues`,\"window.QB.nav('notes')\",'is-violet')}",
                   'All subjects', 'All question banks', '20 questions per session'):
        assert marker in page, marker
    for match in re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>", page):
        inline = page[match.end():page.index("</script>", match.end())]
        if inline.strip():
            subprocess.run(["node", "--check"], input=inline, text=True, check=True)

    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const questions=[
 {id:'anat-wrong',subject:'Anatomy',bank:'Marrow',chapterId:'A1'},
 {id:'bio-bookmark',subject:'Biochemistry',bank:'PrepLadder',chapterId:'B1'},
 {id:'phys-unseen',subject:'Physiology',bank:'Marrow',chapterId:'P1'},
 {id:'phys-due',subject:'Physiology',bank:'PrepLadder',chapterId:'P2'},
 {id:'anat-unseen',subject:'Anatomy',bank:'PrepLadder',chapterId:'A2'}
];
const state={attempts:{'anat-wrong':[{id:'a1',correct:false,at:1}],
 'bio-bookmark':[{id:'a2',correct:true,at:2}],
 'phys-due':[{id:'a3',correct:true,at:3}]},
 bookmarks:{'bio-bookmark':{addedAt:1}},fsrsReviewEligible:{'phys-unseen':{reason:'skipped'}}};
let started=null;
const context={state,Math,Date,BY_ID:{},route:{page:"dashboard"},bottomNav:()=>"",
 dashboard:()=>'<section class="nk-section nk-study-sets"></section>',navigate:page=>{context.route.page=page;},
 nkReviewPool:subject=>questions.filter(q=>(!subject||q.subject===subject)&&state.attempts[q.id]?.length),document:{querySelector:()=>null},qAttempts:id=>state.attempts[id]||[],
 nkAllStudyQuestions:()=>questions,
 nkBankRecord:(subject,bank)=>({topics:questions.filter(q=>q.subject===subject&&q.bank===bank).map(q=>({id:q.chapterId,title:q.chapterId+' title'}))}),
 nkFsrsActiveAttempts:id=>(state.attempts[id]||[]).filter(a=>!a.isUndo),
 nkFsrsEligibility:q=>q.id==='anat-wrong'||q.id.startsWith('wrong-')?'wrong':(['phys-due','bio-bookmark','anat-due'].includes(q.id)?'attempted':''),
 nkFsrsQueue:filters=>{const due=questions.filter(q=>['phys-due','anat-due'].includes(q.id)&&(!filters.subject||q.subject===filters.subject)&&(!filters.bank||q.bank===filters.bank)&&(!filters.topic||q.chapterId===filters.topic));return{due,cards:due,rolledOver:0};},
 startSession:(ids,mode,title,kind)=>{started={ids,mode,title,kind};},
 showToast:()=>{},fmtNum:String,esc:String,navIcon:()=>'',shell:x=>x,nkAppPageHead:()=>'',nkAppEmpty:()=>''};
vm.createContext(context);vm.runInContext(SOURCE,context);
const call=code=>vm.runInContext(code,context);
const pools=call('nkRevisionDeskData()');
assert.deepEqual(Array.from(pools.wrong,q=>q.id),['anat-wrong']);
assert.deepEqual(Array.from(pools.bookmarked,q=>q.id),['bio-bookmark']);
assert.deepEqual(Array.from(pools.unseen,q=>q.id),['anat-unseen'],'submitted skips stay out of unseen');
assert.deepEqual(Array.from(pools.due,q=>q.id),['phys-due']);
state.attempts['anat-wrong'].push({id:'corrected',correct:true,at:4});
assert.equal(call('nkRevisionDeskData().wrong.length'),0,'corrected mistakes leave the queue without erasing history');
state.attempts['anat-wrong'].pop();
call("nkStartRevisionQueue('wrong')");
assert.equal(started.mode,'practice');assert.equal(started.kind,'wrong');assert.deepEqual(started.ids,['anat-wrong']);
call("nkStartRevisionQueue('due')");
assert.equal(started.kind,'fsrs');assert.equal(started.title,'Quick Revision · Due Review');
assert.deepEqual(started.ids,['phys-due']);
questions.push({id:'anat-due',subject:'Anatomy',bank:'Marrow',chapterId:'A2'});
state.attempts['anat-due']=[{id:'a4',correct:true,at:4}];
call("nkSetRevisionScope('subject','Anatomy')");
assert.deepEqual(Array.from(call('nkRevisionDeskData().due'),q=>q.id),['anat-due'],'Due respects subject focus');
call("nkSetRevisionScope('bank','Marrow')");
assert.deepEqual(Array.from(call('nkRevisionDeskData().unseen'),q=>q.id),[],'Bank focus excludes PrepLadder unseen');
call("nkSetRevisionScope('topic','A1')");
assert.deepEqual(Array.from(call('nkRevisionDeskData().wrong'),q=>q.id),['anat-wrong']);
assert.deepEqual(Array.from(call('nkRevisionDeskData().due'),q=>q.id),[],'Topic focus excludes other due topics');
call("nkStartRevisionQueue('wrong')");
assert.deepEqual(started.ids,['anat-wrong'],'Focused mistake session contains only the chosen topic');
call("nkSetRevisionScope('topic','A2')");
call("nkStartRevisionQueue('due')");
assert.deepEqual(started.ids,['anat-due'],'Focused Due session uses its filtered FSRS queue');
// Global reminders must not inherit a focused revision queue.
const focusedHome=call('nkHomeRevisionSummary()');
assert(focusedHome.includes('2 due reviews')&&focusedHome.includes('1 missed questions'));
assert(call('dashboard()').indexOf('nk-home-revision')<call('dashboard()').indexOf('nk-study-sets'));
let nav=call('bottomNav("dashboard")');
assert(nav.includes('Revision')&&!nav.includes('>FSRS<'));
context.route.page='fsrs';nav=call('bottomNav("fsrs")');
assert(nav.includes('nav-item active')&&nav.includes('nkOpenRevisionHub()'));
const now=new Date();now.setHours(0,0,0,0);
state.reviews={'anat-due':{due:now.getTime()-1000},'phys-due':{due:now.getTime()+86400000}};
let chart=call('nkRevisionForecastMarkup()');
assert(chart.includes('Today: 1 reviews')&&!chart.includes(': 2 reviews'));
call('nkOpenRevisionHub()');
assert.equal(context.route.page,'quick-revision');
assert.equal(call('nkRevisionScopeLabel()'),'All subjects · All question banks');
chart=call('nkRevisionForecastMarkup()');
assert(chart.includes('Today: 3 reviews'),'unmigrated eligible attempts appear in today forecast');
// The displayed due count includes rollover; the session remains capped.
context.nkFsrsQueue=()=>({due:questions.slice(0,3),cards:[questions[0]],rolledOver:2});
assert.equal(call('nkRevisionDeskData().due.length'),3);
call("nkStartRevisionQueue('due')");assert.deepEqual(started.ids,['anat-wrong']);
context.nkFsrsQueue=filters=>{const due=questions.filter(q=>['phys-due','anat-due'].includes(q.id)&&(!filters.subject||q.subject===filters.subject)&&(!filters.bank||q.bank===filters.bank)&&(!filters.topic||q.chapterId===filters.topic));return{due,cards:due,rolledOver:0};};

call("nkSetRevisionScope('subject','')");
for(let i=0;i<25;i++){const id='wrong-'+i;questions.push({id,subject:i%2?'Anatomy':'Physiology',bank:i%2?'Marrow':'PrepLadder'});state.attempts[id]=[{id:'wrong-attempt-'+i,correct:false,at:i+10}];}
call("nkStartRevisionQueue('wrong')");
assert.equal(started.ids.length,26,'Revision snapshots the full eligible mistake queue');
assert.equal(new Set(started.ids).size,26,'a revision snapshot contains unique question IDs');
assert(started.ids.every(id=>id==='anat-wrong'||id.startsWith('wrong-')),'mistake session contains only mistake questions');
// Browse queries are scoped to kind and account, and timed tests remain protected.
context.nkAuth={uid:'account-one'};context.route={page:'revision-browse',id:'bookmarks'};
context.document.querySelectorAll=()=>[];
call("nkRevisionBrowsePage('bookmarks')");call("nkFilterRevisionBrowse('Biochemistry')");
assert(call("nkRevisionBrowsePage('bookmarks')").includes('value="Biochemistry"'));
assert(call("nkRevisionBrowsePage('wrong')").includes('value=""'));
context.nkAuth.uid='account-two';assert(call("nkRevisionBrowsePage('bookmarks')").includes('value=""'));
context.nkFindStudyQuestion=id=>questions.find(q=>q.id===id);context.saveState=()=>true;
state.activeSession={id:'protected-exam',mode:'exam'};const oldStart=started;
call("nkOpenRevisionQuestion('bio-bookmark')");assert.equal(started,oldStart);assert.equal(state.activeSession.id,'protected-exam');
console.log('REVISION_DESK_BEHAVIOR_OK globalPools=true skippedExcluded=true dueUsesFSRS=true');
'''.replace("SOURCE", repr(CORE.read_text(encoding="utf-8") + '\n' + bottom_nav), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("REVISION_DESK_INSTALL_OK")
    from test_revision_session_v1 import main as verify_revision_sessions
    verify_revision_sessions()


if __name__ == "__main__":
    main()
