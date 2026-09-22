  /* NK_QUESTION_INTERACTION_INTEGRITY_V1_START */
  // Nested handlers share one durable commit. No render, navigation, or success
  // feedback is published until the complete action has been saved.
  let nkInteractionTransaction=null;
  function nkAfterQuestionCommit(effect){if(nkInteractionTransaction)nkInteractionTransaction.effects.push([effect,[]]);else effect();}
  const nkInteractionSave=saveState,nkInteractionRender=render,nkInteractionNavigate=navigate;
  const nkInteractionToast=showToast,nkInteractionHaptic=haptic;
  saveState=function(){if(nkInteractionTransaction){nkInteractionTransaction.dirty=true;return true;}return nkInteractionSave.apply(this,arguments);};
  render=function(){if(nkInteractionTransaction){nkInteractionTransaction.render=true;return;}return nkInteractionRender.apply(this,arguments);};
  navigate=function(){
    if(nkInteractionTransaction){
      // Flush pending ratings while still inside the transaction, before route publication.
      nkFsrsRecoverPending();
      if(arguments[0]==='result'){
        const t=state.tests.find(t=>String(t.id)===String(arguments[1]));
        if(t)t.originRoute=state.activeSession?.originRoute||nkFsrsSessionOrigin||t.originRoute||(t.kind==='practice'?'topics':'tests');
        nkFsrsSessionOrigin=null;
      }
      nkInteractionTransaction.navigation=[...arguments];return;
    }
    return nkInteractionNavigate.apply(this,arguments);
  };
  showToast=function(){if(nkInteractionTransaction){nkInteractionTransaction.effects.push([nkInteractionToast,[...arguments]]);return;}return nkInteractionToast.apply(this,arguments);};
  haptic=function(){if(nkInteractionTransaction){nkInteractionTransaction.effects.push([nkInteractionHaptic,[...arguments]]);return;}return nkInteractionHaptic.apply(this,arguments);};
  function nkQuestionTransaction(action){
    if(nkInteractionTransaction)return action();
    const before=nkStateClone(state),tx={dirty:false,render:false,navigation:null,effects:[]};nkInteractionTransaction=tx;
    let result;
    try{
      result=action();
      if(result===false){state=before;return false;}
      if(tx.dirty&&nkInteractionSave()===false){state=before;return false;}
    }catch(error){state=before;nkStorageError('Question action was not saved. Try the action again',error);return false;}
    finally{nkInteractionTransaction=null;}
    if(tx.navigation){
      if(!['practice','exam','review-test'].includes(tx.navigation[0])){
        document.getElementById('nk-session-review')?.remove();document.getElementById('qb-question-navigator')?.remove();
      }
      nkFsrsOriginalNavigate.apply(null,tx.navigation);
    }
    if(tx.render)nkInteractionRender();
    tx.effects.forEach(([fn,args])=>fn.apply(null,args));
    return result;
  }
  function nkQuestionAction(handler,guard=()=>true){return function(){const args=[...arguments];if(!guard(...args))return false;return nkQuestionTransaction(()=>handler.apply(this,args));};}
  function nkCurrentQuestion(){const s=state.activeSession;return s?nkPracticeResumeQuestion(s.questionIds?.[s.index]):null;}
  function nkValidQuestionOption(q,n){return Boolean(q)&&Number.isInteger(Number(n))&&(q.options||[]).some(o=>String(o.letter).toUpperCase().charCodeAt(0)-64===Number(n));}
  const nkIntegritySelectPractice=selectPractice;
  selectPractice=nkQuestionAction(nkIntegritySelectPractice,(id,n)=>{
    const s=state.activeSession,q=nkCurrentQuestion();
    return s?.mode==='practice'&&String(q?.id)===String(id)&&!s.submitted?.[id]&&nkValidQuestionOption(q,n);
  });
  selectExam=nkQuestionAction(selectExam,n=>{
    const s=state.activeSession,q=nkCurrentQuestion();
    return s?.mode==='exam'&&!s.strictExpired?.[q?.id]&&nkValidQuestionOption(q,n);
  });
  submitPractice=nkQuestionAction(submitPractice,()=>{const s=state.activeSession,q=nkCurrentQuestion();return s?.mode==='practice'&&q&&!s.submitted?.[q.id]&&nkValidQuestionOption(q,s.answers?.[q.id]);});
  // A submitted question is immutable. Starting another session is the existing
  // way to practise again; Review cannot clear answers through a legacy callback.
  retryCurrent=nkQuestionAction(retryCurrent,()=>{const s=state.activeSession,id=s?.questionIds?.[s.index];return s?.mode==='practice'&&!s.submitted?.[id];});
  nextQ=nkQuestionAction(nextQ);
  prevQ=nkQuestionAction(prevQ);
  goIndex=nkQuestionAction(goIndex,i=>Number.isInteger(Number(i))&&Number(i)>=0&&Number(i)<(state.activeSession?.questionIds?.length||0));
  toggleBookmark=nkQuestionAction(toggleBookmark,id=>Boolean(nkPracticeResumeQuestion(id)));
  nkFsrsCommitPending=nkQuestionAction(nkFsrsCommitPending);
  nkFsrsRecoverPending=nkQuestionAction(nkFsrsRecoverPending);
  nkRateCurrent=nkQuestionAction(nkRateCurrent,r=>[2,3,4].includes(Number(r)));
  // Pause must save its pending recall rating and checkpoint together.
  const nkIntegrityPause=nkPausePractice;
  nkPausePractice=nkQuestionAction(function(){nkFsrsRecoverPending();return nkIntegrityPause.apply(this,arguments);});
  submitExam=nkQuestionAction(submitExam);
  const nkIntegrityFinishPractice=finishPracticeSession;
  finishPracticeSession=nkQuestionAction(function(){
    const s=state.activeSession;
    if(s?.mode==='practice'){
      const index=s.index;
      // Older clients can persist a selected but unsubmitted answer. Explicit
      // final Submit must record it through the same answer/FSRS path once.
      s.questionIds.forEach((id,i)=>{
        if(!s.submitted?.[id]&&nkValidQuestionOption(nkPracticeResumeQuestion(id),s.answers?.[id])){s.index=i;submitPractice();}
      });
      s.index=index;nkFsrsRecoverPending();
    }
    return nkIntegrityFinishPractice.apply(this,arguments);
  });
  nkSubmitPracticeSession=nkQuestionAction(nkSubmitPracticeSession);
  endSession=nkQuestionAction(endSession);
  if(typeof closeQuestionNavigator==='function'){
    const close=closeQuestionNavigator;closeQuestionNavigator=function(){nkAfterQuestionCommit(()=>close());};
  }
  if(typeof closeSessionReview==='function'){
    const close=closeSessionReview;closeSessionReview=function(){nkAfterQuestionCommit(()=>close());};
  }
  if(typeof sessionReviewGo==='function')sessionReviewGo=nkQuestionAction(function(i){
    if(goIndex(i)===false)return false;
    nkAfterQuestionCommit(()=>closeSessionReview());
  });
  if(typeof sessionReviewSubmit==='function')sessionReviewSubmit=nkQuestionAction(function(){
    const s=state.activeSession;if(!s)return false;
    const out=s.mode==='exam'?submitExam(false):endSession();
    if(out!==false)nkAfterQuestionCommit(()=>closeSessionReview());return out;
  });

  // A queued click belongs to the question visible at pointer-down. Reject an
  // old node (including programmatic stale clicks) and the second click of a
  // browser double-click, without throttling distinct keyboard/touch actions.
  function nkQuestionIdentity(){const s=state.activeSession;return s?`${s.id}|${s.mode}|${s.questionIds?.[s.index]}`:'';}
  let nkQuestionPointer=null;
  document.addEventListener('pointerdown',event=>{
    const target=event.target?.closest?.('.option,.nk-session-footer button,.nk-session-review-actions button,.nav-q');
    nkQuestionPointer=target?{target,identity:nkQuestionIdentity()}:null;
  },true);
  document.addEventListener('click',event=>{
    const target=event.target?.closest?.('.option,.nk-session-footer button,.nk-session-review-actions button,.nav-q');
    if(!target)return;
    const stale=!target.isConnected||(nkQuestionPointer?.target===target&&nkQuestionPointer.identity!==nkQuestionIdentity());
    nkQuestionPointer=null;
    if(stale||event.detail>1){event.preventDefault();event.stopImmediatePropagation();}
  },true);
  // Browser history and Android WebView.goBack share this route boundary.
  // Commit pending recall before leaving; keep the old route on storage failure.
  window.addEventListener('hashchange',()=>{
    const s=state.activeSession;if(!s||!['practice','exam'].includes(s.mode))return;
    const next=parseHash();if(next.page===route.page)return;
    const ok=nkQuestionTransaction(()=>{
      if(s.mode==='practice'){savePracticeElapsed();nkFsrsRecoverPending();}else saveExamElapsed();
      saveState();return true;
    });
    if(ok===false){history.replaceState(null,'','#'+route.page+(route.id?'/'+encodeURIComponent(route.id):''));return;}
    document.getElementById('nk-session-review')?.remove();document.getElementById('qb-question-navigator')?.remove();
  },true);
  /* NK_QUESTION_INTERACTION_INTEGRITY_V1_END */
