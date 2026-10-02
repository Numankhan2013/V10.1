#!/usr/bin/env python3
"""Delayed submission cleanup cannot close a later study session's navigator."""
from pathlib import Path
import ast,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    module=ast.parse((ROOT/'tools/cbt_final_lock.py').read_text())
    lock=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='lock' for t in n.targets))
    cleanup=lock[lock.index('  function cleanExamUi('):lock.index('  // Preserve')]
    assert lock.count('()=>cleanExamUi(owner)')==3,'all delayed cleanups need session ownership'
    harness="""
const assert=require('node:assert/strict');let session={id:'old',mode:'exam'},removed=0;
const window={QB:{getState:()=>({activeSession:session})}};
const document={querySelectorAll:()=>[],getElementById:()=>({remove:()=>removed++})};
"""+cleanup+"""
cleanExamUi('old');assert.equal(removed,1);
session={id:'review-old',mode:'review'};cleanExamUi('old');assert.equal(removed,1);
session={id:'practice-new',mode:'practice'};cleanExamUi('old');assert.equal(removed,1);
session={id:'exam-new',mode:'exam'};cleanExamUi('old');assert.equal(removed,1);
session=null;cleanExamUi('old');assert.equal(removed,2);
console.log('CBT_CLEANUP_OWNERSHIP_OK review=true practice=true fresh_exam=true');
"""
    subprocess.run(['node','-e',harness],check=True)
if __name__=='__main__':main()
