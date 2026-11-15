  /* NK_REVIEW_LEARNING_QUEUE_V1_START
   * Due-review sessions only (revisionQueueKind 'due', revision_session.js).
   *
   * 1. In-session learning queue, Anki style. A rating that leaves the card in
   *    learning or relearning (FSRS state 1/3: Again from a wrong answer, Hard on a
   *    learning card) puts the question in session.learningQueue with the card's
   *    FSRS due time. The question list never changes (questionIds and
   *    sessionQuestionIds keep their membership, so the checkpoint membershipHash,
   *    the abandon/Back guard and sync stay as they were): the card reopens in its
   *    own row as a new round. The previous round's answer/submitted/time moves to
   *    session.roundHistory[qid] and the live answer clears, so it is answered
   *    again; the header and the session grid show "Round N". Every round records
   *    a normal FSRS attempt (source fsrs-review; round 2+ carries learningRound).
   *    Setting fsrsPreferences.learningInSession: 'due' (default) shows a queued
   *    card on the next Next once it is due; 'end' after the rest of the set;
   *    'off' keeps one pass. At the end of the set, cards due within the 20 min
   *    learn-ahead show at once; later ones get a "due in N min" choice.
   * 2. Advance after rating (fsrsPreferences.advanceAfterRating, default on): the
   *    first Hard/Good/Easy on an answer saves it, holds the pressed state for
   *    ~250 ms, then goes Next (a due learning card first; the end-of-session sheet
   *    after the last card). Wrong answers never move on; changing a saved rating
   *    only saves. The timer fires only for the same session, question and round.
   * The saved result counts each question once, by its latest answered round.
   * Rules: docs/FSRS.md § "Learning cards in a due review".
   */
  const NK_RLQ_PRESS_MS=250;
  let nkRlqAdvance=null;
  function nkRlqDueSession(s=state.activeSession){
    return Boolean(s)&&s.mode==='practice'&&typeof nkRevisionSessionKind==='function'&&nkRevisionSessionKind(s)==='due'&&!(typeof nkPracticeTerminal==='function'&&nkPracticeTerminal(s));
  }
  function nkRlqMode(){const v=nkFsrsPreferences().learningInSession;return ['due','end','off'].includes(v)?v:'due';}
  function nkRlqAdvanceOn(){return nkFsrsPreferences().advanceAfterRating!==false;}
  function nkRlqRounds(s,qid){return Array.isArray(s?.roundHistory?.[String(qid)])?s.roundHistory[String(qid)]:[];}
  function nkRlqRound(s,qid){return nkRlqRounds(s,qid).length+1;}
  function nkRlqFlagged(qid){return typeof nkNsIsFlagged==='function'&&nkNsIsFlagged(String(qid));}
  function nkRlqQueue(s){if(!s.learningQueue||typeof s.learningQueue!=='object'||Array.isArray(s.learningQueue))s.learningQueue={};return s.learningQueue;}
  function nkRlqMember(s,qid){return (s?.questionIds||[]).map(String).includes(String(qid));}
  // The queue entry follows the card: present while this round is answered (its
  // rating saved) and the card is learning/relearning; gone otherwise (graduated,
  // flagged, rating not saved yet, mode Off, or the round reopened).
  function nkRlqRefresh(qid,s=state.activeSession){
    if(!nkRlqDueSession(s)||qid==null)return false;
    const id=String(qid),queue=nkRlqQueue(s),before=JSON.stringify(queue[id]||null),review=state.reviews?.[id];
    const learning=review?.schemaVersion===2&&[1,3].includes(Number(review.state));
    const answered=Boolean(s.submitted?.[id])&&!s.pendingRating?.[id];
    if(answered&&learning&&nkRlqMode()!=='off'&&!nkRlqFlagged(id)&&nkRlqMember(s,id))queue[id]={due:Number(review.due||review.nextReviewAt||Date.now()),round:nkRlqRound(s,id)};
    else delete queue[id];
    return before!==JSON.stringify(queue[id]||null);
  }
  // The earliest queued card due by `limit` (flagged or foreign entries are dropped).
  function nkRlqNextLearning(s,limit){
    let best=null;const queue=nkRlqQueue(s);
    Object.keys(queue).forEach(id=>{
      if(nkRlqFlagged(id)||!nkRlqMember(s,id)||!s.submitted?.[id]){delete queue[id];return;}
      const due=Number(queue[id]?.due||0);
      if(due<=limit&&(!best||due<best.due||(due===best.due&&id<best.id)))best={id,due};
    });
    return best;
  }
  function nkRlqWaiting(s){return Object.keys(nkRlqQueue(s)).filter(id=>!nkRlqFlagged(id)&&nkRlqMember(s,id)&&s.submitted?.[id]);}
  // This session's saved attempt for the live round (answer, outcome and rating to archive).
  function nkRlqRoundAttempt(s,id){
    const since=Number(nkRlqRounds(s,id).at(-1)?.reopenedAt||0);
    return nkFsrsActiveAttempts(id).filter(a=>String(a.sessionId||'')===String(s.id)&&Number(a.reviewedAt||a.at||0)>=since).at(-1)||null;
  }
  // Reopen a queued card as its next round in its own row.
  function nkRlqOpenRound(s,id){
    const index=s.questionIds.map(String).indexOf(String(id));if(index<0)return false;
    const attempt=nkRlqRoundAttempt(s,id),history=s.roundHistory&&typeof s.roundHistory==='object'&&!Array.isArray(s.roundHistory)?s.roundHistory:(s.roundHistory={}),list=Array.isArray(history[id])?history[id]:(history[id]=[]);
    list.push({round:list.length+1,answer:s.answers?.[id]==null?null:Number(s.answers[id]),submitted:Boolean(s.submitted?.[id]),timeMs:Number(s.questionTimes?.[id]||0),correct:attempt?Boolean(attempt.correct):null,rating:attempt?nkFsrsRating(attempt):null,attemptId:attempt?String(attempt.id):null,reopenedAt:Date.now()});
    if(s.answers)delete s.answers[id];if(s.submitted)delete s.submitted[id];if(s.questionTimes)delete s.questionTimes[id];if(s.pendingRating)delete s.pendingRating[id];
    delete nkRlqQueue(s)[id];
    s.index=index;s.questionEnteredAt=Date.now();return true;
  }
  function nkRlqCancelAdvance(){if(nkRlqAdvance){try{clearTimeout(nkRlqAdvance.timer);}catch(_){}nkRlqAdvance=null;}}
  function nkRlqCloseWait(){document.getElementById('nk-rlq-wait')?.remove();}
  function nkRlqMinutes(ms){return Math.max(1,Math.ceil(ms/60000));}
  function nkRlqWaitCopy(s){
    const waiting=nkRlqWaiting(s),next=nkRlqNextLearning(s,Infinity);if(!next)return '';
    return `${fmtNum(waiting.length)} learning card${waiting.length===1?'':'s'} due in ${nkRlqMinutes(next.due-Date.now())} min`;
  }
  // The set is done and only cards due later than the learn-ahead remain.
  function nkRlqShowWait(s){
    nkRlqCloseWait();const copy=nkRlqWaitCopy(s);if(!copy)return false;
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-rlq-wait" id="nk-rlq-wait"><section class="modal card" role="dialog" aria-modal="true" aria-labelledby="nk-rlq-wait-title"><h2 id="nk-rlq-wait-title">${esc(copy)}</h2><p>You have reached the end of this review. A card you are relearning comes back when its step is due.</p><div class="nk-rlq-wait-actions"><button type="button" class="primary-btn" onclick="window.QB.nkRlqStudyNow()">Study now</button><button type="button" class="ghost-btn" onclick="window.QB.nkRlqFinish()">Finish</button></div></section></div>`);
    document.querySelector?.('#nk-rlq-wait button')?.focus?.();return true;
  }
  function nkRlqGoLearning(s,id){
    if(typeof savePracticeElapsed==='function')savePracticeElapsed();
    if(!Number.isInteger(s.learningReturnIndex))s.learningReturnIndex=Number(s.index)||0;
    nkRlqOpenRound(s,id);saveState();render();return true;
  }
  function nkRlqStudyNow(){
    nkRlqCloseWait();const s=state.activeSession;if(!nkRlqDueSession(s))return false;
    const next=nkRlqNextLearning(s,Infinity);if(!next)return false;
    if(typeof nkQuestionTransaction==='function')return nkQuestionTransaction(()=>nkRlqGoLearning(s,next.id));
    return nkRlqGoLearning(s,next.id);
  }
  // "Finish" on the wait line opens the existing end-of-session sheet (Pause / Finish session).
  function nkRlqFinish(){nkRlqCloseWait();if(!nkRlqDueSession())return false;openSessionReview();return true;}

  // Ratings: the queue follows every committed or revised rating.
  const nkRlqOriginalCommit=nkFsrsCommitPending;
  nkFsrsCommitPending=function(qid){
    const result=nkRlqOriginalCommit.apply(this,arguments);
    if(result&&nkRlqDueSession()&&nkRlqRefresh(qid))saveState();
    return result;
  };
  const nkRlqOriginalSubmit=submitPractice;
  submitPractice=function(){
    const s=state.activeSession,qid=s?.questionIds?.[s?.index];
    const result=nkRlqOriginalSubmit.apply(this,arguments);
    const after=state.activeSession;if(qid!=null&&nkRlqDueSession(after)&&after.submitted?.[qid]&&nkRlqRefresh(qid,after))saveState();
    return result;
  };
  const nkRlqOriginalRate=nkRateCurrent;
  nkRateCurrent=function(rating,questionId,sessionId){
    const s=state.activeSession,qid=String(s?.questionIds?.[s?.index]??'');
    const due=nkRlqDueSession(s)&&Boolean(qid);
    // A double tap while the advance is pending never saves a second rating.
    if(due&&nkRlqAdvance&&nkRlqAdvance.sessionId===String(s.id)&&nkRlqAdvance.qid===qid)return false;
    const first=due&&Boolean(s.pendingRating?.[qid])&&!nkFsrsSessionRating(qid)&&(questionId==null||String(questionId)===qid)&&(sessionId==null||String(sessionId)===String(s.id));
    const action=()=>{const out=nkRlqOriginalRate.apply(this,[rating,questionId,sessionId]);if(out!==false&&due&&nkRlqRefresh(qid))saveState();return out;};
    const result=typeof nkQuestionTransaction==='function'?nkQuestionTransaction(action,()=>typeof nkPatchRecall==='function'&&nkPatchRecall()):action();
    if(result!==false&&first&&nkRlqAdvanceOn()){const now=state.activeSession;if(now&&String(now.id)===String(s.id)&&now.submitted?.[qid])nkRlqScheduleAdvance(now,qid);}
    return result;
  };
  // The advance runs only if nothing moved in the meantime.
  function nkRlqStillCurrent(token){
    const s=state.activeSession;
    return nkRlqDueSession(s)&&String(s.id)===token.sessionId&&!['paused','suspended'].includes(String(s.lifecycle||''))&&Number(s.index)===token.index
      &&String(s.questionIds?.[s.index])===token.qid&&nkRlqRound(s,token.qid)===token.round&&Boolean(s.submitted?.[token.qid])&&!s.pendingRating?.[token.qid]
      &&!nkRlqFlagged(token.qid)&&(typeof route==='undefined'||route.page==='practice')
      &&!document.getElementById('nk-session-review')&&!document.getElementById('nk-abandon-confirm')&&!document.getElementById('nk-rlq-wait');
  }
  function nkRlqScheduleAdvance(s,qid){
    nkRlqCancelAdvance();
    const token={sessionId:String(s.id),qid:String(qid),index:Number(s.index),round:nkRlqRound(s,qid)};
    try{const dock=document.querySelector?.('.nk-fsrs-rating');dock?.classList?.add('is-advancing');dock?.querySelector?.('button[aria-pressed="true"]')?.classList?.add('is-pressed');}catch(_){}
    token.timer=setTimeout(()=>{
      if(nkRlqAdvance!==token)return;nkRlqAdvance=null;
      if(nkRlqStillCurrent(token))nextQ();
    },NK_RLQ_PRESS_MS);
    nkRlqAdvance=token;return token;
  }

  // Navigation: Next shows a due learning card ahead of the rest of the set.
  const nkRlqOriginalNext=nextQ;
  function nkRlqNext(){
    const s=state.activeSession;
    if(!nkRlqDueSession(s))return nkRlqOriginalNext.apply(this,arguments);
    const qid=s.questionIds?.[s.index];
    if(qid!=null){if(s.pendingRating?.[qid])nkFsrsCommitPending(qid,3);nkRlqRefresh(qid,s);}
    const mode=nkRlqMode(),last=s.questionIds.length-1;
    if(mode==='off'){delete s.learningReturnIndex;return nkRlqOriginalNext.apply(this,arguments);}
    const base=Number.isInteger(s.learningReturnIndex)?Math.min(last,s.learningReturnIndex):Number(s.index)||0,now=Date.now();
    const atEnd=base>=last,limit=atEnd?now+NK_FSRS_LEARN_AHEAD:mode==='due'?now:-Infinity;
    const due=nkRlqNextLearning(s,limit);
    if(due){if(!Number.isInteger(s.learningReturnIndex))s.learningReturnIndex=base;return nkRlqGoLearning(s,due.id);}
    if(!atEnd){
      if(base!==s.index){if(typeof savePracticeElapsed==='function')savePracticeElapsed();s.index=base;s.questionEnteredAt=Date.now();}
      delete s.learningReturnIndex;return nkRlqOriginalNext.apply(this,arguments);
    }
    if(nkRlqNextLearning(s,Infinity)){if(typeof savePracticeElapsed==='function')savePracticeElapsed();saveState();return nkRlqShowWait(s);}
    delete s.learningReturnIndex;
    if(s.index!==last){if(typeof savePracticeElapsed==='function')savePracticeElapsed();saveState();openSessionReview();return true;}
    return nkRlqOriginalNext.apply(this,arguments);
  }
  nextQ=function(){nkRlqCancelAdvance();nkRlqCloseWait();return typeof nkQuestionTransaction==='function'?nkQuestionTransaction(()=>nkRlqNext.apply(this,arguments)):nkRlqNext.apply(this,arguments);};
  // Moving by hand leaves any learning interlude: Next then continues from where you are.
  const nkRlqOriginalPrev=prevQ;
  prevQ=function(){nkRlqCancelAdvance();const s=state.activeSession;if(nkRlqDueSession(s))delete s.learningReturnIndex;return nkRlqOriginalPrev.apply(this,arguments);};
  const nkRlqOriginalGo=goIndex;
  goIndex=function(){nkRlqCancelAdvance();const s=state.activeSession;if(nkRlqDueSession(s))delete s.learningReturnIndex;return nkRlqOriginalGo.apply(this,arguments);};
  if(typeof nkToggleNotStudied==='function'){
    const nkRlqOriginalToggle=nkToggleNotStudied;
    nkToggleNotStudied=function(questionId){
      nkRlqCancelAdvance();const result=nkRlqOriginalToggle.apply(this,arguments),s=state.activeSession;
      if(result!==false&&nkRlqDueSession(s)&&nkRlqRefresh(questionId,s))saveState();
      return result;
    };
  }
  const nkRlqOriginalPause=nkPausePractice;
  nkPausePractice=function(){nkRlqCancelAdvance();nkRlqCloseWait();return nkRlqOriginalPause.apply(this,arguments);};
  if(typeof nkAbandonSession==='function'){const nkRlqOriginalAbandon=nkAbandonSession;nkAbandonSession=function(){nkRlqCancelAdvance();nkRlqCloseWait();return nkRlqOriginalAbandon.apply(this,arguments);};}

  // Finish: each question counts once, by its latest answered round. A round
  // reopened but left unanswered gives way to the round before it; the time of
  // every round is the question's time in the result.
  function nkRlqSettleRounds(s){
    if(!s?.roundHistory||typeof s.roundHistory!=='object')return;
    s.answers=s.answers||{};s.submitted=s.submitted||{};s.questionTimes=s.questionTimes||{};
    Object.keys(s.roundHistory).forEach(id=>{
      const list=nkRlqRounds(s,id);if(!list.length)return;
      if(!s.submitted[id]){
        const back=[...list].reverse().find(r=>r.submitted&&r.answer!=null);
        if(back){s.answers[id]=back.answer;s.submitted[id]=true;}
      }
      s.questionTimes[id]=Number(s.questionTimes[id]||0)+list.reduce((sum,r)=>sum+Number(r.timeMs||0),0);
    });
    s.learningQueue={};delete s.learningReturnIndex;
  }
  const nkRlqOriginalFinish=finishPracticeSession;
  finishPracticeSession=function(){
    nkRlqCancelAdvance();nkRlqCloseWait();const s=state.activeSession;
    if(!nkRlqDueSession(s)||!s.roundHistory)return nkRlqOriginalFinish.apply(this,arguments);
    const run=()=>{if(typeof savePracticeElapsed==='function')savePracticeElapsed();nkRlqSettleRounds(s);return nkRlqOriginalFinish.apply(this,arguments);};
    return typeof nkQuestionTransaction==='function'?nkQuestionTransaction(run):run();
  };
  nkFinishRevisionSession=function(){return finishPracticeSession();};

  // Round badge in the question header and the session grid; the sheet says what is still waiting.
  function nkRlqBadge(round){return `<span class="nk-rlq-round" aria-label="Round ${round}">Round ${round}</span>`;}
  const nkRlqOriginalHeader=nkSessionHeader;
  nkSessionHeader=function(q,s){
    const out=nkRlqOriginalHeader.apply(this,arguments);
    if(!q||!nkRlqDueSession(s))return out;const round=nkRlqRound(s,q.id);if(round<2)return out;
    return out.replace(/(<div class="nk-session-count">[\s\S]*?<\/div>)/,`$1${nkRlqBadge(round)}`);
  };
  const nkRlqOriginalReview=openSessionReview;
  openSessionReview=function(){
    const s=state.activeSession,result=nkRlqOriginalReview.apply(this,arguments);
    if(!nkRlqDueSession(s))return result;
    const box=document.getElementById('nk-session-review');if(!box)return result;
    (box.querySelectorAll?.('.nk-session-review-q')||[]).forEach((cell,i)=>{
      const id=s.questionIds[i];if(id==null)return;const round=nkRlqRound(s,id);if(round<2)return;
      cell.classList?.add('has-round');cell.insertAdjacentHTML?.('beforeend',`<em class="nk-rlq-round-dot" aria-hidden="true">R${round}</em>`);
      cell.setAttribute?.('aria-label',`${cell.getAttribute?.('aria-label')||`Question ${i+1}`}, round ${round}`);
    });
    const copy=nkRlqMode()!=='off'?nkRlqWaitCopy(s):'',actions=box.querySelector?.('.nk-session-review-actions');
    if(copy&&actions)actions.insertAdjacentHTML?.('afterbegin',`<p class="nk-rlq-waiting">${esc(copy)} <button type="button" class="nk-text-link" onclick="window.QB.nkRlqStudyNow()">Study now</button></p>`);
    return result;
  };
  /* NK_REVIEW_LEARNING_QUEUE_V1_END */
