  /* NK_TODAY_PLAN_V1_START */
  // Today on Home: one card. What you were doing sits on top (a paused practice, a study set, a timed test),
  // then the day's path: due reviews, mistakes, and new questions toward your own daily goal.
  // Progress is read from today's answers, so any new question answered anywhere counts toward the goal.
  const NK_TODAY_MISTAKES=20,NK_TODAY_NEW=20,NK_GOAL_CHOICES=[20,50,100,150,200];
  function nkTodayGoal(){
    const n=Math.round(Number(state.studyGoals?.newPerDay));
    return Number.isFinite(n)&&n>=1?Math.min(2000,n):NK_TODAY_NEW;
  }
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
  function nkTodayCounts(){
    const t0=nkTodayStart();let reviewed=0,mistakes=0,fresh=0,answered=0;
    Object.keys(state.attempts||{}).forEach(qid=>{
      const list=nkTodayAttempts(qid),today=list.filter(a=>Number(a.at)>=t0);if(!today.length)return;
      answered++;
      const before=list.filter(a=>Number(a.at)<t0);
      if(today.some(a=>a.source==='fsrs-review'))reviewed++;
      else if(!before.length)fresh++;
      else if(nkTodayOpenMistake(before))mistakes++;
    });
    return {reviewed,mistakes,fresh,answered};
  }
  // The plan is fixed when the day starts: reviews already in your deck and mistakes already open. Whatever
  // today's answers create (new mistakes, learning steps, an Again coming back in ten minutes) waits in
  // Revision and joins tomorrow's plan, so studying more never undoes a finished day. FSRS is untouched.
  function nkTodayCarried(){
    const t0=nkTodayStart(),cache=new Map();
    const info=qid=>{qid=String(qid);if(cache.has(qid))return cache.get(qid);
      const list=nkTodayAttempts(qid),before=list.filter(a=>Number(a.at)<t0),today=list.filter(a=>Number(a.at)>=t0);
      const v={known:before.length>0,openAtStart:nkTodayOpenMistake(before),reviewedToday:today.some(a=>a.source==='fsrs-review'),touchedToday:today.length>0};
      cache.set(qid,v);return v;};
    return {
      due:q=>{const v=info(q.id);return v.known&&!v.reviewedToday;},
      wrong:q=>{const v=info(q.id);return v.openAtStart&&!v.touchedToday;}
    };
  }
  function nkTodayPlanData(){
    const desk=nkRevisionDeskData({}),{reviewed,mistakes,fresh,answered}=nkTodayCounts(),goal=nkTodayGoal(),carried=nkTodayCarried();
    const dueCards=desk.dueCards.filter(carried.due),open=desk.wrong.filter(carried.wrong);
    const dueLeft=dueCards.length,missed=open.length,unseen=desk.unseen.length;
    const later={due:desk.dueCards.length-dueLeft,wrong:desk.wrong.length-missed};
    const mistakesLeft=Math.min(missed,Math.max(0,NK_TODAY_MISTAKES-mistakes)),newLeft=Math.min(unseen,Math.max(0,goal-fresh));
    const steps=[
      {kind:'due',title:'Review',done:reviewed,left:dueLeft,total:reviewed+dueLeft,icon:'clock',
        empty:desk.due.length&&!later.due?'Daily review limit reached':'Nothing due',note:n=>`${fmtNum(n)} due`},
      {kind:'wrong',title:'Fix mistakes',done:mistakes,left:mistakesLeft,total:mistakes+mistakesLeft,icon:'refresh',
        empty:missed?'Today’s 20 are done':'No open mistakes',note:n=>`${fmtNum(n)} of ${fmtNum(missed)} open`},
      {kind:'unseen',title:'New questions',done:fresh,left:newLeft,total:Math.max(fresh,Math.min(goal,fresh+unseen)),icon:'book',goal,
        empty:unseen?'Goal met':'Every question seen',note:()=>`${fmtNum(fresh)} of ${fmtNum(goal)} today`}
    ];
    const next=steps.find(s=>s.left>0)||null,total=steps.reduce((n,s)=>n+s.total,0),done=steps.reduce((n,s)=>n+Math.min(s.done,s.total),0);
    return {steps,next,total,done,left:total-done,due:desk.due.length,missed,unseen,answered,fresh,goal,later};
  }
  function nkTodayMarker(step,status){
    if(status==='done')return `<span class="nk-today-marker is-done" aria-hidden="true">${navIcon('check',14)}</span>`;
    return `<span class="nk-today-marker" aria-hidden="true">${navIcon(step.icon,15)}</span>`;
  }
  function nkTodayStepMarkup(step,i,plan,quiet){
    const isNext=plan.next===step,finished=step.left===0,stateName=finished?'done':isNext?'next':'later',isNew=step.kind==='unseen';
    const count=step.kind==='due'?`<b class="nk-count-due">${fmtNum(step.left)}</b>`:step.kind==='wrong'?`<b class="nk-count-missed">${fmtNum(step.left)}</b>`:`<b>${fmtNum(step.left)}</b>`;
    const progress=step.total?`<span class="nk-today-bar" aria-hidden="true"><i style="--nk-today-fill:${Math.round(Math.min(step.done,step.total)/step.total*100)}%"></i></span>`:'';
    const meta=isNew?(finished&&plan.unseen?`${fmtNum(step.done)} today · goal of ${fmtNum(step.goal)} met`:finished?step.empty:step.note(step.left))
      :finished?(step.done?`${fmtNum(step.done)} done · ${step.empty}`:step.empty):`${step.note(step.left)}${step.done?` · ${fmtNum(step.done)} done`:''}`;
    const label=step.kind==='due'?`${fmtNum(step.left)} due reviews`:step.kind==='wrong'?`${fmtNum(plan.missed)} missed questions, ${fmtNum(step.left)} in today's plan`:`${fmtNum(step.left)} new questions left today. Pick a subject`;
    const primary=isNext&&!quiet;
    // New questions always open the topic picker, even after the goal is met, so you can keep going.
    const action=isNew&&plan.unseen?`<button type="button" class="nk-today-go nk-today-learn${primary?' is-primary':''}" onclick="window.QB.nkLearnOpen()" aria-label="${esc(step.title)}: ${esc(finished?'goal met. Pick a subject to keep going':label)}">${finished?'More':primary?`Choose ${count}`:count}${navIcon('chevron',16)}</button>`
      :finished?'':`<button type="button" class="nk-today-go${primary?' is-primary':''}" onclick="window.QB.nkTodayGo('${step.kind}')" aria-label="${esc(step.title)}: ${esc(label)}">${primary?`Start ${count}`:count}${navIcon('chevron',16)}</button>`;
    const goal=isNew?`<button type="button" class="nk-today-goal-edit" aria-expanded="false" aria-controls="nk-today-goal" onclick="window.QB.nkTodayGoalToggle(this)">Goal ${fmtNum(step.goal)}</button>`:'';
    return `<li class="nk-today-step is-${stateName}${isNew?' is-new':''}" style="--nk-i:${i}">${nkTodayMarker(step,stateName)}<div class="nk-today-copy"><strong>${esc(step.title)}</strong><small>${esc(meta)}${goal?' · ':''}${goal}</small>${progress}</div>${action}${isNew?nkTodayGoalMarkup():''}</li>`;
  }
  // The focus band is the old Today's focus card, now the head of this card.
  const nkTodayFocusBand=nkHomeFocusSection;
  nkHomeFocusSection=function(){return '';};
  function nkHomeTodayPlan(){
    const plan=nkTodayPlanData(),complete=!plan.next;
    let band='';
    try{const focus=nkLatestPracticeContext();band=nkTodayFocusBand(focus,nkHomeFocusModule(focus))||'';}catch(_error){band='';}
    const minutes=Math.max(1,Math.round(plan.left*1.1));
    const lead=complete?(plan.answered?`Done for today · ${fmtNum(plan.answered)} answered`:'Nothing scheduled. Pick any topic to study.'):`${fmtNum(plan.left)} questions left · about ${minutes<60?`${fmtNum(minutes)} min`:`${Math.floor(minutes/60)} h ${minutes%60} min`}`;
    const fill=plan.total?Math.round(plan.done/plan.total*100):complete?100:0;
    return `<section class="nk-home-revision nk-today${complete?' is-complete':''}${band?' has-focus':''}" aria-labelledby="nk-today-title">${band}
      <div class="nk-today-body">
      <header class="nk-today-head"><div><h2 id="nk-today-title">Today’s plan</h2><p>${lead}</p></div><button type="button" class="nk-today-link" onclick="window.QB.nkOpenRevisionHub()">Revision ${navIcon('chevron',15)}</button></header>
      <div class="nk-today-meter" role="progressbar" aria-label="Today’s plan" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${fill}"><i style="--nk-today-fill:${fill}%"></i></div>
      <ol class="nk-today-steps">${plan.steps.map((step,i)=>nkTodayStepMarkup(step,i,plan,Boolean(band))).join('')}</ol>
      ${plan.later.due||plan.later.wrong?`<p class="nk-today-later">From today’s answers: ${[plan.later.wrong?`${fmtNum(plan.later.wrong)} mistake${plan.later.wrong===1?'':'s'}`:'',plan.later.due?`${fmtNum(plan.later.due)} review${plan.later.due===1?'':'s'}`:''].filter(Boolean).join(' and ')} wait in Revision. They join tomorrow’s plan.</p>`:''}
      </div>
    </section>`;
  }
  function nkTodayGo(kind,extra=false){
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test first.','bad');return false;}
    // Today's plan covers every subject, whatever focus the Revision page was last left on.
    const scope=typeof nkRevisionScope==='object'?nkRevisionScope:null;
    if(scope)nkRevisionScope={subject:'',bank:'',topic:''};
    try{
      const carried=nkTodayCarried();
      if(kind==='due')return nkStartRevisionQueue('due',0,carried.due);
      const step=nkTodayPlanData().steps.find(s=>s.kind===kind),limit=extra?NK_TODAY_NEW:step?.left;
      if(!limit){showToast(kind==='wrong'?'Today’s mistakes are done.':'Today’s new questions are done.');return false;}
      return nkStartRevisionQueue(kind,limit,kind==='wrong'?carried.wrong:null);
    }finally{if(scope)nkRevisionScope=scope;}
  }
  nkHomeRevisionSummary=nkHomeTodayPlan;

  // New questions: no extra layer. The button takes you down to My Subjects, where every bank and topic
  // already lives; whatever new questions you answer there count toward the goal. The goal itself is set inline.
  function nkLearnOpen(){
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test first.','bad');return false;}
    if(route?.page!=='dashboard'){navigate('dashboard');}
    requestAnimationFrame(()=>{
      const target=document.querySelector('.nk-home-subjects');if(!target)return;
      const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
      target.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'});
      target.classList.remove('is-pointed');void target.offsetWidth;target.classList.add('is-pointed');
      setTimeout(()=>target.classList.remove('is-pointed'),1800);
    });
    return true;
  }
  function nkTodayGoalMarkup(){
    const goal=nkTodayGoal(),custom=!NK_GOAL_CHOICES.includes(goal);
    return `<div class="nk-today-goal" id="nk-today-goal" hidden><span>New questions a day</span><div class="nk-exam-chips" role="radiogroup" aria-label="Daily goal for new questions">${NK_GOAL_CHOICES.map(n=>`<button type="button" role="radio" aria-checked="${goal===n}" class="${goal===n?'is-selected':''}" onclick="window.QB.nkLearnSetGoal(${n})">${n}</button>`).join('')}<label class="nk-today-goal-own${custom?' is-selected':''}"><span class="nk-sr">Your own daily goal</span><input type="number" inputmode="numeric" min="1" max="2000" step="1" placeholder="Own" value="${custom?goal:''}" onchange="window.QB.nkLearnSetGoal(this.value)"></label></div></div>`;
  }
  function nkTodayGoalToggle(button){
    const panel=document.getElementById('nk-today-goal');if(!panel)return;
    const open=panel.hidden;panel.hidden=!open;if(button)button.setAttribute('aria-expanded',String(open));
  }
  function nkLearnSetGoal(value){
    const n=Math.round(Number(value));
    if(!Number.isFinite(n)||n<1){showToast('Set a goal of at least 1 question.','bad');return false;}
    state.studyGoals={...(state.studyGoals||{}),newPerDay:Math.min(2000,n)};saveState();
    try{nkTodayGoalBelow=nkTodayCounts().fresh<Math.min(2000,n);}catch(_error){}
    if(route?.page==='dashboard'&&typeof render==='function'){render();const panel=document.getElementById('nk-today-goal');if(panel){panel.hidden=false;document.querySelector('.nk-today-goal-edit')?.setAttribute('aria-expanded','true');}}
    return true;
  }
  // A quiet word when today's goal is reached, wherever the new question was answered. Answers can be
  // recorded a moment after submit, so the check runs again once they land; it fires once a day, and only
  // after the count was seen below the goal.
  let nkTodayGoalToastDay=0,nkTodayGoalBelow=null;
  function nkTodayGoalCheck(){
    try{
      const day=nkTodayStart(),goal=nkTodayGoal(),fresh=nkTodayCounts().fresh;
      if(nkTodayGoalBelow===true&&fresh>=goal&&nkTodayGoalToastDay!==day){nkTodayGoalToastDay=day;showToast(`Daily goal reached · ${fmtNum(fresh)} new questions today`);}
      nkTodayGoalBelow=fresh<goal;
    }catch(_error){}
  }
  if(typeof submitPractice==='function'){
    const nkTodayOriginalSubmit=submitPractice;
    submitPractice=function(){
      if(nkTodayGoalBelow===null)nkTodayGoalCheck();
      const out=nkTodayOriginalSubmit.apply(this,arguments);
      nkTodayGoalCheck();setTimeout(nkTodayGoalCheck,0);setTimeout(nkTodayGoalCheck,250);
      return out;
    };
  }
  /* NK_TODAY_PLAN_V1_END */
