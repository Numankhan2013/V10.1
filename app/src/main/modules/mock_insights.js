  /* NK_MOCK_INSIGHTS_V1_START */
  // Mock tests on Insights. One chart, four readings of the same sittings: score, accuracy on what you
  // answered, how much of the paper you answered, and pace against the clock. The readout above the chart
  // works like a native chart's selection: it shows the window's average until you touch a sitting, then
  // that sitting. Below it: where the marks went across the window, and which subjects cost them.
  const NK_MI_WINDOW=20;
  const NK_MI_METRICS={
    score:{label:'Score',noun:'score'},
    accuracy:{label:'Accuracy',noun:'accuracy on answered questions'},
    answered:{label:'Answered',noun:'share of the paper answered'},
    pace:{label:'Pace',noun:'seconds per answer'}
  };
  let nkMi={metric:'score',pinned:null};
  function nkMiQuestion(id){return typeof nkFindStudyQuestion==='function'?nkFindStudyQuestion(id):(BY_ID?.[String(id)]||null);}
  function nkMiRows(){
    return (state.tests||[]).filter(t=>t&&t.kind!=='practice'&&Number(t.total)>0).slice()
      .sort((a,b)=>Number(a.createdAt||0)-Number(b.createdAt||0)).slice(-NK_MI_WINDOW).map(t=>{
        const total=Number(t.total)||0,correct=Number(t.correct)||0,incorrect=Number(t.incorrect)||0,answered=correct+incorrect;
        const timeup=Object.keys(t.expired||{}).filter(id=>!t.answers?.[id]).length,blank=Math.max(0,total-answered-timeup);
        const times=(t.questionIds||[]).filter(id=>t.answers?.[id]).map(id=>Number(t.questionTimes?.[id])||0).filter(ms=>ms>0);
        const pace=answered?(times.length?times.reduce((a,b)=>a+b,0)/times.length:(Number(t.totalTimeMs)||0)/answered)/1000:null;
        const marks=t.marking&&!nkExamIsPlain(t.marking)?nkExamMarks(t):null;
        const missed=Boolean(t.missed);
        return {t,total,correct,incorrect,answered,blank,timeup,marks,missed,makeup:Boolean(t.makeupFor),booked:Boolean(t.scheduledMockId),
          limit:Number(t.secondsPerQuestion)||60,
          score:Math.round(correct/total*100),accuracy:answered?Math.round(correct/answered*100):null,
          answeredPct:Math.round(answered/total*100),pace:pace&&Number.isFinite(pace)?Math.round(pace):null};
      });
  }
  function nkMiValue(r,metric){
    if(metric==='score')return r.missed?0:r.score;
    if(r.missed)return null;
    return metric==='accuracy'?r.accuracy:metric==='answered'?r.answeredPct:r.pace;
  }
  function nkMtDay(at){const d=new Date(Number(at)||0);return d.toLocaleDateString(undefined,{month:'short',day:'numeric'});}
  function nkMiFormat(v,metric){return v==null?'—':metric==='pace'?`${fmtNum(v)} s`:`${fmtNum(v)}%`;}
  function nkMiMean(list){return list.length?Math.round(list.reduce((a,b)=>a+b,0)/list.length):null;}
  // Monotone cubic through the points (Fritsch–Carlson), so the line never swings past a real value.
  function nkMiPath(p){
    if(!p.length)return '';if(p.length===1)return `M${p[0][0]},${p[0][1]}`;
    const n=p.length,d=[],m=[];
    for(let i=0;i<n-1;i++)d.push((p[i+1][1]-p[i][1])/((p[i+1][0]-p[i][0])||1));
    m[0]=d[0];m[n-1]=d[n-2];
    for(let i=1;i<n-1;i++)m[i]=d[i-1]*d[i]<=0?0:(d[i-1]+d[i])/2;
    for(let i=0;i<n-1;i++){if(d[i]===0){m[i]=m[i+1]=0;continue;}const a=m[i]/d[i],b=m[i+1]/d[i],s=a*a+b*b;if(s>9){const k=3/Math.sqrt(s);m[i]=k*a*d[i];m[i+1]=k*b*d[i];}}
    let out=`M${p[0][0]},${p[0][1]}`;
    for(let i=0;i<n-1;i++){const h=(p[i+1][0]-p[i][0])/3;out+=` C${(p[i][0]+h).toFixed(1)},${(p[i][1]+m[i]*h).toFixed(1)} ${(p[i+1][0]-h).toFixed(1)},${(p[i+1][1]-m[i+1]*h).toFixed(1)} ${p[i+1][0]},${p[i+1][1]}`;}
    return out;
  }
  function nkMiDetail(r,metric){
    if(r.missed)return 'Missed · scored 0';
    if(metric==='accuracy')return `${fmtNum(r.correct)} right of ${fmtNum(r.answered)} answered`;
    if(metric==='answered')return `${fmtNum(r.answered)} of ${fmtNum(r.total)} answered${r.timeup?` · ${fmtNum(r.timeup)} timed out`:''}`;
    if(metric==='pace')return `Limit ${fmtNum(r.limit)} s a question`;
    return `${fmtNum(r.correct)} / ${fmtNum(r.total)} correct${r.marks?` · ${fmtNum(r.marks.score)} of ${fmtNum(r.marks.max)} marks`:''}`;
  }
  function nkMiSummary(rows,metric){
    const vals=rows.map(r=>nkMiValue(r,metric)).filter(v=>v!=null),avg=nkMiMean(vals);
    const recent=vals.slice(-5),before=vals.slice(-10,-5),delta=before.length?nkMiMean(recent)-nkMiMean(before):null;
    let trend='';
    if(delta!=null){
      const unit=metric==='pace'?' s':' pts',mag=Math.abs(delta);
      trend=!mag?'Level with the 5 before':metric==='pace'?`${fmtNum(mag)}${unit} ${delta<0?'faster':'slower'} than the 5 before`:`${delta>0?'Up':'Down'} ${fmtNum(mag)}${unit} on the 5 before`;
    }
    return {avg,trend,delta,count:vals.length};
  }
  function nkMiReadout(rows,metric,index){
    const r=index==null?null:rows[index];
    if(r){
      return `<div class="nk-mt-readout is-pinned" data-i="${index}"><small>${esc(r.t.title||'Timed test')} · ${esc(fmtDate(r.t.createdAt))}</small><b>${nkMiFormat(nkMiValue(r,metric),metric)}</b><span>${esc(nkMiDetail(r,metric))}</span><button type="button" class="nk-mt-open" onclick="window.QB.nav('result',${esc(JSON.stringify(String(r.t.id)))})">Open result ${navIcon('chevron',14)}</button></div>`;
    }
    const s=nkMiSummary(rows,metric);
    return `<div class="nk-mt-readout"><small>Average ${esc(NK_MI_METRICS[metric].noun)} · last ${fmtNum(s.count)} test${s.count===1?'':'s'}</small><b>${nkMiFormat(s.avg,metric)}</b><span>${esc(s.trend||'Sit a few more to see a trend')}</span></div>`;
  }
  function nkMiChart(rows,metric){
    const W=640,H=200,padX=10,top=14,bottom=10;
    const pts=rows.map((r,i)=>({r,i,v:nkMiValue(r,metric)})).filter(p=>p.v!=null);
    if(!pts.length)return `<p class="nk-mt-none">No answered sittings to plot yet.</p>`;
    const limit=metric==='pace'?Math.round(nkMiMean(rows.map(r=>r.limit))):null;
    const maxV=metric==='pace'?Math.max(limit*1.25,...pts.map(p=>p.v)):100,ceil=metric==='pace'?Math.ceil(maxV/15)*15:100;
    const n=pts.length,x=k=>n===1?W/2:padX+k*(W-padX*2)/(n-1),y=v=>top+(1-v/ceil)*(H-top-bottom);
    const xy=pts.map((p,k)=>[Math.round(x(k)*10)/10,Math.round(y(p.v)*10)/10]);
    const line=nkMiPath(xy),area=n>1?`${line} L${xy[n-1][0]},${H-bottom} L${xy[0][0]},${H-bottom} Z`:'';
    const ref=metric==='pace'?limit:nkMiMean(pts.map(p=>p.v)),refLabel=metric==='pace'?`Limit ${fmtNum(limit)} s`:`Avg ${fmtNum(ref)}%`;
    const ticks=metric==='pace'?[0,ceil]:[0,50,100];
    const pct=(v,of)=>(v/of*100).toFixed(2);
    const dots=pts.map((p,k)=>`<i class="${p.r.missed?'is-missed':p.r.makeup?'is-makeup':p.r.booked?'is-booked':''}" data-i="${p.i}" style="left:${pct(xy[k][0],W)}%;top:${pct(xy[k][1],H)}%;--d:${Math.min(k,24)*35+420}ms"></i>`).join('');
    const first=pts[0].r.t.createdAt,last=pts[n-1].r.t.createdAt;
    return `<div class="nk-mt-plot" tabindex="0" role="group" aria-roledescription="chart" aria-label="${esc(NK_MI_METRICS[metric].label)} across ${fmtNum(n)} timed tests. Left and right arrows read each test, Enter opens it." data-n="${n}" data-points="${esc(JSON.stringify(pts.map((p,k)=>[p.i,Number(pct(xy[k][0],W)),Number(pct(xy[k][1],H))])))}">
        <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">
          <g class="nk-mt-grid">${ticks.map(v=>`<line x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}"/>`).join('')}</g>
          <line class="nk-mt-ref" x1="0" x2="${W}" y1="${y(ref)}" y2="${y(ref)}"/>
          ${area?`<path class="nk-mt-area" d="${area}"/>`:''}<path class="nk-mt-line" d="${line}" pathLength="1"/>
        </svg>
        <div class="nk-mt-ticks" aria-hidden="true">${ticks.map(v=>`<span style="top:${pct(y(v),H)}%">${metric==='pace'?`${fmtNum(v)} s`:fmtNum(v)}</span>`).join('')}<em style="top:${pct(y(ref),H)}%">${esc(refLabel)}</em></div>
        <div class="nk-mt-dots" aria-hidden="true">${dots}</div>
        <i class="nk-mt-cursor" aria-hidden="true"></i>
      </div>
      <div class="nk-mt-axis" aria-hidden="true"><span>${esc(nkMtDay(first))}</span><span>${esc(nkMtDay(last))}</span></div>`;
  }
  // Where the marks went across the window's sat papers: one whole, split four ways.
  function nkMiSplit(rows){
    const sat=rows.filter(r=>!r.missed);if(!sat.length)return '';
    const sum=k=>sat.reduce((n,r)=>n+r[k],0),total=sum('total');
    const parts=[['is-correct','Correct',sum('correct')],['is-wrong','Wrong',sum('incorrect')],['is-blank','Left blank',sum('blank')],['is-timeup','Timed out',sum('timeup')]].filter(p=>p[2]>0);
    const share=v=>Math.round(v/total*100);
    const marked=sat.filter(r=>r.marks&&Number(r.t.marking?.wrong)<0);
    const lost=marked.reduce((n,r)=>n+r.incorrect*Math.abs(Number(r.t.marking.wrong)),0),max=marked.reduce((n,r)=>n+(Number(r.marks.max)||0),0);
    const cost=marked.length&&lost?`<p class="nk-mt-cost">${navIcon('close',14)}<span>Wrong answers cost <b>${fmtNum(Math.round(lost*100)/100)} marks</b>${max?` (${fmtNum(Math.round(lost/max*100))}% of the paper)`:''} across ${fmtNum(marked.length)} negatively marked test${marked.length===1?'':'s'}.</span></p>`:'';
    return `<section class="nk-mt-block" aria-labelledby="nk-mt-split-h"><h3 id="nk-mt-split-h">Where the marks went</h3>
      <div class="nk-mt-bar" role="img" aria-label="${esc(parts.map(([,l,v])=>`${l} ${fmtNum(v)} (${share(v)}%)`).join(', '))}">${parts.map(([k,,v])=>`<i class="${k}" style="flex:${v} 1 0"></i>`).join('')}</div>
      <ul class="nk-mt-key">${parts.map(([k,l,v])=>`<li><i class="${k}" aria-hidden="true"></i><span>${l}</span><b>${fmtNum(v)}</b><small>${share(v)}%</small></li>`).join('')}</ul>${cost}</section>`;
  }
  // Subjects, from the answers inside these mocks: accuracy on what was answered, weakest first.
  function nkMiSubjects(rows){
    const by=new Map();
    rows.filter(r=>!r.missed).forEach(r=>(r.t.questionIds||[]).forEach(id=>{
      const sel=r.t.answers?.[id];const q=nkMiQuestion(id);if(!q)return;
      const name=q.bank==='UWorld'?'My UWorld':String(q.subject||'Other');
      const s=by.get(name)||{name,asked:0,answered:0,right:0};s.asked++;
      if(sel){s.answered++;if(Number(q.correctOption)===Number(sel))s.right++;}
      by.set(name,s);
    }));
    const list=[...by.values()].filter(s=>s.answered>=3).map(s=>({...s,acc:Math.round(s.right/s.answered*100)})).sort((a,b)=>a.acc-b.acc||b.answered-a.answered);
    if(!list.length)return '';
    const row=(s,k)=>`<li style="--k:${k}"><span>${esc(s.name)}</span><b>${fmtNum(s.acc)}%</b><i aria-hidden="true"><i style="width:${Math.max(2,s.acc)}%"></i></i><small>${fmtNum(s.right)} of ${fmtNum(s.answered)} right${s.asked>s.answered?` · ${fmtNum(s.asked-s.answered)} blank`:''}</small></li>`;
    const head=list.slice(0,5),rest=list.slice(5);
    return `<section class="nk-mt-block" aria-labelledby="nk-mt-subj-h"><h3 id="nk-mt-subj-h">By subject <small>weakest first</small></h3>
      <ol class="nk-mt-subjects">${head.map(row).join('')}</ol>${rest.length?`<details class="nk-mt-more"><summary>${fmtNum(rest.length)} more subject${rest.length===1?'':'s'}</summary><ol class="nk-mt-subjects">${rest.map((s,k)=>row(s,k+5)).join('')}</ol></details>`:''}</section>`;
  }
  function nkMiAttendance(rows){
    const att=typeof nkSchedAttendance==='function'?nkSchedAttendance():{booked:0,kept:0,streak:0,best:0};
    const sat=rows.filter(r=>!r.missed),best=sat.length?Math.max(...sat.map(r=>r.score)):null;
    const facts=[`${fmtNum(sat.length)} sat`,best!=null?`best ${fmtNum(best)}%`:'',att.booked?`${fmtNum(att.kept)} of ${fmtNum(att.booked)} booked mocks kept`:''].filter(Boolean).join(' · ');
    const dots=att.booked&&typeof nkSchedList==='function'?nkSchedList().map(m=>({m,st:nkSchedStatus(m)})).filter(v=>v.st==='taken'||v.st==='missed').sort((a,b)=>a.m.at-b.m.at).slice(-16).map(v=>`<i class="is-${v.st}"></i>`).join(''):'';
    return `<footer class="nk-mt-foot"><p>${esc(facts)}</p>${att.booked?`<p><b>${att.streak?`${fmtNum(att.streak)} kept in a row`:'Attendance streak broken'}</b>${att.best>1?` · best run ${fmtNum(att.best)}`:''}</p><span class="nk-sched-attend-dots" aria-hidden="true">${dots}</span>`:''}</footer>`;
  }
  function nkMiTable(rows){
    return `<div class="nk-sr"><table><caption>Timed tests in this chart</caption><thead><tr><th>Test</th><th>Date</th><th>Score</th><th>Accuracy</th><th>Answered</th><th>Seconds per answer</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r.t.title||'Timed test')}${r.missed?' (missed)':''}</td><td>${esc(fmtDate(r.t.createdAt))}</td><td>${nkMiFormat(nkMiValue(r,'score'),'score')}</td><td>${nkMiFormat(nkMiValue(r,'accuracy'),'accuracy')}</td><td>${nkMiFormat(nkMiValue(r,'answered'),'answered')}</td><td>${nkMiFormat(nkMiValue(r,'pace'),'pace')}</td></tr>`).join('')}</tbody></table></div>`;
  }
  function nkMockInsightsSection(){
    const rows=nkMiRows(),metric=nkMi.metric;
    const head=`<div class="nk-section-head"><h2>Mock tests</h2></div>`;
    if(!rows.length)return `<section class="nk-section nk-mock-in">${head}<div class="nk-mt-empty"><p>Sit a timed test or book a mock. Score, accuracy, pace and where your marks go will build up here.</p><button type="button" onclick="window.QB.nav('tests')">Go to Tests ${navIcon('chevron',16)}</button></div></section>`;
    if(nkMi.pinned!=null&&(nkMi.pinned>=rows.length||nkMiValue(rows[nkMi.pinned],metric)==null))nkMi.pinned=null;
    const legend=metric==='score'&&rows.some(r=>r.missed||r.booked||r.makeup)?`<div class="nk-mt-legend"><span><i></i>Timed test</span>${rows.some(r=>r.booked)?'<span><i class="is-booked"></i>Booked mock</span>':''}${rows.some(r=>r.makeup)?'<span><i class="is-makeup"></i>Make-up</span>':''}${rows.some(r=>r.missed)?'<span><i class="is-missed"></i>Missed · 0</span>':''}</div>`
      :metric!=='score'&&rows.some(r=>r.missed)?`<p class="nk-mt-note">Missed mocks count only toward score.</p>`:'';
    return `<section class="nk-section nk-mock-in" data-metric="${metric}">${head}
      <div class="nk-mt-card">
        <div class="nk-mt-metrics" role="radiogroup" aria-label="Measure">${Object.entries(NK_MI_METRICS).map(([k,m])=>`<button type="button" role="radio" aria-checked="${k===metric}" class="${k===metric?'is-on':''}" onclick="window.QB.nkMockInsightSet('${k}')">${m.label}</button>`).join('')}</div>
        <div class="nk-mt-live" aria-live="polite">${nkMiReadout(rows,metric,nkMi.pinned)}</div>
        <div class="nk-mt-chart">${nkMiChart(rows,metric)}</div>
        ${legend}
        ${nkMiSplit(rows)}
        ${nkMiSubjects(rows)}
        ${nkMiAttendance(rows)}
        ${nkMiTable(rows)}
      </div>
    </section>`;
  }
  function nkMockInsightSet(metric){
    nkMi={metric:NK_MI_METRICS[metric]?metric:metric==='marks'?'score':'score',pinned:null};
    const node=document.querySelector('.nk-mock-in');if(node)node.outerHTML=nkMockInsightsSection();
    document.querySelector('.nk-mt-metrics [aria-checked="true"]')?.focus({preventScroll:true});
  }
  // Selection: the readout follows a finger or the arrow keys; a tap pins it and offers the result.
  let nkMiLastTick=null;
  function nkMiShow(plot,index,pinned){
    const pts=JSON.parse(plot.dataset.points||'[]'),hit=pts.find(p=>p[0]===index);if(!hit)return;
    const rows=nkMiRows(),live=plot.closest('.nk-mt-card')?.querySelector('.nk-mt-live');
    plot.dataset.at=String(index);
    const cursor=plot.querySelector('.nk-mt-cursor');
    if(cursor){cursor.style.setProperty('--x',hit[1]+'%');cursor.style.setProperty('--y',hit[2]+'%');cursor.classList.add('is-on');}
    plot.querySelectorAll('.nk-mt-dots i').forEach(d=>d.classList.toggle('is-active',Number(d.dataset.i)===index));
    if(live&&live.firstElementChild?.dataset.i!==String(index)){live.innerHTML=nkMiReadout(rows,nkMi.metric,index);live.firstElementChild.classList.add('is-in');}
    if(pinned)nkMi.pinned=index;
    if(nkMiLastTick!==index){nkMiLastTick=index;if(typeof haptic==='function')haptic(4);}
  }
  function nkMiRelease(plot){
    if(nkMi.pinned!=null)return;
    plot.querySelector('.nk-mt-cursor')?.classList.remove('is-on');
    plot.querySelectorAll('.nk-mt-dots i.is-active').forEach(d=>d.classList.remove('is-active'));
    const live=plot.closest('.nk-mt-card')?.querySelector('.nk-mt-live');
    if(live&&live.firstElementChild?.classList.contains('is-pinned')){live.innerHTML=nkMiReadout(nkMiRows(),nkMi.metric,null);live.firstElementChild.classList.add('is-in');}
    delete plot.dataset.at;nkMiLastTick=null;
  }
  function nkMiNearest(plot,clientX){
    const box=plot.getBoundingClientRect(),rel=(clientX-box.left)/Math.max(1,box.width)*100;
    let best=null,dist=Infinity;JSON.parse(plot.dataset.points||'[]').forEach(p=>{const d=Math.abs(p[1]-rel);if(d<dist){dist=d;best=p[0];}});
    return best;
  }
  document.addEventListener('pointermove',event=>{const plot=event.target instanceof Element&&event.target.closest('.nk-mt-plot');if(plot&&nkMi.pinned==null){const i=nkMiNearest(plot,event.clientX);if(i!=null)nkMiShow(plot,i,false);}},{passive:true});
  document.addEventListener('pointerleave',event=>{if(event.target instanceof Element&&event.target.matches?.('.nk-mt-plot'))nkMiRelease(event.target);},true);
  document.addEventListener('click',event=>{
    const plot=event.target instanceof Element&&event.target.closest('.nk-mt-plot');
    if(!plot){
      // A tap anywhere else lets go of a pinned sitting.
      const inside=event.target instanceof Element&&event.target.closest('.nk-mt-live');
      if(nkMi.pinned!=null&&!inside){nkMi.pinned=null;const p=document.querySelector('.nk-mt-plot');if(p)nkMiRelease(p);}
      return;
    }
    const i=nkMiNearest(plot,event.clientX);if(i==null)return;
    if(nkMi.pinned===i){nkMi.pinned=null;nkMiRelease(plot);return;}
    nkMi.pinned=null;nkMiShow(plot,i,true);
  });
  document.addEventListener('keydown',event=>{
    const plot=event.target instanceof Element&&event.target.closest('.nk-mt-plot');if(!plot)return;
    const order=JSON.parse(plot.dataset.points||'[]').map(p=>p[0]);if(!order.length)return;
    const at=order.indexOf(plot.dataset.at===undefined?order[order.length-1]:Number(plot.dataset.at));
    if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();const k=Math.max(0,Math.min(order.length-1,(at<0?order.length-1:at)+(event.key==='ArrowLeft'?-1:1)));nkMi.pinned=null;nkMiShow(plot,order[k],true);}
    else if(event.key==='Enter'&&plot.dataset.at!==undefined){const r=nkMiRows()[Number(plot.dataset.at)];if(r)navigate('result',r.t.id);}
    else if(event.key==='Escape'){nkMi.pinned=null;nkMiRelease(plot);}
  });
  // The Tests page keeps a one-line summary that opens this section, instead of a second score chart.
  function nkMockInsightsLink(){
    const rows=nkMiRows();if(rows.length<2)return '';
    const s=nkMiSummary(rows,'score');
    return `<section class="nk-v3-section nk-tests-trend" aria-label="Score trend"><button type="button" class="nk-tests-insight" onclick="window.QB.nkMockInsightsOpen()"><span class="nk-tests-insight-copy"><strong>Mock insights</strong><small>Average ${fmtNum(s.avg)}% over ${fmtNum(s.count)} tests${s.trend?` · ${esc(s.trend.toLowerCase())}`:''}</small></span>${navIcon('chevron',18)}</button></section>`;
  }
  function nkMockInsightsOpen(){
    nkMi={metric:'score',pinned:null};navigate('analytics');
    requestAnimationFrame(()=>document.querySelector('.nk-mock-in')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'}));
  }
  if(typeof analytics==='function'){
    const original=analytics;
    analytics=function(){
      if(typeof nkSchedRecordMisses==='function')nkSchedRecordMisses();
      nkMi.pinned=null;
      const html=original.apply(this,arguments);
      return html.includes('<details class="nk-li-methods">')?html.replace('<details class="nk-li-methods">',nkMockInsightsSection()+'<details class="nk-li-methods">'):html;
    };
  }
  /* NK_MOCK_INSIGHTS_V1_END */
