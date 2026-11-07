  /* NK_SCHEDULED_MOCKS_V1_START */
  // Scheduled mocks: a timed test booked for a fixed date and time, like a real exam sitting.
  // The question set, marking and time are frozen when it is booked, and the booking cannot be moved or cancelled.
  // It opens at its time; the clock runs from that time, so starting late leaves less time; if it is never started
  // before the window closes, it is recorded as missed.
  const NK_SCHED_EARLY_MS=0;
  function nkSchedList(){return Array.isArray(state.scheduledMocks)?state.scheduledMocks.filter(m=>m&&m.id&&Number(m.at)>0&&Array.isArray(m.questionIds)&&m.questionIds.length):[];}
  function nkSchedDurationMs(m){return Math.max(1,m.questionIds.length)*(Number(m.seconds)||60)*1000;}
  // Doors: a mock can be started up to 15 minutes after its time (less for a shorter mock); then it is missed.
  const NK_SCHED_DOOR_MS=15*60000;
  function nkSchedDoorMs(m){return Math.min(NK_SCHED_DOOR_MS,nkSchedDurationMs(m));}
  function nkSchedTest(m){return (state.tests||[]).find(t=>String(t.scheduledMockId||'')===String(m.id))||null;}
  function nkSchedMakeup(m){return (state.tests||[]).find(t=>String(t.makeupFor||'')===String(m.id))||null;}
  // The outcome is also stamped on the booking, because the test list keeps only the latest 100 results.
  function nkSchedNoteTaken(session,test){
    const id=String(session?.scheduledMockId||session?.makeupFor||'');if(!id)return;
    const m=nkSchedList().find(item=>String(item.id)===id);if(!m)return;
    if(session.scheduledMockId)m.takenTestId=String(test.id);else m.makeupTestId=String(test.id);
  }
  function nkSchedStatus(m,now=Date.now()){
    if(m.takenTestId)return 'taken';
    if(m.missedAt)return 'missed';
    const test=nkSchedTest(m);
    if(test)return test.missed?'missed':'taken';
    if(String(state.activeSession?.scheduledMockId||'')===String(m.id))return 'live';
    if(now<Number(m.at)-NK_SCHED_EARLY_MS)return 'upcoming';
    if(now<Number(m.at)+nkSchedDoorMs(m))return 'open';
    return 'missed';
  }
  // A missed mock is written into your test history as a zero: it counts, like a skipped exam would.
  function nkSchedRecordMisses(){
    const now=Date.now(),tests=Array.isArray(state.tests)?state.tests:[];let added=0;
    for(const m of nkSchedList()){
      if(m.takenTestId||m.missedAt||nkSchedTest(m)||nkSchedStatus(m,now)!=='missed')continue;
      m.missedAt=Number(m.at)+nkSchedDoorMs(m);
      const n=m.questionIds.length,marking=m.marking||{correct:1,wrong:0,blank:0};
      tests.push({id:`missed_${m.id}`,title:m.name,questionIds:[...m.questionIds],answers:{},questionTimes:{},markedForReview:{},correct:0,incorrect:0,unattempted:n,total:n,attempted:0,totalTimeMs:0,createdAt:Number(m.at)+nkSchedDoorMs(m),autoSubmitted:true,timerEnabled:true,timerMode:'global',originRoute:'tests',marking:{...marking},secondsPerQuestion:Number(m.seconds)||60,scheduledMockId:m.id,missed:true});
      added++;
    }
    if(added){state.tests=tests;saveState();}
    return added;
  }
  // Attendance: booked mocks whose time has passed, newest first; the streak counts the kept ones in a row.
  function nkSchedAttendance(){
    const now=Date.now(),past=nkSchedList().map(m=>({m,st:nkSchedStatus(m,now)})).filter(x=>x.st==='taken'||x.st==='missed').sort((a,b)=>b.m.at-a.m.at);
    const kept=past.filter(x=>x.st==='taken').length;let streak=0;for(const x of past){if(x.st!=='taken')break;streak++;}
    let best=0,run=0;for(const x of past.slice().reverse()){run=x.st==='taken'?run+1:0;best=Math.max(best,run);}
    return {booked:past.length,kept,missed:past.length-kept,streak,best,pending:nkSchedList().filter(m=>nkSchedStatus(m,now)==='missed'&&!m.makeupTestId&&!nkSchedMakeup(m))};
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
    const doors=Number(m.at)+nkSchedDoorMs(m),makeup=status==='missed'?nkSchedMakeup(m):null;
    const line=status==='upcoming'?`Opens ${nkSchedWhen(m.at)} · in ${nkSchedIn(Number(m.at)-now)}`
      :status==='open'?`Doors close ${nkSchedWhen(doors,false)} · ${nkSchedIn(doors-now)} to start`
      :status==='live'?`In progress · ends ${nkSchedWhen(closes,false)}`
      :status==='taken'?`Taken ${nkSchedWhen(m.at)}${test?.total?` · ${Math.round(Number(test.correct||0)/Number(test.total)*100)}%`:''}`
      :makeup?`Missed · scored 0 · made up ${makeup.total?Math.round(Number(makeup.correct||0)/Number(makeup.total)*100):0}%`:`Missed ${nkSchedWhen(m.at)} · scored 0`;
    const arg=esc(JSON.stringify(String(m.id)));
    const action=status==='open'?`<button type="button" class="nk-sched-go" data-sched-id="${esc(m.id)}" onclick="window.QB.nkSchedStart(this.getAttribute('data-sched-id'))">Start ${navIcon('chevron',16)}</button>`
      :status==='live'?`<button type="button" class="nk-sched-go" onclick="window.QB.nav('exam')">Resume ${navIcon('chevron',16)}</button>`
      :status==='taken'&&test?`<button type="button" class="nk-sched-link" data-test-id="${esc(test.id)}" onclick="window.QB.nav('result',this.getAttribute('data-test-id'))">Result ${navIcon('chevron',15)}</button>`
      :status==='missed'&&!makeup?`<button type="button" class="nk-sched-go is-makeup" onclick="window.QB.nkSchedMakeupStart(${arg})">Make up ${navIcon('chevron',16)}</button>`
      :status==='missed'&&makeup?`<button type="button" class="nk-sched-link" data-test-id="${esc(makeup.id)}" onclick="window.QB.nav('result',this.getAttribute('data-test-id'))">Result ${navIcon('chevron',15)}</button>`
      :status==='upcoming'?`<span class="nk-sched-lock">${navIcon('clock',15)} Locked</span>`:'';
    const saved=typeof nkMockList==='function'&&nkMockList().some(x=>x.questionIds.length===m.questionIds.length&&x.questionIds.every((id,i)=>String(id)===String(m.questionIds[i])));
    const save=place==='tests'&&status!=='live'?`<button type="button" class="nk-sched-save${saved?' is-saved':''}" ${saved?'disabled':''} onclick="window.QB.nkSchedSaveMock(${arg})">${navIcon(saved?'check':'bookmark',13)}${saved?'Saved as mock':'Save as mock'}</button>`:'';
    const soon=status==='upcoming'&&Number(m.at)-now<15*60000?' is-soon':'';
    return `<article class="nk-sched-ticket is-${status}${soon}${place==='home'?' is-home':''}" aria-label="${esc(m.name)}, ${esc(line)}">
      <div class="nk-sched-date" aria-hidden="true"><small>${esc(month)}</small><b>${day}</b><span>${esc(nkSchedWhen(m.at,false))}</span></div>
      <div class="nk-sched-copy"><strong>${esc(m.name)}</strong><small>${esc(nkSchedFacts(m))}</small><em>${esc(line).replace(/ · (in [^·]*)$/,' · <span class="nk-sched-in">$1</span>')}</em>${save}</div>
      <div class="nk-sched-actions">${action}</div>
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
    return `<section class="nk-v3-section nk-sched-section"><div class="nk-v3-section-head"><h2>Scheduled mocks</h2><span>${fmtNum(live.length)} upcoming</span></div>${nkSchedAttendanceMarkup()}
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
  let nkSchedSource=null; // a saved mock being booked, or null for the builder's draft
  function nkSchedOpen(mockId){
    const saved=mockId&&typeof nkMockList==='function'?nkMockList().find(x=>String(x.id)===String(mockId)):null;
    if(mockId&&!saved){showToast('That saved mock is gone.','bad');return;}
    nkSchedSource=saved||null;
    if(!saved&&(typeof nkCbtDraft==='undefined'||!nkCbtDraft)){showToast('Build a test first.','bad');return;}
    if(saved&&typeof nkMockClose==='function')nkMockClose();
    const count=saved?saved.questionIds.length:Math.min(Number(nkCbtDraft.count)||20,nkCbtPoolSize());if(!count){showToast('Choose topics with questions first.','bad');return;}
    document.getElementById('nk-sched-sheet')?.remove();
    const x=nkExamSettings(),minutes=Math.round(count*x.seconds/60),first=nkSchedSuggestions()[0]?.[1]||Date.now()+3600000;
    const name=saved?saved.name:((nkCbtDraft.name||'').trim()||nkCbtTitle());
    document.body.insertAdjacentHTML('beforeend',`<div class="nk-qs-backdrop nk-sched-backdrop" id="nk-sched-sheet" onclick="if(event.target===this)window.QB.nkSchedClose()" onkeydown="if(event.key==='Escape'){event.stopPropagation();window.QB.nkSchedClose()}">
      <section class="nk-qs nk-sched-sheet" role="dialog" aria-modal="true" aria-labelledby="nk-sched-title">
        <span class="nk-qs-grip" aria-hidden="true"></span>
        <div class="nk-qs-head"><div><h2 id="nk-sched-title">Schedule this mock</h2><p>${esc(name)} · ${fmtNum(count)} Qs · ${fmtNum(minutes)} min${nkExamIsPlain(x)?'':` · ${esc(nkMarkingLabel(x))}`}</p></div><button type="button" class="nk-qs-close nk-modal-close" aria-label="Close" onclick="window.QB.nkSchedClose()">${navIcon('close',20)}</button></div>
        <h3>When</h3>
        <div class="nk-exam-chips nk-sched-chips" role="radiogroup" aria-label="Suggested times">${nkSchedSuggestions().map(([label,t],i)=>`<button type="button" role="radio" aria-checked="${i===0}" class="${i===0?'is-selected':''}" data-at="${t}" onclick="window.QB.nkSchedPick(${t})">${esc(label)}</button>`).join('')}</div>
        <label class="nk-sched-field" for="nk-sched-at"><span>Date and time</span><input id="nk-sched-at" type="datetime-local" min="${nkSchedLocalValue(Date.now()+5*60000)}" value="${nkSchedLocalValue(first)}" oninput="window.QB.nkSchedPick(null)"></label>
        <ul class="nk-sched-rules">
          <li>${navIcon('clock',16)}<span>The clock starts at this time, whether you have started or not. Doors close 15 minutes later.</span></li>
          <li>${navIcon('close',16)}<span>It can’t be moved or cancelled. Miss it and it scores 0, breaks your attendance streak, and waits on Home as a make-up.</span></li>
          ${saved?'':`<li>${navIcon('test',16)}<span>The questions are drawn now and stay hidden until it opens.</span></li>`}
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
    const ids=nkSchedSource?nkSchedSource.questionIds.map(String):typeof nkMockPick==='function'?nkMockPick():[];if(!ids.length){showToast('No questions in this selection can be scheduled.','bad');return;}
    const x=nkExamSettings(),name=(nkSchedSource?nkSchedSource.name:((nkCbtDraft?.name||'').trim()||nkCbtTitle())).slice(0,80);
    const mock={id:`sm_${Date.now()}_${Math.random().toString(16).slice(2,8)}`,name,questionIds:ids,at,createdAt:Date.now(),marking:{correct:x.correct,wrong:x.wrong,blank:x.blank},seconds:x.seconds};
    state.scheduledMocks=[...nkSchedList(),mock];
    if(saveState()===false){showToast('The schedule could not be saved. Try again.','bad');return;}
    document.getElementById('nk-sched-sheet')?.remove();if(!nkSchedSource)nkCbtDraft=null;nkSchedSource=null;
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
  function nkSchedAttendanceMarkup(){
    const a=nkSchedAttendance();if(!a.booked)return '';
    const pct=Math.round(a.kept/a.booked*100);
    return `<div class="nk-sched-attend" role="group" aria-label="Attendance: kept ${a.kept} of ${a.booked} booked mocks"><div class="nk-sched-attend-ring" style="--p:${pct}%"><b>${pct}%</b></div><div><strong>Kept ${fmtNum(a.kept)} of ${fmtNum(a.booked)}</strong><small>${a.streak?`${fmtNum(a.streak)} in a row`:'Streak broken'}${a.best>1?` · best ${fmtNum(a.best)}`:''}</small></div><span class="nk-sched-attend-dots" aria-hidden="true">${nkSchedList().map(m=>({m,st:nkSchedStatus(m)})).filter(x=>x.st==='taken'||x.st==='missed').sort((x,y)=>x.m.at-y.m.at).slice(-12).map(x=>`<i class="is-${x.st}"></i>`).join('')}</span></div>`;
  }
  // A make-up sits the same paper, full length, from now. It never erases the miss.
  function nkSchedMakeupStart(id){
    const m=nkSchedList().find(item=>String(item.id)===String(id));if(!m)return false;
    if(nkSchedStatus(m)!=='missed'){showToast('Only a missed mock can be made up.');return false;}
    if(m.makeupTestId||nkSchedMakeup(m)){showToast('You already made this one up.');return false;}
    if(state.activeSession?.mode==='exam'){showToast('Finish or leave your current timed test first.','bad');return false;}
    const map=new Map(nkAllStudyQuestions().map(q=>[String(q.id),q])),ids=m.questionIds.map(String).filter(qid=>map.has(qid));
    if(!ids.length){showToast('This mock’s questions are unavailable.','bad');return false;}
    BY_ID={...BY_ID,...Object.fromEntries(ids.map(qid=>[qid,map.get(qid)]))};
    const started=startSession(ids,'exam',`Make-up · ${m.name}`.slice(0,80),`makeup-mock:${m.id}`);
    const s=state.activeSession;if(started===false||s?.mode!=='exam')return false;
    s.makeupFor=m.id;s.originRoute='tests';
    nkExamApply({...m.marking,seconds:m.seconds},true);saveState();
    if(typeof startExamTicker==='function')startExamTicker();
    navigate('exam');return true;
  }
  function nkSchedSaveMock(id){
    const m=nkSchedList().find(item=>String(item.id)===String(id));if(!m||typeof nkMockStore!=='function')return;
    const mock=nkMockStore(m.name,m.questionIds);if(!mock)return;
    showToast(`Saved “${m.name}” to your mocks.`,'good');render();
  }
  // The make-up waits at the top of Today until it is done.
  function nkSchedMakeupCard(){
    const m=nkSchedAttendance().pending.sort((a,b)=>b.at-a.at)[0];if(!m)return '';
    const minutes=Math.round(nkSchedDurationMs(m)/60000),arg=esc(JSON.stringify(String(m.id)));
    return `<section class="nk-sched-makeup" aria-label="Make-up mock"><span class="nk-sched-makeup-icon">${navIcon('refresh',20)}</span><div><small>Make-up owed</small><strong>${esc(m.name)}</strong><em>Missed ${esc(nkSchedWhen(m.at))} · ${fmtNum(m.questionIds.length)} Qs · ${fmtNum(minutes)} min</em></div><button type="button" class="nk-sched-go is-makeup" onclick="window.QB.nkSchedMakeupStart(${arg})">Sit it ${navIcon('chevron',16)}</button></section>`;
  }
  // Abandoning a scheduled mock would let it be retaken at leisure; the grid's Abandon stays for ordinary tests only.
  if(typeof nkAbandonTimedTest==='function'){
    const original=nkAbandonTimedTest;
    nkAbandonTimedTest=function(){if(state.activeSession?.scheduledMockId){showToast('A scheduled mock can’t be abandoned. Submit it when you are done.','bad');return false;}return original.apply(this,arguments);};
  }
  if(typeof testsPage==='function'){
    const original=testsPage;
    testsPage=function(){nkSchedRecordMisses();const html=original.apply(this,arguments),sched=nkSchedTestsMarkup();return sched?html.replace('<section class="nk-v3-section nk-na-saved-mocks',sched+'<section class="nk-v3-section nk-na-saved-mocks'):html;};
  }
  if(typeof dashboard==='function'){
    const original=dashboard;
    dashboard=function(){nkSchedRecordMisses();const html=original.apply(this,arguments),sched=nkSchedMakeupCard()+nkSchedHomeMarkup();if(!sched)return html;const at=html.indexOf('<section class="nk-section nk-study-sets">');return at>=0?html.slice(0,at)+sched+html.slice(at):html.replace('<section class="nk-home-revision nk-today',sched+'<section class="nk-home-revision nk-today');};
  }
  if(typeof nkCbtBuilderPage==='function'){
    const original=nkCbtBuilderPage;
    nkCbtBuilderPage=function(){const html=original.apply(this,arguments);return nkCbtDraft?.step===3?html.replace('<div class="nk-cbt-main-actions">',`<div class="nk-cbt-main-actions"><button type="button" class="nk-sched-open" aria-label="Schedule this mock" onclick="window.QB.nkSchedOpen()">${navIcon('clock',17)} Schedule</button>`):html;};
  }
  if(typeof nkMockOpen==='function'){
    const original=nkMockOpen;
    nkMockOpen=function(id){
      const out=original.apply(this,arguments),foot=document.querySelector('#nk-mock-sheet .nk-mock-sheet-foot');
      if(foot&&!foot.querySelector('.nk-sched-open'))foot.querySelector('.nk-mock-start')?.insertAdjacentHTML('beforebegin',`<button type="button" class="nk-mock-icon-btn nk-sched-open" aria-label="Schedule this mock" data-mock-id="${esc(id)}" onclick="window.QB.nkSchedOpen(this.getAttribute('data-mock-id'))">${navIcon('clock',18)}</button>`);
      return out;
    };
  }
  /* NK_SCHEDULED_MOCKS_V1_END */
