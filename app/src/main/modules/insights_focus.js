  /* NK_INSIGHTS_FOCUS_V1_START */
  function nkInsightsFocusRows(){
    const meta=new Map(),groups=new Map();
    Object.values(typeof BANKS_BY_SUBJECT==='object'?BANKS_BY_SUBJECT:{}).flat().forEach(record=>{
      (record.topics||[]).forEach(topic=>{
        const key=JSON.stringify([record.subject,record.bank,String(topic.id)]);
        meta.set(key,topic.title||topic.name||String(topic.id));
      });
    });
    nkAllStudyQuestions().forEach(q=>{
      const key=JSON.stringify([q.subject,q.bank,String(q.chapterId)]);
      const attempts=typeof nkFsrsActiveAttempts==='function'?nkFsrsActiveAttempts(String(q.id)):
        (qAttempts(String(q.id))||[]).filter(a=>a&&!a.isUndo);
      if(!attempts.length)return;
      let row=groups.get(key);
      if(!row){row={key,subject:q.subject,bank:q.bank,topicId:String(q.chapterId),title:meta.get(key)||q.chapter||q.topic||'Topic',answered:0,missed:[]};groups.set(key,row);}
      row.answered++;
      if(attempts[attempts.length-1].correct===false)row.missed.push(q);
    });
    const studied=[...groups.values()],recommended=studied.filter(row=>row.answered>=3&&row.missed.length>=2);
    recommended.sort((a,b)=>b.missed.length/b.answered-a.missed.length/a.answered||b.missed.length-a.missed.length||a.key.localeCompare(b.key));
    return {recommended,hasEnoughHistory:studied.some(row=>row.answered>=3)};
  }
  function nkInsightsFocusSection(){
    const {recommended,hasEnoughHistory}=nkInsightsFocusRows();
    const rows=recommended.slice(0,3).map(row=>{
      const key=encodeURIComponent(row.key),count=Math.min(20,row.missed.length);
      return '<article class="nk-insights-focus-row"><div><small>'+esc(row.subject)+' · '+esc(row.bank)+'</small><h3>'+esc(row.title)+'</h3><p>'+fmtNum(row.missed.length)+' still missed · '+fmtNum(row.answered)+' answered</p></div><button type="button" onclick="window.QB.nkPracticeInsightFocus(\''+key+'\')">Practice '+fmtNum(count)+' missed '+navIcon('chevron',16)+'</button></article>';
    }).join('');
    const empty=hasEnoughHistory
      ?'<div class="nk-insights-focus-empty"><strong>No topic needs a targeted retry right now.</strong><p>Keep practising; this list updates when your latest answers change.</p></div>'
      :'<div class="nk-insights-focus-empty"><strong>Keep studying to reveal your focus areas.</strong><p>Answer at least 3 questions in a topic. Topics with 2 or more current misses can appear here.</p></div>';
    return '<section class="nk-section nk-insights-focus"><div class="nk-section-head"><div><div class="nk-kicker">STUDY NEXT</div><h2>Topics to revisit</h2></div><span>All subjects · all banks</span></div><p class="nk-insights-focus-explain">Based on the latest answer to each question. A topic needs at least 3 answered questions and 2 current misses to appear.</p>'+(rows||empty)+'</section>';
  }
  function nkPracticeInsightFocus(encodedKey){
    let key;try{key=decodeURIComponent(encodedKey)}catch{return;}
    const row=nkInsightsFocusRows().recommended.find(item=>item.key===key);
    if(!row||!row.missed.length){showToast('These questions are no longer missed.');render();return;}
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test before starting Practice.','bad');return;}
    const pool=row.missed.slice();
    for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]];}
    const selected=pool.slice(0,20),ids=selected.map(q=>String(q.id));
    if(typeof openBank==='function')openBank(row.subject,row.bank);
    BY_ID={...BY_ID,...Object.fromEntries(selected.map(q=>[String(q.id),q]))};
    startSession(ids,'practice','Insights · '+row.title,'wrong');
  }
  /* NK_INSIGHTS_FOCUS_V1_END */
