  /* NK_CONTINUE_PRACTICE_RESUME_V1_START */
  function nkPracticeCloseOverlays(){
    const close=()=>{document.getElementById('nk-session-review')?.remove();document.getElementById('qb-question-navigator')?.remove();};
    if(typeof nkAfterQuestionCommit==='function')nkAfterQuestionCommit(close);else close();
  }
  function nkPracticeResumeQuestion(id){
    return typeof nkFindStudyQuestion==='function' ? nkFindStudyQuestion(id) : (BY_ID?.[String(id)]||null);
  }
  function nkPracticeResumeEligible(s){
    if(!s||s.mode!=='practice'||s.studyModuleId)return false;
    const origin=[s.originRoute,s.context,s.title].filter(Boolean).join(' ').toLowerCase();
    return !/(fsrs|spaced|review|wrong|bookmark)/.test(origin);
  }
  function nkPracticeSessionIds(s){
    const ids=Array.isArray(s?.sessionQuestionIds)&&s.sessionQuestionIds.length?s.sessionQuestionIds:s?.questionIds;
    return [...new Set((ids||[]).map(String))];
  }
  function nkPracticeCheckpoint(){
    const checkpoint=typeof nkNormalizeCheckpoint==='function'?nkNormalizeCheckpoint(state.normalPracticeCheckpoint):state.normalPracticeCheckpoint;
    return checkpoint&& !['submitted','completed','discarded'].includes(String(checkpoint.lifecycle))?checkpoint:null;
  }
  function nkPracticeSessionFromCheckpoint(checkpoint=nkPracticeCheckpoint()){
    if(!checkpoint)return null;
    const ids=[...(checkpoint.sessionQuestionIds||[])].map(String),missing=ids.filter(id=>!nkPracticeResumeQuestion(id));
    if(!ids.length||missing.length){
      state.normalPracticeConflict={type:'missing-questions',sessionId:String(checkpoint.sessionId||''),missingQuestionIds:missing,detectedAt:Date.now()};
      if(typeof nkStorageError==='function')nkStorageError(`Practice ${checkpoint.sessionId} cannot resume because ${missing.length||ids.length} saved question ID${(missing.length||ids.length)===1?' is':'s are'} unavailable`);
      return null;
    }
    const position=checkpoint.position||{},mapped=ids.indexOf(String(position.currentQuestionId||'')),index=mapped>=0?mapped:Math.max(0,Math.min(ids.length-1,Number(position.index)||0));
    return {id:String(checkpoint.sessionId),mode:'practice',title:String(checkpoint.context?.title||'Practice'),questionIds:[...ids],sessionQuestionIds:[...ids],index,
      answers:{...(checkpoint.answers||{})},submitted:{...(checkpoint.submitted||{})},startedAt:Number(checkpoint.startedAt||Date.now()),lastTick:Number(checkpoint.lastTick||Date.now()),
      elapsedMs:Number(checkpoint.elapsedMs||0),questionEnteredAt:Date.now(),questionTimes:{...(checkpoint.questionTimes||{})},pendingRating:{...(checkpoint.pendingFsrsRatings||{})},
      context:'normal',originRoute:'topics',practiceContext:{...(checkpoint.context||{}),questionIds:[...ids]},lifecycle:String(checkpoint.lifecycle)==='active'?'paused':String(checkpoint.lifecycle)};
  }
  function nkPracticeIdentity(s){
    const ids=nkPracticeSessionIds(s),questions=ids.map(nkPracticeResumeQuestion).filter(Boolean);
    if(!questions.length)return null;
    const first=questions[0],subject=String(first.subject||s?.practiceContext?.subject||activeSubject||'');
    let bank=String(first.bank||s?.practiceContext?.bank||'');
    if(!bank&&typeof nkBankRecords==='function'){
      const owner=nkBankRecords(subject).find(r=>(r.questions||[]).some(q=>String(q.id)===String(first.id)));
      bank=String(owner?.bank||'');
    }
    const topicId=String(first.chapterId||s?.practiceContext?.topicId||'');
    const sameTopic=Boolean(topicId)&&questions.every(q=>String(q.subject||subject)===subject&&String(q.bank||bank)===bank&&String(q.chapterId||'')===topicId);
    return {subject,bank,topicId:sameTopic?topicId:'',title:sameTopic?(nkTopicTitleForQuestion(first)||first.chapter||s?.title||'Practice'):String(s?.title||'Practice'),questionIds:ids};
  }
  function nkPracticePrepareSession(s){
    if(!nkPracticeResumeEligible(s))return null;
    if(!Array.isArray(s.sessionQuestionIds)||!s.sessionQuestionIds.length)s.sessionQuestionIds=[...(s.questionIds||[])].map(String);
    const identity=nkPracticeIdentity(s);
    if(identity)s.practiceContext={subject:identity.subject,bank:identity.bank,topicId:identity.topicId,title:identity.title,questionIds:[...identity.questionIds]};
    return identity;
  }
  function nkPracticeRemainingIds(s){
    return nkPracticeSessionIds(s).filter(id=>!Boolean(s?.submitted?.[String(id)]));
  }
  function nkPracticeRecord(subject,bank){
    const records=typeof nkBankRecords==='function'?nkBankRecords(subject):[];
    return records.find(r=>String(r.bank||'')===String(bank||''))||records[0]||(SUBJECTS||[]).find(r=>String(r.subject||'')===String(subject||''))||null;
  }
  function nkPracticeTopicContext(subject,bank,topicId){
    const record=nkPracticeRecord(subject,bank);if(!record)return null;
    const topics=Array.isArray(record.topics)?record.topics:[],index=topics.findIndex(t=>String(t.id)===String(topicId));if(index<0)return null;
    const topic=topics[index],ids=(record.questions||[]).filter(q=>String(q.chapterId)===String(topic.id)).map(q=>String(q.id));
    return {record,topic,index,subject:String(record.subject||subject||''),bank:String(record.bank||bank||''),topicId:String(topic.id),title:String(topic.title||topic.name||'Topic'),questionIds:ids};
  }
  function nkPracticeNextTopic(context){
    if(!context?.topicId)return null;const current=nkPracticeTopicContext(context.subject,context.bank,context.topicId);if(!current)return null;
    const topic=current.record.topics?.[current.index+1];if(!topic)return null;
    return nkPracticeTopicContext(current.subject,current.bank,topic.id);
  }
  function nkPracticeLatestCompletedContext(){
    const tests=(state.tests||[]).filter(t=>t?.kind==='practice'&&t.practiceContext?.topicId).sort((a,b)=>Number(b.createdAt||0)-Number(a.createdAt||0));
    return tests[0]?.practiceContext||null;
  }
  function nkPracticeContinuation(){
    const live=state.activeSession;
    if(nkPracticeResumeEligible(live)&&nkPracticeSessionIds(live).length){
      const identity=nkPracticePrepareSession(live);
      return {kind:live.lifecycle==='paused'?'paused':'active',session:live,context:identity};
    }
    const checkpoint=nkPracticeCheckpoint(),restored=nkPracticeSessionFromCheckpoint(checkpoint);
    if(restored){const identity=nkPracticeIdentity(restored);return {kind:checkpoint.lifecycle==='active'?'paused':checkpoint.lifecycle,session:restored,context:identity,fromCheckpoint:true};}
    const completed=nkPracticeLatestCompletedContext();
    if(completed){
      const current=nkPracticeTopicContext(completed.subject,completed.bank,completed.topicId);
      if(current){
        const pending=current.questionIds.filter(id=>!(typeof qAttempts==='function'&&qAttempts(id).length));
        if(!pending.length){const next=nkPracticeNextTopic(completed);return next?{kind:'next-topic',context:next}:{kind:'library'};}
        return {kind:'topic-remaining',context:{...current,questionIds:pending}};
      }
    }
    const legacy=typeof nkPracticeResumeOriginalLatest==='function'?nkPracticeResumeOriginalLatest():null;
    if(legacy?.q){
      const current=nkPracticeTopicContext(legacy.q.subject,legacy.q.bank,legacy.q.chapterId);
      if(current){
        const pending=current.questionIds.filter(id=>!(typeof qAttempts==='function'&&qAttempts(id).length));
        if(!pending.length){const next=nkPracticeNextTopic(current);return next?{kind:'next-topic',context:next}:{kind:'library'};}
        return {kind:'topic-remaining',context:{...current,questionIds:pending}};
      }
    }
    return {kind:'library'};
  }
  function nkPracticeOpenContext(context,start=false){
    if(!context)return navigate('study-library');
    if(start){
      const ids=[...(context.questionIds||[])];if(!ids.length)return navigate('study-library');
      if(typeof openBank==='function'&&context.bank)openBank(context.subject,context.bank);else if(typeof openSubjectTopics==='function')openSubjectTopics(context.subject);
      startSession(ids,'practice',context.title||`${context.subject} Practice`);
      const s=state.activeSession;if(s){s.lifecycle='active';s.sessionQuestionIds=[...ids];s.practiceContext={subject:context.subject,bank:context.bank,topicId:context.topicId,title:context.title,questionIds:[...ids]};saveState();}
      return;
    }
    if(typeof nkOpenSubjectChapter==='function')return nkOpenSubjectChapter(context.subject,context.bank,context.topicId);
    if(typeof openBank==='function'&&context.bank)openBank(context.subject,context.bank);
    return typeof openChapter==='function'?openChapter(context.topicId):navigate('study-library');
  }
  function nkResumePracticeSession(s){
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));
    if(state.activeSession&&state.activeSession!==s&&!nkPracticeResumeEligible(state.activeSession)){
      if(state.activeSession.mode==='exam')nkOfferTimedSessionDecision();else showToast('Finish or leave the current study session before resuming Practice.','bad');
      return false;
    }
    if(state.activeSession!==s)state.activeSession=s;
    const identity=nkPracticePrepareSession(s),base=nkPracticeSessionIds(s);
    if(!base.length){navigate('study-library');return false;}
    const oldIndex=Math.max(0,Number(s.index)||0),current=String(s.questionIds?.[oldIndex]||'');
    const mappedIndex=base.indexOf(current),savedIndex=Math.max(0,Math.min(base.length-1,Number(s.pausedIndex)||0));
    const targetIndex=mappedIndex>=0?mappedIndex:savedIndex;
    s.questionIds=[...base];s.index=targetIndex;s.lifecycle='active';s.resumedAt=Date.now();s.questionEnteredAt=Date.now();
    if(identity)s.practiceContext={subject:identity.subject,bank:identity.bank,topicId:identity.topicId,title:identity.title,questionIds:[...base]};
    if(saveState()===false){state=before;return false;}navigate('practice');
    if(!nkPracticeRemainingIds(s).length)setTimeout(()=>window.QB.openSessionReview?.(),0);
    return true;
  }
  function nkPausePractice(){
    const s=state.activeSession;if(!nkPracticeResumeEligible(s))return false;
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));
    if(typeof savePracticeElapsed==='function')savePracticeElapsed();nkPracticePrepareSession(s);
    s.lifecycle='paused';s.pausedAt=Date.now();s.pausedIndex=Number(s.index)||0;
    if(saveState()===false){state=before;return false;}nkPracticeCloseOverlays();navigate('dashboard');return true;
  }
  function nkSubmitPracticeSession(){
    const s=state.activeSession;if(!nkPracticeResumeEligible(s))return false;
    nkPracticePrepareSession(s);return finishPracticeSession();
  }

  let nkPendingInteractiveStart=null;
  function nkPracticeReplacementDialog(){
    if(typeof document==='undefined'||!document.body)return false;
    document.getElementById('nk-practice-replacement')?.remove();
    document.body.insertAdjacentHTML('beforeend','<div class="modal-backdrop" id="nk-practice-replacement"><section class="modal card" role="dialog" aria-modal="true" aria-labelledby="nk-practice-replacement-title"><h2 id="nk-practice-replacement-title">Continue your saved Practice?</h2><p>One normal Practice session is already saved. Resume it, or explicitly discard it before starting another.</p><div class="nk-fsrs-leave-actions"><button class="primary-btn" onclick="window.QB.nkResolvePracticeReplacement(\'resume\')">Resume saved Practice</button><button class="danger-btn" onclick="window.QB.nkResolvePracticeReplacement(\'discard\')">Discard and start new</button><button class="ghost-btn" onclick="window.QB.nkResolvePracticeReplacement(\'cancel\')">Cancel</button></div></section></div>');
    return true;
  }
  function nkDiscardNormalPractice(){
    const checkpoint=nkPracticeCheckpoint();if(!checkpoint)return true;
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state)),now=Date.now();
    state.normalPracticeCheckpoint={...checkpoint,lifecycle:'discarded',discardedAt:now,terminalAt:now,updatedAt:now};
    if(nkPracticeResumeEligible(state.activeSession)&&String(state.activeSession.id)===String(checkpoint.sessionId))state.activeSession=null;
    if(saveState()===false){state=before;return false;}return true;
  }
  function nkResolvePracticeReplacement(choice){
    document.getElementById('nk-practice-replacement')?.remove();
    if(choice==='resume'){nkPendingInteractiveStart=null;const next=nkPracticeContinuation();return next.session?nkResumePracticeSession(next.session):false;}
    if(choice!=='discard'){nkPendingInteractiveStart=null;return false;}
    const pending=nkPendingInteractiveStart;nkPendingInteractiveStart=null;if(!nkDiscardNormalPractice()||!pending)return false;
    return nkStartSessionReliably(pending.questionIds,pending.mode,pending.title,pending.context,true);
  }
  function nkTimedSessionExpired(s,now=Date.now()){
    if(!s||s.mode!=='exam')return false;
    const deadline=Number(s.timerMode==='per-question'?(s.strictQuestionStartedAt||s.questionEnteredAt||s.startedAt)+60000:s.deadlineAt||(Number(s.startedAt||now)+Math.max(1,(s.questionIds||[]).length)*60000));
    return deadline<=now;
  }
  function nkOfferTimedSessionDecision(pending=null){
    nkPendingInteractiveStart=pending;
    if(typeof document==='undefined'||!document.body)return false;
    document.getElementById('nk-timed-session-conflict')?.remove();
    document.body.insertAdjacentHTML('beforeend','<div class="modal-backdrop" id="nk-timed-session-conflict"><section class="modal card" role="dialog" aria-modal="true" aria-labelledby="nk-timed-session-title"><h2 id="nk-timed-session-title">Timed CBT in progress</h2><p>Resume the timed test, or explicitly abandon it before opening another interactive session.</p><div class="nk-fsrs-leave-actions"><button class="primary-btn" onclick="window.QB.nkResolveTimedSession(\'resume\')">Resume CBT</button><button class="danger-btn" onclick="window.QB.nkResolveTimedSession(\'abandon\')">Abandon CBT</button><button class="ghost-btn" onclick="window.QB.nkResolveTimedSession(\'cancel\')">Cancel</button></div></section></div>');return true;
  }
  function nkResolveTimedSession(choice){
    document.getElementById('nk-timed-session-conflict')?.remove();const pending=nkPendingInteractiveStart;nkPendingInteractiveStart=null;
    if(choice==='resume'){navigate('exam');return true;}if(choice!=='abandon')return false;
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));if(state.activeSession?.mode==='exam')state.activeSession=null;
    if(saveState()===false){state=before;return false;}return pending?nkStartSessionReliably(pending.questionIds,pending.mode,pending.title,pending.context,true):navigate('dashboard');
  }
  const nkPracticeOriginalStartSession=startSession;
  function nkStartSessionReliably(questionIds,mode='practice',title='Practice Session',context='normal',replacementApproved=false){
    const ids=[...new Set((questionIds||[]).map(String))];if(!ids.length){showToast('No questions available for this session.','bad');return false;}
    const pending={questionIds:ids,mode,title,context},live=state.activeSession;
    if(live?.mode==='exam'){
      if(nkTimedSessionExpired(live)){submitExam(true);return false;}
      nkOfferTimedSessionDecision(pending);return false;
    }
    const candidate={mode,title,context},normal=nkPracticeResumeEligible(candidate);
    if(normal&&!replacementApproved&&nkPracticeCheckpoint()){
      nkPendingInteractiveStart=pending;nkPracticeReplacementDialog();return false;
    }
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state)),now=Date.now();
    if(live&&nkPracticeResumeEligible(live)&&!normal){live.lifecycle='suspended';if(typeof nkMirrorNormalPracticeCheckpoint==='function')nkMirrorNormalPracticeCheckpoint(state);}
    state.activeSession={id:`s_${now}_${Math.random().toString(16).slice(2)}`,mode,title,questionIds:[...ids],index:0,answers:{},submitted:{},startedAt:now,lastTick:now,elapsedMs:0,questionEnteredAt:now,questionTimes:{},context};
    state.activeSession.originRoute=context==='fsrs'||context==='spaced-review'?'fsrs':/bookmark/i.test(title)?'bookmarks':context==='wrong'||/wrong/i.test(title)?'wrong':mode==='exam'?'tests':'topics';
    if(mode==='exam')state.activeSession.deadlineAt=now+ids.length*60000;
    if(normal){state.activeSession.lifecycle='active';state.activeSession.sessionQuestionIds=[...ids];}
    if(!state.studyStartedAt)state.studyStartedAt=now;
    if(saveState()===false){state=before;return false;}navigate(mode==='exam'?'exam':'practice');return true;
  }
  startSession=nkStartSessionReliably;
  const nkPracticeOriginalSubmitExam=submitExam;
  submitExam=function(auto=false){
    const s=state.activeSession;if(!s||s.mode!=='exam')return false;if(s.__terminalSaveInFlight)return false;
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));s.__terminalSaveInFlight=true;
    try{
      if(typeof closeQuestionNavigator==='function')closeQuestionNavigator();
      if(s.timerMode==='per-question'&&typeof nkStrictCommitCurrent==='function')nkStrictCommitCurrent();
      if(typeof saveExamElapsed==='function')saveExamElapsed();
      const now=Date.now(),qt={...(s.questionTimes||{})},strict=s.timerMode==='per-question';let correct=0,incorrect=0,attempted=0;
      Object.entries(s.answers||{}).forEach(([id,selected])=>{if(!selected)return;attempted++;const q=nkPracticeResumeQuestion(id),ok=q&&Number(q.correctOption)===Number(selected);if(ok)correct++;else incorrect++;recordAttempt(id,selected,qt[id]||0,'exam',undefined,now,`exam_${String(s.id)}_${String(id)}`);});
      const unattempted=Math.max(0,s.questionIds.length-attempted);if(typeof nkMarkSkippedFromSession==='function')nkMarkSkippedFromSession(s);
      const raw=now-Number(s.startedAt||now),totalTimeMs=strict?s.questionIds.reduce((total,id)=>total+Math.min(60000,Math.max(Number(qt[id]||0),Number(s.strictQuestionTime?.[id]||0))),0):Math.min(raw,s.questionIds.length*60000);
      const testId=`exam_${String(s.id)}`;let test=(state.tests||[]).find(item=>String(item.id)===testId);
      if(!test){test={id:testId,title:s.title,questionIds:[...s.questionIds],answers:{...(s.answers||{})},questionTimes:qt,correct,incorrect,unattempted,total:s.questionIds.length,attempted,totalTimeMs,createdAt:now,autoSubmitted:Boolean(auto),timerEnabled:true,timerMode:s.timerMode||'global',originRoute:s.originRoute};state.tests.push(test);state.tests=state.tests.slice(-100);}
      s.lifecycle='submitted';s.submittedAt=now;state.activeSession=null;
      if(saveState()===false){state=before;return false;}
      document.querySelectorAll?.('#toast-root .toast').forEach(node=>node.remove());navigate('result',test.id);return true;
    }catch(error){state=before;if(typeof nkStorageError==='function')nkStorageError('Timed CBT submission could not be completed',error);else showToast('Timed CBT could not be saved. Try again.','bad');return false;}
  };

  const nkPracticeResumeOriginalLatest=nkLatestPracticeContext;
  nkLatestPracticeContext=function(){
    const next=nkPracticeContinuation(),context=next.context;
    if(['paused','active','suspended'].includes(next.kind)&&next.session){const ids=nkPracticeSessionIds(next.session),liveId=String(next.session.questionIds?.[Number(next.session.index)||0]||''),mapped=ids.indexOf(liveId),idx=mapped>=0?mapped:Math.max(0,Math.min(ids.length-1,Number(next.session.pausedIndex)||0)),q=nkPracticeResumeQuestion(ids[idx]||context?.questionIds?.[0]);return q?{q,topic:context?.title||nkTopicTitleForQuestion(q),subject:context?.subject||q.subject||activeSubject,live:true,paused:next.kind!=='active'}:null;}
    if((next.kind==='topic-remaining'||next.kind==='next-topic')&&context){const q=nkPracticeResumeQuestion(context.questionIds?.[0]);return q?{q,topic:context.title,subject:context.subject,live:false,nextTopic:next.kind==='next-topic'}:null;}
    return null;
  };
  const nkPracticeResumeOriginalContinue=nkContinueRecentPractice;
  nkContinueRecentPractice=function(){
    const next=nkPracticeContinuation();
    if(['paused','active','suspended'].includes(next.kind))return nkResumePracticeSession(next.session);
    if(next.kind==='topic-remaining')return nkPracticeOpenContext(next.context,true);
    if(next.kind==='next-topic')return nkPracticeOpenContext(next.context,false);
    return navigate('study-library');
  };

  // The visible Home "Continue Practice" button is wired to continuePractice(),
  // not nkContinueRecentPractice(). Route both entry points through the same durable
  // continuation logic so Home can never fall back to the legacy one-question session.
  const nkPracticeResumeOriginalHomeContinue=continuePractice;
  continuePractice=function(){
    return nkContinueRecentPractice();
  };

  const nkPracticeResumeOriginalFinish=finishPracticeSession;
  finishPracticeSession=function(){
    const s=state.activeSession;if(!nkPracticeResumeEligible(s))return nkPracticeResumeOriginalFinish.apply(this,arguments);
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state));
    if(s.__terminalSaveInFlight)return false;s.__terminalSaveInFlight=true;
    try{
      if(typeof savePracticeElapsed==='function')savePracticeElapsed();
      if(typeof nkFsrsRecoverPending==='function')nkFsrsRecoverPending();
      const identity=nkPracticePrepareSession(s),allIds=nkPracticeSessionIds(s),oldIndex=Number(s.index)||0,now=Date.now();
      s.questionIds=[...allIds];s.index=Math.min(oldIndex,Math.max(0,allIds.length-1));s.lifecycle='submitted';s.submittedAt=now;
      if(typeof nkMarkSkippedFromSession==='function')nkMarkSkippedFromSession(s);
      const answers={...(s.answers||{})},qt={...(s.questionTimes||{})};let correct=0,incorrect=0,attempted=0;
      Object.entries(answers).forEach(([id,selected])=>{if(!selected)return;attempted++;const q=nkPracticeResumeQuestion(id);if(q&&Number(q.correctOption)===Number(selected))correct++;else incorrect++;});
      const testId=`practice_${String(s.id)}`,complete=allIds.length>0&&allIds.every(id=>Boolean(s.submitted?.[id]));
      let test=(state.tests||[]).find(item=>String(item.id)===testId);
      if(!test){test={id:testId,title:s.title,kind:'practice',questionIds:[...allIds],answers,questionTimes:qt,correct,incorrect,unattempted:Math.max(0,allIds.length-attempted),total:allIds.length,attempted,totalTimeMs:Object.values(qt).reduce((sum,value)=>sum+Number(value||0),0),createdAt:now,autoSubmitted:false};state.tests.push(test);state.tests=state.tests.slice(-100);}
      if(identity)test.practiceContext={subject:identity.subject,bank:identity.bank,topicId:identity.topicId,title:identity.title,questionIds:[...allIds],completed:complete};
      const checkpoint=typeof nkCheckpointFromSession==='function'?nkCheckpointFromSession(s,state.normalPracticeCheckpoint,'submitted'):{...(state.normalPracticeCheckpoint||{}),lifecycle:'submitted',updatedAt:now,terminalAt:now};
      state.normalPracticeCheckpoint=checkpoint;state.activeSession=null;
      if(saveState()===false){state=before;return false;}
      nkPracticeCloseOverlays();document.querySelectorAll?.('#toast-root .toast').forEach(node=>node.remove());
      navigate('result',test.id);return true;
    }catch(error){state=before;if(typeof nkStorageError==='function')nkStorageError('Practice submission could not be completed',error);else showToast('Practice submission could not be saved. Try again.','bad');return false;}
  };

  function nkReliabilityInit(){
    if(nkReliabilityInit.done)return;nkReliabilityInit.done=true;
    const checkpoint=nkPracticeCheckpoint(),live=state.activeSession;let changed=false;
    if(live&&nkPracticeResumeEligible(live)){
      const terminal=state.normalPracticeCheckpoint&&['submitted','completed','discarded'].includes(String(state.normalPracticeCheckpoint.lifecycle))&&String(state.normalPracticeCheckpoint.sessionId)===String(live.id);
      if(terminal){state.activeSession=null;changed=true;}
      else{
        const ids=nkPracticeSessionIds(live),valid=ids.length&&ids.every(id=>nkPracticeResumeQuestion(id));
        if(valid){live.sessionQuestionIds=[...ids];if(live.questionIds?.length!==ids.length)live.questionIds=[...ids];if(!live.lifecycle)live.lifecycle='paused';changed=true;}
        else{state.normalPracticeConflict={type:'missing-questions',sessionId:String(live.id||''),missingQuestionIds:ids.filter(id=>!nkPracticeResumeQuestion(id)),detectedAt:Date.now()};route={page:'dashboard',id:null};changed=true;}
      }
    }else if(live?.mode==='review'){state.activeSession=null;changed=true;}
    if(state.activeSession?.mode==='exam'){
      if(nkTimedSessionExpired(state.activeSession))setTimeout(()=>submitExam(true),0);
      else{route={page:'exam',id:null};try{history.replaceState(null,'','#exam');}catch(_){}}
    }
    if(typeof nkStorageBootNotice!=='undefined'&&nkStorageBootNotice)setTimeout(()=>nkStorageError(nkStorageBootNotice),0);
    document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&typeof nkFlushLifecycleState==='function')nkFlushLifecycleState();});
    window.addEventListener('pagehide',()=>{if(typeof nkFlushLifecycleState==='function')nkFlushLifecycleState();});
    if(checkpoint&&!state.activeSession&&checkpoint.lifecycle==='active'){state.normalPracticeCheckpoint={...checkpoint,lifecycle:'paused',updatedAt:Date.now()};changed=true;}
    if(changed)saveState();
  }

  const nkPracticeResumeOriginalActionBar=practiceActionBar;
  practiceActionBar=function(){
    const out=nkPracticeResumeOriginalActionBar.apply(this,arguments),s=state.activeSession;
    if(!nkPracticeResumeEligible(s)||!out.includes('<div class="fixed-actions-inner">'))return out;
    const controls='<div class="nk-practice-session-controls" role="group" aria-label="Practice session controls"><button type="button" class="ghost-btn nk-practice-pause" onclick="window.QB.nkPausePractice()">Pause</button><button type="button" class="primary-btn nk-practice-submit" onclick="window.QB.nkSubmitPracticeSession()">Submit</button></div>';
    return out.replace('<div class="fixed-actions-inner">',controls+'<div class="fixed-actions-inner">');
  };

  const nkPracticeResumeOriginalReview=openSessionReview;
  openSessionReview=function(){
    const s=state.activeSession,result=nkPracticeResumeOriginalReview.apply(this,arguments);if(!nkPracticeResumeEligible(s))return result;
    const box=document.getElementById('nk-session-review');if(!box)return result;
    const primary=box.querySelector('.nk-session-review-actions .primary-btn');if(primary){primary.textContent='Submit';primary.setAttribute('onclick','window.QB.nkSubmitPracticeSession()');primary.classList.add('nk-practice-submit');}
    const actions=box.querySelector('.nk-session-review-actions');if(actions&&!actions.querySelector('.nk-practice-pause'))actions.insertAdjacentHTML('beforeend','<button type="button" class="ghost-btn nk-practice-pause" onclick="window.QB.nkPausePractice()">Pause</button>');
    const heading=box.querySelector('.nk-session-review-head h2');if(heading)heading.textContent='Review before submitting';
    return result;
  };
  /* NK_CONTINUE_PRACTICE_RESUME_V1_END */
