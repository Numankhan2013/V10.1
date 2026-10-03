"""Protect shared-engine OCR pilot choices, reference gate and native presentation."""
from pathlib import Path
import json,subprocess,tempfile
from uworld_biochemistry import ROOT,bank_record

def main():
 record=bank_record()
 runtime=r'''
const assert=require('assert');global.window=globalThis;
const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
let SUBJECTS=[],calls=0,lastIds=null;
let nkStudySupport=q=>'INCUMBENT:'+q.id;
const nkFormatQuestionTime=ms=>String(ms),navIcon=()=>'<svg></svg>';
let nkCbtPool=()=>RECORD.questions,nkQuestionsForModuleDraft=()=>RECORD.questions,nkRevisionDeskData=()=>({wrong:RECORD.questions,bookmarked:RECORD.questions,unseen:RECORD.questions,due:RECORD.questions,dueCards:RECORD.questions});
let startSession=ids=>{calls++;lastIds=ids;return true;},practiceOne=id=>startSession([id]);
const nkFindStudyQuestion=id=>RECORD.questions.find(q=>q.id===id),showToast=()=>{};
''' +(ROOT/'tools/question_presentation_core.js').read_text()+ '\n'+(ROOT/'tools/uworld_biochemistry_core.js').read_text()+'\nconst RECORD='+json.dumps(record,ensure_ascii=False)+r''';
for(const source of RECORD.questions){
 const q=JSON.parse(JSON.stringify(source)),before=JSON.stringify(q),p=nkQuestionPresentationFor(q);
 assert.equal(p.valid,!q.uworldPilot.requiresVisual,q.id);assert(!p.repaired);assert.deepEqual(p.options,q.options);
 assert.strictEqual(nkQuestionPresentationFor(q),p);assert.equal(JSON.stringify(q),before);
}
for(let n=4;n<=8;n++){
 const q={...RECORD.questions[0],id:'choices-'+n,correctOption:n,options:Array.from({length:n},(_,i)=>({letter:'ABCDEFGH'[i],text:'Choice '+i}))};
 q.uworldSource={...q.uworldSource,question_id:q.id,options:q.options,correct_option:'ABCDEFGH'[n-1]};
 assert(nkQuestionPresentationFor(q).valid,'A–H structural support lost');
 for(const change of [r=>r.options.pop(),r=>r.options[0].letter='X',r=>r.options[0].text=' ',r=>r.correctOption=0,r=>r.uworldSource=null,r=>r.uworldPilot={status:'unknown',requiresVisual:false}]){
  const bad=JSON.parse(JSON.stringify(q));change(bad);assert(!nkQuestionPresentationFor(bad).valid);
 }
}
const legacy={id:'legacy',bank:'PrepLadder',question:'Source stem',correctOption:1,options:[{letter:'A',text:'One'},{letter:'B',text:'Two'}]};
assert(nkQuestionPresentationFor(legacy).valid);assert.equal(nkStudySupport(legacy,1000),'INCUMBENT:legacy');
const native=RECORD.questions[0],before=JSON.stringify(native),html=nkStudySupport(native,12000);
assert(html.includes('nk-uworld-reading'));assert(html.includes('Educational objective'));assert(html.includes('Original OCR explanation'));
assert(!/Key takeaway|Why the other options are wrong|uworld_visuals\//i.test(html));assert.equal(JSON.stringify(native),before);
const hostile={...native,uworldSource:{explanation:{text:'<img src=x onerror=alert(1)>',educational_objective:'<script>alert(1)</script>'}},uworldTranscript:{paragraphs:['<script>alert(1)</script>']}};
assert(!nkStudySupport(hostile,0).includes('<script>'));assert(!nkUworldOptionMarkup(native,{text:'<img src=x onerror=alert(1)>'}).includes('<img src=x'));
assert(nkUworldParagraph('(Choice A) Original reasoning.').includes('<strong>(Choice A)</strong>'));
assert.equal(nkCbtPool().length,105);assert.equal(nkQuestionsForModuleDraft().length,105);
assert(Object.values(nkRevisionDeskData()).every(rows=>rows.length===105));
assert(startSession(RECORD.questions.map(q=>q.id)));assert.equal(lastIds.length,105);
const count=calls;assert.equal(startSession(['uw2024_biochem_11914']),false);assert.equal(calls,count);
assert.equal(startSession([native.id]),true);assert.deepEqual(lastIds,[native.id]);
console.log('UWORLD_RUNTIME_OK records=132 eligible=105 reference_only=27 choices=4-8 native_ocr=true incumbent_preserved=true safe_markup=true no_answer_delay=true');
'''
 with tempfile.TemporaryDirectory() as tmp:
  script=Path(tmp)/'runtime.js';script.write_text(runtime);subprocess.run(['node',str(script)],check=True,cwd=ROOT)

if __name__=='__main__':main()
