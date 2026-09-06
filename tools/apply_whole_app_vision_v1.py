#!/usr/bin/env python3
"""Apply the V11.4 whole-app visual system after the protected session UI."""

from pathlib import Path
import re


HTML = Path("app/src/main/assets/index.html")
STYLE_ID = "nk-whole-app-vision-v114"


FOUNDATION_AND_DASHBOARD = r'''function nkAppSubjectMeta(name=activeSubject) {
    const key=String(name||'').toLowerCase();
    if(key.includes('physiology')) return {key:'physiology',icon:'heart',tone:'red'};
    if(key.includes('anatomy')) return {key:'anatomy',icon:'body',tone:'blue'};
    return {key:'biochemistry',icon:'dna',tone:'magenta'};
  }

  function nkAppSubjectIcon(name,size=20) {
    return nkSubjectGraphic(name,size);
  }

  // Subject identity uses the open-source Tabler outline icon set (MIT):
  // dna-2, heartbeat, bone, and flame. Keeping the paths inline makes the
  // offline APK independent of a network connection or icon font.
  function nkSubjectGraphic(name,size=20) {
    const key=nkAppSubjectMeta(name).key;
    const paths={
      biochemistry:'<path d="M17 3v1c-.01 3.352 -1.68 6.023 -5.008 8.014c-3.328 1.99 3.336 -2 .008 -.014c-3.328 1.99 -5 4.662 -5.008 8.014v1"/><path d="M17 21.014v-1c-.01 -3.352 -1.68 -6.023 -5.008 -8.014c-3.328 -1.99 3.336 2 .008 .014c-3.328 -1.991 -5 -4.662 -5.008 -8.014v-1"/><path d="M7 4h10M7 20h10M8 8h8M8 16h8"/>',
      physiology:'<path d="M19.5 13.572l-7.5 7.428l-2.896 -2.868m-6.117 -8.104a5 5 0 0 1 9.013 -3.022a5 5 0 1 1 7.5 6.572"/><path d="M3 13h2l2 3l2 -6l1 3h3"/>',
      anatomy:'<path d="M15 3a3 3 0 0 1 3 3a3 3 0 1 1 -2.12 5.122l-4.758 4.758a3 3 0 1 1 -5.117 2.297v-.177h-.176a3 3 0 1 1 2.298 -5.115l4.758 -4.758a3 3 0 0 1 2.12 -5.122z"/>'
    };
    return `<svg class="nk-subject-svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[key]}</svg>`;
  }

  function nkFlameGraphic(size=24) {
    return `<svg class="nk-flame-svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 10.941c2.333 -3.308 .167 -7.823 -1 -8.941c0 3.395 -2.235 5.299 -3.667 6.706c-1.43 1.408 -2.333 3.294 -2.333 5.588c0 3.704 3.134 6.706 7 6.706c3.866 0 7 -3.002 7 -6.706c0 -1.712 -1.232 -4.403 -2.333 -5.588c-2.084 3.353 -3.257 3.353 -4.667 2.235"/></svg>`;
  }

  function nkStreakMilestoneCopy() {
    const streak=currentStreak();
    if(!streak) return 'Answer one question today to light the flame.';
    const next=Math.max(7,Math.ceil((streak+1)/7)*7),remaining=next-streak;
    return `${remaining} more day${remaining===1?'':'s'} to reach ${next} days`;
  }

  function nkAppSubjectStats(name) {
    const record=SUBJECT_BY_NAME[name]||SUBJECTS.find(x=>x.subject===name)||{};
    const questions=Array.isArray(record.questions)?record.questions:[];
    const topics=Array.isArray(record.topics)?record.topics:(Array.isArray(record.chapters)?record.chapters:[]);
    const attempted=questions.filter(q=>qAttempts(q.id).length>0).length;
    const pct=questions.length?Math.round(attempted/questions.length*100):0;
    return {questions:questions.length,topics:topics.length,attempted,pct};
  }

  function nkAppPageHead(kicker,title,copy,action='') {
    return `<header class="nk-page-head"><div><div class="nk-kicker">${esc(kicker)}</div><h1>${esc(title)}</h1>${copy?`<p>${esc(copy)}</p>`:''}</div>${action}</header>`;
  }

  function nkAppEmpty(icon,title,copy,action='') {
    return `<div class="nk-empty"><span class="nk-empty-icon">${navIcon(icon,24)}</span><strong>${esc(title)}</strong><p>${esc(copy)}</p>${action}</div>`;
  }

  function nkWeekStrip() {
    const days=studyDayKeys(),today=dayStart(),names=['S','M','T','W','T','F','S'];
    const items=[];
    for(let i=6;i>=0;i--){
      const d=new Date(today);d.setDate(d.getDate()-i);
      const active=days.has(dayKey(d)),isToday=i===0;
      items.push(`<span class="nk-week-day ${active?'is-done':''} ${isToday?'is-today':''}" title="${isToday?'Today':d.toLocaleDateString()}"><i>${active?nkFlameGraphic(12):''}</i><b>${names[d.getDay()]}</b></span>`);
    }
    return items.join('');
  }

  function dashboard() {
    const attempted=totalAttempted(),total=QUESTIONS.length,acc=overallAccuracy();
    const tests=state.tests.length,due=pendingReviewCount(),wrong=wrongQuestions().length,bm=bookmarkedQuestions().length;
    const recent=state.tests.slice().sort((a,b)=>b.createdAt-a.createdAt).slice(0,3);
    const perf=chapterPerformanceRows().filter(x=>x.s.attempted>0).slice(0,4);
    const focus=due?`Review ${due} due question${due===1?'':'s'}`:wrong?`Revisit ${wrong} missed question${wrong===1?'':'s'}`:'Build recall with 20 focused questions';
    return shell(`<div class="nk-app-v114 nk-home-v114">
      ${nkAppPageHead(`${activeSubject} · Personal QBank`,greetingCopy(),'Choose one useful study action and keep moving.')}
      <section class="nk-streak-strip ${currentStreak()?'is-burning':''}"><div class="nk-streak-copy"><span class="nk-streak-flame">${nkFlameGraphic(28)}</span><div><strong>${currentStreak()} day streak</strong><small>${nkStreakMilestoneCopy()}</small></div></div><div class="nk-week-strip">${nkWeekStrip()}</div></section>
      <section class="nk-focus-panel"><div class="nk-kicker">TODAY'S FOCUS</div><h2>${esc(focus)}</h2><p>${due?'Strengthen scheduled recall before adding new material.':wrong?'A second retrieval pass turns mistakes into memory.':'A compact mixed set is enough to build momentum.'}</p><div class="nk-focus-actions"><button class="nk-focus-primary" onclick="window.QB.continuePractice()">${navIcon('book',18)}<span>Continue Practice</span>${navIcon('chevron',17)}</button>${due?`<button onclick="window.QB.startLibrary('review')">Review ${fmtNum(due)} Due</button>`:``}<button onclick="window.QB.startAllSubjectPractice()">Practice 20 Random Questions</button><button onclick="window.QB.openTestBuilder()">Timed CBT</button></div></section>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">STUDY LIBRARY</div><h2>Subjects</h2></div><span>${fmtNum(SUBJECTS.length)} available</span></div><div class="nk-subject-list">${SUBJECTS.map(x=>{const m=nkAppSubjectMeta(x.subject),s=nkAppSubjectStats(x.subject);return `<button class="nk-subject-row is-${m.key} ${x.subject===activeSubject?'is-active':''}" onclick="window.QB.openSubjectTopics('${esc(x.subject)}')"><span class="nk-subject-mark">${nkAppSubjectIcon(x.subject,22)}</span><span class="nk-subject-copy"><strong>${esc(x.subject)}</strong><small>${fmtNum(s.questions)} questions · ${fmtNum(s.topics)} topics</small><span class="nk-line-progress"><i style="width:${s.pct}%"></i></span></span><span class="nk-subject-percent">${s.pct}%</span>${navIcon('chevron',18)}</button>`}).join('')}</div></section>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">YOUR PROGRESS</div><h2>At a glance</h2></div><button class="nk-text-link" onclick="window.QB.nav('analytics')">Insights ${navIcon('chevron',15)}</button></div><div class="nk-metric-grid"><div><b>${fmtNum(attempted)}</b><strong>Questions</strong><small>of ${fmtNum(total)}</small></div><div><b>${fmtPct(acc)}</b><strong>Accuracy</strong><small>all attempts</small></div><div><b>${fmtNum(due)}</b><strong>Due</strong><small>review now</small></div><div><b>${fmtNum(tests)}</b><strong>Sessions</strong><small>completed</small></div></div></section>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">QUICK ACCESS</div><h2>Keep going</h2></div></div><div class="nk-quick-grid"><button onclick="window.QB.nav('wrong')"><span class="nk-quick-icon is-red">${navIcon('refresh',19)}</span><span><strong>Wrong questions</strong><small>${fmtNum(wrong)} to revisit</small></span>${navIcon('chevron',16)}</button><button onclick="window.QB.nav('review')"><span class="nk-quick-icon is-blue">${navIcon('clock',19)}</span><span><strong>Spaced review</strong><small>${fmtNum(due)} due today</small></span>${navIcon('chevron',16)}</button><button onclick="window.QB.nav('bookmarks')"><span class="nk-quick-icon is-violet">${navIcon('bookmark',19)}</span><span><strong>Bookmarks</strong><small>${fmtNum(bm)} saved</small></span>${navIcon('chevron',16)}</button><button onclick="window.QB.nav('topics')"><span class="nk-quick-icon is-green">${navIcon('book',19)}</span><span><strong>Browse topics</strong><small>Find your next chapter</small></span>${navIcon('chevron',16)}</button></div></section>
      <section class="nk-section nk-home-lower"><div><div class="nk-section-head"><div><div class="nk-kicker">PERFORMANCE</div><h2>Strongest chapters</h2></div><button class="nk-text-link" onclick="window.QB.nav('analytics')">All ${navIcon('chevron',15)}</button></div>${perf.length?`<div class="nk-compact-list">${perf.map(({c,s},i)=>`<div class="nk-compact-row"><span class="nk-rank">${i+1}</span><span><strong>${esc(c.title)}</strong><small>${s.attempted}/${s.total} attempted</small></span><b>${fmtPct(s.accuracy)}</b></div>`).join('')}</div>`:nkAppEmpty('chart','Your chapter picture will appear here','Complete a few questions to build meaningful performance data.')}</div><div><div class="nk-section-head"><div><div class="nk-kicker">RECENT</div><h2>Study sessions</h2></div><button class="nk-text-link" onclick="window.QB.nav('tests')">All ${navIcon('chevron',15)}</button></div>${recent.length?`<div class="nk-session-list">${recent.map(testRow).join('')}</div>`:nkAppEmpty('test','No sessions yet','Your completed Practice and CBT sessions will appear here.')}</div></section>
    </div>`,'dashboard');
  }

  '''


HEADER = r'''function header(title = 'NK QBank'){
    return `<header class="nk-global-header-v114"><div class="nk-global-inner"><div class="nk-global-brand" aria-label="NK QBank"><strong>NK</strong><span>QBank</span></div><div class="nk-global-subject is-${nkAppSubjectMeta().key}">${nkAppSubjectIcon(activeSubject,18)}<span>${esc(activeSubject)}</span></div></div></header>`;
  }

  '''


BOTTOM_NAV = r'''function bottomNav(active) {
    const items=[['dashboard','Home','home'],['topics','Topics','book'],['tests','Tests','test'],['analytics','Insights','chart'],['more','More','more']];
    return `<nav class="bottom-nav nk-bottom-nav-v114" aria-label="Primary navigation">${items.map(([id,label,icon])=>`<button class="nav-item ${active===id?'active':''}" onclick="window.QB.nav('${id}')" aria-current="${active===id?'page':'false'}"><span class="nav-icon-wrap">${navIcon(icon,21)}</span><span class="nav-label">${label}</span></button>`).join('')}</nav>`;
  }

  '''


TEST_ROW = r'''function testRow(t) {
    const score=t.total?t.correct/t.total*100:0,isPractice=t.kind==='practice';
    return `<button class="nk-test-row" onclick="window.QB.openTest('${esc(t.id)}')"><span class="nk-test-icon ${isPractice?'is-practice':'is-cbt'}">${navIcon(isPractice?'book':'test',18)}</span><span class="nk-test-main"><strong>${esc(t.title||(isPractice?'Practice Session':'Timed CBT'))}</strong><small>${t.correct}/${t.total} correct · ${fmtDate(t.createdAt,false)}</small></span><span class="nk-test-score ${score>=75?'success':score>=50?'warning':'danger'}">${fmtPct(score)}</span>${navIcon('chevron',17)}</button>`;
  }

  '''


TOPICS = r'''function topics() {
    const qTerm=searchTerm.trim().toLowerCase();
    const allChapters=CHAPTERS.filter(c=>!qTerm||c.title.toLowerCase().includes(qTerm)||chapterQuestions(c.id).some(q=>q.question.toLowerCase().includes(qTerm)));
    const chapters=allChapters.filter(c=>{const s=chapterStats(c.id);if(topicFilter==='completed')return s.total>0&&s.attempted===s.total;if(topicFilter==='unattempted')return s.attempted===0;if(topicFilter==='inprogress')return s.attempted>0&&s.attempted<s.total;return true;});
    const completed=CHAPTERS.filter(c=>{const s=chapterStats(c.id);return s.total>0&&s.attempted===s.total}).length;
    return shell(`<div class="nk-app-v114 nk-topics-v114">${nkAppPageHead(`${activeSubject} · Study map`,'Topics','Choose a chapter and move directly into focused recall.',`<button class="nk-head-action" onclick="window.QB.startAllPractice()">Mixed Practice ${navIcon('chevron',16)}</button>`)}
      <div class="nk-subject-switch" aria-label="Choose subject">${SUBJECTS.map(x=>`<button class="${x.subject===activeSubject?'is-active':''}" onclick="window.QB.openSubjectTopics('${esc(x.subject)}')">${nkAppSubjectIcon(x.subject,17)}<span>${esc(x.subject)}</span></button>`).join('')}</div>
      <div class="nk-topic-tools"><label class="nk-search">${navIcon('search',18)}<input aria-label="Search chapters or questions" placeholder="Search chapters or questions" value="${esc(searchTerm)}" oninput="window.QB.setSearch(this.value)"></label><div class="nk-filter-tabs">${[['all','All'],['completed','Completed'],['unattempted','Unattempted'],['inprogress','In progress']].map(([v,l])=>`<button class="${topicFilter===v?'is-active':''}" onclick="window.QB.setTopicFilter('${v}')">${l}</button>`).join('')}</div></div>
      <div class="nk-topic-summary"><span><b>${CHAPTERS.length}</b> topics</span><span><b>${completed}</b> completed</span><span><b>${CHAPTERS.filter(c=>chapterStats(c.id).attempted>0).length}</b> started</span></div>
      <div class="nk-topic-list">${chapters.length?chapters.map((c,i)=>{const s=chapterStats(c.id),pct=s.total?Math.round(s.attempted/s.total*100):0;return `<button class="nk-topic-row" onclick="window.QB.openChapter('${c.id}')"><span class="nk-topic-index">${String(i+1).padStart(2,'0')}</span><span class="nk-topic-copy"><strong>${esc(c.title)}</strong><small>${fmtNum(s.total)} MCQs · ${fmtNum(s.attempted)} completed${s.attempted?` · ${fmtPct(s.accuracy)} accuracy`:''}</small><span class="nk-line-progress"><i style="width:${pct}%"></i></span></span><span class="nk-topic-side"><b>${pct}%</b>${navIcon('chevron',17)}</span></button>`}).join(''):nkAppEmpty('search','No matching topics','Try a broader search or a different progress filter.')}</div>
      ${qTerm?`<section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">SEARCH RESULTS</div><h2>Matching questions</h2></div></div><div class="nk-library-list">${QUESTIONS.filter(q=>q.question.toLowerCase().includes(qTerm)).slice(0,40).map(q=>libraryRow(q,'search')).join('')}</div></section>`:''}
    </div>`,'topics');
  }

  '''


CHAPTER = r'''function chapterPage(cid) {
    const c=CHAPTER_BY_ID[String(cid)];if(!c)return topics();
    const qs=chapterQuestions(c.id),s=chapterStats(c.id),unattempted=Math.max(0,s.total-s.attempted),wrong=qs.filter(q=>qAttempts(q.id).some(a=>!a.correct)).length,pct=s.total?Math.round(s.attempted/s.total*100):0;
    return shell(`<div class="nk-app-v114 nk-chapter-v114"><button class="nk-back-link" onclick="window.QB.nav('topics')">${navIcon('back',18)} Topics</button><section class="nk-chapter-hero"><div class="nk-chapter-title"><div class="nk-kicker">${esc(activeSubject)} · CHAPTER ${String(c.id).padStart(2,'0')}</div><h1>${esc(c.title)}</h1><p>${fmtNum(s.total)} questions · ${fmtNum(s.attempted)} completed · ${fmtPct(s.accuracy)} accuracy</p><span class="nk-line-progress"><i style="width:${pct}%"></i></span></div><div class="nk-chapter-actions"><button class="is-primary" onclick="window.QB.openSessionBuilder('${c.id}','practice')">${navIcon('book',19)}<span><strong>Practice</strong><small>Immediate feedback</small></span>${navIcon('chevron',17)}</button><button onclick="window.QB.openSessionBuilder('${c.id}','exam')">${navIcon('clock',19)}<span><strong>Timed test</strong><small>60 sec / question</small></span>${navIcon('chevron',17)}</button></div></section>
      <div class="nk-metric-grid nk-chapter-metrics"><div><b>${fmtPct(s.accuracy)}</b><strong>Accuracy</strong><small>all attempts</small></div><div><b>${fmtNum(s.attempted)}</b><strong>Completed</strong><small>of ${fmtNum(s.total)}</small></div><div><b>${fmtNum(unattempted)}</b><strong>Unattempted</strong><small>remaining</small></div><div><b class="danger">${fmtNum(wrong)}</b><strong>Wrong</strong><small>to revisit</small></div></div>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">SOURCE ORDER</div><h2>Question library</h2></div><span>${fmtNum(qs.length)} questions</span></div><div class="nk-library-list">${qs.map(q=>{const a=latestAttempt(q.id);return `<button class="nk-library-row" onclick="window.QB.practiceOne('${q.id}')"><span class="nk-question-index">${q.questionNumber}</span><span><strong>${esc(q.question.slice(0,150))}${q.question.length>150?'…':''}</strong><small><i class="nk-status ${a?(a.correct?'is-correct':'is-wrong'):'is-unattempted'}">${a?(a.correct?'Correct':'Incorrect'):'Unattempted'}</i>${q.sourcePage?`PDF p.${q.sourcePage}`:''}</small></span>${navIcon('chevron',17)}</button>`}).join('')}</div></section>
    </div>`,'topics');
  }

  '''


TESTS = r'''function testsPage() {
    const tests=state.tests.filter(t=>t.kind!=='practice').slice().sort((a,b)=>b.createdAt-a.createdAt);
    return shell(`<div class="nk-app-v114 nk-tests-v114">${nkAppPageHead(`${activeSubject} · Exam mode`,'Timed CBT','Build a focused test with real exam behavior.',`<button class="nk-head-action" onclick="window.QB.openTestBuilder()">New Test ${navIcon('chevron',16)}</button>`)}
      <section class="nk-test-hero"><span class="nk-test-hero-icon">${navIcon('test',26)}</span><div><div class="nk-kicker">EXAM MODE</div><h2>Test what you can retrieve under time.</h2><p>Answers stay changeable. Correctness and explanations appear only after submission.</p><div class="nk-exam-principles"><span>${navIcon('clock',15)} 60 sec / question</span><span>${navIcon('grid',15)} Free navigation</span><span>${navIcon('check',15)} Final score only</span></div></div><button onclick="window.QB.openTestBuilder()">Start timed CBT ${navIcon('chevron',17)}</button></section>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">HISTORY</div><h2>Completed tests</h2></div><span>${fmtNum(tests.length)} completed</span></div>${tests.length?`<div class="nk-session-list">${tests.map(testRow).join('')}</div>`:nkAppEmpty('test','No test history yet','Your completed timed CBTs will stay here.',`<button class="nk-inline-action" onclick="window.QB.openTestBuilder()">Create first test</button>`)}</section>
    </div>`,'tests');
  }

  '''


ANALYTICS = r'''function analytics() {
    const attempts=Object.values(state.attempts).flat(),avgTime=avg(attempts.map(a=>a.timeSpent||0)),attempted=totalAttempted(),completion=QUESTIONS.length?attempted/QUESTIONS.length*100:0;
    const chapterRows=CHAPTERS.map(c=>({c,s:chapterStats(c.id)})).sort((a,b)=>(b.s.attempted?b.s.accuracy:-1)-(a.s.attempted?a.s.accuracy:-1));
    const recent=state.tests.slice().sort((a,b)=>b.createdAt-a.createdAt).slice(0,5);
    return shell(`<div class="nk-app-v114 nk-analytics-v114">${nkAppPageHead(`${activeSubject} · Local history`,'Insights','Performance calculated from your stored attempts and completed sessions.')}
      <div class="nk-insight-grid"><article class="is-green"><span>${navIcon('check',18)}</span><small>Accuracy</small><b>${fmtPct(overallAccuracy())}</b><p>${fmtNum(totalAttempts())} attempts</p></article><article class="is-blue"><span>${navIcon('clock',18)}</span><small>Avg. time / question</small><b>${formatDuration(avgTime)}</b><p>practice attempts</p></article><article class="is-amber"><span>${navIcon('refresh',18)}</span><small>Questions due</small><b>${fmtNum(pendingReviewCount())}</b><p>spaced review</p></article><article class="is-violet"><span>${navIcon('chart',18)}</span><small>Completion</small><b>${fmtPct(completion)}</b><p>${fmtNum(attempted)} of ${fmtNum(QUESTIONS.length)}</p></article></div>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">CHAPTER PERFORMANCE</div><h2>Accuracy and coverage</h2></div><span>${CHAPTERS.length} chapters</span></div><div class="nk-performance-list">${chapterRows.map(({c,s})=>{const coverage=s.total?s.attempted/s.total*100:0;return `<button onclick="window.QB.openChapter('${c.id}')"><span><strong>${esc(c.title)}</strong><small>${s.attempted}/${s.total} completed · ${s.correct} correct · ${s.incorrect} incorrect</small><i class="nk-line-progress"><i style="width:${coverage}%"></i></i></span><b class="${s.accuracy>=75?'success':s.accuracy>=50?'warning':s.attempted?'danger':''}">${s.attempted?fmtPct(s.accuracy):'—'}</b>${navIcon('chevron',16)}</button>`}).join('')}</div></section>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">RECENT</div><h2>Study sessions</h2></div><button class="nk-text-link" onclick="window.QB.nav('tests')">Tests ${navIcon('chevron',15)}</button></div>${recent.length?`<div class="nk-session-list">${recent.map(testRow).join('')}</div>`:nkAppEmpty('chart','No performance history yet','Complete Practice or CBT questions to build your insights.')}</section>
    </div>`,'analytics');
  }

  '''


MORE = r'''function morePage() {
    const bm=bookmarkedQuestions().length,wrong=wrongQuestions().length,due=pendingReviewCount();
    const row=(icon,title,meta,action,tone='')=>`<button class="nk-settings-row ${tone}" onclick="${action}"><span class="nk-settings-icon">${navIcon(icon,19)}</span><span><strong>${esc(title)}</strong><small>${esc(meta)}</small></span>${navIcon('chevron',17)}</button>`;
    return shell(`<div class="nk-app-v114 nk-more-v114">${nkAppPageHead(`${activeSubject} · Personal QBank`,'More','Revision queues, saved questions, and app controls.')}
      <section class="nk-settings-group"><div class="nk-kicker">REVISION</div><div>${row('refresh','Wrong questions',`${fmtNum(wrong)} missed · retrieval practice`,"window.QB.nav('wrong')",'is-red')}${row('clock','Due review',`${fmtNum(due)} ready today`,"window.QB.nav('review')",'is-blue')}${row('bookmark','Bookmarks',`${fmtNum(bm)} saved by you`,"window.QB.nav('bookmarks')",'is-violet')}</div></section>
      <section class="nk-settings-group"><div class="nk-kicker">STUDY</div><div>${row('test','Timed CBT','Build an exam from your topics','window.QB.openTestBuilder()','is-indigo')}${row('chart','Insights','Performance, completion, and timing',"window.QB.nav('analytics')",'is-green')}${row('book','Topics','Chapter-by-chapter study',"window.QB.nav('topics')",'is-blue')}</div></section>
      <section class="nk-settings-group"><div class="nk-kicker">APP & SOURCE</div><div class="nk-source-card"><span class="nk-settings-icon">${navIcon('book',19)}</span><div><strong>Offline and source-faithful</strong><p>Your progress, bookmarks, review schedules, and test history stay on this device. Original source PDFs remain bundled with the app.</p><div class="nk-source-actions">${activeSubject==='Biochemistry'?`<a href="assets/Biochemistry_QBank_Source.pdf" target="_blank">Open source PDF</a>`:''}<button onclick="window.QB.resetProgress()">Reset progress</button></div></div></div></section>
    </div>`,'more');
  }

  '''


LIBRARY = r'''function libraryPage(kind) {
    const lists={bookmarks:bookmarkedQuestions(),wrong:wrongQuestions(),review:dueQuestions()},list=lists[kind]||[];
    const meta={bookmarks:['Bookmarks','Questions you chose to revisit','bookmark'],wrong:['Wrong questions','Questions missed in previous attempts','refresh'],review:['Due review','Your spaced-repetition queue','clock']};
    const [title,sub,icon]=meta[kind];
    return shell(`<div class="nk-app-v114 nk-library-v114">${nkAppPageHead(`${activeSubject} · Revision`,title,sub,list.length?`<button class="nk-head-action" onclick="window.QB.startLibrary('${kind}')">Practice all ${navIcon('chevron',16)}</button>`:'')}
      <div class="nk-library-summary"><span>${navIcon(icon,20)}</span><div><b>${fmtNum(list.length)}</b><small>questions</small></div><p>${kind==='bookmarks'?'Saved manually during study.':kind==='wrong'?'Built automatically from incorrect attempts.':'Scheduled from your previous performance.'}</p></div>
      ${list.length?`<div class="nk-library-list">${list.map(q=>libraryRow(q,kind)).join('')}</div>`:nkAppEmpty(icon,kind==='bookmarks'?'Nothing bookmarked yet':kind==='wrong'?'No wrong questions yet':'Nothing is due right now',kind==='bookmarks'?'Use the bookmark button during Practice, CBT, or Review.':kind==='wrong'?'Incorrect attempts will appear here automatically.':'Keep practicing; due dates update after each attempt.')}
    </div>`,'more');
  }

  '''


EXAM_BUILDER = r'''function examBuilderMarkup(cid) {
    const selectedId=cid?String(cid):null;
    const rows=CHAPTERS.map(c=>`<label class="nk-builder-topic"><input type="checkbox" name="exam-chapter" value="${c.id}" ${(!selectedId||selectedId===String(c.id))?'checked':''} onchange="window.QB.updateExamPoolCount()"><span class="nk-builder-check">${navIcon('check',13)}</span><span><strong>${esc(c.title)}</strong><small>${fmtNum(c.questionCount)} questions</small></span></label>`).join('');
    const selectedCount=selectedId?1:CHAPTERS.length,pool=selectedId?chapterQuestions(selectedId).length:QUESTIONS.length;
    const countOptions=[10,20,30,40,60,80].filter(n=>n<=pool).map(n=>`<option value="${n}" ${n===Math.min(20,pool)?'selected':''}>${n} questions</option>`).join('');
    return `<div class="exam-builder nk-exam-builder-v114"><div class="nk-builder-section"><div class="nk-builder-label">Test scope</div><div class="nk-scope-choice"><button id="scope-all" class="${selectedId?'':'active'}" onclick="window.QB.setExamScope('all')"><strong>All topics</strong><small>Random questions from the full ${esc(activeSubject)} bank.</small></button><button id="scope-selected" class="${selectedId?'active':''}" onclick="window.QB.setExamScope('selected')"><strong>Selected topics</strong><small>Build a CBT from chapters you choose.</small></button></div></div><div id="exam-topic-panel" class="nk-builder-section ${selectedId?'':'hidden'}"><div class="nk-builder-row"><div class="nk-builder-label">Topics <span id="exam-selected-count">${selectedCount} selected</span></div><button onclick="window.QB.selectAllExamTopics()">Select all</button></div><div class="nk-builder-topic-list">${rows}</div></div><div class="nk-builder-section"><label class="nk-builder-label" for="session-count">Number of questions</label><select id="session-count" onchange="window.QB.updateExamPoolCount()">${countOptions||'<option value="1">1 question</option>'}</select><div id="exam-pool-count" class="nk-builder-pool">Question pool: ${fmtNum(pool)}</div></div><div class="nk-builder-actions"><button onclick="window.QB.closeModal()">Cancel</button><button class="is-primary" onclick="window.QB.confirmSession('${selectedId||''}','exam',${pool})">Start Exam</button></div></div>`;
  }

  '''


SESSION_BUILDER = r'''function openSessionBuilder(cid=null,forcedMode='practice') {
    const qs=cid?chapterQuestions(cid):QUESTIONS,title=cid?(CHAPTER_BY_ID[String(cid)]?.title||'Chapter'):`Mixed ${activeSubject}`;
    const exam=forcedMode==='exam';
    const practice=`<div class="nk-practice-builder"><span class="nk-modal-mode">${navIcon('book',20)}</span><h3>Start Practice</h3><p>${esc(title)} · immediate feedback, source explanations, and free navigation.</p><div class="nk-practice-count"><b>${fmtNum(qs.length)}</b><span>questions in source order</span></div><div class="nk-builder-actions"><button onclick="window.QB.closeModal()">Cancel</button><button class="is-primary" onclick="window.QB.confirmSession('${cid||''}','practice',${qs.length})">Start Practice</button></div></div>`;
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-modal-v114" id="modal"><div class="modal"><button class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button>${exam?`<div class="nk-modal-title"><span class="nk-modal-mode">${navIcon('test',20)}</span><div><h3>Build timed CBT</h3><p>${esc(title)} · 60 seconds per question.</p></div></div>${examBuilderMarkup(cid)}`:practice}</div></div>`);
  }

  '''


OPEN_TEST_BUILDER = r'''function openTestBuilder() {
    openMultiSubjectTestBuilder();
  }

  '''


MULTI_SUBJECT_WORKFLOWS = r'''
  function nkAllQuestionBank() {
    return SUBJECTS.flatMap(record=>(Array.isArray(record.questions)?record.questions:[]).map(q=>({...q,subject:q.subject||record.subject})));
  }

  function startAllSubjectPractice() {
    const pool=nkAllQuestionBank().slice();
    for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]];}
    startSession(pool.slice(0,Math.min(20,pool.length)).map(q=>q.id),'practice','All Subjects · Random Practice');
  }

  function nkMultiExamSelectedSubjectIndexes() {
    return [...document.querySelectorAll('input[name="nk-multi-subject"]:checked')].map(x=>Number(x.value));
  }

  function nkMultiExamPoolIds() {
    const selected=new Set(nkMultiExamSelectedSubjectIndexes());
    const topicScope=document.getElementById('nk-multi-scope-topics')?.classList.contains('active');
    const ids=[];
    SUBJECTS.forEach((record,index)=>{
      if(!selected.has(index)) return;
      let questions=Array.isArray(record.questions)?record.questions:[];
      if(topicScope){
        const topics=new Set([...document.querySelectorAll(`input.nk-multi-topic[data-subject-index="${index}"]:checked`)].map(x=>String(x.dataset.topicId)));
        questions=questions.filter(q=>topics.has(String(q.chapterId)));
      }
      questions.forEach(q=>ids.push(q.id));
    });
    return [...new Set(ids.map(String))];
  }

  function nkSetMultiExamScope(scope) {
    document.getElementById('nk-multi-scope-all')?.classList.toggle('active',scope==='all');
    document.getElementById('nk-multi-scope-topics')?.classList.toggle('active',scope==='topics');
    document.getElementById('nk-multi-topic-panel')?.classList.toggle('hidden',scope!=='topics');
    nkUpdateMultiExamPool();
  }

  function nkUpdateMultiExamPool() {
    const selected=new Set(nkMultiExamSelectedSubjectIndexes());
    document.querySelectorAll('.nk-multi-topic-group').forEach(group=>group.classList.toggle('is-disabled',!selected.has(Number(group.dataset.subjectIndex))));
    const ids=nkMultiExamPoolIds(),pool=ids.length;
    const subjectCount=document.getElementById('nk-multi-subject-count');
    if(subjectCount) subjectCount.textContent=`${selected.size} of ${SUBJECTS.length} selected`;
    const poolNode=document.getElementById('nk-multi-pool-count');
    if(poolNode) poolNode.textContent=`Question pool: ${fmtNum(pool)} across ${selected.size} subject${selected.size===1?'':'s'}`;
    const select=document.getElementById('nk-multi-session-count');
    if(select){
      const current=Number(select.value||20);
      let allowed=[10,20,30,40,60,80,100].filter(n=>n<=pool);
      if(pool>0&&!allowed.length) allowed=[pool];
      select.innerHTML=allowed.length?allowed.map(n=>`<option value="${n}">${n} questions</option>`).join(''):'<option value="0">No questions available</option>';
      const next=allowed.includes(current)?current:(allowed.includes(20)?20:(allowed[allowed.length-1]||0));
      select.value=String(next);
    }
  }

  function nkSelectAllMultiTopics() {
    const selected=new Set(nkMultiExamSelectedSubjectIndexes());
    document.querySelectorAll('input.nk-multi-topic').forEach(x=>{if(selected.has(Number(x.dataset.subjectIndex)))x.checked=true;});
    nkUpdateMultiExamPool();
  }

  function nkMultiExamBuilderMarkup() {
    const allCount=nkAllQuestionBank().length;
    const subjectChoices=SUBJECTS.map((record,index)=>{const stats=nkAppSubjectStats(record.subject),meta=nkAppSubjectMeta(record.subject);return `<label class="nk-multi-subject-card is-${meta.key}"><input type="checkbox" name="nk-multi-subject" value="${index}" checked onchange="window.QB.nkUpdateMultiExamPool()"><span class="nk-multi-subject-check">${navIcon('check',13)}</span><span class="nk-multi-subject-icon">${nkAppSubjectIcon(record.subject,23)}</span><span><strong>${esc(record.subject)}</strong><small>${fmtNum(stats.questions)} questions · ${fmtNum(stats.topics)} topics</small></span></label>`;}).join('');
    const topicGroups=SUBJECTS.map((record,index)=>{const topics=Array.isArray(record.topics)?record.topics:[];return `<section class="nk-multi-topic-group" data-subject-index="${index}"><header><span class="is-${nkAppSubjectMeta(record.subject).key}">${nkAppSubjectIcon(record.subject,17)}</span><strong>${esc(record.subject)}</strong><small>${topics.length} topics</small></header>${topics.map(topic=>`<label class="nk-builder-topic"><input class="nk-multi-topic" type="checkbox" data-subject-index="${index}" data-topic-id="${esc(String(topic.id))}" checked onchange="window.QB.nkUpdateMultiExamPool()"><span class="nk-builder-check">${navIcon('check',13)}</span><span><strong>${esc(topic.title)}</strong><small>${fmtNum(topic.questionCount)} questions</small></span></label>`).join('')}</section>`;}).join('');
    return `<div class="nk-multi-exam-builder"><div class="nk-builder-section"><div class="nk-builder-row"><div class="nk-builder-label">Subjects <span id="nk-multi-subject-count">${SUBJECTS.length} of ${SUBJECTS.length} selected</span></div></div><div class="nk-multi-subject-grid">${subjectChoices}</div></div><div class="nk-builder-section"><div class="nk-builder-label">Test scope</div><div class="nk-scope-choice"><button id="nk-multi-scope-all" class="active" onclick="window.QB.nkSetMultiExamScope('all')"><strong>All topics</strong><small>Random questions from every selected subject.</small></button><button id="nk-multi-scope-topics" onclick="window.QB.nkSetMultiExamScope('topics')"><strong>Selected topics</strong><small>Choose chapters across one or more subjects.</small></button></div></div><div id="nk-multi-topic-panel" class="nk-builder-section hidden"><div class="nk-builder-row"><div class="nk-builder-label">Topics</div><button onclick="window.QB.nkSelectAllMultiTopics()">Select all chosen subjects</button></div><div class="nk-multi-topic-list">${topicGroups}</div></div><div class="nk-builder-section"><label class="nk-builder-label" for="nk-multi-session-count">Number of questions</label><select id="nk-multi-session-count">${[10,20,30,40,60,80,100].map(n=>`<option value="${n}" ${n===20?'selected':''}>${n} questions</option>`).join('')}</select><div id="nk-multi-pool-count" class="nk-builder-pool">Question pool: ${fmtNum(allCount)} across ${SUBJECTS.length} subjects</div></div><div class="nk-builder-actions"><button onclick="window.QB.closeModal()">Cancel</button><button class="is-primary" onclick="window.QB.nkConfirmMultiSubjectExam()">Start Exam</button></div></div>`;
  }

  function openMultiSubjectTestBuilder() {
    document.body.insertAdjacentHTML('beforeend',`<div class="modal-backdrop nk-modal-v114" id="modal"><div class="modal nk-multi-modal"><button class="nk-modal-close" aria-label="Close" onclick="window.QB.closeModal()">${navIcon('close',20)}</button><div class="nk-modal-title"><span class="nk-modal-mode">${navIcon('test',20)}</span><div><h3>Build timed CBT</h3><p>Mix Biochemistry, Physiology, and Anatomy · 60 seconds per question.</p></div></div>${nkMultiExamBuilderMarkup()}</div></div>`);
    nkUpdateMultiExamPool();
  }

  function nkConfirmMultiSubjectExam() {
    const indexes=nkMultiExamSelectedSubjectIndexes();
    if(!indexes.length){showToast('Select at least one subject.','bad');return;}
    const ids=nkMultiExamPoolIds();
    if(!ids.length){showToast('Select at least one topic with questions.','bad');return;}
    for(let i=ids.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[ids[i],ids[j]]=[ids[j],ids[i]];}
    const count=Math.min(Number(document.getElementById('nk-multi-session-count')?.value||20),ids.length);
    const names=indexes.map(i=>SUBJECTS[i]?.subject).filter(Boolean);
    const title=names.length===SUBJECTS.length?'All Subjects CBT':names.length===1?`${names[0]} CBT`:'Mixed Subjects CBT';
    closeModal();
    startSession(ids.slice(0,count),'exam',title);
  }

  '''


RESULT = r'''function resultPage(testId) {
    const t=state.tests.find(x=>x.id===testId);if(!t)return testsPage();
    const isPractice=t.kind==='practice',score=t.total?t.correct/t.total*100:0,attempted=t.correct+t.incorrect;
    const totalQuestionTime=Object.values(t.questionTimes||{}).reduce((a,b)=>a+(b||0),0),attemptedQuestionTime=Object.keys(t.answers||{}).reduce((a,id)=>a+((t.questionTimes||{})[id]||0),0);
    return shell(`<div class="nk-app-v114 nk-result-v114"><button class="nk-back-link" onclick="window.QB.nav('${isPractice?'dashboard':'tests'}')">${navIcon('back',18)} ${isPractice?'Home':'Tests'}</button>${nkAppPageHead(`${isPractice?'Practice':'Timed CBT'} · ${fmtDate(t.createdAt)}`,isPractice?'Practice analysis':'Test analysis',t.title,`<button class="nk-head-action v102-review-action" type="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))">Review Solutions ${navIcon('chevron',16)}</button>`)}
      <section class="nk-result-overview"><div><div class="nk-kicker">YOU SCORED</div><b>${fmtPct(score)}</b><strong>${t.correct} / ${t.total} correct</strong><p>${score>=75?'Strong retrieval. Review the misses and keep the pattern.':score>=50?'A useful baseline. Review the incorrect answers while they are fresh.':'This set has identified exactly what needs another pass.'}</p></div>${donut(score,142)}</section>
      <div class="nk-result-counts"><div class="is-correct"><b>${t.correct}</b><span>Correct</span></div><div class="is-wrong"><b>${t.incorrect}</b><span>Incorrect</span></div><div class="is-missed"><b>${t.unattempted}</b><span>Unattempted</span></div></div>
      <div class="nk-insight-grid nk-result-stats"><article class="is-blue"><span>${navIcon('clock',18)}</span><small>Time taken</small><b>${formatDuration(t.totalTimeMs)}</b><p>${fmtNum(t.questionIds.length)} questions</p></article><article class="is-violet"><span>${navIcon('chart',18)}</span><small>Avg. time / attempted</small><b>${formatDuration(t.attempted?attemptedQuestionTime/t.attempted:0)}</b><p>selected answers only</p></article><article class="is-amber"><span>${navIcon('book',18)}</span><small>Avg. time / question</small><b>${formatDuration(t.total?totalQuestionTime/t.total:0)}</b><p>includes skips</p></article><article class="is-green"><span>${navIcon('check',18)}</span><small>Completion</small><b>${fmtPct(t.total?attempted/t.total*100:0)}</b><p>${attempted} attempted</p></article></div>
      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">QUESTION REVIEW</div><h2>Every answer</h2></div><button class="nk-text-link v102-review-action" type="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))">Open review ${navIcon('chevron',15)}</button></div><div class="nk-result-questions">${t.questionIds.map((id,i)=>{const q=BY_ID[id],sel=t.answers[id],corr=Number(q.correctOption)===Number(sel);return `<div><span class="nk-question-index">${i+1}</span><span><strong>${esc(q.question.slice(0,125))}${q.question.length>125?'…':''}</strong><small><i class="nk-status ${sel?(corr?'is-correct':'is-wrong'):'is-unattempted'}">${sel?(corr?'Correct':'Incorrect'):'Unattempted'}</i>${esc(q.chapter)}</small></span></div>`}).join('')}</div></section>
    </div>`,'tests');
  }

  '''


CSS = r'''<style id="nk-whole-app-vision-v114">
:root{--nk114-canvas:#f7f8fc;--nk114-surface:#fff;--nk114-ink:#121736;--nk114-muted:#727991;--nk114-line:#e3e6ef;--nk114-indigo:#29265f;--nk114-blue:#3979ed;--nk114-green:#119a68;--nk114-red:#c54d5b;--nk114-amber:#d69122;--nk114-violet:#7658bf;--nk114-magenta:#a22a80}
body:has(.nk-app-v114){background:var(--nk114-canvas)!important;color:var(--nk114-ink)}body:has(.nk-app-v114) .page{max-width:1040px!important;padding:22px 20px 104px!important}body:has(.nk-app-v114) .v102-topbar,body:has(.nk-app-v114) .topbar{display:none!important}.nk-app-v114{max-width:980px;margin:0 auto;color:var(--nk114-ink)}.nk-app-v114 button,.nk-global-header-v114 button,.nk-bottom-nav-v114 button{font:inherit}.nk-global-header-v114{height:58px;background:#fff;border-bottom:1px solid var(--nk114-line);position:sticky;top:0;z-index:80}.nk-global-inner{width:min(100% - 32px,980px);height:100%;margin:auto;display:flex;align-items:center;justify-content:space-between}.nk-global-brand{display:flex;align-items:baseline;gap:5px;letter-spacing:-.35px}.nk-global-brand strong{font-size:18px;font-weight:900;color:var(--nk114-indigo)}.nk-global-brand>span{font-size:15px;font-weight:760;color:var(--nk114-ink)}.nk-global-subject{display:flex;align-items:center;gap:7px;padding:7px 10px;border-radius:11px;background:#f3f4f8;color:#4b5575;font-size:11px;font-weight:750}.nk-global-subject.is-physiology{color:#ad4c4c;background:#fff1ef}.nk-global-subject.is-biochemistry{color:#972675;background:#f9edf6}.nk-global-subject.is-anatomy{color:#27758e;background:#ecf7fb}.nk-subject-svg{display:block;flex:none}
.nk-page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;padding:5px 0 18px;border-bottom:1px solid var(--nk114-line)}.nk-kicker{font-size:10px;letter-spacing:1.35px;font-weight:850;color:#52699e}.nk-page-head h1,.nk-chapter-title h1{font-size:30px;line-height:1.08;letter-spacing:-1.15px;margin:6px 0 5px}.nk-page-head p,.nk-chapter-title p{margin:0;color:var(--nk114-muted);font-size:13px;line-height:1.45}.nk-head-action,.nk-inline-action{border:0;background:var(--nk114-indigo);color:#fff;min-height:43px;padding:0 15px;border-radius:11px;display:inline-flex;align-items:center;justify-content:center;gap:7px;font-size:12px;font-weight:800;white-space:nowrap}.nk-text-link{border:0;background:none;color:#4966a8;display:flex;align-items:center;gap:3px;font-size:12px;font-weight:800;padding:4px}.nk-section{padding-top:27px}.nk-section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;padding:0 2px 11px}.nk-section-head h2{font-size:21px;line-height:1.08;letter-spacing:-.55px;margin:4px 0 0}.nk-section-head>span{font-size:11px;color:var(--nk114-muted)}
.nk-streak-strip{min-height:76px;margin-top:14px;padding:11px 14px;background:#fff;border:1px solid #f1d7b5;border-radius:14px;display:flex;align-items:center;justify-content:space-between;gap:14px;box-shadow:0 6px 20px rgba(182,102,24,.08)}.nk-streak-copy{display:flex;align-items:center;gap:11px}.nk-streak-flame{width:44px;height:44px;border-radius:13px;background:#fff1da;color:#e26f19;display:grid;place-items:center;box-shadow:inset 0 0 0 1px #ffdfb3}.nk-streak-strip.is-burning .nk-streak-flame{background:#f47a20;color:#fff;box-shadow:0 7px 17px rgba(226,105,24,.27)}.nk-streak-copy strong,.nk-streak-copy small{display:block}.nk-streak-copy strong{font-size:14px}.nk-streak-copy small{font-size:9.5px;color:#8b684d;margin-top:3px}.nk-week-strip{display:flex;gap:5px}.nk-week-day{display:grid;gap:3px;justify-items:center}.nk-week-day i{width:23px;height:23px;border-radius:8px;background:#f3f2f0;display:grid;place-items:center;color:#fff}.nk-week-day b{font-size:9px;color:#8a90a3}.nk-week-day.is-done i{background:#f47a20;box-shadow:0 3px 8px rgba(226,105,24,.2)}.nk-week-day.is-today i{box-shadow:0 0 0 2px #ffc57e}.nk-focus-panel{margin-top:16px;padding:22px;background:var(--nk114-indigo);color:#fff;border-radius:16px}.nk-focus-panel .nk-kicker{color:#bfc9f5}.nk-focus-panel h2{font-size:23px;line-height:1.17;letter-spacing:-.55px;margin:6px 0}.nk-focus-panel p{color:#c9cee5;margin:0;font-size:12px;line-height:1.45}.nk-focus-actions{display:grid;grid-template-columns:1.4fr .8fr .8fr;gap:8px;margin-top:18px}.nk-focus-actions:has(>button:nth-child(4)){grid-template-columns:1.2fr 1fr 1fr 1fr}.nk-focus-actions button{min-height:48px;padding:8px 12px;border:1px solid rgba(255,255,255,.26);border-radius:11px;background:#3a376f;color:#fff;font-size:11px;font-weight:800}.nk-focus-actions .nk-focus-primary{background:#fff;color:var(--nk114-indigo);border-color:#fff;display:flex;align-items:center;justify-content:center;gap:7px}
.nk-subject-list,.nk-session-list,.nk-compact-list,.nk-topic-list,.nk-library-list,.nk-performance-list,.nk-result-questions{background:#fff;border:1px solid var(--nk114-line);border-radius:14px;overflow:hidden}.nk-subject-row{width:100%;min-height:82px;display:grid;grid-template-columns:42px minmax(0,1fr) 44px 22px;gap:11px;align-items:center;padding:11px 14px;border:0;border-bottom:1px solid var(--nk114-line);background:#fff;text-align:left;color:var(--nk114-ink)}.nk-subject-row:last-child{border-bottom:0}.nk-subject-row.is-active{box-shadow:inset 3px 0 0 var(--nk114-blue);background:#fafbff}.nk-subject-mark,.nk-quick-icon,.nk-settings-icon,.nk-test-icon{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;background:#f1f3f7;color:#52617c}.nk-subject-row.is-physiology .nk-subject-mark{background:#fff0ee;color:#c2534b}.nk-subject-row.is-biochemistry .nk-subject-mark{background:#f9edf6;color:var(--nk114-magenta)}.nk-subject-row.is-anatomy .nk-subject-mark{background:#edf7fc;color:#277899}.nk-subject-copy{min-width:0}.nk-subject-copy strong,.nk-subject-copy small{display:block}.nk-subject-copy strong{font-size:15px}.nk-subject-copy small{font-size:10.5px;color:var(--nk114-muted);margin-top:3px}.nk-line-progress{display:block;height:4px;border-radius:99px;background:#edf0f5;overflow:hidden;margin-top:7px}.nk-line-progress>i,.nk-line-progress>span{display:block;height:100%;border-radius:inherit;background:var(--nk114-blue)}.nk-subject-percent{font-size:11px;font-weight:800;text-align:right}.nk-metric-grid{display:grid;grid-template-columns:repeat(4,1fr);background:#fff;border:1px solid var(--nk114-line);border-radius:14px;overflow:hidden}.nk-metric-grid>div{padding:15px;border-right:1px solid var(--nk114-line)}.nk-metric-grid>div:last-child{border-right:0}.nk-metric-grid b,.nk-metric-grid strong,.nk-metric-grid small{display:block}.nk-metric-grid b{font-size:23px;letter-spacing:-.6px}.nk-metric-grid strong{font-size:11px;margin-top:3px}.nk-metric-grid small{font-size:9.5px;color:var(--nk114-muted);margin-top:2px}
.nk-quick-grid{display:grid;grid-template-columns:1fr 1fr;background:#fff;border:1px solid var(--nk114-line);border-radius:14px;overflow:hidden}.nk-quick-grid button{min-height:72px;display:grid;grid-template-columns:36px 1fr 18px;align-items:center;gap:10px;padding:10px 13px;border:0;border-right:1px solid var(--nk114-line);border-bottom:1px solid var(--nk114-line);background:#fff;text-align:left;color:var(--nk114-ink)}.nk-quick-grid button:nth-child(2n){border-right:0}.nk-quick-grid button:nth-last-child(-n+2){border-bottom:0}.nk-quick-grid strong,.nk-quick-grid small{display:block}.nk-quick-grid strong{font-size:12px}.nk-quick-grid small{font-size:9.5px;color:var(--nk114-muted);margin-top:3px}.nk-quick-icon{width:32px;height:32px}.nk-quick-icon.is-red{background:#fff0f1;color:var(--nk114-red)}.nk-quick-icon.is-blue{background:#edf4ff;color:var(--nk114-blue)}.nk-quick-icon.is-violet{background:#f3effc;color:var(--nk114-violet)}.nk-quick-icon.is-green{background:#eaf8f3;color:var(--nk114-green)}.nk-home-lower{display:grid;grid-template-columns:1fr 1fr;gap:22px}.nk-compact-row,.nk-test-row{min-height:62px;display:grid;align-items:center;gap:10px;padding:9px 12px;border:0;border-bottom:1px solid var(--nk114-line);background:#fff;color:var(--nk114-ink);text-align:left}.nk-compact-row:last-child,.nk-test-row:last-child{border-bottom:0}.nk-compact-row{grid-template-columns:26px 1fr 48px}.nk-rank,.nk-question-index,.nk-topic-index{width:26px;height:26px;border-radius:8px;background:#f0f2f6;display:grid;place-items:center;color:#59617a;font-size:10px;font-weight:850}.nk-compact-row strong,.nk-compact-row small,.nk-test-row strong,.nk-test-row small{display:block}.nk-compact-row strong,.nk-test-row strong{font-size:11.5px}.nk-compact-row small,.nk-test-row small{font-size:9.5px;color:var(--nk114-muted);margin-top:3px}.nk-compact-row>b{font-size:10.5px;text-align:right}.nk-test-row{width:100%;grid-template-columns:36px minmax(0,1fr) 48px 18px}.nk-test-icon.is-practice{background:#eaf8f3;color:var(--nk114-green)}.nk-test-icon.is-cbt{background:#eef1ff;color:#4d54ad}.nk-test-score{font-size:11px;font-weight:850;text-align:right}.nk-empty{min-height:150px;padding:24px;background:#fff;border:1px solid var(--nk114-line);border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}.nk-empty-icon{width:46px;height:46px;border-radius:14px;background:#f1f4fa;color:#5570aa;display:grid;place-items:center}.nk-empty strong{font-size:13px;margin-top:10px}.nk-empty p{max-width:330px;margin:5px 0 0;color:var(--nk114-muted);font-size:10.5px;line-height:1.45}.nk-empty .nk-inline-action{margin-top:12px}
.nk-subject-switch{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:15px 0}.nk-subject-switch button{min-height:42px;border:1px solid var(--nk114-line);border-radius:11px;background:#fff;color:#65708a;display:flex;align-items:center;justify-content:center;gap:7px;font-size:10.5px;font-weight:750}.nk-subject-switch button.is-active{border-color:#9db9f7;background:#f0f5ff;color:#254eae}.nk-topic-tools{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center}.nk-search{height:44px;border:1px solid var(--nk114-line);border-radius:11px;background:#fff;display:flex;align-items:center;gap:8px;padding:0 12px;color:#7a839b}.nk-search input{width:100%;border:0;outline:0;background:transparent;color:var(--nk114-ink);font-size:12px}.nk-filter-tabs{display:flex;padding:3px;border:1px solid var(--nk114-line);border-radius:11px;background:#fff}.nk-filter-tabs button{height:34px;padding:0 10px;border:0;border-radius:8px;background:transparent;color:#6e7589;font-size:10px;font-weight:750}.nk-filter-tabs button.is-active{background:var(--nk114-indigo);color:#fff}.nk-topic-summary{display:flex;gap:16px;padding:13px 2px;color:var(--nk114-muted);font-size:10px}.nk-topic-summary b{color:var(--nk114-ink);font-size:12px}.nk-topic-row{width:100%;min-height:76px;display:grid;grid-template-columns:32px minmax(0,1fr) 54px;gap:11px;align-items:center;padding:10px 13px;border:0;border-bottom:1px solid var(--nk114-line);background:#fff;text-align:left;color:var(--nk114-ink)}.nk-topic-row:last-child{border-bottom:0}.nk-topic-copy strong,.nk-topic-copy small{display:block}.nk-topic-copy strong{font-size:12.5px}.nk-topic-copy small{font-size:9.5px;color:var(--nk114-muted);margin-top:3px}.nk-topic-side{display:flex;align-items:center;justify-content:flex-end;gap:5px}.nk-topic-side b{font-size:10px}
.nk-back-link{border:0;background:none;color:#526594;display:flex;align-items:center;gap:6px;font-size:11px;font-weight:800;padding:4px 0 12px}.nk-chapter-hero{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:24px;padding:22px;background:#fff;border:1px solid var(--nk114-line);border-radius:15px}.nk-chapter-title .nk-line-progress{max-width:380px;margin-top:15px}.nk-chapter-actions{display:grid;gap:8px}.nk-chapter-actions button{min-height:62px;display:grid;grid-template-columns:30px 1fr 18px;align-items:center;gap:8px;padding:9px 11px;border:1px solid var(--nk114-line);border-radius:11px;background:#fff;color:var(--nk114-ink);text-align:left}.nk-chapter-actions button.is-primary{background:var(--nk114-indigo);border-color:var(--nk114-indigo);color:#fff}.nk-chapter-actions strong,.nk-chapter-actions small{display:block}.nk-chapter-actions strong{font-size:12px}.nk-chapter-actions small{font-size:9px;opacity:.72;margin-top:2px}.nk-chapter-metrics{margin-top:12px}.nk-library-row{width:100%;min-height:72px;display:grid;grid-template-columns:30px minmax(0,1fr) 18px;gap:10px;align-items:center;padding:10px 12px;border:0;border-bottom:1px solid var(--nk114-line);background:#fff;color:var(--nk114-ink);text-align:left}.nk-library-row:last-child{border-bottom:0}.nk-library-row strong{display:block;font-size:11px;line-height:1.4}.nk-library-row small{display:flex;align-items:center;gap:7px;color:var(--nk114-muted);font-size:9px;margin-top:5px}.nk-status{font-style:normal;padding:3px 6px;border-radius:6px;background:#f0f2f5;color:#687086}.nk-status.is-correct{background:#eaf8f3;color:var(--nk114-green)}.nk-status.is-wrong{background:#fff0f1;color:var(--nk114-red)}
.nk-test-hero{display:grid;grid-template-columns:54px minmax(0,1fr) auto;align-items:center;gap:16px;margin-top:15px;padding:20px;background:var(--nk114-indigo);color:#fff;border-radius:15px}.nk-test-hero-icon{width:50px;height:50px;border-radius:14px;background:#3c3973;display:grid;place-items:center}.nk-test-hero h2{font-size:20px;margin:4px 0 5px}.nk-test-hero p{margin:0;color:#c8cce1;font-size:10.5px}.nk-test-hero>button{min-height:45px;padding:0 14px;border:0;border-radius:11px;background:#fff;color:var(--nk114-indigo);font-size:11px;font-weight:850;display:flex;align-items:center;gap:6px}.nk-exam-principles{display:flex;flex-wrap:wrap;gap:12px;margin-top:12px;color:#e3e5f2;font-size:9.5px}.nk-exam-principles span{display:flex;align-items:center;gap:4px}
.nk-insight-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:15px}.nk-insight-grid article{min-height:116px;padding:13px;background:#fff;border:1px solid var(--nk114-line);border-radius:13px}.nk-insight-grid article>span{width:29px;height:29px;border-radius:9px;display:grid;place-items:center}.nk-insight-grid article>small,.nk-insight-grid article>b,.nk-insight-grid article>p{display:block}.nk-insight-grid article>small{font-size:9.5px;color:var(--nk114-muted);margin-top:9px}.nk-insight-grid article>b{font-size:20px;margin-top:3px}.nk-insight-grid article>p{font-size:9px;color:var(--nk114-muted);margin:3px 0 0}.nk-insight-grid .is-green>span{background:#eaf8f3;color:var(--nk114-green)}.nk-insight-grid .is-blue>span{background:#edf4ff;color:var(--nk114-blue)}.nk-insight-grid .is-amber>span{background:#fff5e7;color:var(--nk114-amber)}.nk-insight-grid .is-violet>span{background:#f3effc;color:var(--nk114-violet)}.nk-performance-list button{width:100%;min-height:67px;padding:9px 12px;border:0;border-bottom:1px solid var(--nk114-line);background:#fff;color:var(--nk114-ink);display:grid;grid-template-columns:minmax(0,1fr) 48px 18px;align-items:center;gap:9px;text-align:left}.nk-performance-list button:last-child{border-bottom:0}.nk-performance-list strong,.nk-performance-list small{display:block}.nk-performance-list strong{font-size:11.5px}.nk-performance-list small{font-size:9px;color:var(--nk114-muted);margin-top:3px}.nk-performance-list .nk-line-progress{width:min(100%,390px)}.nk-performance-list button>b{font-size:10.5px;text-align:right}
.nk-settings-group{margin-top:22px}.nk-settings-group>.nk-kicker{margin:0 2px 8px}.nk-settings-group>div{background:#fff;border:1px solid var(--nk114-line);border-radius:14px;overflow:hidden}.nk-settings-row{width:100%;min-height:67px;padding:10px 13px;border:0;border-bottom:1px solid var(--nk114-line);background:#fff;color:var(--nk114-ink);display:grid;grid-template-columns:36px 1fr 18px;align-items:center;gap:10px;text-align:left}.nk-settings-row:last-child{border-bottom:0}.nk-settings-row strong,.nk-settings-row small{display:block}.nk-settings-row strong{font-size:12px}.nk-settings-row small{font-size:9.5px;color:var(--nk114-muted);margin-top:3px}.nk-settings-row.is-red .nk-settings-icon{background:#fff0f1;color:var(--nk114-red)}.nk-settings-row.is-blue .nk-settings-icon{background:#edf4ff;color:var(--nk114-blue)}.nk-settings-row.is-violet .nk-settings-icon{background:#f3effc;color:var(--nk114-violet)}.nk-settings-row.is-green .nk-settings-icon{background:#eaf8f3;color:var(--nk114-green)}.nk-settings-row.is-indigo .nk-settings-icon{background:#efeff9;color:var(--nk114-indigo)}.nk-source-card{display:grid;grid-template-columns:36px 1fr;gap:11px;padding:14px}.nk-source-card strong{font-size:12px}.nk-source-card p{font-size:10px;line-height:1.5;color:var(--nk114-muted);margin:5px 0 12px}.nk-source-actions{display:flex;gap:8px}.nk-source-actions a,.nk-source-actions button{min-height:36px;padding:0 10px;border:1px solid var(--nk114-line);border-radius:9px;background:#fff;color:#4d5f8d;display:inline-flex;align-items:center;text-decoration:none;font-size:10px;font-weight:800}.nk-source-actions button{color:var(--nk114-red)}
.nk-library-summary{display:grid;grid-template-columns:40px auto 1fr;align-items:center;gap:11px;margin:15px 0;padding:13px;background:#fff;border:1px solid var(--nk114-line);border-radius:13px}.nk-library-summary>span{width:38px;height:38px;border-radius:11px;background:#edf4ff;color:var(--nk114-blue);display:grid;place-items:center}.nk-library-summary b,.nk-library-summary small{display:block}.nk-library-summary b{font-size:20px}.nk-library-summary small{font-size:9px;color:var(--nk114-muted)}.nk-library-summary p{margin:0;padding-left:12px;border-left:1px solid var(--nk114-line);color:var(--nk114-muted);font-size:10px}
.nk-result-overview{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:15px;padding:20px 24px;background:#fff;border:1px solid var(--nk114-line);border-radius:15px}.nk-result-overview>div:first-child>b,.nk-result-overview>div:first-child>strong{display:block}.nk-result-overview>div:first-child>b{font-size:40px;letter-spacing:-1.6px;margin-top:5px}.nk-result-overview>div:first-child>strong{font-size:12px}.nk-result-overview p{max-width:470px;color:var(--nk114-muted);font-size:10.5px;line-height:1.5;margin:8px 0 0}.nk-result-counts{display:grid;grid-template-columns:repeat(3,1fr);margin-top:10px;background:#fff;border:1px solid var(--nk114-line);border-radius:13px;overflow:hidden}.nk-result-counts div{padding:13px;text-align:center;border-right:1px solid var(--nk114-line)}.nk-result-counts div:last-child{border-right:0}.nk-result-counts b,.nk-result-counts span{display:block}.nk-result-counts b{font-size:20px}.nk-result-counts span{font-size:9.5px;color:var(--nk114-muted);margin-top:2px}.nk-result-counts .is-correct b{color:var(--nk114-green)}.nk-result-counts .is-wrong b{color:var(--nk114-red)}.nk-result-counts .is-missed b{color:var(--nk114-amber)}.nk-result-questions>div{min-height:64px;padding:9px 12px;border-bottom:1px solid var(--nk114-line);display:grid;grid-template-columns:30px 1fr;gap:10px;align-items:center}.nk-result-questions>div:last-child{border-bottom:0}.nk-result-questions strong{display:block;font-size:10.5px;line-height:1.35}.nk-result-questions small{display:flex;align-items:center;gap:7px;color:var(--nk114-muted);font-size:9px;margin-top:4px}
.nk-modal-v114{z-index:1500!important;padding:14px!important}.nk-modal-v114 .modal{position:relative;width:min(100%,560px)!important;max-height:calc(100vh - 28px)!important;overflow:auto!important;padding:20px!important;border-radius:18px!important}.nk-modal-close{position:absolute;right:12px;top:12px;width:38px;height:38px;border:0;border-radius:10px;background:#f2f3f7;color:#4d5671;display:grid;place-items:center}.nk-modal-title{display:flex;align-items:center;gap:11px;padding-right:42px}.nk-modal-title h3,.nk-practice-builder h3{font-size:19px;margin:0}.nk-modal-title p,.nk-practice-builder p{font-size:10.5px;color:var(--nk114-muted);margin:4px 0 0;line-height:1.45}.nk-modal-mode{width:40px;height:40px;border-radius:11px;background:#eef1ff;color:var(--nk114-indigo);display:grid;place-items:center}.nk-exam-builder-v114{margin-top:17px}.nk-builder-section{padding:14px 0;border-top:1px solid var(--nk114-line)}.nk-builder-label{font-size:10px;font-weight:850;color:#535c75}.nk-scope-choice{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:7px}.nk-scope-choice button{min-height:70px;padding:10px;border:1px solid var(--nk114-line);border-radius:11px;background:#fff;text-align:left;color:var(--nk114-ink)}.nk-scope-choice button.active{border-color:#789cf0;background:#f1f5ff}.nk-scope-choice strong,.nk-scope-choice small{display:block}.nk-scope-choice strong{font-size:11px}.nk-scope-choice small{font-size:9px;line-height:1.35;color:var(--nk114-muted);margin-top:4px}.nk-builder-row{display:flex;align-items:center;justify-content:space-between}.nk-builder-row button{border:0;background:none;color:#4464b0;font-size:10px;font-weight:800}.nk-builder-topic-list{max-height:210px;overflow:auto;margin-top:7px;border:1px solid var(--nk114-line);border-radius:11px}.nk-builder-topic{min-height:50px;padding:8px 10px;border-bottom:1px solid var(--nk114-line);display:grid;grid-template-columns:25px 1fr;align-items:center;gap:8px}.nk-builder-topic:last-child{border-bottom:0}.nk-builder-topic input{position:absolute;opacity:0}.nk-builder-check{width:21px;height:21px;border:1px solid #cbd1df;border-radius:6px;color:transparent;display:grid;place-items:center}.nk-builder-topic input:checked+.nk-builder-check{background:var(--nk114-blue);border-color:var(--nk114-blue);color:#fff}.nk-builder-topic strong,.nk-builder-topic small{display:block}.nk-builder-topic strong{font-size:10.5px}.nk-builder-topic small{font-size:8.5px;color:var(--nk114-muted);margin-top:2px}.nk-builder-section select{width:100%;height:43px;margin-top:7px;padding:0 10px;border:1px solid var(--nk114-line);border-radius:10px;background:#fff;color:var(--nk114-ink)}.nk-builder-pool{font-size:9px;color:var(--nk114-muted);margin-top:5px}.nk-builder-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:15px}.nk-builder-actions button{min-height:44px;border:1px solid var(--nk114-line);border-radius:10px;background:#fff;color:var(--nk114-ink);font-weight:800;font-size:11px}.nk-builder-actions button.is-primary{background:var(--nk114-indigo);border-color:var(--nk114-indigo);color:#fff}.nk-practice-builder{text-align:center}.nk-practice-builder>.nk-modal-mode{margin:0 auto 10px}.nk-practice-count{margin-top:15px;padding:15px;border:1px solid var(--nk114-line);border-radius:12px}.nk-practice-count b,.nk-practice-count span{display:block}.nk-practice-count b{font-size:24px}.nk-practice-count span{font-size:9px;color:var(--nk114-muted)}
.nk-multi-modal{width:min(100%,650px)!important}.nk-multi-exam-builder{margin-top:17px}.nk-multi-subject-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:8px}.nk-multi-subject-card{position:relative;min-height:78px;padding:10px 8px;border:1px solid var(--nk114-line);border-radius:12px;background:#fff;display:grid;grid-template-columns:31px 1fr;align-items:center;gap:7px;color:var(--nk114-ink)}.nk-multi-subject-card>input{position:absolute;opacity:0}.nk-multi-subject-check{position:absolute;right:7px;top:7px;width:18px;height:18px;border:1px solid #cbd1df;border-radius:6px;color:transparent;display:grid;place-items:center}.nk-multi-subject-card>input:checked~.nk-multi-subject-check{background:var(--nk114-indigo);border-color:var(--nk114-indigo);color:#fff}.nk-multi-subject-card:has(input:checked){border-color:#9caae0;background:#fafaff}.nk-multi-subject-icon{width:31px;height:31px;border-radius:9px;display:grid;place-items:center}.nk-multi-subject-card.is-biochemistry .nk-multi-subject-icon{background:#f9edf6;color:var(--nk114-magenta)}.nk-multi-subject-card.is-physiology .nk-multi-subject-icon{background:#fff0ee;color:#c2534b}.nk-multi-subject-card.is-anatomy .nk-multi-subject-icon{background:#edf7fc;color:#277899}.nk-multi-subject-card strong,.nk-multi-subject-card small{display:block;padding-right:12px}.nk-multi-subject-card strong{font-size:10.5px}.nk-multi-subject-card small{font-size:8px;line-height:1.35;color:var(--nk114-muted);margin-top:3px}.nk-multi-topic-list{max-height:250px;overflow:auto;margin-top:7px;border:1px solid var(--nk114-line);border-radius:11px}.nk-multi-topic-group+ .nk-multi-topic-group{border-top:6px solid #f4f5f8}.nk-multi-topic-group>header{position:sticky;top:0;z-index:1;min-height:40px;padding:7px 10px;background:#fafbfe;border-bottom:1px solid var(--nk114-line);display:grid;grid-template-columns:25px 1fr auto;align-items:center;gap:7px}.nk-multi-topic-group>header>span{width:25px;height:25px;border-radius:7px;display:grid;place-items:center}.nk-multi-topic-group>header .is-biochemistry{background:#f9edf6;color:var(--nk114-magenta)}.nk-multi-topic-group>header .is-physiology{background:#fff0ee;color:#c2534b}.nk-multi-topic-group>header .is-anatomy{background:#edf7fc;color:#277899}.nk-multi-topic-group>header strong{font-size:10.5px}.nk-multi-topic-group>header small{font-size:8.5px;color:var(--nk114-muted)}.nk-multi-topic-group.is-disabled{display:none}.nk-multi-exam-builder select{width:100%;height:43px;margin-top:7px;padding:0 10px;border:1px solid var(--nk114-line);border-radius:10px;background:#fff;color:var(--nk114-ink)}
.nk-bottom-nav-v114{height:76px!important;background:#fff!important;border-top:1px solid var(--nk114-line)!important;box-shadow:0 -4px 14px rgba(27,34,67,.06)!important;padding:6px max(10px,env(safe-area-inset-left)) calc(6px + env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-right))!important}.nk-bottom-nav-v114 .nav-item{min-height:58px!important;color:#7b8191!important}.nk-bottom-nav-v114 .nav-icon-wrap{width:36px!important;height:31px!important;border-radius:10px!important}.nk-bottom-nav-v114 .nav-label{font-size:9px!important;font-weight:750!important}.nk-bottom-nav-v114 .nav-item.active{color:var(--nk114-indigo)!important}.nk-bottom-nav-v114 .nav-item.active .nav-icon-wrap{background:#eff1fb!important;box-shadow:inset 0 0 0 1px #d9def3!important}
@media(max-width:760px){body:has(.nk-app-v114) .page{padding:16px 14px 98px!important}.nk-page-head h1,.nk-chapter-title h1{font-size:26px}.nk-home-lower{grid-template-columns:1fr}.nk-chapter-hero{grid-template-columns:1fr}.nk-test-hero{grid-template-columns:44px 1fr}.nk-test-hero>button{grid-column:1/-1}.nk-insight-grid{grid-template-columns:1fr 1fr}.nk-topic-tools{grid-template-columns:1fr}.nk-filter-tabs{overflow:auto}.nk-filter-tabs button{flex:1;white-space:nowrap}.nk-subject-switch button span{display:none}}
@media(max-width:480px){.nk-page-head{align-items:flex-start}.nk-page-head p{font-size:11px}.nk-head-action{min-height:40px;padding:0 10px;font-size:10px}.nk-streak-strip{align-items:flex-start}.nk-streak-copy small{display:none}.nk-week-strip{gap:3px}.nk-week-day i{width:19px;height:19px}.nk-focus-panel{padding:18px}.nk-focus-panel h2{font-size:20px}.nk-focus-actions{grid-template-columns:1fr 1fr}.nk-focus-actions .nk-focus-primary{grid-column:1/-1}.nk-metric-grid{grid-template-columns:1fr 1fr}.nk-metric-grid>div:nth-child(2){border-right:0}.nk-metric-grid>div:nth-child(-n+2){border-bottom:1px solid var(--nk114-line)}.nk-subject-row{grid-template-columns:38px minmax(0,1fr) 36px 18px;padding-left:10px}.nk-quick-grid button{grid-template-columns:30px 1fr 15px;padding:9px}.nk-quick-icon{width:29px;height:29px}.nk-result-overview{padding:17px}.nk-result-overview .ring{width:104px!important;height:104px!important}.nk-result-overview>div:first-child>b{font-size:34px}.nk-library-summary{grid-template-columns:36px auto}.nk-library-summary p{grid-column:1/-1;border-left:0;border-top:1px solid var(--nk114-line);padding:8px 0 0}.nk-global-subject span{display:none}.nk-modal-v114 .modal{padding:18px 15px!important}.nk-scope-choice{grid-template-columns:1fr}.nk-multi-subject-grid{grid-template-columns:1fr}.nk-multi-subject-card{min-height:58px}}
@media(prefers-reduced-motion:reduce){.nk-app-v114 *{scroll-behavior:auto!important;transition:none!important}}
</style>'''


def replace_function(source: str, name: str, replacement: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise SystemExit(f"{name} not found")
    brace = source.find("{", start)
    depth = 0
    for index in range(brace, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[index + 1 :]
    raise SystemExit(f"{name} end not found")


def transform(source: str) -> str:
    source = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\s*', '', source, flags=re.S)
    replacements = [
        ("header", HEADER),
        ("bottomNav", BOTTOM_NAV),
        ("dashboard", FOUNDATION_AND_DASHBOARD),
        ("testRow", TEST_ROW),
        ("topics", TOPICS),
        ("analytics", ANALYTICS),
        ("testsPage", TESTS),
        ("morePage", MORE),
        ("libraryPage", LIBRARY),
        ("chapterPage", CHAPTER),
        ("examBuilderMarkup", EXAM_BUILDER),
        ("openSessionBuilder", SESSION_BUILDER),
        ("openTestBuilder", OPEN_TEST_BUILDER),
        ("resultPage", RESULT),
    ]
    for name, replacement in replacements:
        source = replace_function(source, name, replacement)
    source = source.replace(
        "BY_ID=Object.fromEntries(QUESTIONS.map(q=>[String(q.id),q]));",
        "BY_ID=Object.fromEntries(SUBJECTS.flatMap(record=>(Array.isArray(record.questions)?record.questions:[]).map(q=>[String(q.id),{...q,subject:q.subject||record.subject}])));",
        1,
    )
    anchor = "  function richText(text) {"
    if anchor not in source:
        raise SystemExit("richText insertion point not found")
    source = source.replace(anchor, MULTI_SUBJECT_WORKFLOWS + anchor, 1)
    export_anchor = "window.QB={getState:()=>state,"
    export_additions = "window.QB={getState:()=>state,startAllSubjectPractice,openMultiSubjectTestBuilder,nkSetMultiExamScope,nkUpdateMultiExamPool,nkSelectAllMultiTopics,nkConfirmMultiSubjectExam,"
    if export_anchor not in source:
        raise SystemExit("window.QB export point not found")
    source = source.replace(export_anchor, export_additions, 1)
    if "nk-session-experience-v114" not in source:
        raise SystemExit("Protected V11.3.1 session experience missing")
    if "</head>" not in source:
        raise SystemExit("</head> not found")
    return source.replace("</head>", CSS + "\n</head>", 1)


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    HTML.write_text(transform(source), encoding="utf-8")
    print("Applied V11.4 whole-app visual system across Home, Topics, Chapters, Tests, Results, Insights, Revision, and More.")


if __name__ == "__main__":
    main()
