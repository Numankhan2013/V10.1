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
  function nkCbtResultSection(test){
    if(test.kind==='practice'||!Array.isArray(test.questionIds)||!test.questionIds.length)return '';
    const analysis=nkCbtResultAnalysis(test),rows=analysis.rows;if(!rows.length)return '';
    const focus=rows.filter(row=>row.incorrect+row.unattempted>0),rest=rows.filter(row=>row.incorrect+row.unattempted===0);
    const visible=focus.length?focus:rest.slice(0,5),hidden=focus.length?rest:rest.slice(5);
    const missed=analysis.missedIds.length;
    return `<section class="nk-section nk-cbt-analysis" aria-labelledby="nk-cbt-analysis-title"><div class="nk-section-head"><div><div class="nk-kicker">THIS TEST</div><h2 id="nk-cbt-analysis-title">Topic breakdown</h2></div><span>${rows.length} topic${rows.length===1?'':'s'}</span></div><p class="nk-cbt-analysis-intro">Grouped by the exact subject and question bank used in this test. A single question is a starting signal, not a topic mastery rating.</p>${missed?`<div class="nk-cbt-followup"><div><strong>${missed} question${missed===1?'':'s'} to revisit</strong><small>Incorrect and unattempted questions from this saved test.</small></div><button type="button" onclick="window.QB.nkCbtPracticeMisses(this.getAttribute('data-test-id'))" data-test-id="${esc(test.id)}">Practise missed questions ${navIcon('chevron',16)}</button></div>`:`<div class="nk-cbt-followup is-clear"><div><strong>No missed questions</strong><small>Review Solutions is available above if you want to inspect your answers.</small></div></div>`}<div class="nk-cbt-analysis-list">${visible.map(nkCbtResultRow).join('')}${hidden.length?`<details class="nk-cbt-analysis-rest"><summary>${hidden.length} more topic${hidden.length===1?'':'s'}${focus.length?' with no misses':''}</summary>${hidden.map(nkCbtResultRow).join('')}</details>`:''}</div>${analysis.unavailable?`<p class="nk-cbt-analysis-unavailable">${analysis.unavailable} saved question${analysis.unavailable===1?'':'s'} could not be matched to a current bank and are excluded from this breakdown.</p>`:''}</section>`;
  }
  function nkCbtPracticeMisses(testId){
    const test=(state.tests||[]).find(item=>String(item.id)===String(testId));
    if(!test||test.kind==='practice'){showToast('This completed test is unavailable.','bad');return false;}
    const ids=nkCbtResultAnalysis(test).missedIds;
    if(!ids.length){showToast('There are no missed questions in this test.');return false;}
    const questions=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q]));
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(id=>[id,questions.get(id)||BY_ID[id]]).filter(([,q])=>q))};
    return startSession(ids,'practice',`CBT follow-up · ${test.title||'Timed CBT'}`,'cbt-followup');
  }
  /* NK_CBT_RESULT_ANALYSIS_V1_END */
