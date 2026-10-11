  /* NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START */
  // Normal Practice has exactly one end-of-session surface:
  // the existing review grid. Pause/Submit belong there, never on the question footer.
  const nkPracticeSingleGridActionBar=practiceActionBar;
  practiceActionBar=function(){
    const s=state.activeSession;
    if(nkPracticeResumeEligible(s)){
      return nkPracticeResumeOriginalActionBar.apply(this,arguments);
    }
    return nkPracticeSingleGridActionBar.apply(this,arguments);
  };

  // The header grid icon and the last-question boundary both converge on the same
  // review sheet for normal Practice. Keep the legacy navigator for other modes.
  const nkPracticeSingleGridNavigator=openQuestionNavigator;
  openQuestionNavigator=function(){
    const s=state.activeSession;
    if(nkPracticeResumeEligible(s)){
      document.getElementById('qb-question-navigator')?.remove();
      return openSessionReview();
    }
    return nkPracticeSingleGridNavigator.apply(this,arguments);
  };

  // Reduce the final Practice review sheet to only the two session-level decisions.
  // The sheet's X close control and tappable question cells remain owned by the base UI.
  const nkPracticeSingleGridReview=openSessionReview;
  openSessionReview=function(){
    const s=state.activeSession;
    const result=nkPracticeSingleGridReview.apply(this,arguments);
    if(!nkPracticeResumeEligible(s))return result;
    document.getElementById('qb-question-navigator')?.remove();
    const box=document.getElementById('nk-session-review');
    if(!box)return result;
    box.classList.add('nk-practice-final-review');
    // Practice gives feedback per question, so the grid can show the outcome of each one:
    // correct, wrong, or skipped (opened and left blank), in the topic map's colours.
    let shown={correct:0,wrong:0,skipped:0};
    (box.querySelectorAll?.('.nk-session-review-q')||[]).forEach((cell,i)=>{
      const id=s.questionIds[i];if(id==null)return;
      const last=(state.attempts?.[id]||[]).at(-1);
      const outcome=s.answers?.[id]&&s.submitted?.[id]&&last?(last.correct?'correct':'wrong'):(!s.answers?.[id]&&i!==s.index&&Number(s.questionTimes?.[id]||0)>0?'skipped':'');
      if(!outcome)return;
      shown[outcome]++;cell.classList.add('is-'+outcome);
      cell.setAttribute('aria-label',`Question ${i+1} ${outcome}`);
    });
    const legend=box.querySelector('.nk-session-review-legend');
    if(legend&&(shown.correct||shown.wrong||shown.skipped)){
      legend.innerHTML=[['correct','Correct'],['wrong','Wrong'],['skipped','Skipped'],['unanswered','Not attempted'],['active','Current']]
        .filter(([key])=>key==='active'||key==='unanswered'||shown[key]).map(([key,label])=>`<span><i class="nk-review-dot ${key}"></i>${label}</span>`).join('');
    }
    const actions=box.querySelector('.nk-session-review-actions');
    if(actions){
      actions.innerHTML='<button type="button" class="primary-btn nk-practice-pause" onclick="window.QB.nkPausePractice()">Pause</button><button type="button" class="primary-btn nk-practice-submit" onclick="window.QB.nkSubmitPracticeSession()">Submit</button>';
    }
    return result;
  };
  /* NK_PRACTICE_SINGLE_REVIEW_GRID_V1_END */
