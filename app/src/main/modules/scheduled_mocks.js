  /* NK_SCHEDULED_MOCKS_V1_START */
  // Scheduled mocks: a timed test booked for a fixed date and time, like a real exam sitting.
  // The question set, marking and time are frozen when it is booked, and the booking cannot be moved or cancelled.
  // It opens at its time; the clock runs from that time, so starting late leaves less time; if it is never started
  // before the window closes, it is recorded as missed.
  const NK_SCHED_EARLY_MS=0;
  function nkSchedList(){return Array.isArray(state.scheduledMocks)?state.scheduledMocks.filter(m=>m&&m.id&&Number(m.at)>0&&Array.isArray(m.questionIds)&&m.questionIds.length):[];}
  function nkSchedDurationMs(m){return Math.max(1,m.questionIds.length)*(Number(m.seconds)||60)*1000;}
  function nkSchedTest(m){return (state.tests||[]).find(t=>String(t.scheduledMockId||'')===String(m.id))||null;}
  function nkSchedStatus(m,now=Date.now()){
    if(nkSchedTest(m))return 'taken';
    if(String(state.activeSession?.scheduledMockId||'')===String(m.id))return 'live';
    if(now<Number(m.at)-NK_SCHED_EARLY_MS)return 'upcoming';
    if(now<Number(m.at)+nkSchedDurationMs(m))return 'open';
    return 'missed';
  }
  function nkSchedWhen(at,withDay=true){
    const d=new Date(Number(at)),today=new Date(),tomorrow=new Date();tomorrow.setDate(today.getDate()+1);
    const same=(a,b)=>a.toDateString()===b.toDateString();
    const time=d.toLocaleTimeString([], {hour:'numeric',minute:'2-digit'});
    if(!withDay)return time;
    const day=same(d,today)?'Today':same(d,tomorrow)?'Tomorrow':d.toLocaleDateString([], {weekday:'short',day:'numeric',month:'short'});
    return `${day}, ${time}`;
  }
  function nkSchedIn(ms){
    const m=Math.max(0,Math.round(ms/60000)),d=Math.floor(m/1440),h=Math.floor(m%1440/60),min=m%60;
    return d?`${d} d ${h} h`:h?(min?`${h} h ${min} min`:`${h} h`):`${Math.max(1,min)} min`;
  }
  function nkSchedFacts(m){
    const minutes=Math.round(nkSchedDurationMs(m)/60000);
    return `${fmtNum(m.questionIds.length)} Qs · ${fmtNum(minutes)} min${m.marking&&!nkExamIsPlain(m.marking)?` · ${nkMarkingLabel(m.marking)}`:''}`;
  }
  function nkSchedTicket(m,place){
    const status=nkSchedStatus(m),d=new Date(Number(m.at)),now=Date.now();
    const month=d.toLocaleDateString([], {month:'short'}).toUpperCase(),day=d.getDate();
    const test=status==='taken'?nkSchedTest(m):null;
    const closes=Number(m.at)+nkSchedDurationMs(m);
    const line=status==='upcoming'?`Opens ${nkSchedWhen(m.at)} · in ${nkSchedIn(Number(m.at)-now)}`
      :status==='open'?`Open now · closes ${nkSchedWhen(closes,false)}, ${nkSchedIn(closes-now)} left`
      :status==='live'?`In progress · ends ${nkSchedWhen(closes,false)}`
      :status==='taken'?`Taken ${nkSchedWhen(m.at)}${test?.total?` · ${Math.round(Number(test.correct||0)/Number(test.total)*100)}%`:''}`
      :`Missed ${nkSchedWhen(m.at)}`;
    const action=status==='open'?`<button type="button" class="nk-sched-go" data-sched-id="${esc(m.id)}" onclick="window.QB.nkSchedStart(this.getAttribute('data-sched-id'))">Start ${navIcon('chevron',16)}</button>`
      :status==='live'?`<button type="button" class="nk-sched-go" onclick="window.QB.nav('exam')">Resume ${navIcon('chevron',16)}</button>`
      :status==='taken'&&test?`<button type="button" class="nk-sched-link" data-test-id="${esc(test.id)}" onclick="window.QB.nav('result',this.getAttribute('data-test-id'))">Result ${navIcon('chevron',15)}</button>`
      :status==='upcoming'?`<span class="nk-sched-lock">${navIcon('clock',15)} Locked</span>`:'';
    return `<article class="nk-sched-ticket is-${status}${place==='home'?' is-home':''}" aria-label="${esc(m.name)}, ${esc(line)}">
      <div class="nk-sched-date" aria-hidden="true"><small>${esc(month)}</small><b>${day}</b><span>${esc(nkSchedWhen(m.at,false))}</span></div>
      <div class="nk-sched-copy"><strong>${esc(m.name)}</strong><small>${esc(nkSchedFacts(m))}</small><em>${esc(line).replace(/ · (in [^·]*)$/,' · <span class="nk-sched-in">$1</span>')}</em></div>
      ${action}
    </article>`;
  }
  // Home shows a booked mock from the day before until it closes; Tests lists every booking.
  function nkSchedHomeMarkup(){
    const now=Date.now(),list=nkSchedList().filter(m=>{const st=nkSchedStatus(m,now);return st==='open'||st==='live'||st==='upcoming'&&Number(m.at)-now<36*3600000;}).sort((a,b)=>a.at-b.at);
    return list.length?`<section class="nk-sched-home" aria-label="Scheduled mock">${list.slice(0,2).map(m=>nkSchedTicket(m,'home')).join('')}</section>`:'';
  }
  function nkSchedTestsMarkup(){
    const list=nkSchedList(),now=Date.now();if(!list.length)return '';
    const live=list.filter(m=>['open','live','upcoming'].includes(nkSchedStatus(m,now))).sort((a,b)=>a.at-b.at);
    const past=list.filter(m=>!live.includes(m)).sort((a,b)=>b.at-a.at);
    return `<section class="nk-v3-section nk-sched-section"><div class="nk-v3-section-head"><h2>Scheduled mocks</h2><span>${fmtNum(live.length)} upcoming</span></div>
      <div class="nk-sched-list">${live.map(m=>nkSchedTicket(m,'tests')).join('')}${past.slice(0,3).map(m=>nkSchedTicket(m,'tests')).join('')}</div>
      ${past.length>3?`<details class="nk-test-older"><summary>Show ${fmtNum(past.length-3)} older</summary><div class="nk-sched-list">${past.slice(3).map(m=>nkSchedTicket(m,'tests')).join('')}</div></details>`:''}
    </section>`;
  }
  // Booking sheet, opened from the builder's last step.
  function nkSchedLocalValue(ms){const d=new Date(ms),p=n=>String(n).padStart(2,'0');return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;}
  function nkSchedSuggestions(){
    const out=[],at=(days,hour)=>{const d=new Date();d.setDate(d.getDate()+days);d.setHours(hour,0,0,0);return d.getTime();};
    const now=Date.now();
    [[0,20,'Tonight 8 pm'],[1,9,'Tomorrow 9 am'],[1,18,'Tomorrow 6 pm']].forEach(([days,hour,label])=>{const t=at(days,hour);if(t>now+10*60000)out.push([label,t]);});
    const sat=new Date();sat.setDate(sat.getDate()+((6-sat.getDay()+7)%7||7));sat.setHours(10,0,0,0);out.push(['Saturday 10 am',sat.getTime()]);
    return out.slice(0,4);
  }
  function nkSchedOpen(){
    if(typeof nkCbtDraft==='undefined'||!nkCbtDraft){showToast('Build a test first.','bad');return;}
    const count=Math.min(Number(nkCbtDraft.count)||20,nkCbtPoolSize());if(!count){showToast('Choose topics with questions first.','bad');return;}
    document.getElementById('nk-sched-sheet')?.remove();
    const x=nkExamSettings(),minutes=Math.round(count*x.seconds/60),first=nkSchedSuggestions()[0]?.[1]||Date.now()+3600000;
    const name=(nkCbtDraft.name||'').trim()||nkCbtTitle();
    document.body.insertAdjacentHTML('beforeend',`<div class="nk-qs-backdrop nk-sched-backdrop" id="nk-sched-sheet" onclick="if(event.target===this)window.QB.nkSchedClose()" onkeydown="if(event.key==='Escape'){event.stopPropagation();window.QB.nkSchedClose()}">
      <section class="nk-qs nk-sched-sheet" role="dialog" aria-modal="true" aria-labelledby="nk-sched-title">
        <span class="nk-qs-grip" aria-hidden="true"></span>
        <div class="nk-qs-head"><div><h2 id="nk-sched-title">Schedule this mock</h2><p>${esc(name)} · ${fmtNum(count)} Qs · ${fmtNum(minutes)} min${nkExamIsPlain(x)?'':` · ${esc(nkMarkingLabel(x))}`}</p></div><button type="button" class="nk-qs-close nk-modal-close" aria-label="Close" onclick="window.QB.nkSchedClose()">${navIcon('close',20)}</button></div>
        <h3>When</h3>
        <div class="nk-exam-chips nk-sched-chips" role="radiogroup" aria-label="Suggested times">${nkSchedSuggestions().map(([label,t],i)=>`<button type="button" role="radio" aria-checked="${i===0}" class="${i===0?'is-selected':''}" data-at="${t}" onclick="window.QB.nkSchedPick(${t})">${esc(label)}</button>`).join('')}</div>
        <label class="nk-sched-field" for="nk-sched-at"><span>Date and time</span><input id="nk-sched-at" type="datetime-local" min="${nkSchedLocalValue(Date.now()+5*60000)}" value="${nkSchedLocalValue(first)}" oninput="window.QB.nkSchedPick(null)"></label>
        <ul class="nk-sched-rules">
          <li>${navIcon('clock',16)}<span>The clock starts at this time, whether you have started or not.</span></li>
          <li>${navIcon('close',16)}<span>It can’t be moved or cancelled. If you don’t sit it in time, it’s recorded as missed.</span></li>
          <li>${navIcon('test',16)}<span>The questions are drawn now and stay hidden until it opens.</span></li>
        </ul>
        <button type="button" class="nk-qs-start nk-sched-confirm" id="nk-sched-confirm" onclick="window.QB.nkSchedConfirm()">Lock in ${esc(nkSchedWhen(first))}</button>
      </section></div>`);
    document.getElementById('nk-sched-at')?.focus({preventScroll:true});
  }
  function nkSchedClose(){document.getElementById('nk-sched-sheet')?.remove();document.querySelector('.nk-sched-open')?.focus?.({preventScroll:true});}
  function nkSchedPick(at){
    const input=document.getElementById('nk-sched-at');if(!input)return;
    if(at)input.value=nkSchedLocalValue(at);
    const ms=new Date(input.value).getTime();
    document.querySelectorAll('.nk-sched-chips button').forEach(b=>{const on=Number(b.dataset.at)===ms;b.classList.toggle('is-selected',on);b.setAttribute('aria-checked',String(on));});
    const confirm=document.getElementById('nk-sched-confirm');
    if(confirm){const ok=Number.isFinite(ms)&&ms>Date.now()+60000;confirm.disabled=!ok;confirm.textContent=ok?`Lock in ${nkSchedWhen(ms)}`:'Pick a time in the future';}
  }
  function nkSchedConfirm(){
    const input=document.getElementById('nk-sched-at'),at=new Date(input?.value||'').getTime();
    if(!Number.isFinite(at)||at<=Date.now()+60000){showToast('Pick a time in the future.','bad');return;}
    const ids=typeof nkMockPick==='function'?nkMockPick():[];if(!ids.length){showToast('No questions in this selection can be scheduled.','bad');return;}
    const x=nkExamSettings(),name=((nkCbtDraft?.name||'').trim()||nkCbtTitle()).slice(0,80);
    const mock={id:`sm_${Date.now()}_${Math.random().toString(16).slice(2,8)}`,name,questionIds:ids,at,createdAt:Date.now(),marking:{correct:x.correct,wrong:x.wrong,blank:x.blank},seconds:x.seconds};
    state.scheduledMocks=[...nkSchedList(),mock];
    if(saveState()===false){showToast('The schedule could not be saved. Try again.','bad');return;}
    document.getElementById('nk-sched-sheet')?.remove();nkCbtDraft=null;
    showToast(`Scheduled for ${nkSchedWhen(at)}.`,'good');navigate('tests');
  }
  function nkSchedStart(id){
    const m=nkSchedList().find(item=>String(item.id)===String(id));if(!m)return false;
    const status=nkSchedStatus(m);
    if(status==='upcoming'){showToast(`This mock opens ${nkSchedWhen(m.at)}.`);return false;}
    if(status==='live'){navigate('exam');return true;}
    if(status!=='open'){showToast(status==='taken'?'You already sat this mock.':'This mock has closed and is recorded as missed.');return false;}
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your current timed test first.','bad');return false;}
    const map=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),ids=m.questionIds.map(String).filter(qid=>map.has(qid));
    if(!ids.length){showToast('This mock’s questions are unavailable.','bad');return false;}
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(qid=>[qid,map.get(qid)]))};
    const started=startSession(ids,'exam',m.name,`scheduled-mock:${m.id}`);
    const s=state.activeSession;if(started===false||s?.mode!=='exam')return false;
    // The clock belongs to the booking, not to the moment you sat down.
    s.scheduledMockId=m.id;s.originRoute='tests';s.startedAt=Number(m.at);s.lastTick=Date.now();
    nkExamApply({...m.marking,seconds:m.seconds},true);
    s.deadlineAt=Number(m.at)+nkSchedDurationMs(m);saveState();
    if(typeof startExamTicker==='function')startExamTicker();
    render();return true;
  }
  // Abandoning a scheduled mock would let it be retaken at leisure; the grid's Abandon stays for ordinary tests only.
  if(typeof nkAbandonTimedTest==='function'){
    const original=nkAbandonTimedTest;
    nkAbandonTimedTest=function(){if(state.activeSession?.scheduledMockId){showToast('A scheduled mock can’t be abandoned. Submit it when you are done.','bad');return false;}return original.apply(this,arguments);};
  }
  if(typeof testsPage==='function'){
    const original=testsPage;
    testsPage=function(){const html=original.apply(this,arguments),sched=nkSchedTestsMarkup();return sched?html.replace('<section class="nk-v3-section nk-na-saved-mocks',sched+'<section class="nk-v3-section nk-na-saved-mocks'):html;};
  }
  if(typeof dashboard==='function'){
    const original=dashboard;
    dashboard=function(){const html=original.apply(this,arguments),sched=nkSchedHomeMarkup();return sched?html.replace('<section class="nk-home-revision nk-today',sched+'<section class="nk-home-revision nk-today'):html;};
  }
  if(typeof nkCbtBuilderPage==='function'){
    const original=nkCbtBuilderPage;
    nkCbtBuilderPage=function(){const html=original.apply(this,arguments);return nkCbtDraft?.step===3?html.replace('<div class="nk-cbt-main-actions">',`<div class="nk-cbt-main-actions"><button type="button" class="nk-sched-open" aria-label="Schedule this mock" onclick="window.QB.nkSchedOpen()">${navIcon('clock',17)} Schedule</button>`):html;};
  }
  /* NK_SCHEDULED_MOCKS_V1_END */
