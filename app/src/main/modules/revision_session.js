  /* NK_REVISION_SESSION_V1_START */
  // Revision uses the shared Practice engine and durable checkpoint collection.
  // Only explicitly tagged hub queues opt in; chapter/module/exam behavior stays owned elsewhere.
  function nkRevisionSessionKind(s){
    const kind=String(s?.revisionQueueKind||s?.practiceContext?.revisionQueueKind||'');
    return s?.mode==='practice'&&!s.studyModuleId&&['wrong','bookmarks','due'].includes(kind)?kind:'';
  }
  const nkRevisionResumeEligible=nkPracticeResumeEligible;
  nkPracticeResumeEligible=function(s){return Boolean(nkRevisionSessionKind(s)&&!nkPracticeTerminal(s))||nkRevisionResumeEligible(s);};
  const nkRevisionDurableEligible=nkNormalPracticeSession;
  nkNormalPracticeSession=function(s){return Boolean(nkRevisionSessionKind(s))||nkRevisionDurableEligible(s);};
  const nkRevisionPrepare=nkPracticePrepareSession;
  nkPracticePrepareSession=function(s){
    const kind=nkRevisionSessionKind(s),scope=s?.practiceContext?.revisionScope;
    const identity=nkRevisionPrepare.apply(this,arguments);
    if(kind)s.practiceContext={...s.practiceContext,revisionQueueKind:kind,revisionScope:scope||{},revisionContext:kind==='due'?'fsrs':kind==='wrong'?'wrong':'bookmarked'};
    return identity;
  };
  const nkRevisionRestore=nkPracticeSessionFromCheckpoint;
  nkPracticeSessionFromCheckpoint=function(cp){
    if(cp?.context?.revisionQueueKind!=null&&!['wrong','bookmarks','due'].includes(String(cp.context.revisionQueueKind)))return null;
    const restored=nkRevisionRestore.apply(this,arguments),kind=String(cp?.context?.revisionQueueKind||'');
    if(restored&&['wrong','bookmarks','due'].includes(kind)){
      restored.revisionQueueKind=kind;restored.context=kind==='due'?'fsrs':kind==='wrong'?'wrong':'bookmarked';restored.originRoute='quick-revision';
    }
    return restored;
  };
  function nkRevisionTagSession(kind,previous,ids){
    const s=state.activeSession;if(!s||s.id===previous||s.mode!=='practice'||!['wrong','bookmarks','due'].includes(kind)||s.questionIds.join('\u001f')!==ids.join('\u001f'))return false;
    s.revisionQueueKind=kind;s.originRoute='quick-revision';s.lifecycle='active';s.sessionQuestionIds=[...ids];
    s.practiceContext={...(s.practiceContext||{}),revisionQueueKind:kind,revisionScope:{...nkRevisionScope}};
    nkPracticePrepareSession(s);nkPracticeStoreCheckpoint(nkPracticeBuildCheckpoint(s,'active'));return saveState();
  }
  nkStartRevisionQueue=nkQuestionAction(nkStartRevisionQueue);
  function nkRevisionPausedMarkup(){
    const saved=nkPracticeCheckpoints(false).filter(cp=>['wrong','bookmarks','due'].includes(String(cp.context?.revisionQueueKind)));
    if(!saved.length)return '';
    return '<section class="nk-revision-paused" aria-label="Paused revision"><h2>Pick up where you paused</h2>'+saved.map(cp=>{
      const kind=cp.context.revisionQueueKind,label=kind==='wrong'?'mistakes':kind==='due'?'due review':'bookmarks',done=cp.sessionQuestionIds.filter(id=>cp.submitted?.[id]).length;
      const scope=cp.context.revisionScope||{},record=scope.subject&&scope.bank&&typeof nkBankRecord==='function'?nkBankRecord(scope.subject,scope.bank):null,topic=record?.topics?.find(t=>String(t.id)===String(scope.topic));
      const focus=[scope.subject||'All subjects',scope.bank||'All banks',topic?.title||topic?.name].filter(Boolean).join(' · ');
      return '<div class="nk-revision-paused-row"><span><strong>'+esc(cp.context.title||'Revision')+'</strong><small>'+esc(focus)+'</small><small>'+fmtNum(done)+' of '+fmtNum(cp.sessionQuestionIds.length)+' answered · saved position '+fmtNum(Number(cp.position?.index||0)+1)+'</small></span><button type="button" class="primary-btn" onclick="window.QB.nkResumePracticeById('+esc(JSON.stringify(String(cp.sessionId)))+')">Resume '+label+'</button></div>';
    }).join('')+'</section>';
  }
  const nkRevisionPause=nkPausePractice;
  nkPausePractice=nkQuestionAction(function(){
    const revision=Boolean(nkRevisionSessionKind(state.activeSession)),result=nkRevisionPause.apply(this,arguments);
    if(revision&&result!==false)navigate('quick-revision');return result;
  });
  function nkRevisionFinish(){
    const s=state.activeSession;if(!nkRevisionSessionKind(s)||nkPracticeTerminal(s))return false;
    if(typeof savePracticeElapsed==='function')savePracticeElapsed();
    // Recover a selected legacy answer through the same answer/FSRS path once.
    const index=s.index;
    s.questionIds.forEach((id,i)=>{if(!s.submitted?.[id]&&nkValidQuestionOption(nkPracticeResumeQuestion(id),s.answers?.[id])){s.index=i;submitPractice();}});
    s.index=index;nkFsrsRecoverPending();nkPracticePrepareSession(s);
    // Same skip rule as every session: only questions passed over before the last answered one.
    if(typeof nkMarkSkippedFromSession==='function')nkMarkSkippedFromSession(s);
    const all=nkPracticeSessionIds(s),ids=all.filter(id=>s.submitted?.[id]&&nkValidQuestionOption(nkPracticeResumeQuestion(id),s.answers?.[id])),now=Date.now();
    const answers=Object.fromEntries(ids.map(id=>[id,s.answers[id]])),times=Object.fromEntries(ids.map(id=>[id,Number(s.questionTimes?.[id]||0)])),correct=ids.filter(id=>Number(nkPracticeResumeQuestion(id)?.correctOption)===Number(answers[id])).length;
    s.lifecycle='submitted';s.submittedAt=now;const cp=nkPracticeBuildCheckpoint(s,'submitted');cp.terminalAt=now;nkPracticeStoreCheckpoint(cp);
    const resultId='practice_'+String(s.id);
    if(ids.length&&!state.tests.some(t=>String(t.id)===resultId)){
      state.tests.push({id:resultId,sessionId:String(s.id),title:s.title,kind:'practice',questionIds:ids,answers,questionTimes:times,correct,incorrect:ids.length-correct,unattempted:0,total:ids.length,attempted:ids.length,totalTimeMs:Object.values(times).reduce((a,b)=>a+b,0),createdAt:now,autoSubmitted:false,originRoute:'quick-revision',revisionQueueKind:nkRevisionSessionKind(s)});
      state.tests=state.tests.slice(-100);
    }
    // Ending a revision pass never records skipped attempts, and never touches questions after the last one answered.
    nkFsrsSessionOrigin=null;state.activeSession=null;if(saveState()===false)return false;
    nkPracticeCloseOverlays();navigate(ids.length?'result':'quick-revision',ids.length?resultId:undefined);return true;
  }
  const nkRevisionFinishAction=nkQuestionAction(nkRevisionFinish);
  const nkRevisionOriginalFinish=finishPracticeSession;
  finishPracticeSession=function(){return nkRevisionSessionKind(state.activeSession)?nkRevisionFinishAction():nkRevisionOriginalFinish.apply(this,arguments);};
  function nkFinishRevisionSession(){return nkRevisionFinishAction();}
  const nkRevisionReview=openSessionReview;
  openSessionReview=function(){
    const revision=Boolean(nkRevisionSessionKind(state.activeSession)),result=nkRevisionReview.apply(this,arguments);if(!revision)return result;
    const box=document.getElementById('nk-session-review');if(!box)return result;
    box.querySelector('[role="dialog"]')?.setAttribute('aria-label','Your revision session');
    const heading=box.querySelector('.nk-session-review-head h2');if(heading)heading.textContent='Your revision session';
    const sub=box.querySelector('.nk-session-review-head p');if(sub)sub.textContent='Keep going through your set, or stop here for today. Tap any question to return to it.';
    const mode=box.querySelector('.mode-pill');if(mode)mode.textContent='Revision · Session';
    box.querySelector('.nk-session-review-warning,.nk-session-review-ready')?.remove();
    const actions=box.querySelector('.nk-session-review-actions');if(actions)actions.innerHTML='<p class="nk-revision-session-help">Pause to continue this same set later. Finish saves only the questions you answered; the rest stay in Revision.</p><button type="button" class="primary-btn nk-practice-pause" onclick="window.QB.nkPausePractice()">Pause</button><button type="button" class="primary-btn nk-practice-submit" onclick="window.QB.nkFinishRevisionSession()">Finish session</button>';
    return result;
  };
  /* NK_REVISION_SESSION_V1_END */
