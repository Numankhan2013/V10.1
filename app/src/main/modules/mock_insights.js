  /* NK_MOCK_INSIGHTS_V1_START */
  // Mock tests on Insights: every timed test and booked mock as a living line. Drag or hover across it to
  // read any sitting; tap a point to open its result. Missed mocks sit on the floor at zero, in red.
  let nkMockInsightMode='score';
  function nkMockInsightRows(){
    return (state.tests||[]).filter(t=>t&&t.kind!=='practice'&&Number(t.total)>0).slice().sort((a,b)=>Number(a.createdAt||0)-Number(b.createdAt||0)).slice(-24).map(t=>{
      const score=Math.round(Number(t.correct||0)/Number(t.total)*100);
      const marks=t.marking&&!nkExamIsPlain(t.marking)?nkExamMarks(t):null;
      const value=nkMockInsightMode==='marks'&&marks&&marks.max?Math.max(0,Math.round(marks.score/marks.max*100)):score;
      return {t,score,marks,value,missed:Boolean(t.missed),makeup:Boolean(t.makeupFor),scheduled:Boolean(t.scheduledMockId)};
    });
  }
  function nkMockInsightPath(points){
    if(!points.length)return '';
    // A gentle monotone curve through the points.
    let d=`M${points[0][0]},${points[0][1]}`;
    for(let i=1;i<points.length;i++){const [x0,y0]=points[i-1],[x1,y1]=points[i],mx=(x0+x1)/2;d+=` C${mx},${y0} ${mx},${y1} ${x1},${y1}`;}
    return d;
  }
  function nkMockInsightTip(row,i){
    const t=row.t,when=fmtDate(t.createdAt);
    const detail=row.missed?'Missed · scored 0':`${fmtNum(t.correct||0)} / ${fmtNum(t.total)} correct${row.marks?` · ${fmtNum(row.marks.score)} / ${fmtNum(row.marks.max)} marks`:''}`;
    return `<strong>${esc(t.title||'Timed test')}</strong><small>${esc(when)}</small><b>${row.missed?'0%':`${row.value}%`}</b><em>${esc(detail)}</em>`;
  }
  function nkMockInsightsSection(){
    const rows=nkMockInsightRows();
    const att=typeof nkSchedAttendance==='function'?nkSchedAttendance():{booked:0,kept:0,streak:0,best:0};
    const hasMarks=rows.some(r=>r.marks);
    const head=`<div class="nk-section-head"><div><div class="nk-kicker">TIMED TESTS</div><h2>Mock tests</h2></div>${hasMarks?`<div class="nk-mock-in-toggle" role="group" aria-label="Chart value">${[['score','Score'],['marks','Marks']].map(([k,l])=>`<button type="button" aria-pressed="${nkMockInsightMode===k}" onclick="window.QB.nkMockInsightSet('${k}')">${l}</button>`).join('')}</div>`:''}</div>`;
    if(!rows.length)return `<section class="nk-section nk-mock-in">${head}<div class="nk-mock-in-empty"><p>Sit a timed test or book a mock, and your scores will build a line here.</p><button type="button" onclick="window.QB.nav('tests')">Go to Tests ${navIcon('chevron',16)}</button></div></section>`;
    const W=640,H=220,padX=18,padTop=22,padBottom=28,n=rows.length;
    const x=i=>n===1?W/2:padX+i*(W-padX*2)/(n-1),y=v=>padTop+(1-v/100)*(H-padTop-padBottom);
    const pts=rows.map((r,i)=>[Math.round(x(i)*10)/10,Math.round(y(r.value)*10)/10]);
    const line=nkMockInsightPath(pts),area=line?`${line} L${pts[pts.length-1][0]},${H-padBottom} L${pts[0][0]},${H-padBottom} Z`:'';
    const values=rows.map(r=>r.value),avg=Math.round(values.reduce((a,b)=>a+b,0)/n),best=Math.max(...values);
    const recent=values.slice(-5),before=values.slice(-10,-5),trend=before.length?Math.round(recent.reduce((a,b)=>a+b,0)/recent.length-before.reduce((a,b)=>a+b,0)/before.length):null;
    const grid=[0,25,50,75,100].map(v=>`<line x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}"/>`).join('');
    const labels=[0,25,50,75,100].map(v=>`<span style="top:${(y(v)/H*100).toFixed(2)}%">${v}</span>`).join('');
    const dots=rows.map((r,i)=>`<i class="${r.missed?'is-missed':r.makeup?'is-makeup':r.scheduled?'is-booked':''}" style="left:${(pts[i][0]/W*100).toFixed(2)}%;top:${(pts[i][1]/H*100).toFixed(2)}%;--d:${Math.min(i,24)*45+500}ms"></i>`).join('');
    const tips=rows.map((r,i)=>`<template data-i="${i}" data-x="${(pts[i][0]/W*100).toFixed(2)}" data-y="${(pts[i][1]/H*100).toFixed(2)}" data-id="${esc(r.t.id)}">${nkMockInsightTip(r,i)}</template>`).join('');
    const stats=[['Average',`${avg}%`,''],['Best',`${best}%`,''],['Trend',trend===null?'—':`${trend>0?'+':''}${trend} pts`,trend===null?'':trend>0?'is-up':trend<0?'is-down':''],['Kept',att.booked?`${fmtNum(att.kept)} / ${fmtNum(att.booked)}`:'—',att.booked&&att.kept<att.booked?'is-down':'']];
    const last=rows[n-1];
    return `<section class="nk-section nk-mock-in">${head}
      <div class="nk-mock-in-card">
        <div class="nk-mock-in-stats">${stats.map(([l,v,c])=>`<div class="${c}"><small>${l}</small><b>${v}</b></div>`).join('')}</div>
        <div class="nk-mock-in-chart" tabindex="0" role="img" aria-label="${n} timed tests, average ${avg}%, best ${best}%. Use the left and right arrow keys to read each test." data-n="${n}">
          <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="nk-mock-in-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="currentColor" stop-opacity=".16"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></linearGradient></defs>
            <g class="nk-mock-in-grid">${grid}</g>
            <line class="nk-mock-in-avg" x1="0" x2="${W}" y1="${y(avg)}" y2="${y(avg)}"/>
            ${area?`<path class="nk-mock-in-area" d="${area}"/>`:''}${line?`<path class="nk-mock-in-line" d="${line}" pathLength="1"/>`:''}
          </svg>
          <div class="nk-mock-in-labels" aria-hidden="true">${labels}</div><div class="nk-mock-in-dots" aria-hidden="true">${dots}</div>
          <i class="nk-mock-in-cursor" aria-hidden="true"></i>
          <div class="nk-mock-in-tip" role="status" aria-live="polite">${nkMockInsightTip(last,n-1)}</div>
          ${tips}
        </div>
        <div class="nk-mock-in-legend"><span><i class="is-test"></i>Timed test</span><span><i class="is-booked"></i>Booked mock</span><span><i class="is-missed"></i>Missed</span><span><i class="is-avg"></i>Average</span></div>
        ${att.booked?`<div class="nk-mock-in-attend"><strong>${att.streak?`${fmtNum(att.streak)} kept in a row`:'Attendance streak broken'}</strong><span>${att.best>1?`Best run ${fmtNum(att.best)}`:'Book a mock to start a run'}</span><span class="nk-sched-attend-dots" aria-hidden="true">${nkSchedList().map(m=>({m,st:nkSchedStatus(m)})).filter(v=>v.st==='taken'||v.st==='missed').sort((a,b)=>a.m.at-b.m.at).slice(-16).map(v=>`<i class="is-${v.st}"></i>`).join('')}</span></div>`:''}
      </div>
    </section>`;
  }
  function nkMockInsightSet(mode){
    nkMockInsightMode=mode==='marks'?'marks':'score';
    const node=document.querySelector('.nk-mock-in');if(node)node.outerHTML=nkMockInsightsSection();
  }
  // Scrubbing: the nearest sitting to the pointer (or the arrow keys) fills the tip and moves the cursor.
  function nkMockInsightShow(chart,index){
    const tpl=chart.querySelector(`template[data-i="${index}"]`);if(!tpl)return;
    chart.dataset.at=String(index);
    const tip=chart.querySelector('.nk-mock-in-tip'),cursor=chart.querySelector('.nk-mock-in-cursor');
    const px=Number(tpl.dataset.x),py=Number(tpl.dataset.y);
    if(tip){tip.innerHTML=tpl.innerHTML;tip.style.setProperty('--x',px+'%');tip.classList.toggle('is-left',px>62);tip.classList.add('is-live');}
    if(cursor){cursor.style.setProperty('--x',px+'%');cursor.style.setProperty('--y',py+'%');cursor.classList.add('is-on');}
    chart.querySelectorAll('.nk-mock-in-dots i').forEach((c,i)=>c.classList.toggle('is-active',i===index));
  }
  function nkMockInsightIndex(chart,clientX){
    const box=chart.getBoundingClientRect(),n=Number(chart.dataset.n)||1,rel=(clientX-box.left)/Math.max(1,box.width)*100;
    let best=0,dist=Infinity;chart.querySelectorAll('template').forEach(t=>{const d=Math.abs(Number(t.dataset.x)-rel);if(d<dist){dist=d;best=Number(t.dataset.i);}});
    return Math.max(0,Math.min(n-1,best));
  }
  document.addEventListener('pointermove',event=>{const chart=event.target instanceof Element&&event.target.closest('.nk-mock-in-chart');if(chart)nkMockInsightShow(chart,nkMockInsightIndex(chart,event.clientX));},{passive:true});
  document.addEventListener('pointerdown',event=>{const chart=event.target instanceof Element&&event.target.closest('.nk-mock-in-chart');if(chart)nkMockInsightShow(chart,nkMockInsightIndex(chart,event.clientX));},{passive:true});
  document.addEventListener('click',event=>{
    const chart=event.target instanceof Element&&event.target.closest('.nk-mock-in-chart');if(!chart)return;
    const i=nkMockInsightIndex(chart,event.clientX),tpl=chart.querySelector(`template[data-i="${i}"]`);
    // The first tap reads a point; a second tap on the same point opens its result.
    if(chart.dataset.opened===String(i)&&tpl)navigate('result',tpl.dataset.id);else{chart.dataset.opened=String(i);nkMockInsightShow(chart,i);}
  });
  document.addEventListener('keydown',event=>{
    const chart=event.target instanceof Element&&event.target.closest('.nk-mock-in-chart');if(!chart)return;
    const n=Number(chart.dataset.n)||1,at=chart.dataset.at===undefined?n-1:Number(chart.dataset.at);
    if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();nkMockInsightShow(chart,Math.max(0,Math.min(n-1,at+(event.key==='ArrowLeft'?-1:1))));}
    else if(event.key==='Enter'){const tpl=chart.querySelector(`template[data-i="${at}"]`);if(tpl)navigate('result',tpl.dataset.id);}
  });
  if(typeof analytics==='function'){
    const original=analytics;
    analytics=function(){
      if(typeof nkSchedRecordMisses==='function')nkSchedRecordMisses();
      const html=original.apply(this,arguments);
      return html.includes('<details class="nk-li-methods">')?html.replace('<details class="nk-li-methods">',nkMockInsightsSection()+'<details class="nk-li-methods">'):html;
    };
  }
  /* NK_MOCK_INSIGHTS_V1_END */
