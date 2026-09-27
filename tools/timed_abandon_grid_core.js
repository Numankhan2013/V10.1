  /* NK_TIMED_ABANDON_GRID_V1_START */
  function nkAbandonTimedTest(){
    const s=state.activeSession;
    if(!s||s.mode!=='exam'||s.__terminalSaveInFlight)return false;
    if(!confirm('Abandon this timed test? Your answers will be discarded and no test result will be saved.'))return false;
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));
    state.activeSession=null;
    if(saveState()===false){state=before;return false;}
    closeQuestionNavigator();closeSessionReview();
    navigate('tests');showToast('Timed test abandoned.');return true;
  }
  const nkAbandonOriginalNavigator=openQuestionNavigator;
  openQuestionNavigator=function(){
    const result=nkAbandonOriginalNavigator.apply(this,arguments);
    if(state.activeSession?.mode!=='exam')return result;
    const root=document.getElementById('qb-question-navigator'),submit=root?.querySelector('.qb-nav-submit');
    if(submit&&!root.querySelector('.nk-abandon-test')){
      root.classList.add('nk-timed-abandon-grid');
      submit.insertAdjacentHTML('afterend','<button type="button" class="nk-abandon-test" onclick="window.QB.nkAbandonTimedTest()">Abandon test</button>');
    }
    return result;
  };
  const nkAbandonOriginalReview=openSessionReview;
  openSessionReview=function(){
    const result=nkAbandonOriginalReview.apply(this,arguments);
    if(state.activeSession?.mode!=='exam')return result;
    const root=document.getElementById('nk-session-review'),actions=root?.querySelector('.nk-session-review-actions');
    if(actions&&!actions.querySelector('.nk-abandon-test')){
      root.classList.add('nk-timed-abandon-grid');
      actions.insertAdjacentHTML('beforeend','<button type="button" class="nk-abandon-test" onclick="window.QB.nkAbandonTimedTest()">Abandon test</button>');
    }
    return result;
  };
  /* NK_TIMED_ABANDON_GRID_V1_END */
