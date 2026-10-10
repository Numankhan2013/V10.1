  /* NK_QUESTION_INTERACTION_INTEGRITY_V1_START */
  // Nested handlers share one durable commit. No render, navigation, or success
  // feedback is published until the complete action has been saved.
  let nkInteractionTransaction=null;
  function nkAfterQuestionCommit(effect){if(nkInteractionTransaction)nkInteractionTransaction.effects.push([effect,[]]);else effect();}
  const nkInteractionSave=saveState,nkInteractionNavigate=navigate;
  let nkInteractionRender=render;
  const nkInteractionToast=showToast;
  const nkFeedbackPatterns={choice:6,mark:9,primary:12,success:[12,24,16],error:[18,30,8],complete:[14,35,22]};
  let nkFeedbackAt=0;
  function nkPlayFeedback(kind){
    if(!Object.prototype.hasOwnProperty.call(nkFeedbackPatterns,kind))return;
    // Feedback accompanies meaningful committed changes, never general taps.
    const now=Date.now();if(now-nkFeedbackAt<60)return;nkFeedbackAt=now;
    try{
      if(location.hostname==='qbank.local'&&window.QBankHaptics?.play){window.QBankHaptics.play(kind);return;}
      if(typeof navigator!=='undefined'&&typeof navigator.vibrate==='function')navigator.vibrate(nkFeedbackPatterns[kind]);
    }catch(_){}
  }
  let nkAppNavigationTarget=null;
  function nkMarkAppNavigation(args){
    const target='#'+args[0]+(args[1]?'/'+encodeURIComponent(args[1]):'');
    if(location.hash!==target)nkAppNavigationTarget=target;
  }
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
    nkMarkAppNavigation(arguments);
    const result=nkInteractionNavigate.apply(this,arguments);
    if(route.page===arguments[0]&&location.hash===nkAppNavigationTarget)nkAppNavigationTarget=null;
    return result;
  };
  showToast=function(){if(nkInteractionTransaction){nkInteractionTransaction.effects.push([nkInteractionToast,[...arguments]]);return;}return nkInteractionToast.apply(this,arguments);};
  haptic=function(pattern){
    // Practice selection immediately submits: use its outcome pulse only.
    const kind=Array.isArray(pattern)?(pattern[0]>=16?'success':'error'):(state.activeSession?.mode==='exam'?'choice':'');
    if(!kind)return;
    if(nkInteractionTransaction){nkInteractionTransaction.effects.push([nkPlayFeedback,[kind]]);return;}
    nkPlayFeedback(kind);
  };
  function nkPatchExamChoice(){
    const s=state.activeSession,id=s?.questionIds?.[s.index],q=nkCurrentQuestion();
    if(route.page!=='exam'||s?.mode!=='exam'||!q)return false;
    const buttons=document.querySelector('.nk-v114-session.is-exam')?.querySelectorAll('.option-list button.option');
    if(!buttons||buttons.length!==q.options.length)return false;
    buttons.forEach((button,index)=>{
      const selected=Number(s.answers?.[id])===String(q.options[index].letter).toUpperCase().charCodeAt(0)-64;
      button.classList.toggle('selected',selected);button.setAttribute?.('aria-pressed',String(selected));
    });
    return true;
  }
  function nkPatchBookmark(){
    const q=nkCurrentQuestion();if(!q||!['practice','exam','review-test'].includes(route.page))return false;
    const buttons=document.querySelectorAll('.bookmark-toggle');if(!buttons.length)return false;
    const marked=Boolean(state.bookmarks[q.id]);
    buttons.forEach(button=>{button.classList.toggle('bookmarked',marked);button.setAttribute('aria-pressed',String(marked));button.setAttribute('aria-label',marked?'Remove bookmark':'Bookmark question');});
    nkPlayFeedback('mark');return true;
  }
  function nkPatchRecall(){
    const q=nkCurrentQuestion(),dock=document.querySelector('.nk-fsrs-rating');
    if(route.page!=='practice'||!q||!dock)return false;
    const markup=nkFsrsRatingMarkup(q.id);if(!markup)return false;
    // Keep the rating group and focused button mounted during edits.
    const template=document.createElement('template');template.innerHTML=markup;
    const next=template.content.firstElementChild;
    dock.querySelector('.nk-fsrs-recall-label').innerHTML=next.querySelector('.nk-fsrs-recall-label').innerHTML;
    const buttons=dock.querySelectorAll('button'),updated=next.querySelectorAll('button');
    if(buttons.length!==updated.length)return false;
    buttons.forEach((button,i)=>{button.className=updated[i].className;button.setAttribute('aria-pressed',updated[i].getAttribute('aria-pressed'));button.title=updated[i].title;});
    nkPlayFeedback('choice');return true;
  }
  function nkQuestionTransaction(action,paintAfterCommit){
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
      nkMarkAppNavigation(tx.navigation);
      nkFsrsOriginalNavigate.apply(null,tx.navigation);
      if(route.page===tx.navigation[0]&&location.hash===nkAppNavigationTarget)nkAppNavigationTarget=null;
    }
    if(tx.render&&!(paintAfterCommit&&paintAfterCommit()))nkInteractionRender();
    if(tx.navigation?.[0]==='result')nkPlayFeedback('complete');
    tx.effects.forEach(([fn,args])=>fn.apply(null,args));
    return result;
  }
  function nkQuestionAction(handler,guard=()=>true,paintAfterCommit=null){return function(){const args=[...arguments];if(!guard(...args))return false;return nkQuestionTransaction(()=>handler.apply(this,args),paintAfterCommit);};}
  function nkCurrentQuestion(){const s=state.activeSession;return s?nkPracticeResumeQuestion(s.questionIds?.[s.index]):null;}
  function nkValidQuestionOption(q,n){return Boolean(q)&&nkQuestionPresentationFor(q).valid&&Number.isInteger(Number(n))&&(q.options||[]).some(o=>String(o.letter).toUpperCase().charCodeAt(0)-64===Number(n));}
  const nkIntegritySelectPractice=selectPractice;
  selectPractice=nkQuestionAction(nkIntegritySelectPractice,(id,n,owner)=>{
    const s=state.activeSession,q=nkCurrentQuestion();
    return s?.mode==='practice'&&(owner==null||String(s.id)===String(owner))&&String(q?.id)===String(id)&&!s.submitted?.[id]&&nkValidQuestionOption(q,n);
  },()=>typeof nkPatchPracticeOutcome==='function'&&nkPatchPracticeOutcome());
  selectExam=nkQuestionAction(selectExam,(n,id,owner)=>{
    const s=state.activeSession,q=nkCurrentQuestion();
    return s?.mode==='exam'&&(id==null||String(q?.id)===String(id))&&(owner==null||String(s.id)===String(owner))&&!s.strictExpired?.[q?.id]&&(s.timerMode!=='per-question'||typeof nkStrictSpent!=='function'||nkStrictSpent(s,String(q?.id))<60000)&&nkValidQuestionOption(q,n);
  },nkPatchExamChoice);
  submitPractice=nkQuestionAction(submitPractice,()=>{const s=state.activeSession,q=nkCurrentQuestion();return s?.mode==='practice'&&q&&!s.submitted?.[q.id]&&nkValidQuestionOption(q,s.answers?.[q.id]);},()=>typeof nkPatchPracticeOutcome==='function'&&nkPatchPracticeOutcome());
  // A submitted question is immutable. Starting another session is the existing
  // way to practise again; Review cannot clear answers through a legacy callback.
  retryCurrent=nkQuestionAction(retryCurrent,()=>{const s=state.activeSession,id=s?.questionIds?.[s.index];return s?.mode==='practice'&&!s.submitted?.[id];});
  nextQ=nkQuestionAction(nextQ);
  prevQ=nkQuestionAction(prevQ);
  goIndex=nkQuestionAction(goIndex,i=>Number.isInteger(Number(i))&&Number(i)>=0&&Number(i)<(state.activeSession?.questionIds?.length||0));
  toggleBookmark=nkQuestionAction(toggleBookmark,id=>Boolean(nkPracticeResumeQuestion(id)),nkPatchBookmark);
  nkFsrsCommitPending=nkQuestionAction(nkFsrsCommitPending);
  nkFsrsRecoverPending=nkQuestionAction(nkFsrsRecoverPending);
  nkRateCurrent=nkQuestionAction(nkRateCurrent,r=>[2,3,4].includes(Number(r)),nkPatchRecall);
  nkFsrsUndo=nkQuestionAction(nkFsrsUndo);
  // Pause must save its pending recall rating and checkpoint together.
  const nkIntegrityPause=nkPausePractice;
  nkPausePractice=nkQuestionAction(function(){nkFsrsRecoverPending();const out=nkIntegrityPause.apply(this,arguments);if(out!==false)nkAfterQuestionCommit(()=>nkPlayFeedback('primary'));return out;});
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
    // An unfinished study module "Save & exit" keeps its progress; it is never submitted.
    const out=s.mode==='exam'?submitExam(false):(s.studyModuleId&&s.questionIds.some(id=>!s.submitted?.[id])&&typeof exitStudyModule==='function'?exitStudyModule():endSession());
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
  // Browser/PWA system Back changes history before hashchange renders the next
  // route. Keep the question entry when the learner declines to leave.
  // Packaged Android uses its native Back confirmation at qbank.local.
  window.addEventListener('popstate',()=>{
    if(location.hostname==='qbank.local')return;
    if(location.hash===nkAppNavigationTarget){nkAppNavigationTarget=null;return;}
    const s=state.activeSession;
    if(!s||!['practice','exam'].includes(s.mode)||route.page!==s.mode)return;
    if(parseHash().page===route.page)return;
    const current='#'+route.page+(route.id?'/'+encodeURIComponent(route.id):'');
    const detail=s.mode==='exam'?'Your timed test will keep running if you exit now.':'Your practice progress will be saved if you exit now.';
    if(!window.confirm('Do you want to exit?\n\n'+detail))history.pushState(null,'',current);
  },true);
  // Browser history and Android WebView.goBack share this route boundary.
  // Commit pending recall before leaving; keep the old route on storage failure.
  window.addEventListener('hashchange',()=>{
    if(location.hash===nkAppNavigationTarget)nkAppNavigationTarget=null;
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
