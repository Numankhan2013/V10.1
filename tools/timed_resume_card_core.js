  /* NK_TIMED_RESUME_CARD_V1_START */
  function nkTimedResumeCard(place){
    const s=state.activeSession;
    if(!s||s.mode!=='exam'||s.lifecycle==='submitted')return '';
    const total=(s.questionIds||[]).length;
    if(!total)return '';
    const answered=s.questionIds.filter(id=>Boolean(s.answers?.[id])).length;
    const marked=s.questionIds.filter(id=>s.markedForReview?.[String(id)]===true).length;
    const expired=typeof nkTimedSessionExpired==='function'&&nkTimedSessionExpired(s);
    const kind=s.timerMode==='per-question'?'Topic test':'Timed CBT';
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
