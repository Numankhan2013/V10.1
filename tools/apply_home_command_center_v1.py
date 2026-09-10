#!/usr/bin/env python3
"""Install the approved NK QBank Home / Study / Test / FSRS information architecture.

This transform intentionally reuses the established question, Topics, Practice,
CBT, Custom Module, Review, Marrow, and FSRS engines. It owns only the product
routing/composition needed to connect those engines according to the approved
V3 learner flow.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
STYLE_ID = "nk-home-command-center-v1"
FLOW_MARKER = "NK_HOME_FLOW_V3"

HELPERS = r'''
  /* NK_HOME_FLOW_V3_START */
  let nkHomeProgressRange='week';
  let nkTestSetup={mode:'exam',source:'all',count:20};
  let nkFsrsSubjectFilter='';

  function nkAllStudyQuestions(){
    if(typeof nkAllBankQuestions==='function') return nkAllBankQuestions();
    if(typeof nkAllQuestionBank==='function') return nkAllQuestionBank();
    return (SUBJECTS||[]).flatMap(r=>(r.questions||[]).map(q=>({...q,subject:q.subject||r.subject,bank:q.bank||r.bank||'PrepLadder'})));
  }
  function nkFindStudyQuestion(qid){return nkAllStudyQuestions().find(q=>String(q.id)===String(qid))||BY_ID?.[String(qid)]||null;}
  function nkPreferredRecord(subject){
    const records=typeof nkBankRecords==='function'?nkBankRecords(subject):[];
    if(records.length)return records.find(r=>r.bank==='Marrow')||records[0];
    return (SUBJECTS||[]).find(r=>r.subject===subject)||null;
  }
  function nkSubjectStatsV3(subject){
    const r=nkPreferredRecord(subject)||{},questions=Array.isArray(r.questions)?r.questions:[],topics=Array.isArray(r.topics)?r.topics:[];
    const attempted=questions.filter(q=>qAttempts(q.id).length>0).length,pct=questions.length?Math.round(attempted/questions.length*100):0;
    return {record:r,questions:questions.length,topics:topics.length,attempted,pct};
  }
  function nkOpenSubjectLibrary(subject){
    const r=nkPreferredRecord(subject);
    if(!r){showToast('This subject is not available.','bad');return;}
    if(typeof openBank==='function'&&r.bank){openBank(subject,r.bank);return;}
    if(typeof openSubjectTopics==='function'){openSubjectTopics(subject);return;}
    activeSubject=subject;localStorage.setItem('qbank_active_subject_v1',subject);navigate('topics');
  }
  function nkOpenSubjectChapter(subject,bank,topicId){
    if(typeof openBank==='function'&&bank)openBank(subject,bank);else if(typeof openSubjectTopics==='function')openSubjectTopics(subject);
    setTimeout(()=>{if(typeof openChapter==='function')openChapter(topicId);},0);
  }
  function nkSubjectCardsV3(){
    return (SUBJECTS||[]).map(r=>{const s=nkSubjectStatsV3(r.subject),m=nkAppSubjectMeta(r.subject);return `<button class="nk-v3-subject-card is-${m.key}" onclick="window.QB.nkOpenSubjectLibrary('${esc(r.subject)}')"><span class="nk-v3-subject-icon">${nkAppSubjectIcon(r.subject,24)}</span><span class="nk-v3-subject-copy"><strong>${esc(r.subject)}</strong><small>${fmtNum(s.topics)} topics · ${fmtNum(s.questions)} questions</small><span class="nk-v3-subject-progress"><i style="width:${s.pct}%"></i></span></span><b>${s.pct}%</b>${navIcon('chevron',18)}</button>`;}).join('');
  }
  function nkTopicTitleForQuestion(q){
    if(!q)return'';const r=nkPreferredRecord(q.subject),t=(r?.topics||[]).find(x=>String(x.id)===String(q.chapterId));return t?.title||q.topic||q.chapter||'';
  }
  function nkLatestPracticeContext(){
    const live=state.activeSession;
    if(live?.mode==='practice'&&live.questionIds?.length){const q=nkFindStudyQuestion(live.questionIds[Math.max(0,Math.min(live.index||0,live.questionIds.length-1))]);if(q)return{q,topic:nkTopicTitleForQuestion(q),subject:q.subject||activeSubject,live:true};}
    let latest=null;for(const [qid,items] of Object.entries(state.attempts||{}))for(const a of items||[]){if(!a||a.source==='exam'||!a.at)continue;if(!latest||Number(a.at)>latest.at)latest={qid,at:Number(a.at)};}
    const q=latest?nkFindStudyQuestion(latest.qid):null;return q?{q,topic:nkTopicTitleForQuestion(q),subject:q.subject||activeSubject,live:false}:null;
  }
  function nkTopicQuestionIds(q){
    if(!q)return[];return nkAllStudyQuestions().filter(x=>x.subject===q.subject&&String(x.chapterId)===String(q.chapterId)&&(!q.bank||!x.bank||x.bank===q.bank)).map(x=>String(x.id));
  }
  function nkContinueRecentPractice(){
    if(state.activeSession?.mode==='practice'&&state.activeSession.questionIds?.length){navigate('practice');return;}
    const ctx=nkLatestPracticeContext();if(!ctx?.q){navigate('study-library');return;}
    const r=nkPreferredRecord(ctx.q.subject),bank=ctx.q.bank||r?.bank;if(typeof openBank==='function'&&bank)openBank(ctx.q.subject,bank);else if(typeof openSubjectTopics==='function')openSubjectTopics(ctx.q.subject);
    const ids=nkTopicQuestionIds(ctx.q);if(ids.length)startSession(ids,'practice',ctx.topic||`${ctx.subject} Practice`);else navigate('study-library');
  }
  function nkHomeRangeStart(range){const d=new Date();d.setHours(0,0,0,0);if(range==='today')return d.getTime();if(range==='week'){d.setDate(d.getDate()-((d.getDay()+6)%7));return d.getTime();}if(range==='month'){d.setDate(1);return d.getTime();}d.setMonth(0,1);return d.getTime();}
  function nkHomeProgressStats(range=nkHomeProgressRange){
    const start=nkHomeRangeStart(range),attempts=[],qids=new Set();for(const [qid,items] of Object.entries(state.attempts||{}))for(const a of items||[])if(Number(a?.at||0)>=start){attempts.push(a);qids.add(String(qid));}
    const correct=attempts.filter(a=>a.correct).length,practiceMs=attempts.filter(a=>a.source!=='exam').reduce((n,a)=>n+Math.max(0,Number(a.timeSpent)||0),0),testMs=(state.tests||[]).filter(t=>Number(t?.createdAt||0)>=start&&t.kind!=='practice').reduce((n,t)=>n+Math.max(0,Number(t.totalTimeMs)||0),0);
    return {attempted:qids.size,accuracy:attempts.length?correct/attempts.length*100:0,studyMs:practiceMs+testMs};
  }
  function nkSetHomeProgressRange(v){if(['today','week','month','year'].includes(v)){nkHomeProgressRange=v;render();}}
  function nkHomePreferredTotal(){return (SUBJECTS||[]).reduce((n,r)=>n+nkSubjectStatsV3(r.subject).questions,0);}
  function nkStrongestChaptersV3(){
    const rows=[];(SUBJECTS||[]).forEach(s=>{const r=nkPreferredRecord(s.subject);if(!r)return;(r.topics||[]).forEach(t=>{const qs=(r.questions||[]).filter(q=>String(q.chapterId)===String(t.id)),attempts=qs.flatMap(q=>qAttempts(q.id));if(!attempts.length)return;const correct=attempts.filter(a=>a.correct).length;rows.push({subject:s.subject,bank:r.bank||'',topicId:String(t.id),title:t.title||t.name||'Topic',attempted:new Set(qs.filter(q=>qAttempts(q.id).length).map(q=>q.id)).size,total:qs.length,accuracy:correct/attempts.length*100});});});
    return rows.sort((a,b)=>b.accuracy-a.accuracy||b.attempted-a.attempted).slice(0,5);
  }

  function nkReviewEligibility(q){
    const id=String(q?.id||''),history=qAttempts(id);if(history.some(a=>a&&!a.isUndo&&a.correct===false))return'wrong';if(state.fsrsReviewEligible?.[id]?.reason==='skipped')return'skipped';return'';
  }
  function nkReviewPool(subject=''){return nkAllStudyQuestions().filter(q=>(!subject||q.subject===subject)&&nkReviewEligibility(q));}
  function nkReviewDue(subject=''){const now=Date.now();return nkReviewPool(subject).filter(q=>{const r=state.reviews?.[q.id];return !r||Number(r.nextReviewAt||r.due||0)<=now;});}
  function nkReviewCounts(subject=''){
    const now=Date.now(),pool=nkReviewPool(subject),due=nkReviewDue(subject);let learning=0,relearning=0,overdue=0;pool.forEach(q=>{const r=state.reviews?.[q.id];if(Number(r?.state)===1)learning++;if(Number(r?.state)===3)relearning++;const at=Number(r?.nextReviewAt||r?.due||0);if(at&&at<now-86400000)overdue++;});return{pool:pool.length,due:due.length,learning,relearning,overdue};
  }
  function nkReviewForecast(subject=''){
    const out=Array(7).fill(0),start=new Date();start.setHours(0,0,0,0);nkReviewPool(subject).forEach(q=>{const r=state.reviews?.[q.id],at=Number(r?.nextReviewAt||r?.due||0);if(!at){out[0]++;return;}const day=Math.floor((at-start.getTime())/86400000);if(day<0)out[0]++;else if(day<7)out[day]++;});return out;
  }
  function nkSetFsrsSubject(subject=''){nkFsrsSubjectFilter=subject;render();}
  function nkStartReviewOnly(subject=nkFsrsSubjectFilter){const rows=nkReviewDue(subject);if(!rows.length){showToast('No wrong or skipped questions are due for this selection.');return;}BY_ID={...BY_ID,...Object.fromEntries(rows.map(q=>[String(q.id),q]))};startSession(rows.map(q=>String(q.id)),'practice','FSRS Review','fsrs');}
  function nkSessionQuestionEncountered(s,id){
    if(!s)return false;const key=String(id),current=String(s.questionIds?.[Number(s.index)||0]||'');return current===key||Number(s.questionTimes?.[key]||0)>0||Object.prototype.hasOwnProperty.call(s.answers||{},key)||Boolean(s.submitted?.[key])||Number(s.strictQuestionTime?.[key]||0)>0||Boolean(s.strictExpired?.[key]);
  }
  function nkMarkSkippedFromSession(s){
    if(!s?.questionIds?.length)return;state.fsrsReviewEligible=state.fsrsReviewEligible||{};const at=Date.now();s.questionIds.forEach(id=>{const key=String(id),answered=Boolean(s.answers?.[key]),submitted=Boolean(s.submitted?.[key]);if(nkSessionQuestionEncountered(s,key)&&!answered&&!submitted)state.fsrsReviewEligible[key]={reason:'skipped',at};});
  }
  const nkHomeOriginalEndSession=endSession;
  endSession=function(){const s=state.activeSession;if(s?.mode==='practice'&&typeof savePracticeElapsed==='function')savePracticeElapsed();nkMarkSkippedFromSession(s);saveState();return nkHomeOriginalEndSession.apply(this,arguments);};

  function nkStudyLibraryPage(){
    return shell(`<main class="nk-app-v114 nk-study-library-v3"><button class="nk-back-link" onclick="window.QB.nav('dashboard')">${navIcon('back',18)} Home</button><header class="nk-v3-page-hero"><div class="nk-kicker">STUDY LIBRARY</div><h1>My Subjects</h1><p>Choose a subject to open its complete topic journey.</p></header><div class="nk-v3-subject-list">${nkSubjectCardsV3()}</div><p class="nk-v3-page-note">Subjects open the full Topics page. No popup topic picker is used.</p></main>`,'dashboard');
  }
  function nkFsrsReviewPage(){
    const subjects=['',...(SUBJECTS||[]).map(s=>s.subject)],selected=nkFsrsSubjectFilter,c=nkReviewCounts(selected),forecast=nkReviewForecast(selected),max=Math.max(1,...forecast);
    const cards=subjects.map(subject=>{const label=subject||'All Subjects',x=nkReviewCounts(subject),active=subject===selected;return `<button class="nk-fsrs-subject-card ${active?'is-active':''}" onclick="window.QB.nkSetFsrsSubject('${esc(subject)}')"><span>${subject?nkAppSubjectIcon(subject,22):navIcon('grid',22)}</span><span><strong>${esc(label)}</strong><small>${fmtNum(x.due)} due · ${fmtNum(x.pool)} review pool</small></span>${active?navIcon('check',18):navIcon('chevron',18)}</button>`;}).join('');
    return shell(`<main class="nk-app-v114 nk-fsrs-page-v3"><header class="nk-v3-page-hero"><div class="nk-kicker">SPACED REPETITION</div><h1>FSRS Review</h1><p>Only questions you got wrong or encountered and skipped can enter this review queue. Unseen QBank questions are never introduced here.</p></header><section class="nk-v3-section"><div class="nk-v3-section-head"><h2>Choose subject</h2><span>${selected||'All subjects'}</span></div><div class="nk-fsrs-subject-list">${cards}</div></section><section class="nk-v3-section"><div class="nk-v3-section-head"><h2>Today's Review</h2><span>Review-only queue</span></div><div class="nk-review-metrics"><article><b>${fmtNum(c.due)}</b><small>Due</small></article><article><b>${fmtNum(c.learning+c.relearning)}</b><small>Learning</small></article><article><b>${fmtNum(c.overdue)}</b><small>Overdue</small></article></div><div class="nk-review-chart" aria-label="Seven day review forecast">${forecast.map((n,i)=>`<span><i style="height:${Math.max(6,Math.round(n/max*58))}px"></i><b>${n}</b><small>${i===0?'Today':'+'+i}</small></span>`).join('')}</div><button class="nk-v3-primary" onclick="window.QB.nkStartReviewOnly()">Start ${fmtNum(c.due)} due review${c.due===1?'':'s'} ${navIcon('chevron',17)}</button></section></main>`,'fsrs');
  }

  function nkOpenNewTest(mode='exam'){nkTestSetup.mode=mode==='practice'?'practice':'exam';navigate('tests');}
  function nkSetTestMode(mode){nkTestSetup.mode=mode==='practice'?'practice':'exam';render();}
  function nkSetTestSource(source){if(['all','wrong','bookmarks'].includes(source)){nkTestSetup.source=source;render();}}
  function nkSetTestCount(count){nkTestSetup.count=[10,20,50,100].includes(Number(count))?Number(count):20;render();}
  function nkOpenCustomSource(){if(nkTestSetup.mode==='exam'){openMultiSubjectTestBuilder();return;}openStudyModuleBuilder();}
  function nkConfiguredQueueIds(source){const all=nkAllStudyQuestions();if(source==='wrong')return all.filter(q=>qAttempts(q.id).some(a=>a.correct===false)).map(q=>q.id);if(source==='bookmarks')return all.filter(q=>state.bookmarks?.[q.id]).map(q=>q.id);return[];}
  function nkStartConfiguredIds(ids,title){
    const list=[...new Set((ids||[]).map(String))];if(!list.length){showToast('No questions available for this selection.','bad');return;}for(let i=list.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[list[i],list[j]]=[list[j],list[i]];}
    const count=Math.min(nkTestSetup.count,list.length),mode=nkTestSetup.mode==='exam'?'exam':'practice';BY_ID={...BY_ID,...Object.fromEntries(nkAllStudyQuestions().map(q=>[String(q.id),q]))};startSession(list.slice(0,count),mode,title);
    if(mode==='exam'&&state.activeSession){state.activeSession.timerEnabled=true;state.activeSession.timerMode='global';saveState();render();}
  }
  function nkStartConfiguredTest(){
    if(nkTestSetup.source==='all'){if(nkTestSetup.mode==='exam')openMultiSubjectTestBuilder();else navigate('study-library');return;}
    nkStartConfiguredIds(nkConfiguredQueueIds(nkTestSetup.source),nkTestSetup.source==='wrong'?'Wrong Questions':'Bookmarked Questions');
  }

  function nkStartTopicTimedTest(cid){
    const c=CHAPTER_BY_ID[String(cid)],ids=chapterQuestions(cid).map(q=>String(q.id));if(!ids.length){showToast('No questions are available for this topic.','bad');return;}
    startSession(ids,'exam',`${c?.title||'Topic'} · Timed Test`);const s=state.activeSession;if(!s)return;s.timerEnabled=true;s.timerMode='per-question';s.strictQuestionTime={};s.strictExpired={};s.strictQuestionStartedAt=Date.now();saveState();render();
  }
  function nkStrictSpent(s,id){const base=Number(s?.strictQuestionTime?.[id]||0);if(!s||s.timerMode!=='per-question'||s.strictExpired?.[id]||String(s.questionIds?.[s.index])!==String(id))return base;return base+Math.max(0,Date.now()-Number(s.strictQuestionStartedAt||Date.now()));}
  function nkStrictCommitCurrent(){const s=state.activeSession;if(!s||s.mode!=='exam'||s.timerMode!=='per-question')return;const id=String(s.questionIds[s.index]);s.strictQuestionTime=s.strictQuestionTime||{};s.strictQuestionTime[id]=Math.min(60000,nkStrictSpent(s,id));}
  function nkStrictResetClock(){const s=state.activeSession;if(s?.mode==='exam'&&s.timerMode==='per-question'){s.strictQuestionStartedAt=Date.now();saveState();}}
  function nkExpireTopicQuestion(){
    const s=state.activeSession;if(!s||s.mode!=='exam'||s.timerMode!=='per-question')return;const id=String(s.questionIds[s.index]);nkStrictCommitCurrent();saveExamElapsed();s.strictQuestionTime[id]=60000;s.strictExpired=s.strictExpired||{};s.strictExpired[id]=true;
    if(s.index>=s.questionIds.length-1){saveState();submitExam(true);return;}s.index++;s.strictQuestionStartedAt=Date.now();saveState();render();
  }
  const nkHomeNextQ=nextQ;nextQ=function(){nkStrictCommitCurrent();const out=nkHomeNextQ.apply(this,arguments);nkStrictResetClock();return out;};
  const nkHomePrevQ=prevQ;prevQ=function(){nkStrictCommitCurrent();const out=nkHomePrevQ.apply(this,arguments);nkStrictResetClock();return out;};
  const nkHomeGoIndex=goIndex;goIndex=function(){nkStrictCommitCurrent();const out=nkHomeGoIndex.apply(this,arguments);nkStrictResetClock();return out;};
  /* NK_HOME_FLOW_V3_END */
'''

DASHBOARD = r'''function dashboard(){
    const total=nkHomePreferredTotal(),progress=nkHomeProgressStats(),focus=nkLatestPracticeContext(),focusTitle=focus?.topic||'Choose your next topic',focusCopy=focus?.live?'Pick up exactly where you left off.':focus?.topic?`Continue your recent ${focus.subject||''} practice.`:'Choose a subject and begin focused practice.';
    const attemptedPct=total?Math.min(100,Math.round(progress.attempted/total*100)):0,accuracyPct=Math.min(100,Math.round(progress.accuracy||0)),mins=Math.floor(progress.studyMs/60000),studyText=progress.studyMs?`${Math.floor(mins/60)?Math.floor(mins/60)+'h ':''}${mins%60}m`:'—',studyPct=progress.studyMs?Math.max(8,Math.min(100,Math.round(mins/360*100))):0;
    const streak=currentStreak(),now=new Date(),monday=new Date(now);monday.setHours(0,0,0,0);monday.setDate(monday.getDate()-((monday.getDay()+6)%7));const activeDays=new Set();for(const items of Object.values(state.attempts||{}))for(const a of items||[])if(a?.at)activeDays.add(dayKey(new Date(a.at)));const names=['M','T','W','T','F','S','S'];const week=Array.from({length:7},(_,i)=>{const d=new Date(monday);d.setDate(monday.getDate()+i);return `<span class="nk-home-week-day ${activeDays.has(dayKey(d))?'is-done':''} ${dayKey(d)===dayKey(now)?'is-today':''}"><i></i><b>${names[i]}</b></span>`}).join('');
    const rangeLabels={today:'Today',week:'This Week',month:'This Month',year:'This Year'},bm=bookmarkedQuestions().length,strong=nkStrongestChaptersV3(),recent=(state.tests||[]).slice().sort((a,b)=>b.createdAt-a.createdAt).slice(0,4),review=nkReviewCounts(),forecast=nkReviewForecast(),chartMax=Math.max(1,...forecast);
    return shell(`<div class="nk-home-approved-v1 nk-home-command-center" role="main" aria-label="Home"><header class="nk-home-brandbar"><div class="nk-home-brand"><span class="nk-home-brand-icon">${navIcon('book',22)}</span><span><strong>NK QBank</strong><small>Your Personal Study App</small></span></div><button class="nk-home-search" aria-label="Open study library" onclick="window.QB.nav('study-library')">${navIcon('search',23)}</button></header><section class="nk-home-greeting"><h1>${greetingCopy()} <span>☀️</span></h1><p>Small steps every day lead to big results.</p></section><section class="nk-home-streak-card"><span class="nk-home-streak-flame">🔥</span><div class="nk-home-streak-copy"><strong>${fmtNum(streak)} day streak</strong><small>${streak?'Keep going!':'Start your streak today.'}</small></div><div class="nk-home-week">${week}</div></section><section class="nk-home-focus-card"><div class="nk-home-focus-label">TODAY'S FOCUS</div><h2>${esc(focusTitle)}</h2><p>${esc(focusCopy)}</p><span class="nk-home-focus-heart">♡</span><button class="nk-focus-primary nk-home-focus-action" onclick="window.QB.nkContinueRecentPractice()"><span>Continue Practice</span><span>→</span></button></section><section class="nk-home-quick-grid" aria-label="Review shortcuts"><button onclick="window.QB.nav('fsrs')"><span class="nk-home-quick-icon">${navIcon('refresh',22)}</span><span><strong>FSRS</strong><small>${fmtNum(review.due)} due · wrong & skipped only</small></span>${navIcon('chevron',17)}</button><button onclick="window.QB.nav('bookmarks')"><span class="nk-home-quick-icon is-magenta">${navIcon('bookmark',22)}</span><span><strong>Bookmarks</strong><small>${fmtNum(bm)} saved questions</small></span>${navIcon('chevron',17)}</button></section><section class="nk-v3-section nk-home-subjects"><div class="nk-v3-section-head"><div><small>STUDY LIBRARY</small><h2>My Subjects</h2></div><span>${SUBJECTS.length} subjects</span></div><div class="nk-v3-subject-list">${nkSubjectCardsV3()}</div></section><section class="nk-home-progress"><div class="nk-home-progress-head"><h2>My Progress</h2><label class="nk-home-range"><select aria-label="Progress range" onchange="window.QB.nkSetHomeProgressRange(this.value)">${['today','week','month','year'].map(x=>`<option value="${x}" ${nkHomeProgressRange===x?'selected':''}>${rangeLabels[x]}</option>`).join('')}</select><span>⌄</span></label></div><div class="nk-home-progress-card"><div class="nk-home-progress-row"><span class="nk-home-progress-icon">${navIcon('chart',21)}</span><div><div class="nk-home-progress-copy"><strong>Questions Attempted</strong><b>${fmtNum(progress.attempted)} / ${fmtNum(total)}</b></div><span class="nk-home-progress-track"><i style="width:${attemptedPct}%"></i></span></div></div><div class="nk-home-progress-row"><span class="nk-home-progress-icon is-green">${navIcon('check',21)}</span><div><div class="nk-home-progress-copy"><strong>Accuracy</strong><b>${fmtPct(accuracyPct)}</b></div><span class="nk-home-progress-track is-green"><i style="width:${accuracyPct}%"></i></span></div></div><div class="nk-home-progress-row"><span class="nk-home-progress-icon is-blue">${navIcon('clock',21)}</span><div><div class="nk-home-progress-copy"><strong>Study Time</strong><b>${studyText}</b></div><span class="nk-home-progress-track is-blue"><i style="width:${studyPct}%"></i></span></div></div></div></section><section class="nk-home-quote"><span>“</span><div><strong>Better questions. A brighter you.</strong><small>Keep learning, keep growing.</small></div></section><section class="nk-v3-section"><div class="nk-v3-section-head"><div><small>PERFORMANCE</small><h2>Strongest Chapters</h2></div><button onclick="window.QB.nav('analytics')">Insights ${navIcon('chevron',14)}</button></div>${strong.length?`<div class="nk-v3-compact-list">${strong.map((x,i)=>`<button onclick="window.QB.nkOpenSubjectChapter('${esc(x.subject)}','${esc(x.bank)}','${esc(x.topicId)}')"><span class="nk-v3-rank">${i+1}</span><span><strong>${esc(x.title)}</strong><small>${esc(x.subject)} · ${x.attempted}/${x.total} attempted</small></span><b>${fmtPct(x.accuracy)}</b></button>`).join('')}</div>`:`<div class="nk-v3-empty">Complete some questions and your strongest chapters will appear here.</div>`}</section><section class="nk-v3-section"><div class="nk-v3-section-head"><div><small>RECENT</small><h2>Study Sessions</h2></div><button onclick="window.QB.nav('tests')">Tests ${navIcon('chevron',14)}</button></div>${recent.length?`<div class="nk-v3-session-list">${recent.map(testRow).join('')}</div>`:`<div class="nk-v3-empty">Your completed Practice and Test sessions will appear here.</div>`}</section><section class="nk-v3-section nk-home-review"><div class="nk-v3-section-head"><div><small>SPACED REPETITION</small><h2>Today's Review</h2></div><button onclick="window.QB.nav('fsrs')">Open FSRS ${navIcon('chevron',14)}</button></div><div class="nk-review-metrics"><article><b>${fmtNum(review.due)}</b><small>Due</small></article><article><b>${fmtNum(review.learning+review.relearning)}</b><small>Learning</small></article><article><b>${fmtNum(review.overdue)}</b><small>Overdue</small></article></div><div class="nk-review-chart">${forecast.map((n,i)=>`<span><i style="height:${Math.max(6,Math.round(n/chartMax*52))}px"></i><b>${n}</b><small>${i===0?'Today':'+'+i}</small></span>`).join('')}</div></section></div>`,'dashboard');
  }'''

BOTTOM_NAV = r'''function bottomNav(active){const items=[['dashboard','Home','home'],['fsrs','FSRS','refresh'],['tests','Tests','test'],['analytics','Insights','chart'],['more','More','more']];return `<nav class="bottom-nav nk-bottom-nav-v114" aria-label="Primary navigation">${items.map(([id,label,icon])=>`<button class="nav-item ${active===id?'active':''}" onclick="window.QB.nav('${id}')" aria-current="${active===id?'page':'false'}"><span class="nav-icon-wrap">${navIcon(icon,21)}</span><span class="nav-label">${label}</span></button>`).join('')}</nav>`;}'''

TESTS_PAGE = r'''function testsPage(){const mode=nkTestSetup.mode,source=nkTestSetup.source;const cards=[['all','book','Full Question Bank','Choose subjects and topics'],['custom','grid','Custom Module','Build a module from selected subjects or topics'],['wrong','close','Wrong Questions','Focus on questions answered incorrectly'],['bookmarks','bookmark','Bookmarked Questions','Use questions you saved']];const note=mode==='exam'?`${nkTestSetup.count} questions = ${nkTestSetup.count} minutes total. Spend that total time across questions however you need.`:'Practice has no limiting countdown. Time is still recorded for your analysis.';return shell(`<main class="nk-new-test-v2" aria-label="New Test"><header class="nk-test-page-head"><button aria-label="Back" onclick="window.QB.nav('dashboard')">${navIcon('back',24)}</button><h1>New Test</h1></header><div class="nk-test-mode-tabs"><button class="${mode==='exam'?'active':''}" onclick="window.QB.nkSetTestMode('exam')">Timed Test</button><button class="${mode==='practice'?'active':''}" onclick="window.QB.nkSetTestMode('practice')">Practice</button></div><section class="nk-test-setup-section"><h2>Question Source</h2><p>Choose where to get questions from.</p><div class="nk-test-source-list">${cards.map(([key,icon,title,meta])=>`<button class="nk-test-source-card ${source===key?'active':''}" onclick="${key==='custom'?'window.QB.nkOpenCustomSource()':`window.QB.nkSetTestSource('${key}')`}"><span class="nk-test-source-icon is-${key}">${navIcon(icon,23)}</span><span><strong>${title}</strong><small>${meta}</small></span>${navIcon('chevron',20)}</button>`).join('')}</div></section><section class="nk-test-setup-section"><h2>Number of Questions</h2><p>Choose how many questions to include.</p><div class="nk-test-count-grid">${[10,20,50,100].map(n=>`<button class="${nkTestSetup.count===n?'active':''}" onclick="window.QB.nkSetTestCount(${n})">${n}</button>`).join('')}</div></section><div class="nk-test-budget-note">${navIcon('clock',18)}<span>${esc(note)}</span></div><button class="nk-test-start" onclick="window.QB.nkStartConfiguredTest()">${mode==='exam'?'Start Timed Test':'Start Practice'} <span>→</span></button></main>`,'tests');}'''

EXAM_PAGE = r'''function examPage(){const s=state.activeSession;if(!s||s.mode!=='exam')return dashboard();const q=BY_ID[s.questionIds[s.index]]||nkFindStudyQuestion(s.questionIds[s.index]);if(!q)return dashboard();const selected=s.answers[q.id]||null,strict=s.timerMode==='per-question',locked=Boolean(s.strictExpired?.[String(q.id)]);let remaining;if(strict){remaining=Math.max(0,60-Math.floor(nkStrictSpent(s,String(q.id))/1000));}else{remaining=Math.max(0,s.questionIds.length*60-Math.floor((Date.now()-s.startedAt)/1000));}const timer=strict?`<div class="nk-exam-strip"><span>Topic Test · 60 sec this question</span><strong id="exam-timer" class="timer ${remaining<15?'danger':remaining<30?'warn':''}">${locked?'Time expired':formatTimer(remaining)}</strong></div>`:`<div class="nk-exam-strip"><span>Timed Test · ${s.questionIds.length} min total</span><strong id="exam-timer" class="timer ${remaining<120?'danger':remaining<300?'warn':''}">${formatTimer(remaining)}</strong></div>`;const options=locked?q.options.map(o=>{const n=o.letter.charCodeAt(0)-64,chosen=Number(selected)===n;return `<div class="option ${chosen?'selected':''}"><span class="option-letter">${o.letter}</span><span class="option-text">${esc(o.text)}</span></div>`;}).join(''):nkSessionOptions(q,selected,'exam',false);return sessionShell(`<div class="nk-v114-session is-exam">${nkSessionHeader(q,s,'exam',timer)}<div class="question-shell"><section class="question-card">${nkQuestionContext(q)}<div class="question-text" data-marrow-question="${q.bank==='Marrow'?esc(String(q.id)):''}">${esc(q.question)}</div><div class="option-list">${options}</div></section></div></div>`,'tests')+nkSessionActionBar(s,'exam');}'''

START_TICKER = r'''function startExamTicker(){clearInterval(ticker);const current=state.activeSession;if(!current||current.mode!=='exam')return;ticker=setInterval(()=>{const s=state.activeSession;if(!s||s.mode!=='exam'){clearInterval(ticker);return;}let remaining;if(s.timerMode==='per-question'){const id=String(s.questionIds[s.index]);remaining=60-Math.floor(nkStrictSpent(s,id)/1000);const el=document.getElementById('exam-timer');if(el){el.textContent=remaining<=0?'Time expired':formatTimer(Math.max(0,remaining));el.className='timer '+(remaining<15?'danger':remaining<30?'warn':'');}if(remaining<=0){clearInterval(ticker);nkExpireTopicQuestion();}}else{remaining=s.questionIds.length*60-Math.floor((Date.now()-s.startedAt)/1000);const el=document.getElementById('exam-timer');if(el){el.textContent=formatTimer(Math.max(0,remaining));el.className='timer '+(remaining<120?'danger':remaining<300?'warn':'');}if(remaining<=0){clearInterval(ticker);submitExam(true);}}},250);}'''

SUBMIT_EXAM = r'''function submitExam(auto=false){closeQuestionNavigator();const s=state.activeSession;if(!s||s.mode!=='exam')return;if(s.timerMode==='per-question')nkStrictCommitCurrent();saveExamElapsed();const qt=s.questionTimes||{},strict=s.timerMode==='per-question';let correct=0,incorrect=0,attempted=0;Object.entries(s.answers||{}).forEach(([id,sel])=>{if(!sel)return;attempted++;const q=BY_ID[id]||nkFindStudyQuestion(id),ok=q&&Number(q.correctOption)===Number(sel);if(ok)correct++;else incorrect++;recordAttempt(id,sel,qt[id]||0,'exam');});const unattempted=s.questionIds.length-attempted;nkMarkSkippedFromSession(s);const raw=Date.now()-s.startedAt,totalTimeMs=strict?s.questionIds.reduce((n,id)=>n+Math.min(60000,Math.max(Number(qt[id]||0),Number(s.strictQuestionTime?.[id]||0))),0):Math.min(raw,s.questionIds.length*60000);const test={id:`t_${Date.now()}_${Math.random().toString(16).slice(2)}`,title:s.title,questionIds:[...s.questionIds],answers:{...s.answers},questionTimes:{...qt},correct,incorrect,unattempted,total:s.questionIds.length,attempted,totalTimeMs,createdAt:Date.now(),autoSubmitted:auto,timerEnabled:true,timerMode:s.timerMode||'global',originRoute:s.originRoute};state.tests.push(test);state.tests=state.tests.slice(-100);state.activeSession=null;saveState();document.querySelectorAll('#toast-root .toast').forEach(e=>e.remove());navigate('result',test.id);}'''

CSS = r'''<style id="nk-home-command-center-v1">
body:has(.nk-home-approved-v1),body:has(.nk-study-library-v3),body:has(.nk-fsrs-page-v3),body:has(.nk-new-test-v2){background:#f6f7fb}.nk-home-approved-v1,.nk-study-library-v3,.nk-fsrs-page-v3,.nk-new-test-v2{max-width:760px;margin:0 auto;padding:8px 0 32px;color:#151852}.nk-home-brandbar{display:flex;align-items:center;justify-content:space-between;padding:4px 1px 12px}.nk-home-brand{display:flex;align-items:center;gap:10px}.nk-home-brand-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;color:#fff;background:linear-gradient(135deg,#7561ff,#5848e9)}.nk-home-brand span:last-child{display:grid}.nk-home-brand strong{font-size:17px}.nk-home-brand small{font-size:10px;color:#7c80a4}.nk-home-search{border:0;background:transparent;color:#151852;width:44px}.nk-home-greeting{padding:11px 2px 17px}.nk-home-greeting h1{margin:0;font-size:32px;line-height:1.08;font-weight:900;letter-spacing:-1px}.nk-home-greeting p{margin:5px 0 0;color:#7d81a7;font-size:12px}.nk-home-streak-card{display:grid;grid-template-columns:44px minmax(92px,1fr) auto;align-items:center;gap:10px;padding:12px 14px;border:1px solid #ebeaf5;border-radius:17px;background:#fff;box-shadow:0 5px 20px rgba(39,42,101,.045)}.nk-home-streak-flame{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:#ff8c32;font-size:22px}.nk-home-streak-copy{display:grid}.nk-home-streak-copy strong{font-size:13px}.nk-home-streak-copy small{font-size:9px;color:#8a8eaa}.nk-home-week{display:flex;gap:8px}.nk-home-week-day{display:grid;gap:5px;place-items:center}.nk-home-week-day i{width:13px;height:13px;border-radius:50%;background:#e3e5f1}.nk-home-week-day.is-done i{background:#7459ef}.nk-home-week-day.is-today i{box-shadow:0 0 0 3px #eeeaff}.nk-home-week-day b{font-size:8px;color:#777b9f}.nk-home-focus-card{position:relative;overflow:hidden;margin-top:14px;padding:20px;border-radius:20px;background:linear-gradient(135deg,#3f3799,#302b78);color:#fff;box-shadow:0 14px 30px rgba(52,46,130,.22)}.nk-home-focus-label{font-size:9px;letter-spacing:.18em;font-weight:800;opacity:.76}.nk-home-focus-card h2{max-width:80%;margin:8px 0 4px;font-size:22px}.nk-home-focus-card p{max-width:82%;margin:0 0 15px;font-size:11px;line-height:1.45;color:#d8d7ef}.nk-home-focus-heart{position:absolute;right:24px;top:34px;font-size:54px;opacity:.16}.nk-home-focus-action{width:100%;min-height:46px;border:0;border-radius:12px;background:#fff;color:#5d36ed;font-weight:850;display:flex;align-items:center;justify-content:center;gap:10px}.nk-home-quick-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:11px}.nk-home-quick-grid button{min-height:72px;border:1px solid #e8e8f2;border-radius:16px;background:#fff;display:grid;grid-template-columns:38px 1fr 18px;align-items:center;gap:10px;padding:11px;text-align:left;color:#1a1d5f}.nk-home-quick-grid button>span:nth-child(2){display:grid}.nk-home-quick-grid strong{font-size:12px}.nk-home-quick-grid small{font-size:9px;color:#8b8fa9;margin-top:3px}.nk-home-quick-icon{width:36px;height:36px;border-radius:11px;display:grid;place-items:center;background:#f0edff;color:#6d52f3}.nk-home-quick-icon.is-magenta{background:#fff1f7;color:#b6478a}.nk-v3-section{margin-top:24px}.nk-v3-section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:9px}.nk-v3-section-head small{font-size:8px;letter-spacing:.12em;font-weight:850;color:#7265c7}.nk-v3-section-head h2{margin:3px 0 0;font-size:18px}.nk-v3-section-head>span,.nk-v3-section-head>button{border:0;background:transparent;color:#72769a;font-size:10px}.nk-v3-subject-list{display:grid;gap:9px}.nk-v3-subject-card{display:grid;grid-template-columns:44px 1fr 42px 18px;gap:11px;align-items:center;width:100%;padding:12px 13px;border:1px solid #e7e8f0;border-radius:17px;background:#fff;text-align:left;color:#181b58}.nk-v3-subject-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:#f1efff;color:#6a53e8}.nk-v3-subject-card.is-physiology .nk-v3-subject-icon{background:#fff0ee;color:#c2534b}.nk-v3-subject-card.is-anatomy .nk-v3-subject-icon{background:#edf7fc;color:#277899}.nk-v3-subject-card.is-biochemistry .nk-v3-subject-icon{background:#f9edf6;color:#a22a80}.nk-v3-subject-copy{display:grid;min-width:0}.nk-v3-subject-copy strong{font-size:13px}.nk-v3-subject-copy small{font-size:9.5px;color:#8589a6;margin-top:2px}.nk-v3-subject-progress{height:5px;margin-top:8px;border-radius:99px;background:#eceef5;overflow:hidden}.nk-v3-subject-progress i{display:block;height:100%;background:#7459ef}.nk-v3-subject-card>b{font-size:10px;text-align:right}.nk-home-progress{margin-top:24px}.nk-home-progress-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}.nk-home-progress-head h2{margin:0;font-size:18px}.nk-home-range{display:flex;align-items:center;color:#676b96;font-size:10px}.nk-home-range select{appearance:none;border:0;background:transparent;padding:8px 15px 8px 8px;color:inherit;font:inherit;font-weight:750}.nk-home-range>span{margin-left:-13px;pointer-events:none}.nk-home-progress-card{padding:4px 14px;border:1px solid #e9eaf2;border-radius:18px;background:#fff}.nk-home-progress-row{display:grid;grid-template-columns:40px 1fr;gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid #f0f1f5}.nk-home-progress-row:last-child{border-bottom:0}.nk-home-progress-icon{width:35px;height:35px;border-radius:11px;display:grid;place-items:center;background:#efedff;color:#6d52f3}.nk-home-progress-icon.is-green{background:#e6f9ef;color:#20ad70}.nk-home-progress-icon.is-blue{background:#e9f3ff;color:#3295ed}.nk-home-progress-copy{display:flex;justify-content:space-between;gap:10px;font-size:10px}.nk-home-progress-track{display:block;height:6px;margin-top:7px;border-radius:999px;background:#ececf5;overflow:hidden}.nk-home-progress-track i{display:block;height:100%;background:#7357ef}.nk-home-progress-track.is-green i{background:#24c879}.nk-home-progress-track.is-blue i{background:#319cf4}.nk-home-quote{display:flex;align-items:center;gap:12px;margin-top:16px;padding:13px 16px;border-radius:16px;background:linear-gradient(100deg,#f4efff,#f7f2ff)}.nk-home-quote>span{font-size:26px;color:#6b45ef}.nk-home-quote div{display:grid}.nk-home-quote strong{font-size:11px}.nk-home-quote small{font-size:9px;color:#8689a8}.nk-v3-compact-list,.nk-v3-session-list{overflow:hidden;border:1px solid #e7e8f0;border-radius:16px;background:#fff}.nk-v3-compact-list>button{display:grid;grid-template-columns:30px 1fr 48px;gap:10px;align-items:center;width:100%;padding:11px 12px;border:0;border-bottom:1px solid #ececf3;background:#fff;text-align:left;color:#181b58}.nk-v3-compact-list>button:last-child{border-bottom:0}.nk-v3-compact-list strong,.nk-v3-compact-list small{display:block}.nk-v3-compact-list strong{font-size:11px}.nk-v3-compact-list small{font-size:9px;color:#898ca4;margin-top:3px}.nk-v3-rank{width:28px;height:28px;border-radius:9px;background:#f1efff;display:grid;place-items:center;color:#6b55df;font-size:10px;font-weight:850}.nk-v3-empty{padding:20px;border:1px solid #e7e8f0;border-radius:16px;background:#fff;color:#8589a6;font-size:11px;text-align:center}.nk-review-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.nk-review-metrics article{padding:12px;border:1px solid #e8e8f1;border-radius:14px;background:#fff}.nk-review-metrics b,.nk-review-metrics small{display:block}.nk-review-metrics b{font-size:21px}.nk-review-metrics small{font-size:9px;color:#8589a6;margin-top:2px;text-transform:uppercase}.nk-review-chart{height:88px;margin-top:10px;padding:9px 10px 5px;border:1px solid #ebeaf3;border-radius:15px;background:#fff;display:flex;align-items:flex-end;gap:8px}.nk-review-chart span{height:100%;flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px}.nk-review-chart i{display:block;width:100%;max-width:30px;border-radius:6px 6px 2px 2px;background:#7a62ed}.nk-review-chart b{font-size:8px}.nk-review-chart small{font-size:7px;color:#8a8da5}.nk-v3-page-hero{padding:8px 2px 18px}.nk-v3-page-hero h1{font-size:30px;margin:5px 0}.nk-v3-page-hero p{margin:0;max-width:560px;color:#7b809d;font-size:12px;line-height:1.5}.nk-v3-page-note{font-size:10px;color:#8b8fa6;text-align:center;margin:12px}.nk-fsrs-subject-list{display:grid;gap:8px}.nk-fsrs-subject-card{display:grid;grid-template-columns:42px 1fr 18px;gap:11px;align-items:center;padding:12px;border:1px solid #e7e8f0;border-radius:15px;background:#fff;text-align:left;color:#171a58}.nk-fsrs-subject-card>span:first-child{width:38px;height:38px;border-radius:11px;background:#f0edff;color:#6d52f3;display:grid;place-items:center}.nk-fsrs-subject-card>span:nth-child(2){display:grid}.nk-fsrs-subject-card strong{font-size:12px}.nk-fsrs-subject-card small{font-size:9px;color:#898da7;margin-top:3px}.nk-fsrs-subject-card.is-active{border-color:#a99bf4;background:#faf9ff}.nk-v3-primary{width:100%;min-height:50px;margin-top:12px;border:0;border-radius:14px;background:#423790;color:#fff;font-weight:850}.nk-test-page-head{display:flex;align-items:center;gap:10px;padding:4px 0 14px}.nk-test-page-head button{border:0;background:transparent;color:#151852}.nk-test-page-head h1{margin:0;font-size:26px}.nk-test-mode-tabs{display:grid;grid-template-columns:1fr 1fr;padding:2px;border:1px solid #dedff0;border-radius:16px}.nk-test-mode-tabs button{min-height:50px;border:0;border-radius:14px;background:transparent;color:#565a8c;font-weight:850}.nk-test-mode-tabs button.active{background:linear-gradient(135deg,#8a73ff,#674ce9);color:#fff}.nk-test-setup-section{margin-top:24px}.nk-test-setup-section h2{margin:0;font-size:18px}.nk-test-setup-section>p{margin:4px 0 12px;font-size:11px;color:#8185a5}.nk-test-source-list{display:grid;gap:8px}.nk-test-source-card{display:grid;grid-template-columns:46px 1fr 22px;gap:12px;align-items:center;padding:12px;border:1px solid #e6e7ef;border-radius:17px;background:#fff;text-align:left;color:#171a58}.nk-test-source-card>span:nth-child(2){display:grid}.nk-test-source-card strong{font-size:13px}.nk-test-source-card small{font-size:10px;color:#8589a7;margin-top:3px}.nk-test-source-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:#efedff;color:#6951e6}.nk-test-source-icon.is-wrong{background:#ffecef;color:#e94d65}.nk-test-source-icon.is-bookmarks{background:#fff2e6;color:#f38a29}.nk-test-source-icon.is-custom{background:#eaf3ff;color:#378ff0}.nk-test-count-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.nk-test-count-grid button{min-height:54px;border:1px solid #e0e1ed;border-radius:15px;background:#fff;color:#1d205f;font-weight:850}.nk-test-count-grid button.active{border-color:#a99bf4;background:#f0edff;color:#4d30d5}.nk-test-budget-note{display:flex;align-items:flex-start;gap:9px;margin-top:18px;padding:12px;border-radius:13px;background:#f2f0ff;color:#5d5681;font-size:10px;line-height:1.45}.nk-test-start{width:100%;min-height:58px;margin-top:16px;border:0;border-radius:18px;background:linear-gradient(135deg,#413993,#302b78);color:#fff;font-size:17px;font-weight:900}.nk-fsrs-settings label[for="fsrs-newCardLimit"]{display:none!important}
@media(max-width:560px){.nk-home-approved-v1,.nk-study-library-v3,.nk-fsrs-page-v3,.nk-new-test-v2{padding-left:4px;padding-right:4px}.nk-home-greeting h1{font-size:29px}.nk-home-week{gap:6px}.nk-home-streak-card{grid-template-columns:42px minmax(80px,1fr) auto}.nk-test-count-grid{gap:7px}}@media(max-width:390px){.nk-home-week{gap:4px}.nk-home-week-day i{width:11px;height:11px}.nk-home-quick-grid{grid-template-columns:1fr}.nk-test-count-grid{grid-template-columns:1fr 1fr}}@media(prefers-reduced-motion:reduce){.nk-home-approved-v1 *,.nk-study-library-v3 *,.nk-fsrs-page-v3 *,.nk-new-test-v2 *{transition:none!important;animation:none!important}}
</style>'''


def replace_function(source: str, name: str, replacement: str) -> str:
    start=source.find(f"function {name}(")
    if start<0: raise SystemExit(f"{name} not found")
    brace=source.find("{",start)
    if brace<0: raise SystemExit(f"{name} opening brace not found")
    depth=0;mode='code';quote=None;escaped=False;line_comment=False;block_comment=False;interp=[];i=brace
    while i<len(source):
        c=source[i];n=source[i+1] if i+1<len(source) else ''
        if line_comment:
            if c=='\n':line_comment=False
            i+=1;continue
        if block_comment:
            if c=='*' and n=='/':block_comment=False;i+=2
            else:i+=1
            continue
        if quote:
            if escaped:escaped=False
            elif c=='\\':escaped=True
            elif c==quote:quote=None
            i+=1;continue
        if mode=='template':
            if escaped:escaped=False;i+=1;continue
            if c=='\\':escaped=True;i+=1;continue
            if c=='`':mode='code';i+=1;continue
            if c=='$' and n=='{':depth+=1;interp.append(depth);mode='code';i+=2;continue
            i+=1;continue
        if c=='/' and n=='/':line_comment=True;i+=2;continue
        if c=='/' and n=='*':block_comment=True;i+=2;continue
        if c in "'\"":quote=c;i+=1;continue
        if c=='`':mode='template';i+=1;continue
        if c=='{':depth+=1;i+=1;continue
        if c=='}':
            if interp and depth==interp[-1]:depth-=1;interp.pop();mode='template';i+=1;continue
            depth-=1
            if depth==0:return source[:start]+replacement.rstrip()+source[i+1:]
            i+=1;continue
        i+=1
    raise SystemExit(f"{name} end not found")


def transform(source: str) -> str:
    if FLOW_MARKER in source:return source
    if 'NK_CUSTOM_STUDY_MODULES_V1' not in source and 'openStudyModuleBuilder' not in source:raise SystemExit('Home V3 must run after Custom Study Modules')
    source=replace_function(source,'dashboard',HELPERS+'\n'+DASHBOARD)
    source=replace_function(source,'bottomNav',BOTTOM_NAV)
    source=replace_function(source,'testsPage',TESTS_PAGE)
    source=replace_function(source,'examPage',EXAM_PAGE)
    source=replace_function(source,'startExamTicker',START_TICKER)
    source=replace_function(source,'submitExam',SUBMIT_EXAM)
    route_anchor="else if(route.page==='more') out=morePage();"
    if route_anchor not in source:raise SystemExit('render route anchor missing')
    source=source.replace(route_anchor,"else if(route.page==='study-library') out=nkStudyLibraryPage();\n    else if(route.page==='fsrs') out=nkFsrsReviewPage();\n    "+route_anchor,1)
    topic_exam="onclick=\"window.QB.openSessionBuilder('${c.id}','exam')\""
    if topic_exam not in source:raise SystemExit('topic timed-test action anchor missing')
    source=source.replace(topic_exam,"onclick=\"window.QB.nkStartTopicTimedTest('${c.id}')\"",1)
    subject_switch="onclick=\"window.QB.openSubjectTopics('${esc(x.subject)}')\""
    if subject_switch not in source:raise SystemExit('Topics subject-switch anchor missing')
    source=source.replace(subject_switch,"onclick=\"window.QB.nkOpenSubjectLibrary('${esc(x.subject)}')\"")
    bridge='window.QB={'
    if bridge not in source:raise SystemExit('window.QB bridge not found')
    exports="nkOpenSubjectLibrary,nkOpenSubjectChapter,nkContinueRecentPractice,nkSetHomeProgressRange,nkSetFsrsSubject,nkStartReviewOnly,nkOpenNewTest,nkSetTestMode,nkSetTestSource,nkSetTestCount,nkOpenCustomSource,nkStartConfiguredTest,nkStartTopicTimedTest,nkExpireTopicQuestion,"
    source=source.replace(bridge,bridge+exports,1)
    source=re.sub(r'<style id="nk-home-command-center-v1">[\s\S]*?</style>','',source,count=1)
    if '</head>' not in source:raise SystemExit('closing head not found')
    source=source.replace('</head>',CSS+'\n</head>',1)
    required=[FLOW_MARKER,'My Subjects','Strongest Chapters','Study Sessions',"Today's Review",'FSRS Review','wrong or encountered and skipped','Unseen QBank questions are never introduced','study-library',"['fsrs','FSRS'",'Full Question Bank','Custom Module','questions = ${nkTestSetup.count} minutes total',"timerMode='per-question'",'nkExpireTopicQuestion','Time expired','nkStartTopicTimedTest','nkOpenSubjectLibrary','nkSessionQuestionEncountered','nkMarkSkippedFromSession(s)']
    missing=[x for x in required if x not in source]
    if missing:raise SystemExit(f'Home V3 markers missing: {missing}')
    return source


def main() -> None:
    source=HTML.read_text(encoding='utf-8');HTML.write_text(transform(source),encoding='utf-8')
    print('HOME_FLOW_V3_OK: hybrid Home, subject→Topics, FSRS review-only queue, global timed-test budget, strict topic timer')

if __name__=='__main__':main()
