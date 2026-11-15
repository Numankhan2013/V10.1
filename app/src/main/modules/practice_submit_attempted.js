  /* NK_PRACTICE_SUBMIT_ATTEMPTED_V1_START */
  // "Submit attempted" (owner request, 2026-11-15): end a normal topic Practice at
  // the last question you answered, without having to finish the whole set.
  //   - The result covers questions 1..last answered. A question left blank BEFORE
  //     that point is "Skipped" (scored like today's skips: not wrong, and FSRS
  //     treats it exactly as the existing skip rule does).
  //   - Questions AFTER the last answer are left out completely: not in the result,
  //     not in FSRS, not marked skipped, their time not counted.
  //   - The topic page then offers "Continue where you left off" (the questions that
  //     were left out) beside "Practice entire topic". Every other topic option is
  //     unchanged.
  // Only normal Practice (nkPracticeResumeEligible): due reviews, Today's Review,
  // mistakes, bookmarks, modules and timed tests are unchanged.
  function nkSaAnswered(s,id){id=String(id);return Boolean(s?.answers?.[id])&&Boolean(s?.submitted?.[id]);}
  function nkSaFlagged(id){return typeof nkNsIsFlagged==='function'&&Boolean(nkNsIsFlagged(String(id)));}
  function nkSaPlan(s){
    if(!s||s.mode!=='practice'||typeof nkPracticeResumeEligible!=='function'||!nkPracticeResumeEligible(s))return null;
    const ids=nkPracticeSessionIds(s);let last=-1;
    ids.forEach((id,i)=>{if(nkSaAnswered(s,id))last=i;});
    const cut=last<0?[]:ids.slice(0,last+1),rest=ids.slice(last+1);
    const skipped=cut.filter(id=>!nkSaAnswered(s,id)&&!nkSaFlagged(id));
    return {ids,last,cut,rest,skipped};
  }
  function nkSubmitAttemptedPractice(){
    const s=state.activeSession,plan=nkSaPlan(s);if(!plan)return false;
    if(!plan.cut.length){showToast('Answer a question first, then submit what you attempted.','bad');return false;}
    if(!plan.rest.length)return nkSubmitPracticeSession();
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));
    try{
      // Time on the current question is booked before the set is cut.
      if(typeof savePracticeElapsed==='function')savePracticeElapsed();
      const keep=new Set(plan.cut.map(String));
      const prune=obj=>{if(obj&&typeof obj==='object')Object.keys(obj).forEach(k=>{if(!keep.has(String(k)))delete obj[k];});};
      prune(s.answers);prune(s.submitted);prune(s.questionTimes);prune(s.pendingRating);
      // A choice picked but never checked is not an answer.
      plan.cut.forEach(id=>{if(s.answers?.[id]&&!s.submitted?.[id])delete s.answers[id];});
      s.questionIds=[...plan.cut];s.sessionQuestionIds=[...plan.cut];s.index=plan.cut.length-1;s.questionEnteredAt=Date.now();
      if(s.practiceContext)s.practiceContext={...s.practiceContext,questionIds:[...plan.cut]};
      s.partialSubmit={total:plan.ids.length,remainingIds:[...plan.rest],skippedIds:[...plan.skipped],at:Date.now()};
    }catch(error){state=before;showToast('Could not submit. Try again.','bad');return false;}
    const result=finishPracticeSession();
    if(result===false){
      // A refused finish leaves the session whole, as it was before the cut.
      if(state.activeSession&&String(state.activeSession.id)===String(s.id)&&state.activeSession.partialSubmit){state=before;saveState();}
      return false;
    }
    return result;
  }

  // ── The session sheet: a third action under Pause / Submit ──
  const nkSaOriginalReview=openSessionReview;
  openSessionReview=function(){
    const s=state.activeSession,result=nkSaOriginalReview.apply(this,arguments),plan=nkSaPlan(s);
    if(!plan||!plan.cut.length||!plan.rest.length||typeof document==='undefined')return result;
    const actions=document.querySelector('#nk-session-review .nk-session-review-actions');
    if(actions&&!actions.querySelector('.nk-practice-submit-attempted')){
      const range=plan.cut.length===1?'Question 1':`Questions 1–${plan.cut.length}`;
      const note=`${range}${plan.skipped.length?` · ${plan.skipped.length} skipped`:''} · ${plan.rest.length} left for later`;
      actions.insertAdjacentHTML('beforeend',`<button type="button" class="nk-practice-submit-attempted" onclick="window.QB.nkSubmitAttemptedPractice()" aria-label="Submit attempted: ${esc(note)}"><span>Submit attempted</span><small>${esc(note)}</small></button>`);
      actions.classList.add('has-submit-attempted');
    }
    return result;
  };

  // ── Topic page: continue where you left off ──
  function nkSaLeftOff(topicId){
    const tests=(state.tests||[]).filter(t=>t?.kind==='practice'&&String(t.practiceContext?.topicId||'')===String(topicId)&&(t.partial||(t.questionIds||[]).length>1))
      .sort((a,b)=>Number(b.createdAt||0)-Number(a.createdAt||0));
    const t=tests[0];if(!t?.partial)return null;
    const rest=(t.practiceContext?.remainingIds||t.remainingIds||[]).map(String).filter(id=>typeof nkPracticeResumeQuestion==='function'?nkPracticeResumeQuestion(id):BY_ID?.[id]);
    return rest.length?{test:t,ids:rest}:null;
  }
  function nkContinueLeftOff(topicId){
    const offer=nkSaLeftOff(topicId),c=CHAPTER_BY_ID?.[String(topicId)];if(!offer||!c)return false;
    const ctx=offer.test.practiceContext||{};
    return nkPracticeOpenContext({subject:String(ctx.subject||activeSubject),bank:String(ctx.bank||activeBank||''),topicId:String(topicId),title:String(ctx.title||c.title||'Topic'),questionIds:[...offer.ids]},true);
  }
  const nkSaOriginalChapter=chapterPage;
  chapterPage=function(cid){
    const out=nkSaOriginalChapter.apply(this,arguments);
    if(typeof out!=='string'||out.includes('class="nk-topic-resume"')||!out.includes('<div class="nk-chapter-actions">'))return out;
    const offer=nkSaLeftOff(cid);if(!offer)return out;
    const order=(typeof chapterQuestions==='function'?chapterQuestions(cid):[]).map(q=>String(q.id)),total=order.length;
    const at=order.indexOf(offer.ids[0]),from=at>=0?at+1:0;
    const line=`${from?`From question ${fmtNum(from)}${total?` of ${fmtNum(total)}`:''} · `:''}${fmtNum(offer.ids.length)} left`;
    const btn=`<button class="nk-topic-resume nk-topic-leftoff" onclick="window.QB.nkContinueLeftOff(${esc(JSON.stringify(String(cid)))})"><span><strong>Continue where you left off</strong><small>${line}</small></span>${navIcon('chevron',18)}</button>`;
    let html=out.replace('<div class="nk-chapter-actions">',btn+'<div class="nk-chapter-actions">');
    // The main button now reads as the other choice: the whole topic again.
    html=html.replace(/(<div class="nk-chapter-actions"><button class="is-primary"[^>]*><strong>)[^<]*(<\/strong><small>)[^<]*(<\/small>)/,(all,a,b,c2)=>`${a}Practice entire topic${b}${fmtNum(total)} question${total===1?'':'s'}${c2}`);
    return html;
  };

  // ── Result page: a partial Practice calls its blanks "Skipped" and says what was left ──
  const nkSaOriginalResult=resultPage;
  resultPage=function(testId){
    const out=nkSaOriginalResult.apply(this,arguments),t=(state.tests||[]).find(x=>String(x.id)===String(testId));
    if(!t?.partial||typeof out!=='string')return out;
    const rest=(t.practiceContext?.remainingIds||[]).length,total=Number(t.sessionTotal||0)||((t.questionIds||[]).length+rest);
    const note=`<p class="nk-sa-result-note"><strong>Questions 1–${fmtNum((t.questionIds||[]).length)} of ${fmtNum(total)}</strong><span>${fmtNum(rest)} left for later · not counted</span></p>`;
    let html=out.replace(/\bOmitted\b/g,'Skipped').replace(/(\d+) omitted"/g,'$1 skipped"').replace(/\bNot answered\b/g,'Skipped').replace(/(\d+) not answered\b/g,'$1 skipped');
    const anchor=html.indexOf('<section class="nk-na-card nk-na-summary');
    return anchor>=0?html.slice(0,anchor)+note+html.slice(anchor):html;
  };
  /* NK_PRACTICE_SUBMIT_ATTEMPTED_V1_END */
