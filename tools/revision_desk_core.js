  /* NK_REVISION_DESK_V1_START */
  let nkRevisionScope={subject:'',bank:'',topic:''};
  let nkRevisionFocusOpen=false;
  function nkRevisionScopeMatches(q){
    return (!nkRevisionScope.subject||q.subject===nkRevisionScope.subject)
      &&(!nkRevisionScope.bank||q.bank===nkRevisionScope.bank)
      &&(!nkRevisionScope.topic||String(q.chapterId)===nkRevisionScope.topic);
  }
  function nkRevisionScopeChoices(){
    const questions=nkAllStudyQuestions();
    const subjects=[...new Set(questions.map(q=>q.subject).filter(Boolean))].sort();
    const banks=nkRevisionScope.subject?[...new Set(questions.filter(q=>q.subject===nkRevisionScope.subject).map(q=>q.bank).filter(Boolean))].sort():[];
    const record=nkRevisionScope.subject&&nkRevisionScope.bank&&typeof nkBankRecord==='function'
      ?nkBankRecord(nkRevisionScope.subject,nkRevisionScope.bank):null;
    const topics=record?(record.topics||[]).map(t=>({id:String(t.id),title:t.title||t.name||String(t.id)})):[];
    return {subjects,banks,topics};
  }
  function nkRevisionScopeLabel(){
    const choices=nkRevisionScopeChoices();
    const topic=choices.topics.find(t=>t.id===nkRevisionScope.topic);
    return [nkRevisionScope.subject||'All subjects',nkRevisionScope.bank||'All question banks',topic?.title].filter(Boolean).join(' · ');
  }
  function nkRevisionScopeMarkup(){
    const {subjects,banks,topics}=nkRevisionScopeChoices();
    const option=(value,label,selected)=>'<option value="'+esc(value)+'"'+(selected?' selected':'')+'>'+esc(label)+'</option>';
    return '<div class="nk-revision-scope">'+esc(nkRevisionScopeLabel())+'</div><button type="button" class="nk-revision-focus-toggle" aria-expanded="'+String(nkRevisionFocusOpen)+'" onclick="window.QB.nkToggleRevisionFocus()">'+(nkRevisionFocusOpen?'Hide focus':'Focus questions')+' '+navIcon('chevron',16)+'</button>'
      +'<div class="nk-revision-focus"'+(nkRevisionFocusOpen?'':' hidden')+'><p>Choose one area for all four revision queues.</p><div class="nk-revision-focus-fields">'
      +'<label>Subject<select id="nk-revision-subject" onchange="window.QB.nkSetRevisionScope(\'subject\',this.value)">'
      +option('','All subjects',!nkRevisionScope.subject)+subjects.map(s=>option(s,s,s===nkRevisionScope.subject)).join('')+'</select></label>'
      +'<label>Question bank<select id="nk-revision-bank"'+(nkRevisionScope.subject?'':' disabled')+' onchange="window.QB.nkSetRevisionScope(\'bank\',this.value)">'
      +option('','All question banks',!nkRevisionScope.bank)+banks.map(b=>option(b,b,b===nkRevisionScope.bank)).join('')+'</select></label>'
      +'<label>Topic<select id="nk-revision-topic"'+(nkRevisionScope.bank?'':' disabled')+' onchange="window.QB.nkSetRevisionScope(\'topic\',this.value)">'
      +option('','All topics',!nkRevisionScope.topic)+topics.map(t=>option(t.id,t.title,t.id===nkRevisionScope.topic)).join('')+'</select></label></div>'
      +(nkRevisionScope.subject?'<button type="button" class="nk-revision-clear" onclick="window.QB.nkSetRevisionScope(\'subject\',\'\')">Clear focus</button>':'')+'</div>';
  }
  function nkToggleRevisionFocus(){
    nkRevisionFocusOpen=!nkRevisionFocusOpen;
    const area=document.querySelector('.nk-revision-focus'),button=document.querySelector('.nk-revision-focus-toggle');
    if(area)area.hidden=!nkRevisionFocusOpen;
    if(button){button.setAttribute('aria-expanded',String(nkRevisionFocusOpen));button.innerHTML=(nkRevisionFocusOpen?'Hide focus':'Focus questions')+' '+navIcon('chevron',16);}
  }
  function nkSetRevisionScope(field,value){
    const next=String(value||''),choices=nkRevisionScopeChoices();
    if(field==='subject'){
      if(next&&!choices.subjects.includes(next))return;
      nkRevisionScope={subject:next,bank:'',topic:''};
    }else if(field==='bank'){
      if(next&&!choices.banks.includes(next))return;
      nkRevisionScope={...nkRevisionScope,bank:next,topic:''};
    }else if(field==='topic'){
      if(next&&!choices.topics.some(t=>t.id===next))return;
      nkRevisionScope={...nkRevisionScope,topic:next};
    }else return;
    const header=document.querySelector('.nk-revision-focus-wrap'),list=document.querySelector('.nk-revision-list');
    if(header&&list){header.innerHTML=nkRevisionScopeMarkup();list.innerHTML=nkRevisionCards(nkRevisionDeskData());document.getElementById('nk-revision-'+field)?.focus();}
  }
  function nkRevisionDeskData(){
    const questions=nkAllStudyQuestions().filter(nkRevisionScopeMatches);
    const attempts=id=>typeof nkFsrsActiveAttempts==='function'?nkFsrsActiveAttempts(String(id)):
      (qAttempts(String(id))||[]).filter(a=>a&&!a.isUndo);
    const wrong=questions.filter(q=>typeof nkFsrsEligibility==='function'?
      nkFsrsEligibility(q)==='wrong':attempts(q.id).some(a=>a.correct===false));
    const bookmarked=questions.filter(q=>Boolean(state.bookmarks?.[String(q.id)]));
    const unseen=questions.filter(q=>!attempts(q.id).length&&state.fsrsReviewEligible?.[String(q.id)]?.reason!=='skipped');
    const due=typeof nkFsrsQueue==='function'?nkFsrsQueue(nkRevisionScope):
      (typeof nkFsrsLaunchQueue==='function'?nkFsrsLaunchQueue(nkRevisionScope.subject):{cards:[],due:[]});
    return {wrong,bookmarked,unseen,due:due.due||[],dueCards:due.cards||[],rolledOver:Number(due.rolledOver||0)};
  }

  function nkRevisionCard(kind,title,copy,count,actionLabel,disabled=false,detail=''){
    const icon={wrong:'refresh',bookmarks:'bookmark',unseen:'search',due:'clock'}[kind]||'book';
    const browse=!disabled&&['wrong','bookmarks'].includes(kind)?'<button type="button" class="nk-revision-view-all" aria-label="View all '+esc(title.toLowerCase())+'" onclick="window.QB.nav(\'revision-browse\',\''+kind+'\')">View all</button>':'';
    return '<article class="nk-revision-card"><div class="nk-revision-card-head"><span class="nk-revision-icon">'+navIcon(icon,20)+'</span><span class="nk-revision-card-copy"><strong>'+esc(title)+'</strong><small>'+esc(copy)+'</small></span><b>'+fmtNum(count)+'</b></div>'+(detail?'<p class="nk-revision-detail">'+esc(detail)+'</p>':'')+'<div class="nk-revision-actions"><button type="button" '+(disabled?'disabled':'')+' onclick="window.QB.nkStartRevisionQueue(\''+kind+'\')">'+esc(disabled?'Nothing to review':actionLabel)+' '+(disabled?'':navIcon('chevron',16))+'</button>'+browse+'</div></article>';
  }

  function nkRevisionCards(data){
    return nkRevisionCard('wrong','Mistakes','Questions you have answered incorrectly.',data.wrong.length,'Practice '+fmtNum(Math.min(20,data.wrong.length))+' mistakes',!data.wrong.length,data.wrong.length>20?'20 questions per session · sampled from this focus':'')
      +nkRevisionCard('bookmarks','Bookmarks','Questions you saved while studying.',data.bookmarked.length,'Practice '+fmtNum(Math.min(20,data.bookmarked.length))+' bookmarks',!data.bookmarked.length,data.bookmarked.length>20?'20 questions per session · sampled from this focus':'')
      +nkRevisionCard('unseen','Unseen','Questions you have not attempted yet.',data.unseen.length,'Practice '+fmtNum(Math.min(20,data.unseen.length))+' unseen',!data.unseen.length,data.unseen.length>20?'20 questions per session · sampled from this focus':'')
      +nkRevisionCard('due','Due review','Questions scheduled by spaced repetition.',data.due.length,'Review '+fmtNum(Math.min(20,data.dueCards.length))+' due',!data.dueCards.length,(data.dueCards.length>20?'20 questions per session · ':'')+(data.rolledOver?fmtNum(data.dueCards.length)+' available today · '+fmtNum(data.rolledOver)+' roll forward under the daily limit.':'FSRS priority order and daily limit apply.'));
  }
  function nkRevisionDeskPage(){
    const data=nkRevisionDeskData();
    return shell('<main class="nk-app-v114 nk-revision-desk"><header class="nk-v3-page-hero"><div class="nk-kicker">REVISION</div><h1>Quick revision</h1><p>Pick up missed, saved, unseen, or due questions from every subject and bank.</p></header><div class="nk-revision-focus-wrap">'+nkRevisionScopeMarkup()+'</div><section class="nk-revision-list">'
      +nkRevisionCards(data)+'</section></main>','more');
  }

  function nkRevisionBrowsePage(kind){
    if(!['wrong','bookmarks'].includes(kind))return nkRevisionDeskPage();
    const data=nkRevisionDeskData(),rows=kind==='wrong'?data.wrong:data.bookmarked;
    const title=kind==='wrong'?'Mistakes':'Bookmarks';
    return shell('<main class="nk-app-v114 nk-revision-browse"><header class="nk-v3-page-hero"><button class="nk-back-link" onclick="window.QB.nav(\'quick-revision\')">'+navIcon('back',17)+' Quick revision</button><div class="nk-kicker">'+esc(nkRevisionScopeLabel())+'</div><h1>'+title+'</h1><p>'+fmtNum(rows.length)+' questions · search by question, subject, bank, or topic.</p></header><label class="nk-revision-search"><span aria-hidden="true">⌕</span><input type="search" aria-label="Search questions" placeholder="Search questions, subjects, banks" oninput="window.QB.nkFilterRevisionBrowse(this.value)"></label><section class="nk-revision-browse-list">'
      +(rows.length?rows.map(q=>{
        const topic=q.chapter||q.topic||'',meta=[q.subject||'',q.bank||'',topic].filter(Boolean).join(' · ');
        const id=encodeURIComponent(String(q.id)),search=esc((meta+' '+(q.question||'')).toLowerCase());
        return '<article class="nk-revision-item" data-revision-search="'+search+'"><small>'+esc(meta)+'</small><p>'+esc(q.question||'Question text unavailable')+'</p><button type="button" onclick="window.QB.nkOpenRevisionQuestion(\''+id+'\')">Open question '+navIcon('chevron',16)+'</button></article>';
      }).join(''):nkAppEmpty(kind==='wrong'?'refresh':'bookmark',kind==='wrong'?'No mistakes to review':'No bookmarks yet',kind==='wrong'?'Incorrect answers from every subject and bank will appear here.':'Bookmarks from every subject and bank will appear here.'))
      +'</section><p class="nk-revision-no-match" hidden>No questions match your search.</p></main>','more');
  }

  function nkFilterRevisionBrowse(value){
    const term=String(value||'').trim().toLowerCase();let shown=0;
    document.querySelectorAll('.nk-revision-item').forEach(item=>{item.hidden=Boolean(term)&&!item.dataset.revisionSearch.includes(term);if(!item.hidden)shown++;});
    const empty=document.querySelector('.nk-revision-no-match');if(empty)empty.hidden=shown>0;
  }

  function nkOpenRevisionQuestion(encodedId){
    let id;try{id=decodeURIComponent(encodedId)}catch{return;}
    const q=nkFindStudyQuestion(id);if(!q){showToast('This question is unavailable.','bad');return;}
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test before opening another question.','bad');return;}
    if(typeof openBank==='function'&&q.subject&&q.bank)openBank(q.subject,q.bank);
    BY_ID={...BY_ID,[id]:q};practiceOne(id);
  }

  function nkStartRevisionQueue(kind){
    const data=nkRevisionDeskData();
    if(kind==='due'){
      if(!data.dueCards.length){showToast('No reviews are due across your question banks.');return;}
      const rows=data.dueCards.slice(0,20);
      BY_ID={...BY_ID,...Object.fromEntries(rows.map(q=>[String(q.id),q]))};
      startSession(rows.map(q=>String(q.id)),'practice','Quick Revision · Due Review','fsrs');
      if(data.rolledOver)showToast(fmtNum(data.rolledOver)+' due reviews roll forward under your daily limit.');
      return;
    }
    const rows=kind==='wrong'?data.wrong:kind==='bookmarks'?data.bookmarked:kind==='unseen'?data.unseen:[];
    if(!rows.length){showToast('No questions are available in this revision group.');return;}
    const pool=rows.slice();
    for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]];}
    const selected=pool.slice(0,20),ids=selected.map(q=>String(q.id));
    BY_ID={...BY_ID,...Object.fromEntries(selected.map(q=>[String(q.id),q]))};
    const title=kind==='wrong'?'Quick Revision · Mistakes':kind==='bookmarks'?'Quick Revision · Bookmarks':'Quick Revision · Unseen';
    startSession(ids,'practice',title,kind==='wrong'?'wrong':'normal');
  }
  /* NK_REVISION_DESK_V1_END */
