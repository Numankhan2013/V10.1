  /* NK_BANK_AWARE_CBT_BUILDER_V1_START */
  let nkCbtDraft=null;

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
    return (record.questions||[]).filter(q=>String(q.chapterId)===String(topic.id)).length;
  }
  function nkCbtVerifiedPyqTopics(){
    return nkCbtSelectedRecords().flatMap(record=>nkModuleTopics(record).filter(topic=>{
      const questions=(record.questions||[]).filter(q=>String(q.chapterId)===String(topic.id));
      return questions.length>0&&questions.every(q=>Array.isArray(q.studyCollections)&&q.studyCollections.includes('pyq'));
    }).map(topic=>({record,topic})));
  }
  function nkCbtSelectVerifiedPyqs(){
    if(!nkCbtDraft)return;
    const topics=nkCbtVerifiedPyqTopics();
    if(!topics.length){
      const message=document.getElementById('nk-cbt-pyq-status');
      if(message)message.textContent='No verified PYQ topics in the selected banks. Your draft is unchanged.';
      return;
    }
    nkCbtDraft.topicKeys=topics.map(({record,topic})=>nkCbtTopicKey(record,topic));
    nkCbtSyncTopics();
    const message=document.getElementById('nk-cbt-pyq-status');
    if(message)message.textContent=`Selected ${topics.length} verified PYQ topics. Add regular topics below if you want a mixed test.`;
  }
  function nkCbtPool(){
    const selected=new Set(nkCbtDraft?.topicKeys||[]),questions=[];
    nkCbtSelectedRecords().forEach(record=>(record.questions||[]).forEach(q=>{
      if(selected.has(nkModuleTopicKey(record.subject,q.chapterId,record.bank)))questions.push(q);
    }));
    return [...new Map(questions.map(q=>[String(q.id),q])).values()];
  }
  function nkCbtFreshDraft(){
    const records=nkCbtRecords();
    return {step:1,bankKeys:records.map(nkCbtRecordKey),topicKeys:records.flatMap(record=>nkModuleTopics(record).map(topic=>nkCbtTopicKey(record,topic))),count:20};
  }
  function nkCbtOpenBuilder(){
    nkCbtDraft=nkCbtFreshDraft();
    navigate('test-builder');
  }
  function nkCbtSetBanks(select){
    if(!nkCbtDraft)return;
    const records=nkCbtRecords();
    nkCbtDraft.bankKeys=select?records.map(nkCbtRecordKey):[];
    nkCbtDraft.topicKeys=select?records.flatMap(record=>nkModuleTopics(record).map(topic=>nkCbtTopicKey(record,topic))):[];
    render();
  }
  function nkCbtToggleBank(index){
    if(!nkCbtDraft)return;
    const record=nkCbtRecords()[index];if(!record)return;
    const key=nkCbtRecordKey(record),banks=new Set(nkCbtDraft.bankKeys),topics=new Set(nkCbtDraft.topicKeys);
    if(banks.has(key)){
      banks.delete(key);
      nkModuleTopics(record).forEach(topic=>topics.delete(nkCbtTopicKey(record,topic)));
    }else{
      banks.add(key);
      nkModuleTopics(record).forEach(topic=>topics.add(nkCbtTopicKey(record,topic)));
    }
    nkCbtDraft.bankKeys=[...banks];nkCbtDraft.topicKeys=[...topics];render();
  }
  function nkCbtSetStep(step){
    if(!nkCbtDraft)return;
    if(step>nkCbtDraft.step){
      if(!nkCbtDraft.bankKeys.length){showToast('Choose at least one question bank.','bad');return;}
      if(nkCbtDraft.step===2&&!nkCbtPool().length){showToast('Choose a topic with questions.','bad');return;}
    }
    nkCbtDraft.step=Math.max(1,Math.min(3,Number(step)));
    if(nkCbtDraft.step===3)nkCbtDraft.count=Math.min(nkCbtDraft.count,nkCbtPool().length);
    render();resetScrollPosition();
  }
  function nkCbtSetTopics(select,recordIndex=null){
    if(!nkCbtDraft)return;
    const selected=new Set(nkCbtDraft.topicKeys),records=recordIndex===null?nkCbtSelectedRecords():[nkCbtRecords()[recordIndex]];
    records.filter(Boolean).forEach(record=>nkModuleTopics(record).forEach(topic=>{
      const key=nkCbtTopicKey(record,topic);if(select)selected.add(key);else selected.delete(key);
    }));
    nkCbtDraft.topicKeys=[...selected];nkCbtSyncTopics();
  }
  function nkCbtToggleGroup(recordIndex){
    const record=nkCbtRecords()[recordIndex];if(!record)return;
    const selected=new Set(nkCbtDraft?.topicKeys||[]),keys=nkModuleTopics(record).map(topic=>nkCbtTopicKey(record,topic));
    nkCbtSetTopics(!keys.every(key=>selected.has(key)),recordIndex);
  }
  function nkCbtToggleTopic(recordIndex,topicIndex){
    if(!nkCbtDraft)return;
    const record=nkCbtRecords()[recordIndex],topic=nkModuleTopics(record)[topicIndex];if(!record||!topic)return;
    const key=nkCbtTopicKey(record,topic),selected=new Set(nkCbtDraft.topicKeys);
    if(selected.has(key))selected.delete(key);else selected.add(key);
    nkCbtDraft.topicKeys=[...selected];nkCbtSyncTopics();
  }
  function nkCbtSyncTopics(){
    const records=nkCbtRecords(),selected=new Set(nkCbtDraft?.topicKeys||[]);
    document.querySelectorAll('.nk-cbt-topic[data-record-index]').forEach(button=>{
      const record=records[Number(button.dataset.recordIndex)],topic=nkModuleTopics(record)[Number(button.dataset.topicIndex)];
      if(!record||!topic)return;
      const picked=selected.has(nkCbtTopicKey(record,topic));
      button.classList.toggle('is-selected',picked);button.setAttribute('aria-pressed',String(picked));
      const check=button.querySelector('.nk-module-check');if(check)check.innerHTML=picked?navIcon('check',16):'';
    });
    document.querySelectorAll('.nk-cbt-topic-group').forEach(group=>{
      const record=records[Number(group.dataset.recordIndex)];if(!record)return;
      const topics=nkModuleTopics(record),count=topics.filter(topic=>selected.has(nkCbtTopicKey(record,topic))).length;
      const status=group.querySelector('.nk-module-group-count'),action=group.querySelector('.nk-module-group-action');
      if(status)status.textContent=`${count} of ${topics.length} selected`;
      if(action)action.textContent=count===topics.length?`Clear ${topics.length}`:`Select ${topics.length}`;
    });
    const pool=nkCbtPool().length,label=`${selected.size} topic${selected.size===1?'':'s'} · ${fmtNum(pool)} question${pool===1?'':'s'}`;
    for(const id of ['nk-cbt-selected-count','nk-cbt-footer-count']){
      const node=document.getElementById(id);if(node)node.textContent=label;
    }
    const next=document.getElementById('nk-cbt-topics-continue');if(next)next.disabled=!pool;
  }
  function nkCbtFilterTopics(value){
    const query=String(value||'').trim().toLocaleLowerCase();let visible=0;
    document.querySelectorAll('.nk-cbt-topic-group').forEach(group=>{
      const label=group.querySelector('.nk-module-group-title')?.textContent.toLocaleLowerCase()||'';let groupVisible=0;
      group.querySelectorAll('.nk-cbt-topic').forEach(button=>{
        const match=!query||label.includes(query)||button.querySelector('strong')?.textContent.toLocaleLowerCase().includes(query);
        button.hidden=!match;if(match)groupVisible++;
      });
      group.hidden=!groupVisible;visible+=groupVisible;
    });
    const status=document.getElementById('nk-cbt-search-status'),empty=document.getElementById('nk-cbt-search-empty');
    if(status)status.textContent=query?`${visible} matching topic${visible===1?'':'s'}`:'';
    if(empty)empty.hidden=visible>0;
  }
  function nkCbtSetCount(value){
    if(!nkCbtDraft)return;
    if(value==='')return;
    const number=Number(value);if(!Number.isFinite(number))return;
    const pool=nkCbtPool().length;
    nkCbtDraft.count=Math.max(1,Math.min(pool,Math.floor(number)));
    const actual=nkCbtDraft.count;
    const input=document.getElementById('nk-cbt-custom-count');if(input)input.value=String(nkCbtDraft.count);
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
    startSession(chosen,'exam',nkCbtTitle(chosen.map(id=>byId.get(id))));
    if(state.activeSession){state.activeSession.originRoute='tests';saveState();}
    nkCbtDraft=null;
  }
  function nkCbtBanksMarkup(){
    const selected=new Set(nkCbtDraft.bankKeys),records=nkCbtRecords();
    return `<div class="nk-cbt-bank-intro"><strong>Choose the sources for this test</strong><span>${selected.size} of ${records.length} banks selected</span></div><div class="nk-module-select-tools nk-cbt-bank-tools"><button type="button" onclick="window.QB.nkCbtSetBanks(true)">Select all</button><button type="button" onclick="window.QB.nkCbtSetBanks(false)">Clear all</button></div><div class="nk-module-choice-grid">${records.map((record,index)=>{const picked=selected.has(nkCbtRecordKey(record)),meta=nkAppSubjectMeta(record.subject);return `<button type="button" class="nk-module-subject is-${meta.key} ${picked?'is-selected':''}" aria-pressed="${picked}" onclick="window.QB.nkCbtToggleBank(${index})"><span>${nkAppSubjectIcon(record.subject,23)}</span><strong>${esc(record.subject)}</strong><small>${esc(record.bank)} · ${fmtNum(record.questions.length)} questions · ${fmtNum(nkModuleTopics(record).length)} topics</small><i>${picked?navIcon('check',15):''}</i></button>`;}).join('')}</div>`;
  }
  function nkCbtTopicsMarkup(){
    const records=nkCbtRecords(),selected=new Set(nkCbtDraft.topicKeys),active=nkCbtSelectedRecords();
    const total=active.reduce((sum,record)=>sum+nkModuleTopics(record).length,0),pool=nkCbtPool().length;
    const pyqTopics=nkCbtVerifiedPyqTopics(),pyqQuestions=pyqTopics.reduce((sum,{record,topic})=>sum+nkCbtTopicCount(record,topic),0);
    const groups=records.map((record,recordIndex)=>{
      if(!nkCbtDraft.bankKeys.includes(nkCbtRecordKey(record)))return'';
      const topics=nkModuleTopics(record),count=topics.filter(topic=>selected.has(nkCbtTopicKey(record,topic))).length;
      return `<section class="nk-module-topic-group nk-cbt-topic-group" data-record-index="${recordIndex}"><header><span class="is-${nkAppSubjectMeta(record.subject).key}">${nkAppSubjectIcon(record.subject,20)}</span><div><strong class="nk-module-group-title">${esc(record.subject)} · ${esc(record.bank)}</strong><small class="nk-module-group-count">${count} of ${topics.length} selected</small></div><button type="button" class="nk-module-group-action" onclick="window.QB.nkCbtToggleGroup(${recordIndex})">${count===topics.length?`Clear ${topics.length}`:`Select ${topics.length}`}</button></header><div class="nk-module-topic-list">${topics.map((topic,topicIndex)=>{const picked=selected.has(nkCbtTopicKey(record,topic));return `<button type="button" class="nk-module-topic nk-cbt-topic ${picked?'is-selected':''}" data-record-index="${recordIndex}" data-topic-index="${topicIndex}" aria-pressed="${picked}" onclick="window.QB.nkCbtToggleTopic(${recordIndex},${topicIndex})"><span class="nk-module-topic-copy"><strong>${esc(topic.title)}</strong><small>${fmtNum(nkCbtTopicCount(record,topic))} questions${nkModuleTopicHasCollection(record,topic.id,'pyq')?' · PYQs':''}</small></span><span class="nk-module-check" aria-hidden="true">${picked?navIcon('check',16):''}</span></button>`;}).join('')}</div></section>`;
    }).join('');
    return `<div class="nk-module-topic-intro"><strong>${fmtNum(total)} topics in ${active.length} selected bank${active.length===1?'':'s'}</strong><span id="nk-cbt-selected-count">${selected.size} topics · ${fmtNum(pool)} questions</span></div><div class="nk-cbt-pyq-action"><button type="button" onclick="window.QB.nkCbtSelectVerifiedPyqs()">Only verified PYQ topics</button><span>${fmtNum(pyqTopics.length)} eligible topics · ${fmtNum(pyqQuestions)} questions</span></div><p id="nk-cbt-pyq-status" class="nk-cbt-pyq-status" role="status">${pyqTopics.length?'Replaces selected topics. You can add regular topics afterward.':'No verified PYQ topics in the selected banks. Your draft is unchanged.'}</p><label class="nk-module-topic-search"><span>Search topics</span><input type="search" placeholder="Search by chapter or topic name" autocomplete="off" oninput="window.QB.nkCbtFilterTopics(this.value)"></label><div class="nk-module-select-tools"><button type="button" onclick="window.QB.nkCbtSetTopics(true)">Select all</button><button type="button" onclick="window.QB.nkCbtSetTopics(false)">Clear all</button></div><div id="nk-cbt-search-status" class="nk-module-search-status" role="status"></div><div class="nk-module-topic-groups">${groups}</div><div id="nk-cbt-search-empty" class="nk-module-search-empty" hidden>No topics match your search.</div>`;
  }
  function nkCbtQuestionsMarkup(){
    const pool=nkCbtPool().length,actual=Math.min(nkCbtDraft.count,pool),records=nkCbtSelectedRecords();
    const banksBySubject=new Map();records.forEach(record=>{
      const list=banksBySubject.get(record.subject)||[];list.push(record.bank);banksBySubject.set(record.subject,list);
    });
    const bankSummary=[...banksBySubject].map(([subject,banks])=>`${esc(subject)} · ${banks.map(esc).join(' + ')}`).join('<br>');
    const presets=[10,20,50,100].filter(number=>number<=pool);if(!presets.length)presets.push(pool);
    return `<div class="nk-cbt-summary"><div><small>Question banks</small><strong>${bankSummary}</strong></div><div><small>Available pool</small><strong>${fmtNum(pool)} questions</strong><p>${nkCbtDraft.topicKeys.length} selected topics</p></div></div><div class="nk-cbt-count"><h2>How many questions?</h2><p>Questions are randomly drawn from the topics you selected.</p><div class="nk-cbt-count-grid">${presets.map(number=>`<button type="button" class="nk-cbt-count-preset ${nkCbtDraft.count===number?'is-selected':''}" data-count="${number}" onclick="window.QB.nkCbtSetCount(${number})">${number}</button>`).join('')}</div><label for="nk-cbt-custom-count">Custom amount</label><input id="nk-cbt-custom-count" type="number" inputmode="numeric" min="1" max="${pool}" value="${nkCbtDraft.count}" oninput="window.QB.nkCbtSetCount(this.value)"></div><div class="nk-cbt-timing"><span>${navIcon('clock',20)}</span><div><strong id="nk-cbt-count-result">${fmtNum(actual)} questions · ${fmtNum(actual)} minutes total</strong><p>One minute per question. Answers and explanations appear after submission.</p></div></div>`;
  }
  function nkCbtBuilderPage(){
    if(!nkCbtDraft)nkCbtDraft=nkCbtFreshDraft();
    const step=nkCbtDraft.step,titles=['Choose question banks','Choose topics','Set question count'];
    const content=step===1?nkCbtBanksMarkup():step===2?nkCbtTopicsMarkup():nkCbtQuestionsMarkup();
    const action=step===2?`<div class="nk-module-builder-actions nk-module-topic-actions nk-cbt-actions"><span id="nk-cbt-footer-count">${nkCbtDraft.topicKeys.length} topics · ${fmtNum(nkCbtPool().length)} questions</span><button id="nk-cbt-topics-continue" class="is-primary" ${nkCbtPool().length?'':'disabled'} onclick="window.QB.nkCbtSetStep(3)">Continue to questions</button></div>`:step===1?`<div class="nk-cbt-main-actions"><button class="is-primary" ${nkCbtDraft.bankKeys.length?'':'disabled'} onclick="window.QB.nkCbtSetStep(2)">Continue to topics</button></div>`:`<div class="nk-cbt-main-actions"><button class="is-primary" onclick="window.QB.nkCbtStart()">Start timed CBT</button></div>`;
    const description=step===1?'Choose the question banks you want to study.':step===2?'Search or scroll, then tap the topics you want to test.':'Set the number of questions. Your time limit updates with it.';
    return shell(`<main class="nk-app-v114 nk-module-builder nk-cbt-builder ${step===2?'is-topics':step===3?'is-questions':'is-banks'}" aria-label="Build timed test"><button class="nk-back-link" onclick="${step===1?"window.QB.nav('tests')":`window.QB.nkCbtSetStep(${step-1})`}">${navIcon('back',18)} ${step===1?'Tests':'Back'}</button>${nkAppPageHead(`TIMED CBT · STEP ${step} OF 3`,titles[step-1],description)}<div class="nk-module-stepper">${[1,2,3].map(n=>`<span class="${n===step?'is-current':n<step?'is-done':''}"><i>${n<step?navIcon('check',12):n}</i><b>${['Banks','Topics','Questions'][n-1]}</b></span>`).join('')}</div><section class="nk-module-builder-card">${content}</section>${action}</main>`,'tests');
  }
  openTestBuilder=nkCbtOpenBuilder;
  openMultiSubjectTestBuilder=nkCbtOpenBuilder;
  /* NK_BANK_AWARE_CBT_BUILDER_V1_END */
