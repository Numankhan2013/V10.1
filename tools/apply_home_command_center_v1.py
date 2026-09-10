#!/usr/bin/env python3
"""Install the approved NK QBank Home + New Test flows.

Owns only the Home dashboard and the New Test setup surface. It deliberately
reuses the established practice/exam/custom-module engines underneath so Marrow,
Topics, question rendering, review, FSRS, and source fidelity stay untouched.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
STYLE_ID = "nk-home-command-center-v1"
FLOW_MARKER = "NK_HOME_FLOW_V2"

HOME_HELPERS = r'''
  /* NK_HOME_FLOW_V2_START */
  let nkHomeProgressRange='week';
  let nkTestSetup={mode:'exam',source:'all',timer:true,count:20};

  function nkAllStudyQuestions(){
    if(typeof nkAllBankQuestions==='function') return nkAllBankQuestions();
    if(typeof nkAllQuestionBank==='function') return nkAllQuestionBank();
    return Array.isArray(QUESTIONS)?QUESTIONS:[];
  }
  function nkSubjectRecordForQuestion(q){
    if(!q)return null;
    return (SUBJECTS||[]).find(r=>r.subject===q.subject)||null;
  }
  function nkTopicTitleForQuestion(q){
    if(!q)return '';
    const rec=nkSubjectRecordForQuestion(q);
    const topic=(rec?.topics||[]).find(t=>String(t.id)===String(q.chapterId));
    return topic?.title||q.topic||q.chapter||'';
  }
  function nkLatestPracticeContext(){
    const live=state.activeSession;
    if(live?.mode==='practice'&&Array.isArray(live.questionIds)&&live.questionIds.length){
      const q=BY_ID[String(live.questionIds[Math.max(0,Math.min(live.index||0,live.questionIds.length-1))])];
      if(q)return {q,topic:nkTopicTitleForQuestion(q),subject:q.subject||activeSubject,live:true};
    }
    let latest=null;
    for(const [qid,attempts] of Object.entries(state.attempts||{})){
      for(const a of attempts||[]){
        if(!a||a.source==='exam'||!a.at)continue;
        if(!latest||Number(a.at)>Number(latest.at))latest={qid:String(qid),at:Number(a.at)};
      }
    }
    const q=latest?BY_ID[String(latest.qid)]:null;
    return q?{q,topic:nkTopicTitleForQuestion(q),subject:q.subject||activeSubject,live:false}:null;
  }
  function nkTopicQuestionIds(q){
    if(!q)return [];
    const bank=q.bank||'';
    return nkAllStudyQuestions().filter(x=>x.subject===q.subject&&String(x.chapterId)===String(q.chapterId)&&(!bank||!x.bank||x.bank===bank)).map(x=>x.id);
  }
  function nkContinueRecentPractice(){
    if(state.activeSession?.mode==='practice'&&state.activeSession?.questionIds?.length){navigate('practice');return;}
    const ctx=nkLatestPracticeContext();
    if(ctx?.q){
      const ids=nkTopicQuestionIds(ctx.q);
      if(ids.length){activeSubject=ctx.subject||activeSubject;localStorage.setItem('qbank_active_subject_v1',activeSubject);startSession(ids,'practice',ctx.topic||`${activeSubject} Practice`);return;}
    }
    nkOpenPracticeSubjects();
  }
  function nkPracticeSubjectMarkup(){
    return (SUBJECTS||[]).map((record,index)=>`<button class="nk-flow-choice" onclick="window.QB.nkOpenPracticeTopics(${index})"><span class="nk-flow-choice-icon">${nkAppSubjectIcon(record.subject,22)}</span><span><strong>${esc(record.subject)}</strong><small>${fmtNum((record.topics||[]).length)} topics · ${fmtNum((record.questions||[]).length)} questions</small></span>${navIcon('chevron',18)}</button>`).join('');
  }
  function nkOpenPracticeSubjects(){
    closeModal();
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-flow-backdrop" id="modal"><div class="modal nk-flow-modal"><button class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button><div class="nk-flow-modal-head"><span>${navIcon('book',22)}</span><div><small>PRACTICE</small><h3>Choose a subject</h3><p>Pick a subject, then choose the topic you want to practise.</p></div></div><div class="nk-flow-choice-list">${nkPracticeSubjectMarkup()}</div></div></div>`);
  }
  function nkOpenPracticeTopics(index){
    const record=(SUBJECTS||[])[Number(index)];if(!record)return;
    const topics=(record.topics||[]).filter(t=>Number(t.questionCount||0)>0);
    closeModal();
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-flow-backdrop" id="modal"><div class="modal nk-flow-modal"><button class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button><button class="nk-flow-back" onclick="window.QB.nkOpenPracticeSubjects()">${navIcon('back',16)} Subjects</button><div class="nk-flow-modal-head"><span>${nkAppSubjectIcon(record.subject,22)}</span><div><small>${esc(record.subject)}</small><h3>Choose a topic</h3><p>Opening a topic starts Practice immediately.</p></div></div><div class="nk-flow-choice-list">${topics.map(t=>`<button class="nk-flow-choice" onclick="window.QB.nkStartTopicPractice(${Number(index)},'${esc(String(t.id))}')"><span><strong>${esc(t.title)}</strong><small>${fmtNum(t.questionCount||0)} questions</small></span>${navIcon('chevron',18)}</button>`).join('')||`<div class="nk-flow-empty">No topics with questions are available.</div>`}</div></div></div>`);
  }
  function nkStartTopicPractice(index,topicId){
    const record=(SUBJECTS||[])[Number(index)];if(!record)return;
    const topic=(record.topics||[]).find(t=>String(t.id)===String(topicId));
    const ids=(record.questions||[]).filter(q=>String(q.chapterId)===String(topicId)).map(q=>q.id);
    if(!ids.length){showToast('No questions available for this topic.','bad');return;}
    activeSubject=record.subject;localStorage.setItem('qbank_active_subject_v1',activeSubject);closeModal();
    startSession(ids,'practice',topic?.title||`${record.subject} Practice`);
  }
  function nkHomeRangeStart(range){
    const now=new Date(),d=new Date(now);d.setHours(0,0,0,0);
    if(range==='today')return d.getTime();
    if(range==='week'){d.setDate(d.getDate()-((d.getDay()+6)%7));return d.getTime();}
    if(range==='month'){d.setDate(1);return d.getTime();}
    d.setMonth(0,1);return d.getTime();
  }
  function nkHomeProgressStats(range=nkHomeProgressRange){
    const start=nkHomeRangeStart(range),attempts=[];const qids=new Set();
    for(const [qid,items] of Object.entries(state.attempts||{}))for(const a of items||[])if(Number(a?.at||0)>=start){attempts.push(a);qids.add(String(qid));}
    const correct=attempts.filter(a=>a.correct).length;
    const practiceMs=attempts.filter(a=>a.source!=='exam').reduce((sum,a)=>sum+Math.max(0,Number(a.timeSpent)||0),0);
    const testMs=(state.tests||[]).filter(t=>Number(t?.createdAt||0)>=start).reduce((sum,t)=>sum+Math.max(0,Number(t.totalTimeMs)||0),0);
    return {attempted:qids.size,attempts:attempts.length,accuracy:attempts.length?correct/attempts.length*100:0,studyMs:practiceMs+testMs};
  }
  function nkSetHomeProgressRange(value){
    if(!['today','week','month','year'].includes(value))return;nkHomeProgressRange=value;render();
  }
  function nkOpenNewTest(mode='exam'){nkTestSetup.mode=mode==='practice'?'practice':'exam';navigate('tests');}
  function nkSetTestMode(mode){nkTestSetup.mode=mode==='practice'?'practice':'exam';render();}
  function nkSetTestSource(source){if(['all','wrong','bookmarks'].includes(source)){nkTestSetup.source=source;render();}}
  function nkSetTestTimer(enabled){nkTestSetup.timer=Boolean(enabled);render();}
  function nkSetTestCount(count){nkTestSetup.count=[10,20,50,100].includes(Number(count))?Number(count):20;render();}
  function nkStartConfiguredIds(ids,title){
    const list=[...new Set((ids||[]).map(String))];if(!list.length){showToast('No questions available for this selection.','bad');return;}
    for(let i=list.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[list[i],list[j]]=[list[j],list[i]];}
    const count=Math.min(nkTestSetup.count,list.length),mode=nkTestSetup.mode==='exam'?'exam':'practice';
    closeModal();startSession(list.slice(0,count),mode,title);
    if(mode==='exam'&&state.activeSession){state.activeSession.timerEnabled=Boolean(nkTestSetup.timer);saveState();render();}
  }
  function nkOpenTestSubjects(){
    closeModal();
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-flow-backdrop" id="modal"><div class="modal nk-flow-modal"><button class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button><div class="nk-flow-modal-head"><span>${navIcon(nkTestSetup.mode==='exam'?'test':'book',22)}</span><div><small>${nkTestSetup.mode==='exam'?'TIMED TEST':'PRACTICE'}</small><h3>Choose a subject</h3><p>Choose a subject, then a topic.</p></div></div><div class="nk-flow-choice-list">${(SUBJECTS||[]).map((r,i)=>`<button class="nk-flow-choice" onclick="window.QB.nkOpenTestTopics(${i})"><span class="nk-flow-choice-icon">${nkAppSubjectIcon(r.subject,22)}</span><span><strong>${esc(r.subject)}</strong><small>${fmtNum((r.topics||[]).length)} topics</small></span>${navIcon('chevron',18)}</button>`).join('')}</div></div></div>`);
  }
  function nkOpenTestTopics(index){
    const r=(SUBJECTS||[])[Number(index)];if(!r)return;const topics=(r.topics||[]).filter(t=>Number(t.questionCount||0)>0);
    closeModal();
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-flow-backdrop" id="modal"><div class="modal nk-flow-modal"><button class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button><button class="nk-flow-back" onclick="window.QB.nkOpenTestSubjects()">${navIcon('back',16)} Subjects</button><div class="nk-flow-modal-head"><span>${nkAppSubjectIcon(r.subject,22)}</span><div><small>${esc(r.subject)}</small><h3>Choose a topic</h3><p>Tap a topic to ${nkTestSetup.mode==='exam'?'start the test':'start practice'}.</p></div></div><div class="nk-flow-choice-list">${topics.map(t=>`<button class="nk-flow-choice" onclick="window.QB.nkStartConfiguredTopic(${Number(index)},'${esc(String(t.id))}')"><span><strong>${esc(t.title)}</strong><small>${fmtNum(t.questionCount||0)} questions</small></span>${navIcon('chevron',18)}</button>`).join('')}</div></div></div>`);
  }
  function nkStartConfiguredTopic(index,topicId){
    const r=(SUBJECTS||[])[Number(index)];if(!r)return;const topic=(r.topics||[]).find(t=>String(t.id)===String(topicId));
    const ids=(r.questions||[]).filter(q=>String(q.chapterId)===String(topicId)).map(q=>q.id);
    activeSubject=r.subject;localStorage.setItem('qbank_active_subject_v1',activeSubject);
    nkStartConfiguredIds(ids,`${topic?.title||r.subject}${nkTestSetup.mode==='exam'?' Test':' Practice'}`);
  }
  function nkConfiguredQueueIds(source){
    const all=nkAllStudyQuestions();
    if(source==='wrong')return all.filter(q=>qAttempts(q.id).some(a=>!a.correct)).map(q=>q.id);
    if(source==='bookmarks')return all.filter(q=>state.bookmarks?.[q.id]).map(q=>q.id);
    return [];
  }
  function nkStartConfiguredTest(){
    if(nkTestSetup.source==='all'){nkOpenTestSubjects();return;}
    const ids=nkConfiguredQueueIds(nkTestSetup.source);
    nkStartConfiguredIds(ids,nkTestSetup.source==='wrong'?'Wrong Questions':'Bookmarked Questions');
  }
  /* NK_HOME_FLOW_V2_END */
'''

DASHBOARD = r'''function dashboard() {
    const total=nkAllStudyQuestions().length;
    const progress=nkHomeProgressStats();
    const due=pendingReviewCount();
    const bm=bookmarkedQuestions().length;
    const focus=nkLatestPracticeContext();
    const focusTitle=focus?.topic||'Choose your next topic';
    const focusCopy=focus?.live?'Pick up exactly where you left off.':focus?.topic?`Continue your recent ${focus.subject||''} practice.`:'Your next practice session is one tap away.';
    const attemptedPct=total?Math.max(0,Math.min(100,Math.round(progress.attempted/total*100))):0;
    const accuracyPct=Math.max(0,Math.min(100,Math.round(progress.accuracy||0)));
    const mins=Math.floor(progress.studyMs/60000),studyText=progress.studyMs?`${Math.floor(mins/60)?`${Math.floor(mins/60)}h `:''}${mins%60}m`:'—';
    const studyPct=progress.studyMs?Math.max(8,Math.min(100,Math.round(mins/360*100))):0;
    const streak=currentStreak();
    const now=new Date(),monday=new Date(now);monday.setHours(0,0,0,0);monday.setDate(monday.getDate()-((monday.getDay()+6)%7));
    const activeDays=new Set();for(const items of Object.values(state.attempts||{}))for(const a of items||[])if(a?.at)activeDays.add(dayKey(new Date(a.at)));
    const names=['M','T','W','T','F','S','S'];
    const week=Array.from({length:7},(_,i)=>{const d=new Date(monday);d.setDate(monday.getDate()+i);const done=activeDays.has(dayKey(d)),today=dayKey(d)===dayKey(now),future=d>now;return `<span class="nk-home-week-day ${done?'is-done':''} ${today?'is-today':''} ${future?'is-future':''}"><i></i><b>${names[i]}</b></span>`}).join('');
    const rangeLabels={today:'Today',week:'This Week',month:'This Month',year:'This Year'};
    return shell(`
      <main class="nk-home-approved-v1 nk-home-command-center" aria-label="Home">
        <header class="nk-home-brandbar"><div class="nk-home-brand"><span class="nk-home-brand-icon" aria-hidden="true">${navIcon('book',22)}</span><span><strong>NK QBank</strong><small>Your Personal Study App</small></span></div><button class="nk-home-search" aria-label="Search topics" onclick="window.QB.nav('topics');setTimeout(()=>document.querySelector('input[type=search],.search-input')?.focus(),120)">${navIcon('search',23)}</button></header>
        <section class="nk-home-greeting"><h1>${greetingCopy()} <span aria-hidden="true">☀️</span></h1><p>Small steps every day lead to big results.</p></section>
        <section class="nk-home-streak-card" aria-label="Study streak"><span class="nk-home-streak-flame" aria-hidden="true">🔥</span><div class="nk-home-streak-copy"><strong>${fmtNum(streak)} day streak</strong><small>${streak?'Keep going!':'Start your streak today.'}</small></div><div class="nk-home-week">${week}</div></section>
        <div class="nk-focus-secondary">
          <section class="nk-home-focus-card" aria-label="Today's focus"><div class="nk-home-focus-label">TODAY'S FOCUS</div><h2>${esc(focusTitle)}</h2><p>${esc(focusCopy)}</p><span class="nk-home-focus-heart" aria-hidden="true">♡</span><button class="nk-focus-primary nk-home-focus-action" onclick="window.QB.nkContinueRecentPractice()"><span>Continue Practice</span><span aria-hidden="true">→</span></button></section>
          <section class="nk-home-quick-grid" aria-label="Quick actions"><button onclick="window.QB.nkOpenNewTest('exam')"><span class="nk-home-quick-icon is-violet">${navIcon('clock',22)}</span><strong>Timed Test</strong></button><button onclick="window.QB.nkOpenPracticeSubjects()"><span class="nk-home-quick-icon is-indigo">${navIcon('book',22)}</span><strong>Practice</strong></button><button onclick="window.QB.nkStartTodaysReview()"><span class="nk-home-quick-icon is-purple">${navIcon('refresh',22)}</span><strong>FSRS</strong><small>${due?`${fmtNum(due)} due`:''}</small></button><button onclick="window.QB.nav('bookmarks')"><span class="nk-home-quick-icon is-magenta">${navIcon('bookmark',22)}</span><strong>Bookmarks</strong><small>${bm?`${fmtNum(bm)} saved`:''}</small></button></section>
        </div>
        <section class="nk-home-progress" aria-labelledby="nk-home-progress-title"><div class="nk-home-progress-head"><h2 id="nk-home-progress-title">My Progress</h2><label class="nk-home-range"><span class="sr-only">Progress range</span><select onchange="window.QB.nkSetHomeProgressRange(this.value)">${['today','week','month','year'].map(x=>`<option value="${x}" ${nkHomeProgressRange===x?'selected':''}>${rangeLabels[x]}</option>`).join('')}</select><span aria-hidden="true">⌄</span></label></div><div class="nk-home-progress-card">
          <div class="nk-home-progress-row"><span class="nk-home-progress-icon is-violet">${navIcon('chart',21)}</span><div><div class="nk-home-progress-copy"><strong>Questions Attempted</strong><b>${fmtNum(progress.attempted)} / ${fmtNum(total)}</b></div><span class="nk-home-progress-track"><i style="width:${attemptedPct}%"></i></span></div></div>
          <div class="nk-home-progress-row"><span class="nk-home-progress-icon is-green">${navIcon('check',21)}</span><div><div class="nk-home-progress-copy"><strong>Accuracy</strong><b>${fmtPct(accuracyPct)}</b></div><span class="nk-home-progress-track is-green"><i style="width:${accuracyPct}%"></i></span></div></div>
          <div class="nk-home-progress-row"><span class="nk-home-progress-icon is-blue">${navIcon('clock',21)}</span><div><div class="nk-home-progress-copy"><strong>Study Time</strong><b>${studyText}</b></div><span class="nk-home-progress-track is-blue"><i style="width:${studyPct}%"></i></span></div></div>
        </div></section>
        <section class="nk-home-quote" aria-label="Study motivation"><span aria-hidden="true">“</span><div><strong>Better questions. A brighter you.</strong><small>Keep learning, keep growing.</small></div></section>
      </main>`, 'dashboard');
  }'''

TESTS_PAGE = r'''function testsPage() {
    const mode=nkTestSetup.mode,source=nkTestSetup.source;
    const sourceCards=[['all','book','Full Question Bank','Choose a subject, then a topic'],['custom','grid','Custom Module','Select specific subjects or topics'],['wrong','close','Wrong Questions','Focus on questions you answered incorrectly'],['bookmarks','bookmark','Bookmarked Questions','Practise your saved questions']];
    return shell(`<main class="nk-new-test-v2" aria-label="New Test"><header class="nk-test-page-head"><button aria-label="Back" onclick="window.QB.nav('dashboard')">${navIcon('back',24)}</button><h1>New Test</h1></header><div class="nk-test-mode-tabs" role="tablist"><button class="${mode==='exam'?'active':''}" onclick="window.QB.nkSetTestMode('exam')">Timed Test</button><button class="${mode==='practice'?'active':''}" onclick="window.QB.nkSetTestMode('practice')">Practice</button></div><section class="nk-test-setup-section"><h2>Question Source</h2><p>Choose where to get questions from.</p><div class="nk-test-source-list">${sourceCards.map(([key,icon,title,meta])=>`<button class="nk-test-source-card ${source===key?'active':''}" onclick="${key==='custom'?'window.QB.openStudyModuleBuilder()':`window.QB.nkSetTestSource('${key}')`}"><span class="nk-test-source-icon is-${key}">${navIcon(icon,23)}</span><span><strong>${title}</strong><small>${meta}</small></span>${navIcon('chevron',20)}</button>`).join('')}</div></section><section class="nk-test-setup-section nk-test-timer ${mode==='practice'?'is-disabled':''}"><h2>Timer</h2><p>${mode==='exam'?'One minute per question when enabled.':'Practice sessions use no exam countdown.'}</p><div class="nk-test-toggle-grid"><button ${mode==='practice'?'disabled':''} class="${mode==='exam'&&nkTestSetup.timer?'active':''}" onclick="window.QB.nkSetTestTimer(true)">${navIcon('clock',19)} On</button><button ${mode==='practice'?'disabled':''} class="${mode==='exam'&&!nkTestSetup.timer?'active':''}" onclick="window.QB.nkSetTestTimer(false)">${navIcon('close',19)} Off</button></div></section><section class="nk-test-setup-section"><h2>Number of Questions</h2><p>Choose how many questions to include.</p><div class="nk-test-count-grid">${[10,20,50,100].map(n=>`<button class="${nkTestSetup.count===n?'active':''}" onclick="window.QB.nkSetTestCount(${n})">${n}</button>`).join('')}</div></section><button class="nk-test-start" onclick="window.QB.nkStartConfiguredTest()">${mode==='exam'?'Start Test':'Start Practice'} <span aria-hidden="true">→</span></button>${mode==='exam'&&nkTestSetup.timer?`<p class="nk-test-time-note">${nkTestSetup.count} questions = ${nkTestSetup.count} minutes</p>`:''}</main>`, 'tests');
  }'''

EXAM_PAGE = r'''function examPage() {
    const s=state.activeSession;if(!s || s.mode!=='exam') return dashboard();const q=BY_ID[s.questionIds[s.index]];if(!q)return dashboard();
    const selected=s.answers[q.id]||null,timed=s.timerEnabled!==false;const elapsed=Math.max(0,Date.now()-s.startedAt),totalSec=s.questionIds.length*60,remaining=Math.max(0,totalSec-Math.floor(elapsed/1000));
    const timer=timed?`<div class="nk-exam-strip"><span>Timed CBT · 60 sec / question</span><strong id="exam-timer" class="timer ${remaining<120?'danger':remaining<300?'warn':''}">${formatTimer(remaining)}</strong></div>`:`<div class="nk-exam-strip"><span>Test mode · answers remain changeable</span><strong class="timer">Timer off</strong></div>`;
    return sessionShell(`<div class="nk-v114-session is-exam">${nkSessionHeader(q,s,'exam',timer)}<div class="question-shell"><section class="question-card">${nkQuestionContext(q)}<div class="question-text" data-marrow-question="${q.bank==='Marrow'?esc(String(q.id)):''}">${esc(q.question)}</div><div class="option-list">${nkSessionOptions(q,selected,'exam',false)}</div></section></div></div>`,'tests')+nkSessionActionBar(s,'exam');
  }'''

START_TICKER = r'''function startExamTicker() {
    clearInterval(ticker);const current=state.activeSession;if(!current||current.mode!=='exam'||current.timerEnabled===false)return;
    ticker=setInterval(()=>{const s=state.activeSession;if(!s||s.mode!=='exam'||s.timerEnabled===false){clearInterval(ticker);return;}const remaining=s.questionIds.length*60-Math.floor((Date.now()-s.startedAt)/1000);const el=document.getElementById('exam-timer');if(el){el.textContent=formatTimer(remaining);el.className='timer '+(remaining<120?'danger':remaining<300?'warn':'');}if(remaining<=0){clearInterval(ticker);submitExam(true);}},250);
  }'''

SUBMIT_EXAM = r'''function submitExam(auto=false){closeQuestionNavigator();const s=state.activeSession;if(!s||s.mode!=='exam')return;saveExamElapsed();const rawElapsed=Date.now()-s.startedAt;const elapsed=s.timerEnabled===false?rawElapsed:Math.min(rawElapsed,s.questionIds.length*60000);let correct=0,incorrect=0,unattempted=0,attempted=0;const qt=s.questionTimes||{};Object.entries(s.answers).forEach(([id,sel])=>{if(sel){attempted++;const q=BY_ID[id];const isCorrect=Number(q.correctOption)===Number(sel);if(isCorrect)correct++;else incorrect++;recordAttempt(id,sel,qt[id]||0,'exam');}});unattempted=s.questionIds.length-attempted;const test={id:`t_${Date.now()}_${Math.random().toString(16).slice(2)}`,title:s.title,questionIds:[...s.questionIds],answers:{...s.answers},questionTimes:{...qt},correct,incorrect,unattempted,total:s.questionIds.length,attempted,totalTimeMs:elapsed,createdAt:Date.now(),autoSubmitted:auto,timerEnabled:s.timerEnabled!==false};test.originRoute=s.originRoute;state.tests.push(test);state.tests=state.tests.slice(-100);state.activeSession=null;saveState();document.querySelectorAll('#toast-root .toast').forEach(e=>e.remove());navigate('result',test.id);
  }'''

CSS = r'''<style id="nk-home-command-center-v1">
body:has(.nk-home-approved-v1){background:#f6f7fb}.nk-home-approved-v1{max-width:760px;margin:0 auto;padding:8px 0 28px;color:#151852}.nk-home-brandbar{display:flex;align-items:center;justify-content:space-between;padding:4px 1px 12px}.nk-home-brand{display:flex;align-items:center;gap:10px}.nk-home-brand-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;color:#fff;background:linear-gradient(135deg,#7561ff,#5848e9)}.nk-home-brand span:last-child{display:grid}.nk-home-brand strong{font-size:17px}.nk-home-brand small{font-size:10px;color:#7c80a4}.nk-home-search{border:0;background:transparent;color:#151852;width:44px}.nk-home-greeting{padding:11px 2px 17px}.nk-home-greeting h1{margin:0;font-size:32px;line-height:1.08;font-weight:900;letter-spacing:-1px}.nk-home-greeting p{margin:5px 0 0;color:#7d81a7;font-size:12px}.nk-home-streak-card{display:grid;grid-template-columns:44px minmax(92px,1fr) auto;align-items:center;gap:10px;padding:12px 14px;border:1px solid #ebeaf5;border-radius:17px;background:#fff;box-shadow:0 5px 20px rgba(39,42,101,.045)}.nk-home-streak-flame{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:#ff8c32;font-size:22px}.nk-home-streak-copy{display:grid}.nk-home-streak-copy strong{font-size:13px}.nk-home-streak-copy small{font-size:9px;color:#8a8eaa}.nk-home-week{display:flex;gap:8px}.nk-home-week-day{display:grid;gap:5px;place-items:center}.nk-home-week-day i{width:13px;height:13px;border-radius:50%;background:#e3e5f1}.nk-home-week-day.is-done i{background:#7459ef}.nk-home-week-day.is-today i{box-shadow:0 0 0 3px #eeeaff}.nk-home-week-day b{font-size:8px;color:#777b9f}.nk-focus-secondary{margin-top:14px}.nk-home-focus-card{position:relative;overflow:hidden;padding:20px 20px 18px;border-radius:20px;background:linear-gradient(135deg,#3f3799,#302b78);color:#fff;box-shadow:0 14px 30px rgba(52,46,130,.22)}.nk-home-focus-label{font-size:9px;letter-spacing:.18em;font-weight:800;opacity:.76}.nk-home-focus-card h2{max-width:80%;margin:8px 0 4px;font-size:22px;line-height:1.16}.nk-home-focus-card p{max-width:82%;margin:0 0 15px;font-size:11px;line-height:1.45;color:#d8d7ef}.nk-home-focus-heart{position:absolute;right:24px;top:34px;font-size:54px;opacity:.16}.nk-home-focus-action{width:100%;min-height:46px;border:0;border-radius:12px;background:#fff;color:#5d36ed;font-weight:850;display:flex;align-items:center;justify-content:center;gap:10px}.nk-home-quick-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:10px;padding:10px 4px;border:1px solid #ebeaf3;border-radius:16px;background:#fff}.nk-home-quick-grid button{border:0;border-right:1px solid #ececf4;background:transparent;display:grid;place-items:center;gap:4px;color:#1a1d5f;min-width:0}.nk-home-quick-grid button:last-child{border-right:0}.nk-home-quick-icon{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:#f0edff;color:#6d52f3}.nk-home-quick-grid strong{font-size:9px;white-space:nowrap}.nk-home-quick-grid small{font-size:7px;color:#8b8fa9}.nk-home-progress{margin-top:20px}.nk-home-progress-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}.nk-home-progress-head h2{margin:0;font-size:17px}.nk-home-range{position:relative;display:flex;align-items:center;gap:4px;color:#676b96;font-size:10px}.nk-home-range select{appearance:none;border:0;background:transparent;padding:8px 16px 8px 8px;color:#676b96;font:inherit;font-weight:750}.nk-home-range>span:last-child{pointer-events:none;margin-left:-15px}.nk-home-progress-card{padding:4px 14px;border:1px solid #e9eaf2;border-radius:18px;background:#fff}.nk-home-progress-row{display:grid;grid-template-columns:40px 1fr;gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid #f0f1f5}.nk-home-progress-row:last-child{border-bottom:0}.nk-home-progress-icon{width:35px;height:35px;border-radius:11px;display:grid;place-items:center;background:#efedff;color:#6d52f3}.nk-home-progress-icon.is-green{background:#e6f9ef;color:#20ad70}.nk-home-progress-icon.is-blue{background:#e9f3ff;color:#3295ed}.nk-home-progress-copy{display:flex;justify-content:space-between;gap:10px;font-size:10px}.nk-home-progress-copy b{font-size:10px}.nk-home-progress-track{display:block;height:6px;margin-top:7px;border-radius:999px;background:#ececf5;overflow:hidden}.nk-home-progress-track i{display:block;height:100%;background:#7357ef;border-radius:inherit}.nk-home-progress-track.is-green i{background:#24c879}.nk-home-progress-track.is-blue i{background:#319cf4;border-radius:inherit}.nk-home-quote{display:flex;align-items:center;gap:12px;margin-top:16px;padding:13px 16px;border-radius:16px;background:linear-gradient(100deg,#f4efff,#f7f2ff)}.nk-home-quote>span{font-size:26px;color:#6b45ef}.nk-home-quote div{display:grid}.nk-home-quote strong{font-size:11px}.nk-home-quote small{font-size:9px;color:#8689a8}
.nk-flow-backdrop{z-index:140}.nk-flow-modal{width:min(620px,100%);max-height:min(84vh,760px);overflow:auto;border-radius:24px;padding:20px}.nk-flow-modal-head{display:flex;align-items:flex-start;gap:12px;padding-right:34px;margin-bottom:14px}.nk-flow-modal-head>span{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:#f0edff;color:#6750e8}.nk-flow-modal-head small{font-size:8px;font-weight:850;letter-spacing:.12em;color:#7460db}.nk-flow-modal-head h3{margin:2px 0 3px;font-size:21px}.nk-flow-modal-head p{margin:0;color:#7f839e;font-size:10px}.nk-flow-choice-list{display:grid;gap:8px}.nk-flow-choice{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:12px;width:100%;padding:13px;border:1px solid #e8e8f2;border-radius:15px;background:#fff;text-align:left;color:#181b58}.nk-flow-choice>span:nth-last-child(2){display:grid}.nk-flow-choice strong{font-size:12px}.nk-flow-choice small{margin-top:2px;font-size:9px;color:#8b8fa6}.nk-flow-choice-icon{width:36px;height:36px;border-radius:10px;display:grid!important;place-items:center;background:#f0edff;color:#6350e5}.nk-flow-back{border:0;background:transparent;color:#6557d4;font-size:10px;font-weight:800;margin:0 0 12px -5px}.nk-flow-empty{padding:20px;text-align:center;color:#8b8fa6}
body:has(.nk-new-test-v2){background:#f7f8fc}.nk-new-test-v2{max-width:760px;margin:0 auto;padding:8px 0 34px;color:#151852}.nk-test-page-head{display:flex;align-items:center;gap:10px;padding:4px 0 14px}.nk-test-page-head button{border:0;background:transparent;color:#151852}.nk-test-page-head h1{margin:0;font-size:26px;letter-spacing:-.6px}.nk-test-mode-tabs{display:grid;grid-template-columns:1fr 1fr;padding:2px;border:1px solid #dedff0;border-radius:16px;background:#f8f8fd}.nk-test-mode-tabs button{border:0;border-radius:14px;background:transparent;color:#565a8c;min-height:50px;font-weight:850}.nk-test-mode-tabs button.active{background:linear-gradient(135deg,#8a73ff,#674ce9);color:#fff;box-shadow:0 7px 18px rgba(104,76,233,.2)}.nk-test-setup-section{margin-top:24px}.nk-test-setup-section h2{margin:0;font-size:18px}.nk-test-setup-section>p{margin:4px 0 12px;font-size:11px;color:#8185a5}.nk-test-source-list{display:grid;gap:8px}.nk-test-source-card{display:grid;grid-template-columns:46px 1fr 22px;gap:12px;align-items:center;padding:12px 13px;border:1px solid #e6e7ef;border-radius:17px;background:#fff;text-align:left;color:#171a58;box-shadow:0 3px 10px rgba(40,45,90,.025)}.nk-test-source-card.active{border-color:#aaa0f5;box-shadow:0 0 0 2px #f1efff}.nk-test-source-card>span:nth-child(2){display:grid}.nk-test-source-card strong{font-size:13px}.nk-test-source-card small{margin-top:3px;font-size:10px;color:#8589a7}.nk-test-source-icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;background:#efedff;color:#6951e6}.nk-test-source-icon.is-wrong{background:#ffecef;color:#e94d65}.nk-test-source-icon.is-bookmarks{background:#fff2e6;color:#f38a29}.nk-test-source-icon.is-custom{background:#eaf3ff;color:#378ff0}.nk-test-toggle-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.nk-test-toggle-grid button,.nk-test-count-grid button{min-height:54px;border:1px solid #e0e1ed;border-radius:15px;background:#fff;color:#1d205f;font-weight:850}.nk-test-toggle-grid button.active,.nk-test-count-grid button.active{border-color:#a99bf4;background:#f0edff;color:#4d30d5}.nk-test-toggle-grid button{display:flex;align-items:center;justify-content:center;gap:8px}.nk-test-timer.is-disabled{opacity:.58}.nk-test-count-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.nk-test-start{width:100%;min-height:58px;margin-top:26px;border:0;border-radius:18px;background:linear-gradient(135deg,#413993,#302b78);color:#fff;font-size:17px;font-weight:900;box-shadow:0 12px 26px rgba(48,43,120,.2)}.nk-test-time-note{text-align:center;color:#8185a5;font-size:10px;margin:8px 0 0}
@media(max-width:560px){.nk-home-approved-v1,.nk-new-test-v2{padding-left:4px;padding-right:4px}.nk-home-greeting h1{font-size:29px}.nk-home-week{gap:6px}.nk-home-streak-card{grid-template-columns:42px minmax(80px,1fr) auto}.nk-home-quick-grid strong{font-size:8.3px}.nk-test-count-grid{gap:7px}.nk-test-source-card{grid-template-columns:42px 1fr 20px}}@media(max-width:380px){.nk-home-week{gap:4px}.nk-home-week-day i{width:11px;height:11px}.nk-home-streak-copy strong{font-size:11px}.nk-home-quick-grid{grid-template-columns:repeat(2,1fr);gap:8px}.nk-home-quick-grid button{border-right:0;border-bottom:1px solid #ececf4;padding:8px}.nk-test-count-grid{grid-template-columns:repeat(2,1fr)}}@media(prefers-reduced-motion:reduce){.nk-home-approved-v1 *,.nk-new-test-v2 *{transition:none!important;animation:none!important}}
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
            if c=='\n': line_comment=False
            i+=1;continue
        if block_comment:
            if c=='*' and n=='/': block_comment=False;i+=2
            else:i+=1
            continue
        if quote:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c==quote: quote=None
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
    if 'NK_CUSTOM_STUDY_MODULES_V1' not in source and 'openStudyModuleBuilder' not in source:raise SystemExit('Home flow must run after Custom Study Modules')
    source=replace_function(source,'dashboard',HOME_HELPERS+'\n'+DASHBOARD)
    source=replace_function(source,'testsPage',TESTS_PAGE)
    source=replace_function(source,'examPage',EXAM_PAGE)
    source=replace_function(source,'startExamTicker',START_TICKER)
    source=replace_function(source,'submitExam',SUBMIT_EXAM)
    bridge='window.QB={'
    if bridge not in source:raise SystemExit('window.QB bridge not found')
    exports="nkContinueRecentPractice,nkOpenPracticeSubjects,nkOpenPracticeTopics,nkStartTopicPractice,nkSetHomeProgressRange,nkOpenNewTest,nkSetTestMode,nkSetTestSource,nkSetTestTimer,nkSetTestCount,nkStartConfiguredTest,nkOpenTestSubjects,nkOpenTestTopics,nkStartConfiguredTopic,"
    source=source.replace(bridge,bridge+exports,1)
    source=re.sub(r'<style id="nk-home-command-center-v1">[\s\S]*?</style>','',source,count=1)
    if '</head>' not in source:raise SystemExit('closing head not found')
    source=source.replace('</head>',CSS+'\n</head>',1)
    required=[FLOW_MARKER,'Continue Practice','nkOpenPracticeSubjects','nkOpenPracticeTopics','This Week','This Month','This Year','Full Question Bank','Custom Module','Wrong Questions','Bookmarked Questions','60 sec / question','timerEnabled===false','nkStartConfiguredTopic']
    missing=[x for x in required if x not in source]
    if missing:raise SystemExit(f'Home flow marker missing after transform: {missing}')
    return source


def main() -> None:
    source=HTML.read_text(encoding='utf-8')
    updated=transform(source)
    HTML.write_text(updated,encoding='utf-8')
    print('HOME_FLOW_V2_OK: resume focus, subject-topic Practice, progress ranges, New Test setup, custom modules, optional 60s/question timer')

if __name__=='__main__':main()
