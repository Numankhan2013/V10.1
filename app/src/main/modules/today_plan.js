  /* NK_TODAY_PLAN_V1_START */
  // Today on Home: one card. What you were doing sits on top (a paused practice, a study set, a timed test),
  // then the day's path: due reviews, mistakes, and new questions toward your own daily goal.
  // Progress is read from today's answers, so any new question answered anywhere counts toward the goal.
  const NK_TODAY_MISTAKES=20,NK_TODAY_NEW=20,NK_GOAL_CHOICES=[20,50,100,150,200,300];
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
  function nkTodayPlanData(){
    const desk=nkRevisionDeskData({}),{reviewed,mistakes,fresh,answered}=nkTodayCounts(),goal=nkTodayGoal();
    const dueLeft=desk.dueCards.length,missed=desk.wrong.length,unseen=desk.unseen.length;
    const mistakesLeft=Math.min(missed,Math.max(0,NK_TODAY_MISTAKES-mistakes)),newLeft=Math.min(unseen,Math.max(0,goal-fresh));
    const steps=[
      {kind:'due',title:'Review',done:reviewed,left:dueLeft,total:reviewed+dueLeft,icon:'clock',
        empty:desk.due.length?'Daily review limit reached':'Nothing due',note:n=>`${fmtNum(n)} due`},
      {kind:'wrong',title:'Fix mistakes',done:mistakes,left:mistakesLeft,total:mistakes+mistakesLeft,icon:'refresh',
        empty:missed?'Today’s 20 are done':'No open mistakes',note:n=>`${fmtNum(n)} of ${fmtNum(missed)} open`},
      {kind:'unseen',title:'New questions',done:fresh,left:newLeft,total:Math.max(fresh,Math.min(goal,fresh+unseen)),icon:'book',goal,
        empty:unseen?'Goal met':'Every question seen',note:()=>`${fmtNum(fresh)} of ${fmtNum(goal)} today`}
    ];
    const next=steps.find(s=>s.left>0)||null,total=steps.reduce((n,s)=>n+s.total,0),done=steps.reduce((n,s)=>n+Math.min(s.done,s.total),0);
    return {steps,next,total,done,left:total-done,due:desk.due.length,missed,unseen,answered,fresh,goal};
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
    const label=step.kind==='due'?`${fmtNum(step.left)} due reviews`:step.kind==='wrong'?`${fmtNum(plan.missed)} missed questions, ${fmtNum(step.left)} in today's plan`:`${fmtNum(step.left)} new questions left today. Choose topics`;
    const primary=isNext&&!quiet;
    // New questions always open the topic picker, even after the goal is met, so you can keep going.
    const action=isNew&&plan.unseen?`<button type="button" class="nk-today-go nk-today-learn${primary?' is-primary':''}" onclick="window.QB.nkLearnOpen()" aria-label="${esc(step.title)}: ${esc(finished?'goal met. Learn more':label)}">${finished?'More':primary?`Choose ${count}`:count}${navIcon('chevron',16)}</button>`
      :finished?'':`<button type="button" class="nk-today-go${primary?' is-primary':''}" onclick="window.QB.nkTodayGo('${step.kind}')" aria-label="${esc(step.title)}: ${esc(label)}">${primary?`Start ${count}`:count}${navIcon('chevron',16)}</button>`;
    return `<li class="nk-today-step is-${stateName}${isNew?' is-new':''}" style="--nk-i:${i}">${nkTodayMarker(step,stateName)}<div class="nk-today-copy"><strong>${esc(step.title)}</strong><small>${esc(meta)}</small>${progress}</div>${action}</li>`;
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
      </div>
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

  // New questions: a sheet with the daily goal and every subject, bank and topic that still has unseen questions.
  // Nothing ticked means everything. The session holds exactly what is left of today's goal.
  let nkLearn=null; // {tree, picked:Set, open:Set, query, order, dirty}
  const NK_LEARN_SEP='\u001f';
  function nkLearnTree(){
    const subjects=new Map();
    nkRevisionDeskData({}).unseen.forEach((q,at)=>{
      const sName=String(q.subject||'Other'),bName=String(q.bank||''),tId=String(q.chapterId??'');
      let s=subjects.get(sName);if(!s){s={name:sName,count:0,banks:new Map()};subjects.set(sName,s);}
      let b=s.banks.get(bName);if(!b){b={name:bName,count:0,topics:new Map(),record:typeof nkBankRecord==='function'&&bName?nkBankRecord(sName,bName):null};s.banks.set(bName,b);}
      let t=b.topics.get(tId);
      if(!t){
        const list=b.record?.bank===bName?(b.record.topics||[]):[],order=list.findIndex(x=>String(x.id)===tId);
        const title=order>=0?(list[order].title||list[order].name):(typeof nkTopicTitleForQuestion==='function'?nkTopicTitleForQuestion(q):'')||q.topic||q.chapter||'Other';
        t={id:tId,key:[sName,bName,tId].join(NK_LEARN_SEP),title:String(title),order:order>=0?order:1e6+at,ids:[]};b.topics.set(tId,t);
      }
      t.ids.push(String(q.id));b.count++;s.count++;
    });
    return [...subjects.values()].sort((a,b)=>a.name.localeCompare(b.name)).map(s=>({name:s.name,count:s.count,
      banks:[...s.banks.values()].sort((a,b)=>a.name.localeCompare(b.name)).map(b=>({name:b.name,count:b.count,topics:[...b.topics.values()].sort((x,y)=>x.order-y.order)}))}));
  }
  function nkLearnKeys(s,b){return (b?[b]:s.banks).flatMap(bank=>bank.topics.map(t=>t.key));}
  function nkLearnPickState(keys){const on=keys.filter(k=>nkLearn.picked.has(k)).length;return on===0?'off':on===keys.length?'on':'mixed';}
  function nkLearnCheck(st){return `<span class="nk-learn-check is-${st}" aria-hidden="true">${st==='on'?navIcon('check',13):''}</span>`;}
  function nkLearnPool(){
    const ids=[];
    nkLearn.tree.forEach(s=>s.banks.forEach(b=>b.topics.forEach(t=>{if(!nkLearn.picked.size||nkLearn.picked.has(t.key))ids.push(...t.ids);})));
    return ids;
  }
  function nkLearnTarget(){const plan=nkTodayPlanData();return {plan,left:plan.steps[2].left,extra:plan.steps[2].left===0};}
  function nkLearnListMarkup(){
    const q=nkLearn.query.trim().toLowerCase();
    const rows=nkLearn.tree.map((s,si)=>{
      const keys=nkLearnKeys(s),open=q||nkLearn.open.has(s.name);
      const banks=s.banks.map((b,bi)=>{
        const topics=b.topics.map((t,ti)=>({t,ti})).filter(({t})=>!q||t.title.toLowerCase().includes(q)||s.name.toLowerCase().includes(q));
        if(!topics.length)return '';
        const bankHead=s.banks.length>1||b.name?`<button type="button" class="nk-learn-bank" role="checkbox" aria-checked="${{on:'true',off:'false',mixed:'mixed'}[nkLearnPickState(nkLearnKeys(s,b))]}" onclick="window.QB.nkLearnToggle(${si},${bi})">${nkLearnCheck(nkLearnPickState(nkLearnKeys(s,b)))}<span>${esc(b.name||'Questions')}</span><small>${fmtNum(b.count)} new</small></button>`:'';
        return bankHead+topics.map(({t,ti})=>{const st=nkLearn.picked.has(t.key)?'on':'off';return `<button type="button" class="nk-learn-topic" role="checkbox" aria-checked="${st==='on'}" onclick="window.QB.nkLearnToggle(${si},${bi},${ti})">${nkLearnCheck(st)}<span>${esc(t.title)}</span><small>${fmtNum(t.ids.length)}</small></button>`;}).join('');
      }).join('');
      if(q&&!banks)return '';
      const st=nkLearnPickState(keys);
      return `<div class="nk-learn-subj${open?' is-open':''}"><div class="nk-learn-subj-row"><button type="button" class="nk-learn-subj-pick" role="checkbox" aria-checked="${{on:'true',off:'false',mixed:'mixed'}[st]}" onclick="window.QB.nkLearnToggle(${si})">${nkLearnCheck(st)}<span><strong>${esc(s.name)}</strong><small>${fmtNum(s.count)} new${st==='mixed'?` · ${fmtNum(keys.filter(k=>nkLearn.picked.has(k)).length)} topics picked`:''}</small></span></button><button type="button" class="nk-learn-expand" aria-expanded="${Boolean(open)}" aria-label="${open?'Hide':'Show'} ${esc(s.name)} topics" onclick="window.QB.nkLearnExpand(${si})">${navIcon('chevron',18)}</button></div>${open?`<div class="nk-learn-topics">${banks}</div>`:''}</div>`;
    }).join('');
    return rows||`<p class="nk-learn-none">No topic matches “${esc(nkLearn.query)}”.</p>`;
  }
  function nkLearnHeadMarkup(){
    const {plan,left,extra}=nkLearnTarget(),fill=Math.min(100,Math.round(plan.fresh/Math.max(1,plan.goal)*100));
    return `<div class="nk-learn-progress"><p><b>${fmtNum(plan.fresh)}</b> of ${fmtNum(plan.goal)} new today${extra?' · goal met':` · ${fmtNum(left)} to go`}</p><span class="nk-today-bar" aria-hidden="true"><i style="--nk-today-fill:${fill}%"></i></span></div>`;
  }
  function nkLearnGoalMarkup(){
    const goal=nkTodayGoal(),custom=!NK_GOAL_CHOICES.includes(goal);
    return `<div class="nk-exam-chips nk-learn-goal" role="radiogroup" aria-label="Daily goal">${NK_GOAL_CHOICES.map(n=>`<button type="button" role="radio" aria-checked="${goal===n}" class="${goal===n?'is-selected':''}" onclick="window.QB.nkLearnSetGoal(${n})">${n}</button>`).join('')}<label class="nk-learn-goal-own${custom?' is-selected':''}"><span class="nk-sr">Your own daily goal</span><input type="number" inputmode="numeric" min="1" max="2000" step="1" placeholder="Own" value="${custom?goal:''}" onchange="window.QB.nkLearnSetGoal(this.value)"></label></div>`;
  }
  function nkLearnFootMarkup(){
    const {left,extra}=nkLearnTarget(),pool=nkLearnPool().length,want=extra?NK_TODAY_NEW:left,n=Math.min(want,pool);
    const scope=nkLearn.picked.size?`${fmtNum(nkLearn.picked.size)} topic${nkLearn.picked.size===1?'':'s'} · ${fmtNum(pool)} new`:`Every subject · ${fmtNum(pool)} new`;
    return `<div class="nk-learn-scope"><span>${esc(scope)}</span>${nkLearn.picked.size?`<button type="button" onclick="window.QB.nkLearnClear()">Clear</button>`:''}</div>
      <button type="button" class="nk-qs-start nk-learn-start" id="nk-learn-start" onclick="window.QB.nkLearnStart()"${n?'':' disabled'}>${n?`${extra?'Learn':'Start'} ${fmtNum(n)} new question${n===1?'':'s'}`:'No new questions here'}</button>`;
  }
  function nkLearnPaint(part){
    const sheet=document.getElementById('nk-learn-sheet');if(!sheet||!nkLearn)return;
    const put=(sel,html)=>{const node=sheet.querySelector(sel);if(node)node.innerHTML=html;};
    if(!part||part==='head'){put('.nk-learn-head',nkLearnHeadMarkup());put('.nk-learn-goal-wrap',nkLearnGoalMarkup());}
    if(!part||part==='list')put('.nk-learn-list',nkLearnListMarkup());
    put('.nk-learn-foot',nkLearnFootMarkup());
    sheet.querySelectorAll('.nk-learn-order button').forEach(b=>{const on=b.dataset.order===nkLearn.order;b.classList.toggle('is-selected',on);b.setAttribute('aria-checked',String(on));});
  }
  function nkLearnOpen(){
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test first.','bad');return false;}
    const saved=state.todayLearn||{},tree=nkLearnTree();
    const valid=new Set(tree.flatMap(s=>nkLearnKeys(s)));
    nkLearn={tree,picked:new Set((saved.keys||[]).filter(k=>valid.has(k))),open:new Set(),query:'',order:saved.order==='shuffle'?'shuffle':'order',dirty:false};
    nkLearn.picked.forEach(k=>nkLearn.open.add(k.split(NK_LEARN_SEP)[0]));
    document.getElementById('nk-learn-sheet')?.remove();
    document.body.insertAdjacentHTML('beforeend',`<div class="nk-qs-backdrop nk-learn-backdrop" id="nk-learn-sheet" onclick="if(event.target===this)window.QB.nkLearnClose()" onkeydown="if(event.key==='Escape'){event.stopPropagation();window.QB.nkLearnClose()}">
      <section class="nk-qs nk-learn-sheet" role="dialog" aria-modal="true" aria-labelledby="nk-learn-title">
        <span class="nk-qs-grip" aria-hidden="true"></span>
        <div class="nk-qs-head"><div><h2 id="nk-learn-title">New questions</h2><div class="nk-learn-head">${nkLearnHeadMarkup()}</div></div><button type="button" class="nk-qs-close nk-modal-close" aria-label="Close" onclick="window.QB.nkLearnClose()">${navIcon('close',20)}</button></div>
        <h3>Daily goal</h3>
        <div class="nk-learn-goal-wrap">${nkLearnGoalMarkup()}</div>
        <h3>What to learn</h3>
        <label class="nk-learn-search">${navIcon('search',16)}<span class="nk-sr">Find a topic</span><input type="search" placeholder="Find a subject or topic" autocomplete="off" oninput="window.QB.nkLearnSearch(this.value)"></label>
        <div class="nk-learn-list">${nkLearnListMarkup()}</div>
        <div class="nk-learn-order" role="radiogroup" aria-label="Question order">${[['order','In order'],['shuffle','Shuffled']].map(([k,l])=>`<button type="button" role="radio" data-order="${k}" aria-checked="${nkLearn.order===k}" class="${nkLearn.order===k?'is-selected':''}" onclick="window.QB.nkLearnSetOrder('${k}')">${l}</button>`).join('')}</div>
        <div class="nk-learn-foot">${nkLearnFootMarkup()}</div>
      </section></div>`);
    document.querySelector('#nk-learn-sheet .nk-qs-close')?.focus({preventScroll:true});
    return true;
  }
  function nkLearnClose(){
    const dirty=nkLearn?.dirty;document.getElementById('nk-learn-sheet')?.remove();nkLearn=null;
    if(dirty&&route?.page==='dashboard'&&typeof render==='function')render();
    document.querySelector('.nk-today-learn')?.focus?.({preventScroll:true});
  }
  function nkLearnToggle(si,bi,ti){
    if(!nkLearn)return;const s=nkLearn.tree[si];if(!s)return;
    const keys=ti!==undefined?[s.banks[bi]?.topics[ti]?.key].filter(Boolean):nkLearnKeys(s,bi!==undefined?s.banks[bi]:null);
    const on=keys.every(k=>nkLearn.picked.has(k));
    keys.forEach(k=>on?nkLearn.picked.delete(k):nkLearn.picked.add(k));
    nkLearnPaint('list');
  }
  function nkLearnExpand(si){
    if(!nkLearn)return;const s=nkLearn.tree[si];if(!s)return;
    nkLearn.open.has(s.name)?nkLearn.open.delete(s.name):nkLearn.open.add(s.name);nkLearnPaint('list');
  }
  function nkLearnSearch(value){if(!nkLearn)return;nkLearn.query=String(value||'');nkLearnPaint('list');}
  function nkLearnClear(){if(!nkLearn)return;nkLearn.picked.clear();nkLearnPaint('list');}
  function nkLearnSetOrder(order){if(!nkLearn)return;nkLearn.order=order==='shuffle'?'shuffle':'order';nkLearnPaint('foot');}
  function nkLearnSetGoal(value){
    const n=Math.round(Number(value));
    if(!Number.isFinite(n)||n<1){showToast('Set a goal of at least 1 question.','bad');if(nkLearn)nkLearnPaint('head');return false;}
    state.studyGoals={...(state.studyGoals||{}),newPerDay:Math.min(2000,n)};saveState();
    if(nkLearn){nkLearn.dirty=true;nkLearnPaint('head');}
    else if(route?.page==='dashboard'&&typeof render==='function')render();
    return true;
  }
  function nkLearnStart(){
    if(!nkLearn)return false;
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test first.','bad');return false;}
    const {left,extra}=nkLearnTarget(),pool=nkLearnPool(),want=extra?NK_TODAY_NEW:left;
    if(!pool.length||!want){showToast('No new questions here.');return false;}
    if(nkLearn.order==='shuffle')for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]];}
    const ids=pool.slice(0,want),picked=[...nkLearn.picked];
    const subjects=[...new Set(picked.map(k=>k.split(NK_LEARN_SEP)[0]))];
    const title=!picked.length?'New questions':picked.length===1?`New · ${nkLearn.tree.flatMap(s=>s.banks.flatMap(b=>b.topics)).find(t=>t.key===picked[0])?.title||subjects[0]}`:subjects.length===1?`New · ${subjects[0]}`:`New · ${fmtNum(picked.length)} topics`;
    state.todayLearn={keys:picked,order:nkLearn.order};
    const rows=ids.map(id=>nkFindStudyQuestion(id)).filter(Boolean);
    document.getElementById('nk-learn-sheet')?.remove();nkLearn=null;
    BY_ID={...BY_ID,...Object.fromEntries(rows.map(q=>[String(q.id),q]))};
    startSession(rows.map(q=>String(q.id)),'practice',title,'normal');
    return true;
  }
  // A quiet word when today's goal is reached, wherever the new question was answered.
  let nkTodayGoalToastDay=0;
  if(typeof submitPractice==='function'){
    const nkTodayOriginalSubmit=submitPractice;
    submitPractice=function(){
      const s=state.activeSession,qid=s?.mode==='practice'?String(s.questionIds?.[s.index]??''):'';
      const wasNew=qid&&!nkTodayAttempts(qid).length;
      const out=nkTodayOriginalSubmit.apply(this,arguments);
      try{
        const day=nkTodayStart();
        if(wasNew&&nkTodayGoalToastDay!==day&&nkTodayAttempts(qid).length){
          const goal=nkTodayGoal(),fresh=nkTodayCounts().fresh;
          if(fresh===goal){nkTodayGoalToastDay=day;showToast(`Daily goal reached · ${fmtNum(fresh)} new questions today`);}
        }
      }catch(_error){}
      return out;
    };
  }
  /* NK_TODAY_PLAN_V1_END */
