#!/usr/bin/env python3
"""Check timed CBT installation and exact bank/topic pool behavior."""

from pathlib import Path
import subprocess

from apply_bank_aware_cbt_builder_v1 import transform


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/bank_aware_cbt_builder_core.js"


def main() -> None:
    fixture = ("<html><head></head><script>/* NK_CUSTOM_STUDY_MODULES_V1_START */"
               "/* NK_INSIGHTS_FOCUS_V1_START */"
               "function render(){if(false){}\n    else if(route.page==='module-builder') out=studyModuleBuilderPage();}"
               "  window.QB={nav:()=>{}};</script></html>")
    generated = transform(fixture)
    assert transform(generated) == generated
    for marker in ("NK_BANK_AWARE_CBT_BUILDER_V1_START", "route.page==='test-builder'",
                   "nkCbtToggleTopic", "nkCbtSelectVerifiedPyqs", "nk-bank-aware-cbt-builder-v1"):
        assert marker in generated, marker
    inline = generated.split("<script>", 1)[1].split("</script>", 1)[0]
    subprocess.run(["node", "--check"], input=inline, text=True, check=True)

    source = CORE.read_text(encoding="utf-8")
    script = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const prep={subject:'Anatomy',bank:'PrepLadder',topics:[{id:'1',title:'Prep first'},{id:'2',title:'Prep second'}],
  questions:[{id:'prep1',chapterId:'1',studyCollections:['pyq']},{id:'prep2',chapterId:'2'}]};
const marrow={subject:'Anatomy',bank:'Marrow',topics:[{id:'1',title:'Marrow first'},{id:'2',title:'Marrow second'}],
  questions:[{id:'marrow1',chapterId:'1'},{id:'marrow2',chapterId:'2'}]};
const phys={subject:'Physiology',bank:'Marrow',topics:[{id:'1',title:'Phys first'}],
  questions:[{id:'phys1',chapterId:'1'}]};
let route='',started=null,saved=0;
const context={BANKS_BY_SUBJECT:{Anatomy:[prep,marrow],Physiology:[phys]},
  nkModuleScopeKey:(s,b)=>JSON.stringify([s,b]),nkModuleTopicKey:(s,t,b)=>JSON.stringify([s,b,String(t)]),
  nkModuleTopics:r=>r.topics,nkModuleTopicHasCollection:()=>false,
  document:{querySelectorAll:()=>[],getElementById:()=>null},
  navigate:p=>{route=p},render:()=>{},resetScrollPosition:()=>{},
  showToast:()=>{},fmtNum:String,esc:String,navIcon:()=>'',nkAppSubjectMeta:()=>({key:'anatomy'}),
  nkAppSubjectIcon:()=>'',nkAppPageHead:()=>'',shell:x=>x,
  BY_ID:{},state:{activeSession:null},saveState:()=>{saved++},
  startSession:(ids,mode,title)=>{started={ids,mode,title};context.state.activeSession={mode,questionIds:ids}},
  openTestBuilder:()=>{},openMultiSubjectTestBuilder:()=>{},Math,JSON,Set,Map,Object};
vm.createContext(context);vm.runInContext(SOURCE,context);
const call=code=>vm.runInContext(code,context),ids=()=>Array.from(call('nkCbtPool()'),q=>q.id);
call('openTestBuilder()');assert.equal(route,'test-builder');
assert.deepEqual(ids().sort(),['marrow1','marrow2','phys1','prep1','prep2']);
assert(call('nkCbtBuilderPage()').includes('Only verified PYQ topics')===false);
call('nkCbtSetStep(2)');
assert(call('nkCbtBuilderPage()').includes('1 eligible topics · 1 questions'));
call('nkCbtSelectVerifiedPyqs()');assert.deepEqual(ids(),['prep1']);
assert.equal(call('nkCbtTitle(nkCbtPool())'),'PYQ CBT');
call('nkCbtToggleTopic(0,1)');assert.deepEqual(ids().sort(),['prep1','prep2']);
assert.equal(call('nkCbtTitle(nkCbtPool())'),'Mixed Subjects CBT');
call('nkCbtSetBanks(false)');assert.deepEqual(ids(),[]);
call('nkCbtToggleBank(1)');assert.deepEqual(ids().sort(),['marrow1','marrow2']);
const beforeNoPyq=JSON.stringify(call('nkCbtDraft.topicKeys'));
call('nkCbtSelectVerifiedPyqs()');assert.equal(JSON.stringify(call('nkCbtDraft.topicKeys')),beforeNoPyq,'empty PYQ selection preserves draft');
call('nkCbtSetTopics(false)');assert.deepEqual(ids(),[]);
call('nkCbtToggleTopic(1,0)');assert.deepEqual(ids(),['marrow1'],'same chapter ID in another bank stays separate');
call('nkCbtSetStep(2)');
assert(call('nkCbtBuilderPage()').includes('Marrow first'));
call('nkCbtSetCount(10)');call('nkCbtStart()');
assert.deepEqual(Array.from(started.ids),['marrow1']);assert.equal(started.mode,'exam');
assert.equal(started.title,'Anatomy · Marrow CBT');assert.equal(context.state.activeSession.originRoute,'tests');
assert(context.BY_ID.marrow1);assert(saved>0);
call('openTestBuilder()');context.startSession=()=>false;
call('nkCbtStart()');assert.notEqual(call('nkCbtDraft'),null,'blocked start keeps the builder draft');
console.log('BANK_AWARE_CBT_BEHAVIOR_OK exactBank=true exactTopic=true session=true');
'''.replace("SOURCE", repr(source), 1)
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
    print("BANK_AWARE_CBT_INSTALL_OK")


if __name__ == "__main__":
    main()
