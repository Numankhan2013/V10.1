  /* NK_BANK_AWARE_CBT_BUILDER_V1_START */
  let nkCbtDraft=null;
  // Bank records are immutable after boot. Index each record once so rapid
  // topic toggles do not scan the whole question bank for every painted row.
  const nkCbtTopicIndex=new WeakMap();
  // Which questions a test may draw. A bank module can narrow it (UWorld drops questions
  // whose exhibit is missing); the index, the counts and the pool all go through it.
  function nkCbtEligible(q){return typeof nkCountable!=='function'||nkCountable(q);}
  function nkCbtQuestionsByTopic(record){
    if(!record)return new Map();
    // Keyed by the record, checked against its question list: a bank that is filtered
    // or extended in place is indexed again.
    let index=nkCbtTopicIndex.get(record);
    if(!index||index.source!==record.questions||index.size0!==(record.questions||[]).length){
      index=new Map();
      (record.questions||[]).forEach(q=>{
        if(!nkCbtEligible(q))return;
        const key=String(q.chapterId),list=index.get(key)||[];
        list.push(q);index.set(key,list);
      });
      index.source=record.questions;index.size0=(record.questions||[]).length;
      nkCbtTopicIndex.set(record,index);
    }
    return index;
  }

  // Per record, once: topic keys, question counts and PYQ flags, so a tap never
  // re-walks a bank's questions or rebuilds keys for thousands of topics.
  const nkCbtRecordInfoCache=new WeakMap();
  function nkCbtRecordInfo(record){
    let info=nkCbtRecordInfoCache.get(record);
    const byTopic=nkCbtQuestionsByTopic(record);
    if(!info||info.index!==byTopic){
      const topics=nkModuleTopics(record);
      info={topics,keys:[],counts:[],pyq:[],verifiedPyq:[],index:byTopic};
      topics.forEach((topic,i)=>{
        const questions=byTopic.get(String(topic.id))||[],pyq=questions.filter(q=>Array.isArray(q.studyCollections)&&q.studyCollections.includes('pyq')).length;
        info.keys[i]=nkCbtTopicKey(record,topic);info.counts[i]=questions.length;
        info.pyq[i]=pyq>0;info.verifiedPyq[i]=questions.length>0&&pyq===questions.length;
      });
      nkCbtRecordInfoCache.set(record,info);
    }
    return info;
  }
  // Questions a test can draw from the bank: the card agrees with the topic step.
  function nkCbtRecordSize(record){return nkCbtRecordInfo(record).counts.reduce((sum,n)=>sum+n,0);}
  // Every change to the selection drops the cached pool.
  function nkCbtTouch(){if(nkCbtDraft)nkCbtDraft.poolCache=null;}

  function nkCbtRecords(){
    return Object.values(BANKS_BY_SUBJECT).flat().filter(record=>record?.subject&&record?.bank&&Array.isArray(record.questions));
  }

  function nkCbtRecordKey(record){return nkModuleScopeKey(record.subject,record.bank);}
  function nkCbtTopicKey(record,topic){return nkModuleTopicKey(record.subject,topic.id,record.bank);}
  function nkCbtSelectedRecords(){
    const selected=new Set(nkCbtDraft?.bankKeys||[]);
    return nkCbtRecords().filter(record=>selected.has(nkCbtRecordKey(record)));
  }
  function nkCbtTopicCount(record,topic){
    return (nkCbtQuestionsByTopic(record).get(String(topic.id))||[]).length;
  }
  function nkCbtVerifiedPyqTopics(){
    return nkCbtSelectedRecords().flatMap(record=>{
      const info=nkCbtRecordInfo(record);
      return info.topics.filter((_topic,i)=>info.verifiedPyq[i]).map(topic=>({record,topic}));
    });
  }
  function nkCbtSelectVerifiedPyqs(){
    if(!nkCbtDraft)return;
    const topics=nkCbtVerifiedPyqTopics();
    if(!topics.length)return;
    const keys=new Set(topics.map(({record,topic})=>nkCbtTopicKey(record,topic)));
    // Turning PYQs off returns to the selection the user had before turning them on.
    if(nkCbtDraft.pyqSelected){
      const prior=nkCbtDraft.prePyqTopicKeys;
      const added=nkCbtDraft.topicKeys.filter(key=>!keys.has(key));
      nkCbtDraft.topicKeys=Array.isArray(prior)?[...new Set([...prior,...added])]:added;
      nkCbtDraft.prePyqTopicKeys=null;
    }else{
      nkCbtDraft.prePyqTopicKeys=nkCbtDraft.topicKeys.slice();
      nkCbtDraft.topicKeys=[...keys];
    }
    nkCbtDraft.pyqSelected=!nkCbtDraft.pyqSelected;
    nkCbtTouch();nkCbtSyncTopics();
  }
  function nkCbtPool(){
    if(nkCbtDraft?.poolCache)return nkCbtDraft.poolCache.slice();
    const selected=new Set(nkCbtDraft?.topicKeys||[]),seen=new Set(),questions=[];
    nkCbtSelectedRecords().forEach(record=>{
      const info=nkCbtRecordInfo(record),byTopic=nkCbtQuestionsByTopic(record);
      info.topics.forEach((topic,i)=>{
        if(!selected.has(info.keys[i]))return;
        (byTopic.get(String(topic.id))||[]).forEach(q=>{const id=String(q.id);if(!seen.has(id)){seen.add(id);questions.push(q);}});
      });
    });
    if(nkCbtDraft)nkCbtDraft.poolCache=questions;
    return questions.slice();
  }
  // The pool is deduplicated by question id. When no id appears in two banks (checked once
  // per set of banks), its size is a plain sum of the selected topics' counts.
  let nkCbtSharedIds=null;
  function nkCbtIdsShared(){
    const records=nkCbtRecords(),sig=records.map(record=>(record.questions||[]).length).join(',');
    if(nkCbtSharedIds?.sig!==sig){
      const seen=new Set();let shared=false;
      records.forEach(record=>(record.questions||[]).forEach(q=>{const id=String(q.id);if(seen.has(id))shared=true;else seen.add(id);}));
      nkCbtSharedIds={sig,shared};
    }
    return nkCbtSharedIds.shared;
  }
  function nkCbtPoolSize(){
    if(nkCbtDraft?.poolCache)return nkCbtDraft.poolCache.length;
    if(nkCbtIdsShared())return nkCbtPool().length;
    const selected=new Set(nkCbtDraft?.topicKeys||[]);let size=0;
    nkCbtSelectedRecords().forEach(record=>{const info=nkCbtRecordInfo(record);info.keys.forEach((key,i)=>{if(selected.has(key))size+=info.counts[i];});});
    return size;
  }
  function nkCbtFreshDraft(){
    const records=nkCbtRecords();
    return {step:1,bankKeys:records.map(nkCbtRecordKey),topicKeys:records.flatMap(record=>nkCbtRecordInfo(record).keys),pyqSelected:false,count:20,openGroups:{},query:'',queryText:''};
  }
  // A reload keeps the draft for this tab only (sessionStorage), never across visits.
  const NK_CBT_DRAFT_KEY='nk.cbt.draft';
  function nkCbtRememberDraft(){
    try{if(nkCbtDraft){const {poolCache,...draft}=nkCbtDraft;sessionStorage.setItem(NK_CBT_DRAFT_KEY,JSON.stringify(draft));}else sessionStorage.removeItem(NK_CBT_DRAFT_KEY);}catch(_){}
  }
  function nkCbtRestoredDraft(){
    try{const draft=JSON.parse(sessionStorage.getItem(NK_CBT_DRAFT_KEY)||'null');if(draft&&Array.isArray(draft.bankKeys)&&Array.isArray(draft.topicKeys)&&[1,2,3].includes(draft.step))return draft;}catch(_){}
    return null;
  }
  if(typeof window!=='undefined'){
    window.addEventListener('pagehide',nkCbtRememberDraft);
    document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')nkCbtRememberDraft();});
  }
  function nkCbtOpenBuilder(){
    nkCbtDraft=nkCbtFreshDraft();
    navigate('test-builder');
  }
  function nkCbtSetBanks(select){
    if(!nkCbtDraft)return;
    const records=nkCbtRecords();
    nkCbtDraft.bankKeys=select?records.map(nkCbtRecordKey):[];
    nkCbtDraft.topicKeys=select?records.flatMap(record=>nkCbtRecordInfo(record).keys):[];
    nkCbtDraft.pyqSelected=false;nkCbtTouch();
    if(!nkCbtSyncBanks())render();
  }
  function nkCbtToggleBank(index){
    if(!nkCbtDraft)return;
    const record=nkCbtRecords()[index];if(!record)return;
    const key=nkCbtRecordKey(record),banks=new Set(nkCbtDraft.bankKeys),topics=new Set(nkCbtDraft.topicKeys);
    if(banks.has(key)){
      banks.delete(key);
      nkCbtRecordInfo(record).keys.forEach(topicKey=>topics.delete(topicKey));
    }else{
      banks.add(key);
      nkCbtRecordInfo(record).keys.forEach(topicKey=>topics.add(topicKey));
    }
    nkCbtDraft.bankKeys=[...banks];nkCbtDraft.topicKeys=[...topics];nkCbtDraft.pyqSelected=false;nkCbtTouch();
    if(!nkCbtSyncBanks())render();
  }
  // Bank taps update the rows in place: a full render of the step costs far more than the tap.
  function nkCbtSyncBanks(){
    const intro=document.getElementById('nk-cbt-bank-count');if(!intro||!document.querySelectorAll)return false;
    const records=nkCbtRecords(),selected=new Set(nkCbtDraft.bankKeys);
    document.querySelectorAll('.nk-cbt-builder .nk-module-subject[data-bank-index]').forEach(button=>{
      const record=records[Number(button.dataset.bankIndex)];if(!record)return;
      const picked=selected.has(nkCbtRecordKey(record));
      if(button.classList.contains('is-selected')!==picked){button.classList.toggle('is-selected',picked);button.setAttribute('aria-pressed',String(picked));}
    });
    intro.textContent=`${selected.size} of ${records.length} banks selected`;
    document.querySelectorAll('.nk-cbt-builder .nkg-bank-group').forEach(group=>{
      const rows=group.querySelectorAll('.nk-module-subject'),on=group.querySelectorAll('.nk-module-subject.is-selected').length,count=group.querySelector(':scope > header > span');
      if(count)count.textContent=`${on} of ${rows.length}`;
    });
    const sum=document.querySelector('.nk-cbt-builder .nkg-dock-sum');if(sum)sum.textContent=`${selected.size} of ${records.length} banks selected`;
    const next=document.getElementById('nk-cbt-banks-continue');if(next)next.disabled=!selected.size;
    return true;
  }
  function nkCbtSetStep(step){
    if(!nkCbtDraft)return;
    if(step>nkCbtDraft.step){
      if(!nkCbtDraft.bankKeys.length){showToast('Choose at least one question bank.','bad');return;}
      if(step>2&&!nkCbtPoolSize()){showToast('Choose a topic with questions.','bad');return;}
    }
    nkCbtDraft.step=Math.max(1,Math.min(3,Number(step)));nkCbtDraft.query='';nkCbtDraft.queryText='';
    // The pool caps what is shown; widening the topics later restores the count the user asked for.
    if(nkCbtDraft.step===3){if(nkCbtDraft.requestedCount==null)nkCbtDraft.requestedCount=nkCbtDraft.count;nkCbtDraft.count=Math.min(nkCbtDraft.requestedCount,nkCbtPoolSize());}
    render();resetScrollPosition();
  }
  function nkCbtSetTopics(select,recordIndex=null){
    if(!nkCbtDraft)return;
    const selected=new Set(nkCbtDraft.topicKeys),records=recordIndex===null?nkCbtSelectedRecords():[nkCbtRecords()[recordIndex]];
    records.filter(Boolean).forEach(record=>nkCbtRecordInfo(record).keys.forEach(key=>{
      if(select)selected.add(key);else selected.delete(key);
    }));
    nkCbtDraft.topicKeys=[...selected];if(recordIndex===null)nkCbtDraft.pyqSelected=false;nkCbtTouch();nkCbtSyncTopics();
  }
  function nkCbtToggleGroup(recordIndex){
    const record=nkCbtRecords()[recordIndex];if(!record)return;
    const selected=new Set(nkCbtDraft?.topicKeys||[]),keys=nkCbtRecordInfo(record).keys;
    nkCbtSetTopics(!keys.every(key=>selected.has(key)),recordIndex);
  }
  function nkCbtToggleTopic(recordIndex,topicIndex){
    if(!nkCbtDraft)return;
    const record=nkCbtRecords()[recordIndex],key=record&&nkCbtRecordInfo(record).keys[topicIndex];if(!key)return;
    const selected=new Set(nkCbtDraft.topicKeys);
    if(selected.has(key))selected.delete(key);else selected.add(key);
    nkCbtDraft.topicKeys=[...selected];nkCbtTouch();nkCbtSyncTopics();
  }
  function nkCbtSyncTopics(){
    const records=nkCbtRecords(),selected=new Set(nkCbtDraft?.topicKeys||[]);
    if(nkCbtDraft?.pyqSelected&&!nkCbtVerifiedPyqTopics().every(({record,topic})=>selected.has(nkCbtTopicKey(record,topic))))nkCbtDraft.pyqSelected=false;
    const pyqToggle=document.getElementById('nk-cbt-pyq-toggle');
    if(pyqToggle){pyqToggle.classList.toggle('is-selected',Boolean(nkCbtDraft?.pyqSelected));pyqToggle.setAttribute('aria-pressed',String(Boolean(nkCbtDraft?.pyqSelected)));}
    // Only rows of open groups exist; the check mark is drawn by CSS from is-selected.
    document.querySelectorAll('.nk-cbt-topic[data-record-index]').forEach(button=>{
      const record=records[Number(button.dataset.recordIndex)],key=record&&nkCbtRecordInfo(record).keys[Number(button.dataset.topicIndex)];
      if(!key)return;
      const picked=selected.has(key);
      if(button.classList.contains('is-selected')!==picked){button.classList.toggle('is-selected',picked);button.setAttribute('aria-pressed',String(picked));}
    });
    document.querySelectorAll('.nk-cbt-topic-group').forEach(group=>{
      const record=records[Number(group.dataset.recordIndex)];if(!record)return;
      const keys=nkCbtRecordInfo(record).keys,count=keys.filter(key=>selected.has(key)).length;
      const status=group.querySelector('.nk-module-group-count'),action=group.querySelector('.nk-module-group-action');
      const label=`${count} of ${keys.length} selected`,verb=count===keys.length?`Clear ${keys.length}`:`Select ${keys.length}`;
      if(status&&status.textContent!==label)status.textContent=label;
      if(action&&action.textContent!==verb)action.textContent=verb;
    });
    const pool=nkCbtPoolSize(),label=`${selected.size} topic${selected.size===1?'':'s'} · ${fmtNum(pool)} question${pool===1?'':'s'}`;
    for(const id of ['nk-cbt-selected-count','nk-cbt-footer-count']){
      const node=document.getElementById(id);if(node)node.textContent=label;
    }
    const next=document.getElementById('nk-cbt-topics-continue');if(next)next.disabled=!pool;
  }
  // Search filters the data and redraws only the matching rows, never every topic of every bank.
  function nkCbtFilterTopics(value){
    if(!nkCbtDraft)return;
    nkCbtDraft.queryText=String(value||'');nkCbtDraft.query=nkCbtDraft.queryText.trim().toLocaleLowerCase();
    const box=document.querySelector?.('.nk-cbt-builder .nk-module-topic-groups');
    if(box)box.innerHTML=nkCbtTopicGroupsMarkup();
    const search=nkCbtSearchStatus(),status=document.getElementById('nk-cbt-search-status'),empty=document.getElementById('nk-cbt-search-empty');
    if(status)status.textContent=search.label;
    if(empty)empty.hidden=!search.empty;
  }
  // The search line and the no-match note, drawn the same by a search and a full render.
  function nkCbtSearchStatus(){
    const query=nkCbtDraft?.query||'';if(!query)return {label:'',empty:false};
    let visible=0;
    nkCbtRecords().forEach(record=>{if(nkCbtDraft.bankKeys.includes(nkCbtRecordKey(record)))visible+=nkCbtMatchingTopics(record).length;});
    return {label:`${visible} matching topic${visible===1?'':'s'}`,empty:!visible};
  }
  function nkCbtMatchingTopics(record){
    const info=nkCbtRecordInfo(record),query=nkCbtDraft?.query||'',all=info.topics.map((_topic,i)=>i);
    if(!query||`${record.subject} · ${record.bank}`.toLocaleLowerCase().includes(query))return all;
    return all.filter(i=>String(info.topics[i].title||'').toLocaleLowerCase().includes(query));
  }
  function nkCbtGroupOpen(recordIndex){
    if(nkCbtDraft?.query)return true;
    const choice=(nkCbtDraft?.openGroups||{})[recordIndex];
    return choice===undefined?nkCbtSelectedRecords().length===1:choice;
  }
  // Collapsed groups hold no rows: opening one draws its topics in place.
  function nkCbtToggleOpen(recordIndex){
    // A search shows every matching group open; its toggles change nothing until it clears.
    if(!nkCbtDraft||nkCbtDraft.query)return;
    nkCbtDraft.openGroups={...(nkCbtDraft.openGroups||{}),[recordIndex]:!nkCbtGroupOpen(recordIndex)};
    const group=document.querySelector?.(`.nk-cbt-topic-group[data-record-index="${recordIndex}"]`),record=nkCbtRecords()[recordIndex];
    if(!group||!record){render();return;}
    const isOpen=nkCbtGroupOpen(recordIndex),list=group.querySelector('.nk-module-topic-list'),toggle=group.querySelector('.nk-cbt-group-toggle');
    group.classList.toggle('is-collapsed',!isOpen);
    if(list)list.innerHTML=isOpen?nkCbtTopicRowsMarkup(record,recordIndex):'';
    if(toggle){toggle.setAttribute('aria-expanded',String(isOpen));toggle.setAttribute('aria-label',`${isOpen?'Hide':'Show'} ${record.subject} · ${record.bank} topics`);}
  }
  // typing: the field keeps what is typed; the value is tidied when the field changes.
  function nkCbtSetCount(value,typing){
    if(!nkCbtDraft)return;
    if(value==='')return;
    const number=Number(value);if(!Number.isFinite(number))return;
    const pool=nkCbtPoolSize();
    nkCbtDraft.count=Math.max(1,Math.min(pool,Math.floor(number)));
    const actual=nkCbtDraft.count;nkCbtDraft.requestedCount=actual;
    const input=document.getElementById('nk-cbt-custom-count');if(input&&!typing)input.value=String(nkCbtDraft.count);
    document.querySelectorAll('.nk-cbt-count-preset').forEach(button=>button.classList.toggle('is-selected',Number(button.dataset.count)===nkCbtDraft.count));
    const result=document.getElementById('nk-cbt-count-result');
    if(result)result.textContent=`${fmtNum(actual)} question${actual===1?'':'s'} · ${fmtNum(actual)} minute${actual===1?'':'s'} total`;
  }
  function nkCbtTitle(questions=[]){
    if(questions.length&&questions.every(q=>Array.isArray(q.studyCollections)&&q.studyCollections.includes('pyq')))return 'PYQ CBT';
    const records=nkCbtSelectedRecords();
    if(records.length===1)return `${records[0].subject} · ${records[0].bank} CBT`;
    const subjects=[...new Set(records.map(record=>record.subject))];
    return subjects.length===1?`${subjects[0]} · Mixed Banks CBT`:'Mixed Subjects CBT';
  }
  function nkCbtStart(){
    const pool=nkCbtPool();if(!pool.length){showToast('Choose a topic with questions.','bad');return;}
    const ids=pool.map(q=>String(q.id));
    for(let i=ids.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[ids[i],ids[j]]=[ids[j],ids[i]];}
    const count=Math.min(Math.max(1,Number(nkCbtDraft.count||20)),ids.length);
    BY_ID={...BY_ID,...Object.fromEntries(pool.map(q=>[String(q.id),q]))};
    const chosen=ids.slice(0,count),byId=new Map(pool.map(q=>[String(q.id),q]));
    const started=startSession(chosen,'exam',nkCbtTitle(chosen.map(id=>byId.get(id))));
    if(started===false||state.activeSession?.mode!=='exam')return;
    state.activeSession.originRoute='tests';saveState();
    nkCbtDraft=null;
  }
  function nkCbtBanksMarkup(){
    const selected=new Set(nkCbtDraft.bankKeys),records=nkCbtRecords();
    return `<div class="nk-cbt-bank-intro"><strong>Choose the sources for this test</strong><span id="nk-cbt-bank-count">${selected.size} of ${records.length} banks selected</span></div><div class="nk-module-select-tools nk-cbt-bank-tools"><button type="button" onclick="window.QB.nkCbtSetBanks(true)">Select all</button><button type="button" onclick="window.QB.nkCbtSetBanks(false)">Clear all</button></div><div class="nk-module-choice-grid">${records.map((record,index)=>{const picked=selected.has(nkCbtRecordKey(record)),meta=nkAppSubjectMeta(record.subject);return `<button type="button" class="nk-module-subject is-${meta.key} ${picked?'is-selected':''}" data-bank-index="${index}" aria-pressed="${picked}" onclick="window.QB.nkCbtToggleBank(${index})"><span>${nkAppSubjectIcon(record.subject,23)}</span><strong>${esc(record.subject)}</strong><small>${esc(record.bank)} · ${fmtNum(nkCbtRecordSize(record))} questions · ${fmtNum(nkModuleTopics(record).length)} topics</small><i>${picked?navIcon('check',15):''}</i></button>`;}).join('')}</div>`;
  }
  function nkCbtTopicRowsMarkup(record,recordIndex){
    const info=nkCbtRecordInfo(record),selected=new Set(nkCbtDraft.topicKeys),check=navIcon('check',16);
    return nkCbtMatchingTopics(record).map(topicIndex=>{const topic=info.topics[topicIndex],picked=selected.has(info.keys[topicIndex]);return `<button type="button" class="nk-module-topic nk-cbt-topic ${picked?'is-selected':''}" data-record-index="${recordIndex}" data-topic-index="${topicIndex}" aria-pressed="${picked}" onclick="window.QB.nkCbtToggleTopic(${recordIndex},${topicIndex})"><span class="nk-module-topic-copy"><strong>${esc(topic.title)}</strong><small>${fmtNum(info.counts[topicIndex])} question${info.counts[topicIndex]===1?'':'s'}${info.pyq[topicIndex]?' · PYQs':''}</small></span><span class="nk-module-check nkg-check" aria-hidden="true">${check}</span></button>`;}).join('');
  }
  function nkCbtTopicGroupsMarkup(){
    const selected=new Set(nkCbtDraft.topicKeys),caret=typeof window!=='undefined'&&window.NKQ_ICONS?.['caret-down']?`<svg data-nkg-icon="caret-down" width="16" height="16" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" focusable="false">${window.NKQ_ICONS['caret-down']}</svg>`:'';
    return nkCbtRecords().map((record,recordIndex)=>{
      if(!nkCbtDraft.bankKeys.includes(nkCbtRecordKey(record)))return'';
      if(nkCbtDraft.query&&!nkCbtMatchingTopics(record).length)return'';
      const keys=nkCbtRecordInfo(record).keys,count=keys.filter(key=>selected.has(key)).length,open=nkCbtGroupOpen(recordIndex),name=`${record.subject} · ${record.bank}`;
      return `<section class="nk-module-topic-group nk-cbt-topic-group ${open?'':'is-collapsed'}" data-record-index="${recordIndex}"><header><span class="is-${nkAppSubjectMeta(record.subject).key}">${nkAppSubjectIcon(record.subject,20)}</span><div onclick="window.QB.nkCbtToggleOpen(${recordIndex})" style="cursor:pointer"><strong class="nk-module-group-title">${esc(name)}</strong><small class="nk-module-group-count">${count} of ${keys.length} selected</small></div><button type="button" class="nk-module-group-action" onclick="window.QB.nkCbtToggleGroup(${recordIndex})">${count===keys.length?`Clear ${keys.length}`:`Select ${keys.length}`}</button><button type="button" class="nkg-group-toggle nk-cbt-group-toggle" aria-expanded="${open}" aria-label="${open?'Hide':'Show'} ${esc(name)} topics" onclick="window.QB.nkCbtToggleOpen(${recordIndex})">${caret}</button></header><div class="nk-module-topic-list">${open?nkCbtTopicRowsMarkup(record,recordIndex):''}</div></section>`;
    }).join('');
  }
  function nkCbtTopicsMarkup(poolLength){
    const selected=new Set(nkCbtDraft.topicKeys),active=nkCbtSelectedRecords();
    const total=active.reduce((sum,record)=>sum+nkCbtRecordInfo(record).topics.length,0),pool=poolLength===undefined?nkCbtPoolSize():poolLength;
    const search=nkCbtSearchStatus(),pyqTopics=nkCbtVerifiedPyqTopics(),pyqQuestions=pyqTopics.reduce((sum,{record,topic})=>sum+nkCbtTopicCount(record,topic),0);
    return `<div class="nk-module-topic-intro"><strong>${fmtNum(total)} topics in ${active.length} selected bank${active.length===1?'':'s'}</strong><span id="nk-cbt-selected-count">${selected.size} topics · ${fmtNum(pool)} questions</span></div><label class="nk-module-topic-search"><span>Search topics</span><input type="search" placeholder="Search by chapter or topic name" autocomplete="off" value="${esc(nkCbtDraft.queryText||'')}" oninput="window.QB.nkCbtFilterTopics(this.value)"></label><div class="nk-module-select-tools nk-cbt-topic-tools"><button type="button" onclick="window.QB.nkCbtSetTopics(true)">Select all</button><button type="button" onclick="window.QB.nkCbtSetTopics(false)">Clear all</button><button type="button" id="nk-cbt-pyq-toggle" class="nk-cbt-pyq-toggle ${nkCbtDraft.pyqSelected?'is-selected':''}" aria-pressed="${Boolean(nkCbtDraft.pyqSelected)}" aria-label="Only verified PYQ topics, ${pyqTopics.length} eligible topics, ${fmtNum(pyqQuestions)} questions" ${pyqTopics.length?'':'disabled'} onclick="window.QB.nkCbtSelectVerifiedPyqs()"><span>Only PYQ</span><small>${fmtNum(pyqTopics.length)} topics · ${fmtNum(pyqQuestions)} Q</small></button></div>${pyqTopics.length?'':'<p class="nk-cbt-pyq-empty" role="status">No verified PYQ topics in the selected banks. Your draft is unchanged.</p>'}<div id="nk-cbt-search-status" class="nk-module-search-status" role="status">${esc(search.label)}</div><div class="nk-module-topic-groups">${nkCbtTopicGroupsMarkup()}</div><div id="nk-cbt-search-empty" class="nk-module-search-empty" ${search.empty?'':'hidden'}>No topics match your search.</div>`;
  }
  function nkCbtQuestionsMarkup(poolLength){
    const pool=poolLength===undefined?nkCbtPoolSize():poolLength,actual=Math.min(nkCbtDraft.count,pool),records=nkCbtSelectedRecords();
    const banksBySubject=new Map();records.forEach(record=>{
      const list=banksBySubject.get(record.subject)||[];list.push(record.bank);banksBySubject.set(record.subject,list);
    });
    const bankSummary=[...banksBySubject].map(([subject,banks])=>`${esc(subject)} · ${banks.map(esc).join(' + ')}`).join('<br>');
    const presets=[10,20,50,100].filter(number=>number<=pool);if(!presets.length)presets.push(pool);
    return `<div class="nk-cbt-summary"><div><small>Question banks</small><strong>${bankSummary}</strong></div><div><small>Available pool</small><strong>${fmtNum(pool)} questions</strong><p>${nkCbtDraft.topicKeys.length} selected topics</p></div></div><div class="nk-cbt-count"><h2>How many questions?</h2><p>Questions are randomly drawn from the topics you selected.</p><div class="nk-cbt-count-grid">${presets.map(number=>`<button type="button" class="nk-cbt-count-preset ${nkCbtDraft.count===number?'is-selected':''}" data-count="${number}" onclick="window.QB.nkCbtSetCount(${number})">${number}</button>`).join('')}</div><label for="nk-cbt-custom-count">Custom amount</label><input id="nk-cbt-custom-count" type="number" inputmode="numeric" min="1" max="${pool}" value="${nkCbtDraft.count}" oninput="window.QB.nkCbtSetCount(this.value,true)" onchange="window.QB.nkCbtSetCount(this.value)"></div><div class="nk-cbt-timing"><span>${navIcon('clock',20)}</span><div><strong id="nk-cbt-count-result">${fmtNum(actual)} questions · ${fmtNum(actual)} minutes total</strong><p>One minute per question. Answers and explanations appear after submission.</p></div></div>`;
  }
  function nkCbtBuilderPage(){
    if(!nkCbtDraft)nkCbtDraft=nkCbtRestoredDraft()||nkCbtFreshDraft();
    nkCbtRememberDraft();
    const step=nkCbtDraft.step,titles=['Choose question banks','Choose topics','Set question count'];
    /* One pool scan per render: the topic and count screens share it instead of
       re-walking every selected question's topic. */
    const poolLength=step>1?nkCbtPoolSize():0;
    const content=step===1?nkCbtBanksMarkup():step===2?nkCbtTopicsMarkup(poolLength):nkCbtQuestionsMarkup(poolLength);
    const action=step===2?`<div class="nk-module-builder-actions nk-module-topic-actions nk-cbt-actions"><span id="nk-cbt-footer-count">${nkCbtDraft.topicKeys.length} topics · ${fmtNum(poolLength)} questions</span><button id="nk-cbt-topics-continue" class="is-primary" ${poolLength?'':'disabled'} onclick="window.QB.nkCbtSetStep(3)">Continue to questions</button></div>`:step===1?`<div class="nk-cbt-main-actions"><button id="nk-cbt-banks-continue" class="is-primary" ${nkCbtDraft.bankKeys.length?'':'disabled'} onclick="window.QB.nkCbtSetStep(2)">Continue to topics</button></div>`:`<div class="nk-cbt-main-actions"><button class="is-primary" onclick="window.QB.nkCbtStart()">Start timed CBT</button></div>`;
    const description=step===1?'Choose the question banks you want to study.':step===2?'Search or scroll, then tap the topics you want to test.':'Set the number of questions. Your time limit updates with it.';
    return shell(`<main class="nk-app-v114 nk-module-builder nk-cbt-builder ${step===2?'is-topics':step===3?'is-questions':'is-banks'}" aria-label="Build timed test"><button class="nk-back-link" onclick="${step===1?"window.QB.nav('tests')":`window.QB.nkCbtSetStep(${step-1})`}">${navIcon('back',18)} ${step===1?'Tests':'Back'}</button>${nkAppPageHead(`TIMED CBT · STEP ${step} OF 3`,titles[step-1],description)}${nkTimedResumeCard('builder')}<div class="nk-module-stepper">${[1,2,3].map(n=>`<span class="${n===step?'is-current':n<step?'is-done':''}"${n===step?' aria-current="step"':` tabindex="0" aria-label="Go to ${['Banks','Topics','Questions'][n-1]}" onclick="window.QB.nkCbtSetStep(${n})" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();this.click()}"`}><i>${n<step?navIcon('check',12):n}</i><b>${['Banks','Topics','Questions'][n-1]}</b></span>`).join('')}</div><section class="nk-module-builder-card">${content}</section>${action}</main>`,'tests');
  }
  openTestBuilder=nkCbtOpenBuilder;
  openMultiSubjectTestBuilder=nkCbtOpenBuilder;
  /* NK_BANK_AWARE_CBT_BUILDER_V1_END */
