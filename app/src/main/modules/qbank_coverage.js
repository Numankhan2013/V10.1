  /* NK_QBANK_COVERAGE_V1_START */
  let nkCoverageBankKey='';
  let nkCoverageStatus='all';
  let nkCoverageSearch='';
  let nkCoverageExpanded=false;

  function nkCoverageData(){
    const records=nkModuleBankRecords();
    const banks=records.map(record=>{
      const subject=String(record.subject),bank=nkModuleBankName(record),key=JSON.stringify([subject,bank]);
      const questions=new Map((record.questions||[]).map(q=>[String(q.id),q]));
      const byTopic=new Map();
      questions.forEach(q=>{
        const topicId=String(q.chapterId);
        if(!byTopic.has(topicId))byTopic.set(topicId,[]);
        byTopic.get(topicId).push(q);
      });
      const topics=nkModuleTopics(record).map(topic=>{
        const topicId=String(topic.id),rows=byTopic.get(topicId)||[];
        const summary={subject,bank,topicId,title:String(topic.title||topic.name||topicId),total:rows.length,attempted:0,latestMisses:0};
        rows.forEach(q=>{
          const history=typeof nkFsrsActiveAttempts==='function'?nkFsrsActiveAttempts(String(q.id)):
            (qAttempts(String(q.id))||[]).filter(a=>a&&!a.isUndo);
          if(!history.length)return;
          summary.attempted++;
          if(history[history.length-1].correct===false)summary.latestMisses++;
        });
        return summary;
      }).filter(topic=>topic.total>0);
      const attempted=topics.reduce((sum,topic)=>sum+topic.attempted,0);
      const total=topics.reduce((sum,topic)=>sum+topic.total,0);
      const complete=topics.filter(topic=>topic.attempted===topic.total).length;
      return {subject,bank,key,topics,attempted,total,complete};
    }).filter(bank=>bank.total>0);
    return {banks,attempted:banks.reduce((sum,bank)=>sum+bank.attempted,0),
      total:banks.reduce((sum,bank)=>sum+bank.total,0),
      complete:banks.reduce((sum,bank)=>sum+bank.complete,0),
      topics:banks.reduce((sum,bank)=>sum+bank.topics.length,0)};
  }

  function nkCoverageSelected(data){
    const selected=data.banks.find(bank=>bank.key===nkCoverageBankKey);
    if(selected)return selected;
    const preferred=data.banks.find(bank=>bank.subject===activeSubject&&bank.bank==='Marrow')
      ||data.banks.find(bank=>bank.subject===activeSubject)||data.banks[0];
    nkCoverageBankKey=preferred?.key||'';
    return preferred;
  }

  function nkCoverageListMarkup(data){
    const bank=nkCoverageSelected(data);
    if(!bank)return '<p class="nk-coverage-empty">No question banks are available yet.</p>';
    const query=nkCoverageSearch.trim().toLocaleLowerCase();
    const rows=bank.topics.filter(topic=>{
      const status=topic.attempted===topic.total?'complete':topic.attempted?'progress':'new';
      return (nkCoverageStatus==='all'||nkCoverageStatus===status)
        &&(!query||topic.title.toLocaleLowerCase().includes(query));
    });
    const visible=nkCoverageExpanded?rows:rows.slice(0,8);
    const list=visible.map(topic=>{
      const percent=Math.round(topic.attempted/topic.total*100);
      const status=topic.attempted===topic.total?'Complete':topic.attempted?'In progress':'Not started';
      const encoded=encodeURIComponent(JSON.stringify([topic.subject,topic.bank,topic.topicId]));
      return `<button type="button" class="nk-coverage-topic" onclick="window.QB.nkCoverageOpen('${encoded}')"><span class="nk-coverage-topic-copy"><strong>${esc(topic.title)}</strong><small>${status} · ${topic.attempted}/${topic.total} attempted${topic.latestMisses?` · ${topic.latestMisses} latest misses`:''}</small><i class="nk-coverage-track"><i style="width:${percent}%"></i></i></span><b>${percent}%</b>${navIcon('chevron',16)}</button>`;
    }).join('');
    return `<div class="nk-coverage-list-meta">${rows.length} matching topic${rows.length===1?'':'s'} · ${esc(bank.subject)} · ${esc(bank.bank)}</div><div class="nk-coverage-list">${list||'<p class="nk-coverage-empty">No topics match this search and status.</p>'}</div>${rows.length>8?`<button type="button" class="nk-coverage-more" onclick="window.QB.nkCoverageShowMore()">${nkCoverageExpanded?'Show fewer topics':`Show all ${rows.length} topics`}</button>`:''}`;
  }

  function nkCoverageSection(){
    const data=nkCoverageData(),selected=nkCoverageSelected(data);
    if(!selected)return '';
    const percent=Math.round(data.attempted/data.total*100);
    const cards=data.banks.map((bank,index)=>{
      const pct=Math.round(bank.attempted/bank.total*100),active=bank.key===selected.key;
      return `<button type="button" class="nk-coverage-bank ${active?'is-active':''}" aria-pressed="${active}" onclick="window.QB.nkCoverageSelectBank(${index})"><span><strong>${esc(bank.subject)}</strong><small>${esc(bank.bank)} · ${bank.complete}/${bank.topics.length} topics complete</small></span><b>${pct}%</b><i class="nk-coverage-track"><i style="width:${pct}%"></i></i><em>${bank.attempted}/${bank.total} attempted</em></button>`;
    }).join('');
    return `<section class="nk-section nk-coverage" aria-labelledby="nk-coverage-title"><div class="nk-section-head"><div><div class="nk-kicker">QBANK TRACKER</div><h2 id="nk-coverage-title">Your study map</h2></div><span>${data.attempted}/${data.total} attempted</span></div><p class="nk-coverage-intro">Across all subjects and question banks. A question counts as attempted after one answer; this measures coverage, not mastery.</p><div class="nk-coverage-overall"><div><strong>${percent}% covered</strong><span>${data.complete} of ${data.topics} topics complete</span></div><i class="nk-coverage-track"><i style="width:${percent}%"></i></i></div><div class="nk-coverage-banks" role="group" aria-label="Choose question bank">${cards}</div><div class="nk-coverage-detail"><div class="nk-coverage-detail-head"><strong>${esc(selected.subject)} · ${esc(selected.bank)}</strong><span>Open a topic to study</span></div><div class="nk-coverage-tools"><label class="nk-coverage-search"><span>Search topics</span><input type="search" value="${esc(nkCoverageSearch)}" placeholder="Find a topic" autocomplete="off" oninput="window.QB.nkCoverageSetSearch(this.value)"></label><label class="nk-coverage-filter"><span>Progress</span><select onchange="window.QB.nkCoverageSetStatus(this.value)">${[['all','All'],['progress','In progress'],['new','Not started'],['complete','Complete']].map(([value,label])=>`<option value="${value}" ${nkCoverageStatus===value?'selected':''}>${label}</option>`).join('')}</select></label></div><div class="nk-coverage-results">${nkCoverageListMarkup(data)}</div></div></section>`;
  }

  function nkCoverageRefreshList(){
    const node=document.querySelector('.nk-coverage-results');
    if(node)node.innerHTML=nkCoverageListMarkup(nkCoverageData());
  }
  function nkCoverageSelectBank(index){
    const bank=nkCoverageData().banks[Number(index)];if(!bank)return;
    nkCoverageBankKey=bank.key;nkCoverageStatus='all';nkCoverageSearch='';nkCoverageExpanded=false;
    const node=document.querySelector('.nk-coverage');
    if(node)node.outerHTML=nkCoverageSection();
  }
  function nkCoverageSetStatus(status){
    if(!['all','progress','new','complete'].includes(status))return;
    nkCoverageStatus=status;nkCoverageExpanded=false;nkCoverageRefreshList();
  }
  function nkCoverageSetSearch(value){
    nkCoverageSearch=String(value||'');nkCoverageExpanded=false;nkCoverageRefreshList();
  }
  function nkCoverageShowMore(){nkCoverageExpanded=!nkCoverageExpanded;nkCoverageRefreshList();}
  function nkCoverageOpen(encoded){
    let parts;try{parts=JSON.parse(decodeURIComponent(encoded));}catch{return;}
    if(!Array.isArray(parts)||parts.length!==3)return;
    const bank=nkCoverageData().banks.find(item=>item.subject===parts[0]&&item.bank===parts[1]);
    if(!bank||!bank.topics.some(topic=>topic.topicId===String(parts[2])))return;
    nkOpenSubjectChapter(parts[0],parts[1],parts[2]);
  }
  /* NK_QBANK_COVERAGE_V1_END */
