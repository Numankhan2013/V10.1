#!/usr/bin/env python3
"""Reviewed source content, answer contracts, and drift rejection regressions."""
import json
import subprocess

from build_question_completeness_reviews import CORE, LEDGER, ROOT, load_inputs


def main():
    subprocess.run(['python3', 'tools/build_question_completeness_reviews.py', '--check'], cwd=ROOT, check=True)
    inputs, _ = load_inputs()
    ledger = json.loads(LEDGER.read_text())
    node = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert'),data=JSON.parse(fs.readFileSync(0,'utf8'));
const c={window:{},SUBJECTS:[],esc:v=>String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')};
vm.createContext(c);vm.runInContext(data.core,c);
let repaired=0,blocked=0;
for(const entry of data.entries){
 for(const variant of ['raw','learner','clean','normalized']){
  const q=JSON.parse(JSON.stringify(data.inputs[variant][entry.id]));delete q.__nkQuestionPresentation;
  const sourceQuestion=q.question,sourceOptions=JSON.stringify(data.inputs.normalized[entry.id].options),sourceKey=q.correctOption;
  const p=c.nkQuestionPresentationFor(q),html=c.nkQuestionStemMarkup(q);
  if(entry.display.blocked){assert(!p.valid,entry.id+' incomplete source answerable');assert(html.includes('Question content incomplete'));}
  else{
   assert(p.valid,entry.id+' '+variant+' reviewed repair unavailable');
   if(entry.display.question)assert.equal(p.stem,entry.display.question);
   if(entry.display.table){
    assert(html.includes('nk-match-table'),entry.id+' essential table not rendered');
    assert(p.table.prompt.trim(),entry.id+' question prompt lost');
    assert.equal(p.table.rows.length,entry.display.table.groups[0].length);
    assert(p.table.rows.every(row=>row.every(cell=>cell&&cell.label&&cell.value.trim())),entry.id+' lost label/cell');
    for(const group of entry.display.table.groups)for(const cell of group)assert(html.includes(c.nkScientificMarkup(cell.value)),entry.id+' missing source cell '+cell.value);
   }
   assert(!html.includes('[object Object]'));
   assert.equal(q.correctOption,entry.display.correctOption??sourceKey,entry.id+' answer key changed');
   if(entry.display.options)assert.equal(JSON.stringify(p.options),JSON.stringify(entry.display.options));
   else assert.equal(JSON.stringify(p.options),sourceOptions,entry.id+' assessment choices changed');
  }
  assert.equal(q.question,sourceQuestion,entry.id+' imported stem mutated');
  assert.strictEqual(c.nkQuestionPresentationFor(q),p);
  const again=JSON.parse(JSON.stringify(q));delete again.__nkQuestionPresentation;
  assert.equal(c.nkQuestionPresentationFor(again).valid,p.valid,entry.id+' re-presentation not idempotent');
  for(const mutate of [x=>x.question+=' changed',x=>x.sourcePage++,x=>x.options[0].text+=' changed']){
   const changed=JSON.parse(JSON.stringify(q));delete changed.__nkQuestionPresentation;mutate(changed);
   assert(!c.nkQuestionPresentationFor(changed).valid,entry.id+' stale reviewed source accepted');
  }
  if(entry.display.explanation||entry.display.explanationFirstParagraph){
   const changed=JSON.parse(JSON.stringify(q));delete changed.__nkQuestionPresentation;changed.explanation+=' changed';
   assert(!c.nkQuestionPresentationFor(changed).valid,entry.id+' stale explanation accepted');
  }
 }
 if(entry.display.blocked)blocked++;else repaired++;
}
for(const id of ['physiology-23-38','physiology-33-33']){
 const original=data.inputs.raw[id];assert.equal(original.correctOption,null);
 const q=JSON.parse(JSON.stringify(original)),p=c.nkQuestionPresentationFor(q);
 assert(p.valid);assert.equal(q.correctOption,1);assert.equal(p.options.length,5);
 assert.equal(p.options[0].text,'1 and 4 are correct');assert.equal(p.options[4].text,'Both A & D');
 assert.equal(JSON.stringify(q.options),JSON.stringify(original.options));
}
const unrelated={id:'unreviewed-combination',question:'Which statements are correct?',correctOption:1,
 options:['1,2','2,3','1,3','1,2,3'].map((text,index)=>({letter:'ABCD'[index],text}))};
assert(c.nkQuestionPresentationFor(unrelated).valid,'heuristic must not blanket-disable unreviewed content');
console.log('QUESTION_COMPLETENESS_BEHAVIOR_OK repairs='+repaired+' source_omissions='+blocked+' variants=4 drift_rejected=true keys=source_pinned');
'''
    payload = {'inputs': inputs, 'entries': ledger['entries'], 'core': CORE.read_text()}
    subprocess.run(['node', '-e', node], input=json.dumps(payload), text=True, cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
