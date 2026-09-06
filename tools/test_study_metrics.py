"""Execute the real Home template and Topics completion expression in Node.

No medical content or user study data is needed; fixtures exercise the same
subject-array and attempt-history shapes used by the application.
"""
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "tools/apply_home_visual_redesign_v4.py").read_text()
tree = ast.parse(source)
dashboard = next(
    ast.literal_eval(node.value) for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "DASHBOARD"
            for target in node.targets)
)
topic_source = (ROOT / "tools/apply_home_v5_fixes.py").read_text()
match = re.search(r"const s=chapterStats\(c.id\),pct=(.*?);return", topic_source)
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
  totalAttempted:()=>1, overallAccuracy:()=>0,
  pendingReviewCount:()=>0, wrongQuestions:()=>[], bookmarkedQuestions:()=>[],
  chapterPerformanceRows:()=>[], greetingCopy:()=>'Hello', testRow:()=>'',
  qAttempts:id=>Array.isArray(attempts[id])?attempts[id]:[],
  fmtNum:value=>Number(value).toLocaleString('en-US'), fmtPct:value=>value+'%',
  esc:String, shell:markup=>markup
};
vm.createContext(ctx);
vm.runInContext(DASHBOARD, ctx);
function rows() {
  return vm.runInContext('dashboard()', ctx).match(/<button type="button" class="nk-home-v4-subject[\s\S]*?<\/button>/g);
}
let result=rows();
assert.equal(result.length,3);
assert.match(result[0],/2 questions · 1 topics/);
assert.match(result[0],/subject-pct">50%/);
assert.match(result[1],/3 questions · 2 topics/);
assert.match(result[1],/subject-pct">33%/);
assert.match(result[2],/0 questions · 0 topics/);
assert.match(result[2],/subject-pct">0%/);
assert.ok(!result.join('').includes('NaN'));
// Changing the active subject must not change other subjects' denominators.
ctx.activeSubject='Physiology'; ctx.QUESTIONS=subjects[1].questions;
result=rows();
assert.match(result[0],/2 questions · 1 topics/);
assert.match(result[0],/subject-pct">50%/);
// Missing optional arrays and empty attempt histories are safe.
subjects.push({subject:'Empty'});
attempts['bio-2']=[];
assert.match(rows()[3],/0 questions · 0 topics/);
const before=JSON.stringify(attempts);
rows();
assert.equal(JSON.stringify(attempts),before);
const completion=s=>vm.runInNewContext(EXPRESSION,{s,Math});
assert.equal(completion({total:4,attempted:2,accuracy:0}),50);
assert.equal(completion({total:4,attempted:2,accuracy:100}),50);
assert.equal(completion({total:0,attempted:0,accuracy:0}),0);
assert.equal(completion({total:4,attempted:9,accuracy:0}),100);
assert.equal(completion({total:4,attempted:-1,accuracy:0}),0);
console.log('STUDY_METRICS_OK: arrays, subject isolation, unique attempts, wrong answers, empty data, bounds, read-only state');
"""
program = ("const DASHBOARD=" + json.dumps(dashboard) + ";\n"
           + "const EXPRESSION=" + json.dumps(expression) + ";\n" + js)
subprocess.run(["node", "-"], input=program, text=True, check=True)
