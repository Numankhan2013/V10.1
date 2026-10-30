  /* NK_MEMORY_INSIGHTS_V1_START */
  // Subject focus on Insights (weakest subject, subjects gone quiet) and the FSRS
  // insights page. Every action launches the shared Revision queues or Practice,
  // so pause/resume, the daily review cap and result routing stay owned there.
  const NK_FOCUS_WINDOW_DAYS=30,NK_FOCUS_MIN_ANSWERS=10,NK_QUIET_DAYS=14,NK_MEMORY_DAY=86400000,NK_MEMORY_MATURE_DAYS=21;
  let nkMemoryGroup='',nkMemoryForecastDay=-1;
  function nkMemoryIcon(group,size){return nkAppSubjectIcon(group==='UWorld'?'UWorld · ':group,size);}
  function nkMemoryDays(from,to){return Math.round((nkLearningDay(to)-nkLearningDay(from))/NK_MEMORY_DAY);}
  function nkMemoryAgo(days){return days<=0?'today':days===1?'yesterday':`${fmtNum(days)} days ago`;}
  // A group is a subject, or every UWorld collection together (as in the bars).
  function nkFocusScope(group,bank=''){
    if(group==='UWorld')return {subject:'',bank:'UWorld',topic:''};
    return {subject:String(group||''),bank:bank==='UWorld'?'':String(bank||''),topic:''};
  }
  function nkFocusQueues(group,bank){const data=nkRevisionDeskData(nkFocusScope(group,bank));return {mistakes:data.wrong.length,due:data.dueCards.length};}

  /* ---------------------------------------------------------------- Subject focus */
  function nkFocusData(model,now=Date.now()){
    const since=now-NK_FOCUS_WINDOW_DAYS*NK_MEMORY_DAY,groups=new Map();let total=0,correct=0;
    model.data.events.forEach(a=>{
      if(!nkLearningMatches(a.q)||a.at>now)return;
      const subject=nkLearningSubjectGroup(a.q);let row=groups.get(subject);
      if(!row)groups.set(subject,row={subject,last:0,total:0,correct:0});
      if(a.at>row.last)row.last=a.at;
      if(a.at>=since){row.total++;total++;if(a.correct){row.correct++;correct++;}}
    });
    const rows=[...groups.values()].map(r=>({...r,accuracy:r.total?r.correct/r.total*100:null,idle:nkMemoryDays(r.last,now)}));
    const rated=rows.filter(r=>r.total>=NK_FOCUS_MIN_ANSWERS).sort((a,b)=>a.accuracy-b.accuracy||b.total-a.total||a.subject.localeCompare(b.subject));
    // "Weakest" needs something to be weaker than.
    const weakest=rated.length>=2?rated[0]:null;
    const quiet=rows.filter(r=>r.idle>=NK_QUIET_DAYS&&r.subject!==weakest?.subject).sort((a,b)=>b.idle-a.idle||a.subject.localeCompare(b.subject));
    return {rows,rated,weakest,quiet,average:total?correct/total*100:null,studied:rows.length};
  }
  function nkFocusSection(model,now=Date.now()){
    const f=nkFocusData(model,now);
    if(!f.studied)return '';
    let weak='';
    if(f.weakest){
      const w=f.weakest,q=nkFocusQueues(w.subject,nkLearningBank),avg=f.average,arg=esc(JSON.stringify(w.subject));
      const action=q.mistakes
        ?`<button type="button" class="nk-li-focus-go" onclick="window.QB.nkFocusRevise(${arg},'wrong')">${navIcon('refresh',17)}<span>Redo ${fmtNum(q.mistakes)} mistake${q.mistakes===1?'':'s'}</span></button>`
        :`<p class="nk-li-focus-clear">${navIcon('check',16)}<span>No open mistakes in ${esc(w.subject)}</span></p>`;
      weak=`<article class="nk-li-weak" style="--subj:${nkLearningSubjectColor(w.subject)}"><div class="nk-li-weak-top"><span class="nk-li-weak-icon">${nkMemoryIcon(w.subject,22)}</span><span class="nk-li-weak-name"><strong>${esc(w.subject)}</strong><small>Weakest of ${fmtNum(f.rated.length)} subjects</small></span><b class="nk-li-weak-pct">${nkLearningPct(w.accuracy)}<small>correct</small></b></div><div class="nk-li-weak-meter" role="img" aria-label="${esc(w.subject)}: ${nkLearningPct(w.accuracy)} correct; your average is ${nkLearningPct(avg)}"><i style="width:${Math.max(2,w.accuracy)}%"></i><span style="left:${avg}%"></span></div><p class="nk-li-weak-note">${fmtNum(w.total)} answers · your average is ${nkLearningPct(avg)}</p><div class="nk-li-weak-actions">${action}<button type="button" class="nk-li-focus-topics" onclick="window.QB.nkFocusOpen(${arg})">Topics ${navIcon('chevron',15)}</button></div></article>`;
    }
    const quietRows=f.quiet.slice(0,4).map(r=>{
      const q=nkFocusQueues(r.subject,nkLearningBank),arg=esc(JSON.stringify(r.subject));
      const [verb,detail,call]=q.due?['Review',`${fmtNum(q.due)} review${q.due===1?'':'s'} due`,`window.QB.nkFocusRevise(${arg},'due')`]:q.mistakes?['Redo',`${fmtNum(q.mistakes)} mistake${q.mistakes===1?'':'s'} open`,`window.QB.nkFocusRevise(${arg},'wrong')`]:['Open','Pick a topic to pick it back up',`window.QB.nkFocusOpen(${arg})`];
      return `<li><button type="button" onclick="${call}" aria-label="${esc(r.subject)}, last practised ${nkMemoryAgo(r.idle)}. ${verb}: ${detail}"><i style="background:${nkLearningSubjectColor(r.subject)}"></i><span><strong>${esc(r.subject)}</strong><small>${nkMemoryAgo(r.idle)} · ${detail}</small></span><em>${verb}</em>${navIcon('chevron',15)}</button></li>`;
    }).join('');
    const more=f.quiet.length>4?`<p class="nk-li-quiet-more">${fmtNum(f.quiet.length-4)} more not practised for ${NK_QUIET_DAYS}+ days</p>`:'';
    const quiet=quietRows?`<div class="nk-li-quiet"><h3>Gone quiet <small>${NK_QUIET_DAYS}+ days since you practised</small></h3><ul>${quietRows}</ul>${more}</div>`:'';
    const notes=[!f.weakest?`Answer ${NK_FOCUS_MIN_ANSWERS} or more questions in two subjects within ${NK_FOCUS_WINDOW_DAYS} days to compare them.`:'',!f.quiet.length?`Everything you study has been practised in the last ${NK_QUIET_DAYS} days.`:''].filter(Boolean).map(t=>`<p class="nk-li-focus-note">${t}</p>`).join('');
    return `<section class="nk-li-focus" aria-labelledby="nk-li-focus-title"><header><h2 id="nk-li-focus-title">Subject focus</h2><span>Last ${NK_FOCUS_WINDOW_DAYS} days</span></header>${weak}${quiet}${notes}</section>`;
  }
  function nkFocusRevise(group,kind,bank=nkLearningBank){
    if(!['wrong','due'].includes(kind))return false;
    const previous=nkRevisionScope;nkRevisionScope=nkFocusScope(String(group||''),bank);
    try{return nkStartRevisionQueue(kind);}finally{nkRevisionScope=previous;}
  }
  function nkFocusOpen(group){
    if(group==='UWorld'){navigate('uworld');return;}
    if(!(SUBJECTS||[]).some(s=>s.subject===group)&&!(typeof nkBankRecords==='function'&&nkBankRecords(group).length))return;
    nkOpenSubjectLibrary(group);
  }

  /* ---------------------------------------------------------------- FSRS insights */
  const NK_MEMORY_STAGES=[['mature','Mature','Stable for 21+ days','nk-mi-is-mature'],['young','Young','Reviewed, still settling','nk-mi-is-young'],['learning','Learning','In today’s short steps','nk-mi-is-learning'],['relearning','Relearning','Forgotten, coming back','nk-mi-is-relearning'],['new','Not yet answered','Skipped in a session','nk-mi-is-new']];
  const NK_MEMORY_BUCKETS=[['<70%',0,.7,'nk-mi-is-low'],['70–80',.7,.8,'nk-mi-is-fair'],['80–90',.8,.9,'nk-mi-is-mid'],['90–95',.9,.95,'nk-mi-is-good'],['95%+',.95,2,'nk-mi-is-best']];
  function nkMemoryGroups(){const seen=new Set();nkAllStudyQuestions().forEach(q=>{if(nkFsrsEligibility(q))seen.add(nkLearningSubjectGroup(q));});return [...seen].sort((a,b)=>(a==='UWorld')-(b==='UWorld')||a.localeCompare(b));}
  function nkMemoryMedian(list){if(!list.length)return null;const s=[...list].sort((a,b)=>a-b),m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2;}
  function nkMemoryData(group=nkMemoryGroup,now=Date.now()){
    const prefs=nkFsrsPreferences(),engine=nkFsrsEngine(prefs),since=now-NK_FOCUS_WINDOW_DAYS*NK_MEMORY_DAY,today=+nkLearningDay(now);
    const stages=Object.fromEntries(NK_MEMORY_STAGES.map(s=>[s[0],0])),buckets=NK_MEMORY_BUCKETS.map(()=>0),forecast=Array(30).fill(0),bySubject=new Map();
    const comeback={recovered:0,again:0,pending:0,days:[]},hardest=[];let cards=0,due=0,recall=0,recallN=0,tests=0,passed=0;
    nkAllStudyQuestions().forEach(q=>{
      if(!nkFsrsEligibility(q))return;
      const subject=nkLearningSubjectGroup(q);if(group&&subject!==group)return;
      const id=String(q.id),r=state.reviews?.[id],v2=r?.schemaVersion===2;cards++;
      const st=!v2?'new':Number(r.state)===1?'learning':Number(r.state)===3?'relearning':Number(r.state)===2?(Number(r.stability)>=NK_MEMORY_MATURE_DAYS?'mature':'young'):'new';stages[st]++;
      // Today holds everything due now, overdue included; unscheduled cards stay out.
      const isDue=nkFsrsIsDue(r,now),at=Number(r?.due||r?.nextReviewAt||0),day=isDue?0:at?Math.max(0,Math.floor((at-today)/NK_MEMORY_DAY)):-1;
      if(isDue)due++;if(day>=0&&day<30)forecast[day]++;
      if(v2&&(st==='young'||st==='mature'||st==='relearning')&&r.lastReview){const p=Number(nkFsrsRetrievability(r,now,engine));if(Number.isFinite(p)){recall+=p;recallN++;buckets[NK_MEMORY_BUCKETS.findIndex(b=>p>=b[1]&&p<b[2])]++;}}
      const history=nkFsrsActiveAttempts(id).filter(a=>typeof a.correct==='boolean'),stamp=a=>Number(a.reviewedAt||a.at||0);
      // A recall test is an answer given at least half a day after the previous one.
      for(let i=1;i<history.length;i++){const t=stamp(history[i]);if(t<since||t>now||t-stamp(history[i-1])<NK_MEMORY_DAY/2)continue;tests++;let row=bySubject.get(subject);if(!row)bySubject.set(subject,row={subject,tests:0,passed:0});row.tests++;if(history[i].correct){passed++;row.passed++;}}
      const miss=history.findIndex(a=>a.correct===false);
      if(miss>=0){const later=history.slice(miss+1),back=later.find(a=>a.correct);if(history.at(-1).correct)comeback.recovered++;else if(later.length)comeback.again++;else comeback.pending++;if(back)comeback.days.push((stamp(back)-stamp(history[miss]))/NK_MEMORY_DAY);}
      if(v2&&Number(r.lapses)>=2)hardest.push({q,lapses:Number(r.lapses),difficulty:Number(r.difficulty||0)});
    });
    hardest.sort((a,b)=>b.lapses-a.lapses||b.difficulty-a.difficulty||String(a.q.id).localeCompare(String(b.q.id)));
    const retried=comeback.recovered+comeback.again;
    return {group,prefs,cards,due,stages,buckets,forecast,today,
      retention:tests?passed/tests*100:null,tests,target:prefs.desiredRetention*100,
      subjects:[...bySubject.values()].map(r=>({...r,retention:r.passed/r.tests*100})).sort((a,b)=>b.tests-a.tests||a.subject.localeCompare(b.subject)),
      recall:recallN?recall/recallN*100:null,recallN,comeback:{...comeback,retried,rate:retried?comeback.recovered/retried*100:null,median:nkMemoryMedian(comeback.days)},hardest:hardest.slice(0,5),hardestTotal:hardest.length};
  }
  if(typeof nkMemoByState==='function')nkMemoryData=nkMemoByState(nkMemoryData,(group=nkMemoryGroup)=>String(group));
  function nkMemoryCard(title,note,body,extra=''){return `<section class="nk-mi-card ${extra}"><header><h2>${title}</h2>${note?`<span>${note}</span>`:''}</header>${body}</section>`;}
  function nkMemoryStack(parts,label){const total=parts.reduce((s,p)=>s+p.n,0);return `<div class="nk-mi-stack" role="img" aria-label="${esc(label)}">${total?parts.filter(p=>p.n).map(p=>`<i class="${p.cls}" style="flex-grow:${p.n}"></i>`).join(''):'<i class="nk-mi-is-new" style="flex-grow:1"></i>'}</div>`;}
  function nkMemoryLegend(parts){const total=parts.reduce((s,p)=>s+p.n,0);return `<ul class="nk-mi-legend">${parts.map(p=>`<li><i class="${p.cls}"></i><span><strong>${esc(p.label)}</strong>${p.note?`<small>${esc(p.note)}</small>`:''}</span><b>${fmtNum(p.n)}</b><small>${total?Math.round(p.n/total*100):0}%</small></li>`).join('')}</ul>`;}
  function nkMemoryRetention(d){
    if(d.retention===null)return nkMemoryCard('Retention',`Last ${NK_FOCUS_WINDOW_DAYS} days`,'<p class="nk-mi-empty">Come back to a question a day or more after answering it to measure what you retain.</p>');
    const gap=d.retention-d.target,verdict=Math.abs(gap)<1?'On your target':gap>0?`${gap.toFixed(0)} points above your target`:`${Math.abs(gap).toFixed(0)} points below your target`;
    const meter=(pct,color='')=>`<div class="nk-mi-meter"${color?` style="--subj:${color}"`:''}><i style="width:${Math.max(2,pct)}%"></i><span style="left:${d.target}%" title="Target ${Math.round(d.target)}%"></span></div>`;
    const rows=!d.group&&d.subjects.length>1?`<ul class="nk-mi-subjects">${d.subjects.map(s=>`<li style="--subj:${nkLearningSubjectColor(s.subject)}"><span><i></i><strong>${esc(s.subject)}</strong></span><b>${nkLearningPct(s.retention)}</b>${meter(s.retention,nkLearningSubjectColor(s.subject))}<small>${fmtNum(s.tests)} recall${s.tests===1?'':'s'}</small></li>`).join('')}</ul>`:'';
    return nkMemoryCard('Retention',`Last ${NK_FOCUS_WINDOW_DAYS} days`,`<div class="nk-mi-hero"><b>${nkLearningPct(d.retention)}</b><span><strong>${verdict}</strong><small>${fmtNum(d.tests)} recalls · target ${Math.round(d.target)}%</small></span></div>${meter(d.retention)}${rows}`);
  }
  function nkMemoryComeback(d){
    const c=d.comeback,total=c.recovered+c.again+c.pending;
    if(!total)return nkMemoryCard('Comeback rate','','<p class="nk-mi-empty">No missed questions yet. When you miss one, this tracks whether you win it back.</p>');
    const parts=[{n:c.recovered,label:'Won back',note:'Latest answer correct',cls:'nk-mi-is-mature'},{n:c.again,label:'Missed again',note:'Retried, still wrong',cls:'nk-mi-is-relearning'},{n:c.pending,label:'Not retried yet',note:'Waiting in Mistakes',cls:'nk-mi-is-new'}];
    const head=c.rate===null?`<div class="nk-mi-hero"><b>—</b><span><strong>Retry a missed question to start</strong><small>${fmtNum(total)} missed questions</small></span></div>`:`<div class="nk-mi-hero"><b>${nkLearningPct(c.rate)}</b><span><strong>of retried misses won back</strong><small>${c.median===null?`${fmtNum(c.retried)} retried`:`Usually within ${c.median<1?'a day':`${fmtNum(Math.round(c.median))} day${Math.round(c.median)===1?'':'s'}`}`}</small></span></div>`;
    return nkMemoryCard('Comeback rate',`${fmtNum(total)} missed`,`${head}${nkMemoryStack(parts,parts.map(p=>`${p.label}: ${p.n}`).join(', '))}${nkMemoryLegend(parts)}`);
  }
  function nkMemoryStages(d){
    const parts=NK_MEMORY_STAGES.map(([key,label,note,cls])=>({n:d.stages[key],label,note,cls})).filter(p=>p.n||p.label!=='Not yet answered');
    const share=k=>d.cards?d.stages[k]/d.cards:0;
    const line=share('relearning')>=.15?`${fmtNum(d.stages.relearning)} cards are relearning after a lapse; they return sooner until they hold.`:share('mature')>=.5?'Over half your cards are mature: stable for three weeks or more.':d.stages.young+d.stages.learning>d.stages.mature?'Most cards are still settling. Steady reviews move them to mature (21+ days).':'Your cards are spread across every stage.';
    return nkMemoryCard('Stage balance',`${fmtNum(d.cards)} cards`,`${nkMemoryStack(parts,parts.map(p=>`${p.label}: ${p.n}`).join(', '))}<p class="nk-mi-line">${line}</p>${nkMemoryLegend(parts)}`);
  }
  function nkMemoryStrength(d){
    if(!d.recallN)return nkMemoryCard('Memory strength','Right now','<p class="nk-mi-empty">Strength appears once cards have been reviewed.</p>');
    const max=Math.max(1,...d.buckets),low=d.buckets[0];
    return nkMemoryCard('Memory strength','Right now',`<div class="nk-mi-hero"><b>${nkLearningPct(d.recall)}</b><span><strong>average chance of recall</strong><small>${low?`${fmtNum(low)} card${low===1?'':'s'} below 70%`:'No card below 70%'}</small></span></div><div class="nk-mi-hist" role="img" aria-label="${esc(NK_MEMORY_BUCKETS.map((b,i)=>`${b[0]}: ${d.buckets[i]} cards`).join('; '))}">${NK_MEMORY_BUCKETS.map((b,i)=>`<span><b>${fmtNum(d.buckets[i])}</b><i class="${b[3]}" style="height:${d.buckets[i]?Math.max(4,d.buckets[i]/max*72):0}px"></i><small>${b[0]}</small></span>`).join('')}</div>`);
  }
  function nkMemoryForecastLabel(d,i){const day=new Date(d.today);day.setDate(day.getDate()+i);return i===0?'Today':i===1?'Tomorrow':day.toLocaleDateString(undefined,{weekday:'short',day:'numeric',month:'short'});}
  function nkMemoryForecastReadout(d){
    const i=nkMemoryForecastDay;
    if(i>=0)return `<strong>${esc(nkMemoryForecastLabel(d,i))}</strong><span>${fmtNum(d.forecast[i])} review${d.forecast[i]===1?'':'s'}${i===0?' including overdue':''}</span>`;
    const total=d.forecast.reduce((s,n)=>s+n,0),peak=d.forecast.reduce((m,n,j)=>n>d.forecast[m]?j:m,0);
    return `<strong>${fmtNum(total)} reviews</strong><span>${total?`Busiest: ${esc(nkMemoryForecastLabel(d,peak))} (${fmtNum(d.forecast[peak])})`:'Nothing scheduled'}</span>`;
  }
  function nkMemoryForecast(d){
    const max=Math.max(1,...d.forecast),date=i=>esc(new Date(d.today+i*NK_MEMORY_DAY).toLocaleDateString(undefined,{day:'numeric',month:'short'}));
    return nkMemoryCard('Next 30 days','Tap a day',`<div class="nk-mi-forecast" role="group" aria-label="Reviews scheduled over the next 30 days">${d.forecast.map((n,i)=>`<button type="button" aria-pressed="${nkMemoryForecastDay===i}" class="${nkMemoryForecastDay===i?'is-selected':''}" aria-label="${esc(nkMemoryForecastLabel(d,i))}: ${n} reviews" onclick="window.QB.nkMemorySelectDay(${i})"><i style="height:${n?Math.max(3,n/max*88):0}px"></i></button>`).join('')}</div><div class="nk-mi-forecast-axis" aria-hidden="true"><span style="grid-column:1/span 7">Today</span><span style="grid-column:8/span 7">${date(7)}</span><span style="grid-column:15/span 7">${date(14)}</span><span class="is-end" style="grid-column:23/31">${date(29)}</span></div><p class="nk-mi-readout" role="status">${nkMemoryForecastReadout(d)}</p>`);
  }
  function nkMemoryHardest(d){
    if(!d.hardest.length)return '';
    const rows=d.hardest.map(({q,lapses})=>`<li><button type="button" onclick="window.QB.nkMemoryOpenQuestion('${encodeURIComponent(String(q.id))}')"><i style="background:${nkLearningSubjectColor(nkLearningSubjectGroup(q))}"></i><span><strong>${esc(String(q.question||'Question').replace(/\s+/g,' ').slice(0,140))}</strong><small>${esc(nkLearningSubjectGroup(q))} · forgotten ${fmtNum(lapses)} times</small></span>${navIcon('chevron',15)}</button></li>`).join('');
    return nkMemoryCard('Hardest questions',`${fmtNum(d.hardestTotal)} forgotten twice or more`,`<ul class="nk-mi-hardest">${rows}</ul><button type="button" class="nk-mi-secondary" onclick="window.QB.nkMemoryPractiseHardest()">Practise ${fmtNum(Math.min(20,d.hardestTotal))} hardest ${navIcon('chevron',16)}</button>`,'nk-mi-wide');
  }
  function nkMemoryInsightsPage(){
    const groups=nkMemoryGroups();if(nkMemoryGroup&&!groups.includes(nkMemoryGroup))nkMemoryGroup='';
    const d=nkMemoryData(nkMemoryGroup),label=nkMemoryGroup||'All subjects';
    const chips=groups.length>1?`<div class="nk-mi-chips" role="group" aria-label="FSRS insights subject">${['',...groups].map(g=>`<button type="button" aria-pressed="${g===nkMemoryGroup}" onclick="window.QB.nkMemorySetGroup(${esc(JSON.stringify(g))})">${g?`<i style="background:${nkLearningSubjectColor(g)}"></i>`:''}${esc(g||'All')}</button>`).join('')}</div>`:'';
    const summary=`<div class="nk-mi-summary"><span><b>${nkLearningPct(d.retention)}</b><small>Retention</small></span><span><b>${fmtNum(d.due)}</b><small>Due today</small></span><span><b>${fmtNum(d.cards)}</b><small>Cards</small></span></div>`;
    const queue=nkFocusQueues(nkMemoryGroup,'');
    const review=`<button type="button" class="nk-mi-primary" ${queue.due?'':'disabled'} onclick="window.QB.nkMemoryReview()">${queue.due?`Review ${fmtNum(queue.due)} due`:d.due?'Daily review limit reached':'Nothing due today'} ${queue.due?navIcon('chevron',17):''}</button>`;
    const body=d.cards?`${summary}${review}<div class="nk-mi-grid">${nkMemoryRetention(d)}${nkMemoryComeback(d)}${nkMemoryStages(d)}${nkMemoryStrength(d)}${nkMemoryForecast(d)}${nkMemoryHardest(d)}</div>`:`<div class="nk-mi-empty-page">${nkAppEmpty('refresh','Nothing in memory yet','Every question you answer is scheduled by FSRS. Answer a few and come back.')}</div>`;
    return shell(`<main class="nk-app-v114 nk-memory-insights"><button class="nk-back-link" onclick="window.QB.nav('analytics')">${navIcon('back',17)} Insights</button><header class="nk-v3-page-hero"><h1>FSRS insights</h1><p>${esc(label)} · how well reviews are sticking and what comes next.</p></header>${chips}${body}<details class="nk-li-methods nk-mi-methods"><summary>About these metrics</summary><p>Retention counts answers given at least half a day after the previous answer to the same question, over the last ${NK_FOCUS_WINDOW_DAYS} days; the target is your desired retention in FSRS settings. Comeback rate follows every question you have missed: won back means its latest answer is correct.</p><p>Stage balance uses each card’s current FSRS state; mature cards have a stability of ${NK_MEMORY_MATURE_DAYS} days or more. Memory strength is FSRS’s estimated chance you would recall each reviewed card right now. The 30-day view shows when cards fall due; today includes overdue cards, and the daily review limit still applies when you start.</p></details></main>`,'analytics');
  }
  function nkMemorySetGroup(group){const g=String(group||'');if(g&&!nkMemoryGroups().includes(g))return;nkMemoryGroup=g;nkMemoryForecastDay=-1;render();}
  function nkMemorySelectDay(i){const n=Number(i);if(!Number.isInteger(n)||n<0||n>29)return;nkMemoryForecastDay=nkMemoryForecastDay===n?-1:n;const d=nkMemoryData(nkMemoryGroup);document.querySelectorAll('.nk-mi-forecast button').forEach((b,j)=>{b.classList.toggle('is-selected',j===nkMemoryForecastDay);b.setAttribute('aria-pressed',String(j===nkMemoryForecastDay));});const out=document.querySelector('.nk-mi-readout');if(out)out.innerHTML=nkMemoryForecastReadout(d);}
  function nkMemoryReview(){return nkFocusRevise(nkMemoryGroup,'due','');}
  function nkMemoryStart(ids,title){
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test before starting Practice.','bad');return false;}
    const rows=ids.map(id=>nkFindStudyQuestion(id)).filter(Boolean);if(!rows.length){showToast('These questions are unavailable.','bad');return false;}
    BY_ID={...BY_ID,...Object.fromEntries(rows.map(q=>[String(q.id),q]))};
    startSession(rows.map(q=>String(q.id)),'practice',title,'normal');
    return true;
  }
  function nkMemoryOpenQuestion(encoded){let id;try{id=decodeURIComponent(encoded);}catch{return false;}if(!nkMemoryData(nkMemoryGroup).hardest.some(h=>String(h.q.id)===id))return false;return nkMemoryStart([id],'Hardest question');}
  function nkMemoryPractiseHardest(){
    const pool=[];nkAllStudyQuestions().forEach(q=>{const r=state.reviews?.[String(q.id)];if(r?.schemaVersion===2&&Number(r.lapses)>=2&&nkFsrsEligibility(q)&&(!nkMemoryGroup||nkLearningSubjectGroup(q)===nkMemoryGroup))pool.push({id:String(q.id),lapses:Number(r.lapses),difficulty:Number(r.difficulty||0)});});
    pool.sort((a,b)=>b.lapses-a.lapses||b.difficulty-a.difficulty||a.id.localeCompare(b.id));
    return nkMemoryStart(pool.slice(0,20).map(p=>p.id),'Hardest questions');
  }
  // The FSRS Review page links to the same insights.
  if(typeof nkFsrsReviewPage==='function'){
    const nkMemoryOriginalFsrs=nkFsrsReviewPage;
    nkFsrsReviewPage=function(){return nkMemoryOriginalFsrs().replace('</header>',`</header><button type="button" class="nk-li-link nk-mi-entry" onclick="window.QB.nav('fsrs-insights')">FSRS insights ${navIcon('chevron',16)}</button>`);};
  }
  /* NK_MEMORY_INSIGHTS_V1_END */
