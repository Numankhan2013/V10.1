  /* NK_DURABLE_PERSISTENCE_V2_START
   * One state writer for the generated application. The pending journal and
   * last-known-good copy make interrupted/corrupt primary writes recoverable.
   */
  const NK_STATE_SCHEMA_VERSION=2;
  const NK_STATE_LKG_KEY='qbank_state_lkg_v2';
  const NK_STATE_PENDING_KEY='qbank_state_pending_v2';
  const NK_PRACTICE_CHECKPOINT_VERSION=1;
  const NK_PRACTICE_LIFECYCLES=new Set(['active','paused','suspended','submitted','completed','discarded']);
  const NK_PRACTICE_TERMINAL=new Set(['submitted','completed','discarded']);
  let nkStorageBootNotice='';
  let nkStorageLastError='';

  function nkStorageAdapter(){return window.__NK_STORAGE_ADAPTER||localStorage;}
  function nkStateClone(value){return JSON.parse(JSON.stringify(value));}
  function nkStateObject(value){return Boolean(value)&&typeof value==='object'&&!Array.isArray(value);}
  function nkStateRevision(value){const n=Number(value?.stateRevision||0);return Number.isSafeInteger(n)&&n>=0?n:0;}
  function nkCheckpointMembership(ids){let h=2166136261;for(const char of (ids||[]).map(String).join('\u001f')){h^=char.charCodeAt(0);h=Math.imul(h,16777619);}return (h>>>0).toString(36);}
  function nkNormalPracticeSession(s){
    if(!s||s.mode!=='practice'||s.studyModuleId)return false;
    const origin=[s.originRoute,s.context,s.title].filter(Boolean).join(' ').toLowerCase();
    return !/(fsrs|spaced|review|wrong|bookmark)/.test(origin);
  }
  // Due-review learning rounds (review_learning_queue.js): the queue of cards waiting
  // for another round and each question's earlier rounds. Optional, keyed by
  // question ID inside the session's own membership; a checkpoint without them
  // is an ordinary one, so older payloads load unchanged.
  function nkCheckpointLearning(raw,ids){
    const member=new Set(ids),out={},queue={},rounds={};
    if(nkStateObject(raw?.learningQueue))Object.entries(raw.learningQueue).forEach(([id,entry])=>{const due=Number(entry?.due);if(member.has(String(id))&&Number.isFinite(due)&&due>0)queue[String(id)]={due,round:Math.max(1,Math.trunc(Number(entry.round)||1))};});
    if(nkStateObject(raw?.roundHistory))Object.entries(raw.roundHistory).forEach(([id,list])=>{if(!member.has(String(id))||!Array.isArray(list))return;const clean=list.filter(nkStateObject).slice(0,50).map((r,i)=>({round:i+1,answer:r.answer==null?null:Number(r.answer),submitted:Boolean(r.submitted),timeMs:Math.max(0,Number(r.timeMs)||0),correct:typeof r.correct==='boolean'?r.correct:null,rating:[1,2,3,4].includes(Number(r.rating))?Number(r.rating):null,attemptId:r.attemptId==null?null:String(r.attemptId),reopenedAt:Math.max(0,Number(r.reopenedAt)||0)}));if(clean.length)rounds[String(id)]=clean;});
    if(Object.keys(queue).length)out.learningQueue=queue;
    if(Object.keys(rounds).length)out.roundHistory=rounds;
    // The live round 2+: its round number and only its cards (member ids, no repeats).
    const pass=nkStateObject(raw?.roundPass)?raw.roundPass:null,passRound=Math.trunc(Number(pass?.round));
    const passIds=pass&&Array.isArray(pass.ids)?[...new Set(pass.ids.map(String))].filter(id=>member.has(id)):[];
    if(passRound>=2&&passRound<=99&&passIds.length)out.roundPass={round:passRound,ids:passIds};
    const back=Number(raw?.learningReturnIndex);if(Number.isInteger(back)&&back>=0&&back<ids.length)out.learningReturnIndex=back;
    return out;
  }
  function nkCheckpointRounds(roundHistory,id){return Array.isArray(roundHistory?.[id])?roundHistory[id].length:0;}
  function nkNormalizeCheckpoint(raw){
    if(!nkStateObject(raw)||Number(raw.version)!==NK_PRACTICE_CHECKPOINT_VERSION||!raw.sessionId)return null;
    const ids=[...new Set((Array.isArray(raw.sessionQuestionIds)?raw.sessionQuestionIds:[]).map(String).filter(Boolean))];
    if(!ids.length||!NK_PRACTICE_LIFECYCLES.has(String(raw.lifecycle||'')))return null;
    const position=nkStateObject(raw.position)?raw.position:{};
    const base={...raw};delete base.learningQueue;delete base.roundHistory;delete base.learningReturnIndex;delete base.roundPass;
    return {...base,...nkCheckpointLearning(raw,ids),version:NK_PRACTICE_CHECKPOINT_VERSION,sessionId:String(raw.sessionId),sessionQuestionIds:ids,
      membershipHash:nkCheckpointMembership(ids),context:nkStateObject(raw.context)?raw.context:{},
      position:{index:Math.max(0,Math.min(ids.length-1,Number(position.index)||0)),currentQuestionId:String(position.currentQuestionId||ids[Math.max(0,Number(position.index)||0)]||'')},
      answers:nkStateObject(raw.answers)?raw.answers:{},submitted:nkStateObject(raw.submitted)?raw.submitted:{},
      questionTimes:nkStateObject(raw.questionTimes)?raw.questionTimes:{},pendingFsrsRatings:nkStateObject(raw.pendingFsrsRatings)?raw.pendingFsrsRatings:{},
      questionUpdates:nkStateObject(raw.questionUpdates)?raw.questionUpdates:{},lifecycle:String(raw.lifecycle),updatedAt:Math.max(1,Number(raw.updatedAt||raw.createdAt||Date.now()))};
  }
  function nkNormalizePracticeCheckpoints(rawList,legacy){
    const source=Array.isArray(rawList)?[...rawList]:[];
    // The legacy alias may have been written by an older client after its
    // collection copy. Compare revisions even when the IDs already match.
    if(legacy)source.push(legacy);
    const byId=new Map();for(const raw of source){const item=nkNormalizeCheckpoint(raw);if(!item)continue;const old=byId.get(item.sessionId);if(!old||Number(item.updatedAt||0)>=Number(old.updatedAt||0))byId.set(item.sessionId,item);}
    // Terminal records are sync tombstones. Dropping an old one would allow a
    // delayed remote paused copy to reopen a completed or discarded session.
    return [...byId.values()].sort((a,b)=>Number(a.createdAt||a.updatedAt||0)-Number(b.createdAt||b.updatedAt||0));
  }
  function nkLatestPracticeCheckpoint(list){let latest=null;for(const item of list||[]){if(!latest||Number(item.updatedAt||0)>=Number(latest.updatedAt||0))latest=item;}return latest;}
  function nkValidateState(value){
    if(!nkStateObject(value))throw new Error('state root is not an object');
    if(value.stateSchemaVersion!=null&&(!Number.isInteger(Number(value.stateSchemaVersion))||Number(value.stateSchemaVersion)>NK_STATE_SCHEMA_VERSION||Number(value.stateSchemaVersion)<1))throw new Error('unsupported state schema');
    if(value.stateRevision!=null&&(!Number.isSafeInteger(Number(value.stateRevision))||Number(value.stateRevision)<0))throw new Error('invalid state revision');
    if(value.attempts!=null&&!nkStateObject(value.attempts))throw new Error('attempts is not an object');
    if(value.fsrsRatingRevisions!=null&&(!nkStateObject(value.fsrsRatingRevisions)||Object.values(value.fsrsRatingRevisions).some(list=>!Array.isArray(list))))throw new Error('FSRS rating revisions are invalid');
    if(value.bookmarks!=null&&!nkStateObject(value.bookmarks))throw new Error('bookmarks is not an object');
    if(value.questionNotes!=null&&!nkStateObject(value.questionNotes))throw new Error('question notes is not an object');
    if(value.reviews!=null&&!nkStateObject(value.reviews))throw new Error('reviews is not an object');
    if(value.tests!=null&&!Array.isArray(value.tests))throw new Error('tests is not an array');
    if(value.studyModules!=null&&!Array.isArray(value.studyModules))throw new Error('studyModules is not an array');
    if(value.savedMocks!=null&&!Array.isArray(value.savedMocks))throw new Error('savedMocks is not an array');
    if(value.normalPracticeCheckpoint!=null&&!nkNormalizeCheckpoint(value.normalPracticeCheckpoint))throw new Error('normal Practice checkpoint is invalid');
    if(value.normalPracticeCheckpoints!=null&&(!Array.isArray(value.normalPracticeCheckpoints)||value.normalPracticeCheckpoints.some(item=>!nkNormalizeCheckpoint(item))))throw new Error('normal Practice checkpoints are invalid');
    return true;
  }
  function nkNormalizeState(value){
    nkValidateState(value);
    const out={...defaultState(),...value,attempts:value.attempts||{},bookmarks:value.bookmarks||{},questionNotes:value.questionNotes||{},reviews:value.reviews||{},tests:Array.isArray(value.tests)?value.tests:[]};
    out.studyModules=Array.isArray(value.studyModules)?value.studyModules:[];
    out.savedMocks=Array.isArray(value.savedMocks)?value.savedMocks:[];
    out.stateSchemaVersion=NK_STATE_SCHEMA_VERSION;out.stateRevision=nkStateRevision(value);
    out.normalPracticeCheckpoints=nkNormalizePracticeCheckpoints(value.normalPracticeCheckpoints,value.normalPracticeCheckpoint);
    out.normalPracticeCheckpoint=nkLatestPracticeCheckpoint(out.normalPracticeCheckpoints);
    return out;
  }
  function nkReadStateCandidate(key){
    const raw=nkStorageAdapter().getItem(key);if(!raw)return null;
    try{const value=JSON.parse(raw);return {key,value:nkNormalizeState(value),revision:nkStateRevision(value)};}catch(error){return {key,error};}
  }
  function nkDurableLoadState(){
    const primary=nkReadStateCandidate(LS_KEY),pending=nkReadStateCandidate(NK_STATE_PENDING_KEY),lkg=nkReadStateCandidate(NK_STATE_LKG_KEY);
    const valid=[primary,pending,lkg].filter(item=>item&&!item.error).sort((a,b)=>b.revision-a.revision||([LS_KEY,NK_STATE_PENDING_KEY,NK_STATE_LKG_KEY].indexOf(a.key)-[LS_KEY,NK_STATE_PENDING_KEY,NK_STATE_LKG_KEY].indexOf(b.key)));
    if(valid.length){
      const chosen=valid[0];
      if(!primary||primary.error||chosen.key!==LS_KEY)nkStorageBootNotice=primary?.error?'Recovered progress from the last valid snapshot because the main copy was damaged.':'Recovered an interrupted progress save.';
      return chosen.value;
    }
    if(primary?.error||pending?.error||lkg?.error){
      // Keep the unreadable bytes before any later save overwrites every copy with a fresh state.
      try{const store=nkStorageAdapter(),raw=store.getItem(LS_KEY)||store.getItem(NK_STATE_LKG_KEY)||store.getItem(NK_STATE_PENDING_KEY);if(raw&&!store.getItem('qbank_state_unreadable_v1'))store.setItem('qbank_state_unreadable_v1',raw);}catch(_){}
      nkStorageBootNotice='Saved progress could not be read. No valid recovery snapshot was available; a raw copy was kept. Retry before studying.';
    }
    return nkNormalizeState(defaultState());
  }
  function nkStorageError(message,error){
    nkStorageLastError=`${message}${error?.message?`: ${error.message}`:''}`;
    try{
      let box=document.getElementById('nk-storage-error');
      if(!box){box=document.createElement('div');box.id='nk-storage-error';box.className='nk-storage-error';box.setAttribute('role','alert');box.innerHTML='<span></span><button type="button" onclick="window.QB.nkRetryPersistence()">Retry save</button>';document.body.appendChild(box);}
      box.querySelector('span').textContent=nkStorageLastError;
    }catch(_){}
  }
  function nkStorageClearError(){nkStorageLastError='';try{document.getElementById('nk-storage-error')?.remove();}catch(_){}}
  function nkCheckpointQuestionUpdate(previous,id,next,now){
    const rounds=nkCheckpointRounds(next.roundHistory,id),fields=[next.answers[id]??null,Boolean(next.submitted[id]),Number(next.questionTimes[id]||0),next.pendingFsrsRatings[id]||null];
    // A reopened learning round is a new edit of that question (older signatures stay as they were).
    const before=previous?.questionUpdates?.[id]||{},signature=JSON.stringify(rounds?[...fields,rounds]:fields);
    return before.signature===signature?before:{revision:Math.max(1,Number(before.revision||0)+1),updatedAt:now,signature};
  }
  function nkCheckpointFromSession(s,previous,lifecycle){
    const prior=previous&&String(previous.sessionId)===String(s.id)?previous:null;
    const ids=prior?.sessionQuestionIds?.length?[...prior.sessionQuestionIds]:[...new Set((s.sessionQuestionIds?.length?s.sessionQuestionIds:s.questionIds||[]).map(String))];
    const current=String(s.questionIds?.[Number(s.index)||0]||ids[Math.max(0,Number(s.pausedIndex)||0)]||'');
    const learning=nkCheckpointLearning(s,ids);
    const now=Date.now(),next={answers:{...(s.answers||{})},submitted:{...(s.submitted||{})},questionTimes:{...(s.questionTimes||{})},pendingFsrsRatings:{...(s.pendingRating||{})},roundHistory:learning.roundHistory};
    const questionUpdates={};ids.forEach(id=>questionUpdates[id]=nkCheckpointQuestionUpdate(prior,id,next,now));
    return {version:NK_PRACTICE_CHECKPOINT_VERSION,sessionId:String(s.id),sessionQuestionIds:ids,membershipHash:nkCheckpointMembership(ids),
      context:{...(s.practiceContext||{}),...(s.originRoute&&s.originRoute!=='topics'?{originRoute:String(s.originRoute)}:{}),subject:String(s.practiceContext?.subject||''),bank:String(s.practiceContext?.bank||''),topicId:String(s.practiceContext?.topicId||''),title:String(s.practiceContext?.title||s.title||'Practice')},
      position:{index:Math.max(0,Math.min(ids.length-1,Number(s.index)||0)),currentQuestionId:current},answers:next.answers,submitted:next.submitted,
      startedAt:Number(s.startedAt||now),lastTick:Number(s.lastTick||now),elapsedMs:Number(s.elapsedMs||0),questionEnteredAt:Number(s.questionEnteredAt||now),
      questionTimes:next.questionTimes,pendingFsrsRatings:next.pendingFsrsRatings,questionUpdates,...learning,lifecycle:lifecycle||String(s.lifecycle||'active'),
      createdAt:Number(prior?.createdAt||s.startedAt||now),updatedAt:now,terminalAt:NK_PRACTICE_TERMINAL.has(lifecycle)?now:(prior?.terminalAt||null)};
  }
  function nkMirrorNormalPracticeCheckpoint(target){
    const checkpoints=nkNormalizePracticeCheckpoints(target.normalPracticeCheckpoints,target.normalPracticeCheckpoint),session=target.activeSession;
    if(nkNormalPracticeSession(session)){
      const current=checkpoints.find(item=>String(item.sessionId)===String(session.id))||null;
      if(current&&NK_PRACTICE_TERMINAL.has(current.lifecycle)){target.activeSession=null;target.normalPracticeCheckpoints=checkpoints;target.normalPracticeCheckpoint=nkLatestPracticeCheckpoint(checkpoints);return target.normalPracticeCheckpoint;}
      if(current&&(session.lifecycle==='paused'||session.lifecycle==='suspended')){target.normalPracticeCheckpoints=checkpoints;target.normalPracticeCheckpoint=nkLatestPracticeCheckpoint(checkpoints);return current;}
      const next=nkCheckpointFromSession(session,current,String(session.lifecycle||'active')),index=checkpoints.findIndex(item=>String(item.sessionId)===String(session.id));
      // An unchanged checkpoint keeps its time, so a save that changes nothing stays a no-op.
      if(current&&JSON.stringify({...next,updatedAt:0})===JSON.stringify({...current,updatedAt:0}))next.updatedAt=current.updatedAt;
      next.updatedAt=Math.max(Number(next.updatedAt||0),...checkpoints.filter(item=>String(item.sessionId)!==String(session.id)).map(item=>Number(item.updatedAt||0)+1));
      if(index<0)checkpoints.push(next);else checkpoints[index]=next;
      target.normalPracticeCheckpoints=checkpoints;target.normalPracticeCheckpoint=nkLatestPracticeCheckpoint(checkpoints);return next;
    }
    if(session){for(let index=0;index<checkpoints.length;index++){const item=checkpoints[index];if(item.lifecycle==='active')checkpoints[index]={...item,lifecycle:'suspended',updatedAt:Date.now()};}}
    target.normalPracticeCheckpoints=checkpoints;target.normalPracticeCheckpoint=nkLatestPracticeCheckpoint(checkpoints);return target.normalPracticeCheckpoint;
  }
  function nkPrepareTimedSession(target){
    const s=target.activeSession;if(!s||s.mode!=='exam')return;
    if(!Number(s.deadlineAt))s.deadlineAt=Number(s.startedAt||Date.now())+(typeof nkExamTotalSeconds==='function'?nkExamTotalSeconds(s):Math.max(1,(s.questionIds||[]).length)*60)*1000;
    s.updatedAt=Date.now();
  }
  // Another tab or window saved progress: this copy is stale, so it stops writing
  // instead of overwriting the newer answers, and offers a reload.
  let nkOtherTabNewer=false;
  function nkStorageStaleTab(){
    try{
      let box=document.getElementById('nk-storage-error');
      if(!box){box=document.createElement('div');box.id='nk-storage-error';box.className='nk-storage-error';box.setAttribute('role','alert');document.body.appendChild(box);}
      box.innerHTML='<span>Progress was updated in another tab or window. Reload to continue here without overwriting it.</span><button type="button" onclick="location.reload()">Reload</button>';
    }catch(_){}
  }
  // Ask the browser not to evict progress under storage pressure (Safari tabs especially).
  try{navigator.storage?.persisted?.().then(done=>{if(!done)navigator.storage.persist?.();}).catch(()=>{});}catch(_){}
  try{window.addEventListener('storage',event=>{if(event.key===LS_KEY&&event.newValue){nkOtherTabNewer=true;nkStorageStaleTab();}});}catch(_){}
  // Progress outgrew the localStorage mirror, so this boot started from an empty
  // state; NKStore has now read the real progress from IndexedDB. Adopt it in place.
  try{window.addEventListener('nk-store-recovered',()=>{
    nkStorageBootNotice='';state=nkDurableLoadState();
    if(typeof nkNormalizeStudyModules==='function')nkNormalizeStudyModules();
    nkStateChanged();if(typeof nkReliabilityInit==='function')nkReliabilityInit(true);
    if(!state.fsrsMigratedAt&&typeof nkFsrsInit==='function')try{nkFsrsInit();}catch(_){}
    render();
  });}catch(_){}
  function nkDurablePersist(candidate,reason='state save'){
    if(nkOtherTabNewer){nkStorageStaleTab();return false;}
    const store=nkStorageAdapter(),previousPrimary=store.getItem(LS_KEY);
    const previousLkg=store.getItem(NK_STATE_LKG_KEY);
    try{
      nkMirrorNormalPracticeCheckpoint(candidate);nkPrepareTimedSession(candidate);
      // Normalize makes a new root object and never mutates its input. Avoid a
      // second full-state clone and the checkpoint normalization done by a
      // redundant primary read on every question tap.
      const next=nkNormalizeState(candidate);
      let storedRevision=0;
      if(previousPrimary){try{storedRevision=nkStateRevision(JSON.parse(previousPrimary));}catch(_){}}
      // A save that changes nothing (a tab closed or hidden without studying) writes
      // nothing, so other open tabs are not told their copy is stale.
      if(previousPrimary&&nkStateRevision(candidate)===storedRevision){next.stateRevision=storedRevision;if(JSON.stringify(next)===previousPrimary){nkStorageClearError();return true;}}
      next.stateRevision=Math.max(nkStateRevision(candidate),storedRevision)+1;
      const raw=JSON.stringify(next);
      store.setItem(NK_STATE_PENDING_KEY,raw);store.setItem(LS_KEY,raw);
      const check=store.getItem(LS_KEY);if(check!==raw)throw new Error('primary verification failed');
      store.setItem(NK_STATE_LKG_KEY,raw);store.removeItem(NK_STATE_PENDING_KEY);
      candidate.stateSchemaVersion=next.stateSchemaVersion;candidate.stateRevision=next.stateRevision;candidate.normalPracticeCheckpoints=next.normalPracticeCheckpoints;candidate.normalPracticeCheckpoint=next.normalPracticeCheckpoint;
      nkStorageClearError();return true;
    }catch(error){
      try{store.removeItem(NK_STATE_PENDING_KEY);}catch(_){}
      try{if(previousPrimary==null)store.removeItem(LS_KEY);else store.setItem(LS_KEY,previousPrimary);}catch(_){}
      try{if(previousLkg==null)store.removeItem(NK_STATE_LKG_KEY);else store.setItem(NK_STATE_LKG_KEY,previousLkg);}catch(_){}
      nkStorageError(`Progress was not saved during ${reason}. Nothing destructive was completed`,error);return false;
    }
  }
  function nkDurablePersistExternal(candidate){
    const live=window.QB?.getState?.();if(live&&candidate&&candidate!==live)Object.assign(live,candidate);
    return window.QB?.saveState?window.QB.saveState():nkDurablePersist(candidate||live,'compatibility save');
  }
  function nkRetryPersistence(){const ok=saveState();if(ok){nkStorageClearError();if(typeof nkScheduleCloudSync==='function')nkScheduleCloudSync();}return ok;}
  function nkFlushLifecycleState(){
    // Only the tab showing the session charges the time; another tab on Home leaves it alone.
    const live=state?.activeSession,s=typeof route==='undefined'||route?.page===live?.mode?live:null;
    if(s?.mode==='practice'&&s.lifecycle!=='paused'&&s.lifecycle!=='suspended'&&typeof savePracticeElapsed==='function')savePracticeElapsed();
    else if(s?.mode==='exam'&&typeof saveExamElapsed==='function')saveExamElapsed();
    const ok=saveState();if(typeof nkCaptureCloudChanges==='function')nkCaptureCloudChanges();return ok;
  }
  window.NKQBankStorage={persistExternalState:nkDurablePersistExternal,getLastError:()=>nkStorageLastError};
  /* NK_DURABLE_PERSISTENCE_V2_END */
