#!/usr/bin/env python3
"""Behavior, corpus, and transform contracts for question presentation."""

from pathlib import Path
import subprocess
import tempfile

from apply_question_presentation_v1 import transform

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/question_presentation_core.js"


def run_node_behavior() -> None:
    runtime = r'''
const assert=require('assert'),fs=require('fs'),vm=require('vm');
global.window=globalThis;const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
let SUBJECTS=[];
''' + CORE.read_text(encoding="utf-8") + r'''
const broken={id:'match',question:'Match the following neurotransmitters. A. Acetylcholine 1. Raphe nuclei B. Dopamine 2. Substantia nigra',correctOption:2,options:[
 {letter:'A',text:'Acetylcholine 1. Raphe nuclei'},{letter:'B',text:'Dopamine 2. Substantia nigra'},
 {letter:'A',text:'A-2, B-1'},{letter:'B',text:'A-1, B-2'},{letter:'C',text:'A-2, B-2'},{letter:'D',text:'A-1, B-1'}]};
const bp=nkQuestionPresentationFor(broken);assert.equal(bp.options.length,4);assert.deepEqual(bp.options.map(o=>o.letter),['A','B','C','D']);assert.equal(bp.supporting.length,2);assert(bp.repaired);
const table=nkQuestionStemMarkup(broken);assert(table.includes('nk-match-table'));assert(table.includes('Acetylcholine'));assert(table.includes('Raphe nuclei'));assert(!table.includes('A-2, B-1'));
const alternate={id:'alternate-match',question:'Match the ion with its equilibrium potential in a normal mammalian cell. Ion Equilibrium Potential (mV) 1. Sodium A. -70 2. Chloride B. +63 3. Potassium C. +132 4. Calcium D. -90 Ion Equilibrium Potential (mV) 1. Sodium A. -70 2. Chloride B. +63 3. Potassium C. +132 4. Calcium D. -90',correctOption:1,options:[
 {letter:'A',text:'1-B, 2-A, 3-D, 4-C'},{letter:'B',text:'1-D, 2-C, 3-B, 4-A'},{letter:'C',text:'1-C, 2-D, 3-A, 4-B'},{letter:'D',text:'1-A, 2-B, 3-C, 4-D'}]};
const alternateMarkup=nkQuestionStemMarkup(alternate);assert(alternateMarkup.includes('nk-match-table'));for(const expected of ['Sodium','Chloride','Potassium','Calcium','-70','+63','+132','-90'])assert(alternateMarkup.includes(expected));assert.equal((alternateMarkup.match(/Ion Equilibrium Potential \(mV\)/g)||[]).length,1);assert(!alternateMarkup.includes('-90 Ion Equilibrium'));
const five={question:'Assertion and reason',correctOption:5,options:'ABCDE'.split('').map(letter=>({letter,text:'Choice '+letter}))};assert.equal(nkQuestionPresentationFor(five).options.length,5);assert(nkQuestionPresentationFor(five).valid);
const leaked={question:'Which statements are correct?',correctOption:1,options:[...['A','B','C','D'].map(letter=>({letter,text:'Choice '+letter})),{letter:'E',text:'Fig: source. The other options B, C and D are incorrect.'}]};assert.equal(nkQuestionPresentationFor(leaked).options.length,4);
const incomplete={question:'Image-only source',correctOption:4,options:[{letter:'B',text:'caption'}]};assert(!nkQuestionPresentationFor(incomplete).valid);assert(nkQuestionStemMarkup(incomplete).includes('answering is disabled'));
const hostile={question:'Ordinary <script>alert(1)</script>',correctOption:1,options:[{letter:'A',text:'Yes'},{letter:'B',text:'No'}]};const safe=nkQuestionStemMarkup(hostile);assert(safe.includes('&lt;script&gt;'));assert(!safe.includes('<script>'));

const context={window:{}};vm.createContext(context);
for(const file of ['app/src/main/assets/qbank_data.js','app/src/main/assets/subjects_qbank_data.js'])vm.runInContext(fs.readFileSync(file,'utf8'),context);
SUBJECTS=[{subject:'Biochemistry',questions:context.window.QBANK_DATA.questions},...context.window.SUBJECT_QBANK_DATA.subjects];
let repaired=0,repairedIds=[],invalid=[];for(const q of SUBJECTS.flatMap(record=>record.questions||[])){delete q.__nkQuestionPresentation;const p=nkQuestionPresentationFor(q);if(p.repaired){repaired++;repairedIds.push(q.id);}if(!p.valid)invalid.push(q.id);}
assert.equal(repaired,8,'all extraction-shaped option arrays should normalize generically');
assert.deepEqual(repairedIds.sort(),['anatomy-10-1','anatomy-29-1','anatomy-46-12','physiology-1-13','physiology-19-12','physiology-24-10','physiology-4-8','physiology-6-2']);
assert.deepEqual(invalid.sort(),['anatomy-22-4','physiology-23-38','physiology-24-6','physiology-33-33']);
const byId=Object.fromEntries(SUBJECTS.flatMap(record=>record.questions||[]).map(q=>[q.id,q]));
assert.equal(byId['physiology-1-13'].options.length,4);
for(const id of ['physiology-1-13','physiology-4-8','physiology-6-2','physiology-24-10','physiology-6-6','physiology-9-17','anatomy-5-6','anatomy-7-9','5-8','10-10','22-18','anatomy-14-5','anatomy-40-10','anatomy-47-2','anatomy-49-9']){
  const markup=nkQuestionStemMarkup(byId[id]);assert(markup.includes('nk-match-table'),id+' should render structured matching data');assert(markup.includes('List I')&&markup.includes('List II'),id+' should retain both matching lists');
}
const ionMarkup=nkQuestionStemMarkup(byId['physiology-9-17']);
for(const expected of ['Sodium','Chloride','Potassium','Calcium','-70','+63','+132','-90'])assert(ionMarkup.includes(expected),'equilibrium-potential table lost '+expected);
assert.equal((ionMarkup.match(/Ion Equilibrium Potential \(mV\)/g)||[]).length,1,'duplicated equilibrium-potential source block leaked into learner markup');
const nerveMarkup=nkQuestionStemMarkup(byId['physiology-9-6']);
assert(nerveMarkup.includes('Proprioception</span>'));assert(!nerveMarkup.includes('Proprioception Fibre type Property'));
const enzymeMarkup=nkQuestionStemMarkup(byId['22-18']);
assert(enzymeMarkup.includes('<b>F</b><span>Ligases</span>'));assert(enzymeMarkup.includes('<b>6</b><span>Triosephosphate isomerase</span>'));assert(!enzymeMarkup.includes('Aldolase F'));
const bareMarkup=nkQuestionStemMarkup(byId['anatomy-49-9']);
for(const expected of ['Spine of scapula','Highest point of iliac crest','T2','T3','T7','L4'])assert(bareMarkup.includes(expected),'bare-label matching table lost '+expected);
const combination=nkQuestionStemMarkup(byId['physiology-19-12']);
for(const expected of ['Statements','Liver','Kidney','Muscle','Heart'])assert(combination.includes(expected),'combination question lost '+expected);
assert.equal(byId['physiology-19-12'].options.length,4);
let tableCount=0;
for(const q of SUBJECTS.flatMap(record=>record.questions||[])){
  const markup=nkQuestionStemMarkup(q);assert.equal(typeof markup,'string');assert(!markup.includes('[object Object]'),q.id+' rendered an object token');
  if(markup.includes('nk-match-table'))tableCount++;
}
assert(tableCount>=53,'expected corpus-wide matching/list questions to use semantic tables');
console.log('QUESTION_PRESENTATION_BEHAVIOR_OK repaired='+repaired+' invalid='+invalid.length+' semantic_tables='+tableCount);
'''
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(runtime)
        test_path = Path(handle.name)
    try:
        subprocess.run(["node", str(test_path)], cwd=ROOT, check=True)
    finally:
        test_path.unlink(missing_ok=True)


def test_transform() -> None:
    fixture = '''<html><head></head><body><script>
function nkSessionOptions(q,selected,mode,submitted) {
    const locked=true;return q.options;}
function practicePage(){return `<div class="question-text">${esc(q.question)}</div>`}
function examPage(){return `<div class="question-text" data-marrow-question="">${esc(q.question)}</div>`}
function reviewTestPage(){return `<div class="question-text">${esc(q.question)}</div>`}
  window.QB={};
</script></body></html>'''
    updated = transform(fixture)
    assert transform(updated) == updated
    assert updated.count("${nkQuestionStemMarkup(q)}") == 3
    assert "if(!presentation.valid)return '';" in updated
    for marker in ("NK_QUESTION_PRESENTATION_V1_START", "nk-question-presentation-v1", "nkQuestionPresentationFor", "nkQuestionMatchingTable"):
        assert marker in updated


if __name__ == "__main__":
    test_transform()
    run_node_behavior()
    print("QUESTION_PRESENTATION_V1_TEST_OK shared_renderer=practice,cbt,review source_data=unchanged")
