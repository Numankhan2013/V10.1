#!/usr/bin/env python3
"""Check source-exact coverage, latest-answer evidence, and tracker installation."""

from pathlib import Path
import subprocess

from apply_qbank_coverage_v1 import transform


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/qbank_coverage_core.js"


def main() -> None:
    fixture = (
        '<html><head></head><script>/* NK_CBT_RESULT_ANALYSIS_V1_START */'
        'function analytics(){return `<main>      ${nkInsightsFocusSection()}\n'
        '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">CHAPTER PERFORMANCE</div></div></section>'
        '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">RECENT</div></div></section>'
        '</main>`;}  window.QB={nav:()=>{}};</script></html>'
    )
    generated = transform(fixture)
    assert transform(generated) == generated
    assert "${nkCoverageSection()}" in generated
    assert "CHAPTER PERFORMANCE" not in generated
    for marker in ("NK_QBANK_COVERAGE_V1_START", "nk-coverage-v1",
                   "nkCoverageSelectBank", "nkCoverageOpen"):
        assert marker in generated, marker
    inline = generated.split("<script>", 1)[1].split("</script>", 1)[0]
    subprocess.run(["node", "--check"], input=inline, text=True, check=True)

    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const records=[
 {subject:'Anatomy',bank:'PrepLadder',topics:[{id:'1',title:'Prep Topic'}],questions:[
  {id:'p1',chapterId:'1'},{id:'p2',chapterId:'1'}]},
 {subject:'Anatomy',bank:'Marrow',topics:[{id:'1',title:'Marrow Topic'},{id:'2',title:'Next Topic'}],questions:[
  {id:'m1',chapterId:'1'},{id:'m2',chapterId:'1'},{id:'m4',chapterId:'1'},{id:'m3',chapterId:'2'}]},
 {subject:'Physiology',bank:'Marrow',topics:[{id:'1',title:'Another Topic'}],questions:[{id:'v1',chapterId:'1'}]}
];
const history={p1:[{id:'p1a',correct:true}],m1:[{id:'m1a',correct:false}],
 m2:[{id:'m2a',correct:false},{id:'m2b',correct:true}],v1:[{id:'v1a',correct:false,isUndo:true}]};
let opened=null;
const ctx={activeSubject:'Anatomy',nkModuleBankRecords:()=>records,nkModuleBankName:r=>r.bank,
 nkModuleTopics:r=>r.topics,nkFsrsActiveAttempts:id=>(history[id]||[]).filter(a=>!a.isUndo),
 nkOpenSubjectChapter:(s,b,t)=>{opened=[s,b,t]},esc:String,navIcon:()=>'',
 document:{querySelector:()=>null},JSON,Map,String,Math,encodeURIComponent,decodeURIComponent};
vm.createContext(ctx);vm.runInContext(SOURCE,ctx);
const call=code=>vm.runInContext(code,ctx);
let data=call('nkCoverageData()');
assert.equal(data.total,7);assert.equal(data.attempted,3);
assert.equal(data.complete,0);
assert.equal(data.banks[0].attempted,1);
assert.equal(data.banks[1].attempted,2);
assert.equal(data.banks[2].attempted,0,'undone answer is not counted');
assert.equal(data.banks[1].topics[0].latestMisses,1,'latest answer replaces old incorrect');
assert.equal(call('nkCoverageSelected(nkCoverageData()).bank'),'Marrow');
assert(call('nkCoverageSection()').includes('3/7 attempted'));
call("nkCoverageSetStatus('progress')");
assert(call('nkCoverageListMarkup(nkCoverageData())').includes('Marrow Topic'));
assert(!call('nkCoverageListMarkup(nkCoverageData())').includes('Next Topic'));
call("nkCoverageSetSearch('not here')");
assert(call('nkCoverageListMarkup(nkCoverageData())').includes('No topics match'));
call("nkCoverageSetSearch('')");
const key=encodeURIComponent(JSON.stringify(['Anatomy','Marrow','1']));
call('nkCoverageOpen('+JSON.stringify(key)+')');
assert.deepEqual(opened,['Anatomy','Marrow','1']);
opened=null;call('nkCoverageOpen('+JSON.stringify(encodeURIComponent(JSON.stringify(['Anatomy','Marrow','not real'])))+')');
assert.equal(opened,null,'unavailable topic must not open');
history.m1.push({id:'m1b',correct:true});
data=call('nkCoverageData()');
assert.equal(data.banks[1].topics[0].latestMisses,0);
console.log('QBANK_COVERAGE_BEHAVIOR_OK exactBanks=true activeAttempts=true latest=true navigation=true');
'''.replace("SOURCE", repr(CORE.read_text(encoding="utf-8")), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("QBANK_COVERAGE_INSTALL_OK")


if __name__ == "__main__":
    main()
