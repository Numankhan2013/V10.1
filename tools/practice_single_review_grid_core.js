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
    const actions=box.querySelector('.nk-session-review-actions');
    if(actions){
      actions.innerHTML='<button type="button" class="primary-btn nk-practice-pause" onclick="window.QB.nkPausePractice()">Pause</button><button type="button" class="primary-btn nk-practice-submit" onclick="window.QB.nkSubmitPracticeSession()">Submit</button>';
    }
    return result;
  };
  /* NK_PRACTICE_SINGLE_REVIEW_GRID_V1_END */
