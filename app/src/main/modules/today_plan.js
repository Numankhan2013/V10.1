  /* NK_TODAY_PLAN_V1_START */
  // Today's plan: one ordered path on Home. Due reviews first, then mistakes, then new questions.
  // Progress is read from today's answers, so the plan survives reloads and device sync without extra state.
  const NK_TODAY_MISTAKES=20,NK_TODAY_NEW=20;
  function nkTodayStart(){const d=new Date();d.setHours(0,0,0,0);return d.getTime();}
  function nkTodayAttempts(qid){
    const list=typeof nkFsrsActiveAttempts==='function'?nkFsrsActiveAttempts(String(qid)):(qAttempts(String(qid))||[]).filter(a=>a&&!a.isUndo);
    return list.filter(a=>Number(a?.at)>0);
  }
  // Was this question an open mistake when today began? Same rule as nkFsrsPracticeMistake, on yesterday's history.
  function nkTodayOpenMistake(before){
    let open=false;
    for(const a of before){if(a.correct===true)open=false;else if(a.correct===false&&a.source!=='fsrs-review')open=true;}
    return open;
  }
  function nkTodayPlanData(){
    const t0=nkTodayStart(),desk=nkRevisionDeskData({});
    let reviewed=0,mistakes=0,fresh=0,answered=0;
    Object.keys(state.attempts||{}).forEach(qid=>{
      const list=nkTodayAttempts(qid),today=list.filter(a=>Number(a.at)>=t0);if(!today.length)return;
      answered++;
      const before=list.filter(a=>Number(a.at)<t0);
      if(today.some(a=>a.source==='fsrs-review'))reviewed++;
      else if(!before.length)fresh++;
      else if(nkTodayOpenMistake(before))mistakes++;
    });
    const dueLeft=desk.dueCards.length,missed=desk.wrong.length,unseen=desk.unseen.length;
    const mistakesLeft=Math.min(missed,Math.max(0,NK_TODAY_MISTAKES-mistakes)),newLeft=Math.min(unseen,Math.max(0,NK_TODAY_NEW-fresh));
    const steps=[
      {kind:'due',title:'Review',done:reviewed,left:dueLeft,total:reviewed+dueLeft,icon:'clock',
        empty:desk.due.length?'Daily review limit reached':'Nothing due',note:n=>`${fmtNum(n)} due`},
      {kind:'wrong',title:'Fix mistakes',done:mistakes,left:mistakesLeft,total:mistakes+mistakesLeft,icon:'refresh',
        empty:missed?'Today’s 20 are done':'No open mistakes',note:n=>`${fmtNum(n)} of ${fmtNum(missed)} open`},
      {kind:'unseen',title:'Learn new',done:fresh,left:newLeft,total:fresh+newLeft,icon:'book',
        empty:unseen?'Today’s 20 are done':'Every question seen',note:n=>`${fmtNum(n)} new questions`}
    ];
    const next=steps.find(s=>s.left>0)||null,total=steps.reduce((n,s)=>n+s.total,0),done=steps.reduce((n,s)=>n+Math.min(s.done,s.total),0);
    return {steps,next,total,done,left:total-done,due:desk.due.length,missed,answered};
  }
  function nkTodayMarker(step,status){
    if(status==='done')return `<span class="nk-today-marker is-done" aria-hidden="true">${navIcon('check',14)}</span>`;
    return `<span class="nk-today-marker" aria-hidden="true">${navIcon(step.icon,15)}</span>`;
  }
  function nkTodayStepMarkup(step,i,plan){
    const isNext=plan.next===step,finished=step.left===0,stateName=finished?'done':isNext?'next':'later';
    const count=step.kind==='due'?`<b class="nk-count-due">${fmtNum(step.left)}</b>`:step.kind==='wrong'?`<b class="nk-count-missed">${fmtNum(step.left)}</b>`:`<b>${fmtNum(step.left)}</b>`;
    const progress=step.total?`<span class="nk-today-bar" aria-hidden="true"><i style="--nk-today-fill:${Math.round(Math.min(step.done,step.total)/step.total*100)}%"></i></span>`:'';
    const meta=finished?(step.done?`${fmtNum(step.done)} done · ${step.empty}`:step.empty):`${step.note(step.left)}${step.done?` · ${fmtNum(step.done)} done`:''}`;
    const label=step.kind==='due'?`${fmtNum(step.left)} due reviews`:step.kind==='wrong'?`${fmtNum(plan.missed)} missed questions, ${fmtNum(step.left)} in today's plan`:`${fmtNum(step.left)} new questions`;
    const action=finished?'':`<button type="button" class="nk-today-go${isNext?' is-primary':''}" onclick="window.QB.nkTodayGo('${step.kind}')" aria-label="${esc(step.title)}: ${esc(label)}">${isNext?`Start ${count}`:count}${navIcon('chevron',16)}</button>`;
    return `<li class="nk-today-step is-${stateName}" style="--nk-i:${i}">${nkTodayMarker(step,stateName)}<div class="nk-today-copy"><strong>${esc(step.title)}</strong><small>${esc(meta)}</small>${progress}</div>${action}</li>`;
  }
  function nkHomeTodayPlan(){
    const plan=nkTodayPlanData(),complete=!plan.next;
    const minutes=Math.max(1,Math.round(plan.left*1.1));
    const lead=complete?(plan.answered?`Done for today · ${fmtNum(plan.answered)} answered`:'Nothing scheduled. Pick any topic to study.'):`${fmtNum(plan.left)} questions · about ${minutes<60?`${fmtNum(minutes)} min`:`${Math.floor(minutes/60)} h ${minutes%60} min`}`;
    const fill=plan.total?Math.round(plan.done/plan.total*100):complete?100:0;
    return `<section class="nk-home-revision nk-today${complete?' is-complete':''}" aria-labelledby="nk-today-title">
      <header class="nk-today-head"><div><h2 id="nk-today-title">Today</h2><p>${lead}</p></div><button type="button" class="nk-today-link" onclick="window.QB.nkOpenRevisionHub()">Revision ${navIcon('chevron',15)}</button></header>
      <div class="nk-today-meter" role="progressbar" aria-label="Today’s plan" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${fill}"><i style="--nk-today-fill:${fill}%"></i></div>
      <ol class="nk-today-steps">${plan.steps.map((step,i)=>nkTodayStepMarkup(step,i,plan)).join('')}</ol>
      ${complete&&nkRevisionDeskData({}).unseen.length?`<button type="button" class="nk-today-more" onclick="window.QB.nkTodayGo('unseen',true)">${navIcon('plus',16)} 20 more new questions</button>`:''}
    </section>`;
  }
  function nkTodayGo(kind,extra=false){
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test first.','bad');return false;}
    if(kind==='due')return nkStartRevisionQueue('due');
    const step=nkTodayPlanData().steps.find(s=>s.kind===kind),limit=extra?NK_TODAY_NEW:step?.left;
    if(!limit){showToast(kind==='wrong'?'Today’s mistakes are done.':'Today’s new questions are done.');return false;}
    return nkStartRevisionQueue(kind,limit);
  }
  nkHomeRevisionSummary=nkHomeTodayPlan;
  /* NK_TODAY_PLAN_V1_END */
