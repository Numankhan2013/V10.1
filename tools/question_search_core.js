  /* NK_QUESTION_SEARCH_V1_START */
  let nkQuestionSearchState={query:'',subject:'',bank:'',status:'',limit:30};
  let nkQuestionSearchCache=null;

  function nkQuestionSearchFold(value){
    return String(value||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
  }
  function nkQuestionSearchIndex(){
    if(nkQuestionSearchCache)return nkQuestionSearchCache;
    const seen=new Set();
    nkQuestionSearchCache=nkAllStudyQuestions().filter(q=>{
      const id=String(q?.id||'');if(!id||seen.has(id))return false;seen.add(id);return true;
    }).map(q=>{
      const id=String(q.id),topic=String(q.chapter||q.topic||'');
      const options=Array.isArray(q.options)?q.options.map(option=>typeof option==='string'?option:option?.text||'').join(' '):'';
      return {q,id,foldedId:nkQuestionSearchFold(id),foldedQuestion:nkQuestionSearchFold(q.question),text:nkQuestionSearchFold([id,q.question,options,topic,q.subject,q.bank].join(' '))};
    });
    return nkQuestionSearchCache;
  }
  function nkQuestionSearchStatus(id){
    const attempts=typeof nkFsrsActiveAttempts==='function'?nkFsrsActiveAttempts(id):(qAttempts(id)||[]).filter(a=>a&&!a.isUndo);
    return {unattempted:attempts.length===0,missed:attempts.some(a=>a.correct===false),bookmarked:Boolean(state.bookmarks?.[id])};
  }
  function nkQuestionSearchMatches(){
    const {query,subject,bank,status}=nkQuestionSearchState,term=nkQuestionSearchFold(query);
    if(!term&&!subject&&!bank&&!status)return {rows:[],idle:true};
    if(term.length===1&&!subject&&!bank&&!status)return {rows:[],short:true};
    const words=term.split(' ').filter(Boolean);
    const rows=nkQuestionSearchIndex().filter(entry=>{
      const q=entry.q;
      if(subject&&q.subject!==subject||bank&&q.bank!==bank)return false;
      if(words.length&&!words.every(word=>entry.text.includes(word)))return false;
      if(status){const progress=nkQuestionSearchStatus(entry.id);if(!progress[status])return false;}
      return true;
    });
    if(term)rows.sort((a,b)=>{
      const rank=entry=>entry.foldedId===term?0:entry.foldedId.startsWith(term)?1:entry.foldedQuestion.startsWith(term)?2:entry.foldedQuestion.includes(term)?3:4;
      return rank(a)-rank(b);
    });
    return {rows};
  }
  function nkQuestionSearchRow(entry){
    const q=entry.q,id=entry.id,progress=nkQuestionSearchStatus(id),topic=q.chapter||q.topic||'Topic unavailable';
    const badges=[progress.unattempted?'Unattempted':progress.missed?'Missed before':'Attempted'];
    if(progress.bookmarked)badges.push('Bookmarked');
    if(Array.isArray(q.studyCollections)&&q.studyCollections.includes('pyq'))badges.push('PYQ');
    return `<article class="nk-question-search-item"><div class="nk-question-search-meta">${esc(q.subject||'Subject')} · ${esc(q.bank||'Question bank')} · ${esc(topic)}</div><p>${esc(q.question||'Question text unavailable')}</p><div class="nk-question-search-bottom"><span class="nk-question-search-id">${esc(id)} · ${badges.map(esc).join(' · ')}</span><button type="button" onclick="window.QB.nkQuestionSearchOpen('${encodeURIComponent(id)}')">Practice ${navIcon('chevron',16)}</button></div></article>`;
  }
  function nkQuestionSearchResultsMarkup(){
    const {rows,idle,short}=nkQuestionSearchMatches();
    if(idle)return `<div class="nk-question-search-empty">Search question wording, answer options, topics, or a question ID. Choose a filter to browse without typing.</div>`;
    if(short)return `<div class="nk-question-search-empty">Type at least two characters to search all questions.</div>`;
    if(!rows.length)return `<div class="nk-question-search-empty">No questions match. Try a different phrase or clear a filter.</div>`;
    const shown=rows.slice(0,nkQuestionSearchState.limit),batch=Math.min(20,rows.length);
    return `<div class="nk-question-search-summary"><span role="status">${fmtNum(rows.length)} matching question${rows.length===1?'':'s'} · showing ${fmtNum(shown.length)}</span><button type="button" onclick="window.QB.nkQuestionSearchPracticeMatches()">Practice first ${batch} match${batch===1?'':'es'}</button></div><div class="nk-question-search-list">${shown.map(nkQuestionSearchRow).join('')}</div>${shown.length<rows.length?`<button type="button" class="nk-question-search-more" onclick="window.QB.nkQuestionSearchMore()">Show more questions</button>`:''}`;
  }
  function nkQuestionSearchPage(){
    const subjects=[...new Set(nkQuestionSearchIndex().map(entry=>entry.q.subject).filter(Boolean))].sort();
    const banks=[...new Set(nkQuestionSearchIndex().map(entry=>entry.q.bank).filter(Boolean))].sort();
    const option=(value,label,selected)=>`<option value="${esc(value)}"${selected?' selected':''}>${esc(label)}</option>`;
    return shell(`<main class="nk-app-v114 nk-question-search"><header class="nk-v3-page-hero"><div class="nk-kicker">QUESTION BANK</div><h1>Find a question</h1><p>Search every subject and bank, then practice exactly what you found.</p></header><label class="nk-question-search-box"><span aria-hidden="true">${navIcon('search',20)}</span><input type="search" value="${esc(nkQuestionSearchState.query)}" placeholder="Question wording or ID" aria-label="Search all questions" autocomplete="off" oninput="window.QB.nkQuestionSearchQuery(this.value)"></label><div class="nk-question-search-filters"><label>Subject<select onchange="window.QB.nkQuestionSearchSetFilter('subject',this.value)">${option('','All subjects',!nkQuestionSearchState.subject)}${subjects.map(subject=>option(subject,subject,nkQuestionSearchState.subject===subject)).join('')}</select></label><label>Bank<select onchange="window.QB.nkQuestionSearchSetFilter('bank',this.value)">${option('','All banks',!nkQuestionSearchState.bank)}${banks.map(bank=>option(bank,bank,nkQuestionSearchState.bank===bank)).join('')}</select></label><label>Progress<select onchange="window.QB.nkQuestionSearchSetFilter('status',this.value)">${option('','Any progress',!nkQuestionSearchState.status)}${option('unattempted','Unattempted',nkQuestionSearchState.status==='unattempted')}${option('missed','Missed before',nkQuestionSearchState.status==='missed')}${option('bookmarked','Bookmarked',nkQuestionSearchState.status==='bookmarked')}</select></label></div><div class="nk-question-search-results">${nkQuestionSearchResultsMarkup()}</div></main>`,'more');
  }
  function nkQuestionSearchUpdate(){const list=document.querySelector('.nk-question-search-results');if(list)list.innerHTML=nkQuestionSearchResultsMarkup();}
  function nkQuestionSearchQuery(value){nkQuestionSearchState.query=String(value||'');nkQuestionSearchState.limit=30;nkQuestionSearchUpdate();}
  function nkQuestionSearchSetFilter(field,value){
    if(!['subject','bank','status'].includes(field))return;
    nkQuestionSearchState[field]=String(value||'');nkQuestionSearchState.limit=30;nkQuestionSearchUpdate();
  }
  function nkQuestionSearchMore(){
    const surface=document.querySelector('.nk-question-search-results'),list=surface?.querySelector('.nk-question-search-list'),button=surface?.querySelector('.nk-question-search-more');
    const keyboard=button===document.activeElement&&button?.matches(':focus-visible'),x=window.scrollX,y=window.scrollY;
    const count=list?.children.length||0;
    nkQuestionSearchState.limit+=30;
    if(!list){nkQuestionSearchUpdate();return;}
    const template=document.createElement('template');template.innerHTML=nkQuestionSearchResultsMarkup();
    const added=[...template.content.querySelectorAll('.nk-question-search-item')].slice(count);
    list.append(...added);
    const status=surface.querySelector('[role="status"]'),nextStatus=template.content.querySelector('[role="status"]');
    if(status&&nextStatus)status.textContent=nextStatus.textContent;
    if(!template.content.querySelector('.nk-question-search-more'))button?.remove();
    if(keyboard)added[0]?.querySelector('button')?.focus({preventScroll:true});
    window.scrollTo(x,y);
  }
  function nkQuestionSearchStart(rows,title){
    if(!rows.length)return false;
    if(state.activeSession?.mode==='exam'){showToast('Resume or abandon your timed test before starting Practice.','bad');return false;}
    const ids=rows.map(entry=>entry.id),previous=state.activeSession?.id;
    BY_ID={...BY_ID,...Object.fromEntries(rows.map(entry=>[entry.id,entry.q]))};
    const started=startSession(ids,'practice',title,'question-search');
    const session=state.activeSession;
    if(started===false||!session||session.id===previous||session.mode!=='practice'||ids.join('\u001f')!==session.questionIds?.join('\u001f'))return false;
    session.originRoute='question-search';saveState();return true;
  }
  function nkQuestionSearchOpen(encodedId){
    let id;try{id=decodeURIComponent(encodedId);}catch(_){return false;}
    const entry=nkQuestionSearchIndex().find(item=>item.id===id);
    if(!entry){showToast('This question is unavailable.','bad');return false;}
    if(state.activeSession?.mode==='exam'){showToast('Resume or abandon your timed test before starting Practice.','bad');return false;}
    if(typeof openBank==='function'&&entry.q.subject&&entry.q.bank)openBank(entry.q.subject,entry.q.bank);
    return nkQuestionSearchStart([entry],`Question ${entry.q.questionNumber||id}`);
  }
  function nkQuestionSearchPracticeMatches(){
    const rows=nkQuestionSearchMatches().rows.slice(0,20);
    if(!rows.length)return false;
    const label=nkQuestionSearchState.query.trim()||[nkQuestionSearchState.subject,nkQuestionSearchState.bank,nkQuestionSearchState.status].filter(Boolean).join(' · ');
    return nkQuestionSearchStart(rows,`Search Practice · ${label.slice(0,48)}`);
  }
  /* NK_QUESTION_SEARCH_V1_END */
