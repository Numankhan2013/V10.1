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
    const origin=t.originRoute||(practice?'topics':'tests'),browse=/^revision-browse\/(wrong|bookmarks)$/.exec(origin);
    const backLabel=browse?(browse[1]==='wrong'?'Mistakes':'Bookmarks'):origin;
    const backAction=browse?`window.QB.nav('revision-browse','${browse[1]}')`:`window.QB.nav('${esc(origin)}')`;
    const questionMap=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));BY_ID={...BY_ID,...Object.fromEntries((t.questionIds||[]).filter(id=>questionMap.has(String(id))).map(id=>[id,questionMap.get(String(id))]))};
    const module=t.studyModuleId&&nkFindStudyModule(t.studyModuleId);
    return shell(`<main class="nk-app-v114 nk-result-v114 nk-refined-analysis"><header class="nk-na-head"><button class="nk-na-back" aria-label="Back to ${esc(backLabel)}" onclick="${backAction}">${navIcon('back',22)}</button><h1>${practice?'Practice':'Test'} analysis</h1></header><div class="nk-na-name"><span>${navIcon(practice?'book':'test',19)}</span><div><strong>${esc(t.title||'Untitled test')}</strong><small>${fmtDate(t.createdAt)}</small></div>${!practice?`<button aria-label="Rename test" onclick="document.getElementById('nk-na-rename').hidden=false;document.getElementById('nk-na-title').focus()">${nkAnalysisIcon('edit',18)}</button>`:''}</div>${!practice?`<form id="nk-na-rename" hidden novalidate onsubmit="event.preventDefault();window.QB.nkAnalysisRename('${esc(t.id)}')"><label for="nk-na-title">Test name</label><input id="nk-na-title" required maxlength="80" aria-describedby="nk-na-rename-status" oninput="if(this.value.trim()){this.removeAttribute('aria-invalid');document.getElementById('nk-na-rename-status').textContent='';}" value="${esc(t.title||'')}"><button type="submit">Save name</button><small id="nk-na-rename-status" role="status"></small></form>`:''}
      <section class="nk-na-card nk-na-summary nk-result-overview">${nkAnalysisRing(t,true)}<div><div class="nk-result-percentages"><strong>${t.correct} / ${t.total}</strong><span>Correct answers</span><span class="nk-na-accuracy">Accuracy <b>${accuracy}</b></span><span class="nk-na-sr">Score: all questions ${score}. Accuracy: answered questions ${accuracy}. ${attempted} answered.</span></div><div class="nk-na-outcome-counts nk-result-counts">${nkAnalysisOutcomes(t).map(([label,n,tone,icon])=>`<div class="is-${tone}"><span>${icon==='minus'?nkAnalysisIcon('minus',14):navIcon(icon,14)}</span><b>${n}</b><small>${label}</small></div>`).join('')}</div></div></section>
      <div class="nk-na-metrics">${[['clock','Time taken',nkAnalysisDuration(totalTime)],['stopwatch','Avg. time / Q',nkAnalysisDuration(totalTime===null||!t.total?null:totalTime/t.total)]].map(([icon,label,value])=>`<article><span>${icon==='stopwatch'?nkAnalysisIcon('stopwatch',21):navIcon(icon,21)}</span><div><small>${label}</small><b>${value}</b></div></article>`).join('')}</div>
      <div class="nk-na-analysis-grid">${!practice?nkAnalysisBreakdown(t):''}<section class="nk-na-card nk-na-performance"><header><h2>Question performance</h2></header><div>${nkAnalysisRing(t)}<dl>${nkAnalysisOutcomes(t).map(([label,n,tone])=>`<div><dt><i class="is-${tone}"></i>${label}</dt><dd>${n}<small>${t.total?Math.round(n/t.total*100):0}%</small></dd></div>`).join('')}</dl></div></section>${nkAnalysisTimeChart(t)}</div>
      <div class="nk-na-actions"><button class="v102-review-action" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))">Review Solutions</button>${!practice&&t.timerMode!=='per-question'?`<button class="is-primary" data-test-id="${esc(t.id)}" onclick="window.QB.nkCbtRetake(this.getAttribute('data-test-id'),event)">Retry Test</button>`:''}</div>
      ${practice?nkCorrectionResultSection(t):nkAnalysisFollowup(t)+nkAnalysisMarked(t)}${!practice?nkCbtComparisonSection(t):''}${!practice?(nkMockFor(t)?nkMockSavedMarkup(nkMockFor(t)):`<button type="button" class="nk-na-save-mock" data-test-id="${esc(t.id)}" onclick="window.QB.nkMockSaveResult(this.getAttribute('data-test-id'))">${navIcon('bookmark',17)}<span>Save as mock</span></button>`):''}${module?`<section class="nk-na-card nk-module-result"><header><h2>${esc(module.name)}</h2></header><div class="nk-module-result-actions"><button onclick="window.QB.restartStudyModule(this.getAttribute('data-module-id'))" data-module-id="${esc(module.id)}">Restart module</button><button onclick="window.QB.nav('dashboard')">Return Home</button></div></section>`:''}
      <details class="nk-na-card nk-na-answers"><summary>Every answer</summary><div class="nk-result-questions">${(t.questionIds||[]).map((id,i)=>{const q=questionMap.get(String(id)),sel=t.answers?.[id],correct=q&&Number(q.correctOption)===Number(sel);return `<div><span class="nk-question-index">${i+1}</span><span><strong>${q?esc(q.question.slice(0,125)):esc('Saved question unavailable')}</strong><small><i class="nk-status ${sel?(correct?'is-correct':'is-wrong'):'is-unattempted'}">${sel?(correct?'Correct':'Incorrect'):'Omitted'}</i>${q?esc(q.chapter||''):''}</small></span></div>`;}).join('')}</div></details></main>`,'tests');
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
      const key=subject+'\u0000'+topic,row=topics.get(key)||{title:topic,subject,count:0};row.count++;topics.set(key,row);
    }
    const sort=entries=>[...entries].sort((a,b)=>b[1]-a[1]||String(a[0]).localeCompare(String(b[0])));
    const attempts=(state.tests||[]).filter(t=>t.kind!=='practice'&&nkCbtSameQuestions(t,m)).sort((a,b)=>Number(b.createdAt)-Number(a.createdAt));
    return {total:ids.length,missing,subjects:sort(subjects),banks:sort(banks),topics:[...topics.values()].sort((a,b)=>b.count-a.count||a.title.localeCompare(b.title)),attempts};
  }
  function nkMockScore(t){return t&&t.total?Math.round(Number(t.correct||0)/Number(t.total)*100):0;}
  function nkMockDay(ts){const d=new Date(Number(ts||0));return Number.isNaN(d.getTime())?'':d.toLocaleDateString(undefined,{day:'numeric',month:'short',year:d.getFullYear()===new Date().getFullYear()?undefined:'numeric'});}
  function nkMockGraphic(subject,size){return typeof nkSubjectGraphic==='function'?nkSubjectGraphic(subject,size):navIcon('test',size);}
  function nkMockClose(){document.getElementById?.('nk-mock-sheet')?.remove?.();}
  function nkMockOpen(id){
    if(typeof document==='undefined'||!document.body?.insertAdjacentHTML)return false;
    const m=nkMockList().find(x=>String(x.id)===String(id));if(!m)return false;nkMockClose();
    const map=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),sum=nkMockSummary(m,map),arg=esc(JSON.stringify(String(m.id)));
    const stack=sum.subjects.map(([name,n],i)=>`<i style="--nk-share:${n/sum.total*100}%;--nk-tone:${i}" title="${esc(name)} ${n}"></i>`).join('');
    const legend=sum.subjects.map(([name,n],i)=>`<li style="--nk-tone:${i}"><span class="nk-mock-dot"></span><span class="nk-mock-legend-name">${esc(name)}</span><b>${n}</b><small>${Math.round(n/sum.total*100)}%</small></li>`).join('');
    const topic=t=>`<li><span><strong>${esc(t.title)}</strong>${sum.subjects.length>1?`<small>${esc(t.subject)}</small>`:''}</span><b>${t.count}</b></li>`;
    const first=sum.topics.slice(0,5),rest=sum.topics.slice(5);
    const attempts=sum.attempts.slice(0,5).map(t=>`<li><span>${esc(nkMockDay(t.createdAt))}</span><span class="nk-mock-attempt-bar"><i style="width:${nkMockScore(t)}%"></i></span><b>${nkMockScore(t)}%</b></li>`).join('');
    const blocked=sum.missing>0;
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-mock-sheet-backdrop" id="nk-mock-sheet" onclick="if(event.target===this)window.QB.nkMockClose()" onkeydown="if(event.key==='Escape'){event.stopPropagation();window.QB.nkMockClose()}"><section class="modal card nk-mock-sheet" role="dialog" aria-modal="true" aria-labelledby="nk-mock-sheet-title" data-mock-id="${esc(m.id)}">
      <header class="nk-mock-sheet-head"><span class="nk-mock-sheet-icon" aria-hidden="true">${nkMockGraphic(sum.subjects[0]?.[0]||'',22)}</span><div class="nk-mock-sheet-title"><h2 id="nk-mock-sheet-title">${esc(m.name)}</h2><small>Saved ${esc(nkMockDay(m.createdAt))}</small></div><button type="button" class="nk-modal-close" aria-label="Close" onclick="window.QB.nkMockClose()">${navIcon('close',20)}</button></header>
      <div class="nk-mock-sheet-body">
        <dl class="nk-mock-facts"><div><dt>Questions</dt><dd>${sum.total}</dd></div><div><dt>Time limit</dt><dd>${sum.total} min</dd></div><div><dt>${sum.attempts.length?'Best score':'Attempts'}</dt><dd>${sum.attempts.length?Math.max(...sum.attempts.map(nkMockScore))+'%':'None yet'}</dd></div></dl>
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
  const nkAnalysisTestsPage=testsPage;
  testsPage=function(){
    const mocks=nkMockList();if(!mocks.length)return nkAnalysisTestsPage();
    const map=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),many=mocks.length>5;
    const rows=mocks.slice().reverse().map((m,i)=>{
      const sum=nkMockSummary(m,map),names=sum.subjects.map(([n])=>n),last=sum.attempts[0];
      const subjects=names.length>2?`${names.slice(0,2).join(', ')} +${names.length-2}`:names.join(', ');
      const search=[m.name,...names,...sum.banks.map(([n])=>n),...sum.topics.map(t=>t.title)].join(' ').toLowerCase();
      return `<div class="nk-na-mock-row${i>=5?' is-extra':''}" data-mock-search="${esc(search)}"><button type="button" data-mock-id="${esc(m.id)}" aria-haspopup="dialog" onclick="window.QB.nkMockOpen(this.getAttribute('data-mock-id'))"><span class="nk-na-mock-icon">${nkMockGraphic(names[0]||'',20)}</span><span class="nk-na-mock-copy"><strong>${esc(m.name)}</strong><small>${[`${sum.total} Qs`,`${sum.total} min`,subjects].filter(Boolean).map(esc).join(' · ')}</small></span><span class="nk-na-mock-state${last?'':' is-new'}">${last?`${nkMockScore(last)}%`:'New'}</span>${navIcon('chevron',18)}</button></div>`;
    }).join('');
    const section=`<section class="nk-section nk-na-saved-mocks"><div class="nk-section-head"><h2>Saved mocks</h2><span>${mocks.length}</span></div>${many?`<label class="nk-na-mock-search">${navIcon('search',18)}<input type="search" placeholder="Search name, subject or topic" aria-label="Search saved mocks" oninput="window.QB.nkMockFilter(this.value)"></label>`:''}<div class="nk-session-list">${rows}</div><p class="nk-na-mock-none" hidden>No saved mocks match.</p>${many?`<button type="button" class="nk-na-mock-more" onclick="window.QB.nkMockShowAll()">Show all ${mocks.length}</button>`:''}</section>`;
    return nkAnalysisTestsPage().replace('<section class="nk-v3-section nk-test-history">',section+'<section class="nk-v3-section nk-test-history">');
  };
  /* NK_REFINED_ANALYSIS_V1_END */
