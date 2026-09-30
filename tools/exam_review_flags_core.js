  /* NK_EXAM_REVIEW_FLAGS_V1_START */
  function nkMarkedTestIds(test){
    const flags=test?.markedForReview||{};
    return (test?.questionIds||[]).map(String).filter(id=>flags[id]===true);
  }
  function nkToggleExamReviewFlag(questionId,sessionId){
    const s=state.activeSession,id=String(questionId||'');
    if(!s||s.mode!=='exam'||String(s.id)!==String(sessionId)||String(s.questionIds[s.index])!==id)return false;
    return nkQuestionTransaction(()=>{
      const flags={...(s.markedForReview||{})};
      if(flags[id])delete flags[id];else flags[id]=true;
      s.markedForReview=flags;
      saveState();render();return true;
    });
  }
  function nkExamReviewButton(q,s){
    const marked=s.markedForReview?.[String(q.id)]===true;
    return `<div class="nk-exam-review-row"><button type="button" class="nk-exam-review-toggle ${marked?'is-marked':''}" aria-pressed="${marked}" onclick="window.QB.nkToggleExamReviewFlag('${esc(String(q.id))}','${esc(String(s.id))}')"><span aria-hidden="true">⚑</span>${marked?'Marked for review':'Mark for review'}</button><small>Use this for guesses or questions to revisit after the test.</small></div>`;
  }
  const nkMarkedOriginalSessionReview=openSessionReview;
  openSessionReview=function(){
    const result=nkMarkedOriginalSessionReview.apply(this,arguments),s=state.activeSession;
    if(s?.mode!=='exam')return result;
    const root=document.getElementById('nk-session-review');if(!root)return result;
    const flags=s.markedForReview||{},count=s.questionIds.filter(id=>flags[String(id)]===true).length;
    if(!count)return result;
    const summary=root.querySelector('.nk-session-review-summary strong');
    if(summary)summary.textContent+=` · ${count} marked`;
    root.querySelectorAll('.nk-session-review-q').forEach((button,i)=>{
      if(flags[String(s.questionIds[i])]!==true)return;
      button.classList.add('is-marked');
      button.setAttribute('aria-label',`${button.getAttribute('aria-label')}, marked for review`);
      const label=button.querySelector('small');if(label)label.textContent='Marked';
    });
    root.querySelector('.nk-session-review-legend')?.insertAdjacentHTML('beforeend','<span><i class="nk-review-dot is-marked"></i>Marked for review</span>');
    return result;
  };
  const nkMarkedOriginalNavigator=openQuestionNavigator;
  openQuestionNavigator=function(){
    const result=nkMarkedOriginalNavigator.apply(this,arguments),s=state.activeSession;
    if(s?.mode!=='exam')return result;
    const root=document.getElementById('qb-question-navigator');if(!root)return result;
    const flags=s.markedForReview||{};
    root.querySelectorAll('.qb-nav-q').forEach((button,i)=>{
      if(flags[String(s.questionIds[i])]!==true)return;
      button.classList.add('is-marked');
      button.setAttribute('aria-label',`${button.getAttribute('aria-label')}, marked for review`);
    });
    root.querySelector('.qb-nav-legend')?.insertAdjacentHTML('beforeend','<span><i class="qb-legend-dot is-marked"></i>Marked for review</span>');
    return result;
  };
  const nkMarkedOriginalResultSection=nkCbtResultSection;
  nkCbtResultSection=function(test){
    const base=nkMarkedOriginalResultSection.apply(this,arguments);
    if(test?.kind==='practice')return base;
    const ids=nkMarkedTestIds(test);if(!ids.length)return base;
    return base+`<section class="nk-section nk-cbt-marked" aria-label="Marked questions"><div><strong>${ids.length} marked for review</strong><small>Your uncertain answers are saved with this test, including any you got right.</small></div><button type="button" data-test-id="${esc(String(test.id))}" onclick="window.QB.nkCbtPracticeMarked(this.getAttribute('data-test-id'),event)">Practise marked questions ${navIcon('chevron',16)}</button></section>`;
  };
  function nkCbtPracticeMarked(testId,clickEvent){
    const test=(state.tests||[]).find(item=>String(item.id)===String(testId));
    if(!test||test.kind==='practice'){showToast('This completed test is unavailable.','bad');return false;}
    if(Number(clickEvent?.detail)>1)return false;
    const questions=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));
    const ids=nkMarkedTestIds(test).filter(id=>questions.has(id)||BY_ID[id]);
    if(!ids.length){showToast('Marked questions are unavailable in the current banks.','bad');return false;}
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(id=>[id,questions.get(id)||BY_ID[id]]))};
    return startSession(ids,'practice',`Marked follow-up · ${test.title||'Timed CBT'}`,'cbt-marked-followup');
  }
  /* NK_EXAM_REVIEW_FLAGS_V1_END */
