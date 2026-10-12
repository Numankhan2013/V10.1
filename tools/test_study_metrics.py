"""Execute the real Home subject cards and Topics completion expression in Node.

No medical content or user study data is needed; fixtures exercise the same
subject-array and attempt-history shapes used by the application.
"""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8")


def section(start, end):
    if page.count(start) != 1 or end not in page.split(start, 1)[1]:
        raise SystemExit(f"App page section not found: {start}")
    return start + page.split(start, 1)[1].split(end, 1)[0]


home = (section("function nkPreferredRecord(", "function nkOpenSubjectLibrary(")
        + section("function nkSubjectCardsV3(", "function nkTopicTitleForQuestion(")
        + section("function chapterStats(", "function wrongQuestions("))
match = re.search(r"const x=chapterStats\(c.id\),pct=(.*?),status=", page)
if not match:
    raise SystemExit("Topics completion expression not found")
expression = match.group(1)

js = r"""
const assert = require('node:assert/strict');
const vm = require('node:vm');
const subjects = [
  {subject:'Biochemistry',questions:[{id:'bio-1'},{id:'bio-2'}],topics:[{}]},
  {subject:'Physiology',questions:[{id:'phys-1'},{id:'phys-2'},{id:'phys-3'}],topics:[{},{}]},
  {subject:'Anatomy',questions:[],topics:[]}
];
const attempts = {
  'bio-1':[{correct:false},{correct:false}],
  'phys-2':[{correct:true}],
  'unrelated-question':[{correct:true}]
};
const ctx = {
  SUBJECTS:subjects, activeSubject:'Biochemistry',
  QUESTIONS:subjects[0].questions,
  state:{attempts,tests:[]},
  qAttempts:id=>Array.isArray(attempts[id])?attempts[id]:[],
  chapterQuestions:()=>[],
  fmtNum:value=>Number(value).toLocaleString('en-US'),
  esc:String, navIcon:()=>'', nkAppSubjectMeta:()=>({key:'subject'}), nkAppSubjectIcon:()=>''
};
vm.createContext(ctx);
vm.runInContext(HOME, ctx);
function rows() {
  return vm.runInContext('nkSubjectCardsV3()', ctx).match(/<button class="nk-v3-subject-card[\s\S]*?<\/button>/g);
}
let result=rows();
assert.equal(result.length,3);
assert.match(result[0],/1 topics · 2 questions/);
assert.match(result[0],/<b>50%<\/b>/);
assert.match(result[1],/2 topics · 3 questions/);
assert.match(result[1],/<b>33%<\/b>/);
assert.match(result[2],/0 topics · 0 questions/);
assert.match(result[2],/<b>0%<\/b>/);
assert.ok(!result.join('').includes('NaN'));
// Changing the active subject must not change other subjects' denominators.
ctx.activeSubject='Physiology'; ctx.QUESTIONS=subjects[1].questions;
result=rows();
assert.match(result[0],/1 topics · 2 questions/);
assert.match(result[0],/<b>50%<\/b>/);
// Missing optional arrays and empty attempt histories are safe.
subjects.push({subject:'Empty'});
attempts['bio-2']=[];
assert.match(rows()[3],/0 topics · 0 questions/);
// A question shared by two banks of one subject is counted once.
ctx.nkBankRecords=s=>s==='Biochemistry'?[{bank:'Marrow',questions:[{id:'bio-1'},{id:'bio-2'}],topics:[{}]},{bank:'PrepLadder',questions:[{id:'bio-1'}],topics:[{}]}]:[];
assert.match(rows()[0],/2 topics · 2 questions[\s\S]*<b>50%<\/b>/);
delete ctx.nkBankRecords;
const before=JSON.stringify(attempts);
rows();
assert.equal(JSON.stringify(attempts),before);
const completion=s=>vm.runInNewContext(EXPRESSION,{x:s,Math});
assert.equal(completion({total:4,attempted:2,accuracy:0}),50);
assert.equal(completion({total:4,attempted:2,accuracy:100}),50);
assert.equal(completion({total:0,attempted:0,accuracy:0}),0);
// Bounds: attempted is unique answered questions, so repeats cannot exceed the topic total.
ctx.chapterQuestions=()=>[{id:'bio-1'},{id:'bio-2'}];
attempts['bio-1']=[{correct:false},{correct:true},{correct:true},{correct:false,isUndo:true}];
const stats=vm.runInContext('chapterStats("t")',ctx);
assert.equal(stats.attempted,1);assert.equal(stats.total,2);
assert.equal(completion(stats),50);
attempts['bio-2']=[{correct:true},{correct:true}];
assert.equal(completion(vm.runInContext('chapterStats("t")',ctx)),100);
console.log('STUDY_METRICS_OK: arrays, subject isolation, unique attempts, wrong answers, empty data, bounds, read-only state');
"""
program = ("const HOME=" + json.dumps(home) + ";\n"
           + "const EXPRESSION=" + json.dumps(expression) + ";\n" + js)
subprocess.run(["node", "-"], input=program, text=True, check=True)
