#!/usr/bin/env python3
"""Skip rule: only questions passed over BEFORE the last answered one may enter FSRS."""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
home = (ROOT / "tools/apply_home_command_center_v1.py").read_text(encoding="utf-8")
interaction = (ROOT / "tools/question_interaction_core.js").read_text(encoding="utf-8")

match = re.search(r"  function nkMarkSkippedFromSession\(s\)\{.*?\n  \}\n", home, re.S)
if not match:
    raise SystemExit("nkMarkSkippedFromSession source owner not found")
function = match.group(0)
if "s.studyModuleId" in function:
    raise SystemExit("the skip rule is shared by modules, Practice, CBT and Revision; no module special case")
if "s.studyModuleId&&s.questionIds.some(id=>!s.submitted?.[id])" not in interaction or "exitStudyModule()" not in interaction:
    raise SystemExit("review-sheet Save & exit must keep an unfinished module instead of ending it")

harness = f"""
const assert=require('assert');
let state={{fsrsReviewEligible:{{}},attempts:{{}}}};const nkFindStudyQuestion=()=>null,qAttempts=id=>state.attempts[id]||[];
{function}
const ids=n=>Array.from({{length:n}},(_,i)=>'q'+(i+1)),run=(session)=>{{state.fsrsReviewEligible={{}};nkMarkSkippedFromSession(session);return Object.keys(state.fsrsReviewEligible).sort((a,b)=>Number(a.slice(1))-Number(b.slice(1)));}};
// Your example: 20 questions, answered 1, 3, 4 and 5. Question 2 was passed over; 6-20 were never reached.
assert.deepEqual(run({{questionIds:ids(20),answers:{{q1:1,q3:1,q4:1,q5:1}}}}),['q2'],'only the skipped question before the last answer enters FSRS');
// Looking at question 6 after answering 5 does not matter: it comes after the last answer.
assert.deepEqual(run({{questionIds:ids(20),answers:{{q1:1,q5:1}}}}),['q2','q3','q4']);
// Nothing answered: nothing enters FSRS.
assert.deepEqual(run({{questionIds:ids(20),answers:{{}}}}),[],'a session with no answers marks nothing');
// Study modules follow the same rule (no special case).
assert.deepEqual(run({{studyModuleId:'m1',questionIds:ids(6),answers:{{q1:1}}}}),[]);
assert.deepEqual(run({{studyModuleId:'m1',questionIds:ids(6),answers:{{q1:1,q4:1}}}}),['q2','q3']);
// Only the last answered question defines the boundary, wherever it is in the list.
assert.deepEqual(run({{questionIds:ids(5),answers:{{q5:1}}}}),['q1','q2','q3','q4']);
// Questions that already have history are already in FSRS: no stale skip entry.
state.attempts={{q2:[{{id:'old'}}]}};assert.deepEqual(run({{questionIds:ids(5),answers:{{q1:1,q4:1}}}}),['q3']);
console.log('SKIP_RULE_OK');
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
    handle.write(harness)
    path = Path(handle.name)
try:
    subprocess.run(["node", str(path)], check=True)
finally:
    path.unlink(missing_ok=True)
print("SKIP_RULE_TEST_OK: only questions before the last answered one can enter FSRS; Save & exit keeps an unfinished module open")
