  /* NK_NOT_STUDIED_V1_START
   * "Not studied yet" flag. During Practice or a timed test the learner can flag
   * a question from the session header. A flagged question stays out of
   * everything that measures learning: no FSRS card or skip mark, no attempt,
   * and it is removed from the saved test/practice result, so accuracy, test
   * stats, Insights, coverage and weak areas never see it.
   *
   * State: state.notStudied[qid] = {on:true, at, updatedAt} | {on:false, updatedAt}
   * (a cleared flag is a tombstone so cross_device_sync.js can merge per
   * question, newest edit wins, ties resolve to cleared).
   *
   * Lifecycle rule (one rule for Practice and timed tests): answering a question
   * whose flag was set BEFORE the current session started clears the flag and
   * the answer counts normally. A flag set DURING the session stays, even if the
   * question is answered, and that answer is withheld; unflagging in the same
   * session restores it. Practice answers are recorded at once, so flagging an
   * already answered Practice question withdraws this session's attempts with
   * the existing FSRS undo events (replayed, synced like any attempt).
   */
  const NK_NS_RESULT_WINDOW=10*60000;
  function nkNsMap(){if(!state.notStudied||typeof state.notStudied!=='object'||Array.isArray(state.notStudied))state.notStudied={};return state.notStudied;}
  function nkNsClean(raw){
    if(!raw||typeof raw!=='object')return null;
    const updatedAt=Math.max(0,Math.trunc(Number(raw.updatedAt)||0));if(!updatedAt)return null;
    return raw.on===true?{on:true,at:Math.max(0,Math.trunc(Number(raw.at)||updatedAt)),updatedAt}:{on:false,updatedAt};
  }
  function nkNsEntry(qid){return state.notStudied?.[String(qid)]||null;}
  function nkNsIsFlagged(qid){return nkNsEntry(qid)?.on===true;}
  function nkNsSet(qid,on){
    const map=nkNsMap(),id=String(qid),prev=map[id];if(Boolean(prev?.on)===Boolean(on))return false;
    const at=Math.max(Date.now(),Number(prev?.updatedAt||0)+1);
    map[id]=on?{on:true,at,updatedAt:at}:{on:false,updatedAt:at};return true;
  }
  function nkNsFlaggedIds(ids){return (ids||[]).map(String).filter(nkNsIsFlagged);}
  function nkNsNewer(a,b){
    if(!b)return true;
    if(Number(a.updatedAt)!==Number(b.updatedAt))return Number(a.updatedAt)>Number(b.updatedAt);
    return a.on!==true&&b.on===true; // tie: cleared wins on every device
  }
  function nkNsMergeEntry(qid,incoming){
    const item=nkNsClean(incoming),id=String(qid||'');if(!item||!id)return false;
    const map=nkNsMap(),local=nkNsClean(map[id]);
    if(!nkNsNewer(item,local))return false;map[id]=item;return true;
  }
  // Flags made before this session started clear when the question is answered.
  function nkNsPredates(s,qid){const e=nkNsEntry(qid);return e?.on===true&&Number(e.at||0)<Number(s?.startedAt||0);}
  function nkNsQuestion(qid){const id=String(qid);return BY_ID?.[id]||(typeof nkFindStudyQuestion==='function'?nkFindStudyQuestion(id):null);}
  function nkNsIsCorrect(qid,selected){const q=nkNsQuestion(qid);return Boolean(q&&Number(q.correctOption)===Number(selected));}
  function nkNsSessionAttempts(s,qid){
    const active=typeof nkFsrsActiveAttempts==='function'?nkFsrsActiveAttempts(String(qid)):(state.attempts?.[qid]||[]).filter(a=>a&&!a.isUndo);
    return active.filter(a=>a.sessionId?String(a.sessionId)===String(s.id):Number(a.reviewedAt||a.at||0)>=Number(s.startedAt||Infinity));
  }
  // Withdraw this session's answer: the uncommitted recall rating is dropped and
  // committed attempts get undo events, then the FSRS card is replayed without them.
  function nkNsWithdrawSessionAnswer(s,qid){
    const id=String(qid);if(s.pendingRating?.[id])delete s.pendingRating[id];
    const mine=nkNsSessionAttempts(s,id);if(!mine.length)return false;
    let now=Date.now();state.attempts[id]=Array.isArray(state.attempts[id])?state.attempts[id]:[];
    mine.forEach(a=>{now=Math.max(now+1,Number(a.at||0)+1);state.attempts[id].push({id:`undo_${now}_${Math.random().toString(16).slice(2)}`,isUndo:true,undoOf:a.id,at:now,reason:'not-studied',...(typeof NK_FSRS_VERSION!=='undefined'?{schedulerVersion:NK_FSRS_VERSION}:{})});});
    if(typeof nkFsrsReplay==='function')nkFsrsReplay(id,false);return true;
  }
  // Unflagging in the same session gives the withheld answer back to FSRS: a miss is
  // recorded now, a correct answer waits for its recall rating like any other.
  function nkNsRestoreSessionAnswer(s,qid){
    const id=String(qid),selected=s.answers?.[id];
    if(s.mode!=='practice'||!s.submitted?.[id]||!selected||s.pendingRating?.[id]||nkNsSessionAttempts(s,id).length)return false;
    const source=typeof nkFsrsSessionAttemptSource==='function'?nkFsrsSessionAttemptSource(s):(s.studyModuleId?'study-module':'practice'),time=Number(s.questionTimes?.[id]||0);
    if(nkNsIsCorrect(id,selected)){s.pendingRating=s.pendingRating||{};s.pendingRating[id]={id:`pending_${Date.now()}_${Math.random().toString(16).slice(2)}`,selected:Number(selected),timeSpent:time,source,reviewedAt:Date.now()};}
    else recordAttempt(id,selected,time,source,1);
    return true;
  }
  function nkNsIcon(size=20){return `<svg class="nk-ns-icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5.5 21V3.5"/><path class="nk-ns-flag" d="M5.5 4h11.2l-2.4 4.2 2.4 4.3H5.5"/></svg>`;}
  function nkNsButton(q,s){
    const on=nkNsIsFlagged(q.id),label=on?'Not studied yet (flagged). Tap to remove the flag':'Flag as not studied yet';
    return `<button type="button" class="icon-btn nk-ns-toggle${on?' is-on':''}" aria-pressed="${on}" aria-label="${label}" title="${on?'Flagged: not studied yet':'Not studied yet'}" onclick="window.QB.nkToggleNotStudied(${esc(JSON.stringify(String(q.id)))},${esc(JSON.stringify(String(s.id)))})">${nkNsIcon(21)}</button>`;
  }
  // Answers paint in place without a full render, so the header button is patched too.
  function nkNsPatchButton(qid){
    const button=document.querySelector?.('.nk-ns-toggle');if(!button)return;
    const on=nkNsIsFlagged(qid);button.classList.toggle('is-on',on);button.setAttribute('aria-pressed',String(on));
    button.setAttribute('aria-label',on?'Not studied yet (flagged). Tap to remove the flag':'Flag as not studied yet');button.title=on?'Flagged: not studied yet':'Not studied yet';
  }
  function nkToggleNotStudied(questionId,sessionId){
    const s=state.activeSession,id=String(questionId||'');
    if(!s||!['practice','exam'].includes(s.mode)||String(s.id)!==String(sessionId)||String(s.questionIds?.[s.index])!==id)return false;
    const on=!nkNsIsFlagged(id);
    const apply=()=>{
      nkNsSet(id,on);
      if(s.mode==='practice'){if(on)nkNsWithdrawSessionAnswer(s,id);else nkNsRestoreSessionAnswer(s,id);}
      saveState();render();
      showToast(on?'Flagged as not studied. It stays out of your scores and reviews.':'Flag removed. This question counts again.');
      return true;
    };
    return typeof nkQuestionTransaction==='function'?nkQuestionTransaction(apply):apply();
  }

  // No attempt is recorded for a flagged question (timed-test submission, recall
  // commits, any other path); a flag from before this session clears instead.
  const nkNsOriginalRecord=nkFsrsRecordAttempt;
  nkFsrsRecordAttempt=function(qid,selected){
    if(nkNsIsFlagged(qid)){
      const s=state.activeSession;
      if(s&&nkNsPredates(s,qid))nkNsSet(qid,false);
      else return nkNsIsCorrect(qid,selected);
    }
    return nkNsOriginalRecord.apply(this,arguments);
  };
  recordAttempt=nkFsrsRecordAttempt;

  const nkNsOriginalSubmitPractice=submitPractice;
  submitPractice=function(){
    const s=state.activeSession,id=String(s?.questionIds?.[s?.index]??'');
    const live=s?.mode==='practice'&&id&&!s.submitted?.[id]&&s.answers?.[id];
    const prior=live?nkNsEntry(id):null,cleared=Boolean(live&&nkNsPredates(s,id)&&nkNsSet(id,false));
    const result=nkNsOriginalSubmitPractice.apply(this,arguments);
    const after=state.activeSession;
    if(cleared&&!(after?.submitted?.[id])){nkNsMap()[id]=prior;return result;}
    if(live&&after&&after.submitted?.[id]&&nkNsIsFlagged(id)&&after.pendingRating?.[id]){delete after.pendingRating[id];saveState();render();return result;}
    if(cleared){saveState();nkNsPatchButton(id);}
    return result;
  };
  const nkNsOriginalSelectExam=selectExam;
  selectExam=function(){
    const result=nkNsOriginalSelectExam.apply(this,arguments),s=state.activeSession,id=String(s?.questionIds?.[s?.index]??'');
    if(s?.mode==='exam'&&id&&s.answers?.[id]&&nkNsPredates(s,id)&&nkNsSet(id,false)){saveState();nkNsPatchButton(id);}
    return result;
  };
  // Flagged questions never become submitted-as-skipped FSRS cards.
  const nkNsOriginalMarkSkipped=nkMarkSkippedFromSession;
  nkMarkSkippedFromSession=function(s){
    const ids=nkNsFlaggedIds([...(s?.sessionQuestionIds||[]),...(s?.questionIds||[])]),prior={};
    ids.forEach(id=>{prior[id]=state.fsrsReviewEligible?.[id];});
    const result=nkNsOriginalMarkSkipped.apply(this,arguments);
    ids.forEach(id=>{if(!state.fsrsReviewEligible)return;if(prior[id]===undefined)delete state.fsrsReviewEligible[id];else state.fsrsReviewEligible[id]=prior[id];});
    return result;
  };

  // A just-saved result drops its flagged questions, so every analysis that reads
  // saved tests (score, accuracy, timing, CBT/topic analysis, Insights) skips them.
  // notStudiedIds marks a result as handled; older results are never rewritten.
  function nkNsSanitizeTest(t){
    if(!t||!Array.isArray(t.questionIds)||Array.isArray(t.notStudiedIds))return false;
    const flagged=new Set(nkNsFlaggedIds(t.questionIds));t.notStudiedIds=[...flagged];
    if(!flagged.size)return true;
    const keep=id=>!flagged.has(String(id));
    t.questionIds=t.questionIds.filter(keep);
    ['answers','questionTimes','markedForReview','expired'].forEach(key=>{if(t[key]&&typeof t[key]==='object')t[key]=Object.fromEntries(Object.entries(t[key]).filter(([id])=>keep(id)));});
    let correct=0,incorrect=0,attempted=0;
    Object.entries(t.answers||{}).forEach(([id,selected])=>{if(!selected)return;attempted++;if(nkNsIsCorrect(id,selected))correct++;else incorrect++;});
    Object.assign(t,{correct,incorrect,attempted,total:t.questionIds.length,unattempted:Math.max(0,t.questionIds.length-attempted)});
    if(t.kind==='practice'||t.timerMode==='per-question')t.totalTimeMs=Object.values(t.questionTimes||{}).reduce((sum,v)=>sum+Number(v||0),0);
    return true;
  }
  const nkNsOriginalNavigate=navigate;
  navigate=function(page,id){
    if(page==='result'&&id!=null){
      const tests=Array.isArray(state.tests)?state.tests:[],t=tests.find(x=>String(x.id)===String(id));
      if(t&&!Array.isArray(t.notStudiedIds)&&Date.now()-Number(t.createdAt||0)<NK_NS_RESULT_WINDOW&&nkNsSanitizeTest(t)){
        if(!t.questionIds.length){
          state.tests=tests.filter(x=>x!==t);saveState();
          showToast('Every question was flagged as not studied, so no result was saved.');
          return nkNsOriginalNavigate.call(this,t.originRoute||(t.kind==='practice'?'topics':'tests'));
        }
        saveState();
      }
    }
    return nkNsOriginalNavigate.apply(this,arguments);
  };

  // Session header: the flag sits beside the bookmark (Practice and timed tests only).
  const nkNsOriginalHeader=nkSessionHeader;
  nkSessionHeader=function(q,s,mode){
    const out=nkNsOriginalHeader.apply(this,arguments);
    if(!q||!s||!['practice','exam'].includes(mode)||s.mode!==mode)return out;
    return out.replace('<div class="q-actions">','<div class="q-actions">'+nkNsButton(q,s));
  };
  function nkNsDecorateGrid(root,selector,s){
    if(!root||!s)return;let count=0;
    root.querySelectorAll(selector).forEach((cell,i)=>{
      const id=s.questionIds?.[i];if(id==null||!nkNsIsFlagged(id))return;count++;
      cell.classList.add('is-ns');cell.setAttribute('aria-label',`${cell.getAttribute('aria-label')||`Question ${i+1}`}, not studied`);
      const small=cell.querySelector('small');if(small)small.textContent='Not studied';
      if(!cell.querySelector('.nk-ns-icon'))cell.insertAdjacentHTML('beforeend',`<span class="nk-ns-corner">${nkNsIcon(10)}</span>`);
    });
    return count;
  }
  const nkNsOriginalSessionReview=openSessionReview;
  openSessionReview=function(){
    const result=nkNsOriginalSessionReview.apply(this,arguments),s=state.activeSession;
    if(!['practice','exam'].includes(s?.mode))return result;
    const root=document.getElementById('nk-session-review');
    if(nkNsDecorateGrid(root,'.nk-session-review-q',s))root.querySelector('.nk-session-review-legend')?.insertAdjacentHTML('beforeend',`<span><i class="nk-review-dot is-ns"></i>Not studied</span>`);
    return result;
  };
  const nkNsOriginalNavigator=openQuestionNavigator;
  openQuestionNavigator=function(){
    const result=nkNsOriginalNavigator.apply(this,arguments),s=state.activeSession;
    if(!['practice','exam'].includes(s?.mode))return result;
    const root=document.getElementById('qb-question-navigator');
    if(nkNsDecorateGrid(root,'.qb-nav-q',s))root.querySelector('.qb-nav-legend')?.insertAdjacentHTML('beforeend','<span><i class="qb-legend-dot is-ns"></i>Not studied</span>');
    return result;
  };

  // Topics: a flag badge with the count on each topic row; the topic page marks
  // flagged cells and offers "Practice flagged (N)".
  function nkNsTopicIds(cid){return typeof chapterQuestions==='function'?chapterQuestions(cid).filter(q=>nkNsIsFlagged(q.id)).map(q=>String(q.id)):[];}
  function nkNsAnyFlags(){return Object.values(state.notStudied||{}).some(e=>e?.on===true);}
  function nkNsReEscape(value){return String(value).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
  const nkNsOriginalTopics=topics;
  topics=function(){
    let out=nkNsOriginalTopics.apply(this,arguments);if(!nkNsAnyFlags())return out;
    (CHAPTERS||[]).forEach(c=>{
      const n=nkNsTopicIds(c.id).length;if(!n)return;
      const pattern=new RegExp(`(onclick="window\\.QB\\.openChapter\\('${nkNsReEscape(c.id)}'\\)"[\\s\\S]*?<span class="nk-topic-copy">[\\s\\S]*?<small>[\\s\\S]*?)(</small>)`);
      out=out.replace(pattern,`$1<span class="nk-ns-badge" aria-label="${n} flagged not studied">${nkNsIcon(12)}${n}</span>$2`);
    });
    return out;
  };
  const nkNsOriginalChapterPage=chapterPage;
  chapterPage=function(cid){
    let out=nkNsOriginalChapterPage.apply(this,arguments);
    const c=typeof CHAPTER_BY_ID!=='undefined'?CHAPTER_BY_ID[String(cid)]:null;if(!c||!nkNsAnyFlags())return out;
    const ids=new Set(nkNsTopicIds(c.id));if(!ids.size)return out;
    out=out.replace(/<button class="(nk-library-row nk-topic-cell[^"]*)"([^>]*?) aria-label="([^"]*)"([^>]*?) onclick="window\.QB\.practiceOne\('([^']*)'\)">([^<]*)<\/button>/g,(all,cls,a,label,b,qid,text)=>ids.has(String(qid))?`<button class="${cls} is-ns"${a} aria-label="${label}, flagged not studied"${b} onclick="window.QB.practiceOne('${qid}')">${text}<span class="nk-ns-corner">${nkNsIcon(10)}</span></button>`:all);
    const item=`<li class="is-ns"><b>${fmtNum(ids.size)}</b> not studied</li>`;
    out=out.includes('<ul class="nk-topic-legend">')?out.replace(/(<ul class="nk-topic-legend">[\s\S]*?)(<\/ul>)/,`$1${item}$2`):out.replace(/(<div class="nk-topic-map">[\s\S]*?<\/div>)/,`$1<ul class="nk-topic-legend">${item}</ul>`);
    out=out.replace(/(<div class="nk-topic-options">[\s\S]*?)(<\/div><\/div><\/section>)/,`$1<button class="nk-topic-option nk-topic-ns" onclick="window.QB.nkPracticeNotStudied('${esc(String(c.id))}')">${nkNsIcon(18)}<span>Practice flagged</span><small>${fmtNum(ids.size)}</small>${navIcon('chevron',16)}</button>$2`);
    return out;
  };
  function nkPracticeNotStudied(cid){
    const c=CHAPTER_BY_ID[String(cid)],ids=nkNsTopicIds(cid);
    if(!ids.length){showToast('No flagged questions in this topic.','bad');return false;}
    return startSession(ids,'practice',`${c?.title||'Topic'} · Not studied`);
  }
  /* NK_NOT_STUDIED_V1_END */
