  /* NK_EXAM_SETTINGS_V1_START */
  // Exam settings: marks per correct / wrong / blank answer and time per question.
  // Kept in a closed disclosure on the builder's last step and remembered as the default for every new timed test.
  const NK_EXAM_PRESETS=[
    {id:'plain',label:'No negative',correct:1,wrong:0,blank:0},
    {id:'neet',label:'NEET PG',correct:4,wrong:-1,blank:0},
    {id:'thirds',label:'+1 / −⅓',correct:1,wrong:-1/3,blank:0},
    {id:'quarter',label:'+1 / −¼',correct:1,wrong:-0.25,blank:0}
  ];
  const NK_EXAM_SECONDS=[45,60,63,72,90];
  function nkExamNum(value,fallback,min,max){const n=Number(value);return Number.isFinite(n)?Math.min(max,Math.max(min,n)):fallback;}
  function nkExamSettings(){
    const raw=state.examSettings||{};
    return {correct:nkExamNum(raw.correct,1,0.25,100),wrong:nkExamNum(raw.wrong,0,-100,0),blank:nkExamNum(raw.blank,0,-100,100),seconds:Math.round(nkExamNum(raw.seconds,60,10,600))};
  }
  function nkExamIsPlain(m){return !m||(Number(m.correct)===1&&Number(m.wrong)===0&&!Number(m.blank));}
  function nkExamPresetId(x=nkExamSettings()){return NK_EXAM_PRESETS.find(p=>Math.abs(p.correct-x.correct)<1e-6&&Math.abs(p.wrong-x.wrong)<1e-6&&Math.abs(p.blank-x.blank)<1e-6)?.id||'custom';}
  function nkExamApply(settings=nkExamSettings(),force=false){
    const s=state.activeSession;if(!s||s.mode!=='exam'||s.timerMode==='per-question')return false;
    if(s.examSettingsApplied&&!force)return false;
    const x={...nkExamSettings(),...settings};
    s.marking={correct:x.correct,wrong:x.wrong,blank:x.blank};
    s.secondsPerQuestion=Math.round(x.seconds);s.examSettingsApplied=true;
    s.deadlineAt=Number(s.startedAt||Date.now())+nkExamTotalSeconds(s)*1000;
    saveState();
    if(typeof startExamTicker==='function'&&route.page==='exam')startExamTicker();
    return true;
  }
  function nkExamSummary(x=nkExamSettings()){
    const preset=NK_EXAM_PRESETS.find(p=>p.id===nkExamPresetId(x));
    return `${preset&&preset.id!=='plain'?esc(preset.label)+' · ':''}${nkMarkingLabel(x)} · ${fmtNum(x.seconds)} s per question`;
  }
  function nkExamField(id,label,value,min,max,step){
    return `<label class="nk-exam-field" for="nk-exam-${id}"><span>${label}</span><input id="nk-exam-${id}" type="number" inputmode="decimal" step="${step}" min="${min}" max="${max}" value="${Math.round(value*1000)/1000}" onchange="window.QB.nkExamSet('${id}',this.value)"></label>`;
  }
  function nkExamSettingsMarkup(){
    const x=nkExamSettings(),active=nkExamPresetId(x),open=state.examSettingsOpen?' open':'';
    return `<details class="nk-exam-settings"${open} ontoggle="window.QB.nkExamToggle(this.open)">
      <summary><span class="nk-exam-settings-icon">${navIcon('more',18)}</span><span class="nk-exam-settings-copy"><strong>Exam settings</strong><small id="nk-exam-summary">${nkExamSummary(x)}</small></span><span class="nk-exam-settings-chev" aria-hidden="true">${navIcon('chevron',16)}</span></summary>
      <div class="nk-exam-settings-body">
        <fieldset><legend>Marking</legend>
          <div class="nk-exam-chips" role="radiogroup" aria-label="Marking scheme">${NK_EXAM_PRESETS.map(p=>`<button type="button" role="radio" aria-checked="${active===p.id}" class="${active===p.id?'is-selected':''}" onclick="window.QB.nkExamPreset('${p.id}')">${esc(p.label)}</button>`).join('')}<button type="button" role="radio" aria-checked="${active==='custom'}" class="${active==='custom'?'is-selected':''}" onclick="document.getElementById('nk-exam-correct')?.focus()">Custom</button></div>
          <div class="nk-exam-fields">${nkExamField('correct','Correct',x.correct,0.25,100,0.25)}${nkExamField('wrong','Wrong',x.wrong,-100,0,0.25)}${nkExamField('blank','Blank',x.blank,-100,100,0.25)}</div>
        </fieldset>
        <fieldset><legend>Time per question</legend>
          <div class="nk-exam-chips" role="radiogroup" aria-label="Seconds per question">${NK_EXAM_SECONDS.map(n=>`<button type="button" role="radio" aria-checked="${x.seconds===n}" class="${x.seconds===n?'is-selected':''}" onclick="window.QB.nkExamSet('seconds',${n})">${n} s</button>`).join('')}</div>
          <p>NEET PG gives about 63 s a question. Your choice applies to every new timed test until you change it.</p>
        </fieldset>
      </div>
    </details>`;
  }
  function nkExamRefresh(){
    const box=document.querySelector('.nk-exam-settings');
    // Blur the edited field first: replacing the box while it holds focus fires blur mid-replace and throws.
    if(box){const open=box.open,focused=box.contains(document.activeElement)?document.activeElement:null,key=focused?.id||'';
      if(focused)focused.blur();
      box.outerHTML=nkExamSettingsMarkup();const next=document.querySelector('.nk-exam-settings');if(next)next.open=open;
      if(key)document.getElementById(key)?.focus({preventScroll:true});}
    if(typeof nkCbtDraft!=='undefined'&&nkCbtDraft&&typeof nkCbtSetCount==='function')nkCbtSetCount(nkCbtDraft.count);
  }
  function nkExamSet(field,value){
    const x=nkExamSettings();
    if(field==='seconds')x.seconds=Math.round(nkExamNum(value,60,10,600));
    else if(field==='correct')x.correct=nkExamNum(value,x.correct,0.25,100);
    else if(field==='wrong')x.wrong=-Math.abs(nkExamNum(value,x.wrong,-100,100));
    else if(field==='blank')x.blank=nkExamNum(value,x.blank,-100,100);
    state.examSettings=x;saveState();nkExamRefresh();
  }
  function nkExamPreset(id){const p=NK_EXAM_PRESETS.find(item=>item.id===id);if(!p)return;state.examSettings={...nkExamSettings(),correct:p.correct,wrong:p.wrong,blank:p.blank};saveState();nkExamRefresh();}
  function nkExamToggle(open){state.examSettingsOpen=Boolean(open);}
  if(typeof nkCbtQuestionsMarkup==='function'){
    const nkExamOriginalQuestions=nkCbtQuestionsMarkup;
    nkCbtQuestionsMarkup=function(){
      const x=nkExamSettings();
      return nkExamOriginalQuestions.apply(this,arguments)
        .replace('One minute per question. Answers and explanations appear after submission.',`${fmtNum(x.seconds)} seconds per question${nkExamIsPlain(x)?'':` · ${esc(nkMarkingLabel(x))} marking`}. Answers appear after submission.`)
        +nkExamSettingsMarkup();
    };
  }
  if(typeof nkCbtSetCount==='function'){
    const nkExamOriginalSetCount=nkCbtSetCount;
    nkCbtSetCount=function(){
      const out=nkExamOriginalSetCount.apply(this,arguments),result=document.getElementById('nk-cbt-count-result'),n=Number(nkCbtDraft?.count)||0;
      if(result&&n){const minutes=Math.round(n*nkExamSettings().seconds/60);result.textContent=`${fmtNum(n)} question${n===1?'':'s'} · ${fmtNum(minutes)} minute${minutes===1?'':'s'} total`;}
      return out;
    };
  }
  // Every timed test started from Tests takes the current settings; a retake keeps the original test's.
  if(typeof nkCbtStart==='function'){const original=nkCbtStart;nkCbtStart=function(){const out=original.apply(this,arguments);nkExamApply();return out;};}
  if(typeof nkMockStart==='function'){const original=nkMockStart;nkMockStart=function(){const out=original.apply(this,arguments);if(out!==false)nkExamApply();return out;};}
  if(typeof nkCbtRetake==='function'){
    const original=nkCbtRetake;
    nkCbtRetake=function(testId){
      const test=(state.tests||[]).find(t=>String(t.id)===String(testId)),out=original.apply(this,arguments);
      if(out!==false&&test)nkExamApply(test.marking?{...test.marking,seconds:test.secondsPerQuestion||60}:{correct:1,wrong:0,blank:0,seconds:60},true);
      return out;
    };
  }
  /* NK_EXAM_SETTINGS_V1_END */
