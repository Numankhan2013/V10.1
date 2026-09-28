  /* NK_PRACTICE_CORRECTION_V1_START */
  // Keep the first saved Practice result intact. Each correction is a fresh
  // retrieval attempt with its own saved result and normal FSRS scheduling.
  function nkCorrectionQuestionMap(){return new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));}
  function nkCorrectionMisses(test,questions=nkCorrectionQuestionMap()){
    const ids=[],missing=[],unanswerable=[];
    for(const raw of test?.questionIds||[]){
      const id=String(raw),q=questions.get(id);
      if(!q){missing.push(id);continue;}
      const answer=Number(q.correctOption),optionCount=Array.isArray(q.options)?q.options.length:4;
      if(!Number.isInteger(answer)||answer<1||answer>optionCount){unanswerable.push(id);continue;}
      if(Number(test.answers?.[id])!==Number(q.correctOption))ids.push(id);
    }
    return {ids,missing,unanswerable};
  }
  function nkCorrectionResultSection(test){
    if(test?.kind!=='practice'||!Array.isArray(test.questionIds)||!test.questionIds.length)return '';
    const questions=nkCorrectionQuestionMap(),{ids,missing,unanswerable}=nkCorrectionMisses(test,questions);
    const parent=(state.tests||[]).find(item=>item?.kind==='practice'&&String(item.id)===String(test.correctionOf||''));
    let comparison='';
    if(parent){
      const priorMisses=new Set(nkCorrectionMisses(parent,questions).ids);
      const targeted=test.questionIds.map(String).filter(id=>priorMisses.has(id));
      const still=new Set(ids),corrected=targeted.filter(id=>!still.has(id)&&questions.has(id)).length;
      comparison=`<p class="nk-correction-progress"><strong>${corrected} corrected</strong> from the previous pass · ${targeted.filter(id=>still.has(id)).length} still missed or unattempted. A correct answer here is a step; spaced review checks retention later.</p><button type="button" class="nk-correction-parent" data-result-id="${esc(String(parent.id))}" onclick="window.QB.nav('result',this.getAttribute('data-result-id'))">View previous result</button>`;
    }
    const latest=(state.tests||[]).filter(item=>item?.kind==='practice'&&String(item.correctionOf||'')===String(test.id)).sort((a,b)=>Number(b.createdAt||0)-Number(a.createdAt||0))[0];
    const recent=latest?`<button type="button" class="nk-correction-parent" data-result-id="${esc(String(latest.id))}" onclick="window.QB.nav('result',this.getAttribute('data-result-id'))">View latest correction pass</button>`:'';
    const action=missing.length?`<p class="nk-correction-unavailable">${missing.length} saved question${missing.length===1?' is':'s are'} unavailable in the current banks, so an exact correction pass cannot start.</p>`:
      ids.length?`<div class="nk-correction-action"><div><strong>${ids.length} question${ids.length===1?' needs':'s need'} another pass</strong><small>Retry this result's answerable misses with blank answers. Your saved result stays unchanged.</small></div><button type="button" data-result-id="${esc(String(test.id))}" onclick="window.QB.nkCorrectionStart(this.getAttribute('data-result-id'),event)">Correct my misses ${navIcon('chevron',16)}</button></div>`:
      unanswerable.length?'<p class="nk-correction-unavailable">No answerable misses remain in this pass.</p>':
      `<p class="nk-correction-clear">All questions in this pass were correct. They remain in your spaced review schedule.</p>`;
    if(!ids.length&&!test.correctionOf&&!latest&&!missing.length&&!unanswerable.length)return '';
    const caveat=unanswerable.length?`<p class="nk-correction-unavailable">${unanswerable.length} source question${unanswerable.length===1?' lacks':'s lack'} a reliable answer key and ${unanswerable.length===1?'is':'are'} excluded.</p>`:'';
    return `<section class="nk-correction-section" aria-labelledby="nk-correction-heading"><div class="nk-kicker">LEARN FROM THIS SESSION</div><h2 id="nk-correction-heading">Close the gaps</h2>${comparison}${action}${caveat}${recent}</section>`;
  }
  function nkCorrectionStart(testId,clickEvent){
    const test=(state.tests||[]).find(item=>item?.kind==='practice'&&String(item.id)===String(testId));
    if(!test){showToast('This saved Practice result is unavailable.','bad');return false;}
    // Ignore the carried-over second tap from the Submit action on a new page.
    if(Number(clickEvent?.detail)>1||Date.now()-Number(test.createdAt||0)<900)return false;
    const questions=nkCorrectionQuestionMap(),{ids,missing}=nkCorrectionMisses(test,questions);
    if(missing.length){showToast('Some saved questions are unavailable. This exact pass cannot start.','bad');return false;}
    if(!ids.length){showToast('This result has no missed questions.');return false;}
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(id=>[id,questions.get(id)]))};
    return startSession(ids,'practice',`Correction pass · ${ids.length} question${ids.length===1?'':'s'}`,`correction:${String(test.id)}`);
  }
  /* NK_PRACTICE_CORRECTION_V1_END */
