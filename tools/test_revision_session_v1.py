#!/usr/bin/env python3
"""Source contracts for opt-in continuous Revision sessions and answered-only completion."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]

def main():
    source=(ROOT/'tools/revision_session_core.js').read_text()
    script=r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const questions=Array.from({length:27},(_,i)=>({id:'q'+i,correctOption:2}));
const context={state:{activeSession:null,tests:[]},Date,esc:String,fmtNum:String,nkRevisionScope:{subject:'Biochemistry',bank:'UWorld',topic:''},
 document:{getElementById:()=>null},saveState:()=>true,navigate:(...args)=>{context.destination=args;},
 nkPracticeResumeEligible:s=>s?.mode==='practice'&&s.context==='normal',nkNormalPracticeSession:s=>s?.context==='normal',
 nkPracticeTerminal:s=>['submitted','completed','discarded'].includes(s?.lifecycle),
 nkPracticePrepareSession:s=>{s.practiceContext={title:s.title};return {};},
 nkPracticeSessionFromCheckpoint:cp=>cp?{id:cp.sessionId,mode:'practice',originRoute:'topics',context:'normal',practiceContext:{...cp.context}}:null,
 nkPracticeBuildCheckpoint:(s,lifecycle)=>({sessionId:s.id,sessionQuestionIds:[...s.sessionQuestionIds],context:{...s.practiceContext},lifecycle}),
 nkPracticeCheckpoints:()=>[],nkPracticeSessionIds:s=>s.sessionQuestionIds,nkPracticeResumeQuestion:id=>questions.find(q=>q.id===id),
 nkPracticeStoreCheckpoint:cp=>{context.checkpoint=cp;},nkStartRevisionQueue:()=>{},nkQuestionAction:fn=>fn,
 nkPausePractice:()=>true,finishPracticeSession:()=>{context.legacyFinished=true;},openSessionReview:()=>{},
 savePracticeElapsed:()=>{},nkFsrsRecoverPending:()=>{},nkValidQuestionOption:(q,n)=>q&&[1,2,3,4].includes(Number(n)),
 submitPractice:()=>{const s=context.state.activeSession;s.submitted[s.questionIds[s.index]]=true;},nkPracticeCloseOverlays:()=>{}};
vm.createContext(context);vm.runInContext(SOURCE,context);const call=x=>vm.runInContext(x,context);
const ids=questions.map(q=>q.id);
for(const kind of ['wrong','bookmarks','due']){
 const s={id:'revision-'+kind,mode:'practice',context:kind==='due'?'fsrs':kind==='wrong'?'wrong':'bookmarked',title:'Revision',questionIds:[...ids],index:1,answers:{q0:2},submitted:{q0:true},questionTimes:{q0:1250},practiceContext:{}};
 context.state={activeSession:s,tests:[]};
 assert(call('nkRevisionTagSession('+JSON.stringify(kind)+',null,'+JSON.stringify(ids)+')'));
 assert(call('nkPracticeResumeEligible(state.activeSession)'));assert(call('nkNormalPracticeSession(state.activeSession)'));
 assert.equal(context.checkpoint.sessionQuestionIds.length,27);assert.equal(context.checkpoint.context.revisionQueueKind,kind);
 assert.equal(context.checkpoint.context.revisionScope.subject,'Biochemistry');
 context.cp=context.checkpoint;
 const restored=call('nkPracticeSessionFromCheckpoint(cp)');assert.equal(restored.revisionQueueKind,kind);assert.equal(restored.originRoute,'quick-revision');assert.equal(restored.context,s.context);
 call('nkPracticePrepareSession(state.activeSession)');assert.equal(s.practiceContext.revisionQueueKind,kind);
 assert(call('nkFinishRevisionSession()'));assert.equal(context.state.activeSession,null);
 assert.deepEqual(Array.from(context.state.tests[0].questionIds),['q0']);assert.equal(context.state.tests[0].total,1);assert.equal(context.state.tests[0].unattempted,0);assert.equal(context.state.tests[0].correct,1);
 assert.equal(context.checkpoint.lifecycle,'submitted');assert.equal(context.checkpoint.sessionQuestionIds.length,27,'terminal checkpoint retains original membership');
 assert.equal(context.legacyFinished,undefined);assert.equal(call('nkFinishRevisionSession()'),false,'repeat finish cannot save a second result');
}
context.state.activeSession={id:'normal',mode:'practice',context:'normal'};call('finishPracticeSession()');assert(context.legacyFinished);
assert.equal(call('nkRevisionSessionKind({mode:"practice",revisionQueueKind:"unknown"})'),'');
assert.equal(call('nkRevisionSessionKind({mode:"exam",revisionQueueKind:"wrong"})'),'');
assert.equal(call('nkRevisionSessionKind({mode:"practice",studyModuleId:"m",revisionQueueKind:"wrong"})'),'');
context.cp={sessionId:'legacy',context:{}};assert.equal(call('nkPracticeSessionFromCheckpoint(cp).context'),'normal');
context.cp={sessionId:'unsupported',context:{revisionQueueKind:'unknown'}};assert.equal(call('nkPracticeSessionFromCheckpoint(cp)'),null);
console.log('REVISION_SESSION_SOURCE_OK fullSnapshot=true taggedOnly=true restoredKind=true answeredOnly=true');
'''.replace('SOURCE',repr(source),1)
    subprocess.run(['node','-e',script],check=True,cwd=ROOT)
if __name__=='__main__':main()
