#!/usr/bin/env python3
"""Regression contract for the approved Home / Study / Test / FSRS V3 flows."""

from pathlib import Path
import subprocess
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
    script=updated.split('<script>',1)[1].split('</script>',1)[0]
    subprocess.run(['node','--check'],input=script,text=True,check=True)

    required=(
        FLOW_MARKER,STYLE_ID,'nk-home-approved-v1','CONTINUE STUDYING','Continue Practice',
        'body:has(.nk-home-approved-v1) .nk-global-header-v114{display:none!important}',
        'nkHomeFocusSection(focus)','nkStudySetsSection()',
        'FSRS','My Subjects','nkSubjectStatsV3','nkOpenSubjectLibrary',
        'STUDY LIBRARY','study-library','complete topic journey','My Progress','Today','This Week','This Month','This Year',
        'FSRS Review','Choose subject','All Subjects','Every answered question is scheduled here','pausing keeps untouched questions out',
        "['fsrs','FSRS','refresh']",'Timed tests','Choose subjects and topics','Quick test','Wrong questions','Bookmarked questions','Completed tests',
        'openMultiSubjectTestBuilder','Number of questions','[10,20,50,100]',
        "timerMode='global'","timerMode='per-question'",'Topic Test · 60 sec this question','nkExpireTopicQuestion','Time expired','submitExam(true)',
        "state.fsrsReviewEligible", "reason:'skipped'", 'nkReviewEligibility', 'nkReviewDue',
        'function nkFsrsLaunchQueue', 'nkFsrsQueue({subject})', 'queue.cards||[]', 'queue.rolledOver',
        'due reviews roll forward under your daily limit.',
        "if(!answered)state.fsrsReviewEligible[key]", 'nkMarkSkippedFromSession(s)',
        "route.page==='study-library'", "route.page==='fsrs'", "window.QB.nkStartTopicTimedTest('${c.id}')",
        "window.QB.nkOpenSubjectLibrary('${esc(x.subject)}')", '@media(max-width:560px)','@media(prefers-reduced-motion:reduce)'
    )
    missing=[x for x in required if x not in updated]
    if missing:raise SystemExit(f'Home V3 contract missing: {missing}')

    prohibited=(
        'Start focused study','Full Question Bank','Custom Module','Review shortcuts',
        "nkOpenPracticeSubjects","nkOpenPracticeTopics","nkSetTestTimer","One minute per question when enabled.",
        "nk-test-toggle-grid","Timer off","Practice 20 Random Questions",
        "['topics','Topics','book']",
        "s.questionIds.forEach(id=>{if(!s.answers?.[id])state.fsrsReviewEligible",
        "if(!answered&&!submitted)state.fsrsReviewEligible[key]",
        "function nkStartReviewOnly(subject=nkFsrsSubjectFilter){const rows=nkReviewDue(subject)",
        "nkSessionQuestionEncountered"
    )
    survived=[x for x in prohibited if x in updated]
    if survived:raise SystemExit(f'Obsolete Home/Test behavior survived: {survived}')

    if updated.count(f'id="{STYLE_ID}"')!=1:raise SystemExit('Home V3 stylesheet duplicated')
    home=updated.split('function dashboard(){',1)[1].split('function bottomNav(',1)[0]
    tests=updated.split('function testsPage(){',1)[1].split('function examPage()',1)[0]
    if '<section class="nk-home-quick-grid"' in home or 'Strongest Chapters' in home or "Today's Review" in home:raise SystemExit('Home retained duplicate launch surfaces')
    if not home.index('${nkStudySetsSection()}') < home.index('nk-home-subjects') < home.index('nk-home-streak-card'):
        raise SystemExit('Home places study actions below the streak decoration')
    if 'nk-test-mode-tabs' in tests or 'Custom Module' in tests or 'Full Question Bank' in tests:raise SystemExit('Tests retained duplicate setup paths')
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

    print('HOME_V3_CONTRACT_OK: hybrid Home, subject→Topics, answered-plus-submitted-skip FSRS, global Test budget, strict topic timer')


if __name__=='__main__':main()
