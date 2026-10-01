  /* NK_CBT_RESULT_ANALYSIS_V1_START */
  function nkCbtResultAnalysis(test){
    const questions=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));
    const rows=new Map(),missedIds=[];let unavailable=0;
    (test.questionIds||[]).forEach(id=>{
      const key=String(id),q=questions.get(key)||BY_ID[key];
      if(!q){unavailable++;return;}
      const subject=String(q.subject||'Unknown subject'),bank=String(q.bank||'PrepLadder');
      const topicId=String(q.chapterId||q.chapter||'unknown');
      const record=nkModuleSubjectRecord(subject,bank);
      const topic=nkModuleTopics(record).find(item=>String(item.id)===topicId);
      const title=String(topic?.title||q.chapter||'Unknown topic');
      const rowKey=JSON.stringify([subject,bank,topicId]);
      const row=rows.get(rowKey)||{subject,bank,topicId,title,total:0,correct:0,incorrect:0,unattempted:0};
      const selected=test.answers?.[key];row.total++;
      if(!selected){row.unattempted++;missedIds.push(key);}
      else if(Number(selected)===Number(q.correctOption))row.correct++;
      else{row.incorrect++;missedIds.push(key);}
      rows.set(rowKey,row);
    });
    return {rows:[...rows.values()].sort((a,b)=>(b.incorrect+b.unattempted)-(a.incorrect+a.unattempted)||a.subject.localeCompare(b.subject)||a.bank.localeCompare(b.bank)||a.title.localeCompare(b.title)),missedIds,unavailable};
  }
  function nkCbtResultRow(row){
    const missed=row.incorrect+row.unattempted,percent=Math.round(row.correct/row.total*100);
    return `<div class="nk-cbt-analysis-row"><div class="nk-cbt-analysis-copy"><strong>${esc(row.title)}</strong><small>${esc(row.subject)} · ${esc(row.bank)}</small></div><div class="nk-cbt-analysis-numbers"><b>${row.correct}/${row.total} correct</b><small>${row.incorrect} incorrect · ${row.unattempted} unattempted</small></div><div class="nk-cbt-analysis-track" role="img" aria-label="${percent}% correct"><span style="width:${percent}%"></span></div></div>`;
  }
  function nkCbtSameQuestions(first,second){
    const left=(first?.questionIds||[]).map(String),right=(second?.questionIds||[]).map(String);
    return left.length>0&&left.length===right.length&&left.sort().join('\u001f')===right.sort().join('\u001f');
  }
  function nkCbtInitialTest(test){
    if(!test?.retakeOf)return null;
    const seen=new Set([String(test.id)]);let current=test;
    while(current.retakeOf){
      const id=String(current.retakeOf);
      if(seen.has(id))return null;
      const parent=(state.tests||[]).find(item=>String(item.id)===id);
      if(!parent||parent.kind==='practice'||!nkCbtSameQuestions(test,parent))return null;
      seen.add(id);current=parent;
    }
    return current;
  }
  function nkCbtTimeLabel(ms){
    const seconds=Math.max(0,Math.round(Number(ms||0)/1000));
    return `${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`;
  }
  function nkCbtComparisonSection(test){
    if(!test?.retakeOf||test.kind==='practice')return '';
    const initial=nkCbtInitialTest(test);
    if(!initial)return `<section class="nk-section nk-cbt-comparison"><div class="nk-section-head"><div><div class="nk-kicker">RETAKE</div><h2>Compared with your initial test</h2></div></div><p class="nk-cbt-analysis-intro">The initial saved test is unavailable, so an exact comparison cannot be shown.</p></section>`;
    const first=nkCbtResultAnalysis(initial),last=nkCbtResultAnalysis(test);
    const initialMissed=new Set(first.missedIds),finalMissed=new Set(last.missedIds);
    const recovered=[...initialMissed].filter(id=>!finalMissed.has(id)).length;
    const newMisses=[...finalMissed].filter(id=>!initialMissed.has(id)).length;
    const delta=Number(test.correct||0)-Number(initial.correct||0);
    const total=(test.questionIds||[]).length;
    const accuracy=item=>{const answered=Number(item.attempted??(Number(item.correct||0)+Number(item.incorrect||0)));return answered?`${Math.round(Number(item.correct||0)/answered*100)}%`:'—';};
    const metrics=[
      ['Correct',`${Number(initial.correct||0)}/${total}`,`${Number(test.correct||0)}/${total}`],
      ['Accuracy: answered questions',accuracy(initial),accuracy(test)],
      ['Attempted',String(Number(initial.attempted??(Number(initial.correct||0)+Number(initial.incorrect||0)))),String(Number(test.attempted??(Number(test.correct||0)+Number(test.incorrect||0))))],
      ['Incorrect',String(Number(initial.incorrect||0)),String(Number(test.incorrect||0))],
      ['Unattempted',String(Number(initial.unattempted||0)),String(Number(test.unattempted||0))],
      ['Time',nkCbtTimeLabel(initial.totalTimeMs),nkCbtTimeLabel(test.totalTimeMs)]
    ];
    const firstRows=new Map(first.rows.map(row=>[JSON.stringify([row.subject,row.bank,row.topicId]),row]));
    const lastRows=new Map(last.rows.map(row=>[JSON.stringify([row.subject,row.bank,row.topicId]),row]));
    const keys=[...new Set([...firstRows.keys(),...lastRows.keys()])];
    const missedCount=row=>row?row.incorrect+row.unattempted:0;
    const topics=keys.map(key=>({initial:firstRows.get(key),final:lastRows.get(key)}))
      .filter(pair=>missedCount(pair.initial)||missedCount(pair.final))
      .sort((a,b)=>(missedCount(b.final)-missedCount(a.final))||(missedCount(b.initial)-missedCount(a.initial))||
        (a.final||a.initial).title.localeCompare((b.final||b.initial).title));
    const topicRows=topics.map(pair=>{
      const row=pair.final||pair.initial,was=missedCount(pair.initial),now=missedCount(pair.final);
      const status=now<was?'Improved':now>was?'More misses':'Still missed';
      const detail=part=>`${part?.incorrect||0} incorrect · ${part?.unattempted||0} unattempted`;
      return `<div class="nk-cbt-comparison-topic"><div><strong>${esc(row.title)}</strong><small>${esc(row.subject)} · ${esc(row.bank)}</small></div><div class="nk-cbt-comparison-topic-values"><span>Initial <b>${was} missed</b><small>${detail(pair.initial)}</small></span><span>Retake <b>${now} missed</b><small>${detail(pair.final)}</small></span><em class="${now<was?'is-improved':now>was?'is-regressed':''}">${status}</em></div></div>`;
    }).join('');
    const progress=delta>0?`${delta} more correct than your initial test`:delta<0?`${Math.abs(delta)} fewer correct than your initial test`:'The same number correct as your initial test';
    return `<section class="nk-section nk-cbt-comparison" aria-labelledby="nk-cbt-comparison-title"><div class="nk-section-head"><div><div class="nk-kicker">SAME QUESTIONS · TWO ATTEMPTS</div><h2 id="nk-cbt-comparison-title">Initial test vs retake</h2></div><button type="button" class="nk-cbt-initial-link" data-test-id="${esc(initial.id)}" onclick="window.QB.nav('result',this.getAttribute('data-test-id'))">View initial result</button></div><p class="nk-cbt-comparison-summary"><strong>${progress}.</strong> ${recovered} previous miss${recovered===1?'':'es'} corrected · ${newMisses} new miss${newMisses===1?'':'es'}.</p><div class="nk-cbt-comparison-metrics">${metrics.map(([label,before,after])=>`<article><small>${label}</small><span>${before}<i aria-hidden="true">→</i><b>${after}</b></span></article>`).join('')}</div><div class="nk-cbt-comparison-topics"><h3>Topics missed in either test</h3>${topics.length?topicRows:'<p>No topics were missed in either test.</p>'}</div>${first.unavailable||last.unavailable?`<p class="nk-cbt-analysis-unavailable">${Math.max(first.unavailable,last.unavailable)} saved question${Math.max(first.unavailable,last.unavailable)===1?'':'s'} could not be matched to a current bank; topic comparison is incomplete.</p>`:''}</section>`;
  }
  function nkCbtRetake(testId,clickEvent){
    const test=(state.tests||[]).find(item=>String(item.id)===String(testId));
    if(!test||test.kind==='practice'||test.timerMode==='per-question'||!Array.isArray(test.questionIds)||!test.questionIds.length){
      showToast('This timed CBT is unavailable for a retake.','bad');return false;
    }
    if(Number(clickEvent?.detail)>1)return false;
    const questions=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));
    const ids=test.questionIds.map(String);
    if(new Set(ids).size!==ids.length||ids.some(id=>!questions.has(id))){
      showToast('Some saved questions are unavailable, so this exact test cannot be retaken.','bad');return false;
    }
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(id=>[id,questions.get(id)]))};
    const initial=nkCbtInitialTest(test)||test;
    return startSession(ids,'exam',test.title||'Timed CBT',`cbt-retake:${String(initial.id)}`);
  }
  function nkCbtResultSection(test){
    if(test.kind==='practice'||!Array.isArray(test.questionIds)||!test.questionIds.length)return '';
    const analysis=nkCbtResultAnalysis(test),rows=analysis.rows;if(!rows.length)return '';
    const focus=rows.filter(row=>row.incorrect+row.unattempted>0),rest=rows.filter(row=>row.incorrect+row.unattempted===0);
    const visible=focus.length?focus:rest.slice(0,5),hidden=focus.length?rest:rest.slice(5);
    const originalMisses=analysis.missedIds.length,remaining=typeof nkFsrsUnresolvedResultMisses==='function'?nkFsrsUnresolvedResultMisses(test,analysis.missedIds):analysis.missedIds;
    const missed=remaining.length,corrected=originalMisses-missed,canRetake=test.timerMode!=='per-question';
    const retake=canRetake?`<div class="nk-cbt-retake"><div><strong>Try the same ${test.questionIds.length} questions again</strong><small>Fresh timer and blank answers; your saved results stay in history.</small></div><button type="button" onclick="window.QB.nkCbtRetake(this.getAttribute('data-test-id'),event)" data-test-id="${esc(test.id)}">Retake timed CBT ${navIcon('chevron',16)}</button></div>`:'';
    return `<section class="nk-section nk-cbt-analysis" aria-labelledby="nk-cbt-analysis-title"><div class="nk-section-head"><div><div class="nk-kicker">THIS TEST</div><h2 id="nk-cbt-analysis-title">Topic breakdown</h2></div><span>${rows.length} topic${rows.length===1?'':'s'}</span></div><p class="nk-cbt-analysis-intro">Grouped by the exact subject and question bank used in this test. A single question is a starting signal, not a topic mastery rating.</p>${retake}${missed?`<div class="nk-cbt-followup"><div><strong>${missed} question${missed===1?'':'s'} to revisit</strong><small>${corrected?corrected+' corrected since this test. ':''}Remaining incorrect and unattempted questions; your saved score stays unchanged.</small></div><button type="button" onclick="window.QB.nkCbtPracticeMisses(this.getAttribute('data-test-id'),event)" data-test-id="${esc(test.id)}">Practise missed questions ${navIcon('chevron',16)}</button></div>`:`<div class="nk-cbt-followup is-clear"><div><strong>${corrected?'All original misses corrected':'No missed questions'}</strong><small>${corrected?'Spaced review checks retention later; your saved score stays unchanged.':'Review Solutions is available above if you want to inspect your answers.'}</small></div></div>`}<div class="nk-cbt-analysis-list">${visible.map(nkCbtResultRow).join('')}${hidden.length?`<details class="nk-cbt-analysis-rest"><summary>${hidden.length} more topic${hidden.length===1?'':'s'}${focus.length?' with no misses':''}</summary>${hidden.map(nkCbtResultRow).join('')}</details>`:''}</div>${analysis.unavailable?`<p class="nk-cbt-analysis-unavailable">${analysis.unavailable} saved question${analysis.unavailable===1?'':'s'} could not be matched to a current bank and are excluded from this breakdown.</p>`:''}</section>`;
  }
  function nkCbtPracticeMisses(testId,clickEvent){
    const test=(state.tests||[]).find(item=>String(item.id)===String(testId));
    if(!test||test.kind==='practice'){showToast('This completed test is unavailable.','bad');return false;}
    // A repeated Submit tap can land on this newly rendered button at the same
    // screen position. Event detail distinguishes it from a first intentional tap.
    if(Number(clickEvent?.detail)>1)return false;
    const original=nkCbtResultAnalysis(test).missedIds;
    const ids=typeof nkFsrsUnresolvedResultMisses==='function'?nkFsrsUnresolvedResultMisses(test,original):original;
    if(!ids.length){showToast('There are no missed questions in this test.');return false;}
    const questions=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(id=>[id,questions.get(id)||BY_ID[id]]).filter(([,q])=>q))};
    return startSession(ids,'practice',`CBT follow-up · ${test.title||'Timed CBT'}`,'cbt-followup');
  }
  /* NK_CBT_RESULT_ANALYSIS_V1_END */
