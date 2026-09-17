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
const nerveRows=[['1','Aα','a','Preganglionic autonomic'],['2','Aβ','b','Touch'],['3','Aδ','c','Temperature'],['4','B','d','Proprioception']];
const nerveOptions=[{letter:'A',text:'1-d, 2-b, 3-c, 4-a'},{letter:'B',text:'1-a, 2-b, 3-d, 4-c'},{letter:'C',text:'1-b, 2-a, 3-c, 4-d'},{letter:'D',text:'1-c, 2-d, 3-b, 4-a'}];
const nerveBlock='Fibre type Property 1. Aα a. Preganglionic autonomic 2. Aβ b. Touch 3. Aδ c. Temperature 4. B d. Proprioception';
const nerve={id:'physiology-9-6',sourcePage:253,question:'Match the following nerve fibre type with its respective property. '+nerveBlock+' '+nerveBlock,correctOption:1,options:nerveOptions.map(option=>({...option}))};
const assertNerve=q=>{
  const before=JSON.stringify(q),p=nkQuestionPresentationFor(q),markup=nkQuestionStemMarkup(q);
  assert.equal(q.id,'physiology-9-6');assert.equal(q.sourcePage,253);assert(p.valid);
  assert.deepEqual(p.table.rows.map(row=>row.flatMap(cell=>[cell.label,cell.value])),nerveRows);
  assert(markup.includes('<table class="nk-match-table">'));assert.equal((markup.match(/<tr>/g)||[]).length,5);
  for(const row of nerveRows)assert(markup.includes('<tr>'+[row.slice(0,2),row.slice(2)].map(([label,value])=>'<td><b>'+label+'</b><span>'+value+'</span></td>').join('')+'</tr>'));
  assert(!markup.includes('—'));assert.equal((markup.match(/Proprioception/g)||[]).length,1);
  assert.deepEqual(p.options,nerveOptions);assert.equal(p.options.length,4);assert.equal(q.correctOption,1);assert.equal(p.options[q.correctOption-1].text,nerveOptions[0].text);
  assert.strictEqual(nkQuestionPresentationFor(q),p);assert.equal(JSON.stringify(q),before);
};
assertNerve(nerve);
const malformed=[
  'List I List II 1. Alpha 2. Beta',
  'Column A Column B 1. Alpha 2. Beta',
  'a Alpha i One b Beta ii',
  '1. Alpha a. One 2. Beta b. Two 1. CHANGED a. WRONG',
  'a Alpha i One b Beta ii Two a Gamma iii Three c Delta iv Four',
  '1. Alpha a. One 2. Beta b. Two 1. Alpha a. WRONG',
  'a Alpha i One b Beta ii Two a Alpha i WRONG',
  '1. Alpha a. One 2. Beta b. Two 3. Gamma c. Three 4. Delta',
  '1. Alpha a. One 2. Beta b. Two 3. Gamma c. Three d. Four',
  '1. Alpha a. One 2. Beta b. Two 3. Gamma c.',
  '1. Alpha a. One 2. Beta b. — 3. Gamma c. Three',
  '1. Alpha a. One 2. b. Two 3. Gamma c. Three',
  '1. Alpha a. One 3. Gamma b. Two 4. Delta c. Three',
  '1. Alpha b. One 2. Beta c. Two 3. Gamma d. Three',
  '1. Alpha a. One 2. Beta b. Two 3. Gamma d. Three',
  '1. Alpha a. One 2. Beta b. Two 3. Gamma b. Three',
  '1. Alpha a. One 2. Beta b. Two 1. Gamma c. Three',
  'a Alpha i One b Beta ii Two c Gamma iv Three',
  'a Alpha i One b Beta ii Two c Gamma iii Three d Delta',
  'a Alpha i One b Beta ii Two c Gamma iii —'
];
for(const source of malformed){
  const q={question:'Match the following: '+source,correctOption:1,options:nerveOptions.map(option=>({...option}))},before=JSON.stringify(q);
  const p=nkQuestionPresentationFor(q);assert.equal(p.valid,false,source);assert.equal(p.table,null,source);
  const markup=nkQuestionStemMarkup(q);assert(markup.includes('answering is disabled'),source);assert(!markup.includes('<table'),source);
  assert.strictEqual(nkQuestionPresentationFor(q),p);assert.equal(JSON.stringify(q),before);
}
for(const source of [nerveBlock,nerveBlock+' '+nerveBlock,nerveBlock+' '+nerveBlock+' '+nerveBlock,nerveBlock+' Fibre type Property 1. Aα a. Preganglionic autonomic']){
  const parsed=nkQuestionMatchingTable('Match the following: '+source);assert.deepEqual(parsed.rows.map(row=>row.flatMap(cell=>[cell.label,cell.value])),nerveRows);
}
const bare=nkQuestionMatchingTable('Match each: a Alpha i One b Beta ii Two c Gamma iii Three a Alpha i One b Beta ii Two c Gamma iii Three');
assert.deepEqual(bare.rows.map(row=>row.map(cell=>cell.value)),[['Alpha','One'],['Beta','Two'],['Gamma','Three']]);
const ordinary={question:'He was injured during a soccer match. Which muscle is affected?',correctOption:1,options:nerveOptions};
assert(nkQuestionPresentationFor(ordinary).valid);assert.equal(nkQuestionPresentationFor(ordinary).table,null);
for(const question of ['During a match he sustained an injury. 1. Pain 2. Swelling','Match the clinical description to the diagnosis.']){
  const q={...ordinary,question};assert(nkQuestionPresentationFor(q).valid);assert.equal(nkQuestionPresentationFor(q).table,null);
}
const barePrefix=nkQuestionMatchingTable('Match each: a Alpha i One b Beta ii Two a Alpha i On');
assert.deepEqual(barePrefix.rows.map(row=>row.map(cell=>cell.value)),[['Alpha','One'],['Beta','Two']]);
const startupContext={SUBJECTS:[{questions:malformed.map(source=>({question:'Match the following: '+source,correctOption:1,options:nerveOptions}))}]};
vm.createContext(startupContext);vm.runInContext(fs.readFileSync('tools/question_presentation_core.js','utf8'),startupContext);
for(const q of startupContext.SUBJECTS[0].questions){assert.equal(q.__nkQuestionPresentation.valid,false);assert.equal(q.__nkQuestionPresentation.table,null);}
const single=nkQuestionMatchingTable('Choose statements: A. Liver B. Kidney C. Muscle D. Heart',true);assert.equal(single.groups.length,1);assert.equal(single.rows.length,4);
const five={question:'Assertion and reason',correctOption:5,options:'ABCDE'.split('').map(letter=>({letter,text:'Choice '+letter}))};assert.equal(nkQuestionPresentationFor(five).options.length,5);assert(nkQuestionPresentationFor(five).valid);
const leaked={question:'Which statements are correct?',correctOption:1,options:[...['A','B','C','D'].map(letter=>({letter,text:'Choice '+letter})),{letter:'E',text:'Fig: source. The other options B, C and D are incorrect.'}]};assert.equal(nkQuestionPresentationFor(leaked).options.length,4);
const incomplete={question:'Image-only source',correctOption:4,options:[{letter:'B',text:'caption'}]};assert(!nkQuestionPresentationFor(incomplete).valid);assert(nkQuestionStemMarkup(incomplete).includes('answering is disabled'));
const hostile={question:'Ordinary <script>alert(1)</script>',correctOption:1,options:[{letter:'A',text:'Yes'},{letter:'B',text:'No'}]};const safe=nkQuestionStemMarkup(hostile);assert(safe.includes('&lt;script&gt;'));assert(!safe.includes('<script>'));
const scientific=nkScientificMarkup('10^6; H2O + CO2 → HCO3^- + H+; Ca2+; α2; HbA1c');
for(const expected of [
  '10<sup class="nk-sci-sup">6</sup>',
  'H<sub class="nk-sci-sub">2</sub>O',
  'CO<sub class="nk-sci-sub">2</sub>',
  'HCO<sub class="nk-sci-sub">3</sub><sup class="nk-sci-sup">−</sup>',
  'H<sup class="nk-sci-sup">+</sup>',
  'Ca<sup class="nk-sci-sup">2+</sup>',
  'α<sub class="nk-sci-sub">2</sub>',
  'HbA<sub class="nk-sci-sub">1c</sub>'
])assert(scientific.includes(expected),'scientific renderer lost '+expected);
const repairedScience=nkScientificMarkup('Mg²■; Na■; Cl■; pCO■; HCO■■; PO2■■');
for(const expected of ['Mg<sup class="nk-sci-sup">2+</sup>','Na<sup class="nk-sci-sup">+</sup>','Cl<sup class="nk-sci-sup">−</sup>','pCO<sub class="nk-sci-sub">2</sub>','HCO<sub class="nk-sci-sub">3</sub><sup class="nk-sci-sup">−</sup>','PO<sub class="nk-sci-sub">2</sub>'])assert(repairedScience.includes(expected),'safe OCR notation repair lost '+expected);
assert(!nkScientificMarkup('A<B<C').includes('<B>'),'scientific formatting bypassed HTML escaping');

const context={window:{}};vm.createContext(context);
for(const file of ['app/src/main/assets/qbank_data.js','app/src/main/assets/subjects_qbank_data.js'])vm.runInContext(fs.readFileSync(file,'utf8'),context);
SUBJECTS=[{subject:'Biochemistry',questions:context.window.QBANK_DATA.questions},...context.window.SUBJECT_QBANK_DATA.subjects];
const porphyria=SUBJECTS.flatMap(record=>record.questions||[]).find(q=>q.id==='24-9');
const porphyriaGroups=[
  ['Acute intermittent porphyria','Porphyria Cutanea Tarda','Hereditary coproporphyria','Congenital erythropoietic porphyria'].map((value,index)=>({label:'ABCD'[index],value})),
  ['Neuropsychiatric manifestations','Photosensitivity','Both Neuropsychiatric manifestation and photosensitivity'].map((value,index)=>({label:['i','ii','iii'][index],value}))
];
assert.deepEqual(porphyria.options.map(option=>option.text),['A-i, B-ii, C-iii, D-ii','A-i, B-ii, C-ii, D-iii','A-ii, B-i, C-iii, D-iii','A-ii, B-i, C-ii, D-iii']);
assert.equal(porphyria.correctOption,1);assert.equal(nkQuestionPairedTableValid(porphyriaGroups,true),true);assert.equal(nkQuestionPairedTableValid(porphyriaGroups),false);
console.log('PORPHYRIA_MANY_TO_ONE_OK lengths='+porphyriaGroups.map(group=>group.length).join(',')+' canonical='+porphyria.options[porphyria.correctOption-1].text);
const rawById=Object.fromEntries(SUBJECTS.flatMap(record=>record.questions||[]).map(q=>[q.id,JSON.stringify(q)]));
let repaired=0,repairedIds=[],invalid=[];for(const q of SUBJECTS.flatMap(record=>record.questions||[])){delete q.__nkQuestionPresentation;const p=nkQuestionPresentationFor(q);if(p.repaired){repaired++;repairedIds.push(q.id);}if(!p.valid)invalid.push(q.id);}
assert.equal(repaired,8,'all extraction-shaped option arrays should normalize generically');
assert.deepEqual(repairedIds.sort(),['anatomy-10-1','anatomy-29-1','anatomy-46-12','physiology-1-13','physiology-19-12','physiology-24-10','physiology-4-8','physiology-6-2']);
assert.deepEqual(invalid.sort(),['anatomy-14-5','anatomy-22-4','anatomy-40-10','anatomy-47-2','anatomy-9-1','physiology-23-38','physiology-24-6','physiology-33-33']);
const byId=Object.fromEntries(SUBJECTS.flatMap(record=>record.questions||[]).map(q=>[q.id,q]));
const completeSources={
  '10-10':{correct:1,rows:[
    ['1','Apolipoprotein A-I','a','Enhances lipoprotein lipase activity, facilitating triglyceride hydrolysis.'],
    ['2','Apolipoprotein B-100','b','Involved in the transport of dietary lipids from the intestine to other tissues.'],
    ['3','Apolipoprotein C-II','c','Helps in reverse cholesterol transport, removing excess cholesterol from tissue back to liver.'],
    ['4','Apolipoprotein E','d','Essential for binding to LDL receptors on various tissues.']
  ]},
  '10-4':{correct:1,rows:[
    ['A','Choline Deficiency','1','Increases NADH, hindering fatty acid oxidation and promoting triacylglycerol accumulation.'],
    ['B','Orotic Acid Interference','2','Impairs VLDL secretion, resulting in triacylglycerol accumulation and a fatty liver.'],
    ['C','Vitamin E and Selenium','3','Involved in pyrimidine synthesis. Disrupts VLDL glycosylation, hindering release.'],
    ['D','Ethanol Consumption','4','Protect against liver damage from lipid peroxidation']
  ]},
  '13-21':{correct:2,rows:[
    ['1','Ninhydrin test','a','Detects compouds containing 2 or more peptide bonds'],
    ['2','Xanthoproteic test','b','Detects aromatic amino acids'],
    ['3','Sakaguchi test','c','Detects arginine'],
    ['4','Biuret test','d','Detects alpha-amino acids']
  ]},
  'anatomy-46-8':{correct:3,rows:[
    ['1','Found in cartilage (Hyaline and Elastic Cartilage)','a','Type I collagen'],
    ['2','Major component of basement membranes','b','Type II collagen'],
    ['3','Predominant in bowel and blood vessels','c','Type III collagen'],
    ['4','Primary collagen in bones, tendons, and dermis','d','Type IV collagen']
  ]},
  'anatomy-49-9':{correct:4,rows:[
    ['a','Spine of scapula','i','T2'],
    ['b','Highest point of iliac crest','ii','T3'],
    ['c','Superior angle of scapula','iii','T7'],
    ['d','Inferior angle of scapula','iv','L4']
  ]},
  'anatomy-50-8':{correct:4,rows:[
    ['a','Pectoralis major','1','Extension at shoulder'],
    ['b','Supraspinatus','2','Flexion at shoulder'],
    ['c','Infraspinatus','3','Lateral rotation of the shoulder'],
    ['d','Latissimus dorsi','4','Abduction at shoulder']
  ]},
  'physiology-20-25':{correct:2,rows:[
    ['1','Ascending Limb of Loop of Henle','a','Blood loses water and gains solutes as it passes through the hyperosmotic medullary interstitium.'],
    ['2','Descending Limb of Loop of Henle','b','Blood gains water and loses solutes as it passes through the less concentrated interstitium.'],
    ['3','Ascending Vasa Recta','c','Actively transports sodium and chloride into the interstitium, diluting the filtrate.'],
    ['4','Descending Vasa Recta','d','Permeable to water; water is reabsorbed into the interstitium, concentrating the filtrate.']
  ]},
  'physiology-24-10':{correct:2,rows:[
    ['','1','A','Pulmonary artery pressure > Pulmonary venous pressure > Alveolar pressure','i','Continuous blood flow'],
    ['','2','B','Alveolar pressure > Pulmonary artery pressure > Pulmonary venous pressure','ii','No blood flow'],
    ['','3','C','Pulmonary artery pressure > Alveolar pressure > Pulmonary venous pressure','iii','Intermittent blood flow (only during systole)']
  ]},
  'physiology-4-8':{correct:2,rows:[
    ['1','Cingulate Gyrus','A','Conversion of short-term memory to long-term memory'],
    ['2','Parahippocampal Gyrus','B','Controls heart rate, blood pressure, cognitive and emotional processing'],
    ['3','Hippocampus','C','Responsible for controlling recent memories of the brain'],
    ['4','Mammillary Body and Anterior Nucleus of Thalamus','D','Spatial memory, the memory of three-dimensional space']
  ]},
  'physiology-6-2':{correct:1,rows:[
    ['1','Beta','A','8-13','i','Deep sleep'],
    ['2','Alpha','B','14-30','ii','Relaxation, eyes closed'],
    ['3','Theta','C','2-4','iii','Alert and active thinking'],
    ['4','Delta','D','5-7','iv','Light sleep, emotional stress in adults']
  ]}
};
for(const [id,expected] of Object.entries(completeSources)){
  const q=byId[id],raw=JSON.parse(rawById[id]),p=nkQuestionPresentationFor(q),markup=nkQuestionStemMarkup(q);
  assert(p.valid,id);assert.equal(q.id,id);assert.equal(q.question,raw.question,id);
  assert.equal(q.sourcePage,raw.sourcePage,id);assert.equal(q.sourcePageEnd,raw.sourcePageEnd,id);
  assert.equal(q.correctOption,expected.correct,id);assert.equal(q.correctOption,raw.correctOption,id);
  assert.equal(p.options.length,4,id);assert.deepEqual(p.options,raw.options.slice(-4),id);assert.deepEqual(q.options,p.options,id);
  assert.deepEqual(p.options.map(option=>option.letter),['A','B','C','D'],id);
  assert.equal(p.options[q.correctOption-1].text,raw.options.slice(-4)[expected.correct-1].text,id);
  assert.deepEqual(p.supporting,raw.options.slice(0,-4),id);
  assert.deepEqual(p.table.rows.map(row=>row.flatMap(cell=>[cell.label,cell.value])),expected.rows,id);
  assert.equal((markup.match(/<tr>/g)||[]).length,expected.rows.length+1,id);
  assert(!markup.includes('—'),id);assert(!markup.includes('<span></span>'),id);assert(!markup.includes('answering is disabled'),id);
  for(const row of expected.rows){
    let html='<tr>';
    for(let index=0;index<row.length;index+=2)html+='<td>'+(row[index]?'<b>'+nkScientificMarkup(row[index])+'</b>':'')+'<span>'+nkScientificMarkup(row[index+1])+'</span></td>';
    assert(markup.includes(html+'</tr>'),id);
  }
  assert(!markup.includes('Prepladder X Qbank'),id);
  const selected=nkQuestionCompleteSourceOverride(raw,{supporting:raw.options.slice(0,-4)});
  assert.deepEqual(selected.rows,p.table.rows,id);assert.equal(JSON.stringify(raw),rawById[id],id+' selection must not mutate source');
  const before=JSON.stringify(q);assert.strictEqual(nkQuestionPresentationFor(q),p);assert.equal(JSON.stringify(q),before,id);
  const mutations=[
    q=>{q.id+='-changed';},
    q=>{q.question=' '+q.question;},
    q=>{q.question+=' changed';},
    q=>{q.question=q.question.replace('Match','Changed');},
    q=>{q.correctOption=q.correctOption===1?2:1;},
    q=>{q.sourcePage++;},
    q=>{q.sourcePageEnd++;},
    q=>{delete q.sourcePageEnd;},
    q=>{q.options.reverse();},
    q=>{q.options.pop();},
    q=>{q.options.push({letter:'E',text:'changed'});},
    ...raw.options.flatMap((_,index)=>[
      q=>{q.options[index].text+=' changed';},
      q=>{q.options[index].letter='Z';}
    ])
  ];
  if(raw.options.length>4)mutations.push(q=>{q.options=q.options.slice(-4);});
  for(const mutate of mutations){
    const changed=JSON.parse(rawById[id]);mutate(changed);
    const rejected=nkQuestionCompleteSourceOverride(changed,{supporting:changed.options.slice(0,-4)});
    assert(rejected===null||rejected.valid===false,id+' stale override');
    const changedPresentation=nkQuestionPresentationFor(changed);
    assert(!changedPresentation.valid,id+' stale source must fail closed');assert.equal(changedPresentation.table,null,id);
  }
}
const zones=byId['physiology-24-10'].__nkQuestionPresentation.table;
assert.deepEqual(zones.headers,['Zone','Pressure Relationship','Blood Flow Characteristic']);
assert.deepEqual(zones.groups[0],[{label:'',value:'1'},{label:'',value:'2'},{label:'',value:'3'}]);
const completeStartup={SUBJECTS:[{questions:Object.keys(completeSources).map(id=>JSON.parse(rawById[id]))}]};
vm.createContext(completeStartup);vm.runInContext(fs.readFileSync('tools/question_presentation_core.js','utf8'),completeStartup);
for(const q of completeStartup.SUBJECTS[0].questions){
  assert(q.__nkQuestionPresentation.valid,q.id+' startup');
  assert.deepEqual(q.__nkQuestionPresentation.table.rows.map(row=>row.flatMap(cell=>[cell.label,cell.value])),completeSources[q.id].rows,q.id);
  assert.deepEqual(q.options,JSON.parse(rawById[q.id]).options.slice(-4),q.id);
}
const hygieneStartup={SUBJECTS:[{questions:Object.keys(completeSources).map(id=>JSON.parse(rawById[id]))}]};
vm.createContext(hygieneStartup);
vm.runInContext(fs.readFileSync('tools/question_content_hygiene_core.js','utf8'),hygieneStartup);
const sourceHash=q=>{
  const source=JSON.stringify([q.id,q.question,q.options,q.correctOption,q.sourcePage,q.sourcePageEnd]);
  let hash=2166136261;
  for(let index=0;index<source.length;index++)hash=Math.imul(hash^source.charCodeAt(index),16777619);
  return hash>>>0;
};
for(const q of hygieneStartup.SUBJECTS[0].questions){
  const before=sourceHash(q);
  hygieneStartup.nkSanitizeMarrowQuestion(q);
  const cleaned=JSON.stringify(q);
  hygieneStartup.nkSanitizeMarrowQuestion(q);
  assert.equal(JSON.stringify(q),cleaned,q.id+' hygiene idempotence');
  console.log('OVERRIDE_HYGIENE_HASH id='+q.id+' raw='+before+' cleaned='+sourceHash(q));
}
vm.runInContext(fs.readFileSync('tools/question_presentation_core.js','utf8'),hygieneStartup);
for(const q of hygieneStartup.SUBJECTS[0].questions){
  const raw=JSON.parse(rawById[q.id]);
  assert(q.__nkQuestionPresentation.valid,q.id+' hygiene-before-presentation startup');
  assert.deepEqual(q.__nkQuestionPresentation.table.rows.map(row=>row.flatMap(cell=>[cell.label,cell.value])),completeSources[q.id].rows,q.id);
  assert.deepEqual(q.options,raw.options.slice(-4),q.id);
  assert.equal(q.correctOption,raw.correctOption,q.id);
  assert.equal(q.sourcePage,raw.sourcePage,q.id);
  assert.equal(q.sourcePageEnd,raw.sourcePageEnd,q.id);
  const clean=JSON.parse(rawById[q.id]);hygieneStartup.nkSanitizeMarrowQuestion(clean);
  for(const mutate of [
    value=>{value.question+=' changed';},
    value=>{value.question=' '+value.question;},
    value=>{value.question=value.question.replace('Match','Changed');},
    value=>{value.sourcePage++;},
    value=>{value.sourcePageEnd++;},
    value=>{value.correctOption=value.correctOption===1?2:1;},
    value=>{value.options.reverse();},
    value=>{value.options.pop();},
    ...clean.options.flatMap((_,index)=>[
      value=>{value.options[index].text+=' changed';},
      value=>{value.options[index].letter='Z';}
    ])
  ]){
    const changed=JSON.parse(JSON.stringify(clean));mutate(changed);
    const rejected=hygieneStartup.nkQuestionPresentationFor(changed);
    assert(!rejected.valid,q.id+' changed hygienic source must fail closed');
    assert.equal(rejected.table,null,q.id);
  }
}
console.log('COMPLETE_SOURCE_OVERRIDES_OK records='+Object.keys(completeSources).length+' exact_rows=true mutation_rejection=true startup=true hygiene_startup=true');
assertNerve(byId['physiology-9-6']);
for(const [id,labels] of Object.entries({'24-9':'A,B,C,D|i,ii,iii','anatomy-27-23':'1,2,3,4|a,b,c,d,e','anatomy-7-8':'1,2|a,b|i,ii,iii,iv'})){
  const q=byId[id],p=nkQuestionPresentationFor(q),before=JSON.stringify(q);
  assert(p.valid,id);assert.equal(p.table.groups.map(group=>group.map(cell=>cell.label).join(',')).join('|'),labels);
  assert.strictEqual(nkQuestionPresentationFor(q),p);assert.equal(JSON.stringify(q),before);
  for(const mutate of [q=>{q.question=q.question.replace(/3\)|4\)/g,'');},q=>{q.options[0].text+=' changed';},q=>{q.sourcePage++;},q=>{q.correctOption=q.correctOption===1?2:1;},q=>{q.question=q.question.replace(/porphyria|artery|Fourth/g,'CHANGED');}]){
    const changed=JSON.parse(before);mutate(changed);if(JSON.stringify(changed)===before)continue;assert.equal(nkQuestionMatchingOverride(changed),null,id+' stale override');
    if(changed.question!==q.question||changed.options[0].text!==q.options[0].text||changed.sourcePage!==q.sourcePage||changed.correctOption!==q.correctOption)assert(!nkQuestionPresentationFor(changed).valid,id+' stale unequal question');
  }
}
const missingCoronary=JSON.parse(JSON.stringify(byId['anatomy-27-23']));missingCoronary.question=missingCoronary.question.replace(/3\)|4\)/g,'');
assert(!nkQuestionPresentationFor(missingCoronary).valid);assert(nkQuestionStemMarkup(missingCoronary).includes('answering is disabled'));
for(const id of ['physiology-36-7','anatomy-29-16'])assert(nkQuestionPresentationFor(byId[id]).valid,id+' established unequal override');
assert.equal(byId['physiology-1-13'].options.length,4);
for(const id of ['anatomy-14-5','anatomy-40-10','anatomy-47-2','anatomy-9-1']){
  const p=nkQuestionPresentationFor(byId[id]);
  assert(!p.valid,id+' with incomplete or conflicting source structure must fail closed');assert.equal(p.table,null,id+' with incomplete or conflicting source structure must not render a fabricated table');
  const markup=nkQuestionStemMarkup(byId[id]);assert(markup.includes('answering is disabled'),id+' must hide choices when source structure is incomplete');assert(!markup.includes('<table'),id+' must not render a table when source structure is incomplete');
}
for(const id of ['physiology-1-13','physiology-6-6','physiology-9-17','anatomy-5-6','anatomy-7-9','5-8','22-18']){
  const markup=nkQuestionStemMarkup(byId[id]);assert(markup.includes('nk-match-table'),id+' should render structured matching data');assert(markup.includes('List I')&&markup.includes('List II'),id+' should retain both matching lists');
}
const ionMarkup=nkQuestionStemMarkup(byId['physiology-9-17']);
for(const expected of ['Sodium','Chloride','Potassium','Calcium','-70','+63','+132','-90'])assert(ionMarkup.includes(expected),'equilibrium-potential table lost '+expected);
assert.equal((ionMarkup.match(/Ion Equilibrium Potential \(mV\)/g)||[]).length,1,'duplicated equilibrium-potential source block leaked into learner markup');
const transportMarkup=nkQuestionStemMarkup(byId['physiology-9-22']);
for(const expected of ['Statement','Type','Direction','Mediator','Anterograde','Retrograde','Cell body to axon terminal','Axon terminal to cell body','Dynein','Kinesin'])assert(transportMarkup.includes(expected),'axonal-transport table lost '+expected);
assert.equal((transportMarkup.match(/Anterograde/g)||[]).length,2,'duplicated anterograde source rows leaked into learner markup');
assert.equal((transportMarkup.match(/Retrograde/g)||[]).length,2,'duplicated retrograde source rows leaked into learner markup');
assert.deepEqual(byId['physiology-9-22'].options.map(option=>option.text),['1','2','3','4']);
assert.equal(byId['physiology-9-22'].correctOption,3,'axonal-transport canonical answer changed');
const combination=nkQuestionStemMarkup(byId['physiology-19-12']);
for(const expected of ['Statements','Liver','Kidney','Muscle','Heart'])assert(combination.includes(expected),'combination question lost '+expected);
assert.equal(byId['physiology-19-12'].options.length,4);
let tableCount=0;
for(const q of SUBJECTS.flatMap(record=>record.questions||[])){
  const markup=nkQuestionStemMarkup(q);assert.equal(typeof markup,'string');assert(!markup.includes('[object Object]'),q.id+' rendered an object token');
  if(markup.includes('nk-match-table'))tableCount++;
}
assert(tableCount>=46,'expected corpus-wide matching/list/row-table questions to use semantic tables');
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
    fixture = r'''<html><head></head><body><script>
  function richText(text) {
    return esc(String(text||'')).replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>');
  }
function nkSessionOptions(q,selected,mode,submitted) {
    const locked=true;return `<span class="option-text">${esc(o.text)}</span>`;}
function nkGoldText(text){let html=esc(String(text||''));return html;}
function nkGoldWrong(o,reason){return '<strong>'+esc(o.text||'')+'</strong><p>'+esc(reason)+'</p>';}
function nkTakeaway(takeaway){return `<p>${esc(takeaway)}</p>`;}
function practicePage(){return `<div class="question-text">${esc(q.question)}</div>`}
function examPage(){return `<div class="question-text" data-marrow-question="">${esc(q.question)}</div>`}
function reviewTestPage(){return `<div class="question-text">${esc(q.question)}</div>`}
  window.QB={};
</script></body></html>'''
    updated = transform(fixture)
    assert transform(updated) == updated
    assert updated.count("${nkQuestionStemMarkup(q)}") == 3
    assert "if(!presentation.valid)return '';" in updated
    assert "return nkScientificMarkup(text)" in updated
    assert "${nkScientificMarkup(o.text)}" in updated
    assert "${nkScientificMarkup(takeaway)}" in updated
    assert "let html=nkScientificMarkup(text);" in updated
    assert "'<strong>'+nkScientificMarkup(o.text||'')+'</strong>" in updated
    assert "nkScientificMarkup(reason)" in updated
    assert ".nk-sci-sub,.nk-sci-sup" in updated
    for marker in ("NK_QUESTION_PRESENTATION_V1_START", "nk-question-presentation-v1", "nkQuestionPresentationFor", "nkQuestionMatchingTable"):
        assert marker in updated


if __name__ == "__main__":
    test_transform()
    run_node_behavior()
    print("QUESTION_PRESENTATION_V1_TEST_OK shared_renderer=practice,cbt,review source_data=unchanged")
