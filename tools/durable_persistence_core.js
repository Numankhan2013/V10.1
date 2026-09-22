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
    const origin=String(s.originRoute||s.context||s.title||'').toLowerCase();
    return !/(fsrs|spaced|review|wrong|bookmark)/.test(origin);
  }
  function nkNormalizeCheckpoint(raw){
    if(!nkStateObject(raw)||Number(raw.version)!==NK_PRACTICE_CHECKPOINT_VERSION||!raw.sessionId)return null;
    const ids=[...new Set((Array.isArray(raw.sessionQuestionIds)?raw.sessionQuestionIds:[]).map(String).filter(Boolean))];
    if(!ids.length||!NK_PRACTICE_LIFECYCLES.has(String(raw.lifecycle||'')))return null;
    const position=nkStateObject(raw.position)?raw.position:{};
    return {...raw,version:NK_PRACTICE_CHECKPOINT_VERSION,sessionId:String(raw.sessionId),sessionQuestionIds:ids,
      membershipHash:nkCheckpointMembership(ids),context:nkStateObject(raw.context)?raw.context:{},
      position:{index:Math.max(0,Math.min(ids.length-1,Number(position.index)||0)),currentQuestionId:String(position.currentQuestionId||ids[Math.max(0,Number(position.index)||0)]||'')},
      answers:nkStateObject(raw.answers)?raw.answers:{},submitted:nkStateObject(raw.submitted)?raw.submitted:{},
      questionTimes:nkStateObject(raw.questionTimes)?raw.questionTimes:{},pendingFsrsRatings:nkStateObject(raw.pendingFsrsRatings)?raw.pendingFsrsRatings:{},
      questionUpdates:nkStateObject(raw.questionUpdates)?raw.questionUpdates:{},lifecycle:String(raw.lifecycle),updatedAt:Math.max(1,Number(raw.updatedAt||raw.createdAt||Date.now()))};
  }
  function nkValidateState(value){
    if(!nkStateObject(value))throw new Error('state root is not an object');
    if(value.stateSchemaVersion!=null&&(!Number.isInteger(Number(value.stateSchemaVersion))||Number(value.stateSchemaVersion)>NK_STATE_SCHEMA_VERSION||Number(value.stateSchemaVersion)<1))throw new Error('unsupported state schema');
    if(value.stateRevision!=null&&(!Number.isSafeInteger(Number(value.stateRevision))||Number(value.stateRevision)<0))throw new Error('invalid state revision');
    if(value.attempts!=null&&!nkStateObject(value.attempts))throw new Error('attempts is not an object');
    if(value.bookmarks!=null&&!nkStateObject(value.bookmarks))throw new Error('bookmarks is not an object');
    if(value.reviews!=null&&!nkStateObject(value.reviews))throw new Error('reviews is not an object');
    if(value.tests!=null&&!Array.isArray(value.tests))throw new Error('tests is not an array');
    if(value.studyModules!=null&&!Array.isArray(value.studyModules))throw new Error('studyModules is not an array');
    if(value.normalPracticeCheckpoint!=null&&!nkNormalizeCheckpoint(value.normalPracticeCheckpoint))throw new Error('normal Practice checkpoint is invalid');
    return true;
  }
  function nkNormalizeState(value){
    nkValidateState(value);
    const out={...defaultState(),...value,attempts:value.attempts||{},bookmarks:value.bookmarks||{},reviews:value.reviews||{},tests:Array.isArray(value.tests)?value.tests:[]};
    out.studyModules=Array.isArray(value.studyModules)?value.studyModules:[];
    out.stateSchemaVersion=NK_STATE_SCHEMA_VERSION;out.stateRevision=nkStateRevision(value);
    out.normalPracticeCheckpoint=value.normalPracticeCheckpoint?nkNormalizeCheckpoint(value.normalPracticeCheckpoint):null;
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
    if(primary?.error||pending?.error||lkg?.error)nkStorageBootNotice='Saved progress could not be read. No valid recovery snapshot was available; retry before studying.';
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
    const before=previous?.questionUpdates?.[id]||{},signature=JSON.stringify([next.answers[id]??null,Boolean(next.submitted[id]),Number(next.questionTimes[id]||0),next.pendingFsrsRatings[id]||null]);
    return before.signature===signature?before:{revision:Math.max(1,Number(before.revision||0)+1),updatedAt:now,signature};
  }
  function nkCheckpointFromSession(s,previous,lifecycle){
    const prior=previous&&String(previous.sessionId)===String(s.id)?previous:null;
    const ids=prior?.sessionQuestionIds?.length?[...prior.sessionQuestionIds]:[...new Set((s.sessionQuestionIds?.length?s.sessionQuestionIds:s.questionIds||[]).map(String))];
    const current=String(s.questionIds?.[Number(s.index)||0]||ids[Math.max(0,Number(s.pausedIndex)||0)]||'');
    const now=Date.now(),next={answers:{...(s.answers||{})},submitted:{...(s.submitted||{})},questionTimes:{...(s.questionTimes||{})},pendingFsrsRatings:{...(s.pendingRating||{})}};
    const questionUpdates={};ids.forEach(id=>questionUpdates[id]=nkCheckpointQuestionUpdate(prior,id,next,now));
    return {version:NK_PRACTICE_CHECKPOINT_VERSION,sessionId:String(s.id),sessionQuestionIds:ids,membershipHash:nkCheckpointMembership(ids),
      context:{...(s.practiceContext||{}),subject:String(s.practiceContext?.subject||''),bank:String(s.practiceContext?.bank||''),topicId:String(s.practiceContext?.topicId||''),title:String(s.practiceContext?.title||s.title||'Practice')},
      position:{index:Math.max(0,Math.min(ids.length-1,Number(s.index)||0)),currentQuestionId:current},answers:next.answers,submitted:next.submitted,
      startedAt:Number(s.startedAt||now),lastTick:Number(s.lastTick||now),elapsedMs:Number(s.elapsedMs||0),questionEnteredAt:Number(s.questionEnteredAt||now),
      questionTimes:next.questionTimes,pendingFsrsRatings:next.pendingFsrsRatings,questionUpdates,lifecycle:lifecycle||String(s.lifecycle||'active'),
      createdAt:Number(prior?.createdAt||s.startedAt||now),updatedAt:now,terminalAt:NK_PRACTICE_TERMINAL.has(lifecycle)?now:(prior?.terminalAt||null)};
  }
  function nkMirrorNormalPracticeCheckpoint(target){
    const current=nkNormalizeCheckpoint(target.normalPracticeCheckpoint),session=target.activeSession;
    if(nkNormalPracticeSession(session)){
      if(current&&NK_PRACTICE_TERMINAL.has(current.lifecycle)&&String(current.sessionId)===String(session.id)){target.activeSession=null;target.normalPracticeCheckpoint=current;return current;}
      target.normalPracticeCheckpoint=nkCheckpointFromSession(session,current,String(session.lifecycle||'active'));return target.normalPracticeCheckpoint;
    }
    if(session&&current&&!NK_PRACTICE_TERMINAL.has(current.lifecycle))target.normalPracticeCheckpoint={...current,lifecycle:'suspended',updatedAt:Date.now()};
    else target.normalPracticeCheckpoint=current;
    return target.normalPracticeCheckpoint;
  }
  function nkPrepareTimedSession(target){
    const s=target.activeSession;if(!s||s.mode!=='exam')return;
    if(!Number(s.deadlineAt))s.deadlineAt=Number(s.startedAt||Date.now())+Math.max(1,(s.questionIds||[]).length)*60000;
    s.updatedAt=Date.now();
  }
  function nkDurablePersist(candidate,reason='state save'){
    const store=nkStorageAdapter(),previousPrimary=store.getItem(LS_KEY);
    try{
      nkMirrorNormalPracticeCheckpoint(candidate);nkPrepareTimedSession(candidate);
      const next=nkNormalizeState(nkStateClone(candidate));next.stateRevision=Math.max(nkStateRevision(candidate),nkStateRevision(nkReadStateCandidate(LS_KEY)?.value))+1;
      const raw=JSON.stringify(next);
      store.setItem(NK_STATE_PENDING_KEY,raw);store.setItem(LS_KEY,raw);
      const check=store.getItem(LS_KEY);if(check!==raw)throw new Error('primary verification failed');
      store.setItem(NK_STATE_LKG_KEY,raw);store.removeItem(NK_STATE_PENDING_KEY);
      candidate.stateSchemaVersion=next.stateSchemaVersion;candidate.stateRevision=next.stateRevision;candidate.normalPracticeCheckpoint=next.normalPracticeCheckpoint;
      nkStorageClearError();return true;
    }catch(error){
      try{store.removeItem(NK_STATE_PENDING_KEY);if(previousPrimary==null)store.removeItem(LS_KEY);else store.setItem(LS_KEY,previousPrimary);}catch(_){}
      nkStorageError(`Progress was not saved during ${reason}. Nothing destructive was completed`,error);return false;
    }
  }
  function nkDurablePersistExternal(candidate){
    const live=window.QB?.getState?.();if(live&&candidate&&candidate!==live)Object.assign(live,candidate);
    return window.QB?.saveState?window.QB.saveState():nkDurablePersist(candidate||live,'compatibility save');
  }
  function nkRetryPersistence(){const ok=saveState();if(ok){nkStorageClearError();if(typeof nkScheduleCloudSync==='function')nkScheduleCloudSync();}return ok;}
  function nkFlushLifecycleState(){
    const s=state?.activeSession;
    if(s?.mode==='practice'&&typeof savePracticeElapsed==='function')savePracticeElapsed();
    else if(s?.mode==='exam'&&typeof saveExamElapsed==='function')saveExamElapsed();
    const ok=saveState();if(typeof nkCaptureCloudChanges==='function')nkCaptureCloudChanges();return ok;
  }
  window.NKQBankStorage={persistExternalState:nkDurablePersistExternal,getLastError:()=>nkStorageLastError};
  /* NK_DURABLE_PERSISTENCE_V2_END */
