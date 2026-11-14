  /* NK_NOT_STUDIED_V1_START
   * "Not studied yet" flag. During Practice or a timed test the learner can flag
   * a question from the session header. A flagged question stays out of
   * everything that measures learning: no FSRS card or skip mark, no attempt,
   * and it is removed from the saved test/practice result, so accuracy, test
   * stats, Insights, coverage and weak areas never see it.
   *
   * State: state.notStudied[qid] = {on:true, at, updatedAt} | {on:false, updatedAt}
   * (a cleared flag is a tombstone so cross_device_sync.js can merge per
   * question, newest edit wins, ties resolve to cleared).
   *
   * Lifecycle rule (one rule for Practice and timed tests): answering a question
   * whose flag was set BEFORE the current session started clears the flag and
   * the answer counts normally. A flag set DURING the session stays, even if the
   * question is answered, and that answer is withheld; unflagging in the same
   * session restores it. Practice answers are recorded at once, so flagging an
   * already answered Practice question withdraws this session's attempts with
   * the existing FSRS undo events (replayed, synced like any attempt).
   */
  const NK_NS_RESULT_WINDOW=10*60000,NK_NS_SESSION_ID=/^[A-Za-z0-9_.:-]{1,160}$/;
  function nkNsMap(){if(!state.notStudied||typeof state.notStudied!=='object'||Array.isArray(state.notStudied))state.notStudied={};return state.notStudied;}
  // Local only (never synced): what a flag set during a Practice session put aside,
  // so unflagging in that session gives back exactly what was there.
  function nkNsHeldMap(){if(!state.notStudiedHeld||typeof state.notStudiedHeld!=='object'||Array.isArray(state.notStudiedHeld))state.notStudiedHeld={};return state.notStudiedHeld;}
  function nkNsClean(raw){
    if(!raw||typeof raw!=='object')return null;
    const updatedAt=Math.max(0,Math.trunc(Number(raw.updatedAt)||0));if(!updatedAt)return null;
    if(raw.on!==true)return {on:false,updatedAt};
    const item={on:true,at:Math.max(0,Math.trunc(Number(raw.at)||updatedAt)),updatedAt};
    if(typeof raw.session==='string'&&NK_NS_SESSION_ID.test(raw.session))item.session=raw.session;
    return item;
  }
  function nkNsEntry(qid){return state.notStudied?.[String(qid)]||null;}
  function nkNsIsFlagged(qid){return nkNsEntry(qid)?.on===true;}
  function nkNsStamp(prev){return Math.max(Date.now(),Number(prev?.updatedAt||0)+1);}
  // A cleared flag that has synced leaves state.notStudied (so sync capture stops
  // walking it) and keeps only its time here, local only: the merge still refuses
  // anything not newer, exactly as the tombstone did.
  function nkNsClearedMap(){if(!state.notStudiedCleared||typeof state.notStudiedCleared!=='object'||Array.isArray(state.notStudiedCleared))state.notStudiedCleared={};return state.notStudiedCleared;}
  function nkNsKnown(qid){
    const id=String(qid),entry=nkNsClean(state.notStudied?.[id]);if(entry)return entry;
    const at=Math.trunc(Number(state.notStudiedCleared?.[id])||0);return at>0?{on:false,updatedAt:at}:null;
  }
  function nkNsSet(qid,on,session){
    const map=nkNsMap(),id=String(qid),prev=map[id]||nkNsKnown(id);if(Boolean(prev?.on)===Boolean(on))return false;
    const at=nkNsStamp(prev);
    map[id]=on?{on:true,at,updatedAt:at,...(session&&NK_NS_SESSION_ID.test(String(session))?{session:String(session)}:{})}:{on:false,updatedAt:at};
    if(state.notStudiedCleared)delete state.notStudiedCleared[id];return true;
  }
  // Called by cross_device_sync.js before each capture: a tombstone whose exact
  // payload this device already holds as synced (hash recorded, nothing waiting in
  // the outbox) moves to the compact cleared map.
  function nkNsPruneSynced(meta){
    if(!meta||typeof nkHash!=='function'||!state.notStudied)return 0;let pruned=0;
    Object.entries(state.notStudied).forEach(([id,raw])=>{
      const item=nkNsClean(raw);if(!item||item.on)return;
      const key=`notStudied/${id}`;
      if(meta.outbox?.[key]||meta.localHashes?.[key]!==nkHash({deleted:false,payload:JSON.stringify(item)}))return;
      nkNsClearedMap()[id]=item.updatedAt;delete state.notStudied[id];pruned++;
    });
    return pruned;
  }
  function nkNsFlaggedIds(ids){return (ids||[]).map(String).filter(nkNsIsFlagged);}
  function nkNsNewer(a,b){
    if(!b)return true;
    if(Number(a.updatedAt)!==Number(b.updatedAt))return Number(a.updatedAt)>Number(b.updatedAt);
    return a.on!==true&&b.on===true; // tie: cleared wins on every device
  }

  // While a flag made in session S is on, S's answers to that question are hidden
  // from FSRS and every statistic (they all read nkFsrsActiveAttempts). Nothing is
  // deleted, so unflagging in S shows them again exactly as they were.
  let nkNsBypass=false;
  const nkNsOriginalActive=nkFsrsActiveAttempts;
  function nkNsAllActive(qid){return nkNsOriginalActive(String(qid));}
  function nkNsHiddenSession(qid){const e=nkNsEntry(qid);return e?.on===true&&e.session?String(e.session):'';}
  nkFsrsActiveAttempts=function(qid){
    const list=nkNsOriginalActive.apply(this,arguments);if(nkNsBypass)return list;
    const hidden=nkNsHiddenSession(qid);return hidden?list.filter(a=>String(a?.sessionId||'')!==hidden):list;
  };
  function nkNsHiddenAttempts(qid,session){const sid=String(session||'');return sid?nkNsAllActive(qid).filter(a=>String(a?.sessionId||'')===sid):[];}
  function nkNsSignature(qid){return JSON.stringify(nkNsAllActive(qid).map(a=>[String(a.id),Number(a.rating||0)]));}
  function nkNsClone(value){return value==null?null:JSON.parse(JSON.stringify(value));}
  function nkNsSetReview(qid,review){if(review)state.reviews[qid]=nkNsClone(review);else delete state.reviews[qid];}
  function nkNsReplay(qid){if(typeof nkFsrsReplay==='function')nkFsrsReplay(String(qid),false);}
  // The card as it would be with the hidden answers counted.
  function nkNsFullReview(qid){
    const id=String(qid),held=nkNsHeldMap()[id];
    if(held&&held.sig===nkNsSignature(id)&&(held.review||!nkNsAllActive(id).length))return nkNsClone(held.review);
    const visible=nkNsClone(state.reviews[id]);nkNsBypass=true;
    try{nkNsReplay(id);return nkNsClone(state.reviews[id]);}finally{nkNsBypass=false;nkNsSetReview(id,visible);}
  }
  function nkNsMergeEntry(qid,incoming){
    const item=nkNsClean(incoming),id=String(qid||'');if(!item||!id)return false;
    const map=nkNsMap(),local=nkNsKnown(id);
    if(!nkNsNewer(item,local))return false;
    const before=nkNsHiddenSession(id);map[id]=item;if(state.notStudiedCleared)delete state.notStudiedCleared[id];
    if(before!==nkNsHiddenSession(id)&&nkNsAllActive(id).some(a=>a?.sessionId))nkNsReplay(id);
    return true;
  }
  // A flag set in an earlier session is being cleared: the answers it withheld are
  // withdrawn for good (FSRS undo events, synced like any attempt) so they never
  // come back, then the tombstone is written. The visible card does not change.
  function nkNsClearEarlier(qid){
    const id=String(qid),e=nkNsEntry(id);if(e?.on!==true)return false;
    const hidden=nkNsHiddenAttempts(id,e.session);
    if(hidden.length){
      state.attempts[id]=Array.isArray(state.attempts[id])?state.attempts[id]:[];
      let now=Date.now();
      hidden.forEach(a=>{now=Math.max(now+1,Number(a.at||0)+1);state.attempts[id].push({id:`undo_${now}_${Math.random().toString(16).slice(2)}`,isUndo:true,undoOf:a.id,at:now,reason:'not-studied',...(typeof NK_FSRS_VERSION!=='undefined'?{schedulerVersion:NK_FSRS_VERSION}:{})});});
    }
    const held=nkNsHeldMap();if(held[id]&&String(held[id].session)===String(e.session||''))delete held[id];
    return nkNsSet(id,false);
  }
  // Flags made outside the current session (an earlier session, another device's
  // session, or with no session) clear when the question is answered.
  function nkNsPredates(s,qid){
    const e=nkNsEntry(qid);if(e?.on!==true||!s)return false;
    if(e.session)return String(e.session)!==String(s.id);
    return Number(e.at||0)<Number(s.startedAt||0);
  }
  function nkNsQuestion(qid){const id=String(qid);return BY_ID?.[id]||(typeof nkFindStudyQuestion==='function'?nkFindStudyQuestion(id):null);}
  function nkNsIsCorrect(qid,selected){const q=nkNsQuestion(qid);return Boolean(q&&Number(q.correctOption)===Number(selected));}
  // Flag in this Practice session: put the card (with this session's answers) aside,
  // then show the card without them. A recall rating still waiting stays with the
  // session and commits as usual, hidden, so an unflag finds exactly what an
  // unflagged session would have recorded by then.
  function nkNsHold(s,qid){
    const id=String(qid);
    nkNsHeldMap()[id]={session:String(s.id),review:nkNsClone(state.reviews[id]),sig:nkNsSignature(id)};
  }
  // Unflag in the same session: exactly what was put aside comes back.
  function nkNsRelease(s,qid){
    const id=String(qid),map=nkNsHeldMap(),held=map[id];delete map[id];
    // A missing card cache (review null while answers exist) is rebuilt from the
    // answers, never written back as "no card".
    if(held&&String(held.session)===String(s.id)&&held.sig===nkNsSignature(id)&&(held.review||!nkFsrsActiveAttempts(id).length))nkNsSetReview(id,held.review);
    else nkNsReplay(id);
  }
  function nkNsIcon(size=20){return `<svg class="nk-ns-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5.5 21V3.5"/><path class="nk-ns-flag" d="M5.5 4h11.2l-2.4 4.2 2.4 4.3H5.5"/></svg>`;}
  function nkNsButton(q,s){
    const on=nkNsIsFlagged(q.id),label=on?'Not studied yet (flagged). Tap to remove the flag':'Flag as not studied yet';
    return `<button type="button" class="icon-btn nk-ns-toggle${on?' is-on':''}" aria-pressed="${on}" aria-label="${label}" title="${on?'Flagged: not studied yet':'Not studied yet'}" onclick="window.QB.nkToggleNotStudied(${esc(JSON.stringify(String(q.id)))},${esc(JSON.stringify(String(s.id)))})">${nkNsIcon(21)}</button>`;
  }
  // Answers paint in place without a full render, so the header button is patched too.
  function nkNsPatchButton(qid){
    const button=document.querySelector?.('.nk-ns-toggle');if(!button)return;
    const on=nkNsIsFlagged(qid);button.classList.toggle('is-on',on);button.setAttribute('aria-pressed',String(on));
    button.setAttribute('aria-label',on?'Not studied yet (flagged). Tap to remove the flag':'Flag as not studied yet');button.title=on?'Flagged: not studied yet':'Not studied yet';
  }
  // Time is up (per-question timer spent or expired, or the test clock ran out):
  // flagging then would only lift the score, so it is refused. Unflagging stays.
  function nkNsTimeUp(s,id){
    if(s?.mode!=='exam')return false;
    if(s.strictExpired?.[id])return true;
    if(s.timerMode==='per-question'&&typeof nkStrictSpent==='function'&&nkStrictSpent(s,id)>=60000)return true;
    return typeof nkTimedSessionExpired==='function'&&nkTimedSessionExpired(s);
  }
  function nkToggleNotStudied(questionId,sessionId){
    const s=state.activeSession,id=String(questionId||'');
    if(!s||!['practice','exam'].includes(s.mode)||String(s.id)!==String(sessionId)||String(s.questionIds?.[s.index])!==id)return false;
    const on=!nkNsIsFlagged(id);
    if(on&&nkNsTimeUp(s,id)){showToast('Time is up for this question, so it can’t be flagged.','bad');return false;}
    const apply=()=>{
      if(on){
        if(s.mode==='practice')nkNsHold(s,id);
        nkNsSet(id,true,s.id);
        if(nkNsHiddenAttempts(id,s.id).length)nkNsReplay(id);
      }else{
        const e=nkNsEntry(id);
        if(e?.session&&String(e.session)===String(s.id)){nkNsSet(id,false);if(s.mode==='practice')nkNsRelease(s,id);}
        else nkNsClearEarlier(id);
      }
      saveState();render();
      showToast(on?'Flagged as not studied. It stays out of your scores and reviews.':'Flag removed. This question counts again.');
      return true;
    };
    return typeof nkQuestionTransaction==='function'?nkQuestionTransaction(apply):apply();
  }

  // Recording an answer to a flagged question: a flag from outside this session
  // clears and the answer counts; a flag from this Practice session records the
  // answer hidden (the card it builds is kept aside for an unflag); anything else
  // (a timed test, no session) records nothing.
  const nkNsOriginalRecord=nkFsrsRecordAttempt;
  nkFsrsRecordAttempt=function(qid){
    const id=String(qid),e=nkNsEntry(id);
    if(e?.on!==true)return nkNsOriginalRecord.apply(this,arguments);
    const s=state.activeSession;
    if(s&&nkNsPredates(s,id)){nkNsClearEarlier(id);return nkNsOriginalRecord.apply(this,arguments);}
    if(s?.mode!=='practice'||String(e.session||'')!==String(s.id))return nkNsIsCorrect(id,arguments[1]);
    const visible=nkNsClone(state.reviews[id]),full=nkNsFullReview(id),held=nkNsHeldMap();
    nkNsBypass=true;let result;
    try{nkNsSetReview(id,full);result=nkNsOriginalRecord.apply(this,arguments);
      held[id]={session:String(s.id),review:nkNsClone(state.reviews[id]),sig:nkNsSignature(id)};
    }finally{nkNsBypass=false;nkNsSetReview(id,visible);}
    saveState();return result;
  };
  recordAttempt=nkFsrsRecordAttempt;

  // A flagged question shows no recall rating and takes none.
  const nkNsOriginalRatingMarkup=nkFsrsRatingMarkup;
  nkFsrsRatingMarkup=function(qid){return nkNsIsFlagged(qid)?'':nkNsOriginalRatingMarkup.apply(this,arguments);};
  const nkNsOriginalRate=nkRateCurrent;
  nkRateCurrent=function(rating,questionId){const s=state.activeSession,id=String(questionId??s?.questionIds?.[s?.index]??'');return id&&nkNsIsFlagged(id)?false:nkNsOriginalRate.apply(this,arguments);};
  // Clearing an earlier flag writes undo events, drops what was kept aside and
  // writes the tombstone before the guarded submit runs; if the submit is refused
  // (invalid option, already submitted, save failed) all three are put back.
  const nkNsOriginalSubmitPractice=submitPractice;
  submitPractice=function(){
    const s=state.activeSession,id=String(s?.questionIds?.[s?.index]??'');
    const live=Boolean(s?.mode==='practice'&&id&&!s.submitted?.[id]&&s.answers?.[id]);
    const prior=live&&nkNsPredates(s,id)?{flag:nkNsClone(nkNsEntry(id)),attempts:Array.isArray(state.attempts?.[id])?nkNsClone(state.attempts[id]):undefined,held:Object.prototype.hasOwnProperty.call(nkNsHeldMap(),id)?nkNsClone(nkNsHeldMap()[id]):undefined}:null;
    const cleared=Boolean(prior&&nkNsClearEarlier(id));
    const result=nkNsOriginalSubmitPractice.apply(this,arguments);
    const after=state.activeSession;
    if(cleared&&!(after?.submitted?.[id])){
      nkNsMap()[id]=prior.flag;
      if(prior.attempts===undefined){if(state.attempts)delete state.attempts[id];}else state.attempts[id]=prior.attempts;
      if(prior.held===undefined)delete nkNsHeldMap()[id];else nkNsHeldMap()[id]=prior.held;
      return result;
    }
    if(cleared){saveState();nkNsPatchButton(id);}
    return result;
  };
  // Timed-test answers are provisional until submit, so choosing an option never
  // clears an earlier flag; the record wrapper above clears it at submission.
  // Flagged questions never become submitted-as-skipped FSRS cards.
  const nkNsOriginalMarkSkipped=nkMarkSkippedFromSession;
  nkMarkSkippedFromSession=function(s){
    const ids=nkNsFlaggedIds([...(s?.sessionQuestionIds||[]),...(s?.questionIds||[])]),prior={};
    ids.forEach(id=>{prior[id]=state.fsrsReviewEligible?.[id];});
    const result=nkNsOriginalMarkSkipped.apply(this,arguments);
    ids.forEach(id=>{if(!state.fsrsReviewEligible)return;if(prior[id]===undefined)delete state.fsrsReviewEligible[id];else state.fsrsReviewEligible[id]=prior[id];});
    return result;
  };
  // A flagged question with no visible answer is not in Today's Review, its counts
  // or forecast, even if an earlier session left a skip mark. The mark itself is
  // kept, so unflagging puts the question back exactly as it was. A flagged
  // question with earlier answers keeps its card and stays due (R4).
  if(typeof nkFsrsEligibility==='function'){
    const nkNsOriginalEligibility=nkFsrsEligibility;
    nkFsrsEligibility=function(q){
      const id=String(q?.id||'');
      if(id&&nkNsIsFlagged(id)&&!nkFsrsActiveAttempts(id).length)return '';
      return nkNsOriginalEligibility.apply(this,arguments);
    };
  }

  // A just-saved result drops its flagged questions, so every analysis that reads
  // saved tests (score, accuracy, timing, CBT/topic analysis, Insights) skips them.
  // notStudiedIds marks a result as handled; older results are never rewritten.
  // It runs when the result is created (the first save of the ending session),
  // so no unclean copy is ever saved or queued for sync.
  function nkNsTestSession(t){
    if(t?.sessionId!=null&&String(t.sessionId))return String(t.sessionId);
    const m=/^(?:exam|practice)_(.+)$/.exec(String(t?.id||''));return m?m[1]:'';
  }
  function nkNsFromSession(id,sid){return Boolean(sid)&&nkNsAllActive(id).some(a=>String(a?.sessionId||'')===sid);}
  // This session's answers to it were withdrawn by a later session's flag clearing (R3).
  function nkNsWithdrawn(id,sid){
    if(!sid)return false;const list=Array.isArray(state.attempts?.[id])?state.attempts[id]:[];
    const undone=new Set(list.filter(a=>a?.isUndo&&a.reason==='not-studied'&&a.undoOf).map(a=>String(a.undoOf)));
    return list.some(a=>a&&!a.isUndo&&String(a.sessionId||'')===sid&&undone.has(String(a.id)))&&!nkNsFromSession(id,sid);
  }
  // Left out of this result: flagged by this session, or flagged elsewhere with no
  // counted answer from this session; or answered here and withdrawn later.
  function nkNsDropFromResult(id,sid){
    const e=nkNsEntry(id);
    if(e?.on===true)return !sid||String(e.session||'')===sid||!nkNsFromSession(id,sid);
    return nkNsWithdrawn(id,sid);
  }
  const NK_NS_SHELL_KEYS=['id','title','kind','sessionId','createdAt','autoSubmitted','originRoute','scheduledMockId','makeupFor'];
  function nkNsSanitizeTest(t,session){
    if(!t||!Array.isArray(t.questionIds)||Array.isArray(t.notStudiedIds))return false;
    const sid=String(session?.id||nkNsTestSession(t)||'');
    const flagged=new Set(t.questionIds.map(String).filter(id=>nkNsDropFromResult(id,sid)));t.notStudiedIds=[...flagged];
    if(!flagged.size)return true;
    // The full order is kept so result grids and Review Solutions can show the
    // flagged questions in place, marked "Not studied" and outside the score.
    t.allQuestionIds=t.questionIds.map(String);t.updatedAt=Math.max(Date.now(),Number(t.createdAt||0)+1);
    const keep=id=>!flagged.has(String(id));
    if(!t.questionIds.some(keep)){
      // Every question flagged: no result, but a hidden shell stays (never deleted),
      // so a copy queued earlier can never come back through sync (the shell is
      // newer and wins) and a scheduled mock or make-up still reads as taken.
      const shell={},all=t.allQuestionIds,updatedAt=t.updatedAt;NK_NS_SHELL_KEYS.forEach(key=>{if(t[key]!==undefined)shell[key]=t[key];});
      Object.keys(t).forEach(key=>delete t[key]);
      Object.assign(t,shell,{noResult:true,notStudiedIds:[...flagged],allQuestionIds:all,questionIds:[],answers:{},questionTimes:{},correct:0,incorrect:0,attempted:0,unattempted:0,total:0,totalTimeMs:0,updatedAt});
      return true;
    }
    t.questionIds=t.questionIds.filter(keep);
    ['answers','questionTimes','markedForReview','expired'].forEach(key=>{if(t[key]&&typeof t[key]==='object')t[key]=Object.fromEntries(Object.entries(t[key]).filter(([id])=>keep(id)));});
    let correct=0,incorrect=0,attempted=0;
    Object.entries(t.answers||{}).forEach(([id,selected])=>{if(!selected)return;attempted++;if(nkNsIsCorrect(id,selected))correct++;else incorrect++;});
    Object.assign(t,{correct,incorrect,attempted,total:t.questionIds.length,unattempted:Math.max(0,t.questionIds.length-attempted)});
    if(t.kind==='practice'||t.timerMode==='per-question')t.totalTimeMs=Object.values(t.questionTimes||{}).reduce((sum,v)=>sum+Number(v||0),0);
    return true;
  }
  function nkNsFresh(t){return Boolean(t)&&!Array.isArray(t.notStudiedIds)&&Date.now()-Number(t.createdAt||0)<NK_NS_RESULT_WINDOW;}
  // The session being submitted or finished; its result is cleaned on its first save.
  let nkNsEnding=null;
  function nkNsCleanEnding(){
    const s=nkNsEnding,sid=String(s?.id||'');if(!sid||!Array.isArray(state.tests))return false;
    let changed=false;
    state.tests.forEach(t=>{if(nkNsFresh(t)&&(String(t.sessionId||'')===sid||String(t.id)===`exam_${sid}`||String(t.id)===`practice_${sid}`)&&nkNsSanitizeTest(t,s))changed=true;});
    return changed;
  }
  function nkNsEndingCall(session,fn,self,args){const prev=nkNsEnding;nkNsEnding=session||prev;try{return fn.apply(self,args);}finally{nkNsEnding=prev;}}
  const nkNsOriginalSave=saveState;
  saveState=function(){if(nkNsEnding)nkNsCleanEnding();return nkNsOriginalSave.apply(this,arguments);};
  if(typeof submitExam==='function'){
    const nkNsOriginalSubmitExam=submitExam;
    submitExam=function(){const s=state.activeSession;return nkNsEndingCall(s?.mode==='exam'?s:null,nkNsOriginalSubmitExam,this,arguments);};
  }
  // Practice ends: answers still hidden by a flag from this session are withdrawn
  // for good (undo events), so app versions that predate the flag never count them
  // either. Nothing visible changes. What was put aside for an unflag is dropped.
  function nkNsSettleSession(s){
    if(!s?.id)return false;let changed=false;const held=nkNsHeldMap();
    [...new Set([...(s.sessionQuestionIds||[]),...(s.questionIds||[])].map(String))].forEach(id=>{
      const e=nkNsEntry(id);
      if(held[id]&&String(held[id].session)===String(s.id)){delete held[id];changed=true;}
      if(e?.on!==true||String(e.session||'')!==String(s.id))return;
      const hidden=nkNsHiddenAttempts(id,s.id);if(!hidden.length)return;
      state.attempts[id]=Array.isArray(state.attempts[id])?state.attempts[id]:[];let now=Date.now();
      hidden.forEach(a=>{now=Math.max(now+1,Number(a.at||0)+1);state.attempts[id].push({id:`undo_${now}_${Math.random().toString(16).slice(2)}`,isUndo:true,undoOf:a.id,at:now,reason:'not-studied',...(typeof NK_FSRS_VERSION!=='undefined'?{schedulerVersion:NK_FSRS_VERSION}:{})});});
      changed=true;
    });
    return changed;
  }
  // What was kept aside for an unflag only matters while its session can still
  // run here (the live session or a paused/active checkpoint); drop the rest.
  function nkNsPruneHeld(){
    const held=nkNsHeldMap(),ids=Object.keys(held);if(!ids.length||typeof nkPracticeCheckpoints!=='function')return false;
    const live=new Set(nkPracticeCheckpoints(false).map(cp=>String(cp.sessionId)));
    const s=state.activeSession;if(s?.id&&!(typeof nkPracticeTerminal==='function'&&nkPracticeTerminal(s)))live.add(String(s.id));
    let changed=false;ids.forEach(id=>{if(!live.has(String(held[id]?.session||''))){delete held[id];changed=true;}});
    return changed;
  }
  // Settles only once the finish really ended the session: a failed save restores
  // the state (a copy of the session, same id), so the session is compared by id.
  const nkNsOriginalFinishPractice=finishPracticeSession;
  finishPracticeSession=function(){
    const s=state.activeSession,result=nkNsEndingCall(s?.mode==='practice'?s:null,nkNsOriginalFinishPractice,this,arguments);
    if(s?.mode==='practice'&&result!==false&&String(state.activeSession?.id??'')!==String(s.id)){
      const settled=nkNsSettleSession(s),pruned=nkNsPruneHeld();if(settled||pruned)saveState();
    }
    return result;
  };
  // Discarding a paused Practice settles it like a finish: its hidden answers are
  // withdrawn for good and nothing stays kept aside.
  if(typeof nkDiscardNormalPractice==='function'){
    const nkNsOriginalDiscard=nkDiscardNormalPractice;
    nkDiscardNormalPractice=function(){
      const open=typeof nkPracticeCheckpoints==='function'?nkPracticeCheckpoints(false):[],result=nkNsOriginalDiscard.apply(this,arguments);
      if(result===false||typeof nkPracticeFindCheckpoint!=='function')return result;
      let changed=false;
      open.forEach(cp=>{if(String(nkPracticeFindCheckpoint(cp.sessionId)?.lifecycle||'')==='discarded'&&nkNsSettleSession({id:String(cp.sessionId),sessionQuestionIds:cp.sessionQuestionIds||[]}))changed=true;});
      if(nkNsPruneHeld())changed=true;
      if(changed)saveState();
      return result;
    };
  }
  // A Practice that cannot be paused (Today's Review, wrong answers, bookmarks) is
  // abandoned when another session replaces it: settle it the same way.
  if(typeof startSession==='function'){
    const nkNsOriginalStartSession=startSession;
    startSession=function(){
      const prev=state.activeSession,result=nkNsOriginalStartSession.apply(this,arguments),now=state.activeSession;
      const abandoned=result!==false&&prev?.mode==='practice'&&!prev.studyModuleId&&now!==prev&&String(now?.id??'')!==String(prev.id)&&
        typeof nkPracticeResumeEligible==='function'&&!nkPracticeResumeEligible(prev)&&!(typeof nkPracticeTerminal==='function'&&nkPracticeTerminal(prev));
      if(abandoned){const settled=nkNsSettleSession(prev),pruned=nkNsPruneHeld();if(settled||pruned)saveState();}
      return result;
    };
  }
  // Opening a result: one that is still unclean is cleaned now (paths that save a
  // result outside submit/finish); a hidden shell has nothing to show.
  const nkNsOriginalNavigate=navigate;
  navigate=function(page,id){
    if(page==='result'&&id!=null){
      const tests=Array.isArray(state.tests)?state.tests:[],t=tests.find(x=>String(x.id)===String(id));
      if(nkNsFresh(t)&&nkNsSanitizeTest(t))saveState();
      if(t?.noResult){
        showToast('Every question was flagged as not studied, so no result was saved.');
        return nkNsOriginalNavigate.call(this,t.originRoute||(t.kind==='practice'?'topics':'tests'));
      }
    }
    return nkNsOriginalNavigate.apply(this,arguments);
  };

  // Session header: the flag sits beside the bookmark (Practice and timed tests only).
  const nkNsOriginalHeader=nkSessionHeader;
  nkSessionHeader=function(q,s,mode){
    const out=nkNsOriginalHeader.apply(this,arguments);
    if(!q||!s||!['practice','exam'].includes(mode)||s.mode!==mode)return out;
    return out.replace('<div class="q-actions">','<div class="q-actions">'+nkNsButton(q,s));
  };
  // Outcome looks a flagged cell must not wear: it is neither answered, right,
  // wrong nor skipped, it is "not studied" (the topic grid's corner flag).
  const NK_NS_OUTCOME_CLASSES=['answered','unanswered','correct','incorrect','is-correct','is-wrong','is-skipped','skipped','is-answered','is-incorrect','is-omitted','is-timeup'];
  function nkNsLegendMark(dotClass){return `<span class="nk-ns-legend"><i class="${dotClass} is-ns" aria-hidden="true">${nkNsIcon(10)}</i>Not studied</span>`;}
  function nkNsDecorateGrid(root,selector,s,flagged){
    if(!root||!s)return 0;let count=0;const isFlagged=flagged||(id=>nkNsIsFlagged(id));
    root.querySelectorAll(selector).forEach((cell,i)=>{
      const id=s.questionIds?.[i];if(id==null||!isFlagged(String(id)))return;count++;
      NK_NS_OUTCOME_CLASSES.forEach(name=>cell.classList.remove(name));
      cell.classList.add('is-ns');cell.setAttribute('aria-label',`Question ${i+1}, not studied${cell.classList.contains('active')?', current':''}`);
      const small=cell.querySelector('small');if(small)small.textContent='Not studied';
      if(!cell.querySelector('.nk-ns-icon'))cell.insertAdjacentHTML('beforeend',`<span class="nk-ns-corner">${nkNsIcon(10)}</span>`);
    });
    return count;
  }
  // The Practice review legend counts outcomes; drop the ones only flagged cells had.
  function nkNsTidyLegend(root,cellSelector,legend){
    if(!legend)return;
    [['correct','is-correct'],['wrong','is-wrong'],['skipped','is-skipped']].forEach(([dot,cls])=>{
      const item=legend.querySelector?.(`.nk-review-dot.${dot}`)?.parentElement;
      if(item&&!root.querySelector(`${cellSelector}.${cls}`))item.remove();
    });
  }
  const nkNsOriginalSessionReview=openSessionReview;
  openSessionReview=function(){
    const result=nkNsOriginalSessionReview.apply(this,arguments),s=state.activeSession;
    if(!['practice','exam'].includes(s?.mode))return result;
    const root=document.getElementById('nk-session-review');
    if(nkNsDecorateGrid(root,'.nk-session-review-q',s)){
      const legend=root.querySelector('.nk-session-review-legend');
      if(s.mode==='practice')nkNsTidyLegend(root,'.nk-session-review-q',legend);
      legend?.insertAdjacentHTML('beforeend',nkNsLegendMark('nk-review-dot'));
    }
    return result;
  };
  // Review Solutions shows the result's own not-studied list, not today's flags.
  function nkNsReviewFlagged(s){
    const t=(state.tests||[]).find(x=>String(x.id)===String(s?.sourceTestId));
    const ids=new Set((Array.isArray(s?.notStudiedIds)?s.notStudiedIds:t?.notStudiedIds||[]).map(String));
    return id=>ids.has(String(id));
  }
  const nkNsOriginalNavigator=openQuestionNavigator;
  openQuestionNavigator=function(){
    const result=nkNsOriginalNavigator.apply(this,arguments),s=state.activeSession;
    if(!['practice','exam','review'].includes(s?.mode))return result;
    const root=document.getElementById('qb-question-navigator');
    if(nkNsDecorateGrid(root,'.qb-nav-q',s,s.mode==='review'?nkNsReviewFlagged(s):null))root.querySelector('.qb-nav-legend')?.insertAdjacentHTML('beforeend',nkNsLegendMark('qb-legend-dot'));
    return result;
  };

  // Results: the flagged questions sit in their place in every result grid and in
  // Review Solutions, marked "Not studied" (corner flag), never counted as skipped.
  function nkNsResultOrder(t){
    const flagged=(t?.notStudiedIds||[]).map(String);if(!flagged.length)return null;
    if(Array.isArray(t.allQuestionIds)&&flagged.every(id=>t.allQuestionIds.map(String).includes(id)))return t.allQuestionIds.map(String);
    const context=(t.practiceContext?.questionIds||[]).map(String),kept=(t.questionIds||[]).map(String);
    if(context.length&&[...flagged,...kept].every(id=>context.includes(id)))return context.filter(id=>flagged.includes(id)||kept.includes(id));
    return [...kept,...flagged];
  }
  if(typeof nkResultStrip==='function'){
    const nkNsOriginalStrip=nkResultStrip;
    nkResultStrip=function(t){
      const order=nkNsResultOrder(t);if(!order)return nkNsOriginalStrip.apply(this,arguments);
      const flagged=new Set(t.notStudiedIds.map(String));
      let out=nkNsOriginalStrip.call(this,{...t,questionIds:order});
      out=out.replace(/<button type="button" class="is-[a-z]+"( style="[^"]*") aria-label="Question (\d+): [^"]*"/g,(all,style,n)=>flagged.has(order[Number(n)-1])?`<button type="button" class="is-ns"${style} aria-label="Question ${n}: Not studied, not scored"`:all);
      out=out.replace(/(<button type="button" class="is-ns"[^>]*>)(<\/button>)/g,`$1${nkNsIcon(10)}$2`);
      // A timed test or mock also shows the score with them counted, so leaving
      // questions out never hides what the raw score was.
      const raw=t.kind!=='practice'&&order.length?` · ${Math.round(Number(t.correct||0)/order.length*100)}% counting them`:'';
      return out.replace(/(<div class="nk-rs-strip[^"]*">[\s\S]*<\/div>)(<\/section>)$/,`$1<p class="nk-rs-ns-note">${nkNsIcon(12)}<span>${fmtNum(flagged.size)} not studied · left out of the score${raw}</span></p>$2`);
    };
  }
  if(typeof resultPage==='function'){
    const nkNsOriginalResultPage=resultPage;
    resultPage=function(testId){
      const t=(state.tests||[]).find(x=>String(x.id)===String(testId));
      if(t?.noResult&&typeof testsPage==='function')return testsPage();
      const out=nkNsOriginalResultPage.apply(this,arguments),order=nkNsResultOrder(t);
      if(!order)return out;
      const flagged=new Set(t.notStudiedIds.map(String));
      const rows=order.map((id,i)=>{
        const q=typeof nkBankQuestionById==='function'?nkBankQuestionById(id):nkNsQuestion(id),sel=t.answers?.[id],correct=q&&Number(q.correctOption)===Number(sel);
        const status=flagged.has(id)?'<i class="nk-status is-ns">'+nkNsIcon(11)+'Not studied</i>':`<i class="nk-status ${sel?(correct?'is-correct':'is-wrong'):'is-unattempted'}">${sel?(correct?'Correct':'Incorrect'):t.expired?.[id]?'Time up':'Omitted'}</i>`;
        return `<div${flagged.has(id)?' class="is-ns"':''}><span class="nk-question-index">${i+1}</span><span><strong>${q?esc(String(q.question||'').slice(0,125)):esc('Saved question unavailable')}</strong><small>${status}${q?esc(q.chapter||''):''}</small></span></div>`;
      }).join('');
      return out.replace(/(<details class="nk-na-card nk-na-answers"><summary>Every answer<\/summary><div class="nk-result-questions">)[\s\S]*?(<\/div><\/details>)/,(all,a,b)=>a+rows+b);
    };
  }
  const nkNsOriginalBuildReview=buildReviewSession;
  buildReviewSession=function(t){
    const s=nkNsOriginalBuildReview.apply(this,arguments),order=nkNsResultOrder(t);
    if(!order||!s)return s;
    const current=String(s.questionIds?.[s.index]??'');
    s.questionIds=order;s.index=Math.max(0,order.indexOf(current));s.notStudiedIds=t.notStudiedIds.map(String);
    s.notStudiedIds.forEach(id=>{if(s.submitted)s.submitted[id]=false;});
    return s;
  };

  // Topics: a flag badge with the count on each topic row; the topic page marks
  // flagged cells and offers "Practice flagged (N)".
  function nkNsTopicIds(cid){return typeof chapterQuestions==='function'?chapterQuestions(cid).filter(q=>nkNsIsFlagged(q.id)).map(q=>String(q.id)):[];}
  function nkNsAnyFlags(){return Object.values(state.notStudied||{}).some(e=>e?.on===true);}
  function nkNsReEscape(value){return String(value).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
  const nkNsOriginalTopics=topics;
  topics=function(){
    let out=nkNsOriginalTopics.apply(this,arguments);if(!nkNsAnyFlags())return out;
    (CHAPTERS||[]).forEach(c=>{
      const n=nkNsTopicIds(c.id).length;if(!n)return;
      const pattern=new RegExp(`(onclick="window\\.QB\\.openChapter\\('${nkNsReEscape(c.id)}'\\)"[\\s\\S]*?<span class="nk-topic-copy">[\\s\\S]*?<small>[\\s\\S]*?)(</small>)`);
      out=out.replace(pattern,`$1<span class="nk-ns-badge" aria-label="${n} flagged not studied">${nkNsIcon(12)}${n}</span>$2`);
    });
    return out;
  };
  const nkNsOriginalChapterPage=chapterPage;
  chapterPage=function(cid){
    let out=nkNsOriginalChapterPage.apply(this,arguments);
    const c=typeof CHAPTER_BY_ID!=='undefined'?CHAPTER_BY_ID[String(cid)]:null;if(!c||!nkNsAnyFlags())return out;
    const ids=new Set(nkNsTopicIds(c.id));if(!ids.size)return out;
    out=out.replace(/<button class="(nk-library-row nk-topic-cell[^"]*)"([^>]*?) aria-label="([^"]*)"([^>]*?) onclick="window\.QB\.practiceOne\('([^']*)'\)">([^<]*)<\/button>/g,(all,cls,a,label,b,qid,text)=>ids.has(String(qid))?`<button class="${cls} is-ns"${a} aria-label="${label}, flagged not studied"${b} onclick="window.QB.practiceOne('${qid}')">${text}<span class="nk-ns-corner">${nkNsIcon(10)}</span></button>`:all);
    const item=`<li class="is-ns"><b>${fmtNum(ids.size)}</b> not studied</li>`;
    out=out.includes('<ul class="nk-topic-legend">')?out.replace(/(<ul class="nk-topic-legend">[\s\S]*?)(<\/ul>)/,`$1${item}$2`):out.replace(/(<div class="nk-topic-map">[\s\S]*?<\/div>)/,`$1<ul class="nk-topic-legend">${item}</ul>`);
    out=out.replace(/(<div class="nk-topic-options">[\s\S]*?)(<\/div><\/div><\/section>)/,`$1<button class="nk-topic-option nk-topic-ns" onclick="window.QB.nkPracticeNotStudied('${esc(String(c.id))}')">${nkNsIcon(18)}<span>Practice flagged</span><small>${fmtNum(ids.size)}</small>${navIcon('chevron',16)}</button>$2`);
    return out;
  };
  function nkPracticeNotStudied(cid){
    const c=CHAPTER_BY_ID[String(cid)],ids=nkNsTopicIds(cid);
    if(!ids.length){showToast('No flagged questions in this topic.','bad');return false;}
    return startSession(ids,'practice',`${c?.title||'Topic'} · Not studied`);
  }
  /* NK_NOT_STUDIED_V1_END */
