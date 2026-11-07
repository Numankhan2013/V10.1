  /* NK_LEARNING_INSIGHTS_V1_START */
  let nkLearningPeriod='week',nkLearningOffset=0,nkLearningSubject='',nkLearningBank='',nkLearningTopicMode='needs',nkLearningBin=-1,nkLearningHeatYear='rolling',nkLearningFocusSubject='';
  let nkLearningNoShell=false,nkLearningMetric='attempts';
  const NK_LEARNING_REVIEW_SOURCES=new Set(['fsrs-review','spaced-review']);
  function nkLearningNumber(value){const n=Number(value);return Number.isFinite(n)?Math.max(0,n):0;}
  function nkLearningDay(date){const d=new Date(date);d.setHours(0,0,0,0);return d;}
  function nkLearningShift(date,days){const d=new Date(date);d.setDate(d.getDate()+days);return d;}
  function nkLearningStart(date,period){const d=nkLearningDay(date);if(period==='week')d.setDate(d.getDate()-(d.getDay()+6)%7);else if(period==='month')d.setDate(1);else {d.setMonth(0,1);}return d;}
  function nkLearningAdvance(date,period,n){const d=new Date(date);if(period==='week')d.setDate(d.getDate()+7*n);else if(period==='month')d.setMonth(d.getMonth()+n,1);else d.setFullYear(d.getFullYear()+n,0,1);return d;}
  function nkLearningRange(now=Date.now(),period=nkLearningPeriod,offset=nkLearningOffset){
    const start=nkLearningAdvance(nkLearningStart(now,period),period,Math.min(0,offset)),end=nkLearningAdvance(start,period,1),previous=nkLearningAdvance(start,period,-1),cut=new Date(Math.min(Number(end),now+1));
    // Compare the same local calendar position, including DST and short months.
    let previousCut=new Date(start);
    if(cut<end){
      if(period==='week'){const days=Math.round((Date.UTC(cut.getFullYear(),cut.getMonth(),cut.getDate())-Date.UTC(start.getFullYear(),start.getMonth(),start.getDate()))/86400000);previousCut=nkLearningShift(previous,days);}
      else if(period==='month')previousCut=new Date(previous.getFullYear(),previous.getMonth(),Math.min(cut.getDate(),new Date(previous.getFullYear(),previous.getMonth()+1,0).getDate()));
      else previousCut=new Date(previous.getFullYear(),cut.getMonth(),Math.min(cut.getDate(),new Date(previous.getFullYear(),cut.getMonth()+1,0).getDate()));
      previousCut.setHours(cut.getHours(),cut.getMinutes(),cut.getSeconds(),cut.getMilliseconds());
    }
    const bins=[];
    if(period==='year'){for(let i=0;i<12;i++)bins.push({start:new Date(start.getFullYear(),i,1),end:new Date(start.getFullYear(),i+1,1),label:new Date(start.getFullYear(),i,1).toLocaleDateString(undefined,{month:'short'}),previousStart:new Date(previous.getFullYear(),i,1),previousEnd:new Date(previous.getFullYear(),i+1,1)});}
    else if(period==='month'){for(let i=0;i<31;i+=7){const a=nkLearningShift(start,i);if(a>=end)break;bins.push({start:a,end:new Date(Math.min(Number(nkLearningShift(a,7)),Number(end))),label:i===0?'1–7':`${i+1}–${Math.min(i+7,new Date(end-1).getDate())}`,previousStart:nkLearningShift(previous,Math.min(i,new Date(start-1).getDate())),previousEnd:new Date(Math.min(Number(nkLearningShift(previous,i+7)),Number(start)))});}}
    else for(let i=0;i<7;i++)bins.push({start:nkLearningShift(start,i),end:nkLearningShift(start,i+1),label:nkLearningShift(start,i).toLocaleDateString(undefined,{weekday:'short'}),previousStart:nkLearningShift(previous,i),previousEnd:nkLearningShift(previous,i+1)});
    return {period,start:+start,end:+end,cut:+cut,previous:+previous,previousCut:Math.min(+start,+previousCut),partial:cut<end,bins};
  }
  function nkLearningDate(at){return new Date(at).toLocaleDateString(undefined,{day:'numeric',month:'short'});}
  function nkLearningRangeLabel(range){return range.period==='year'?String(new Date(range.start).getFullYear()):range.period==='month'?new Date(range.start).toLocaleDateString(undefined,{month:'long',year:'numeric'}):`${nkLearningDate(range.start)} – ${nkLearningDate(range.end-1)}`;}
  function nkLearningTime(ms){const minutes=Math.floor(nkLearningNumber(ms)/60000);return minutes>=60?`${Math.floor(minutes/60)}h ${minutes%60}m`:minutes?`${minutes}m`:ms>0?'<1m':'0m';}
  function nkLearningPct(value){return value===null?'—':`${Math.round(value)}%`;}
  function nkLearningDelta(current,previous,points=false){if(current===null||previous===null)return '<span class="nk-li-delta is-neutral">No comparison yet</span>';if(!previous&&!points)return `<span class="nk-li-delta is-neutral">${current?'New activity':'No change'}</span>`;const diff=points?current-previous:(current-previous)/previous*100;return `<span class="nk-li-delta ${diff>0?'is-up':diff<0?'is-down':'is-neutral'}">${diff>0?'↑ ':diff<0?'↓ ':''}${Math.abs(diff)<.05?'No change':`${Math.abs(diff).toFixed(points?1:0)}${points?' pp':'%'}`}</span>`;}
  function nkLearningCollect(){
    const questions=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),events=[],histories=new Map(),seen=new Set();
    questions.forEach((q,qid)=>{
      const history=nkFsrsActiveAttempts(qid).filter(a=>typeof a.correct==='boolean'&&!a.isUndo&&!a.isRatingRevision);
      const rows=[];
      history.forEach((a,index)=>{const at=Number(a.reviewedAt||a.at||0),key=`${qid}:${a.id||`${at}:${index}`}`;if(!Number.isFinite(at)||at<=0||seen.has(key))return;seen.add(key);const row={...a,qid,q,at,timeSpent:nkLearningNumber(a.timeSpent),key};events.push(row);rows.push(row);});
      histories.set(qid,rows);
    });
    events.sort((a,b)=>a.at-b.at||a.key.localeCompare(b.key));
    const tests=[...new Map((state.tests||[]).filter(t=>t&&!t.isDeleted&&Number(t.createdAt)>0).map(t=>[String(t.id),t])).values()].sort((a,b)=>Number(a.createdAt)-Number(b.createdAt));
    const timeEvents=[],skips=[],matched=new Set();
    // A saved session replaces its own answer timing, never adds a second copy.
    // Old results predate session IDs: match one latest retrieval per answered ID.
    tests.forEach(t=>{
      const at=Number(t.createdAt),ids=[...new Set((t.questionIds||[]).map(String))],known=ids.filter(id=>questions.has(id));
      if(!known.length)return;
      const candidates=[];
      known.forEach(id=>{
        if(!Number(t.answers?.[id])){skips.push({qid:id,q:questions.get(id),at});return;}
        const candidate=(histories.get(id)||[]).filter(a=>!matched.has(a.key)&&a.at<=at&&Number(a.selected)===Number(t.answers[id])&&(t.sessionId?String(a.sessionId)===String(t.sessionId):t.kind==='practice'?a.source!=='exam':a.source==='exam')).at(-1);
        if(candidate)candidates.push(candidate);
      });
      candidates.forEach(a=>matched.add(a.key));
      const weights=known.map(id=>nkLearningNumber(t.questionTimes?.[id])),weightTotal=weights.reduce((a,b)=>a+b,0),total=t.totalTimeMs==null?weightTotal:nkLearningNumber(t.totalTimeMs);
      known.forEach((id,i)=>timeEvents.push({qid:id,q:questions.get(id),at,ms:total*(weightTotal?weights[i]/weightTotal:1/known.length),source:t.kind==='practice'?'practice':'exam',session:String(t.id)}));
    });
    events.filter(a=>!matched.has(a.key)).forEach(a=>timeEvents.push({qid:a.qid,q:a.q,at:a.at,ms:a.timeSpent,source:a.source,session:a.sessionId||''}));
    return {questions,events,histories,tests,timeEvents,skips};
  }
  function nkLearningMatches(q){return (!nkLearningSubject||q.subject===nkLearningSubject)&&(!nkLearningBank||q.bank===nkLearningBank);}
  function nkLearningSummarize(data,start,end){
    const inRange=a=>a.at>=start&&a.at<end&&nkLearningMatches(a.q),events=data.events.filter(inRange),skips=data.skips.filter(inRange),times=data.timeEvents.filter(inRange),correct=events.filter(a=>a.correct).length,incorrect=events.length-correct,review=events.filter(a=>NK_LEARNING_REVIEW_SOURCES.has(a.source)),reviewCorrect=review.filter(a=>a.correct).length;
    const modules=(state.studyModules||[]).filter(m=>!m.isDeleted&&(m.questionIds||[]).some(id=>data.questions.has(String(id))&&nkLearningMatches(data.questions.get(String(id)))));
    const completed=modules.filter(m=>m.isCompleted&&Number(m.completedAt)>=start&&Number(m.completedAt)<end).length;
    const missedIds=new Set(events.filter(a=>!a.correct).map(a=>a.qid));let corrected=0;
    missedIds.forEach(id=>{const latest=(data.histories.get(id)||[]).filter(a=>a.at<end).at(-1);if(latest?.correct)corrected++;});
    return {events,skips,times,correct,incorrect,attempts:events.length,unique:new Set(events.map(a=>a.qid)).size,skipped:skips.length,accuracy:events.length?correct/events.length*100:null,time:times.reduce((s,t)=>s+t.ms,0),reviews:review.length,reviewAccuracy:review.length?reviewCorrect/review.length*100:null,completed,missed:missedIds.size,corrected,modules};
  }
  function nkLearningForecast(data,now){
    const today=nkLearningDay(now),days=Array.from({length:8},(_,i)=>nkLearningShift(today,i)),counts=Array(7).fill(0);let due=0,total=0;
    data.questions.forEach(q=>{if(!nkLearningMatches(q)||!nkFsrsEligibility(q))return;total++;const r=state.reviews?.[q.id],at=Number(r?.due||r?.nextReviewAt||0);if(typeof nkFsrsIsDue==='function'?nkFsrsIsDue(r,now):(!at||at<=now))due++;if(!at||at<+days[1])counts[0]++;else {const i=days.findIndex((day,index)=>index<7&&at>=+day&&at<+days[index+1]);if(i>=0)counts[i]++;}});
    return {counts,due,total,days};
  }
  function nkLearningModel(now=Date.now()){
    const data=nkLearningCollect(),range=nkLearningRange(now),current=nkLearningSummarize(data,range.start,range.cut),previous=nkLearningSummarize(data,range.previous,range.previousCut);
    const bins=range.bins.map(b=>({...b,active:+b.start<range.cut,current:nkLearningSummarize(data,+b.start,Math.min(+b.end,range.cut)),previous:nkLearningSummarize(data,+b.previousStart,Math.min(+b.previousEnd,range.previousCut))}));
    const meta=new Map();nkModuleBankRecords().forEach(r=>nkModuleTopics(r).forEach(t=>meta.set(JSON.stringify([r.subject,nkModuleBankName(r),String(t.id)]),t.title||t.name||String(t.id))));
    const topics=new Map();current.events.forEach(a=>{const key=JSON.stringify([a.q.subject,a.q.bank,String(a.q.chapterId)]);if(!topics.has(key))topics.set(key,{key,subject:a.q.subject,bank:a.q.bank,topicId:String(a.q.chapterId),title:meta.get(key)||a.q.chapter||'Topic',correct:0,total:0,unique:new Set()});const row=topics.get(key);row.total++;row.correct+=a.correct?1:0;row.unique.add(a.qid);});
    const topicRows=[...topics.values()].map(t=>({...t,accuracy:t.correct/t.total*100}));
    const subjects=[...new Set([...data.questions.values()].filter(nkLearningMatches).map(q=>q.subject))].map(subject=>{const all=current.events.filter(a=>a.q.subject===subject),last=previous.events.filter(a=>a.q.subject===subject);return {subject,total:all.length,correct:all.filter(a=>a.correct).length,accuracy:all.length?all.filter(a=>a.correct).length/all.length*100:null,previous:last.length?last.filter(a=>a.correct).length/last.length*100:null};});
    const activeDays=new Set(current.events.map(a=>dayKey(a.at))).size;
    const unresolved=[...data.histories.values()].filter(h=>h.length&&nkLearningMatches(h.at(-1).q)&&h.at(-1).correct===false).length;
    return {data,range,current,previous,bins,topicRows,subjects,activeDays,unresolved,forecast:nkLearningForecast(data,now)};
  }
  function nkLearningPeriodLabels(model){
    const unit=model.range.period;
    if(nkLearningOffset===0)return {current:`This ${unit}`,previous:`Previous ${unit}`};
    const r=model.range;
    return {current:nkLearningRangeLabel(r),previous:nkLearningRangeLabel({...r,start:r.previous,end:r.start})};
  }
  // The four headline measures. The selected one drives the main chart (dashboard pattern: tiles pick the metric).
  const NK_LI_METRICS={
    attempts:{label:'Questions practised',unit:['answer','answers'],value:s=>s.attempts,plot:s=>s.attempts,format:n=>fmtNum(n),small:5},
    accuracy:{label:'Accuracy',unit:['%','%'],value:s=>s.accuracy,plot:s=>s.accuracy,format:n=>nkLearningPct(n),points:true},
    time:{label:'Study time',unit:['min','min'],value:s=>s.time,plot:s=>s.time/60000,format:ms=>nkLearningTime(ms),small:5*60000},
    reviews:{label:'FSRS reviews',unit:['review','reviews'],value:s=>s.reviews,plot:s=>s.reviews,format:n=>fmtNum(n),small:5}
  };
  // A change with what it compares to; a tiny base reads "was N" in grey instead of a loud percentage.
  function nkLearningVs(key,current,previous,label){
    const m=NK_LI_METRICS[key],cur=m.value(current),prev=m.value(previous),lower=String(label||'').toLowerCase();
    if(cur===null||cur===undefined)return '<span class="nk-li-vs is-neutral">No answers yet</span>';
    if(prev===null||prev===undefined)return `<span class="nk-li-vs is-neutral">Nothing ${esc(lower)}</span>`;
    if(m.points){const d=cur-prev;return Math.abs(d)<.5?`<span class="nk-li-vs is-neutral">Same as ${esc(lower)}</span>`:`<span class="nk-li-vs ${d>0?'is-up':'is-down'}">${d>0?'+':'−'}${Math.abs(d).toFixed(0)} pts vs ${esc(lower)}</span>`;}
    if(prev<m.small)return `<span class="nk-li-vs is-neutral">was ${esc(m.format(prev))}</span>`;
    const pct=(cur-prev)/prev*100;
    if(Math.abs(pct)<.5)return `<span class="nk-li-vs is-neutral">Same as ${esc(lower)}</span>`;
    return `<span class="nk-li-vs ${pct>0?'is-up':'is-quiet'}">${pct>0?'+':'−'}${Math.abs(pct)>999?'999+':Math.round(Math.abs(pct))}% vs ${esc(lower)}</span>`;
  }
  function nkLearningNiceMax(max,unit=''){
    if(unit==='min'&&max>60){const h=nkLearningNiceMax(max/60);return h*60;}
    if(max<=2)return 2;const step=Math.pow(10,Math.floor(Math.log10(max))),n=max/step;return (n<=1?1:n<=2?2:n<=5?5:10)*step;
  }
  function nkLearningKpis(model){
    const labels=nkLearningPeriodLabels(model);
    return `<div class="nk-li-kpis" role="group" aria-label="Choose what the chart shows">${Object.entries(NK_LI_METRICS).map(([key,m])=>{const v=m.value(model.current);return `<button type="button" class="nk-li-kpi" data-metric="${m.label}" aria-pressed="${nkLearningMetric===key}" onclick="window.QB.nkLearningSetMetric('${key}')"><small>${m.label}</small><b>${v===null?'—':m.format(v)}</b>${nkLearningVs(key,model.current,model.previous,labels.previous)}</button>`;}).join('')}</div>`;
  }
  function nkLearningSetMetric(key){if(!NK_LI_METRICS[key]||key===nkLearningMetric)return;const keep=document.activeElement?.classList?.contains('nk-li-kpi');nkLearningMetric=key;nkLearningBin=-1;nkLearningFocusSubject='';nkLearningRefresh();if(keep)document.querySelector(`.nk-li-kpi[data-metric="${NK_LI_METRICS[key].label}"]`)?.focus({preventScroll:true});}
  // Dragging across the chart picks the bar under the finger, so narrow bars stay easy to read on a phone.
  function nkLearningScrub(event){
    if(!event||(event.pointerType==='mouse'&&!event.buttons))return;
    const box=event.currentTarget?.getBoundingClientRect?.(),n=event.currentTarget?.children?.length||0;if(!box||!box.width||!n)return;
    const i=Math.max(0,Math.min(n-1,Math.floor((event.clientX-box.left)/box.width*n)));
    if(i!==nkLearningBin)nkLearningSelectBin(i);
  }
  function nkLearningCard(title,body,extra='',action=''){return `<section class="nk-li-card ${extra}"><header><h2>${title}</h2>${action}</header>${body}</section>`;}
  function nkLearningEmpty(message='No activity in this period yet.'){return `<p class="nk-li-empty">${message}</p>`;}
  // Bars split by subject in each subject's theme colour; UWorld collections share one grey band.
  function nkLearningSubjectGroup(q){const subject=String(q?.subject||'');return q?.bank==='UWorld'||/^UWorld\b/.test(subject)?'UWorld':subject||'Other';}
  function nkLearningSubjectColor(subject){const key=subject==='UWorld'?'uworld':nkAppSubjectMeta(subject).key;return `var(--nkg-subj-${key},var(--nkg-subj-uworld,#8a8a8a))`;}
  function nkLearningSubjectSplit(events){const rows=new Map();events.forEach(a=>{const subject=nkLearningSubjectGroup(a.q),row=rows.get(subject)||{subject,total:0,correct:0};row.total++;if(a.correct)row.correct++;rows.set(subject,row);});return [...rows.values()].sort((a,b)=>b.total-a.total||a.subject.localeCompare(b.subject));}
  function nkLearningSplitRows(rows,total){return `<ul class="nk-li-split">${rows.map(r=>`<li class="${nkLearningFocusSubject===r.subject?'is-focus':''}"><i style="background:${nkLearningSubjectColor(r.subject)}"></i><span>${esc(r.subject)}</span><b>${fmtNum(r.total)}</b><small>${total?Math.round(r.total/total*100):0}% of answers · ${nkLearningPct(r.correct/r.total*100)} correct</small></li>`).join('')}</ul>`;}
  function nkLearningBarChart(model){
    const m=NK_LI_METRICS[nkLearningMetric],labels=nkLearningPeriodLabels(model),stacked=nkLearningMetric==='attempts';
    const plot=b=>{const v=m.plot(b);return v===null||v===undefined?null:v;};
    const max=m.points?100:nkLearningNiceMax(Math.max(0,...model.bins.flatMap(b=>[plot(b.current)||0,plot(b.previous)||0])),nkLearningMetric==='time'?'min':'');
    const pct=v=>v?Math.max(1.5,Math.min(100,v/max*100)).toFixed(1):'0';
    const order=nkLearningSubjectSplit(model.current.events);
    if(nkLearningFocusSubject&&!order.some(r=>r.subject===nkLearningFocusSubject))nkLearningFocusSubject='';
    const stack=b=>{const counts=new Map(nkLearningSubjectSplit(b.current.events).map(r=>[r.subject,r.total]));return order.filter(r=>counts.get(r.subject)).map(r=>`<span data-li-subject="${esc(r.subject)}" class="${nkLearningFocusSubject&&nkLearningFocusSubject!==r.subject?'is-dim':''}" style="flex-grow:${counts.get(r.subject)};background:${nkLearningSubjectColor(r.subject)}"></span>`).join('');};
    const tick=v=>m.points?`${Math.round(v)}%`:nkLearningMetric==='time'?(v>=60?`${+(v/60).toFixed(1)}h`:`${Math.round(v)}m`):fmtNum(v);
    const legend=stacked&&order.length?`<div class="nk-li-subject-key" role="group" aria-label="Subjects practised">${order.map(r=>`<button type="button" data-li-subject="${esc(r.subject)}" aria-pressed="${nkLearningFocusSubject===r.subject}" onclick="window.QB.nkLearningFocus(${esc(JSON.stringify(r.subject))})"><i style="background:${nkLearningSubjectColor(r.subject)}"></i>${esc(r.subject)} <b>${fmtNum(r.total)}</b></button>`).join('')}</div>`:'';
    const say=v=>v===null?'no answers':m.points?nkLearningPct(v):nkLearningMetric==='time'?nkLearningTime(v*60000):`${fmtNum(v)} ${m.unit[v===1?0:1]}`;
    return `<div class="nk-li-plot"><div class="nk-li-grid-lines" aria-hidden="true">${[1,.5,0].map(f=>`<span style="bottom:${f*100}%"><em>${tick(max*f)}</em></span>`).join('')}</div><div class="nk-li-plotbars" role="group" aria-label="${esc(m.label)} by ${model.range.period==='year'?'month':model.range.period==='month'?'week':'day'}; drag or tap a bar for detail" onpointermove="window.QB.nkLearningScrub(event)">${model.bins.map((b,i)=>{const cur=b.active?plot(b.current):null,prev=plot(b.previous);return `<button type="button" ${!b.active?'disabled':''} class="${nkLearningBin===i?'is-selected':''}" aria-pressed="${nkLearningBin===i}" aria-label="${esc(b.label)}: ${say(cur)}; ${esc(labels.previous.toLowerCase())} ${say(prev)}" onclick="window.QB.nkLearningSelectBin(${i},event.target.closest('[data-li-subject]')?.dataset.liSubject||'')"><span class="nk-li-col"><i class="is-prev" style="height:${pct(prev)}%"></i><i class="is-cur${stacked?' nk-li-stack':''}" style="height:${pct(cur)}%">${stacked&&b.active?stack(b):''}</i></span><small>${esc(b.label)}</small></button>`;}).join('')}</div></div><div class="nk-li-key"><span><i></i>${esc(labels.current)}</span><span><i class="is-previous"></i>${esc(labels.previous)}</span></div>${legend}<div class="nk-li-bin-readout" role="status" aria-atomic="true">${nkLearningBinReadout(model)}</div>`;
  }
  function nkLearningBinReadout(model){
    const m=NK_LI_METRICS[nkLearningMetric],b=model.bins[nkLearningBin],labels=nkLearningPeriodLabels(model),fmt=v=>v===null||v===undefined?'—':m.format(v);
    if(!b){
      const focus=nkLearningFocusSubject&&nkLearningSubjectSplit(model.current.events).find(r=>r.subject===nkLearningFocusSubject);
      if(focus){const peak=model.bins.map(x=>({x,n:x.current.events.filter(a=>nkLearningSubjectGroup(a.q)===focus.subject).length})).sort((a,c)=>c.n-a.n)[0];
        return `<strong><i style="background:${nkLearningSubjectColor(focus.subject)}"></i>${esc(focus.subject)} · ${esc(labels.current)}</strong><span>${fmtNum(focus.total)} answers · ${model.current.attempts?Math.round(focus.total/model.current.attempts*100):0}% of your practice · ${nkLearningPct(focus.correct/focus.total*100)} correct</span>${peak?.n?`<small>Busiest: ${esc(peak.x.label)} (${fmtNum(peak.n)})</small>`:''}`;}
      // Summary chips: the macro, meso and micro view of the period, as label and number.
      const active=model.bins.filter(x=>x.active&&x.current.attempts),unit=model.range.period==='year'?'month':model.range.period==='month'?'week':'day';
      const values=model.bins.filter(x=>x.active).map(x=>({x,v:m.value(x.current)})).filter(r=>r.v!==null&&r.v!==undefined&&(m.points?r.x.current.attempts:r.v));
      const best=values.sort((a,c)=>c.v-a.v)[0],avg=values.length?(m.points?m.value(model.current):values.reduce((n,r)=>n+r.v,0)/model.bins.filter(x=>x.active).length):null;
      const worst=m.points?values.slice().sort((a,c)=>a.v-c.v)[0]:null;
      return `<ul class="nk-li-chips"><li><small>${m.points?`Weakest ${unit}`:`Avg per ${unit}`}</small><b>${m.points?(worst?`${esc(worst.x.label)} · ${fmt(worst.v)}`:'—'):fmt(avg)}</b></li><li><small>Best ${unit}</small><b>${best?`${esc(best.x.label)} · ${fmt(best.v)}`:'—'}</b></li><li><small>Active ${unit}s</small><b>${fmtNum(active.length)} of ${fmtNum(model.bins.filter(x=>x.active).length)}</b></li></ul>`;
    }
    const rows=nkLearningSubjectSplit(b.current.events);
    return `<strong>${esc([...new Set([nkLearningDate(+b.start),nkLearningDate(Math.min(+b.end,model.range.cut)-1)])].join(' – '))}</strong><span>${[nkLearningMetric==='attempts'?'':`<b>${fmt(m.value(b.current))}</b> ${esc(m.label.toLowerCase())}`,`${fmtNum(b.current.attempts)} answer${b.current.attempts===1?'':'s'}`,nkLearningMetric==='accuracy'?'':`${nkLearningPct(b.current.accuracy)} correct`,b.current.time&&nkLearningMetric!=='time'?nkLearningTime(b.current.time):''].filter(Boolean).join(' · ')}</span>${rows.length?nkLearningSplitRows(rows,b.current.attempts):''}<small>${esc(labels.previous)}: ${fmt(m.value(b.previous))} ${esc(m.label.toLowerCase())} · ${b.previous.attempts} answers</small>`;
  }
  function nkLearningAccuracyBar(row){
    return `<i class="nk-li-progress nk-li-accuracy-bar" role="img" aria-label="${row.correct} of ${row.total} recorded answers correct${row.accuracy===null?'':`: ${nkLearningPct(row.accuracy)}`}" ><i style="width:${row.accuracy||0}%"></i></i>`;
  }
  function nkLearningTopics(model){
    // Needs improvement ranks topics with enough answers first; a one-answer topic never leads the list.
    const rows=model.topicRows.slice().sort((a,b)=>(b.total>=3)-(a.total>=3)||(nkLearningTopicMode==='top'?b.accuracy-a.accuracy:a.accuracy-b.accuracy)||b.total-a.total).slice(0,6);
    return `<div class="nk-li-tabs" role="group" aria-label="Sort topic performance">${[['needs','Needs improvement'],['top','Top performing']].map(([v,l])=>`<button type="button" aria-pressed="${nkLearningTopicMode===v}" onclick="window.QB.nkLearningSetTopics('${v}')">${l}</button>`).join('')}</div>${rows.length?`<ol class="nk-li-rank">${rows.map(t=>`<li><button type="button" class="nk-li-topic" onclick="window.QB.nkLearningOpenTopic('${encodeURIComponent(t.key)}')" aria-label="${esc(t.title)}, ${t.correct} of ${t.total} correct. Open topic"><span><strong>${esc(t.title)}</strong><small>${esc(t.subject)} · ${esc(t.bank)} · ${t.correct}/${t.total}</small></span><b class="${t.total>=3&&t.accuracy<60?'is-low':''}">${nkLearningPct(t.accuracy)}</b><i class="nk-li-share" style="--share:${t.accuracy}%"></i></button></li>`).join('')}</ol>`:nkLearningEmpty('Answer questions to reveal topic strengths and gaps.')}`;
  }
  // Subjects with no answers in either period carry no information; list them in one line.
  // Subjects ranked by answers in the period, each with its accuracy and the change since the previous period.
  function nkLearningSubjects(model){const labels=nkLearningPeriodLabels(model),shown=model.subjects.filter(s=>s.total||s.previous!==null).sort((a,b)=>b.total-a.total||a.subject.localeCompare(b.subject)),idle=model.subjects.length-shown.length;return `<div class="nk-li-subjects">${shown.length?`<ol class="nk-li-rank">${shown.map(s=>{const d=s.accuracy!==null&&s.previous!==null?s.accuracy-s.previous:null;return `<li><div class="nk-li-rank-row"><span><strong>${esc(s.subject)}</strong><small>${s.correct}/${s.total} correct${d===null?'':Math.abs(d)<.5?` · same as ${esc(labels.previous.toLowerCase())}`:` · <em class="${d>0?'is-up':'is-down'}">${d>0?'+':'−'}${Math.abs(d).toFixed(0)} pts</em>`}</small></span><b>${nkLearningPct(s.accuracy)}</b><i class="nk-li-share" style="--share:${s.accuracy||0}%;--tone:${nkLearningSubjectColor(s.subject)}"></i></div></li>`;}).join('')}</ol>`:'<p class="nk-li-subjects-empty">No answers in this period yet.</p>'}${idle&&shown.length?`<p class="nk-li-subjects-idle">${nkLearningIdleLine(model.subjects.filter(s=>!shown.includes(s)))} with no answers in this period.</p>`:''}</div>`;}
  // UWorld collections sit in the subject list too; count them by name.
  function nkLearningIdleLine(rows){
    const names=new Set((typeof SUBJECTS!=='undefined'?SUBJECTS||[]:[]).map(r=>r.subject)),subjects=rows.filter(r=>names.has(r.subject)).length,collections=rows.length-subjects;
    const part=(n,one,many)=>`${fmtNum(n)} ${n===1?one:many}`;
    return [subjects?part(subjects,'other subject','other subjects'):'',collections?part(collections,'UWorld collection','UWorld collections'):''].filter(Boolean).join(' and ');
  }
  function nkLearningFsrs(model){
    const f=model.forecast,max=Math.max(1,...f.counts);
    return `<div class="nk-li-memory"><div class="nk-li-memory-now"><small>Due now</small><b>${fmtNum(f.due)}</b><span>${fmtNum(model.current.reviews)} reviewed · ${nkLearningPct(model.current.reviewAccuracy)} recalled · ${fmtNum(f.total)} cards</span></div><div class="nk-li-forecast" role="img" aria-label="Next 7 days: ${esc(f.counts.map((n,i)=>`${nkLearningDate(+f.days[i])}: ${n} due`).join('; '))}">${f.counts.map((n,i)=>`<span><b>${n}</b><i style="height:${n?Math.max(3,n/max*56):0}px"></i><small>${i===0?'Today':esc(f.days[i].toLocaleDateString(undefined,{weekday:'short'}))}</small></span>`).join('')}</div></div><div class="nk-li-actions">${f.due?`<button type="button" class="nk-li-go" onclick="window.QB.nav('review-dues')">Review by subject ${navIcon('chevron',16)}</button>`:''}<button class="nk-li-link" onclick="window.QB.nav('fsrs-insights')">FSRS insights ${navIcon('chevron',16)}</button></div>`;
  }
  // Activity shade: relative to the busiest day, one green hue from pale to deep, no glow.
  function nkLearningHeatStyle(count,peak){
    if(!count||!peak)return '--heat-fill:var(--nkg-bg-subtle,#f1f1f1);--heat-border:var(--nkg-border,#e5e5e5);--heat-glow:none';
    const ratio=Math.min(1,Math.max(0,count/peak)),light=86-50*ratio,saturation=38+22*ratio;
    return `--heat-fill:hsl(146 ${saturation.toFixed(2)}% ${light.toFixed(2)}%);--heat-border:hsl(146 ${saturation.toFixed(2)}% ${Math.max(30,light-6).toFixed(2)}%);--heat-glow:none`;
  }
  function nkLearningYearActivity(model,now=Date.now()){
    const today=nkLearningDay(now),end=nkLearningHeatYear==='rolling'?nkLearningShift(today,1):new Date(Number(nkLearningHeatYear)+1,0,1),start=nkLearningHeatYear==='rolling'?new Date(today):new Date(Number(nkLearningHeatYear),0,1);
    if(nkLearningHeatYear==='rolling'){start.setFullYear(start.getFullYear()-1);start.setDate(start.getDate()+1);}
    const counts=new Map();model.data.events.filter(a=>nkLearningMatches(a.q)&&a.at>=+start&&a.at<+end&&a.at<=now).forEach(a=>counts.set(dayKey(a.at),(counts.get(dayKey(a.at))||0)+1));
    const first=nkLearningStart(start,'week'),cells=[];let active=0,total=0,longest=0,run=0;
    for(let date=new Date(first);date<end;date=nkLearningShift(date,1)){
      const n=counts.get(dayKey(date))||0,ghost=date<start,future=date>today;
      if(!ghost&&!future){if(n){active++;run++;longest=Math.max(longest,run);}else run=0;total+=n;}
      cells.push({at:+date,n,ghost,future});
    }
    const focusAt=cells.filter(c=>!c.ghost&&!c.future).at(-1)?.at;
    const peak=Math.max(0,...counts.values()),columns=Math.ceil(cells.length/7),months=[];
    cells.forEach((cell,i)=>{const date=new Date(cell.at);if(!cell.ghost&&(date.getDate()===1||i===0||cell.at===+start))months.push({column:Math.floor(i/7)+1,label:date.toLocaleDateString(undefined,{month:'short'})});});
    // A partial first month leaves no room for its label before the next one; drop it rather than overlap.
    for(let i=months.length-2;i>=0;i--)if(months[i+1].column-months[i].column<3)months.splice(i,1);
    const years=[...new Set([today.getFullYear(),...model.data.events.map(a=>new Date(a.at).getFullYear()).filter(y=>y<=today.getFullYear())])].sort((a,b)=>b-a).slice(0,12);
    return `<section class="nk-li-year-activity" aria-labelledby="nk-li-year-title"><header><div><h2 id="nk-li-year-title">Activity</h2><p>${esc(nkLearningDate(+start))} ${start.getFullYear()} – ${esc(nkLearningDate(+end-1))} ${new Date(end-1).getFullYear()}</p></div><label><span class="nk-li-sr">Activity year</span><select aria-label="Activity year" onchange="window.QB.nkLearningSetHeatYear(this.value)"><option value="rolling" ${nkLearningHeatYear==='rolling'?'selected':''}>Past 12 months</option>${years.map(y=>`<option value="${y}" ${String(y)===nkLearningHeatYear?'selected':''}>${y}</option>`).join('')}</select></label></header><div class="nk-li-year-body"><div class="nk-li-year-days" aria-hidden="true"><span>Mon</span><span>Wed</span><span>Fri</span></div><div class="nk-li-year-scroll" tabindex="0" role="group" aria-label="Year of daily study activity; scroll horizontally to explore months"><div class="nk-li-year-canvas" style="--weeks:${columns}"><div class="nk-li-year-months">${months.map(m=>`<span style="grid-column:${m.column}">${esc(m.label)}</span>`).join('')}</div><div class="nk-li-year-grid" role="group" aria-label="Daily study activity; use arrow keys to move between days, Enter to show details">${cells.map((c,i)=>`<button type="button" class="${c.ghost?'is-ghost':''} ${c.future?'is-future':''} ${c.at===+today?'is-today':''}" ${c.ghost||c.future?'disabled':''} tabindex="${c.at===focusAt?'0':'-1'}" aria-pressed="false" aria-label="${esc(new Date(c.at).toLocaleDateString(undefined,{dateStyle:'long'}))}: ${c.n} answers" title="${esc(nkLearningDate(c.at))}: ${c.n} answers" onclick="window.QB.nkLearningYearDetail(${c.at})" style="${nkLearningHeatStyle(c.n,peak)};grid-column:${Math.floor(i/7)+1};grid-row:${i%7+1}"></button>`).join('')}</div></div></div></div><div class="nk-li-year-foot"><p id="nk-li-year-detail" role="status"></p><div class="nk-li-year-key" aria-label="Relative activity scale: 0 to ${peak} answers"><span>0</span>${[0,.25,.5,.75,1].map(r=>`<i style="${nkLearningHeatStyle(peak*r,peak)}" title="${Math.round(peak*r)} answers"></i>`).join('')}<span>${fmtNum(peak)} answers</span></div></div><div class="nk-li-year-summary"><span><b>${fmtNum(active)}</b><small>active days</small></span><span><b>${fmtNum(total)}</b><small>questions answered</small></span><span><b>${fmtNum(longest)} day${longest===1?'':'s'}</b><small>longest run</small></span></div></section>`;
  }
  function nkLearningModules(model){
    const modules=model.current.modules,done=modules.filter(m=>m.isCompleted).length;
    return `<div class="nk-li-modules"><span><b>${done}/${modules.length}</b><small>complete</small></span><span><b>${fmtNum(model.current.completed)}</b><small>finished this period</small></span><i class="nk-li-share" style="--share:${modules.length?done/modules.length*100:0}%"></i></div>${modules.length?'':nkLearningEmpty('Create a focused study module to track your progress.')}<button class="nk-li-link" onclick="window.QB.nav('dashboard')">My study sets ${navIcon('chevron',16)}</button>`;
  }
  // One question per screen: "how is my studying going, and what next?" The selected measure leads as one
  // interactive chart; what needs attention follows; breakdowns, memory and the year come after.
  function nkLearningContent(model){
    const m=NK_LI_METRICS[nkLearningMetric],labels=nkLearningPeriodLabels(model),v=m.value(model.current);
    // The selected tile above already states the total and its change; the chart only names what it plots.
    void v;const main=`<section class="nk-li-main" aria-labelledby="nk-li-main-title"><header><small id="nk-li-main-title">${esc(m.label)} · ${esc(labels.current)}</small></header>${nkLearningBarChart(model)}</section>`;
    return `<section class="nk-li-overview">${nkLearningKpis(model)}${main}</section>${nkFocusSection(model)}<div class="nk-li-grid">${nkLearningCard('Topics',nkLearningTopics(model),'is-topics')}${nkLearningCard('Subjects',nkLearningSubjects(model))}${nkLearningCard('Memory',nkLearningFsrs(model))}${nkLearningCard('Study modules',nkLearningModules(model))}</div>${nkLearningYearActivity(model)}`;
  }
  function analytics(){
    const model=nkLearningModel(),r=model.range,subjects=[...new Set([...model.data.questions.values()].filter(q=>!nkLearningBank||q.bank===nkLearningBank).map(q=>q.subject))],banks=[...new Set([...model.data.questions.values()].filter(q=>!nkLearningSubject||q.subject===nkLearningSubject).map(q=>q.bank))],recent=model.data.tests.filter(t=>Number(t.createdAt)>=r.start&&Number(t.createdAt)<r.cut&&(t.questionIds||[]).some(id=>nkLearningMatches(model.data.questions.get(String(id))||{}))).slice(-5).reverse();
    nkLearningAlignHeatmap();
    const nkHtml=`<div class="nk-app-v114 nk-analytics-v114 nk-learning-insights"><header class="nk-li-head"><div><h1>Insights</h1></div><label><span class="nk-li-sr">Time period</span><select id="nk-li-period" aria-label="Time period" onchange="window.QB.nkLearningSetPeriod(this.value)">${[['week','Week'],['month','Month'],['year','Year']].map(([v,l])=>`<option value="${v}" ${nkLearningPeriod===v?'selected':''}>${nkLearningOffset===0?'This ':''}${l}</option>`).join('')}</select></label></header><div class="nk-li-controls"><div class="nk-li-period-nav"><button type="button" aria-label="Previous ${r.period}" onclick="window.QB.nkLearningMove(-1)">${navIcon('back',18)}</button><strong>${esc(nkLearningRangeLabel(r))}</strong><button type="button" aria-label="Next ${r.period}" ${nkLearningOffset===0?'disabled':''} onclick="window.QB.nkLearningMove(1)">${navIcon('chevron',18)}</button>${nkLearningOffset?'<button class="nk-li-today" onclick="window.QB.nkLearningMove(0)">Today</button>':''}</div><div class="nk-li-scope"><label><span class="nk-li-sr">Insights subject</span><select aria-label="Insights subject" onchange="window.QB.nkLearningSetScope('subject',this.value)"><option value="">All subjects</option>${subjects.map(s=>`<option ${s===nkLearningSubject?'selected':''}>${esc(s)}</option>`).join('')}</select></label><label><span class="nk-li-sr">Insights bank</span><select aria-label="Insights bank" onchange="window.QB.nkLearningSetScope('bank',this.value)"><option value="">All banks</option>${banks.map(b=>`<option ${b===nkLearningBank?'selected':''}>${esc(b)}</option>`).join('')}</select></label></div></div><p class="nk-li-period-note">Compared with ${esc(nkLearningDate(r.previous))} – ${esc(nkLearningDate(r.previousCut-1))}${r.period==='year'?` ${new Date(r.previous).getFullYear()}`:''}${r.partial?' · to date':''}</p><div id="nk-li-content">${nkLearningContent(model)}</div><details class="nk-li-methods"><summary>About these metrics</summary><p>Questions practised counts saved answer attempts across your selected subjects and banks; repeats count again. Accuracy excludes skipped questions. Undo and recall-rating edits do not create extra answers or reviews. Missing timing is not estimated.</p><p>Recorded study time uses each completed session’s duration once, replacing its answer timing. Answers outside completed sessions use their saved question timing. Completed-session time is attributed to the completion date; this is recorded study time, not a background screen-time tracker. Subject/bank time is apportioned using saved question timing, or equally when timing is unavailable.</p><p>FSRS reviews and recall accuracy use spaced-review sessions only. Due counts and forecasts always show the current schedule, including when viewing a past period. Missed-question recovery follows the latest answer by the selected period’s end. The year heatmap uses daily saved answers, with shade relative to the busiest day in the displayed year and scope. It remains independent of the comparison period above.</p><p>Comparisons match the elapsed calendar position of an unfinished period. Module completion uses current saved modules; deleted modules and older sessions removed from saved history are unavailable.</p></details><section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">In this period</div><h2>Study sessions</h2></div><button class="nk-li-link" onclick="window.QB.nav('tests')">All sessions ${navIcon('chevron',16)}</button></div>${recent.length?`<div class="nk-session-list">${recent.map(testRow).join('')}</div>`:nkLearningEmpty('No completed sessions in this period.')}</section></div>`;
    // In-place refreshes only need the Insights markup, not a full app shell (nav, badges, due counts).
    return nkLearningNoShell?nkHtml:shell(nkHtml,'analytics');
  }
  // Recalculate immediately while preserving native pickers, the app shell,
  // disclosure state and the learner's place in the report.
  function nkLearningRefresh(){
    const current=document.querySelector('.nk-learning-insights');if(!current){render();return;}
    const x=window.scrollX,y=window.scrollY,heat=current.querySelector('.nk-li-year-scroll')?.scrollLeft||0;
    const nav=current.querySelector('.nk-li-period-nav'),focusIndex=[...nav.querySelectorAll('button')].indexOf(document.activeElement);
    const template=document.createElement('template');nkLearningNoShell=true;try{template.innerHTML=analytics();}finally{nkLearningNoShell=false;}
    const next=template.content.querySelector('.nk-learning-insights');if(!next){render();return;}
    for(const selector of ['#nk-li-period','select[aria-label="Insights subject"]','select[aria-label="Insights bank"]']){
      const select=current.querySelector(selector),updated=next.querySelector(selector),value=updated.value;
      select.replaceChildren(...updated.childNodes);select.value=value;
    }
    nav.replaceChildren(...next.querySelector('.nk-li-period-nav').childNodes);
    current.querySelector('.nk-li-period-note').textContent=next.querySelector('.nk-li-period-note').textContent;
    const liveYear=current.querySelector('.nk-li-year-activity'),nextYear=next.querySelector('.nk-li-year-activity');
    if(liveYear&&nextYear&&liveYear.dataset.nkYearKey===nkLearningYearMemo.key)nextYear.replaceWith(liveYear);
    current.querySelector('#nk-li-content').replaceChildren(...next.querySelector('#nk-li-content').childNodes);
    const year=current.querySelector('.nk-li-year-activity');if(year)year.dataset.nkYearKey=nkLearningYearMemo.key;
    current.querySelector('.nk-section').replaceWith(next.querySelector('.nk-section'));
    if(focusIndex>=0){const buttons=nav.querySelectorAll('button');(buttons[focusIndex]?.disabled?buttons[0]:buttons[focusIndex])?.focus({preventScroll:true});}
    window.scrollTo(x,y);
    requestAnimationFrame(()=>{const scroll=current.querySelector('.nk-li-year-scroll');if(scroll)scroll.scrollLeft=heat;});
  }
  // Collecting every saved answer is the expensive step; reuse it until study data changes.
  const nkLearningCollectRaw=nkLearningCollect;let nkLearningCollectMemo={key:'',data:null};
  nkLearningCollect=function(){
    let n=0,last=0;for(const list of Object.values(state.attempts||{})){if(!Array.isArray(list))continue;n+=list.length;const e=list[list.length-1],at=Number(e?.reviewedAt||e?.at||0);if(at>last)last=at;}
    const tests=state.tests||[],t=tests[tests.length-1],s=state.activeSession;
    const names=tests.reduce((h,x)=>h+String(x?.title||'').length*31+String(x?.id||'').length,0);
    const key=[n,last,tests.length,t?.id,t?.createdAt,names,Object.keys(state.fsrsReviewEligible||{}).length,s?.id,Object.keys(s?.answers||{}).length,nkAllStudyQuestions().length].join('|');
    if(nkLearningCollectMemo.key!==key)nkLearningCollectMemo={key,data:nkLearningCollectRaw()};
    return nkLearningCollectMemo.data;
  };
  // The year heatmap ignores the comparison period, so period/offset changes reuse it.
  const nkLearningYearActivityRaw=nkLearningYearActivity;let nkLearningYearMemo={key:'',html:''};
  nkLearningYearActivity=function(model,now=Date.now()){
    const events=model.data.events;let last=0;for(const a of events)if(a.at>last)last=a.at;
    const key=[nkLearningHeatYear,nkLearningSubject,nkLearningBank,events.length,last,dayKey(now)].join('|');
    if(nkLearningYearMemo.key!==key)nkLearningYearMemo={key,html:nkLearningYearActivityRaw(model,now)};
    return nkLearningYearMemo.html;
  };
  // The period pill slides on the compositor; re-render the report a frame later so the slide starts first.
  let nkLearningRefreshQueued=false;
  function nkLearningRefreshSoon(){
    if(typeof requestAnimationFrame!=='function'){nkLearningRefresh();return;}
    if(nkLearningRefreshQueued)return;nkLearningRefreshQueued=true;
    requestAnimationFrame(()=>requestAnimationFrame(()=>{nkLearningRefreshQueued=false;if(document.querySelector('.nk-learning-insights'))nkLearningRefresh();}));
  }
  function nkLearningSetPeriod(value){if(!['week','month','year'].includes(value))return;nkLearningPeriod=value;nkLearningOffset=0;nkLearningBin=-1;nkLearningRefreshSoon();}
  function nkLearningMove(n){if(![-1,0,1].includes(n))return;nkLearningOffset=n===0?0:Math.min(0,nkLearningOffset+n);nkLearningBin=-1;nkLearningRefresh();}
  // Subject and bank narrow each other: a bank only offers the subjects it contains
  // (UWorld offers its collections, PrepLadder/Marrow offer the three core subjects)
  // and vice versa. Picking one keeps the other when still valid, otherwise clears it.
  function nkLearningSetScope(field,value){
    const all=nkAllStudyQuestions(),has=(subject,bank)=>all.some(q=>(!subject||q.subject===subject)&&(!bank||q.bank===bank));
    if(field==='subject'){if(value&&!has(value,''))return;nkLearningSubject=value;if(nkLearningBank&&!has(value,nkLearningBank))nkLearningBank='';}
    else if(field==='bank'){if(value&&!has('',value))return;nkLearningBank=value;if(nkLearningSubject&&!has(nkLearningSubject,value))nkLearningSubject='';}
    else return;nkLearningBin=-1;nkLearningRefresh();
  }
  function nkLearningSelectBin(index,subject=''){const model=nkLearningModel(),b=model.bins[Number(index)];if(!b?.active)return;nkLearningBin=Number(index);nkLearningFocusSubject=String(subject||'');nkLearningPaintFocus();document.querySelectorAll('.nk-li-plotbars button').forEach((button,i)=>{button.classList.toggle('is-selected',i===nkLearningBin);button.setAttribute('aria-pressed',String(i===nkLearningBin));});const node=document.querySelector('.nk-li-bin-readout');if(node)node.innerHTML=nkLearningBinReadout(model);}
  function nkLearningPaintFocus(){document.querySelectorAll('.nk-li-stack span').forEach(n=>n.classList.toggle('is-dim',Boolean(nkLearningFocusSubject)&&n.dataset.liSubject!==nkLearningFocusSubject));document.querySelectorAll('.nk-li-subject-key button').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.liSubject===nkLearningFocusSubject)));}
  // The key toggles one subject: other bands fade and the readout shows that subject's period.
  function nkLearningFocus(subject){nkLearningFocusSubject=nkLearningFocusSubject===subject?'':String(subject||'');nkLearningBin=-1;document.querySelectorAll('.nk-li-plotbars button').forEach(button=>{button.classList.remove('is-selected');button.setAttribute('aria-pressed','false');});nkLearningPaintFocus();const node=document.querySelector('.nk-li-bin-readout');if(node)node.innerHTML=nkLearningBinReadout(nkLearningModel());}
  function nkLearningSetTopics(value){if(!['needs','top'].includes(value))return;nkLearningTopicMode=value;const node=document.querySelector('.nk-li-card.is-topics');if(node&&typeof nkPolishReplaceSurface==='function')nkPolishReplaceSurface(node,nkLearningCard('Topics',nkLearningTopics(nkLearningModel()),'is-topics'));else if(node)node.outerHTML=nkLearningCard('Topics',nkLearningTopics(nkLearningModel()),'is-topics');if(typeof requestAnimationFrame==='function')requestAnimationFrame(()=>document.querySelector(`.nk-li-card.is-topics .nk-li-tabs [onclick*="'${value}'"]`)?.focus({preventScroll:true}));}
  function nkLearningOpenTopic(encoded){let key;try{key=JSON.parse(decodeURIComponent(encoded));}catch{return;}if(!Array.isArray(key)||key.length!==3)return;if(!nkModuleBankRecords().some(r=>r.subject===key[0]&&nkModuleBankName(r)===key[1]&&nkModuleTopics(r).some(t=>String(t.id)===String(key[2]))))return;nkOpenSubjectChapter(...key);}
  function nkLearningSetHeatYear(value){const year=Number(value);if(value!=='rolling'&&(!Number.isInteger(year)||year<2000||year>new Date().getFullYear()))return;nkLearningHeatYear=String(value);const node=document.querySelector('.nk-li-year-activity');if(node&&typeof nkPolishReplaceSurface==='function')nkPolishReplaceSurface(node,nkLearningYearActivity(nkLearningModel()));else if(node)node.outerHTML=nkLearningYearActivity(nkLearningModel());nkLearningAlignHeatmap();}
  function nkLearningYearDetail(at){const date=nkLearningDay(at),end=nkLearningShift(date,1),rows=nkLearningCollect().events.filter(a=>nkLearningMatches(a.q)&&a.at>=+date&&a.at<+end),node=document.getElementById('nk-li-year-detail');if(node)node.textContent=`${date.toLocaleDateString(undefined,{dateStyle:'medium'})}: ${fmtNum(rows.length)} answers · ${rows.filter(a=>a.correct).length} correct · ${rows.filter(a=>!a.correct).length} incorrect.`;document.querySelectorAll('.nk-li-year-grid button').forEach(button=>{const selected=button.getAttribute('onclick')===`window.QB.nkLearningYearDetail(${+date})`;button.classList.toggle('is-selected',selected);button.setAttribute('aria-pressed',String(selected));button.tabIndex=selected?0:-1;});}
  function nkLearningAlignHeatmap(){if(typeof requestAnimationFrame!=='function')return;requestAnimationFrame(()=>{const node=document.querySelector('.nk-li-year-scroll');if(!node)return;const today=node.querySelector('.is-today');node.scrollLeft=today?Math.max(0,today.getBoundingClientRect().left-node.getBoundingClientRect().left+node.scrollLeft-node.clientWidth+40):nkLearningHeatYear==='rolling'?node.scrollWidth:0;});}
  /* NK_LEARNING_INSIGHTS_V1_END */
