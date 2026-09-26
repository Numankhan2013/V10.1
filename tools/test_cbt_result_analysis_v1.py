#!/usr/bin/env python3
"""Check deterministic result installation and saved-answer bank/topic grouping."""

from pathlib import Path
import subprocess

from apply_cbt_result_analysis_v1 import transform


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/cbt_result_analysis_core.js"


def main() -> None:
    fixture = ("<html><head></head><script>/* NK_BANK_AWARE_CBT_BUILDER_V1_START */"
               "function resultPage(t){return `      ${studyModule?nkModuleResultExtras(t,studyModule):''}`;}"
               "  window.QB={nav:()=>{}};</script></html>")
    generated = transform(fixture)
    assert transform(generated) == generated
    for marker in ("NK_CBT_RESULT_ANALYSIS_V1_START", "nkCbtResultSection(t)",
                   "nkCbtPracticeMisses", "nk-cbt-result-analysis-v1"):
        assert marker in generated, marker
    inline = generated.split("<script>", 1)[1].split("</script>", 1)[0]
    subprocess.run(["node", "--check"], input=inline, text=True, check=True)

    source = CORE.read_text(encoding="utf-8")
    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const prep={subject:'Anatomy',bank:'PrepLadder',topics:[{id:'1',title:'Prep topic'}]};
const marrow={subject:'Anatomy',bank:'Marrow',topics:[{id:'1',title:'Marrow topic'}]};
const physiology={subject:'Physiology',bank:'Marrow',topics:[{id:'1',title:'Physiology topic'}]};
const questions=[
 {id:'p1',subject:'Anatomy',bank:'PrepLadder',chapterId:'1',chapter:'Prep topic',correctOption:2},
 {id:'m1',subject:'Anatomy',bank:'Marrow',chapterId:'1',chapter:'Marrow topic',correctOption:3},
 {id:'ph1',subject:'Physiology',bank:'Marrow',chapterId:'1',chapter:'Physiology topic',correctOption:1}];
const test={id:'saved1',title:'Mixed CBT',questionIds:['p1','m1','ph1'],answers:{p1:1,m1:3},kind:'exam'};
let started=null;const context={nkAllStudyQuestions:()=>questions,nkModuleSubjectRecord:(s,b)=>
  [prep,marrow,physiology].find(r=>r.subject===s&&r.bank===b),nkModuleTopics:r=>r?.topics||[],
  state:{tests:[test],attempts:{p1:[{correct:true}]}},BY_ID:{},
  startSession:(ids,mode,title,kind)=>{started={ids:Array.from(ids),mode,title,kind};return true},
  showToast:()=>{},esc:String,navIcon:()=>'',JSON,Map,String,Math};
vm.createContext(context);vm.runInContext(SOURCE,context);
const analysis=vm.runInContext('nkCbtResultAnalysis(state.tests[0])',context);
assert.equal(analysis.rows.length,3,'matching chapter IDs must stay separate across banks');
assert.deepEqual(Array.from(analysis.missedIds),['p1','ph1'],'saved answers govern misses, not current attempts');
assert.equal(analysis.rows.find(r=>r.bank==='PrepLadder').incorrect,1);
assert.equal(analysis.rows.find(r=>r.title==='Marrow topic').correct,1);
assert.equal(analysis.rows.find(r=>r.subject==='Physiology').unattempted,1);
const markup=vm.runInContext('nkCbtResultSection(state.tests[0])',context);
assert(markup.includes('Prep topic')&&markup.includes('Marrow topic'));
assert(markup.includes('1 incorrect · 0 unattempted'));
assert(markup.includes('0 incorrect · 1 unattempted'));
assert.equal(vm.runInContext('nkCbtPracticeMisses("saved1")',context),true);
assert.deepEqual(started.ids,['p1','ph1']);assert.equal(started.mode,'practice');
assert.equal(started.kind,'cbt-followup');
assert.equal(context.state.attempts.p1[0].correct,true,'past attempt state stays untouched');
console.log('CBT_RESULT_ANALYSIS_BEHAVIOR_OK sourceExact=true snapshot=true followup=true');
'''.replace("SOURCE", repr(source), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("CBT_RESULT_ANALYSIS_INSTALL_OK")


if __name__ == "__main__":
    main()
