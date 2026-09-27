  /* NK_TIMED_RESUME_CARD_V1_START */
  function nkTimedResumeCard(place){
    const sessions=typeof nkTimedSessions==='function'?nkTimedSessions():state.activeSession?.mode==='exam'?[state.activeSession]:[];
    if(!sessions.length)return '';
    return sessions.map(s=>{
      const total=(s.questionIds||[]).length;if(!total)return '';
      const answered=s.questionIds.filter(id=>Boolean(s.answers?.[id])).length;
      const marked=s.questionIds.filter(id=>s.markedForReview?.[String(id)]===true).length;
      const expired=typeof nkTimedSessionExpired==='function'&&nkTimedSessionExpired(s);
      const strict=s.timerMode==='per-question',kind=strict?'Topic test':'Timed CBT',id=esc(JSON.stringify(String(s.id)));
      const current=state.activeSession?.mode==='exam'&&String(state.activeSession.id)===String(s.id);
      return `<section class="nk-timed-resume is-${place}" aria-label="Saved timed test"><div class="nk-timed-resume-copy"><span>${expired?(strict?'QUESTION TIME REACHED':'TIME LIMIT REACHED'):current?'TEST IN PROGRESS':'SAVED TEST'}</span><h2>${esc(s.title||kind)}</h2><p>${answered} of ${total} answered${marked?` · ${marked} marked for review`:''}</p><small>${expired?(strict?'Open the test to advance from this question.':'Open the test to finish it and see your result.'):'The timer keeps running while you are away.'}</small></div><div class="nk-timed-resume-actions"><button type="button" onclick="window.QB.nkResumeTimedTest(${id})">${expired?(strict?'Resume topic test':'Finish timed test'):'Resume timed test'} ${navIcon('chevron',17)}</button><button type="button" class="nk-timed-discard" onclick="window.QB.nkDiscardTimedTest(${id})">Discard</button></div></section>`;
    }).join('');
  }
  function nkResumeTimedTest(sessionId){
    if(sessionId&&String(state.activeSession?.id)!==String(sessionId)){
      if(typeof nkActivateTimedSession!=='function'||!nkActivateTimedSession(sessionId))return false;
    }
    const s=state.activeSession;
    if(!s||s.mode!=='exam'){showToast('There is no timed test in progress.','bad');return false;}
    if(typeof nkTimedSessionExpired==='function'&&nkTimedSessionExpired(s)){
      if(s.timerMode==='per-question')nkExpireTopicQuestion();
      else submitExam(true);
      if(state.activeSession?.mode!=='exam')return true;
    }
    navigate('exam');return true;
  }
  function nkDiscardTimedTest(sessionId){
    const s=typeof nkTimedSessions==='function'?nkTimedSessions().find(item=>String(item.id)===String(sessionId)):null;
    if(!s)return false;
    if(!confirm(`Discard ${s.title||'this timed test'}? Your answers in this unfinished test will be removed.`))return false;
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));
    if(!nkTimedStoreSession(s,'discarded'))return false;
    if(state.activeSession?.mode==='exam'&&String(state.activeSession.id)===String(sessionId))state.activeSession=null;
    if(saveState()===false){state=before;return false;}
    if(route?.page==='exam')navigate('dashboard');else render();return true;
  }
  /* NK_TIMED_RESUME_CARD_V1_END */
