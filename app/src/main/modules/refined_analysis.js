  /* NK_REFINED_ANALYSIS_V1_START */
  let nkAnalysisTab='topic',nkAnalysisTimeMode='bins';
  function nkAnalysisIcon(name,size=18){
    const path=name==='minus'?'<path d="M6 12h12"/>':name==='edit'?'<path d="m15 4 5 5-11 11H4v-5L15 4Z"/><path d="m12 7 5 5"/>':'<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M10 2h4M12 2v3"/>';
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`;
  }
  function nkAnalysisTest(id){return (state.tests||[]).find(t=>String(t.id)===String(id));}
  function nkAnalysisDuration(ms){
    if(!Number.isFinite(ms)||ms<0)return '—';
    const seconds=Math.round(ms/1000),minutes=Math.floor(seconds/60);
    // One format: "43s" under a minute, "2m 10s" above it, "1h 5m" past an hour.
    return minutes>=60?`${Math.floor(minutes/60)}h ${minutes%60}m`:minutes?`${minutes}m ${seconds%60}s`:`${seconds}s`;
  }
  function nkAnalysisOutcomes(t){
    const timeUp=(t.questionIds||[]).filter(id=>t.expired?.[id]&&!t.answers?.[id]).length,omitted=Math.max(0,(Number(t.unattempted)||0)-timeUp);
    return [['Correct',Number(t.correct)||0,'correct','check'],['Incorrect',Number(t.incorrect)||0,'incorrect','close'],...(timeUp?[['Time up',timeUp,'timeup','clock']]:[]),['Omitted',omitted,'omitted','minus']];
  }
  // marks: with negative marking the headline score is marks earned out of the maximum, as in the exam.
  function nkAnalysisRing(t,scoreOnly=false,marks=null){
    const total=Number(t.total)||0,w=total?t.incorrect/total*100:0;
    const c=scoreOnly&&marks&&Number(marks.max)>0?Math.max(0,Math.min(100,Number(marks.score)/Number(marks.max)*100)):total?t.correct/total*100:0;
    const fill=!total?'#edeaf5':scoreOnly?`conic-gradient(var(--na-green) 0 ${c}%,#eceaf4 ${c}% 100%)`:`conic-gradient(var(--na-green) 0 ${c}%,var(--na-red) ${c}% ${c+w}%,var(--na-amber) ${c+w}% 100%)`;
    return `<div class="nk-na-ring" style="--na-ring:${fill}" role="img" aria-label="${scoreOnly?'Score':'Question performance'}: ${t.correct||0} correct, ${t.incorrect||0} incorrect, ${t.unattempted||0} omitted"><span><b>${scoreOnly?fmtPct(c):fmtNum(total)}</b><small>${scoreOnly?'Score':'questions'}</small></span></div>`;
  }
  function nkAnalysisRows(t,tab=nkAnalysisTab){
    const analysis=nkCbtResultAnalysis(t);
    if(tab==='topic')return analysis;
    const subjects=new Map();
    for(const topic of analysis.rows){const row=subjects.get(topic.subject)||{title:topic.subject,subject:topic.subject,bank:'',total:0,correct:0,incorrect:0,unattempted:0};for(const key of ['total','correct','incorrect','unattempted'])row[key]+=topic[key];subjects.set(topic.subject,row);}
    return {...analysis,rows:[...subjects.values()].sort((a,b)=>a.title.localeCompare(b.title))};
  }
  function nkAnalysisRow(row){
    const outcomes=[['correct',row.correct,'Correct'],['incorrect',row.incorrect,'Incorrect'],['omitted',row.unattempted,'Unattempted']];
    return `<article class="nk-cbt-analysis-row nk-na-row"><header><span><strong>${esc(row.title)}</strong>${row.bank?`<small>${esc(row.subject)} · ${esc(row.bank)}</small>`:''}</span><b>${row.correct}<small> / ${row.total} correct</small></b></header><div class="nk-na-row-bar" role="img" aria-label="${esc(row.title)}: ${row.correct} correct, ${row.incorrect} incorrect, ${row.unattempted} unattempted">${outcomes.filter(([,n])=>n>0).map(([tone,n])=>`<i class="is-${tone}" style="width:${row.total?n/row.total*100:0}%"></i>`).join('')}</div><div class="nk-na-row-counts">${outcomes.map(([tone,n,label])=>`<span class="is-${tone}"><i aria-hidden="true"></i><b>${n}</b> ${label}</span>`).join('')}</div></article>`;
  }
  function nkAnalysisBreakdown(t){
    const analysis=nkAnalysisRows(t),focus=analysis.rows.filter(r=>r.incorrect+r.unattempted>0),rest=analysis.rows.filter(r=>r.incorrect+r.unattempted===0),ordered=[...focus,...rest],visible=ordered.slice(0,6),hidden=ordered.slice(6);
    return `<section class="nk-na-card nk-cbt-analysis"><div class="nk-na-tabs" role="group" aria-label="Performance breakdown">${[['subject','Subject-wise'],['topic','Topic-wise']].map(([tab,label])=>`<button aria-pressed="${nkAnalysisTab===tab}" onclick="window.QB.nkAnalysisSetTab('${tab}',${esc(JSON.stringify(String(t.id)))})">${label}</button>`).join('')}</div><header><h2>${nkAnalysisTab==='subject'?'Subject':'Topic'} breakdown</h2><small>Correct / Total</small></header><div class="nk-cbt-analysis-list">${visible.map(nkAnalysisRow).join('')}${hidden.length?`<details class="nk-cbt-analysis-rest"><summary>${hidden.length} more ${nkAnalysisTab==='subject'?'subjects':'topics'}</summary>${hidden.map(nkAnalysisRow).join('')}</details>`:''}</div>${analysis.unavailable?`<p class="nk-na-note">${analysis.unavailable} saved questions are unavailable in the current banks.</p>`:''}</section>`;
  }
  function nkAnalysisTimeData(t){
    const bins=[0,0,0,0,0];let missing=0;
    for(const id of new Set(t.questionIds||[])){const value=Object.prototype.hasOwnProperty.call(t.questionTimes||{},id)?t.questionTimes[id]:null;if(typeof value!=='number'||!Number.isFinite(value)||value<0){missing++;continue;}bins[value<30000?0:value<60000?1:value<120000?2:value<=180000?3:4]++;}
    let total=0;const counts=nkAnalysisTimeMode==='cumulative'?bins.map(n=>total+=n):bins;
    return {counts,bins,missing,recorded:bins.reduce((a,b)=>a+b,0)};
  }
  // Time on every question, in the order sat: bar height is the time, colour is the outcome, the line is the
  // per-question limit (or one minute in practice). One chart answers both "how long" and "within time".
  function nkAnalysisTimeChart(t){
    const ids=[...new Set(t.questionIds||[])],limit=Number(t.secondsPerQuestion)||60;
    const rows=ids.map((id,i)=>{const ms=t.questionTimes?.[id],sel=t.answers?.[id],q=(typeof nkBankQuestionById==='function'?nkBankQuestionById(id):BY_ID?.[id]),right=sel&&q&&Number(q.correctOption)===Number(sel);
      return {id,i,s:typeof ms==='number'&&Number.isFinite(ms)&&ms>=0?ms/1000:null,tone:sel?(right?'correct':'incorrect'):t.expired?.[id]?'timeup':'omitted'};});
    const timed=rows.filter(r=>r.s!=null);
    if(!timed.length)return `<section class="nk-na-card nk-na-time nk-pace"><header><h2>Time per question</h2></header><p class="nk-na-note">Question timing was not recorded.</p></section>`;
    const fmt=s=>s<60?`${Math.round(s)} s`:`${Math.floor(s/60)}m ${String(Math.round(s%60)).padStart(2,'0')}s`;
    // Facts count only questions that were opened: a never-visited question's zero is not "within time".
    const seen=timed.filter(r=>r.s>0),sorted=(seen.length?seen:timed).map(r=>r.s).sort((a,b)=>a-b),mid=sorted.length>>1;
    const median=sorted.length%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2;
    const within=seen.filter(r=>r.s<=limit).length,over=seen.length-within;
    const rushed=timed.filter(r=>r.tone==='incorrect'&&r.s<Math.min(15,limit/3)).length;
    const top=Math.max(limit*1.5,Math.min(limit*3,sorted[sorted.length-1])),h=s=>Math.max(3,Math.min(1,s/top)*100);
    const label={correct:'Correct',incorrect:'Wrong',timeup:'Time up',omitted:'Not answered'};
    const bars=rows.map(r=>r.s==null?`<i class="is-none" aria-hidden="true"></i>`:`<button type="button" class="is-${r.tone}${r.s>top?' is-clipped':''}" style="--h:${h(r.s).toFixed(1)}%;--k:${Math.min(r.i,80)}" aria-label="Question ${r.i+1}: ${fmt(r.s)}, ${label[r.tone]}" title="Q${r.i+1} · ${fmt(r.s)} · ${label[r.tone]}" onclick="window.QB.nkResultReviewAt(${esc(JSON.stringify(String(t.id)))},${esc(JSON.stringify(String(r.id)))})"></button>`).join('');
    const tones=['correct','incorrect','timeup','omitted'].filter(k=>timed.some(r=>r.tone===k));
    const facts=[`<span><b>${fmtNum(within)}</b> of ${fmtNum(seen.length)} within ${fmt(limit)}</span>`,`<span>Median <b>${fmt(median)}</b></span>`,rushed?`<span><b>${fmtNum(rushed)}</b> wrong in under ${fmt(Math.min(15,limit/3))}</span>`:over?`<span><b>${fmtNum(over)}</b> over the line</span>`:''].filter(Boolean).join('');
    const missing=rows.length-timed.length;
    return `<section class="nk-na-card nk-na-time nk-pace"><header><h2>Time per question</h2></header>
      <p class="nk-pace-facts">${facts}</p>
      <div class="nk-pace-chart" style="--line:${(limit/top*100).toFixed(1)}%"><div class="nk-pace-bars${rows.length>40?' is-dense':''}" role="group" aria-label="Time on each question, in order. The line marks ${fmt(limit)}.">${bars}</div><em class="nk-pace-line" aria-hidden="true"><span>${fmt(limit)}</span></em></div>
      <div class="nk-pace-axis" aria-hidden="true"><span>Q1</span><span>Q${rows.length}</span></div>
      <ul class="nk-pace-key">${tones.map(k=>`<li><i class="is-${k}"></i>${label[k]}</li>`).join('')}</ul>
      ${missing?`<p class="nk-na-note">${fmtNum(missing)} question${missing===1?' has':'s have'} no saved time.</p>`:''}</section>`;
  }
  function nkAnalysisSetTab(tab,id){if(!['topic','subject'].includes(tab))return;nkAnalysisTab=tab;const t=nkAnalysisTest(id),node=document.querySelector('.nk-na-card.nk-cbt-analysis');if(t&&node){if(typeof nkPolishReplaceSurface==='function')nkPolishReplaceSurface(node,nkAnalysisBreakdown(t));else node.outerHTML=nkAnalysisBreakdown(t);}}
  function nkAnalysisSetTime(mode,id){if(!['bins','cumulative'].includes(mode))return;nkAnalysisTimeMode=mode;const t=nkAnalysisTest(id),node=document.querySelector('.nk-na-time');if(t&&node){if(typeof nkPolishReplaceSurface==='function')nkPolishReplaceSurface(node,nkAnalysisTimeChart(t));else node.outerHTML=nkAnalysisTimeChart(t);}}
  function nkAnalysisFollowup(t){
    const analysis=nkCbtResultAnalysis(t),ids=typeof nkFsrsUnresolvedResultMisses==='function'?nkFsrsUnresolvedResultMisses(t,analysis.missedIds):analysis.missedIds,corrected=analysis.missedIds.length-ids.length;
    return `<div class="nk-cbt-followup nk-na-followup"><strong>${ids.length?`${ids.length} questions to revisit`:corrected?'All original misses corrected':'No missed questions'}</strong>${ids.length?`<button onclick="window.QB.nkCbtPracticeMisses(this.getAttribute('data-test-id'),event)" data-test-id="${esc(t.id)}">Practise missed questions ${navIcon('chevron',16)}</button>`:''}</div>`;
  }
  function nkAnalysisMarked(t){
    const ids=typeof nkMarkedTestIds==='function'?nkMarkedTestIds(t):[];
    return ids.length?`<section class="nk-cbt-marked nk-na-followup" aria-label="Marked questions"><strong>${ids.length} marked for review</strong><button data-test-id="${esc(t.id)}" onclick="window.QB.nkCbtPracticeMarked(this.getAttribute('data-test-id'),event)">Practise marked questions ${navIcon('chevron',16)}</button></section>`:'';
  }
  // Average over answered questions only; omitted ones would dilute it.
  function nkAnalysisAnsweredAverage(t,totalTime){
    const answered=[...new Set(t.questionIds||[])].filter(id=>t.answers?.[id]);
    if(!answered.length)return null;
    const times=answered.map(id=>t.questionTimes?.[id]);
    if(times.every(v=>typeof v==='number'&&Number.isFinite(v)&&v>=0))return times.reduce((a,b)=>a+b,0)/answered.length;
    return totalTime===null?null:totalTime/answered.length;
  }
  // One cell per question, in order: the whole sitting at a glance. A tap opens that question's solution.
  function nkResultStrip(t){
    const ids=t.questionIds||[];if(!ids.length)return '';
    const cells=ids.map((id,i)=>{const sel=t.answers?.[id],q=(typeof nkBankQuestionById==='function'?nkBankQuestionById(id):BY_ID?.[id]),right=q&&Number(q.correctOption)===Number(sel);const tone=sel?(right?'correct':'incorrect'):t.expired?.[id]?'timeup':'omitted';const label=sel?(right?'Correct':'Incorrect'):tone==='timeup'?'Time up':'Omitted';
      return `<button type="button" class="is-${tone}" style="--i:${Math.min(i,60)}" aria-label="Question ${i+1}: ${label}" onclick="window.QB.nkResultReviewAt(${esc(JSON.stringify(String(t.id)))},${esc(JSON.stringify(String(id)))})"></button>`;}).join('');
    return `<section class="nk-na-card nk-rs-strip-card"><header><h2>Question by question</h2><small>Tap one to see its solution</small></header><div class="nk-rs-strip${ids.length>60?' is-dense':''}">${cells}</div></section>`;
  }
  function nkResultVerdict(t){
    const total=Number(t.total)||0,c=Number(t.correct)||0,answered=c+(Number(t.incorrect)||0);
    if(!total||!answered)return 'Nothing answered this time.';
    const pct=c/total*100;
    return pct>=85?'Excellent work.':pct>=70?'Strong result.':pct>=50?'Solid, with room to grow.':pct>=30?'Getting there. Review the misses.':'A tough set. The misses are where you learn.';
  }
  // Practice sessions: only the topics where an answer went wrong, worst first.
  function nkResultPracticeTopics(t){
    // One topic means the summary above already says it all.
    if(nkCbtResultAnalysis(t).rows.length<2)return '';
    const rows=nkCbtResultAnalysis(t).rows.filter(r=>r.incorrect>0).sort((a,b)=>b.incorrect-a.incorrect||(b.incorrect/b.total)-(a.incorrect/a.total)||a.title.localeCompare(b.title));
    if(!rows.length)return '';
    const visible=rows.slice(0,4),hidden=rows.slice(4);
    return `<section class="nk-na-card nk-rs-topics"><header><h2>Where you slipped</h2><small>Correct / Total</small></header><div class="nk-cbt-analysis-list">${visible.map(nkAnalysisRow).join('')}${hidden.length?`<details class="nk-cbt-analysis-rest"><summary>${hidden.length} more topics</summary>${hidden.map(nkAnalysisRow).join('')}</details>`:''}</div></section>`;
  }
  function nkResultReviewAt(testId,questionId){
    if(window.__QB_OPEN_REVIEW(testId)===false)return;
    const s=state.activeSession;if(!s||s.mode!=='review')return;
    const index=s.questionIds.findIndex(id=>String(id)===String(questionId));
    if(index>=0&&index!==s.index){s.index=index;saveState();render();}
  }
  resultPage=function(testId){
    const t=nkAnalysisTest(testId);if(!t)return testsPage();
    const practice=t.kind==='practice',attempted=Number(t.correct||0)+Number(t.incorrect||0),accuracy=attempted?fmtPct(t.correct/attempted*100):'—',score=t.total?fmtPct(t.correct/t.total*100):'0%',totalTime=typeof t.totalTimeMs==='number'?t.totalTimeMs:null;
    const chapterId=/^chapter\/(.+)$/.exec(String(t.originHash||''))?.[1];
    const origin=t.originRoute||(practice?'topics':'tests'),browse=/^revision-browse\/(wrong|bookmarks)$/.exec(origin);
    const backLabel=browse?(browse[1]==='wrong'?'Mistakes':'Bookmarks'):chapterId?'topic':origin;
    const [backPage,backId]=browse?['revision-browse',browse[1]]:chapterId?['chapter',decodeURIComponent(chapterId)]:[String(origin),''];
    const backAction=`window.QB.nkResultBack(${esc(JSON.stringify(backPage))},${esc(JSON.stringify(backId))})`;
    const questionMap=new Map();(t.questionIds||[]).forEach(id=>{const q=nkBankQuestionById(id);if(q){questionMap.set(String(id),q);BY_ID[id]=q;}});
    const module=t.studyModuleId&&nkFindStudyModule(t.studyModuleId);
    const marks=!practice&&t.marking&&!nkExamIsPlain(t.marking)?nkExamMarks(t):null;
    return shell(`<main class="nk-app-v114 nk-result-v114 nk-refined-analysis"><header class="nk-na-head"><button class="nk-na-back" aria-label="Back to ${esc(backLabel)}" onclick="${backAction}">${navIcon('back',22)}</button><h1>${practice?'Practice':'Test'} analysis</h1></header><div class="nk-na-name"><span>${navIcon(practice?'book':'test',19)}</span><div><strong>${esc(t.title||'Untitled test')}</strong><small>${fmtDate(t.createdAt)}</small></div>${!practice?`<button aria-label="Rename test" onclick="document.getElementById('nk-na-rename').hidden=false;document.getElementById('nk-na-title').focus()">${nkAnalysisIcon('edit',18)}</button>`:''}</div>${!practice?`<form id="nk-na-rename" hidden novalidate onsubmit="event.preventDefault();window.QB.nkAnalysisRename(${esc(JSON.stringify(String(t.id)))})"><label for="nk-na-title">Test name</label><input id="nk-na-title" required maxlength="80" aria-describedby="nk-na-rename-status" oninput="if(this.value.trim()){this.removeAttribute('aria-invalid');document.getElementById('nk-na-rename-status').textContent='';}" value="${esc(t.title||'')}"><button type="submit">Save name</button><small id="nk-na-rename-status" role="status"></small></form>`:''}
      <section class="nk-na-card nk-na-summary nk-result-overview">${nkAnalysisRing(t,true,marks)}<div><div class="nk-result-percentages"><strong>${t.correct} / ${t.total}</strong><span>Correct answers</span><span class="nk-na-accuracy">Accuracy <b>${accuracy}</b></span><em class="nk-rs-verdict">${esc(nkResultVerdict(t))}</em><span class="nk-na-sr">Score: ${marks&&Number(marks.max)>0?`${fmtPct(Math.max(0,Number(marks.score)/Number(marks.max)*100))} of marks`:`all questions ${score}`}. Accuracy: answered questions ${accuracy}. ${attempted} answered.</span></div><div class="nk-na-outcome-counts nk-result-counts">${nkAnalysisOutcomes(t).map(([label,n,tone,icon])=>`<div class="is-${tone}"><span>${icon==='minus'?nkAnalysisIcon('minus',14):navIcon(icon,14)}</span><b>${n}</b><small>${label}</small></div>`).join('')}</div></div></section>
      <div class="nk-na-metrics${marks?' has-marks':''}">${[...(marks?[['star','Marks',`${(typeof fmtMarks==='function'?fmtMarks:fmtNum)(marks.score)} / ${(typeof fmtMarks==='function'?fmtMarks:fmtNum)(marks.max)}`,nkMarkingLabel(marks)]]:[]),['clock','Time taken',nkAnalysisDuration(totalTime)],['stopwatch','Avg. time / Q',nkAnalysisDuration(nkAnalysisAnsweredAverage(t,totalTime))]].map(([icon,label,value,note])=>`<article><span>${icon==='stopwatch'?nkAnalysisIcon('stopwatch',21):navIcon(icon,21)}</span><div><small>${label}</small><b>${value}</b>${note?`<em>${esc(note)}</em>`:''}</div></article>`).join('')}</div>
      ${nkResultStrip(t)}<div class="nk-na-analysis-grid">${!practice?nkAnalysisBreakdown(t):nkResultPracticeTopics(t)}<section class="nk-na-card nk-na-performance"><header><h2>Question performance</h2></header><div>${nkAnalysisRing(t)}<dl>${nkAnalysisOutcomes(t).map(([label,n,tone])=>`<div><dt><i class="is-${tone}"></i>${label}</dt><dd>${n}<small>${t.total?Math.round(n/t.total*100):0}%</small></dd></div>`).join('')}</dl></div></section>${nkAnalysisTimeChart(t)}</div>
      <div class="nk-na-actions"><button class="v102-review-action" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))">Review Solutions</button>${!practice&&t.timerMode!=='per-question'?`<button class="is-secondary" data-test-id="${esc(t.id)}" onclick="window.QB.nkCbtRetake(this.getAttribute('data-test-id'),event)">Retry Test</button>`:''}</div>
      ${practice?nkCorrectionResultSection(t):nkAnalysisFollowup(t)+nkAnalysisMarked(t)}${!practice?nkCbtComparisonSection(t):''}${!practice?(nkMockFor(t)?nkMockSavedMarkup(nkMockFor(t)):`<button type="button" class="nk-na-save-mock" data-test-id="${esc(t.id)}" onclick="window.QB.nkMockSaveResult(this.getAttribute('data-test-id'))">${navIcon('bookmark',17)}<span>Save as mock</span></button>`):''}${module?`<section class="nk-na-card nk-module-result"><header><h2>${esc(module.name)}</h2></header><div class="nk-module-result-actions"><button onclick="window.QB.restartStudyModule(this.getAttribute('data-module-id'))" data-module-id="${esc(module.id)}">Restart module</button><button onclick="window.QB.nav('dashboard')">Return Home</button></div></section>`:''}
      <details class="nk-na-card nk-na-answers"><summary>Every answer</summary><div class="nk-result-questions">${(t.questionIds||[]).map((id,i)=>{const q=questionMap.get(String(id)),sel=t.answers?.[id],correct=q&&Number(q.correctOption)===Number(sel);return `<div><span class="nk-question-index">${i+1}</span><span><strong>${q?esc(q.question.slice(0,125)):esc('Saved question unavailable')}</strong><small><i class="nk-status ${sel?(correct?'is-correct':'is-wrong'):'is-unattempted'}">${sel?(correct?'Correct':'Incorrect'):t.expired?.[id]?'Time up':'Omitted'}</i>${q?esc(q.chapter||''):''}</small></span></div>`;}).join('')}</div></details></main>`,'tests');
  };
  function nkAnalysisRename(id){
    const t=nkAnalysisTest(id),input=document.getElementById('nk-na-title'),status=document.getElementById('nk-na-rename-status'),value=input?.value.trim().slice(0,80);
    if(!t)return;
    if(!value){input?.setAttribute?.('aria-invalid','true');if(status)status.textContent='Enter a test name.';input?.focus?.({preventScroll:true});return;}
    input?.removeAttribute?.('aria-invalid');
    const prior=t.title,priorUpdatedAt=t.updatedAt;t.title=value;t.updatedAt=Date.now();
    if(saveState()===false){t.title=prior;if(priorUpdatedAt===undefined)delete t.updatedAt;else t.updatedAt=priorUpdatedAt;if(status)status.textContent='Could not save the name. Your text is still here.';return;}
    render();
    document.querySelector?.('.nk-na-name button')?.focus({preventScroll:true});
  }
  function nkMockList(){return Array.isArray(state.savedMocks)?state.savedMocks:[];}
  function nkMockStore(name,ids){
    if(nkMockList().length>=100){showToast('Your saved mocks are full. Remove one before saving another.','bad');return null;}
    const now=Date.now(),mock={id:`mock_${now}_${Math.random().toString(36).slice(2,9)}`,name:String(name||'Timed CBT').trim().slice(0,80),questionIds:ids.map(String),createdAt:now,updatedAt:now};
    const before=state.savedMocks;state.savedMocks=[...nkMockList(),mock];if(saveState()===false){state.savedMocks=before;return null;}return mock;
  }
  function nkMockPick(){const pool=nkCbtPool().filter(q=>nkQuestionPresentationFor(q).valid),ids=pool.map(q=>String(q.id));for(let i=ids.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[ids[i],ids[j]]=[ids[j],ids[i]];}return ids.slice(0,Math.min(Math.max(1,Number(nkCbtDraft.count||20)),ids.length));}
  function nkMockName(value){if(nkCbtDraft)nkCbtDraft.name=String(value).slice(0,80);}
  function nkMockSaveDraft(){if(!nkCbtDraft)return;const ids=nkMockPick();if(!ids.length){showToast('No questions in this selection can be saved as a mock.','bad');return;}const mock=nkMockStore(nkCbtDraft.name||nkCbtTitle(),ids);if(mock){nkCbtDraft=null;showToast('Mock saved.','good');navigate('tests');}}
  const nkAnalysisOriginalCbtStart=nkCbtStart;
  nkCbtStart=function(){if(!nkCbtDraft?.name?.trim())return nkAnalysisOriginalCbtStart();let mock=nkMockList().find(m=>m.id===nkCbtDraft.savedMockId);if(!mock){const ids=nkMockPick();if(!ids.length)return nkAnalysisOriginalCbtStart();mock=nkMockStore(nkCbtDraft.name,ids);}if(mock){nkCbtDraft.savedMockId=mock.id;if(nkMockStart(mock.id)!==false)nkCbtDraft=null;}};
  function nkMockStart(id){
    const mock=nkMockList().find(m=>String(m.id)===String(id));if(!mock)return false;
    const map=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),ids=mock.questionIds||[];
    if(!ids.length||new Set(ids).size!==ids.length||ids.some(id=>!map.has(String(id))||!nkQuestionPresentationFor(map.get(String(id))).valid)){showToast('Some saved questions are unavailable. This mock cannot start.','bad');return false;}
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(id=>[id,map.get(String(id))]))};
    const initial=(state.tests||[]).filter(t=>t.kind!=='practice'&&t.timerMode!=='per-question'&&nkCbtSameQuestions(t,{questionIds:ids})).sort((a,b)=>Number(a.createdAt)-Number(b.createdAt))[0];
    const started=startSession(ids,'exam',mock.name,initial?`cbt-retake:${String(initial.id)}`:`saved-mock:${mock.id}`);
    // A mock named like "wrong" or "bookmarks" still belongs to Tests.
    if(started!==false&&state.activeSession){state.activeSession.originRoute='tests';saveState();}
    return started;
  }
  function nkMockFor(t){return t&&t.kind!=='practice'?nkMockList().find(m=>nkCbtSameQuestions(t,m)):null;}
  function nkMockSavedMarkup(m){return `<div class="nk-na-mock-saved" data-mock-id="${esc(m.id)}"><span class="nk-na-mock-saved-icon">${navIcon('check',16)}</span><div role="status"><strong>Saved as mock</strong><small>${esc(m.name)}</small></div><button type="button" data-mock-id="${esc(m.id)}" onclick="window.QB.nkMockRenameInline(this.getAttribute('data-mock-id'))">Rename</button></div>`;}
  function nkMockSaveResult(id){
    const t=nkAnalysisTest(id);if(!t||t.kind==='practice')return;
    const mock=nkMockFor(t)||nkMockStore(t.title,t.questionIds);if(!mock)return;
    const button=document.querySelector?.(`.nk-na-save-mock[data-test-id="${String(id).replace(/["\\]/g,'\\$&')}"]`);
    if(button){button.outerHTML=nkMockSavedMarkup(mock);document.querySelector?.('.nk-na-mock-saved button')?.focus({preventScroll:true});}
    else showToast('Mock saved to Tests.','good');
  }
  // Rename straight from the result card: the saved state turns into a one-field form.
  function nkMockRenameInline(id,cancel){
    const card=[...(document.querySelectorAll?.('.nk-na-mock-saved')||[])].find(n=>n.getAttribute('data-mock-id')===String(id)),m=nkMockList().find(x=>String(x.id)===String(id));
    if(!card||!m)return;
    if(cancel){card.outerHTML=nkMockSavedMarkup(m);return;}
    card.classList.add('is-editing');
    card.innerHTML=`<form class="nk-na-mock-rename" novalidate onsubmit="event.preventDefault();window.QB.nkMockRename(this.getAttribute('data-mock-id'),this.elements.name.value)" data-mock-id="${esc(m.id)}"><label for="nk-mock-inline-name">Mock name</label><input id="nk-mock-inline-name" name="name" maxlength="80" required value="${esc(m.name)}" onkeydown="if(event.key==='Escape')window.QB.nkMockRenameInline(this.form.getAttribute('data-mock-id'),true)"><div><button type="button" onclick="window.QB.nkMockRenameInline(this.form.getAttribute('data-mock-id'),true)">Cancel</button><button type="submit">Save</button></div><small role="status"></small></form>`;
    const input=card.querySelector('input');input?.focus({preventScroll:true});input?.select?.();
  }
  function nkMockRename(id,value){
    const m=nkMockList().find(x=>String(x.id)===String(id)),name=String(value||'').trim().slice(0,80);if(!m)return false;
    const status=document.querySelector?.('.nk-na-mock-rename small, .nk-mock-rename small');
    if(!name){if(status)status.textContent='Enter a name.';return false;}
    const prior=m.name,priorAt=m.updatedAt;m.name=name;m.updatedAt=Date.now();
    if(saveState()===false){m.name=prior;m.updatedAt=priorAt;if(status)status.textContent='Could not save the name. Try again.';return false;}
    const card=[...(document.querySelectorAll?.('.nk-na-mock-saved')||[])].find(n=>n.getAttribute('data-mock-id')===String(id));
    if(card){card.outerHTML=nkMockSavedMarkup(m);document.querySelector?.('.nk-na-mock-saved button')?.focus({preventScroll:true});}
    if(document.getElementById?.('nk-mock-sheet')?.remove){render();nkMockOpen(id);}
    return true;
  }
  // Composition of a saved set, computed from the bank so older mocks get details too.
  function nkMockSummary(m,map){
    const ids=(m.questionIds||[]).map(String),subjects=new Map(),banks=new Map(),topics=new Map();let missing=0;
    for(const id of ids){
      const q=map.get(id);if(!q){missing++;continue;}
      const subject=String(q.subject||'Other').replace(/^UWorld · /,''),bank=String(q.bank||(String(q.subject||'').startsWith('UWorld')?'UWorld':'PrepLadder')),topic=String(q.chapter||q.topic||'Untitled topic');
      subjects.set(subject,(subjects.get(subject)||0)+1);banks.set(bank,(banks.get(bank)||0)+1);
      // Banks reuse titles such as "Previous Year Questions"; each bank topic keeps its own row.
      const key=[subject,bank,q.chapterId??topic].join('\u0000'),row=topics.get(key)||{title:topic,subject,bank,count:0};row.count++;topics.set(key,row);
    }
    const sort=entries=>[...entries].sort((a,b)=>b[1]-a[1]||String(a[0]).localeCompare(String(b[0])));
    const attempts=(state.tests||[]).filter(t=>t.kind!=='practice'&&nkCbtSameQuestions(t,m)).sort((a,b)=>Number(b.createdAt)-Number(a.createdAt));
    return {total:ids.length,missing,subjects:sort(subjects),banks:sort(banks),topics:[...topics.values()].sort((a,b)=>b.count-a.count||a.title.localeCompare(b.title)),attempts};
  }
  // The same score as the result ring: with negative marking, marks earned out of the maximum.
  function nkMockScore(t){
    if(!t||!t.total)return 0;
    const marks=t.marking&&typeof nkExamIsPlain==='function'&&!nkExamIsPlain(t.marking)&&typeof nkExamMarks==='function'?nkExamMarks(t):null;
    if(marks&&Number(marks.max)>0)return Math.max(0,Math.round(Number(marks.score)/Number(marks.max)*100));
    return Math.round(Number(t.correct||0)/Number(t.total)*100);
  }
  function nkMockDay(ts){const d=new Date(Number(ts||0));return Number.isNaN(d.getTime())?'':d.toLocaleDateString(undefined,{day:'numeric',month:'short',year:d.getFullYear()===new Date().getFullYear()?undefined:'numeric'});}
  function nkMockGraphic(subject,size){return typeof nkSubjectGraphic==='function'?nkSubjectGraphic(subject,size):navIcon('test',size);}
  let nkMockOpener=null;
  function nkMockClose(){
    const sheet=document.getElementById?.('nk-mock-sheet');if(!sheet)return;sheet.remove?.();
    // Keyboard users land back on the mock row that opened the sheet.
    const opener=nkMockOpener,id=sheet.querySelector?.('[data-mock-id]')?.getAttribute('data-mock-id');nkMockOpener=null;
    const target=opener?.isConnected?opener:[...(document.querySelectorAll?.('#app [data-mock-id]')||[])].find(n=>n.getAttribute('data-mock-id')===id&&n.matches?.('button,[tabindex]'));
    target?.focus?.({preventScroll:true});
  }
  function nkMockOpen(id){
    if(typeof document==='undefined'||!document.body?.insertAdjacentHTML)return false;
    const m=nkMockList().find(x=>String(x.id)===String(id));if(!m)return false;
    const opener=document.getElementById?.('nk-mock-sheet')?nkMockOpener:document.activeElement;nkMockClose();nkMockOpener=opener&&opener!==document.body?opener:null;
    const map=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),sum=nkMockSummary(m,map),arg=esc(JSON.stringify(String(m.id)));
    const stack=sum.subjects.map(([name,n],i)=>`<i style="--nk-share:${n/sum.total*100}%;--nk-tone:${i}" title="${esc(name)} ${n}"></i>`).join('');
    const legend=sum.subjects.map(([name,n],i)=>`<li style="--nk-tone:${i}"><span class="nk-mock-dot"></span><span class="nk-mock-legend-name">${esc(name)}</span><b>${n}</b><small>${Math.round(n/sum.total*100)}%</small></li>`).join('');
    const topic=t=>`<li><span><strong>${esc(t.title)}</strong>${sum.subjects.length>1||sum.banks.length>1?`<small>${esc(sum.banks.length>1?`${t.subject} · ${t.bank}`:t.subject)}</small>`:''}</span><b>${t.count}</b></li>`;
    const first=sum.topics.slice(0,5),rest=sum.topics.slice(5);
    const attempts=sum.attempts.slice(0,5).map(t=>`<li><span>${esc(nkMockDay(t.createdAt))}</span><span class="nk-mock-attempt-bar"><i style="width:${nkMockScore(t)}%"></i></span><b>${nkMockScore(t)}%</b></li>`).join('');
    const blocked=sum.missing>0;
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-mock-sheet-backdrop" id="nk-mock-sheet" onclick="if(event.target===this)window.QB.nkMockClose()" onkeydown="if(event.key==='Escape'){event.stopPropagation();window.QB.nkMockClose()}"><section class="modal card nk-mock-sheet" role="dialog" aria-modal="true" aria-labelledby="nk-mock-sheet-title" data-mock-id="${esc(m.id)}">
      <header class="nk-mock-sheet-head"><span class="nk-mock-sheet-icon" aria-hidden="true">${nkMockGraphic(sum.subjects[0]?.[0]||'',22)}</span><div class="nk-mock-sheet-title"><h2 id="nk-mock-sheet-title">${esc(m.name)}</h2><small>Saved ${esc(nkMockDay(m.createdAt))}</small></div><button type="button" class="nk-modal-close" aria-label="Close" onclick="window.QB.nkMockClose()">${navIcon('close',20)}</button></header>
      <div class="nk-mock-sheet-body">
        <dl class="nk-mock-facts"><div><dt>Questions</dt><dd>${sum.total}</dd></div><div><dt>Time limit</dt><dd>${fmtNum(Math.round(sum.total*(typeof nkExamSettings==='function'?Number(nkExamSettings().seconds)||60:60)/60))} min</dd></div><div><dt>${sum.attempts.length?'Best score':'Attempts'}</dt><dd>${sum.attempts.length?Math.max(...sum.attempts.map(nkMockScore))+'%':'None yet'}</dd></div></dl>
        ${blocked?`<p class="nk-mock-warning" role="alert">${sum.missing} of ${sum.total} questions are no longer in the bank, so this mock cannot start.</p>`:''}
        ${sum.subjects.length?`<section class="nk-mock-block"><h3>Subjects</h3><div class="nk-mock-stack" aria-hidden="true">${stack}</div><ul class="nk-mock-legend">${legend}</ul></section>`:''}
        ${sum.topics.length?`<section class="nk-mock-block"><h3>Topics <span>${sum.topics.length}</span></h3><ul class="nk-mock-topics">${first.map(topic).join('')}</ul>${rest.length?`<details class="nk-mock-more"><summary>${rest.length} more ${rest.length===1?'topic':'topics'}</summary><ul class="nk-mock-topics">${rest.map(topic).join('')}</ul></details>`:''}</section>`:''}
        ${sum.banks.length?`<section class="nk-mock-block"><h3>Sources</h3><div class="nk-mock-chips">${sum.banks.map(([name,n])=>`<span>${esc(name)} <b>${n}</b></span>`).join('')}</div></section>`:''}
        ${attempts?`<section class="nk-mock-block"><h3>Past attempts</h3><ul class="nk-mock-attempts">${attempts}</ul></section>`:''}
      </div>
      <footer class="nk-mock-sheet-foot"><button type="button" class="nk-mock-icon-btn" aria-label="Rename mock" onclick="window.QB.nkMockSheetRename(${arg})">${navIcon('edit',18)}</button><button type="button" class="nk-mock-icon-btn nk-mock-delete" aria-label="Delete mock" onclick="window.QB.nkMockAskDelete(${arg})">${navIcon('trash',18)}</button><button type="button" class="primary-btn nk-mock-start" ${blocked?'disabled':''} onclick="window.QB.nkMockLaunch(${arg})">Start mock</button></footer>
    </section></div>`);
    document.querySelector?.('#nk-mock-sheet .nk-modal-close')?.focus({preventScroll:true});
    return true;
  }
  function nkMockLaunch(id){nkMockClose();return nkMockStart(id);}
  function nkMockSheetRename(id){
    const head=document.querySelector?.('#nk-mock-sheet .nk-mock-sheet-title'),m=nkMockList().find(x=>String(x.id)===String(id));if(!head||!m)return;
    head.innerHTML=`<form class="nk-mock-rename" novalidate data-mock-id="${esc(m.id)}" onsubmit="event.preventDefault();window.QB.nkMockRename(this.getAttribute('data-mock-id'),this.elements.name.value)"><label for="nk-mock-sheet-name" class="nk-na-sr">Mock name</label><input id="nk-mock-sheet-name" name="name" maxlength="80" required value="${esc(m.name)}" onkeydown="if(event.key==='Escape'){event.stopPropagation();window.QB.nkMockOpen(this.form.getAttribute('data-mock-id'))}"><button type="submit">Save</button><small role="status"></small></form>`;
    const input=head.querySelector('input');input?.focus({preventScroll:true});input?.select?.();
  }
  function nkMockAskDelete(id,cancel){
    const foot=document.querySelector?.('#nk-mock-sheet .nk-mock-sheet-foot'),m=nkMockList().find(x=>String(x.id)===String(id));if(!foot||!m)return;
    if(cancel){nkMockOpen(id);document.querySelector?.('#nk-mock-sheet .nk-mock-delete')?.focus({preventScroll:true});return;}
    const arg=esc(JSON.stringify(String(m.id)));foot.classList.add('is-confirming');
    foot.innerHTML=`<p>Delete this mock? Past results stay in Completed tests.</p><button type="button" class="ghost-btn" onclick="window.QB.nkMockAskDelete(${arg},true)">Cancel</button><button type="button" class="danger-btn" onclick="window.QB.nkMockRemove(${arg})">Delete</button>`;
    foot.querySelector('.ghost-btn')?.focus({preventScroll:true});
  }
  let nkMockLastRemoved=null,nkMockUndoTimer=0;
  function nkMockRemove(id){
    const before=nkMockList(),index=before.findIndex(m=>String(m.id)===String(id));if(index<0)return;
    const x=typeof window!=='undefined'?window.scrollX:0,y=typeof window!=='undefined'?window.scrollY:0;
    state.savedMocks=before.filter(m=>String(m.id)!==String(id));if(saveState()===false){state.savedMocks=before;showToast('Could not delete this mock. Try again.','bad');return;}
    nkMockClose();nkMockLastRemoved={mock:before[index],index};render();
    if(typeof window!=='undefined')window.scrollTo?.(x,y);
    const root=document.getElementById?.('toast-root');
    if(!root?.appendChild||typeof document.createElement!=='function'){showToast('Saved mock deleted.','good');return;}
    // Stop an earlier toast's timer from clearing this one before Undo's seven seconds are up.
    if(typeof toastTimer!=='undefined'&&typeof clearTimeout==='function')clearTimeout(toastTimer);
    root.innerHTML='';const el=document.createElement('div');el.className='toast good nk-undo-toast';el.setAttribute('role','status');
    el.innerHTML=`<span>Mock deleted</span><button type="button" onclick="window.QB.nkMockUndo()">Undo</button>`;root.appendChild(el);
    if(typeof clearTimeout==='function'){clearTimeout(nkMockUndoTimer);nkMockUndoTimer=setTimeout(()=>{el.remove();nkMockLastRemoved=null;},7000);}
  }
  function nkMockUndo(){
    const last=nkMockLastRemoved;nkMockLastRemoved=null;document.querySelector?.('.nk-undo-toast')?.remove();if(!last)return false;
    const list=nkMockList(),before=state.savedMocks;if(list.some(m=>String(m.id)===String(last.mock.id)))return true;
    const next=[...list];next.splice(Math.min(last.index,next.length),0,{...last.mock,updatedAt:Date.now()});state.savedMocks=next;
    if(saveState()===false){state.savedMocks=before;showToast('Could not restore the mock.','bad');return false;}
    render();showToast('Mock restored.','good');return true;
  }
  function nkMockFilter(value){
    const section=document.querySelector?.('.nk-na-saved-mocks');if(!section)return;
    const terms=String(value||'').toLowerCase().split(/\s+/).filter(Boolean);let shown=0;
    section.classList.toggle('is-searching',terms.length>0);
    section.querySelectorAll('.nk-na-mock-row').forEach(row=>{const hay=row.getAttribute('data-mock-search')||'',hit=terms.every(t=>hay.includes(t));row.hidden=!hit;if(hit)shown++;});
    const none=section.querySelector('.nk-na-mock-none');if(none)none.hidden=shown>0;
  }
  function nkMockShowAll(){const section=document.querySelector?.('.nk-na-saved-mocks');section?.classList.add('is-expanded');section?.querySelector('.nk-na-mock-more')?.remove();}
  const nkAnalysisQuestionsMarkup=nkCbtQuestionsMarkup;
  nkCbtQuestionsMarkup=function(){return `<label class="nk-na-mock-name" for="nk-cbt-name">Mock name <small>Optional</small><input id="nk-cbt-name" maxlength="80" placeholder="e.g. Biochemistry mock 01" value="${esc(nkCbtDraft?.name||'')}" oninput="window.QB.nkMockName(this.value)"></label>`+nkAnalysisQuestionsMarkup();};
  const nkAnalysisBuilderPage=nkCbtBuilderPage;
  nkCbtBuilderPage=function(){const html=nkAnalysisBuilderPage();return nkCbtDraft?.step===3?html.replace('<div class="nk-cbt-main-actions">','<div class="nk-cbt-main-actions"><button onclick="window.QB.nkMockSaveDraft()">Save mock</button>'):html;};
  /* NK_REFINED_ANALYSIS_V1_END */
