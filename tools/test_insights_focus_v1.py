#!/usr/bin/env python3
"""Verify cross-bank evidence, latest-answer recovery, and direct Practice entry."""

from pathlib import Path
import subprocess

from apply_insights_focus_v1 import transform


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/insights_focus_core.js"


def main() -> None:
    fixture = (
        '<html><head></head><script>/* NK_REVISION_DESK_V1_START */'
        'function analytics(){return `<main>'
        '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">CHAPTER PERFORMANCE</div>'
        '</main>`;}  window.QB={nav:()=>{}};</script></html>'
    )
    generated = transform(fixture)
    assert transform(generated) == generated
    for marker in ("NK_INSIGHTS_FOCUS_V1_START", "${nkInsightsFocusSection()}",
                   "nkPracticeInsightFocus", "nk-insights-focus-v1"):
        assert marker in generated, marker
    inline = generated.split("<script>", 1)[1].split("</script>", 1)[0]
    subprocess.run(["node", "--check"], input=inline, text=True, check=True)

    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const questions=[
  ...['a1','a2','a3','a4'].map(id=>({id,subject:'Anatomy',bank:'Marrow',chapterId:'A1'})),
  ...['p1','p2','p3'].map(id=>({id,subject:'Anatomy',bank:'PrepLadder',chapterId:'A1'})),
  ...['v1','v2'].map(id=>({id,subject:'Physiology',bank:'Marrow',chapterId:'P1'}))
];
const attempts={a1:[{id:'1',correct:false}],a2:[{id:'2',correct:false}],a3:[{id:'3',correct:true}],
  a4:[{id:'4',correct:false},{id:'5',correct:true}],p1:[{id:'6',correct:true}],p2:[{id:'7',correct:true}],
  p3:[{id:'8',correct:true}],v1:[{id:'9',correct:false}],v2:[{id:'10',correct:false}]};
const state={attempts,activeSession:null},BANKS_BY_SUBJECT={
  Anatomy:[{subject:'Anatomy',bank:'Marrow',topics:[{id:'A1',title:'Thorax'}]},
           {subject:'Anatomy',bank:'PrepLadder',topics:[{id:'A1',title:'Other Anatomy'}]}],
  Physiology:[{subject:'Physiology',bank:'Marrow',topics:[{id:'P1',title:'Circulation'}]}]
};
let started=null,opened=null,rendered=0;
const context={state,BANKS_BY_SUBJECT,BY_ID:{},Math,JSON,encodeURIComponent,decodeURIComponent,
  nkAllStudyQuestions:()=>questions,nkFsrsActiveAttempts:id=>attempts[id]||[],
  qAttempts:id=>attempts[id]||[],openBank:(subject,bank)=>{opened=[subject,bank]},
  startSession:(ids,mode,title,origin)=>{started={ids,mode,title,origin}},
  showToast:()=>{},render:()=>{rendered++},fmtNum:String,esc:String,navIcon:()=>''};
vm.createContext(context);vm.runInContext(SOURCE,context);
const call=code=>vm.runInContext(code,context);
let result=call('nkInsightsFocusRows()');
assert.equal(result.recommended.length,1);
assert.equal(result.recommended[0].title,'Thorax');
assert.deepEqual(Array.from(result.recommended[0].missed,q=>q.id),['a1','a2'],
  'the latest correct answer removes an old miss');
assert.equal(result.recommended[0].answered,4,'same-name bank topics stay separate');
assert(call('nkInsightsFocusSection()').includes('Thorax'));
call("nkPracticeInsightFocus('"+encodeURIComponent(result.recommended[0].key)+"')");
assert.deepEqual(opened,['Anatomy','Marrow']);
assert.deepEqual(Array.from(started.ids).sort(),['a1','a2']);
assert.equal(started.mode,'practice');assert.equal(started.origin,'wrong');
attempts.a1.push({id:'11',correct:true});
result=call('nkInsightsFocusRows()');
assert.equal(result.recommended.length,0,'improvement removes the recommendation');
assert(call('nkInsightsFocusSection()').includes('No topic needs a targeted retry'));
state.attempts={};Object.keys(attempts).forEach(id=>delete attempts[id]);
assert(call('nkInsightsFocusSection()').includes('Keep studying to reveal your focus areas'),
  'no evidence has a distinct state');
console.log('INSIGHTS_FOCUS_BEHAVIOR_OK banks=true latest=true practice=true emptyStates=true');
'''.replace("SOURCE", repr(CORE.read_text(encoding="utf-8")), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("INSIGHTS_FOCUS_INSTALL_OK")


if __name__ == "__main__":
    main()
