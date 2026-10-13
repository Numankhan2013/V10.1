  /* NK_TIMED_RESUME_CARD_V1_START */
  function nkTimedResumeDetails(s){
    const total=(s.questionIds||[]).length;
    return {total,answered:s.questionIds.filter(id=>Boolean(s.answers?.[id])).length,
      marked:s.questionIds.filter(id=>s.markedForReview?.[String(id)]===true).length,
      expired:typeof nkTimedSessionExpired==='function'&&nkTimedSessionExpired(s),
      kind:s.timerMode==='per-question'?'Topic test':'Timed CBT'};
  }
  function nkTimedFocusCard(){
    const s=state.activeSession;
    if(!s||s.mode!=='exam'||s.lifecycle==='submitted')return '';
    const {total,answered,marked,expired,kind}=nkTimedResumeDetails(s);
    if(!total)return '';
    return `<section class="nk-home-focus-card nk-home-timed-focus" aria-label="Today's Focus: timed test in progress"><div class="nk-home-focus-label">TODAY'S FOCUS · ${expired?'TIME LIMIT REACHED':'TEST IN PROGRESS'}</div><h2>${esc(s.title||kind)}</h2><p>${answered} of ${total} answered · ${marked} marked for review</p><p>${expired?'Finish the timed test to see your result.':'The timer keeps running while you are away.'}</p><button type="button" class="nk-focus-primary nk-home-focus-action" onclick="window.QB.nkResumeTimedTest()"><span>${expired?'Finish timed test':'Resume timed test'}</span><span aria-hidden="true">→</span></button></section>`;
  }
  function nkTimedResumeCard(place){
    const s=state.activeSession;
    if(!s||s.mode!=='exam'||s.lifecycle==='submitted')return '';
    const {total,answered,marked,expired,kind}=nkTimedResumeDetails(s);
    if(!total)return '';
    return `<section class="nk-timed-resume is-${place}" aria-label="Timed test in progress"><div class="nk-timed-resume-copy"><span>${expired?'TIME LIMIT REACHED':'TEST IN PROGRESS'}</span><h2>${esc(s.title||kind)}</h2><p>${answered} of ${total} answered${marked?` · ${marked} marked for review`:''}</p><small>${expired?'Finish the timed test to see your result.':'The timer keeps running while you are away.'}</small></div><button type="button" onclick="window.QB.nkResumeTimedTest()">${expired?'Finish timed test':'Resume timed test'} ${navIcon('chevron',17)}</button></section>`;
  }
  function nkResumeTimedTest(){
    const s=state.activeSession;
    if(!s||s.mode!=='exam'){showToast('There is no timed test in progress.','bad');return false;}
    if(typeof nkTimedSessionExpired==='function'&&nkTimedSessionExpired(s)){
      if(s.timerMode==='per-question')nkExpireTopicQuestion();
      else submitExam(true);
      if(state.activeSession?.mode!=='exam')return true;
    }
    navigate('exam');return true;
  }
  /* NK_TIMED_RESUME_CARD_V1_END */
