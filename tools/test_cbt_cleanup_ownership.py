#!/usr/bin/env python3
"""Delayed submission cleanup cannot close a later study session's navigator."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    app=(ROOT/'app/src/main/assets/index.html').read_text()
    assert app.count('<script id="cbt-final-lock-v2">')==1,'final CBT lock must ship once'
    start=app.index('<script id="cbt-final-lock-v2">');lock=app[start:app.index('</script>',start)]
    assert app.count('  function cleanExamUi(')==1,'only the final lock may define submission cleanup'
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
cleanExamUi('');assert.equal(removed,1,'a repeated submit without an owner cannot touch a fresh exam');
session=null;cleanExamUi('old');assert.equal(removed,2);
console.log('CBT_CLEANUP_OWNERSHIP_OK review=true practice=true fresh_exam=true');
"""
    subprocess.run(['node','-e',harness],check=True)
if __name__=='__main__':main()
