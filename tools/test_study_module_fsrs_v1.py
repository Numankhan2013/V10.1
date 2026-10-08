#!/usr/bin/env python3
"""Study modules must never seed FSRS with questions the learner did not reach."""
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
if "s.studyModuleId" not in function:
    raise SystemExit("nkMarkSkippedFromSession must ignore study-module sessions")
if "s.studyModuleId&&s.questionIds.some(id=>!s.submitted?.[id])" not in interaction or "exitStudyModule()" not in interaction:
    raise SystemExit("review-sheet Save & exit must keep an unfinished module instead of ending it")

harness = f"""
const assert=require('assert');
let state={{fsrsReviewEligible:{{}}}};const nkFindStudyQuestion=()=>null;
{function}
// An unfinished module: one answered, five never reached.
nkMarkSkippedFromSession({{studyModuleId:'m1',questionIds:['a','b','c','d','e','f'],answers:{{a:1}}}});
assert.deepEqual(state.fsrsReviewEligible,{{}},'study-module questions never reached must not enter FSRS');
// Deliberate Practice/CBT submissions keep their documented behavior.
nkMarkSkippedFromSession({{questionIds:['a','b','c'],answers:{{a:1}}}});
assert.deepEqual(Object.keys(state.fsrsReviewEligible).sort(),['b','c'],'submitted Practice/CBT skips remain eligible');
console.log('STUDY_MODULE_FSRS_OK');
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
    handle.write(harness)
    path = Path(handle.name)
try:
    subprocess.run(["node", str(path)], check=True)
finally:
    path.unlink(missing_ok=True)
print("STUDY_MODULE_FSRS_TEST_OK: unfinished modules never seed FSRS; Save & exit keeps the module open")
