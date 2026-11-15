  /* NK_REVIEW_LEARNING_QUEUE_V1_START
   * Due-review sessions only (revisionQueueKind 'due', revision_session.js).
   *
   * 1. Learning rounds, Anki style. A rating that leaves the card in learning or
   *    relearning (FSRS state 1/3: Again from a wrong answer, Hard on a learning
   *    card) puts the question in session.learningQueue with the card's FSRS due
   *    time. Round 1 is the whole set. When the last card of a round is done (every
   *    card in it answered or flagged), the queued cards due within the 20 min
   *    learn-ahead become the next round, session.roundPass = {round, ids}: only
   *    those cards, in due order, fresh and unanswered (the previous answer, time
   *    and rating move to session.roundHistory[qid]). The header counter, progress
   *    bar and the session sheet count only that round ("1 / 4", "Round 2"), and
   *    Next / Previous / the sheet move only inside it. A card that comes due again
   *    in round N goes to round N+1; when none is left the review ends by itself and
   *    Revision opens (no result page; Finish early does the same). Cards due later than the learn-ahead are never
   *    pulled in by themselves: a "due in N min" line offers Study now or Finish.
   *    The question list never changes (questionIds and sessionQuestionIds keep their
   *    membership, so the checkpoint membershipHash, the abandon/Back guard and sync
   *    stay as they were). Every round records a normal FSRS attempt (source
   *    fsrs-review; round 2+ carries learningRound). Setting
   *    fsrsPreferences.learningInSession: 'end' (default; the older 'due' value
   *    means the same) or 'off' (one pass).
   * 2. Advance after rating (fsrsPreferences.advanceAfterRating, default on): the
   *    first Hard/Good/Easy on an answer saves it, holds the pressed state for
   *    ~250 ms, then goes Next. Wrong answers never move on; changing a saved rating
   *    only saves. The timer fires only for the same session, question and round.
   * Finishing a due review saves no result (revision_session.js): every round is an
   * FSRS attempt, round 2+ tagged learningRound, and Insights read those.
   * Rules: docs/FSRS.md § "Learning cards in a due review".
   */
  const NK_RLQ_PRESS_MS=250;
  let nkRlqAdvance=null;
  function nkRlqDueSession(s=state.activeSession){
    return Boolean(s)&&s.mode==='practice'&&typeof nkRevisionSessionKind==='function'&&nkRevisionSessionKind(s)==='due'&&!(typeof nkPracticeTerminal==='function'&&nkPracticeTerminal(s));
  }
  function nkRlqMode(){return nkFsrsPreferences().learningInSession==='off'?'off':'end';}
  function nkRlqAdvanceOn(){return nkFsrsPreferences().advanceAfterRating!==false;}
  function nkRlqRounds(s,qid){return Array.isArray(s?.roundHistory?.[String(qid)])?s.roundHistory[String(qid)]:[];}
  function nkRlqRound(s,qid){return nkRlqRounds(s,qid).length+1;}
  function nkRlqFlagged(qid){return typeof nkNsIsFlagged==='function'&&nkNsIsFlagged(String(qid));}
  function nkRlqQueue(s){if(!s.learningQueue||typeof s.learningQueue!=='object'||Array.isArray(s.learningQueue))s.learningQueue={};return s.learningQueue;}
  function nkRlqMember(s,qid){return (s?.questionIds||[]).map(String).includes(String(qid));}
  // The live round 2+ (null in round 1). Only member ids count; a damaged pass is dropped.
  function nkRlqPass(s=state.activeSession){
    const p=s?.roundPass;if(!p||typeof p!=='object'||!Array.isArray(p.ids))return null;
    const ids=p.ids.map(String).filter(id=>nkRlqMember(s,id));
    if(!ids.length||!(Number(p.round)>=2)){delete s.roundPass;return null;}
    if(ids.length!==p.ids.length)p.ids=ids;
    return p;
  }
  function nkRlqPassRound(s){return nkRlqPass(s)?Math.trunc(Number(s.roundPass.round)):1;}
  // The cards of the live round: the pass, or the whole set in round 1.
  function nkRlqRoundIds(s){const p=nkRlqPass(s);return p?p.ids.map(String):(s?.questionIds||[]).map(String);}
  function nkRlqRow(s,qid){return (s?.questionIds||[]).map(String).indexOf(String(qid));}
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
  // Queued cards due by `limit`, earliest first (ties in set order); flagged, foreign or
  // reopened-and-unanswered entries are dropped.
  function nkRlqQueued(s,limit=Infinity){
    const queue=nkRlqQueue(s),rows=[];
    Object.keys(queue).forEach(id=>{
      if(nkRlqFlagged(id)||!nkRlqMember(s,id)||!s.submitted?.[id]){delete queue[id];return;}
      const due=Number(queue[id]?.due||0);if(due<=limit)rows.push({id,due,row:nkRlqRow(s,id)});
    });
    return rows.sort((a,b)=>a.due-b.due||a.row-b.row);
  }
  // A card still to do in the live round (not answered and not flagged).
  function nkRlqOpenCards(s){return nkRlqRoundIds(s).filter(id=>!s.submitted?.[id]&&!nkRlqFlagged(id));}
  // This session's saved attempt for the live round (answer, outcome and rating to archive).
  function nkRlqRoundAttempt(s,id){
    const since=Number(nkRlqRounds(s,id).at(-1)?.reopenedAt||0);
    return nkFsrsActiveAttempts(id).filter(a=>String(a.sessionId||'')===String(s.id)&&Number(a.reviewedAt||a.at||0)>=since).at(-1)||null;
  }
  // Archive the card's live round and clear it, so it is answered fresh.
  function nkRlqArchive(s,id){
    const attempt=nkRlqRoundAttempt(s,id),history=s.roundHistory&&typeof s.roundHistory==='object'&&!Array.isArray(s.roundHistory)?s.roundHistory:(s.roundHistory={}),list=Array.isArray(history[id])?history[id]:(history[id]=[]);
    list.push({round:list.length+1,answer:s.answers?.[id]==null?null:Number(s.answers[id]),submitted:Boolean(s.submitted?.[id]),timeMs:Number(s.questionTimes?.[id]||0),correct:attempt?Boolean(attempt.correct):null,rating:attempt?nkFsrsRating(attempt):null,attemptId:attempt?String(attempt.id):null,reopenedAt:Date.now()});
    if(s.answers)delete s.answers[id];if(s.submitted)delete s.submitted[id];if(s.questionTimes)delete s.questionTimes[id];if(s.pendingRating)delete s.pendingRating[id];
    delete nkRlqQueue(s)[id];
  }
  // Open the next round with exactly these cards (due order), on its first card.
  function nkRlqStartRound(s,ids){
    if(!ids.length)return false;
    if(typeof savePracticeElapsed==='function')savePracticeElapsed();
    const round=nkRlqPassRound(s)+1;
    ids.forEach(id=>nkRlqArchive(s,id));
    s.roundPass={round,ids:[...ids]};delete s.learningReturnIndex;
    s.index=nkRlqRow(s,ids[0]);s.questionEnteredAt=Date.now();
    saveState();render();
    showToast(`Round ${round} · ${fmtNum(ids.length)} card${ids.length===1?'':'s'} to relearn`);
    return true;
  }
  function nkRlqCancelAdvance(){if(nkRlqAdvance){try{clearTimeout(nkRlqAdvance.timer);}catch(_){}nkRlqAdvance=null;}}
  function nkRlqCloseWait(){document.getElementById('nk-rlq-wait')?.remove();}
  function nkRlqMinutes(ms){return Math.max(1,Math.ceil(ms/60000));}
  function nkRlqCards(n){return `${fmtNum(n)} card${n===1?'':'s'}`;}
  // What waits after this round: cards ready now (next round) or only later ones.
  function nkRlqWaitInfo(s){
    const all=nkRlqQueued(s);if(!all.length)return null;
    const ready=all.filter(r=>r.due<=Date.now()+NK_FSRS_LEARN_AHEAD),next=nkRlqPassRound(s)+1;
    if(ready.length)return {ready:true,count:all.length,copy:`${nkRlqCards(all.length)} to relearn`,action:`Start Round ${next}`};
    return {ready:false,count:all.length,copy:`${fmtNum(all.length)} learning card${all.length===1?'':'s'} due in ${nkRlqMinutes(all[0].due-Date.now())} min`,action:'Study now'};
  }
  // The round is done and only cards due later than the learn-ahead remain.
  function nkRlqShowWait(s){
    nkRlqCloseWait();const info=nkRlqWaitInfo(s);if(!info)return false;
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-rlq-wait" id="nk-rlq-wait"><section class="modal card" role="dialog" aria-modal="true" aria-labelledby="nk-rlq-wait-title"><h2 id="nk-rlq-wait-title">${esc(info.copy)}</h2><p>You have reached the end of this review. A card you are relearning comes back when its step is due; Finish ends the review and leaves it in Revision.</p><div class="nk-rlq-wait-actions"><button type="button" class="primary-btn" onclick="window.QB.nkRlqStudyNow()">${esc(info.action)}</button><button type="button" class="ghost-btn" onclick="window.QB.nkRlqFinish()">Finish</button></div></section></div>`);
    document.querySelector?.('#nk-rlq-wait button')?.focus?.();return true;
  }
  // End of a round: the next round, the wait line, or (nothing left) the review ends and
  // Revision opens, like Anki. A round with an unanswered card opens the session sheet.
  function nkRlqEndRound(s){
    if(typeof savePracticeElapsed==='function')savePracticeElapsed();
    if(!nkRlqOpenCards(s).length){
      if(nkRlqMode()!=='off'){
        const ready=nkRlqQueued(s,Date.now()+NK_FSRS_LEARN_AHEAD);
        if(ready.length)return nkRlqStartRound(s,ready.map(r=>r.id));
        if(nkRlqQueued(s).length){saveState();return nkRlqShowWait(s);}
      }
      return finishPracticeSession();
    }
    saveState();openSessionReview();return true;
  }
  // Study now / Start Round N: every waiting card, ready or not, as the next round.
  function nkRlqStudyNow(){
    nkRlqCloseWait();const s=state.activeSession;if(!nkRlqDueSession(s))return false;
    const ids=nkRlqQueued(s).map(r=>r.id);if(!ids.length)return false;
    const run=()=>{document.getElementById('nk-session-review')?.remove();return nkRlqStartRound(s,ids);};
    return typeof nkQuestionTransaction==='function'?nkQuestionTransaction(run):run();
  }
  // "Finish" on the wait line ends the review (the later cards keep their FSRS due time).
  function nkRlqFinish(){nkRlqCloseWait();if(!nkRlqDueSession())return false;return finishPracticeSession();}

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

  // Navigation. Round 1 is the ordinary set; its last Next ends the round. In round 2+
  // Next / Previous / jumps stay inside the round's cards.
  const nkRlqOriginalNext=nextQ,nkRlqOriginalPrev=prevQ,nkRlqOriginalGo=goIndex;
  function nkRlqNext(){
    const s=state.activeSession;
    if(!nkRlqDueSession(s))return nkRlqOriginalNext.apply(this,arguments);
    const qid=s.questionIds?.[s.index];
    if(qid!=null){if(s.pendingRating?.[qid])nkFsrsCommitPending(qid,3);nkRlqRefresh(qid,s);}
    delete s.learningReturnIndex;
    const pass=nkRlqPass(s);
    if(pass){
      const p=pass.ids.indexOf(String(qid));
      if(p<0)return nkRlqOriginalGo.call(this,nkRlqRow(s,pass.ids[0]));
      if(p<pass.ids.length-1)return nkRlqOriginalGo.call(this,nkRlqRow(s,pass.ids[p+1]));
      return nkRlqEndRound(s);
    }
    if(Number(s.index)<s.questionIds.length-1)return nkRlqOriginalNext.apply(this,arguments);
    return nkRlqEndRound(s);
  }
  nextQ=function(){nkRlqCancelAdvance();nkRlqCloseWait();return typeof nkQuestionTransaction==='function'?nkQuestionTransaction(()=>nkRlqNext.apply(this,arguments)):nkRlqNext.apply(this,arguments);};
  prevQ=function(){
    nkRlqCancelAdvance();const s=state.activeSession,pass=nkRlqDueSession(s)?nkRlqPass(s):null;
    if(!pass)return nkRlqOriginalPrev.apply(this,arguments);
    const p=pass.ids.indexOf(String(s.questionIds?.[s.index]));
    return p>0?nkRlqOriginalGo.call(this,nkRlqRow(s,pass.ids[p-1])):false;
  };
  // A jump (the session sheet, the navigator) can only reach a card of the live round.
  goIndex=function(i){
    nkRlqCancelAdvance();const s=state.activeSession,pass=nkRlqDueSession(s)?nkRlqPass(s):null;
    if(pass&&!pass.ids.includes(String(s.questionIds?.[Number(i)])))return false;
    return nkRlqOriginalGo.apply(this,arguments);
  };
  // Previous is disabled on the first card of a round.
  const nkRlqOriginalActionBar=practiceActionBar;
  practiceActionBar=function(){
    const out=nkRlqOriginalActionBar.apply(this,arguments),s=state.activeSession,pass=nkRlqDueSession(s)?nkRlqPass(s):null;
    if(!pass)return out;const first=pass.ids.indexOf(String(s.questionIds?.[s.index]))<=0;
    return out.replace(/(<button class="ghost-btn" onclick="window\.QB\.prevQ\(\)")\s*(?:disabled)?/,`$1${first?' disabled':''}`);
  };
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

  // Finish: each question counts once, by its round 1 answer (round 2+ are relearning
  // repeats, kept in FSRS history); the question's time is every round's time.
  function nkRlqSettleRounds(s){
    if(!s?.roundHistory||typeof s.roundHistory!=='object')return;
    s.answers=s.answers||{};s.submitted=s.submitted||{};s.questionTimes=s.questionTimes||{};
    Object.keys(s.roundHistory).forEach(id=>{
      const list=nkRlqRounds(s,id);if(!list.length)return;
      const first=list[0];
      if(first.submitted&&first.answer!=null){s.answers[id]=first.answer;s.submitted[id]=true;}
      s.questionTimes[id]=Number(s.questionTimes[id]||0)+list.reduce((sum,r)=>sum+Number(r.timeMs||0),0);
    });
    s.learningQueue={};delete s.learningReturnIndex;delete s.roundPass;
  }
  const nkRlqOriginalFinish=finishPracticeSession;
  finishPracticeSession=function(){
    nkRlqCancelAdvance();nkRlqCloseWait();const s=state.activeSession;
    if(!nkRlqDueSession(s)||!s.roundHistory)return nkRlqOriginalFinish.apply(this,arguments);
    // The live round's pending rating is saved first, from its own answer.
    const run=()=>{if(typeof savePracticeElapsed==='function')savePracticeElapsed();if(typeof nkFsrsRecoverPending==='function')nkFsrsRecoverPending();nkRlqSettleRounds(s);return nkRlqOriginalFinish.apply(this,arguments);};
    return typeof nkQuestionTransaction==='function'?nkQuestionTransaction(run):run();
  };
  nkFinishRevisionSession=function(){return finishPracticeSession();};

  // Header: round 2+ counts only its own cards; a small "Round N" badge sits inside the
  // counter, so the back button, flag, bookmark and grid keep their places.
  function nkRlqBadge(round){return `<span class="nk-rlq-round">Round ${round}</span>`;}
  const nkRlqOriginalHeader=nkSessionHeader;
  nkSessionHeader=function(q,s,mode){
    const out=nkRlqOriginalHeader.apply(this,arguments);
    if(!q||mode!=='practice'||!nkRlqDueSession(s))return out;const pass=nkRlqPass(s);if(!pass)return out;
    const p=pass.ids.indexOf(String(q.id));if(p<0)return out;
    const total=pass.ids.length,position=p+1,progress=Math.max(0,Math.min(100,Math.round(position/total*100)));
    return out.replace(/<div class="nk-session-count">[\s\S]*?<\/div>/,`<div class="nk-session-count has-round" aria-label="Round ${pass.round}, question ${position} of ${total}"><strong>${position}</strong> / ${total}${nkRlqBadge(pass.round)}</div>`)
      .replace(/aria-valuenow="\d+"><i style="width:\d+%"><\/i><span>\d+%<\/span>/,`aria-valuenow="${progress}"><i style="width:${progress}%"></i><span>${progress}%</span>`);
  };
  // The session sheet (also the grid button): in round 2+ only the round's cards, numbered
  // in round order; the line above the actions says what waits after this round.
  const nkRlqOriginalReview=openSessionReview;
  openSessionReview=function(){
    const s=state.activeSession,result=nkRlqOriginalReview.apply(this,arguments);
    if(!nkRlqDueSession(s))return result;
    const box=document.getElementById('nk-session-review');if(!box)return result;
    const pass=nkRlqPass(s),grid=box.querySelector?.('.nk-session-review-grid');
    if(pass&&grid){
      const cells=[...(grid.querySelectorAll?.('.nk-session-review-q')||[])],byId=new Map();
      cells.forEach((cell,i)=>{const id=s.questionIds[i];if(id!=null)byId.set(String(id),cell);cell.remove();});
      pass.ids.forEach((id,k)=>{
        const cell=byId.get(id);if(!cell)return;
        const number=cell.querySelector?.('span');if(number)number.textContent=String(k+1);
        cell.setAttribute?.('aria-label',String(cell.getAttribute?.('aria-label')||`Question ${k+1}`).replace(/^Question \d+/,`Question ${k+1}`));
        grid.appendChild(cell);
      });
      // Legend entries only for outcomes still on the grid (round 1 outcomes are not shown).
      const legend=box.querySelector?.('.nk-session-review-legend');
      [['correct','is-correct'],['wrong','is-wrong'],['skipped','is-skipped']].forEach(([dot,cls])=>{const item=legend?.querySelector?.(`.nk-review-dot.${dot}`)?.parentElement;if(item&&!grid.querySelector?.(`.nk-session-review-q.${cls}`))item.remove();});
      if(!grid.querySelector?.('.nk-session-review-q.is-ns'))legend?.querySelector?.('.nk-ns-legend')?.remove();
      const answered=pass.ids.filter(id=>s.submitted?.[id]).length,left=pass.ids.length-answered;
      const strong=box.querySelector?.('.nk-session-review-summary strong'),span=box.querySelector?.('.nk-session-review-summary span');
      if(strong)strong.textContent=left?`${fmtNum(answered)} answered · ${fmtNum(left)} unanswered`:`${fmtNum(answered)} answered · all cards covered`;
      if(span)span.textContent=`Round ${pass.round} · ${nkRlqCards(pass.ids.length)}`;
      const sub=box.querySelector?.('.nk-session-review-head p');if(sub)sub.textContent=`Round ${pass.round} holds only the cards you are relearning. Tap one to return to it, or finish: every answer is already saved to FSRS.`;
    }
    // The next round starts only once this one is done; before that the line just says what waits.
    const info=nkRlqMode()!=='off'?nkRlqWaitInfo(s):null,actions=box.querySelector?.('.nk-session-review-actions'),open=nkRlqOpenCards(s).length;
    if(info&&actions)actions.insertAdjacentHTML?.('afterbegin',open?`<p class="nk-rlq-waiting">${esc(info.copy)} after this round</p>`:`<p class="nk-rlq-waiting">${esc(info.copy)} <button type="button" class="nk-text-link" onclick="window.QB.nkRlqStudyNow()">${esc(info.action)}</button></p>`);
    return result;
  };
  /* NK_REVIEW_LEARNING_QUEUE_V1_END */
