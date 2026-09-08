  /* NK_FSRS_V6_START — shared offline scheduler, queue, migration and UI. */
  const NK_FSRS_BACKUP_KEY='qbank_pre_fsrs_backup_v1';
  const NK_FSRS_VERSION='fsrs6';
  const NK_FSRS_DAY=86400000;
  const NK_FSRS_DEFAULTS={desiredRetention:.90,newCardLimit:30,dailyCap:150,maximumInterval:365};
  const nkFsrsAllQuestions=()=>SUBJECTS.flatMap(subject=>(subject.questions||[]).map(q=>({...q,subject:q.subject||subject.subject})));
  const nkFsrsAllById=()=>Object.fromEntries(nkFsrsAllQuestions().map(q=>[String(q.id),q]));
  function nkFsrsPreferences(){
    const raw=state.fsrsPreferences||{};
    return state.fsrsPreferences={
      desiredRetention:Math.min(.97,Math.max(.80,Number(raw.desiredRetention||NK_FSRS_DEFAULTS.desiredRetention))),
      newCardLimit:Math.min(100,Math.max(0,Math.round(Number(raw.newCardLimit??NK_FSRS_DEFAULTS.newCardLimit)))),
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
  function nkFsrsReplay(qid,preserveLegacyDue=false){
    const attempts=nkFsrsActiveAttempts(qid); if(!attempts.length){delete state.reviews[qid];return null;}
    const engine=nkFsrsEngine(),old=state.reviews[qid],firstAt=Number(attempts[0].reviewedAt||attempts[0].at||Date.now());
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
    const now=Date.now(),prefs=nkFsrsPreferences(),all=nkFsrsAllQuestions().filter(q=>(!filters.subject||q.subject===filters.subject)&&(!filters.topic||String(q.chapterId)===String(filters.topic))),due=[],fresh=[];
    all.forEach(q=>{const r=state.reviews[q.id];if(!nkFsrsActiveAttempts(q.id).length)fresh.push(q);else if(r&&Number(r.nextReviewAt||r.due)<=now)due.push(q);});
    due.sort((a,b)=>{const ar=state.reviews[a.id],br=state.reviews[b.id],al=[1,3].includes(Number(ar?.state))?0:1,bl=[1,3].includes(Number(br?.state))?0:1;return al-bl||nkFsrsRetrievability(ar,now)-nkFsrsRetrievability(br,now)||Number(ar?.due)-Number(br?.due)||String(a.id).localeCompare(String(b.id));});
    const today=new Date(now).toDateString(),seen=new Set(),introduced=new Set();
    nkFsrsAllQuestions().forEach(q=>{const history=nkFsrsActiveAttempts(q.id),daily=history.filter(a=>a.schedulerVersion===NK_FSRS_VERSION&&new Date(a.at).toDateString()===today);if(daily.length)seen.add(String(q.id));if(daily.some(a=>a.schedulerBefore?.state===0))introduced.add(String(q.id));});
    const remaining=Math.max(0,prefs.dailyCap-seen.size),dueEligible=due.filter(q=>!seen.has(String(q.id)));
    const dueTake=dueEligible.slice(0,remaining),newTake=fresh.slice(0,Math.min(Math.max(0,prefs.newCardLimit-introduced.size),Math.max(0,remaining-dueTake.length)));
    return {cards:[...dueTake,...newTake],due,totalDue:due.length,newCards:newTake,rolledOver:Math.max(0,due.length-dueTake.length)};
  }
  function nkFsrsCounts(now=Date.now()){
    const counts={due:0,new:0,learning:0,relearning:0,young:0,mature:0,overdue:0,attention:0};
    nkFsrsAllQuestions().forEach(q=>{const r=state.reviews[q.id];if(!nkFsrsActiveAttempts(q.id).length){counts.new++;return;}const due=Number(r?.due||0);if(due<=now){counts.due++;if(now-due>=NK_FSRS_DAY)counts.overdue++;}if(Number(r?.state)===1)counts.learning++;else if(Number(r?.state)===3)counts.relearning++;else if(Number(r?.stability)>=21)counts.mature++;else counts.young++;if(r?.needsAttention)counts.attention++;});return counts;
  }
  function nkFsrsForecast(){const out=Array(7).fill(0),start=new Date();start.setHours(0,0,0,0);Object.values(state.reviews||{}).forEach(r=>{const day=Math.floor((Number(r?.due||0)-start.getTime())/NK_FSRS_DAY);if(day<0)out[0]++;else if(day<7)out[day]++;});return out;}
  function nkStartTodaysReview(subject='',topic=''){
    const queue=nkFsrsQueue({subject,topic});if(!queue.cards.length){showToast('Nothing is due and the new-card limit is zero.');return;}
    BY_ID=nkFsrsAllById();startSession(queue.cards.map(q=>q.id),'practice',"Today's Review",'spaced-review');if(queue.rolledOver)showToast(`${queue.rolledOver} due cards roll forward.`);
  }
  function nkFsrsTopicOptions(subject){const item=SUBJECTS.find(s=>s.subject===subject),select=document.getElementById('nk-fsrs-topic');if(!select)return;select.innerHTML='<option value="">All topics</option>'+((item?.topics||[]).map(t=>`<option value="${esc(t.id)}">${esc(t.title||t.name)}</option>`).join(''));}
  function nkFsrsQueueDialog(){
    const subjects=SUBJECTS.map(s=>s.subject),counts=nkFsrsCounts(),queue=nkFsrsQueue();
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop" id="nk-fsrs-modal"><div class="modal card"><div class="modal-head"><div><h2>Today's Review</h2><div class="small-muted">${queue.totalDue} due · ${queue.newCards.length} new · about ${Math.ceil(queue.cards.length*1.2)} min</div></div><button class="icon-btn" onclick="document.getElementById('nk-fsrs-modal')?.remove()">×</button></div><label>Subject<select id="nk-fsrs-subject" onchange="window.QB.nkFsrsTopicOptions(this.value)"><option value="">All subjects</option>${subjects.map(x=>`<option>${esc(x)}</option>`).join('')}</select></label><label>Topic<select id="nk-fsrs-topic"><option value="">All topics</option></select></label><div class="nk-fsrs-breakdown">Learning ${counts.learning} · Relearning ${counts.relearning} · Young ${counts.young} · Mature ${counts.mature} · Overdue ${counts.overdue}${counts.attention?` · Needs attention ${counts.attention}`:''}</div><button class="primary-btn" onclick="const v=document.getElementById('nk-fsrs-subject').value,t=document.getElementById('nk-fsrs-topic').value;document.getElementById('nk-fsrs-modal').remove();window.QB.nkStartTodaysReview(v,t)">Start ${queue.cards.length} cards</button>${queue.rolledOver?`<div class="small-muted">${queue.rolledOver} excess due cards will roll forward.</div>`:''}</div></div>`);
  }
  function nkFsrsUndo(){
    let hit=null,qid=null;Object.keys(state.attempts||{}).forEach(id=>nkFsrsActiveAttempts(id).forEach(a=>{if(!hit||Number(a.at)>Number(hit.at)){hit=a;qid=id;}}));if(!hit){showToast('Nothing to undo.');return;}
    state.attempts[qid].push({id:`undo_${Date.now()}_${Math.random().toString(16).slice(2)}`,isUndo:true,undoOf:hit.id,at:Date.now(),schedulerVersion:NK_FSRS_VERSION});nkFsrsReplay(qid,false);saveState();showToast('Most recent rating undone.');render();
  }
  function nkFsrsSetPreference(name,value){const p=nkFsrsPreferences(),n=Number(value),bounds={desiredRetention:[80,97],newCardLimit:[0,100],dailyCap:[20,300],maximumInterval:[30,3650]},b=bounds[name];if(!b)return;p[name]=name==='desiredRetention'?Math.min(b[1],Math.max(b[0],n))/100:Math.round(Math.min(b[1],Math.max(b[0],n)));}
  function nkFsrsSaveSettings(){
    const fields=['desiredRetention','newCardLimit','dailyCap','maximumInterval'],inputs=Array.from(document.querySelectorAll('.nk-fsrs-settings input'));
    if(inputs.length!==fields.length||inputs.some(input=>!input.value.trim()||!Number.isFinite(Number(input.value))||!input.checkValidity())){showToast('Enter a value within each displayed range.','bad');return;}
    fields.forEach((key,index)=>nkFsrsSetPreference(key,inputs[index].value));saveState();showToast('Review settings saved.','good');render();
  }
  function nkFsrsSettingsMarkup(){const p=nkFsrsPreferences();return `<details class="nk-settings-group nk-fsrs-customization"><summary><span><b>FSRS customization</b><small>Retention, daily limits and intervals</small></span>${navIcon("chevron",17)}</summary><div class="card pad nk-fsrs-settings"><label>Desired retention <input type="number" min="80" max="97" value="${Math.round(p.desiredRetention*100)}">%</label>${p.desiredRetention>.95?'<div class="nk-fsrs-warning">Above 95% can increase review workload sharply.</div>':''}<label>New cards / day <input type="number" min="0" max="100" value="${p.newCardLimit}"></label><label>Total daily cap <input type="number" min="20" max="300" value="${p.dailyCap}"></label><label>Maximum interval (days) <input type="number" min="30" max="3650" value="${p.maximumInterval}"></label><p class="small-muted">Changes apply to future ratings; existing due dates are not bulk-rescheduled.</p><div class="nk-fsrs-save-actions"><button class="primary-btn" onclick="window.QB.nkFsrsSaveSettings()">Save changes</button><button class="ghost-btn" onclick="window.QB.nkFsrsUndo()">Undo most recent rating</button></div></div></details>`;}
  const nkFsrsOriginalDashboard=dashboard;
  dashboard=function(){const out=nkFsrsOriginalDashboard(),c=nkFsrsCounts(),f=nkFsrsForecast(),q=nkFsrsQueue();const card=`<section class="card pad nk-fsrs-today"><div class="section-title"><span>Today's Review</span><span class="sub">FSRS 6 · ${Math.ceil(q.cards.length*1.2)} min</span></div><div class="nk-fsrs-counts"><b>${c.due}<small>Due</small></b><b>${c.new}<small>New</small></b><b>${c.learning+c.relearning}<small>Learning</small></b></div><div class="nk-fsrs-forecast" aria-label="Seven-day workload forecast">${f.map((n,i)=>`<span title="Day ${i+1}: ${n}"><i style="height:${Math.max(4,Math.min(42,n*2))}px"></i><small>${i?'+'+i:'Today'}</small></span>`).join('')}</div><button class="primary-btn" onclick="window.QB.nkFsrsQueueDialog()">Review all subjects</button>${q.rolledOver?`<p class="small-muted">${q.rolledOver} due cards roll forward after today's cap.</p>`:''}</section>`;return out.replace('</main>',card+'</main>');};
  const nkFsrsOriginalMore=morePage;morePage=function(){return nkFsrsOriginalMore().replace('</main>',nkFsrsSettingsMarkup()+'</main>');};
  const nkFsrsOriginalActionBar=practiceActionBar;
  practiceActionBar=function(){
    const out=nkFsrsOriginalActionBar.apply(this,arguments),s=state.activeSession,qid=s?.questionIds?.[s.index],markup=qid?nkFsrsRatingMarkup(qid):'';
    if(!markup||s?.mode!=='practice')return out;
    return out.replace('nk-session-footer','nk-session-footer nk-fsrs-docked').replace('<div class="fixed-actions-inner">',markup+'<div class="fixed-actions-inner">');
  };
  const nkFsrsOriginalSubmitPractice=submitPractice;submitPractice=function(){const s=state.activeSession;if(!s||s.mode!=='practice')return;const q=nkFsrsAllById()[s.questionIds[s.index]];if(!q||s.submitted[q.id])return;const sel=s.answers[q.id];if(!sel)return;savePracticeElapsed();s.submitted[q.id]=true;const correct=Number(q.correctOption)===Number(sel);haptic(correct?[16,18,16]:[10,32,10]);if(correct){s.pendingRating=s.pendingRating||{};s.pendingRating[q.id]={id:`pending_${Date.now()}_${Math.random().toString(16).slice(2)}`,selected:Number(sel),timeSpent:s.questionTimes[q.id]||0,source:s.studyModuleId?'study-module':'practice',reviewedAt:Date.now()};saveState();}else nkFsrsRecordAttempt(q.id,sel,s.questionTimes[q.id]||0,s.studyModuleId?'study-module':'practice',1);render();};
  const nkFsrsOriginalNext=nextQ;nextQ=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalNext.apply(this,arguments);};
  const nkFsrsOriginalPrev=prevQ;prevQ=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalPrev.apply(this,arguments);};
  const nkFsrsOriginalGo=goIndex;goIndex=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalGo.apply(this,arguments);};
  const nkFsrsOriginalRetry=retryCurrent;retryCurrent=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalRetry.apply(this,arguments);};
  const nkFsrsOriginalEnd=endSession;endSession=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalEnd.apply(this,arguments);};
  const nkFsrsOriginalNavigate=navigate;navigate=function(){const s=state.activeSession,qid=s?.questionIds?.[s.index];if(qid)nkFsrsCommitPending(qid,3);return nkFsrsOriginalNavigate.apply(this,arguments);};
  recordAttempt=nkFsrsRecordAttempt;
  qAttempts=function(qid){return nkFsrsActiveAttempts(qid);};
  window.addEventListener('pagehide',()=>nkFsrsRecoverPending());
  /* NK_FSRS_V6_END */
