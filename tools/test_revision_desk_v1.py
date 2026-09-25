#!/usr/bin/env python3
"""Check all-bank revision pools and install points without changing app assets."""

from pathlib import Path
import subprocess

from apply_revision_desk_v1 import transform


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/revision_desk_core.js"


def main() -> None:
    rows = "${row('refresh','Wrong questions',`${fmtNum(wrong)} missed · retrieval practice`,\"window.QB.nav('wrong')\",'is-red')}${row('bookmark','Bookmarks',`${fmtNum(bm)} saved by you`,\"window.QB.nav('bookmarks')\",'is-violet')}${row('book','My notes',`${fmtNum(nkSavedQuestionNotes().length)} recall cues`,\"window.QB.nav('notes')\")}"
    fixture = (
        '<html><head></head><script>/* NK_QUESTION_NOTES_V1_START */'
        'let route={page:"notes"};function render(){let out="";if(false){} else if(route.page===\'notes\') out=nkNotesPage();}'
        'function morePage(){const bm=bookmarkedQuestions().length,wrong=wrongQuestions().length;'
        'return `<div>' + rows + '</div>`; }'
        '  window.QB={nkFilterNotes,nkOpenNotedQuestion,};</script></html>'
    )
    generated = transform(fixture)
    assert transform(generated) == generated
    for marker in ('NK_REVISION_DESK_V1_START', 'nkRevisionDeskPage()', 'nkRevisionBrowsePage(route.id)',
                   'nkStartRevisionQueue', 'nkOpenRevisionQuestion',
                   "route.page==='quick-revision'", "window.QB.nav('quick-revision')",
                   'All subjects', 'All question banks', 'nkSetRevisionScope',
                   'nkToggleRevisionFocus', '20 questions per session'):
        assert marker in generated, marker
    inline = generated.split("<script>", 1)[1].split("</script>", 1)[0]
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
const context={state,Math,Date,BY_ID:{},document:{querySelector:()=>null},qAttempts:id=>state.attempts[id]||[],
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
call("nkSetRevisionScope('subject','')");
for(let i=0;i<25;i++){const id='wrong-'+i;questions.push({id,subject:i%2?'Anatomy':'Physiology',bank:i%2?'Marrow':'PrepLadder'});state.attempts[id]=[{id:'wrong-attempt-'+i,correct:false,at:i+10}];}
call("nkStartRevisionQueue('wrong')");
assert.equal(started.ids.length,20,'Quick revision keeps a mistake session to 20 questions');
assert.equal(new Set(started.ids).size,20,'a revision sample contains unique question IDs');
assert(started.ids.every(id=>id==='anat-wrong'||id.startsWith('wrong-')),'mistake session contains only mistake questions');
console.log('REVISION_DESK_BEHAVIOR_OK globalPools=true skippedExcluded=true dueUsesFSRS=true');
'''.replace("SOURCE", repr(CORE.read_text(encoding="utf-8")), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("REVISION_DESK_INSTALL_OK")


if __name__ == "__main__":
    main()
