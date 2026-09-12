  /* NK_CONTINUE_PRACTICE_RESUME_V1_START */
  function nkPracticeResumeQuestion(id){
    return typeof nkFindStudyQuestion==='function' ? nkFindStudyQuestion(id) : (BY_ID?.[String(id)]||null);
  }
  function nkPracticeResumeEligible(s){
    if(!s||s.mode!=='practice'||s.studyModuleId)return false;
    const origin=String(s.originRoute||s.context||s.title||'').toLowerCase();
    return !/(fsrs|spaced|review|wrong|bookmark)/.test(origin);
  }
  function nkPracticeSessionIds(s){
    const ids=Array.isArray(s?.sessionQuestionIds)&&s.sessionQuestionIds.length?s.sessionQuestionIds:s?.questionIds;
    return [...new Set((ids||[]).map(String))];
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
    const identity=nkPracticePrepareSession(s),base=nkPracticeSessionIds(s);
    if(!base.length){navigate('study-library');return false;}
    const oldIndex=Math.max(0,Number(s.index)||0),current=String(s.questionIds?.[oldIndex]||'');
    const mappedIndex=base.indexOf(current),savedIndex=Math.max(0,Math.min(base.length-1,Number(s.pausedIndex)||0));
    const targetIndex=mappedIndex>=0?mappedIndex:savedIndex;
    s.questionIds=[...base];s.index=targetIndex;s.lifecycle='active';s.resumedAt=Date.now();s.questionEnteredAt=Date.now();
    if(identity)s.practiceContext={subject:identity.subject,bank:identity.bank,topicId:identity.topicId,title:identity.title,questionIds:[...base]};
    saveState();navigate('practice');
    if(!nkPracticeRemainingIds(s).length)setTimeout(()=>window.QB.openSessionReview?.(),0);
    return true;
  }
  function nkPausePractice(){
    const s=state.activeSession;if(!nkPracticeResumeEligible(s))return false;
    if(typeof savePracticeElapsed==='function')savePracticeElapsed();nkPracticePrepareSession(s);
    s.lifecycle='paused';s.pausedAt=Date.now();s.pausedIndex=Number(s.index)||0;
    saveState();document.getElementById('nk-session-review')?.remove();document.getElementById('qb-question-navigator')?.remove();navigate('dashboard');return true;
  }
  function nkSubmitPracticeSession(){
    const s=state.activeSession;if(!nkPracticeResumeEligible(s))return false;
    nkPracticePrepareSession(s);s.lifecycle='submitted';s.submittedAt=Date.now();saveState();document.getElementById('nk-session-review')?.remove();return endSession(),true;
  }

  const nkPracticeResumeOriginalLatest=nkLatestPracticeContext;
  nkLatestPracticeContext=function(){
    const next=nkPracticeContinuation(),context=next.context;
    if((next.kind==='paused'||next.kind==='active')&&next.session){const ids=nkPracticeSessionIds(next.session),liveId=String(next.session.questionIds?.[Number(next.session.index)||0]||''),mapped=ids.indexOf(liveId),idx=mapped>=0?mapped:Math.max(0,Math.min(ids.length-1,Number(next.session.pausedIndex)||0)),q=nkPracticeResumeQuestion(ids[idx]||context?.questionIds?.[0]);return q?{q,topic:context?.title||nkTopicTitleForQuestion(q),subject:context?.subject||q.subject||activeSubject,live:true,paused:next.kind==='paused'}:null;}
    if((next.kind==='topic-remaining'||next.kind==='next-topic')&&context){const q=nkPracticeResumeQuestion(context.questionIds?.[0]);return q?{q,topic:context.title,subject:context.subject,live:false,nextTopic:next.kind==='next-topic'}:null;}
    return null;
  };
  const nkPracticeResumeOriginalContinue=nkContinueRecentPractice;
  nkContinueRecentPractice=function(){
    const next=nkPracticeContinuation();
    if(next.kind==='paused'||next.kind==='active')return nkResumePracticeSession(next.session);
    if(next.kind==='topic-remaining')return nkPracticeOpenContext(next.context,true);
    if(next.kind==='next-topic')return nkPracticeOpenContext(next.context,false);
    return navigate('study-library');
  };

  const nkPracticeResumeOriginalFinish=finishPracticeSession;
  finishPracticeSession=function(){
    const s=state.activeSession;if(!nkPracticeResumeEligible(s))return nkPracticeResumeOriginalFinish.apply(this,arguments);
    const identity=nkPracticePrepareSession(s),allIds=nkPracticeSessionIds(s),oldIndex=Number(s.index)||0;
    s.questionIds=[...allIds];s.index=Math.min(oldIndex,Math.max(0,allIds.length-1));s.lifecycle='completed';
    const complete=allIds.length>0&&allIds.every(id=>Boolean(s.submitted?.[id]));
    const result=nkPracticeResumeOriginalFinish.apply(this,arguments),test=(state.tests||[]).at(-1);
    if(test?.kind==='practice'&&identity){test.practiceContext={subject:identity.subject,bank:identity.bank,topicId:identity.topicId,title:identity.title,questionIds:[...allIds],completed:complete};saveState();}
    return result;
  };

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
