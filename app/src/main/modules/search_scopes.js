  /* NK_SEARCH_SCOPES_V1_START */
  // Find a question can search three things: question wording (default), explanations, and your own notes.
  // Explanations live in per-subject packs, so that scope asks for a subject and downloads only its packs once.
  const nkSearchText=new Map(); // question id → {raw, folded} explanation text
  const nkSearchPacksDone=new Set();
  let nkSearchLoad=null; // {key, done, total, failed}
  function nkSearchScope(){return ['explanations','notes'].includes(nkQuestionSearchState.scope)?nkQuestionSearchState.scope:'questions';}
  function nkSearchPlainText(value,depth=0){
    if(depth>6||value==null)return '';
    if(typeof value==='string')return value;
    if(Array.isArray(value))return value.map(item=>nkSearchPlainText(item,depth+1)).join(' ');
    if(typeof value==='object')return Object.entries(value).filter(([key])=>!/^(src|image|images|url|href|asset|id|type|style|width|height|page|pages)$/i.test(key)).map(([,item])=>nkSearchPlainText(item,depth+1)).join(' ');
    return '';
  }
  function nkSearchClean(text){
    return String(text||'').replace(/<[^>]+>/g,' ').replace(/\{\{[^}]*\}\}/g,' ').replace(/\*\*|__|`/g,'').replace(/&(amp|lt|gt|quot|#39|nbsp);/g,(m,k)=>({amp:'&',lt:'<',gt:'>',quot:'"','#39':"'",nbsp:' '})[k]).replace(/\s+/g,' ').trim();
  }
  function nkSearchIndexExplanation(id,fields){
    const raw=nkSearchClean([fields?.explanation,nkSearchPlainText(fields?.structuredExplanation)].filter(Boolean).join(' '));
    if(raw)nkSearchText.set(String(id),{raw,folded:nkQuestionSearchFold(raw)});
  }
  function nkSearchScopeEntries(){
    const {subject,bank}=nkQuestionSearchState;
    return nkQuestionSearchIndex().filter(entry=>(!subject||entry.q.subject===subject)&&(!bank||entry.q.bank===bank));
  }
  // Inline explanations index straight away; packed ones download pack by pack with visible progress.
  function nkSearchEnsureExplanations(){
    const subject=nkQuestionSearchState.subject;if(!subject)return;
    const entries=nkSearchScopeEntries(),packs=new Set();
    entries.forEach(entry=>{
      const q=entry.q,id=entry.id;
      if(Number.isInteger(q.detailPack)){if(!nkSearchPacksDone.has(q.detailPack))packs.add(q.detailPack);}
      else if(!nkSearchText.has(id))nkSearchIndexExplanation(id,q);
    });
    const key=subject+'|'+(nkQuestionSearchState.bank||'');
    if(!packs.size){nkSearchLoad=null;return;}
    if(nkSearchLoad?.key===key&&nkSearchLoad.running)return;
    const queue=[...packs],load=nkSearchLoad={key,done:0,total:queue.length,failed:0,running:true};
    const next=()=>{
      if(nkSearchLoad!==load)return;
      const index=queue.shift();
      if(index===undefined){load.running=false;if(!load.failed)nkSearchLoad=null;nkQuestionSearchUpdate();return;}
      nkDetailPack(index).then(pack=>{
        Object.entries(pack?.q||{}).forEach(([id,fields])=>nkSearchIndexExplanation(id,fields));
        nkSearchPacksDone.add(index);
      }).catch(()=>{load.failed++;}).finally(()=>{load.done++;if(nkSearchLoad===load)nkQuestionSearchUpdate();next();});
    };
    next();
  }
  function nkSearchNoteText(id){
    const note=typeof nkQuestionNote==='function'?nkQuestionNote(id):null;
    return note?nkSearchClean(nkNoteSummary(nkNoteBlocks(note))):'';
  }
  function nkSearchOtherText(id,scope){
    if(scope==='notes')return nkSearchNoteText(id);
    return nkSearchText.get(String(id))?.raw||'';
  }
  // A short window of the matching text with every search word highlighted.
  function nkSearchSnippet(raw,words){
    if(!raw)return '';
    const lower=raw.toLowerCase();let at=-1;
    for(const word of words){const i=lower.indexOf(word);if(i>=0&&(at<0||i<at))at=i;}
    const start=Math.max(0,at<0?0:at-70),end=Math.min(raw.length,start+220);
    let text=(start?'…':'')+raw.slice(start,end).replace(/^\S*\s/,start?'':'$&')+(end<raw.length?'…':'');
    let html=esc(text);
    words.filter(w=>w.length>1).sort((a,b)=>b.length-a.length).forEach(word=>{
      const pattern=new RegExp('('+esc(word).replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi');
      html=html.replace(pattern,'<mark>$1</mark>');
    });
    return html;
  }
  const nkSearchOriginalMatches=nkQuestionSearchMatches;
  nkQuestionSearchMatches=function(){
    const scope=nkSearchScope();if(scope==='questions')return nkSearchOriginalMatches.apply(this,arguments);
    const {query,subject,bank,status}=nkQuestionSearchState,term=nkQuestionSearchFold(query),words=term.split(' ').filter(Boolean);
    if(scope==='explanations'&&!subject)return {rows:[],needSubject:true};
    if(scope==='explanations')nkSearchEnsureExplanations();
    if(!term)return {rows:[],idle:true};
    if(term.length===1)return {rows:[],short:true};
    const rows=nkQuestionSearchIndex().filter(entry=>{
      const q=entry.q;
      if(subject&&q.subject!==subject||bank&&q.bank!==bank)return false;
      const text=scope==='notes'?nkQuestionSearchFold(nkSearchNoteText(entry.id)):nkSearchText.get(entry.id)?.folded||'';
      if(!text||!words.every(word=>text.includes(word)))return false;
      if(status){const progress=nkQuestionSearchStatus(entry.id);if(!progress[status])return false;}
      return true;
    });
    return {rows,words};
  };
  const nkSearchOriginalRow=nkQuestionSearchRow;
  nkQuestionSearchRow=function(entry){
    const html=nkSearchOriginalRow.apply(this,arguments),scope=nkSearchScope();
    if(scope==='questions')return html;
    const words=nkQuestionSearchFold(nkQuestionSearchState.query).split(' ').filter(Boolean);
    const snippet=nkSearchSnippet(nkSearchOtherText(entry.id,scope),words);
    return snippet?html.replace('<div class="nk-question-search-bottom">',`<blockquote class="nk-search-snippet"><span>${scope==='notes'?'Your note':'Explanation'}</span>${snippet}</blockquote><div class="nk-question-search-bottom">`):html;
  };
  const nkSearchOriginalResults=nkQuestionSearchResultsMarkup;
  nkQuestionSearchResultsMarkup=function(){
    const scope=nkSearchScope();if(scope==='questions')return nkSearchOriginalResults.apply(this,arguments);
    const result=nkQuestionSearchMatches();
    const load=scope==='explanations'&&nkSearchLoad&&nkSearchLoad.key===nkQuestionSearchState.subject+'|'+(nkQuestionSearchState.bank||'')?nkSearchLoad:null;
    const progress=load?`<div class="nk-search-loading" role="status"><span>${load.running?`Downloading ${esc(nkQuestionSearchState.subject)} explanations · ${fmtNum(load.done)} of ${fmtNum(load.total)}`:`${fmtNum(load.failed)} explanation pack${load.failed===1?'':'s'} could not download. Results may be incomplete.`}</span>${load.running?`<i style="--nk-search-fill:${Math.round(load.done/Math.max(1,load.total)*100)}%"></i>`:`<button type="button" onclick="window.QB.nkSearchRetry()">Retry</button>`}</div>`:'';
    if(result.needSubject)return `<div class="nk-question-search-empty">Choose a subject to search its explanations. Each subject downloads once, then searches instantly.</div>`;
    if(result.idle)return progress+`<div class="nk-question-search-empty">${scope==='notes'?'Search the notes you wrote on questions.':'Search the explanation text of every question in this subject.'}</div>`;
    if(result.short)return progress+`<div class="nk-question-search-empty">Type at least two characters.</div>`;
    if(!result.rows.length)return progress+(load?.running?'':`<div class="nk-question-search-empty">${scope==='notes'?'No notes match.':'No explanations match. Try a different phrase.'}</div>`);
    return progress+nkSearchOriginalResults.apply(this,arguments);
  };
  function nkSearchSetScope(scope){
    nkQuestionSearchState.scope=['explanations','notes'].includes(scope)?scope:'questions';nkQuestionSearchState.limit=30;
    document.querySelectorAll('.nk-search-scope button').forEach(button=>{const on=button.dataset.scope===nkQuestionSearchState.scope;button.classList.toggle('is-selected',on);button.setAttribute('aria-checked',String(on));});
    const input=document.querySelector('.nk-question-search-box input');
    if(input){input.placeholder=nkSearchPlaceholder();input.focus({preventScroll:true});}
    nkQuestionSearchUpdate();
  }
  function nkSearchRetry(){nkSearchLoad=null;nkQuestionSearchUpdate();}
  function nkSearchPlaceholder(){const scope=nkSearchScope();return scope==='explanations'?'Words in an explanation':scope==='notes'?'Words in your notes':'Question wording or ID';}
  const nkSearchOriginalPage=nkQuestionSearchPage;
  nkQuestionSearchPage=function(){
    const html=nkSearchOriginalPage.apply(this,arguments),scope=nkSearchScope();
    const notes=typeof nkSavedQuestionNotes==='function'?nkSavedQuestionNotes().length:0;
    const tabs=[['questions','Questions'],['explanations','Explanations'],['notes',`My notes${notes?` · ${fmtNum(notes)}`:''}`]];
    const control=`<div class="nk-search-scope" role="radiogroup" aria-label="Search in">${tabs.map(([key,label])=>`<button type="button" role="radio" data-scope="${key}" aria-checked="${scope===key}" class="${scope===key?'is-selected':''}" onclick="window.QB.nkSearchSetScope('${key}')">${esc(label)}</button>`).join('')}</div>`;
    return html.replace('placeholder="Question wording or ID"',`placeholder="${nkSearchPlaceholder()}"`).replace('<div class="nk-question-search-filters">',control+'<div class="nk-question-search-filters">');
  };
  /* NK_SEARCH_SCOPES_V1_END */
