#!/usr/bin/env python3
"""Regression contract for the approved Home / Study / Test / FSRS V3 flows."""

from pathlib import Path
from apply_home_command_center_v1 import FLOW_MARKER, STYLE_ID, transform

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'


def main():
    fixture='''<html><head></head><body><script>
function openStudyModuleBuilder(){return 'custom';}
/* NK_CUSTOM_STUDY_MODULES_V1_START */
function endSession(){return 'end';}
function nextQ(){return 'next';}
function prevQ(){return 'prev';}
function goIndex(){return 'go';}
function dashboard(){return shell(`<main><b>${[1].map(x=>`${x}`).join('')}</b></main>`,'dashboard');}
function bottomNav(active){return `<nav>${active}</nav>`;}
function testsPage(){return shell('<div>old tests</div>','tests');}
function examPage(){return '<div>old exam</div>';}
function startExamTicker(){return 'old ticker';}
function submitExam(auto=false){return auto;}
function chapterPage(c){return `<button onclick="window.QB.openSessionBuilder('${c.id}','exam')">Timed</button>`;}
function topics(){return `<button onclick="window.QB.openSubjectTopics('${esc(x.subject)}')">Subject</button>`;}
function render(){let out='';if(route.page==='dashboard')out=dashboard();else if(route.page==='more') out=morePage();return out;}
function untouchedQuestionEngine(){return 'protected';}
window.QB={openStudyModuleBuilder};
</script></body></html>'''
    updated=transform(fixture)
    if transform(updated)!=updated:raise SystemExit('Home V3 transform is not idempotent')

    required=(
        FLOW_MARKER,STYLE_ID,'nk-home-approved-v1','TODAY\'S FOCUS','Continue Practice',
        'Review shortcuts','FSRS','Bookmarks','My Subjects','nkSubjectStatsV3','nkOpenSubjectLibrary',
        'STUDY LIBRARY','study-library','complete topic journey','My Progress','Today','This Week','This Month','This Year',
        'Better questions. A brighter you.','Strongest Chapters','Study Sessions',"Today's Review",
        'FSRS Review','Choose subject','All Subjects','wrong or encountered and skipped','Unseen QBank questions are never introduced here.',
        "['fsrs','FSRS','refresh']",'Question Source','Full Question Bank','Custom Module','Wrong Questions','Bookmarked Questions',
        'openMultiSubjectTestBuilder','openStudyModuleBuilder','Number of Questions','[10,20,50,100]',
        'minutes total. Spend that total time across questions however you need.','Practice has no limiting countdown. Time is still recorded for your analysis.',
        "timerMode='global'","timerMode='per-question'",'Topic Test · 60 sec this question','nkExpireTopicQuestion','Time expired','submitExam(true)',
        "state.fsrsReviewEligible", "reason:'skipped'", 'nkReviewEligibility', 'nkReviewDue',
        'function nkFsrsLaunchQueue', 'nkFsrsQueue({subject})', 'queue.cards||[]', 'queue.rolledOver',
        'due reviews roll forward under your daily limit.',
        'function nkSessionQuestionEncountered(s,id)', 'Number(s.questionTimes?.[key]||0)>0',
        'Number(s.strictQuestionTime?.[key]||0)>0', 'Boolean(s.strictExpired?.[key])',
        'if(nkSessionQuestionEncountered(s,key)&&!answered&&!submitted)', 'nkMarkSkippedFromSession(s)',
        "route.page==='study-library'", "route.page==='fsrs'", "window.QB.nkStartTopicTimedTest('${c.id}')",
        "window.QB.nkOpenSubjectLibrary('${esc(x.subject)}')", '@media(max-width:560px)','@media(prefers-reduced-motion:reduce)'
    )
    missing=[x for x in required if x not in updated]
    if missing:raise SystemExit(f'Home V3 contract missing: {missing}')

    prohibited=(
        "nkOpenPracticeSubjects","nkOpenPracticeTopics","nkSetTestTimer","One minute per question when enabled.",
        "nk-test-toggle-grid","Timer off","Practice 20 Random Questions",
        "['topics','Topics','book']",
        "s.questionIds.forEach(id=>{if(!s.answers?.[id])state.fsrsReviewEligible",
        "function nkStartReviewOnly(subject=nkFsrsSubjectFilter){const rows=nkReviewDue(subject)"
    )
    survived=[x for x in prohibited if x in updated]
    if survived:raise SystemExit(f'Obsolete Home/Test behavior survived: {survived}')

    if updated.count(f'id="{STYLE_ID}"')!=1:raise SystemExit('Home V3 stylesheet duplicated')
    for fn in ('dashboard','bottomNav','testsPage','examPage','startExamTicker','submitExam'):
        if updated.count(f'function {fn}(')!=1:raise SystemExit(f'{fn} duplicated or missing')
    if "function untouchedQuestionEngine(){return 'protected';}" not in updated:raise SystemExit('Protected question engine mutated')
    for bad in ('Membership','Premium Member','Rank'):
        if bad in updated:raise SystemExit(f'Personal QBank introduced prohibited UI: {bad}')

    if HTML.exists():
        html=HTML.read_text(encoding='utf-8')
        if FLOW_MARKER in html:
            absent=[x for x in required if x not in html]
            if absent:raise SystemExit(f'Generated Home V3 integration missing: {absent}')
            for bad in prohibited[-2:]:
                if bad in html:raise SystemExit(f'Generated app retained prohibited FSRS behavior: {bad}')
            print('HOME_V3_INTEGRATION_OK')

    print('HOME_V3_CONTRACT_OK: hybrid Home, subject→Topics, capped FSRS wrong/encountered-skip only, global Test budget, strict topic timer')


if __name__=='__main__':main()
