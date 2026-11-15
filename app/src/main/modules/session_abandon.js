  /* NK_SESSION_ABANDON_V1_START
   * Abandon any in-progress session (Practice, revision, study module, FSRS
   * review, timed CBT / topic test / quick test). Supersedes the timed-only
   * grid action (timed_abandon_grid.js). Rules: docs/SESSION_ABANDON.md.
   *
   * An abandoned session leaves one trace: its entry in state.abandonedSessions
   * (shown as "Abandoned" in the session lists, synced as kind `abandoned`).
   * - Practice records each answer at once, so its attempts are withdrawn with
   *   FSRS undo events (reason 'abandoned'), which every app version honours,
   *   and the session's cards are replayed without them.
   * - nkFsrsActiveAttempts also drops every attempt whose sessionId is an
   *   abandoned session, so an answer that reaches this device later (another
   *   device still in the session, an old outbox) never counts either. FSRS,
   *   mistakes, stats, Insights, coverage, streak, heatmap and Today all read it.
   * - Timed tests record nothing until Submit; their session is dropped.
   * - The resume checkpoint becomes a terminal 'discarded' tombstone, the synced
   *   special session is deleted, a study module gets its progress from before
   *   the session back (new sync epoch, so no merge resurrects it), and a
   *   not-studied flag that answering in this session cleared is put back.
   */
  const NK_AB_KEEP=200,NK_AB_SESSION_ID=/^[A-Za-z0-9_.:-]{1,160}$/;
  function nkAbList(){if(!Array.isArray(state.abandonedSessions))state.abandonedSessions=[];return state.abandonedSessions;}
  function nkAbClean(raw){
    if(!raw||typeof raw!=='object')return null;
    const sessionId=String(raw.sessionId||'');if(!NK_AB_SESSION_ID.test(sessionId))return null;
    const num=v=>Math.max(0,Math.trunc(Number(v)||0)),at=num(raw.abandonedAt)||num(raw.updatedAt);if(!at)return null;
    const mode=raw.mode==='exam'?'exam':'practice',kind=['practice','test','revision','module','review'].includes(raw.kind)?raw.kind:mode==='exam'?'test':'practice';
    return {id:`abandoned_${sessionId}`,sessionId,title:String(raw.title||'').slice(0,120),mode,kind,subject:String(raw.subject||'').slice(0,60),
      total:num(raw.total),answered:num(raw.answered),startedAt:num(raw.startedAt),abandonedAt:at,updatedAt:Math.max(at,num(raw.updatedAt))};
  }
  // Abandoned session IDs, cached per list (the list only ever grows or is replaced).
  let nkAbCache={list:null,sig:'',ids:new Set()};
  function nkAbIds(){
    const list=Array.isArray(state?.abandonedSessions)?state.abandonedSessions:[];
    const sig=list.length+':'+(list[0]?.sessionId||'')+':'+(list[list.length-1]?.sessionId||'');
    if(nkAbCache.list!==list||nkAbCache.sig!==sig)nkAbCache={list,sig,ids:new Set(list.map(e=>String(e?.sessionId||'')).filter(Boolean))};
    return nkAbCache.ids;
  }
  function nkAbIsAbandoned(sessionId){return Boolean(sessionId)&&nkAbIds().has(String(sessionId));}

  // Every measure reads active attempts through this one function.
  const nkAbOriginalActive=nkFsrsActiveAttempts;
  nkFsrsActiveAttempts=function(qid){
    const list=nkAbOriginalActive.apply(this,arguments),ids=nkAbIds();
    if(!ids.size||!list.some(a=>a?.sessionId&&ids.has(String(a.sessionId))))return list;
    return list.filter(a=>!(a?.sessionId&&ids.has(String(a.sessionId))));
  };

  function nkAbSessionKind(s){
    if(s?.mode==='exam')return 'test';
    if(s?.studyModuleId)return 'module';
    if(typeof nkRevisionSessionKind==='function'&&nkRevisionSessionKind(s))return 'revision';
    const origin=[s?.originRoute,s?.context,s?.title].filter(Boolean).join(' ').toLowerCase();
    return /(fsrs|spaced|review)/.test(origin)?'review':'practice';
  }
  function nkAbSessionIds(s){return [...new Set([...(s?.sessionQuestionIds||[]),...(s?.questionIds||[])].map(String))];}
  function nkAbCanAbandon(s){
    if(!s||!['practice','exam'].includes(s.mode)||s.__terminalSaveInFlight)return false;
    if(['submitted','completed','discarded'].includes(String(s.lifecycle||'')))return false;
    return !s.scheduledMockId;
  }
  function nkAbQuestion(id){return BY_ID?.[String(id)]||(typeof nkFindStudyQuestion==='function'?nkFindStudyQuestion(String(id)):null);}

  // Study modules mirror their session on every save, so the progress a module had
  // when this session began is kept on the session to give back on abandon.
  function nkAbModuleProgress(module){return {answers:{...(module?.answers||{})},submitted:{...(module?.submitted||{})},questionTimes:{...(module?.questionTimes||{})},currentPosition:Number(module?.currentPosition||0),completedQuestionIds:[...(module?.completedQuestionIds||[])].map(String)};}
  if(typeof startStudyModule==='function'){
    const nkAbOriginalStartModule=startStudyModule;
    startStudyModule=function(id){
      const module=typeof nkFindStudyModule==='function'?nkFindStudyModule(id):null,base=module?nkAbModuleProgress(module):null;
      const result=nkAbOriginalStartModule.apply(this,arguments),s=state.activeSession;
      if(base&&s?.studyModuleId&&String(s.studyModuleId)===String(module.id)&&!s.abandonBase){s.abandonBase={module:base};saveState();}
      return result;
    };
  }
  function nkAbRestoreModule(s,undone,now){
    const module=typeof nkFindStudyModule==='function'?nkFindStudyModule(s.studyModuleId):null;if(!module)return false;
    const base=s.abandonBase?.module;
    if(base)Object.assign(module,JSON.parse(JSON.stringify(base)));
    else{
      // A session that began before this version: drop what this session answered.
      undone.forEach(id=>{delete module.answers?.[id];delete module.submitted?.[id];delete module.questionTimes?.[id];});
      module.completedQuestionIds=(module.completedQuestionIds||[]).map(String).filter(id=>!undone.has(id));
    }
    module.completedAt=null;module.isCompleted=false;module.resultTestId=null;
    // Module sync unions progress within one epoch; a new epoch makes the restored copy win as a whole.
    module.syncEpoch=`epoch_${now}_${Math.random().toString(36).slice(2)}`;module.updatedAt=now;module.lastOpenedAt=now;
    return true;
  }

  // Not-studied flags (not_studied_flags.js): a flag from elsewhere clears when its
  // question is answered. If this session is abandoned that answer never happened,
  // so the flag is put back. Unflagging by hand stays the learner's choice.
  let nkAbManualFlag=false;
  if(typeof nkToggleNotStudied==='function'&&typeof nkNsClearEarlier==='function'){
    const nkAbOriginalToggle=nkToggleNotStudied,nkAbOriginalClearEarlier=nkNsClearEarlier;
    nkToggleNotStudied=function(){nkAbManualFlag=true;try{return nkAbOriginalToggle.apply(this,arguments);}finally{nkAbManualFlag=false;}};
    nkNsClearEarlier=function(qid){
      const s=state.activeSession,id=String(qid),prior=state.notStudied?.[id];
      if(!nkAbManualFlag&&s&&['practice','exam'].includes(s.mode)&&prior?.on===true){
        s.abandonFlags=s.abandonFlags&&typeof s.abandonFlags==='object'?s.abandonFlags:{};
        if(!s.abandonFlags[id])s.abandonFlags[id]=JSON.parse(JSON.stringify(prior));
      }
      return nkAbOriginalClearEarlier.apply(this,arguments);
    };
  }
  function nkAbRestoreFlags(s){
    let changed=false;
    Object.entries(s?.abandonFlags||{}).forEach(([id,prior])=>{
      const now=state.notStudied?.[id];if(now?.on===true||!prior||prior.on!==true)return;
      const stamp=Math.max(Date.now(),Number(now?.updatedAt||state.notStudiedCleared?.[id]||0)+1);
      state.notStudied=state.notStudied||{};state.notStudied[id]={...prior,updatedAt:stamp};if(state.notStudiedCleared)delete state.notStudiedCleared[id];changed=true;
    });
    return changed;
  }

  // Withdraw every attempt this session recorded (undo events, like the FSRS undo),
  // then rebuild those cards without them. Returns the question IDs touched.
  function nkAbWithdrawAttempts(sessionId,now){
    const sid=String(sessionId),touched=new Set();let stamp=now;
    Object.keys(state.attempts||{}).forEach(qid=>{
      const list=Array.isArray(state.attempts[qid])?state.attempts[qid]:[];
      const undone=new Set(list.filter(a=>a?.isUndo&&a.undoOf).map(a=>String(a.undoOf)));
      const mine=list.filter(a=>a&&!a.isUndo&&!a.isRatingRevision&&String(a.sessionId||'')===sid&&!undone.has(String(a.id)));
      if(!mine.length)return;
      mine.forEach(a=>{stamp=Math.max(stamp+1,Number(a.at||0)+1);list.push({id:`undo_${stamp}_${Math.random().toString(16).slice(2)}`,isUndo:true,undoOf:a.id,at:stamp,reason:'abandoned',...(typeof NK_FSRS_VERSION!=='undefined'?{schedulerVersion:NK_FSRS_VERSION}:{})});});
      touched.add(String(qid));
      const first=mine.slice().sort((a,b)=>Number(a.reviewedAt||a.at||0)-Number(b.reviewedAt||b.at||0))[0];
      if(typeof nkFsrsReplay==='function'){
        const review=nkFsrsReplay(String(qid),false);
        // A card migrated from the old scheduler kept its old due date until a new-scheduler
        // answer replaced it; give that date back when only old answers remain.
        const legacyDue=Number(first?.schedulerBefore?.due||0);
        if(review&&legacyDue&&!nkFsrsActiveAttempts(String(qid)).some(a=>typeof NK_FSRS_VERSION!=='undefined'&&a.schedulerVersion===NK_FSRS_VERSION)){review.due=legacyDue;review.nextReviewAt=legacyDue;review.legacyDueOverride=legacyDue;}
      }
    });
    return touched;
  }
  function nkAbHistoryEntry(s,now){
    const ids=nkAbSessionIds(s),answered=ids.filter(id=>s.answers?.[id]||(Array.isArray(s.roundHistory?.[id])&&s.roundHistory[id].some(r=>r?.submitted))).length,first=nkAbQuestion(ids[0]);
    return nkAbClean({sessionId:String(s.id),title:s.practiceContext?.title||s.title||(s.mode==='exam'?'Timed test':'Practice'),mode:s.mode,kind:nkAbSessionKind(s),
      subject:first?.bank==='UWorld'?'My UWorld':String(first?.subject||''),total:ids.length,answered,startedAt:Number(s.startedAt||0),abandonedAt:now,updatedAt:now});
  }
  function nkAbAddEntry(entry){
    if(!entry)return false;const list=nkAbList(),index=list.findIndex(e=>String(e?.sessionId)===entry.sessionId);
    if(index>=0){if(Number(list[index].updatedAt||0)>=entry.updatedAt)return false;list[index]=entry;}
    else list.push(entry);
    list.sort((a,b)=>Number(a.abandonedAt||0)-Number(b.abandonedAt||0));
    if(list.length>NK_AB_KEEP)list.splice(0,list.length-NK_AB_KEEP);
    return true;
  }
  function nkAbDestination(s){
    if(s.mode==='exam')return 'tests';
    if(s.studyModuleId)return 'dashboard';
    if(typeof nkRevisionSessionKind==='function'&&nkRevisionSessionKind(s))return 'quick-revision';
    const origin=String(s.originRoute||'');
    return ['topics','dashboard','study-library','notes','question-search','quick-revision','fsrs','tests'].includes(origin)?origin:'dashboard';
  }
  // The single place a session is abandoned. Confirmation happens before this.
  function nkAbandonCommit(s,options={}){
    if(!nkAbCanAbandon(s)||state.activeSession!==s)return false;
    const before=typeof nkStateClone==='function'?nkStateClone(state):JSON.parse(JSON.stringify(state)),now=Date.now(),sid=String(s.id);
    const entry=nkAbHistoryEntry(s,now);if(!entry)return false;
    nkAbAddEntry(entry);
    const touched=nkAbWithdrawAttempts(sid,now);
    // A pending recall rating is part of the session and goes with it.
    if(state.notStudiedHeld)Object.keys(state.notStudiedHeld).forEach(id=>{if(String(state.notStudiedHeld[id]?.session)===sid)delete state.notStudiedHeld[id];});
    nkAbRestoreFlags(s);
    // Clear the session before saving: saving a module session mirrors it back into the module.
    state.activeSession=null;
    if(s.studyModuleId)nkAbRestoreModule(s,touched,now);
    if(s.mode==='practice'&&typeof nkPracticeFindCheckpoint==='function'&&typeof nkPracticeStoreCheckpoint==='function'){
      const cp=nkPracticeFindCheckpoint(sid);
      if(cp)nkPracticeStoreCheckpoint({...cp,lifecycle:'discarded',abandonedAt:now,discardedAt:now,terminalAt:now,updatedAt:now});
    }
    if(saveState()===false){state=before;return false;}
    nkAbCloseSheet();
    if(typeof closeQuestionNavigator==='function')closeQuestionNavigator();
    if(typeof closeSessionReview==='function')closeSessionReview();
    if(options.navigate!==false){
      navigate(nkAbDestination(s));
      showToast(s.mode==='exam'?'Test abandoned. Nothing from it was saved.':'Session abandoned. Nothing from it was saved.');
    }
    return true;
  }

  // ── Confirmation ──
  // Android shell: a native AlertDialog through QBankShell.confirmAction (newer
  // shells). Everywhere else (PWA, browsers, older shells): an in-app alert sheet.
  function nkAbHaptic(kind){try{window.NKFeel?.haptics?.(kind);}catch(_){}}
  function nkAbCopy(s){
    const exam=s.mode==='exam',ids=nkAbSessionIds(s),answered=ids.filter(id=>s.answers?.[id]||(Array.isArray(s.roundHistory?.[id])&&s.roundHistory[id].some(r=>r?.submitted))).length;
    return {title:exam?'Abandon this test?':'Abandon this session?',
      body:`Your answers won’t be saved or counted. Nothing from this ${exam?'test':'session'} reaches your reviews, mistakes or stats.`,
      meta:`${answered} of ${ids.length} answered`,confirm:'Abandon',cancel:'Cancel'};
  }
  let nkAbPending=null,nkAbReturnFocus=null;
  function nkAbNativeShell(){
    try{const shell=window.QBankShell;return shell&&typeof shell.confirmAction==='function'&&typeof shell.platform==='function'&&shell.platform()==='android'?shell:null;}catch(_){return null;}
  }
  function nkAbandonSession(){
    const s=state.activeSession;
    if(s?.scheduledMockId){showToast('A scheduled mock can’t be abandoned. Submit it when you are done.','bad');return false;}
    if(!nkAbCanAbandon(s))return false;
    const copy=nkAbCopy(s),requestId=`ab${Date.now().toString(36)}${Math.random().toString(36).slice(2,8)}`;
    nkAbPending={requestId,sessionId:String(s.id)};
    const shell=nkAbNativeShell();
    if(shell){
      try{if(shell.confirmAction(requestId,copy.title,`${copy.body}\n\n${copy.meta}.`,copy.confirm,copy.cancel)!==false)return true;}catch(_){}
    }
    nkAbOpenSheet(s,copy,requestId);return true;
  }
  // Answer from the native dialog or the sheet.
  function nkAbandonAnswer(requestId,confirmed){
    const pending=nkAbPending;
    if(!pending||String(pending.requestId)!==String(requestId))return false;
    nkAbPending=null;
    const s=state.activeSession;
    if(!confirmed||!s||String(s.id)!==pending.sessionId){nkAbCloseSheet(true);return false;}
    nkAbHaptic('impact');
    return nkAbandonCommit(s);
  }
  function nkAbIcon(size=20){return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="m9.2 9.2 5.6 5.6M14.8 9.2l-5.6 5.6"/></svg>`;}
  function nkAbOpenSheet(s,copy,requestId){
    if(typeof document==='undefined'||!document.body)return false;
    document.getElementById('nk-abandon-confirm')?.remove();
    nkAbReturnFocus=document.activeElement||null;
    const arg=esc(JSON.stringify(String(requestId)));
    document.body.insertAdjacentHTML('beforeend',`<div class="nk-abandon-backdrop" id="nk-abandon-confirm" onclick="if(event.target===this)window.QB.nkAbandonAnswer(${arg},false)"><section class="nk-abandon-dialog" role="alertdialog" aria-modal="true" aria-labelledby="nk-abandon-title" aria-describedby="nk-abandon-body"><span class="nk-abandon-mark" aria-hidden="true">${nkAbIcon(22)}</span><h2 id="nk-abandon-title">${esc(copy.title)}</h2><p id="nk-abandon-body">${esc(copy.body)}</p><p class="nk-abandon-meta">${esc(copy.meta)}</p><div class="nk-abandon-actions"><button type="button" class="nk-abandon-cancel" onclick="window.QB.nkAbandonAnswer(${arg},false)">${esc(copy.cancel)}</button><button type="button" class="nk-abandon-go" onclick="window.QB.nkAbandonAnswer(${arg},true)">${esc(copy.confirm)}</button></div></section></div>`);
    const root=document.getElementById('nk-abandon-confirm');
    root?.addEventListener('keydown',event=>{
      if(event.key==='Escape'){event.preventDefault();event.stopPropagation();nkAbandonAnswer(requestId,false);return;}
      if(event.key!=='Tab')return;
      const buttons=[...root.querySelectorAll('button')];if(!buttons.length)return;
      const first=buttons[0],last=buttons[buttons.length-1];
      if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
      else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    });
    // Cancel is the safe default.
    root?.querySelector('.nk-abandon-cancel')?.focus({preventScroll:true});
    nkAbHaptic('toggle');
    return true;
  }
  function nkAbCloseSheet(restoreFocus=false){
    const root=typeof document!=='undefined'?document.getElementById?.('nk-abandon-confirm'):null;if(!root)return;
    root.remove();
    if(restoreFocus&&nkAbReturnFocus&&document.contains?.(nkAbReturnFocus))try{nkAbReturnFocus.focus({preventScroll:true});}catch(_){}
    nkAbReturnFocus=null;
  }

  // ── Placement: a quiet destructive row at the foot of the session sheets ──
  // The review sheet (header Back, and the grid icon in Practice) and the question
  // navigator (grid icon in tests and the other modes) are where a session is ended,
  // so Abandon sits there, under the Pause/Submit decisions and apart from them.
  function nkAbTrigger(s){
    const label=s.mode==='exam'?'Abandon test':'Abandon session';
    return `<div class="nk-abandon-row"><button type="button" class="nk-abandon-trigger" onclick="window.QB.nkAbandonSession()">${nkAbIcon(17)}<span>${label}</span></button></div>`;
  }
  function nkAbAppend(root,selector){
    const s=state.activeSession;if(!root||!nkAbCanAbandon(s))return false;
    const host=root.querySelector(selector);if(!host||host.querySelector('.nk-abandon-row'))return false;
    host.insertAdjacentHTML('beforeend',nkAbTrigger(s));return true;
  }
  const nkAbOriginalReview=openSessionReview;
  openSessionReview=function(){
    const result=nkAbOriginalReview.apply(this,arguments);
    nkAbAppend(document.getElementById('nk-session-review'),'.nk-session-review-card');
    return result;
  };
  const nkAbOriginalNavigator=openQuestionNavigator;
  openQuestionNavigator=function(){
    const result=nkAbOriginalNavigator.apply(this,arguments);
    if(state.activeSession?.mode!=='review')nkAbAppend(document.getElementById('qb-question-navigator'),'.qb-nav-panel');
    return result;
  };
  // Kept for the scheduled-mock guard (scheduled_mocks.js wraps it) and older callers.
  function nkAbandonTimedTest(){return state.activeSession?.mode==='exam'?nkAbandonSession():false;}

  // "Timed test in progress" (starting another session): its Abandon choice is already
  // a confirmation, so the test is abandoned straight away and recorded the same way.
  if(typeof nkResolveTimedSession==='function'){
    const nkAbOriginalResolve=nkResolveTimedSession;
    nkResolveTimedSession=function(choice){
      const s=state.activeSession;
      if(choice==='abandon'&&s?.mode==='exam'&&nkAbCanAbandon(s)&&!nkAbandonCommit(s,{navigate:false}))return false;
      return nkAbOriginalResolve.apply(this,arguments);
    };
  }
  // An abandoned session never comes back: not from a checkpoint, not through sync.
  if(typeof nkPracticeSessionFromCheckpoint==='function'){
    const nkAbOriginalFromCheckpoint=nkPracticeSessionFromCheckpoint;
    nkPracticeSessionFromCheckpoint=function(cp){return cp&&nkAbIsAbandoned(cp.sessionId)?null:nkAbOriginalFromCheckpoint.apply(this,arguments);};
  }
  if(typeof nkPracticeCheckpoints==='function'){
    const nkAbOriginalCheckpoints=nkPracticeCheckpoints;
    nkPracticeCheckpoints=function(includeTerminal=false){
      const list=nkAbOriginalCheckpoints.apply(this,arguments);
      return includeTerminal?list:list.filter(cp=>!nkAbIsAbandoned(cp?.sessionId));
    };
  }
  // A remote entry: record it; a session still open here ends; its checkpoint becomes terminal.
  function nkAbMergeEntry(raw){
    const entry=nkAbClean(raw);if(!entry||!nkAbAddEntry(entry))return false;
    if(state.activeSession&&String(state.activeSession.id)===entry.sessionId)state.activeSession=null;
    if(typeof nkPracticeFindCheckpoint==='function'&&typeof nkPracticeStoreCheckpoint==='function'){
      const cp=nkPracticeFindCheckpoint(entry.sessionId);
      if(cp&&!['submitted','completed','discarded'].includes(String(cp.lifecycle)))nkPracticeStoreCheckpoint({...cp,lifecycle:'discarded',abandonedAt:entry.abandonedAt,discardedAt:entry.abandonedAt,terminalAt:entry.abandonedAt,updatedAt:Math.max(Date.now(),Number(cp.updatedAt||0)+1)});
    }
    return true;
  }
  if(typeof nkApplyCloudEnvelope==='function'){
    const nkAbOriginalApply=nkApplyCloudEnvelope;
    nkApplyCloudEnvelope=function(){
      const result=nkAbOriginalApply.apply(this,arguments);
      if(state.activeSession&&nkAbIsAbandoned(state.activeSession.id))state.activeSession=null;
      return result;
    };
  }

  // ── History: abandoned sessions sit in the session lists with an "Abandoned" badge ──
  function nkAbandonedEntries(filter){return nkAbList().map(nkAbClean).filter(Boolean).filter(e=>!filter||filter(e)).sort((a,b)=>b.abandonedAt-a.abandonedAt);}
  function nkAbandonedRow(e){
    const exam=e.mode==='exam',meta=[exam?'Timed test':e.kind==='module'?'Study module':e.kind==='revision'?'Revision':e.kind==='review'?'Review':'Practice',`${fmtNum(e.answered)} of ${fmtNum(e.total)} answered`,fmtDate(e.abandonedAt,false)].join(' · ');
    return `<div class="nk-test-row is-abandoned" role="group" aria-label="${esc(`${e.title||'Session'}, abandoned, ${meta}`)}"><span class="nk-test-icon ${exam?'is-cbt':'is-practice'}">${navIcon(exam?'test':'book',18)}</span><span class="nk-test-main"><strong>${esc(e.title||(exam?'Timed test':'Practice'))}</strong><small>${esc(meta)}</small></span><span class="nk-abandoned-badge">Abandoned</span></div>`;
  }
  // Rows for a mixed list of saved results and abandoned entries, newest first.
  function nkSessionHistoryRows(tests,entries){
    return [...(tests||[]).map(t=>({at:Number(t.createdAt||0),html:()=>testRow(t)})),...(entries||[]).map(e=>({at:e.abandonedAt,html:()=>nkAbandonedRow(e)}))].sort((a,b)=>b.at-a.at);
  }

  // ── System Back during a session asks to abandon it ──
  // nkSessionBackTarget: the session system Back belongs to (live, not paused, on its own
  // route). Scheduled mocks are not abandonable and keep the existing exit warning.
  function nkSessionBackTarget(){
    const s=state.activeSession;
    if(!s||!['practice','exam'].includes(s.mode)||s.lifecycle==='paused')return null;
    return route.page===s.mode&&parseHash().page===s.mode?s:null;
  }
  // One Back press: cancel an open abandon dialog, else close a sheet or viewer, else ask.
  // Returns 'handled', the session mode when the old exit warning applies, or '' to leave.
  // The Android shell calls this from MainActivity.onBackPressed.
  function nkSessionBack(){
    if(nkAbPending&&typeof document!=='undefined'&&document.getElementById?.('nk-abandon-confirm')){nkAbandonAnswer(nkAbPending.requestId,false);return 'handled';}
    const s=nkSessionBackTarget();if(!s)return '';
    const overlay=typeof nkSessionBackOverlay==='function'?nkSessionBackOverlay():null;
    if(overlay){overlay();return 'handled';}
    if(nkAbCanAbandon(s)&&nkAbandonSession())return 'handled';
    return s.mode;
  }
  // Browser / PWA: a guard history entry (same URL, state {nkSessionGuard:id}) sits on top
  // while a session is live, so system Back pops the guard instead of leaving. The page
  // puts it back and asks. When the session ends (submit, pause, abandon, any navigation
  // away) the guard is popped before that navigation runs, so history is exactly what it
  // was without the guard: nothing doubled, nothing lost. The Android shell answers Back
  // natively (QBankShell), so no guard is pushed there.
  let nkGuardTop=null,nkGuardHeld=null,nkGuardHeldTimer=0,nkGuardSilent=false;
  function nkGuardHistory(){return typeof window!=='undefined'&&window.history&&typeof window.history.pushState==='function'&&typeof window.addEventListener==='function';}
  function nkGuardWanted(){
    if(!nkGuardHistory()||window.QBankShell||location.hostname==='qbank.local')return null;
    const s=nkSessionBackTarget();return s&&nkAbCanAbandon(s)?s:null;
  }
  function nkGuardState(){try{return history.state&&history.state.nkSessionGuard?String(history.state.nkSessionGuard):null;}catch(_){return null;}}
  function nkBackGuardSync(){
    if(!nkGuardHistory()||nkGuardHeld||nkGuardSilent)return;
    const s=nkGuardWanted(),top=nkGuardState();
    try{
      if(s){
        if(top===String(s.id))return;
        if(top)history.replaceState({nkSessionGuard:String(s.id)},'',location.href);
        else history.pushState({nkSessionGuard:String(s.id)},'',location.href);
        nkGuardTop=String(s.id);
      }else if(top&&!(state.activeSession&&String(state.activeSession.id)===top))nkGuardDropLater();
    }catch(_){}
  }
  // The session ended without leaving its page (e.g. abandoned on another device): drop
  // the guard quietly. Checked a tick later, because a page that renders before it sets
  // its URL (Review Solutions replaces the entry right after rendering) is moving on, and
  // a guard it replaced is gone already.
  let nkGuardDropTimer=0;
  function nkGuardDropLater(){
    clearTimeout(nkGuardDropTimer);
    nkGuardDropTimer=setTimeout(()=>{
      if(nkGuardHeld||nkGuardSilent)return;
      const top=nkGuardState();if(!top||nkGuardWanted())return;
      if(state.activeSession&&String(state.activeSession.id)===top)return;
      if(!['practice','exam'].includes(parseHash().page))return;
      try{nkGuardSilent=true;history.back();}catch(_){nkGuardSilent=false;}
    },0);
  }
  // Called first thing by the page's navigate(): hold a navigation off the session page
  // until the guard entry is popped. Returns true when held.
  function nkBackGuardHold(page,id){
    if(!nkGuardHistory()||!nkGuardState())return false;
    if(page===route.page&&['practice','exam'].includes(page))return false;
    const first=!nkGuardHeld;nkGuardHeld=[page,id];
    if(first){
      try{history.back();}catch(_){nkGuardHeld=null;return false;}
      // A popstate that never arrives must not swallow the navigation.
      clearTimeout(nkGuardHeldTimer);nkGuardHeldTimer=setTimeout(()=>{if(!nkGuardHeld)return;const held=nkGuardHeld;nkGuardHeld=null;nkGuardTop=nkGuardState();nkNavigateBase(...held);},500);
    }
    return true;
  }
  function nkBackGuardPop(event){
    const wasGuard=nkGuardTop;nkGuardTop=nkGuardState();
    if(nkGuardHeld){
      const held=nkGuardHeld;nkGuardHeld=null;clearTimeout(nkGuardHeldTimer);
      event?.stopImmediatePropagation?.();
      if(nkGuardTop){nkGuardHeld=held;try{history.back();}catch(_){nkGuardHeld=null;nkNavigateBase(...held);}return;}
      nkNavigateBase(...held);return;
    }
    if(nkGuardSilent){nkGuardSilent=false;event?.stopImmediatePropagation?.();return;}
    // Only a press that popped the guard and stayed on the session's URL is ours.
    if(!wasGuard||nkGuardTop||parseHash().page!==route.page)return;
    event?.stopImmediatePropagation?.();
    const s=nkGuardWanted();
    // The guarded session is gone (or paused): this Back press goes on to the previous page.
    if(!s){try{history.back();}catch(_){}return;}
    // Put the guard back first, then act: Cancel leaves the learner exactly where they were.
    try{history.pushState({nkSessionGuard:String(s.id)},'',location.href);nkGuardTop=String(s.id);}catch(_){}
    nkSessionBack();
  }
  if(nkGuardHistory()){
    nkGuardTop=nkGuardState();
    window.addEventListener('popstate',nkBackGuardPop,true);
    const nkAbOriginalRender=render;
    render=function(){const out=nkAbOriginalRender.apply(this,arguments);nkBackGuardSync();return out;};
  }
  /* NK_SESSION_ABANDON_V1_END */
