  /* NK_REVISION_DESK_V1_START */
  let nkRevisionScope={subject:'',bank:'',topic:''};
  let nkRevisionFocusOpen=false;
  let nkRevisionBrowseQueries={wrong:"",bookmarks:""},nkRevisionBrowseAccount="";
  function nkRevisionScopeMatches(q,scope=nkRevisionScope){
    return (!scope.subject||q.subject===scope.subject)
      &&(!scope.bank||q.bank===scope.bank)
      &&(!scope.topic||String(q.chapterId)===scope.topic);
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
    if(header&&list){header.innerHTML=nkRevisionScopeMarkup();const data=nkRevisionDeskData();list.innerHTML=nkRevisionCards(data);const forecast=document.querySelector('.nk-revision-forecast');if(forecast)forecast.outerHTML=nkRevisionForecastMarkup();document.getElementById('nk-revision-'+field)?.focus();}
  }
  function nkRevisionDeskData(scope=nkRevisionScope){
    const questions=nkAllStudyQuestions().filter(q=>nkRevisionScopeMatches(q,scope));
    const attempts=id=>typeof nkFsrsActiveAttempts==='function'?nkFsrsActiveAttempts(String(id)):
      (qAttempts(String(id))||[]).filter(a=>a&&!a.isUndo);
    const wrong=questions.filter(q=>typeof nkFsrsPracticeMistake==='function'?
      nkFsrsPracticeMistake(q.id):attempts(q.id).at(-1)?.correct===false);
    const bookmarked=questions.filter(q=>Boolean(state.bookmarks?.[String(q.id)]));
    const unseen=questions.filter(q=>!attempts(q.id).length&&state.fsrsReviewEligible?.[String(q.id)]?.reason!=='skipped'&&(typeof nkFsrsAnswerable!=='function'||nkFsrsAnswerable(q)));
    const due=typeof nkFsrsQueue==='function'?nkFsrsQueue(scope):
      (typeof nkFsrsLaunchQueue==='function'?nkFsrsLaunchQueue(scope.subject):{cards:[],due:[]});
    return {wrong,bookmarked,unseen,due:due.due||[],dueCards:due.cards||[],rolledOver:Number(due.rolledOver||0)};
  }

  function nkHomeRevisionSummary(){
    const data=nkRevisionDeskData({}),due=data.due.length,missed=data.wrong.length;
    return '<section class="nk-home-revision" aria-label="Revision overview"><div class="nk-home-revision-head"><h2>Ready to revisit</h2><button type="button" onclick="window.QB.nkOpenRevisionHub()">Revision '+navIcon('chevron',16)+'</button></div><div class="nk-home-revision-counts"><button type="button" onclick="window.QB.nkOpenRevisionHub()" aria-label="'+fmtNum(due)+' due reviews. Open Revision"><strong class="nk-count-due">'+fmtNum(due)+'</strong><span>Due review</span><small>'+(due?'Scheduled for now':'You’re up to date')+'</small></button><button type="button" onclick="window.QB.nkOpenRevisionHub()" aria-label="'+fmtNum(missed)+' missed questions. Open Revision"><strong class="nk-count-missed">'+fmtNum(missed)+'</strong><span>Mistakes</span><small>'+(missed?'Ready for another pass':'No mistakes to revisit')+'</small></button></div></section>';
  }
  function nkOpenRevisionHub(){nkRevisionScope={subject:'',bank:'',topic:''};nkRevisionFocusOpen=false;navigate('quick-revision');}
  function nkRevisionForecastMarkup(){
    const pool=typeof nkReviewPool==='function'?nkReviewPool(nkRevisionScope.subject).filter(q=>nkRevisionScopeMatches(q)):[];
    const start=new Date();start.setHours(0,0,0,0);
    const days=Array.from({length:7},(_,i)=>{const day=new Date(start);day.setDate(day.getDate()+i);return day;});
    const end=new Date(days[6]);end.setDate(end.getDate()+1);
    const forecast=Array(7).fill(0);
    for(const q of pool){const review=state.reviews?.[q.id],at=Number(review?.nextReviewAt||review?.due||0);if(!at||at<start.getTime())forecast[0]++;else if(at<end.getTime()){const index=days.reduce((index,day,i)=>at>=day.getTime()?i:index,0);forecast[index]++;}}
    const max=Math.max(1,...forecast),total=forecast.reduce((n,x)=>n+x,0);
    return '<section class="nk-revision-forecast" aria-label="Spaced repetition forecast"><div class="nk-revision-forecast-head"><h2>Review forecast</h2><button type="button" onclick="window.QB.nav(\'fsrs\')">Open FSRS '+navIcon('chevron',16)+'</button></div><p>Scheduled reviews for this focus over the next seven days.</p><div class="nk-review-chart" role="img" aria-label="'+esc(forecast.map((n,i)=>(i===0?'Today':days[i].toLocaleDateString(undefined,{weekday:'short'}))+': '+n+' reviews').join('; '))+'">'+forecast.map((n,i)=>'<span><i style="height:'+(n?Math.max(4,Math.round(n/max*64)):0)+'px"></i><b>'+fmtNum(n)+'</b><small>'+(i===0?'Today':esc(days[i].toLocaleDateString(undefined,{weekday:'short'})))+'</small></span>').join('')+'</div><div class="nk-revision-forecast-foot"><small>'+(pool.length?fmtNum(total)+' scheduled · daily review limit applies':'Answer questions to build your review schedule')+'</small><button type="button" onclick="window.QB.nav(\'fsrs-settings\')">Review settings</button></div></section>';
  }
  if(typeof dashboard==='function'){
    const nkRevisionOriginalDashboard=dashboard;
    dashboard=function(){return nkRevisionOriginalDashboard().replace('<section class="nk-section nk-study-sets">',nkHomeRevisionSummary()+'<section class="nk-section nk-study-sets">');};
  }
  if(typeof nkFsrsReviewPage==='function'){
    const nkRevisionOriginalFsrs=nkFsrsReviewPage;
    nkFsrsReviewPage=function(){return nkRevisionOriginalFsrs().replace('<header class="nk-v3-page-hero">','<button class="nk-back-link" onclick="window.QB.nav(\'quick-revision\')">'+navIcon('back',17)+' Revision</button><header class="nk-v3-page-hero">');};
  }

  function nkRevisionCard(kind,title,copy,count,actionLabel,disabled=false,detail=''){
    const icon={wrong:'refresh',bookmarks:'bookmark',unseen:'search',due:'clock'}[kind]||'book';
    const tone={wrong:'is-red',bookmarks:'is-violet',unseen:'is-blue',due:'is-green'}[kind]||'is-indigo';
    const browse=!disabled&&['wrong','bookmarks'].includes(kind)?'<button type="button" class="nk-revision-view-all" aria-label="View all '+esc(title.toLowerCase())+'" onclick="window.QB.nav(\'revision-browse\',\''+kind+'\')">View all</button>':'';
    return '<article class="nk-revision-card '+tone+(count?'':' is-empty')+'"><div class="nk-revision-card-head"><span class="nk-revision-icon">'+navIcon(icon,20)+'</span><span class="nk-revision-card-copy"><strong>'+esc(title)+'</strong><small>'+esc(copy)+'</small></span><b>'+fmtNum(count)+'</b></div>'+(detail?'<p class="nk-revision-detail">'+esc(detail)+'</p>':'')+'<div class="nk-revision-actions"><button type="button" '+(disabled?'disabled':'')+' onclick="window.QB.nkStartRevisionQueue(\''+kind+'\')">'+esc(disabled?'Nothing to review':actionLabel)+' '+(disabled?'':navIcon('chevron',16))+'</button>'+browse+'</div></article>';
  }

  function nkRevisionCards(data){
    return nkRevisionCard('wrong','Mistakes','Questions you have answered incorrectly.',data.wrong.length,'Practice mistakes',!data.wrong.length,'Pause or finish at any point.')
      +nkRevisionCard('bookmarks','Bookmarks','Questions you saved while studying.',data.bookmarked.length,'Practice bookmarks',!data.bookmarked.length,'Pause or finish at any point.')
      +nkRevisionCard('unseen','Unseen','Questions you have not attempted yet.',data.unseen.length,'Practice '+fmtNum(Math.min(20,data.unseen.length))+' unseen',!data.unseen.length,data.unseen.length>20?'20 questions per session · sampled from this focus':'')
      +nkRevisionCard('due','Due review','Questions scheduled by spaced repetition.',data.due.length,'Review due',!data.dueCards.length,(data.rolledOver?fmtNum(data.dueCards.length)+' available today · '+fmtNum(data.rolledOver)+' roll forward under the daily limit.':'Daily review limit applies.'));
  }
  function nkRevisionDeskPage(){
    const data=nkRevisionDeskData();
    return shell('<main class="nk-app-v114 nk-revision-desk"><header class="nk-v3-page-hero"><div class="nk-kicker">REVISION</div><h1>Revision</h1><p>Pick up missed, saved, unseen, or due questions from every subject and bank.</p></header>'+(typeof nkRevisionPausedMarkup==='function'?nkRevisionPausedMarkup():'')+'<div class="nk-revision-focus-wrap">'+nkRevisionScopeMarkup()+'</div><section class="nk-revision-list">'
      +nkRevisionCards(data)+'</section>'+nkRevisionForecastMarkup()+'</main>','quick-revision');
  }

  function nkRevisionBrowsePage(kind){
    if(!['wrong','bookmarks'].includes(kind))return nkRevisionDeskPage();
    const account=String(typeof nkAuth!=='undefined'&&nkAuth?.uid||'local');
    if(account!==nkRevisionBrowseAccount){nkRevisionBrowseQueries={wrong:'',bookmarks:''};nkRevisionBrowseAccount=account;}
    const query=nkRevisionBrowseQueries[kind]||'',term=query.trim().toLowerCase();let shown=0;
    const data=nkRevisionDeskData(),rows=kind==='wrong'?data.wrong:data.bookmarked;
    const title=kind==='wrong'?'Mistakes':'Bookmarks';
    return shell('<main class="nk-app-v114 nk-revision-browse"><header class="nk-v3-page-hero"><button class="nk-back-link" onclick="window.QB.nav(\'quick-revision\')">'+navIcon('back',17)+' Revision</button><div class="nk-kicker">'+esc(nkRevisionScopeLabel())+'</div><h1>'+title+'</h1><p>'+fmtNum(rows.length)+' questions · search by question, subject, bank, or topic.</p></header><label class="nk-revision-search"><span aria-hidden="true">'+navIcon('search',20)+'</span><input type="search" value="'+esc(query)+'" aria-label="Search questions" placeholder="Search questions, subjects, banks" oninput="window.QB.nkFilterRevisionBrowse(this.value)"></label><section class="nk-revision-browse-list">'
      +(rows.length?rows.map(q=>{
        const topic=q.chapter||q.topic||'',meta=[q.subject||'',q.bank||'',topic].filter(Boolean).join(' · ');
        const id=encodeURIComponent(String(q.id)),raw=(meta+' '+(q.question||'')).toLowerCase(),search=esc(raw),hidden=Boolean(term)&&!raw.includes(term);if(!hidden)shown++;
        return '<article class="nk-revision-item"'+(hidden?' hidden':'')+' data-revision-search="'+search+'"><small>'+esc(meta)+'</small><p>'+esc(q.question||'Question text unavailable')+'</p><button type="button" onclick="window.QB.nkOpenRevisionQuestion(\''+id+'\')">Open question '+navIcon('chevron',16)+'</button></article>';
      }).join(''):nkAppEmpty(kind==='wrong'?'refresh':'bookmark',kind==='wrong'?'No mistakes to review':'No bookmarks yet',kind==='wrong'?'Incorrect answers from every subject and bank will appear here.':'Bookmarks from every subject and bank will appear here.'))
      +'</section><p class="nk-revision-no-match" role="status"'+(shown||!rows.length?' hidden':'')+'>No questions match your search.</p></main>','quick-revision');
  }

  function nkFilterRevisionBrowse(value){
    if(['wrong','bookmarks'].includes(route.id))nkRevisionBrowseQueries[route.id]=String(value||'');
    const term=String(value||'').trim().toLowerCase();let shown=0;
    document.querySelectorAll('.nk-revision-item').forEach(item=>{item.hidden=Boolean(term)&&!item.dataset.revisionSearch.includes(term);if(!item.hidden)shown++;});
    const empty=document.querySelector('.nk-revision-no-match');if(empty)empty.hidden=shown>0;
  }

  function nkOpenRevisionQuestion(encodedId){
    let id;try{id=decodeURIComponent(encodedId)}catch{return;}
    const q=nkFindStudyQuestion(id);if(!q){showToast('This question is unavailable.','bad');return;}
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test before opening another question.','bad');return;}
    const kind=['wrong','bookmarks'].includes(route.id)?route.id:null,previous=state.activeSession?.id;
    if(typeof openBank==='function'&&q.subject&&q.bank)openBank(q.subject,q.bank);
    BY_ID={...BY_ID,[id]:q};
    startSession([id],'practice',`Question ${q.questionNumber||''}`,kind==='wrong'?'wrong':kind==='bookmarks'?'bookmarked':'normal');
    if(state.activeSession?.id!==previous&&state.activeSession?.questionIds?.[0]===id){
      state.activeSession.originRoute=kind?'revision-browse/'+kind:'quick-revision';saveState();
    }
  }

  function nkStartRevisionQueue(kind){
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your timed test before starting revision.','bad');return false;}
    const previous=state.activeSession?.id;
    const data=nkRevisionDeskData();
    if(kind==='due'){
      if(!data.dueCards.length){showToast('No reviews are due across your question banks.');return;}
      const rows=data.dueCards;
      BY_ID={...BY_ID,...Object.fromEntries(rows.map(q=>[String(q.id),q]))};
      startSession(rows.map(q=>String(q.id)),'practice','Quick Revision · Due Review','fsrs');
      if(typeof nkRevisionTagSession==='function')nkRevisionTagSession(kind,previous,rows.map(q=>String(q.id)));
      if(data.rolledOver)showToast(fmtNum(data.rolledOver)+' due reviews roll forward under your daily limit.');
      return;
    }
    const rows=kind==='wrong'?data.wrong:kind==='bookmarks'?data.bookmarked:kind==='unseen'?data.unseen:[];
    if(!rows.length){showToast('No questions are available in this revision group.');return;}
    const pool=rows.slice();
    for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]];}
    const selected=kind==='unseen'?pool.slice(0,20):pool,ids=selected.map(q=>String(q.id));
    BY_ID={...BY_ID,...Object.fromEntries(selected.map(q=>[String(q.id),q]))};
    const title=kind==='wrong'?'Quick Revision · Mistakes':kind==='bookmarks'?'Quick Revision · Bookmarks':'Quick Revision · Unseen';
    startSession(ids,'practice',title,kind==='wrong'?'wrong':kind==='bookmarks'?'bookmarked':'normal');
    if(typeof nkRevisionTagSession==='function')nkRevisionTagSession(kind,previous,ids);
  }
  /* NK_REVISION_DESK_V1_END */
