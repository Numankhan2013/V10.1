  /* NK_UWORLD_BIOCHEMISTRY_V1_START */
  // Presentation adapter only. The incumbent engine owns answer commits and FSRS.
  function nkUworldOptionMarkup(q,o){return nkScientificMarkup(o.text);}
  function nkUworldParagraph(text){
    const label=String(text).match(/^(\(Choices?[^)]*\)|[1-9]\.\s+[A-Z][a-z]+:)(\s*)([\s\S]*)$/);
    return label?`<p><strong>${nkScientificMarkup(label[1])}</strong> ${nkScientificMarkup(label[3])}</p>`:`<p>${nkScientificMarkup(text)}</p>`;
  }
  function nkUworldReading(q){
    const transcript=q.uworldTranscript,objective=q.uworldSource?.explanation?.educational_objective;
    const paragraphs=transcript?.paragraphs||[q.uworldSource?.explanation?.text||''];
    return `<div class="nk-uworld-reading">${paragraphs.map(nkUworldParagraph).join('')}${objective?`<section class="nk-uworld-objective"><h3>Educational objective</h3><p>${nkScientificMarkup(objective)}</p></section>`:'<p class="nk-uworld-source-note">The educational objective is clipped in the supplied source.</p>'}<details class="nk-uworld-original"><summary>About this OCR text</summary><p class="nk-uworld-source-note">This Biochemistry pilot uses the supplied OCR text. Scanning errors and flattened tables may remain. Diagrams and question-by-question validation will follow.</p><details><summary>Original OCR explanation</summary><p>${nkScientificMarkup(q.uworldSource?.explanation?.text||'')}</p></details></details></div>`;
  }
  const nkUworldOriginalStem=nkQuestionStemMarkup;
  nkQuestionStemMarkup=function(q){
    if(q?.bank!=='UWorld')return nkUworldOriginalStem(q);
    return `<span class="nk-uworld-stem">${nkUworldOriginalStem(q)}</span>`;
  };
  const nkUworldOriginalSupport=nkStudySupport;
  nkStudySupport=function(q,timeMs,unattempted=false,renderedSource=''){
    if(q?.bank!=='UWorld')return nkUworldOriginalSupport(q,timeMs,unattempted,renderedSource);
    const time=unattempted?'<span>Not answered in this test</span>':`<span>Answered in <strong>${esc(nkFormatQuestionTime(timeMs||0))}</strong></span>`;
    return `<div class="nk-study-support is-uworld"><div class="nk-answer-time">${navIcon('clock',19)}${time}</div><section class="nk-source-section nk-uworld-explanation"><header><div>${navIcon('book',19)}<strong>Explanation</strong></div><span>UWorld 2024 · OCR pilot</span></header>${nkUworldReading(q)}</section></div>`;
  };
  function nkUworldEligible(q){return q?.bank!=='UWorld'||nkQuestionPresentationFor(q).valid;}
  // Filter before sampling, so new tests/modules have accurate counts and full sets.
  const nkUworldCbtPool=nkCbtPool;
  nkCbtPool=function(){return nkUworldCbtPool.apply(this,arguments).filter(nkUworldEligible);};
  const nkUworldModulePool=nkQuestionsForModuleDraft;
  nkQuestionsForModuleDraft=function(){return nkUworldModulePool.apply(this,arguments).filter(nkUworldEligible);};
  const nkUworldRevisionData=nkRevisionDeskData;
  nkRevisionDeskData=function(){
    const data=nkUworldRevisionData.apply(this,arguments);
    for(const key of ['wrong','bookmarked','unseen','due','dueCards'])data[key]=(data[key]||[]).filter(nkUworldEligible);
    return data;
  };
  const nkUworldStartSession=startSession;
  startSession=function(ids){
    const eligible=(ids||[]).filter(id=>nkUworldEligible(nkFindStudyQuestion(id)));
    if(!eligible.length&&ids?.length){showToast('These questions need source diagrams. Open them individually to read the available OCR text.','bad');return false;}
    const args=[...arguments];args[0]=eligible;return nkUworldStartSession.apply(this,args);
  };
  function nkUworldReference(id){
    const q=nkFindStudyQuestion(id);if(q?.bank!=='UWorld'||nkUworldEligible(q))return false;
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test before opening another question.','bad');return false;}
    closeModal();
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-modal-v114" id="modal"><section class="modal nk-uworld-reference" role="dialog" aria-modal="true" aria-labelledby="nk-uworld-reference-title"><button type="button" class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button><h2 id="nk-uworld-reference-title">Diagram needed</h2><p class="nk-uworld-source-note">This question is reference only until its source diagram is added. Reading it does not record an answer or affect your score.</p><div class="nk-uworld-reference-question">${nkScientificMarkup(q.question)}</div><details class="nk-uworld-reference-explanation"><summary>Read explanation</summary>${nkUworldReading(q)}</details></section></div>`);
    return true;
  }
  const nkUworldPracticeOne=practiceOne;
  practiceOne=function(id){const q=nkFindStudyQuestion(id);return q?.bank==='UWorld'&&!nkUworldEligible(q)?nkUworldReference(id):nkUworldPracticeOne.apply(this,arguments);};
  /* NK_UWORLD_BIOCHEMISTRY_V1_END */
