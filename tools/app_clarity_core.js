  /* NK_APP_CLARITY_V1_START */
  // Presentation only: retain queue selection, scheduling, persistence and actions.
  function nkCompactScreenMarkup(markup){
    const redundant=[
      'Return to this topic and keep your momentum.',
      'Your progress, bookmarks, review schedules, and test history stay on this device. Original source PDFs remain bundled with the app.',
      'Pick up exactly where you left off.',
      'Pick a subject below and make today’s study session yours.',
      'Choose the question banks you want to study.',
      'Search or scroll, then tap the topics you want to test.',
      'Set the number of questions. Your time limit updates with it.',
      'Search or scroll, then tap the topics you want in this module.',
      'Build a focused set that stays stable while you work through it.',
      'Pick up missed, saved, unseen, or due questions from every subject and bank.',
      'Choose one area for all four revision queues.',
      'Choose a question source, then work under exam conditions. Answers and explanations appear after submission.',
      'Set the question count inside the test builder.',
      'Choose a subject, then choose PrepLadder or Marrow.',
      'Choose a subject to open its complete topic journey.',
      'Each subject opens its question-bank chooser before Topics.',
      'Subjects open the full Topics page. No popup topic picker is used.',
      'Search every subject and bank, then practice exactly what you found.',
      'Recall cues saved while reviewing questions.',
      'Saved questions and app controls.',
      'Small steps every day lead to big results.',
      'Build lasting recall at a pace that works for you.',
      'Balance confidence and workload','Keep review work bounded','Keep knowledge within reach',
      'Choose banks, topics, PYQs, mistakes, or unseen questions.',
      'Scheduled reviews for this focus over the next seven days.',
      'Every answered question is scheduled here. Unanswered questions enter only after you submit their session; pausing keeps untouched questions out.'
    ];
    for(const copy of redundant)markup=markup.split('<p>'+copy+'</p>').join('');
    markup=markup.replace(/<p class="nk-v3-page-note">(?:Each subject opens its question-bank chooser before Topics\.|Subjects open the full Topics page\. No popup topic picker is used\.)<\/p>/g,'');
    markup=markup.replace(/<div class="nk-kicker">(?:REVISION|EXAM PRACTICE|STUDY LIBRARY|SPACED REPETITION|INTENTIONAL STUDY|SAVED QUESTIONS|APP &amp; SOURCE|APP & SOURCE|QUESTION BANK|PERSONAL REVISION|MAKE IT YOURS|FROM YOUR HISTORY|HISTORY|IN THIS PERIOD|PERFORMANCE|RECENT|CROSS-DEVICE|CROSS-DEVICE SYNC)<\/div>/g,'');
    markup=markup.replace(/<small>(?:STUDY LIBRARY|FROM YOUR HISTORY|HISTORY|PERFORMANCE|RECENT|CROSS-DEVICE|CROSS-DEVICE SYNC)<\/small>/g,'');
    markup=markup.replace(/<small>Questions you (?:have answered incorrectly|saved while studying|have not attempted yet)\.<\/small>|<small>Questions scheduled by spaced repetition\.<\/small>/g,'');
    markup=markup.replace(/<p class="nk-revision-detail">(?:20 questions per session · sampled from this focus|(?:20 questions per session · )?FSRS priority order and daily limit apply\.)<\/p>/g,'');
    markup=markup.replace(/<small>(?:Scheduled for now|You’re up to date|Ready for another pass|No mistakes to revisit)<\/small>/g,'');
    markup=markup.replace(/<section class="nk-home-quote">[\s\S]*?<\/section>/g,'');
    markup=markup.replace('<small>Your Personal Study App</small>','');
    markup=markup.replace('<h1>Your review rhythm</h1>','<h1>Review settings</h1>');
    markup=markup.replace(/<div class="nk-kicker">(?:[^<]+ · Personal QBank|TIMED CBT · STEP [^<]+|CUSTOM STUDY · STEP [^<]+)<\/div>/g,'');
    markup=markup.replace('<strong>Build your first focused module</strong>','<strong>No study sets yet</strong>');
    markup=markup.replace(/<p class="nk-fsrs-settings-note">([\s\S]*?)<\/p>/g,'<details class="nk-clarity-help"><summary>Review scheduling</summary><p>$1</p></details>');
    markup=markup.replace(/<header><span>0[123]<\/span><div><h2>(?:Memory goal|Daily pace|Long-term recall)<\/h2><\/div><\/header>/g,'');
    markup=markup.replace('Practice 1 mistakes','Practice 1 mistake').replace('Practice 1 bookmarks','Practice 1 bookmark');
    markup=markup.replace('<strong>Offline and source-faithful</strong>','<strong>Source PDFs</strong>');
    markup=markup.replace('<small>Search every subject and bank</small>','');
    markup=markup.replace('<small>Your memory goal, daily review cap and review intervals</small>','');
    return markup;
  }
  const nkClarityDashboard=dashboard;dashboard=function(){return nkCompactScreenMarkup(nkClarityDashboard.apply(this,arguments));};
  const nkClarityRevision=nkRevisionDeskPage;nkRevisionDeskPage=function(){return nkCompactScreenMarkup(nkClarityRevision.apply(this,arguments));};
  const nkClarityTests=testsPage;testsPage=function(){return nkCompactScreenMarkup(nkClarityTests.apply(this,arguments));};
  const nkClarityMore=morePage;morePage=function(){return nkCompactScreenMarkup(nkClarityMore.apply(this,arguments));};
  const nkClarityFsrs=nkFsrsReviewPage;nkFsrsReviewPage=function(){return nkCompactScreenMarkup(nkClarityFsrs.apply(this,arguments));};
  const nkClaritySettings=nkFsrsSettingsMarkup;nkFsrsSettingsMarkup=function(){return nkCompactScreenMarkup(nkClaritySettings.apply(this,arguments));};
  const nkClarityLibrary=nkStudyLibraryPage;nkStudyLibraryPage=function(){return nkCompactScreenMarkup(nkClarityLibrary.apply(this,arguments));};
  const nkClaritySearch=nkQuestionSearchPage;nkQuestionSearchPage=function(){return nkCompactScreenMarkup(nkClaritySearch.apply(this,arguments));};
  const nkClarityNotes=nkNotesPage;nkNotesPage=function(){return nkCompactScreenMarkup(nkClarityNotes.apply(this,arguments));};
  const nkClarityCbtBuilder=nkCbtBuilderPage;nkCbtBuilderPage=function(){return nkCompactScreenMarkup(nkClarityCbtBuilder.apply(this,arguments));};
  const nkClarityModuleBuilder=studyModuleBuilderPage;studyModuleBuilderPage=function(){return nkCompactScreenMarkup(nkClarityModuleBuilder.apply(this,arguments));};
  // Scope updates replace cards independently of the page renderer.
  const nkClarityRevisionCards=nkRevisionCards;nkRevisionCards=function(){return nkCompactScreenMarkup(nkClarityRevisionCards.apply(this,arguments));};
  /* NK_APP_CLARITY_V1_END */
