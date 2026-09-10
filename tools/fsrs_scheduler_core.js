  /* NK_FSRS_V6_START — shared offline scheduler, queue, migration and UI. */
  const NK_FSRS_BACKUP_KEY='qbank_pre_fsrs_backup_v1';
  const NK_FSRS_VERSION='fsrs6';
  const NK_FSRS_DAY=86400000;
  const NK_FSRS_DEFAULTS={desiredRetention:.90,dailyCap:150,maximumInterval:365};
  const nkFsrsAllQuestions=()=>typeof nkAllBankQuestions==='function'?nkAllBankQuestions():SUBJECTS.flatMap(subject=>(subject.questions||[]).map(q=>({...q,subject:q.subject||subject.subject})));
  const nkFsrsAllById=()=>Object.fromEntries(nkFsrsAllQuestions().map(q=>[String(q.id),q]));
  function nkFsrsPreferences(){
    const raw=state.fsrsPreferences||{};
    return state.fsrsPreferences={
      desiredRetention:Math.min(.97,Math.max(.80,Number(raw.desiredRetention||NK_FSRS_DEFAULTS.desiredRetention))),
      dailyCap:Math.min(300,Math.max(20,Math.round(Number(raw.dailyCap||NK_FSRS_DEFAULTS.dailyCap)))),
      maximumInterval:Math.min(3650,Math.max(30,Math.round(Number(raw.maximumInterval||NK_FSRS_DEFAULTS.maximumInterval))))
    };
  }
  function nkFsrsEngine(preferences){
    const p=preferences||nkFsrsPreferences();
    if(!window.FSRS?.fsrs)throw new Error('The offline FSRS scheduler is unavailable.');
    return window.FSRS.fsrs({request_retention:p.desiredRetention,maximum_interval:p.maximumInterval,enable_fuzz:false,enable_short_term:true,learning_steps:['10m'],relearning_steps:['10m']});
  }
  function nkFsrsCardFromReview(review,now=Date.now()){
    if(!review||review.schemaVersion!==2)return window.FSRS.createEmptyCard(new Date(now));
    return {due:new Date(Number(review.due||review.nextReviewAt||now)),stability:Number(review.stability||0),difficulty:Number(review.difficulty||0),elapsed_days:Number(review.elapsedDays||0),scheduled_days:Number(review.scheduledDays||0),reps:Number(review.repetitions||0),lapses:Number(review.lapses||0),learning_steps:Number(review.learningSteps||0),state:Number(review.state||0),last_review:review.lastReview?new Date(Number(review.lastReview)):undefined};
  }
  function nkFsrsCardSnapshot(card,extra={}){
    return {schemaVersion:2,schedulerVersion:NK_FSRS_VERSION,due:new Date(card.due).getTime(),nextReviewAt:new Date(card.due).getTime(),stability:Number(card.stability||0),difficulty:Number(card.difficulty||0),state:Number(card.state||0),repetitions:Number(card.reps||0),lapses:Number(card.lapses||0),elapsedDays:Number(card.elapsed_days||0),scheduledDays:Number(card.scheduled_days||0),learningSteps:Number(card.learning_steps||0),lastReview:card.last_review?new Date(card.last_review).getTime():null,...extra};
  }
  function nkFsrsRating(attempt){return [1,2,3,4].includes(Number(attempt?.rating))?Number(attempt.rating):(attempt?.correct?3:1);}
  function nkFsrsActiveAttempts(qid){
    const list=Array.isArray(state.attempts?.[qid])?state.attempts[qid]:[],undone=new Set(list.filter(a=>a?.isUndo&&a.undoOf).map(a=>String(a.undoOf)));
    return list.filter(a=>a&&!a.isUndo&&!undone.has(String(a.id))).sort((a,b)=>Number(a.reviewedAt||a.at||0)-Number(b.reviewedAt||b.at||0)||String(a.id||'').localeCompare(String(b.id||'')));
  }
  function nkFsrsEligibility(q){
    const id=String(q?.id||''),history=nkFsrsActiveAttempts(id);
    if(history.some(a=>a?.correct===false))return 'wrong';
    if(state.fsrsReviewEligible?.[id]?.reason==='skipped')return 'skipped';
    return '';
  }
  function nkFsrsReplay(qid,preserveLegacyDue=false){
    const attempts=nkFsrsActiveAttempts(qid); if(!attempts.length){delete state.reviews[qid];return null;}
    const old=state.reviews[qid],firstAt=Number(attempts[0].reviewedAt||attempts[0].at||Date.now());
    let card=window.FSRS.createEmptyCard(new Date(firstAt));
    attempts.forEach(a=>{const at=Number(a.reviewedAt||a.at||firstAt);card=nkFsrsEngine(a.schedulerPreferences||NK_FSRS_DEFAULTS).next(card,new Date(at),nkFsrsRating(a)).card;});
    const rated=attempts.some(a=>a.schedulerVersion===NK_FSRS_VERSION);
    const legacyDue=rated?0:(preserveLegacyDue&&old?.nextReviewAt?Number(old.nextReviewAt):Number(old?.legacyDueOverride||0));
    const review=nkFsrsCardSnapshot(card,{migratedAt:Number(old?.migratedAt||firstAt),legacyDueOverride:legacyDue||null,needsAttention:Number(card.lapses||0)>=6});
    if(legacyDue){review.due=legacyDue;review.nextReviewAt=legacyDue;}
    state.reviews[qid]=review; return review;
  }
  function nkFsrsRebuildAll(preserveLegacy=false){Object.keys(state.attempts||{}).sort().forEach(qid=>nkFsrsReplay(qid,preserveLegacy));}
  function nkFsrsInit(){
    const ids=nkFsrsAllQuestions().map(q=>String(q.id)),unique=new Set(ids);if(ids.length!==unique.size)throw new Error('Today’s Review requires globally unique question IDs.');
    nkFsrsPreferences();
    if(!localStorage.getItem(NK_FSRS_BACKUP_KEY)){const raw=localStorage.getItem(LS_KEY);if(raw)localStorage.setItem(NK_FSRS_BACKUP_KEY,raw);nkFsrsRebuildAll(true);state.fsrsMigratedAt=Date.now();saveState();}
    else if(!state.fsrsMigratedAt){nkFsrsRebuildAll(true);state.fsrsMigratedAt=Date.now();saveState();}
    nkFsrsRecoverPending();
  }
  function nkFsrsPreview(qid,now=Date.now()){
    const card=nkFsrsCardFromReview(state.reviews[qid],now),result=nkFsrsEngine().repeat(card,new Date(now));
    return Object.fromEntries([1,2,3,4].map(r=>[r,result[r]]));
  }
  function nkFsrsRecordAttempt(qid,selected,timeSpent,source='practice',rating,reviewedAt,attemptId){
    const q=nkFsrsAllById()[String(qid)];if(!q||!selected)return false;
    const correct=Number(q.correctOption)===Number(selected),grade=correct&&[2,3,4].includes(Number(rating))?Number(rating):(correct?3:1),now=Number(reviewedAt||Date.now());
    if(attemptId&&(state.attempts[qid]||[]).some(a=>a.id===attemptId))return correct;
    const before=nkFsrsCardFromReview(state.reviews[qid],now),out=nkFsrsEngine().next(before,new Date(now),grade),after=nkFsrsCardSnapshot(out.card);
    const entry={id:attemptId||`${now}_${Math.random().toString(16).slice(2)}`,selected:Number(selected),correct,timeSpent:Math.max(0,Number(timeSpent||0)),at:now,reviewedAt:now,source,rating:grade,ratingLabel:['','Again','Hard','Good','Easy'][grade],schedulerVersion:NK_FSRS_VERSION,schedulerPreferences:{...nkFsrsPreferences()},schedulerBefore:nkFsrsCardSnapshot(before),schedulerAfter:after};
    if(!state.attempts[qid])state.attempts[qid]=[];state.attempts[qid].push(entry);
    state.reviews[qid]={...after,migratedAt:Number(state.reviews[qid]?.migratedAt||state.fsrsMigratedAt||now),legacyDueOverride:null,needsAttention:after.lapses>=6};saveState();return correct;
  }
  function nkFsrsFormatInterval(ms){const m=Math.max(1,Math.round(ms/60000));if(m<60)return `${m}m`;const h=Math.round(m/60);if(h<48)return `${h}h`;const d=Math.round(h/24);if(d<60)return `${d}d`;return `${Math.round(d/30)}mo`;}
  function nkFsrsRatingMarkup(qid){
    const s=state.activeSession,p=s?.pendingRating?.[qid];if(!p)return '';
    const previews=nkFsrsPreview(qid,p.reviewedAt||Date.now());
    const brain='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5a3 3 0 0 0-5.8-1A3.5 3.5 0 0 0 3 9a4 4 0 0 0 0 6 3.5 3.5 0 0 0 3.2 5A3 3 0 0 0 12 19V5Zm0 0a3 3 0 0 1 5.8-1A3.5 3.5 0 0 1 21 9a4 4 0 0 1 0 6 3.5 3.5 0 0 1-3.2 5A3 3 0 0 1 12 19"/><path d="M7 4v4m-4 1h4l2 3m-6 3h4v5m10-16v4m4 1h-4l-2 3m6 3h-4v5"/></svg>';
    return `<div class="nk-fsrs-rating" role="group" aria-label="Rate recall"><div class="nk-fsrs-recall-label"><span class="nk-fsrs-medallion">${brain}</span><span><strong>Rate recall</strong><small>Default: Good</small></span></div>${[2,3,4].map(r=>`<button type="button" class="nk-fsrs-pill ${r===3?'is-default':''}" aria-pressed="${r===3}" title="Review in ${nkFsrsFormatInterval(new Date(previews[r].card.due)-Number(p.reviewedAt||Date.now()))}" onclick="window.QB.nkRateCurrent(${r})">${['','','Hard','Good','Easy'][r]}</button>`).join('')}</div>`;
  }
  function nkFsrsCommitPending(qid,rating=3){
    const s=state.activeSession,p=s?.pendingRating?.[qid];if(!p)return false;
    delete s.pendingRating[qid];nkFsrsRecordAttempt(qid,p.selected,p.timeSpent,p.source,rating,p.reviewedAt,p.id);saveState();return true;
  }
  function nkRateCurrent(rating){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(!qid)return;nkFsrsCommitPending(qid,rating);render();}
  function nkFsrsRecoverPending(){const s=state.activeSession;if(!s?.pendingRating)return;Object.keys(s.pendingRating).forEach(qid=>nkFsrsCommitPending(qid,3));}
  function nkFsrsRetrievability(review,now=Date.now()){try{return nkFsrsEngine().get_retrievability(nkFsrsCardFromReview(review,now),new Date(now),false);}catch(_){return 1;}}
  function nkFsrsQueue(filters={}){
    const now=Date.now(),prefs=nkFsrsPreferences(),all=nkFsrsAllQuestions().filter(q=>(!filters.subject||q.subject===filters.subject)&&(!filters.topic||String(q.chapterId)===String(filters.topic))&&nkFsrsEligibility(q)),due=[];
    all.forEach(q=>{const r=state.reviews[q.id];if(!r||Number(r.nextReviewAt||r.due||0)<=now)due.push(q);});
    due.sort((a,b)=>{const ar=state.reviews[a.id],br=state.reviews[b.id],al=[1,3].includes(Number(ar?.state))?0:1,bl=[1,3].includes(Number(br?.state))?0:1;return al-bl||nkFsrsRetrievability(ar,now)-nkFsrsRetrievability(br,now)||Number(ar?.due||0)-Number(br?.due||0)||String(a.id).localeCompare(String(b.id));});
    const today=new Date(now).toDateString(),seen=new Set();
    nkFsrsAllQuestions().forEach(q=>{const daily=nkFsrsActiveAttempts(q.id).filter(a=>a.schedulerVersion===NK_FSRS_VERSION&&['fsrs-review','spaced-review'].includes(a.source)&&new Date(a.at).toDateString()===today);if(daily.length)seen.add(String(q.id));});
    const repeatIds=new Set(due.filter(q=>seen.has(String(q.id))&&[1,3].includes(Number(state.reviews?.[q.id]?.state))).map(q=>String(q.id)));
    const firstToday=due.filter(q=>!seen.has(String(q.id))),remaining=Math.max(0,prefs.dailyCap-seen.size),admittedIds=new Set(firstToday.slice(0,remaining).map(q=>String(q.id)));
    const cards=due.filter(q=>repeatIds.has(String(q.id))||admittedIds.has(String(q.id)));
    return {cards,due,totalDue:due.length,rolledOver:Math.max(0,firstToday.length-admittedIds.size)};
  }
  function nkFsrsCounts(now=Date.now()){
    const counts={eligible:0,due:0,learning:0,relearning:0,young:0,mature:0,overdue:0,attention:0};
    nkFsrsAllQuestions().forEach(q=>{if(!nkFsrsEligibility(q))return;counts.eligible++;const r=state.reviews[q.id],at=Number(r?.due||r?.nextReviewAt||0);if(!r||at<=now){counts.due++;if(r&&now-at>=NK_FSRS_DAY)counts.overdue++;}if(Number(r?.state)===1)counts.learning++;else if(Number(r?.state)===3)counts.relearning++;else if(r&&Number(r.stability)>=21)counts.mature++;else if(r)counts.young++;if(r?.needsAttention)counts.attention++;});return counts;
  }
  function nkFsrsForecast(){const out=Array(7).fill(0),start=new Date();start.setHours(0,0,0,0);nkFsrsAllQuestions().forEach(q=>{if(!nkFsrsEligibility(q))return;const r=state.reviews[q.id],at=Number(r?.due||r?.nextReviewAt||0);if(!at){out[0]++;return;}const day=Math.floor((at-start.getTime())/NK_FSRS_DAY);if(day<0)out[0]++;else if(day<7)out[day]++;});return out;}
  function nkStartTodaysReview(subject='',topic=''){
    const queue=nkFsrsQueue({subject,topic});if(!queue.cards.length){showToast('No wrong or skipped questions are due for this selection.');return;}
    BY_ID=nkFsrsAllById();startSession(queue.cards.map(q=>q.id),'practice',"Today's Review",'spaced-review');if(queue.rolledOver)showToast(`${queue.rolledOver} due cards roll forward.`);
  }
  function nkFsrsTopicOptions(subject){const item=SUBJECTS.find(s=>s.subject===subject),select=document.getElementById('nk-fsrs-topic');if(!select)return;select.innerHTML='<option value="">All topics</option>'+((item?.topics||[]).map(t=>`<option value="${esc(t.id)}">${esc(t.title||t.name)}</option>`).join(''));}
  function nkFsrsQueueDialog(){navigate('fsrs');}
  function nkFsrsUndo(){
    let hit=null,qid=null;Object.keys(state.attempts||{}).forEach(id=>nkFsrsActiveAttempts(id).forEach(a=>{if(!hit||Number(a.at)>Number(hit.at)){hit=a;qid=id;}}));if(!hit){showToast('Nothing to undo.');return;}
    state.attempts[qid].push({id:`undo_${Date.now()}_${Math.random().toString(16).slice(2)}`,isUndo:true,undoOf:hit.id,at:Date.now(),schedulerVersion:NK_FSRS_VERSION});nkFsrsReplay(qid,false);saveState();showToast('Most recent rating undone.');render();
  }
  function nkFsrsSetPreference(name,value){const p=nkFsrsPreferences(),n=Number(value),bounds={desiredRetention:[80,97],dailyCap:[20,300],maximumInterval:[30,3650]},b=bounds[name];if(!b)return;p[name]=name==='desiredRetention'?Math.min(b[1],Math.max(b[0],n))/100:Math.round(Math.min(b[1],Math.max(b[0],n)));}
  let nkFsrsDraft=null,nkFsrsPendingRoute=null;
  const nkFsrsFields=[['desiredRetention','Desired retention','%',80,97,'How often you aim to remember a card. Higher retention means more reviews.'],['dailyCap','Daily review limit','cards',20,300,'Limits due review work. Excess due questions roll forward.'],['maximumInterval','Longest review interval','days',30,3650,'The maximum gap before a question returns for review.']];
  function nkFsrsReadSettings(){const p=nkFsrsPreferences();return {desiredRetention:String(Math.round(p.desiredRetention*100)),dailyCap:String(p.dailyCap),maximumInterval:String(p.maximumInterval)};}
  function nkFsrsDirty(){return nkFsrsDraft&&JSON.stringify(nkFsrsDraft)!==JSON.stringify(nkFsrsReadSettings());}
  function nkFsrsEditSetting(key,value){if(!nkFsrsDraft)nkFsrsDraft=nkFsrsReadSettings();nkFsrsDraft[key]=value;const status=document.getElementById('nk-fsrs-save-status');if(status)status.textContent=nkFsrsDirty()?'Unsaved changes':'All changes saved';const warning=document.getElementById('nk-fsrs-high-retention');if(warning)warning.hidden=Number(nkFsrsDraft.desiredRetention)<=95;}
  function nkFsrsSaveSettings(){
    if(!nkFsrsDraft)return true;
    if(nkFsrsFields.some(([key,label,unit,min,max])=>!String(nkFsrsDraft[key]).trim()||!Number.isInteger(Number(nkFsrsDraft[key]))||Number(nkFsrsDraft[key])<min||Number(nkFsrsDraft[key])>max)){showToast('Enter a whole number within each displayed range.','bad');document.querySelector('.nk-fsrs-settings input:invalid')?.reportValidity();return false;}
    nkFsrsFields.forEach(([key])=>nkFsrsSetPreference(key,nkFsrsDraft[key]));saveState();nkFsrsDraft=nkFsrsReadSettings();showToast('Review settings saved.','good');render();return true;
  }
  function nkFsrsCancelSettings(){nkFsrsDraft=null;navigate('more');}
  function nkFsrsLeaveSettings(choice){
    if(choice==='stay'){nkFsrsPendingRoute=null;document.getElementById('nk-fsrs-unsaved')?.remove();return;}
    if(choice==='save'&&!nkFsrsSaveSettings())return;
    const next=nkFsrsPendingRoute||{page:'more'};nkFsrsPendingRoute=null;nkFsrsDraft=null;document.getElementById('nk-fsrs-unsaved')?.remove();navigate(next.page,next.id);
  }
  function nkFsrsAskToLeave(next){
    nkFsrsPendingRoute=next;if(document.getElementById('nk-fsrs-unsaved'))return;
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop" id="nk-fsrs-unsaved"><section class="modal card" role="dialog" aria-modal="true" aria-labelledby="nk-fsrs-unsaved-title"><h2 id="nk-fsrs-unsaved-title">Save your changes?</h2><p>Your review preferences have unsaved changes.</p><div class="nk-fsrs-leave-actions"><button class="primary-btn" onclick="window.QB.nkFsrsLeaveSettings('save')">Save and leave</button><button class="ghost-btn" onclick="window.QB.nkFsrsLeaveSettings('discard')">Discard changes</button><button class="ghost-btn" onclick="window.QB.nkFsrsLeaveSettings('stay')">Keep editing</button></div></section></div>`);
    document.querySelector('#nk-fsrs-unsaved button')?.focus();
  }
  function nkFsrsGuardRoute(){
    if(nkFsrsDraft&&route.page!=='fsrs-settings'){
      if(nkFsrsDirty()){const next={...route};history.replaceState(null,'','#fsrs-settings');route={page:'fsrs-settings'};nkFsrsAskToLeave(next);return true;}
      nkFsrsDraft=null;
    }return false;
  }
  function nkFsrsSettingsMarkup(){
    if(!nkFsrsDraft)nkFsrsDraft=nkFsrsReadSettings();
    const field=([key,label,unit,min,max,help])=>`<label class="nk-fsrs-field" for="fsrs-${key}"><span><strong>${label}</strong><small id="fsrs-${key}-help">${help}</small><em>${min}–${max} ${unit}</em></span><span class="nk-fsrs-value"><input id="fsrs-${key}" aria-describedby="fsrs-${key}-help" type="number" inputmode="numeric" required step="1" min="${min}" max="${max}" value="${esc(nkFsrsDraft[key])}" oninput="window.QB.nkFsrsEditSetting('${key}',this.value)"><b>${unit}</b></span></label>`;
    return shell(`<div class="nk-app-v114 nk-fsrs-customization nk-fsrs-settings"><button class="nk-back-link" onclick="window.QB.nav('more')">${navIcon('back',18)} More</button><header class="nk-fsrs-settings-hero"><span class="nk-fsrs-settings-mark">${navIcon('clock',28)}</span><div class="nk-kicker">MAKE IT YOURS</div><h1>Your review rhythm</h1><p>Build lasting recall at a pace that works for you.</p></header><section class="nk-fsrs-settings-section"><header><span>01</span><div><h2>Memory goal</h2><p>Balance confidence and workload</p></div></header>${field(nkFsrsFields[0])}<p id="nk-fsrs-high-retention" class="nk-fsrs-warning" ${Number(nkFsrsDraft.desiredRetention)<=95?'hidden':''}>Above 95% can increase your review workload sharply.</p></section><section class="nk-fsrs-settings-section"><header><span>02</span><div><h2>Daily pace</h2><p>Keep review work bounded</p></div></header>${field(nkFsrsFields[1])}</section><section class="nk-fsrs-settings-section"><header><span>03</span><div><h2>Long-term recall</h2><p>Keep knowledge within reach</p></div></header>${field(nkFsrsFields[2])}</section><p class="nk-fsrs-settings-note">FSRS schedules only questions you got wrong or encountered and skipped. Unseen questions are never introduced here.</p><button class="nk-text-link" onclick="window.QB.nkFsrsUndo()">Undo most recent rating</button><footer class="nk-fsrs-settings-save"><small id="nk-fsrs-save-status" role="status">${nkFsrsDirty()?'Unsaved changes':'All changes saved'}</small><div><button class="ghost-btn" onclick="window.QB.nkFsrsCancelSettings()">Cancel</button><button class="primary-btn" onclick="window.QB.nkFsrsSaveSettings()">Save changes</button></div></footer></div>`,'more');
  }
  const nkFsrsOriginalMore=morePage;morePage=function(){return nkFsrsOriginalMore().replace('</main>',`<button class="nk-fsrs-settings-entry" onclick="window.QB.nav('fsrs-settings')"><span class="nk-fsrs-settings-mark">${navIcon('clock',24)}</span><span><strong>FSRS customization</strong><small>Your memory goal, daily review cap and review intervals</small></span>${navIcon('chevron',20)}</button></main>`);};
  const nkFsrsOriginalActionBar=practiceActionBar;
  practiceActionBar=function(){
    const out=nkFsrsOriginalActionBar.apply(this,arguments),s=state.activeSession,qid=s?.questionIds?.[s.index],markup=qid?nkFsrsRatingMarkup(qid):'';
    if(!markup||s?.mode!=='practice')return out;
    return out.replace('nk-session-footer','nk-session-footer nk-fsrs-docked').replace('<div class="fixed-actions-inner">',markup+'<div class="fixed-actions-inner">');
  };
  function nkFsrsSessionAttemptSource(s){const origin=String(s?.originRoute||'');if(origin==='fsrs'||origin==='spaced-review')return'fsrs-review';return s?.studyModuleId?'study-module':'practice';}
  const nkFsrsOriginalSubmitPractice=submitPractice;submitPractice=function(){const s=state.activeSession;if(!s||s.mode!=='practice')return;const q=nkFsrsAllById()[s.questionIds[s.index]];if(!q||s.submitted[q.id])return;const sel=s.answers[q.id];if(!sel)return;savePracticeElapsed();s.submitted[q.id]=true;const correct=Number(q.correctOption)===Number(sel),source=nkFsrsSessionAttemptSource(s);haptic(correct?[16,18,16]:[10,32,10]);if(correct){s.pendingRating=s.pendingRating||{};s.pendingRating[q.id]={id:`pending_${Date.now()}_${Math.random().toString(16).slice(2)}`,selected:Number(sel),timeSpent:s.questionTimes[q.id]||0,source,reviewedAt:Date.now()};saveState();}else nkFsrsRecordAttempt(q.id,sel,s.questionTimes[q.id]||0,source,1);render();};
  const nkFsrsOriginalNext=nextQ;nextQ=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalNext.apply(this,arguments);};
  const nkFsrsOriginalPrev=prevQ;prevQ=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalPrev.apply(this,arguments);};
  const nkFsrsOriginalGo=goIndex;goIndex=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalGo.apply(this,arguments);};
  const nkFsrsOriginalRetry=retryCurrent;retryCurrent=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalRetry.apply(this,arguments);};
  let nkFsrsSessionOrigin=null;
  const nkFsrsOriginalEnd=endSession;endSession=function(){nkFsrsSessionOrigin=state.activeSession?.originRoute;const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalEnd.apply(this,arguments);};
  const nkFsrsOriginalNavigate=navigate;navigate=function(page,id){if(page==='result'){const t=state.tests.find(t=>String(t.id)===String(id));if(t){t.originRoute=state.activeSession?.originRoute||nkFsrsSessionOrigin||t.originRoute||(t.kind==='practice'?'topics':'tests');saveState();}nkFsrsSessionOrigin=null;}if(route.page==='fsrs-settings'&&page!=='fsrs-settings'&&nkFsrsDirty()){nkFsrsAskToLeave({page,id});return;}const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalNavigate.apply(this,arguments);};
  recordAttempt=nkFsrsRecordAttempt;
  qAttempts=function(qid){return nkFsrsActiveAttempts(qid);};
  window.addEventListener('pagehide',()=>nkFsrsRecoverPending());
  /* NK_FSRS_V6_END */
