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
    return minutes>=60?`${Math.floor(minutes/60)}h ${minutes%60}m`:`${minutes}m ${seconds%60}s`;
  }
  function nkAnalysisOutcomes(t){
    return [['Correct',Number(t.correct)||0,'correct','check'],['Incorrect',Number(t.incorrect)||0,'incorrect','close'],['Omitted',Number(t.unattempted)||0,'omitted','minus']];
  }
  function nkAnalysisRing(t,scoreOnly=false){
    const total=Number(t.total)||0,c=total?t.correct/total*100:0,w=total?t.incorrect/total*100:0;
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
    return `<section class="nk-na-card nk-cbt-analysis"><div class="nk-na-tabs" role="group" aria-label="Performance breakdown">${[['subject','Subject-wise'],['topic','Topic-wise']].map(([tab,label])=>`<button aria-pressed="${nkAnalysisTab===tab}" onclick="window.QB.nkAnalysisSetTab('${tab}','${esc(t.id)}')">${label}</button>`).join('')}</div><header><h2>${nkAnalysisTab==='subject'?'Subject':'Topic'} breakdown</h2><small>Correct / Total</small></header><div class="nk-cbt-analysis-list">${visible.map(nkAnalysisRow).join('')}${hidden.length?`<details class="nk-cbt-analysis-rest"><summary>${hidden.length} more ${nkAnalysisTab==='subject'?'subjects':'topics'}</summary>${hidden.map(nkAnalysisRow).join('')}</details>`:''}</div>${analysis.unavailable?`<p class="nk-na-note">${analysis.unavailable} saved questions are unavailable in the current banks.</p>`:''}</section>`;
  }
  function nkAnalysisTimeData(t){
    const bins=[0,0,0,0,0];let missing=0;
    for(const id of new Set(t.questionIds||[])){const value=Object.prototype.hasOwnProperty.call(t.questionTimes||{},id)?t.questionTimes[id]:null;if(typeof value!=='number'||!Number.isFinite(value)||value<0){missing++;continue;}bins[value<30000?0:value<60000?1:value<120000?2:value<=180000?3:4]++;}
    let total=0;const counts=nkAnalysisTimeMode==='cumulative'?bins.map(n=>total+=n):bins;
    return {counts,bins,missing,recorded:bins.reduce((a,b)=>a+b,0)};
  }
  function nkAnalysisTimeChart(t){
    const {counts,bins,missing,recorded}=nkAnalysisTimeData(t),within=nkAnalysisTimeMode==='cumulative',max=Math.max(1,...counts),labels=within?['< 30s','< 1m','< 2m','≤ 3m','Any time']:['< 30s','30–60s','1–2m','2–3m','> 3m'];
    const explanation=within?'Running total: each bar includes every recorded question below its time limit. The same question can appear in several bars.':'Each recorded question appears in one time range.';
    const repeated=within&&recorded&&bins[0]===recorded?`<p class="nk-na-note nk-na-time-readout">All ${recorded} recorded questions took under 30 seconds, so every running total is ${recorded}.</p>`:'';
    return `<section class="nk-na-card nk-na-time"><header><h2>Time per question</h2><div class="nk-na-tabs" role="group" aria-label="Time analysis view">${[['bins','Time ranges'],['cumulative','Within time']].map(([mode,label])=>`<button aria-pressed="${nkAnalysisTimeMode===mode}" onclick="window.QB.nkAnalysisSetTime('${mode}','${esc(t.id)}')">${label}</button>`).join('')}</div></header><p class="nk-na-note nk-na-time-explanation">${explanation}</p>${recorded?`<div class="nk-na-time-bars" role="img" aria-label="${within?'Questions within each time limit':'Question time distribution'}: ${counts.map((n,i)=>`${labels[i]}: ${n}`).join('; ')}">${counts.map((n,i)=>`<div><b>${n}</b><span><i style="height:${n/max*105}px"></i></span><small>${esc(labels[i])}</small></div>`).join('')}</div>${repeated}<p class="nk-na-note nk-na-time-coverage">Timing saved for ${recorded} of ${recorded+missing} questions.${missing?` ${missing} without saved timing are excluded.`:''} Recorded time includes revisits.</p>`:'<p class="nk-na-note">Question timing was not recorded.</p>'}</section>`;
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
  resultPage=function(testId){
    const t=nkAnalysisTest(testId);if(!t)return testsPage();
    const practice=t.kind==='practice',attempted=Number(t.correct||0)+Number(t.incorrect||0),accuracy=attempted?fmtPct(t.correct/attempted*100):'—',score=t.total?fmtPct(t.correct/t.total*100):'0%',totalTime=typeof t.totalTimeMs==='number'?t.totalTimeMs:null;
    const origin=t.originRoute||(practice?'topics':'tests');
    const questionMap=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));BY_ID={...BY_ID,...Object.fromEntries((t.questionIds||[]).filter(id=>questionMap.has(String(id))).map(id=>[id,questionMap.get(String(id))]))};
    const module=t.studyModuleId&&nkFindStudyModule(t.studyModuleId);
    return shell(`<main class="nk-app-v114 nk-result-v114 nk-refined-analysis"><header class="nk-na-head"><button class="nk-na-back" aria-label="Back to ${esc(origin)}" onclick="window.QB.nav('${esc(origin)}')">${navIcon('back',22)}</button><h1>${practice?'Practice':'Test'} analysis</h1></header><div class="nk-na-name"><span>${navIcon(practice?'book':'test',19)}</span><div><strong>${esc(t.title||'Untitled test')}</strong><small>${fmtDate(t.createdAt)}</small></div>${!practice?`<button aria-label="Rename test" onclick="document.getElementById('nk-na-rename').hidden=false;document.getElementById('nk-na-title').focus()">${nkAnalysisIcon('edit',18)}</button>`:''}</div>${!practice?`<form id="nk-na-rename" hidden onsubmit="event.preventDefault();window.QB.nkAnalysisRename('${esc(t.id)}')"><label for="nk-na-title">Test name</label><input id="nk-na-title" maxlength="80" value="${esc(t.title||'')}"><button type="submit">Save name</button></form>`:''}
      <section class="nk-na-card nk-na-summary nk-result-overview">${nkAnalysisRing(t,true)}<div><div class="nk-result-percentages"><strong>${t.correct} / ${t.total}</strong><span>Correct answers</span><span class="nk-na-accuracy">Accuracy <b>${accuracy}</b></span><span class="nk-na-sr">Score: all questions ${score}. Accuracy: answered questions ${accuracy}. ${attempted} answered.</span></div><div class="nk-na-outcome-counts nk-result-counts">${nkAnalysisOutcomes(t).map(([label,n,tone,icon])=>`<div class="is-${tone}"><span>${icon==='minus'?nkAnalysisIcon('minus',14):navIcon(icon,14)}</span><b>${n}</b><small>${label}</small></div>`).join('')}</div></div></section>
      <div class="nk-na-metrics">${[['clock','Time taken',nkAnalysisDuration(totalTime)],['stopwatch','Avg. time / Q',nkAnalysisDuration(totalTime===null||!t.total?null:totalTime/t.total)]].map(([icon,label,value])=>`<article><span>${icon==='stopwatch'?nkAnalysisIcon('stopwatch',21):navIcon(icon,21)}</span><div><small>${label}</small><b>${value}</b></div></article>`).join('')}</div>
      <div class="nk-na-analysis-grid">${!practice?nkAnalysisBreakdown(t):''}<section class="nk-na-card nk-na-performance"><header><h2>Question performance</h2></header><div>${nkAnalysisRing(t)}<dl>${nkAnalysisOutcomes(t).map(([label,n,tone])=>`<div><dt><i class="is-${tone}"></i>${label}</dt><dd>${n}<small>${t.total?Math.round(n/t.total*100):0}%</small></dd></div>`).join('')}</dl></div></section>${nkAnalysisTimeChart(t)}</div>
      <div class="nk-na-actions"><button class="v102-review-action" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))">Review Solutions</button>${!practice&&t.timerMode!=='per-question'?`<button class="is-primary" data-test-id="${esc(t.id)}" onclick="window.QB.nkCbtRetake(this.getAttribute('data-test-id'),event)">Retry Test</button>`:''}</div>
      ${practice?nkCorrectionResultSection(t):nkAnalysisFollowup(t)+nkAnalysisMarked(t)}${!practice?nkCbtComparisonSection(t):''}${!practice?`<button class="nk-na-save-mock" data-test-id="${esc(t.id)}" onclick="window.QB.nkMockSaveResult(this.getAttribute('data-test-id'))">${navIcon('bookmark',17)} Save as mock</button>`:''}${module?`<section class="nk-na-card nk-module-result"><header><h2>${esc(module.name)}</h2></header><div class="nk-module-result-actions"><button onclick="window.QB.restartStudyModule(this.getAttribute('data-module-id'))" data-module-id="${esc(module.id)}">Restart module</button><button onclick="window.QB.nav('dashboard')">Return Home</button></div></section>`:''}
      <details class="nk-na-card nk-na-answers"><summary>Every answer</summary><div class="nk-result-questions">${(t.questionIds||[]).map((id,i)=>{const q=questionMap.get(String(id)),sel=t.answers?.[id],correct=q&&Number(q.correctOption)===Number(sel);return `<div><span class="nk-question-index">${i+1}</span><span><strong>${q?esc(q.question.slice(0,125)):esc('Saved question unavailable')}</strong><small><i class="nk-status ${sel?(correct?'is-correct':'is-wrong'):'is-unattempted'}">${sel?(correct?'Correct':'Incorrect'):'Omitted'}</i>${q?esc(q.chapter||''):''}</small></span></div>`;}).join('')}</div></details></main>`,'tests');
  };
  function nkAnalysisRename(id){const t=nkAnalysisTest(id),value=document.getElementById('nk-na-title')?.value.trim().slice(0,80);if(!t||!value)return;const prior=t.title;t.title=value;t.updatedAt=Date.now();if(saveState()===false){t.title=prior;return;}render();}
  function nkMockList(){return Array.isArray(state.savedMocks)?state.savedMocks:[];}
  function nkMockStore(name,ids){
    if(nkMockList().length>=100){showToast('Your saved mocks are full. Remove one before saving another.','bad');return null;}
    const now=Date.now(),mock={id:`mock_${now}_${Math.random().toString(36).slice(2,9)}`,name:String(name||'Timed CBT').trim().slice(0,80),questionIds:ids.map(String),createdAt:now,updatedAt:now};
    const before=state.savedMocks;state.savedMocks=[...nkMockList(),mock];if(saveState()===false){state.savedMocks=before;return null;}return mock;
  }
  function nkMockPick(){const pool=nkCbtPool().filter(q=>nkQuestionPresentationFor(q).valid),ids=pool.map(q=>String(q.id));for(let i=ids.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[ids[i],ids[j]]=[ids[j],ids[i]];}return ids.slice(0,Math.min(Math.max(1,Number(nkCbtDraft.count||20)),ids.length));}
  function nkMockName(value){if(nkCbtDraft)nkCbtDraft.name=String(value).slice(0,80);}
  function nkMockSaveDraft(){if(!nkCbtDraft)return;const ids=nkMockPick();if(!ids.length)return;const mock=nkMockStore(nkCbtDraft.name||nkCbtTitle(),ids);if(mock){nkCbtDraft=null;showToast('Mock saved.','good');navigate('tests');}}
  const nkAnalysisOriginalCbtStart=nkCbtStart;
  nkCbtStart=function(){if(!nkCbtDraft?.name?.trim())return nkAnalysisOriginalCbtStart();const mock=nkMockList().find(m=>m.id===nkCbtDraft.savedMockId)||nkMockStore(nkCbtDraft.name,nkMockPick());if(mock){nkCbtDraft.savedMockId=mock.id;if(nkMockStart(mock.id)!==false)nkCbtDraft=null;}};
  function nkMockStart(id){
    const mock=nkMockList().find(m=>String(m.id)===String(id));if(!mock)return false;
    const map=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),ids=mock.questionIds||[];
    if(!ids.length||new Set(ids).size!==ids.length||ids.some(id=>!map.has(String(id))||!nkQuestionPresentationFor(map.get(String(id))).valid)){showToast('Some saved questions are unavailable. This mock cannot start.','bad');return false;}
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(id=>[id,map.get(String(id))]))};
    const initial=(state.tests||[]).filter(t=>t.kind!=='practice'&&t.timerMode!=='per-question'&&nkCbtSameQuestions(t,{questionIds:ids})).sort((a,b)=>Number(a.createdAt)-Number(b.createdAt))[0];
    return startSession(ids,'exam',mock.name,initial?`cbt-retake:${String(initial.id)}`:`saved-mock:${mock.id}`);
  }
  function nkMockSaveResult(id){const t=nkAnalysisTest(id);if(!t||t.kind==='practice')return;if(nkMockList().some(m=>nkCbtSameQuestions(t,m))){showToast('This question set is already saved.');return;}if(nkMockStore(t.title,t.questionIds))showToast('Mock saved to Tests.','good');}
  function nkMockRemove(id){const before=nkMockList();state.savedMocks=before.filter(m=>String(m.id)!==String(id));if(saveState()===false){state.savedMocks=before;return;}render();}
  const nkAnalysisQuestionsMarkup=nkCbtQuestionsMarkup;
  nkCbtQuestionsMarkup=function(){return `<label class="nk-na-mock-name" for="nk-cbt-name">Mock name <small>Optional</small><input id="nk-cbt-name" maxlength="80" placeholder="e.g. Biochemistry mock 01" value="${esc(nkCbtDraft?.name||'')}" oninput="window.QB.nkMockName(this.value)"></label>`+nkAnalysisQuestionsMarkup();};
  const nkAnalysisBuilderPage=nkCbtBuilderPage;
  nkCbtBuilderPage=function(){const html=nkAnalysisBuilderPage();return nkCbtDraft?.step===3?html.replace('<div class="nk-cbt-main-actions">','<div class="nk-cbt-main-actions"><button onclick="window.QB.nkMockSaveDraft()">Save mock</button>'):html;};
  const nkAnalysisTestsPage=testsPage;
  testsPage=function(){const mocks=nkMockList();if(!mocks.length)return nkAnalysisTestsPage();const section=`<section class="nk-section nk-na-saved-mocks"><div class="nk-section-head"><h2>Saved mocks</h2><span>${mocks.length}</span></div><div class="nk-session-list">${mocks.slice().reverse().map(m=>`<div class="nk-na-mock-row"><button onclick="window.QB.nkMockStart(this.getAttribute('data-mock-id'))" data-mock-id="${esc(m.id)}"><span>${navIcon('test',20)}</span><span><strong>${esc(m.name)}</strong><small>${m.questionIds.length} questions · ${m.questionIds.length} min</small></span>${navIcon('chevron',18)}</button><button class="nk-na-remove" aria-label="Remove ${esc(m.name)}" data-mock-id="${esc(m.id)}" onclick="window.QB.nkMockRemove(this.getAttribute('data-mock-id'))">${navIcon('close',16)}</button></div>`).join('')}</div></section>`;return nkAnalysisTestsPage().replace('<section class="nk-v3-section nk-test-history">',section+'<section class="nk-v3-section nk-test-history">');};
  /* NK_REFINED_ANALYSIS_V1_END */
