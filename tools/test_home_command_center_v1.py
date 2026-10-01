#!/usr/bin/env python3
"""Regression contract for the approved Home / Study / Test / FSRS V3 flows."""

from pathlib import Path
import subprocess
import json
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
        FLOW_MARKER,STYLE_ID,'nk-home-approved-v1',"TODAY'S FOCUS",'Continue Practice','Choose a subject',
        'body:has(.nk-home-approved-v1) .nk-global-header-v114{display:none!important}',
        'nkHomeFocusSection(focus,focusModule)','nkStudySetsSection(focusModule?.id)',
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
    if not home.index('${nkHomeStreakMarkup()}') < home.index('${nkHomeFocusSection(focus,focusModule)}') < home.index('${nkStudySetsSection(focusModule?.id)}') < home.index('nk-home-subjects'):
        raise SystemExit('Home lost its streak, Today focus, study sets, subjects hierarchy')
    if 'nk-test-mode-tabs' in tests or 'Custom Module' in tests or 'Full Question Bank' in tests:raise SystemExit('Tests retained duplicate setup paths')
    if 'Questions Attempted' in home or ' / ${fmtNum(total)}' in home or 'nk-home-progress-track' in home:
        raise SystemExit('Home period metrics still imply full-bank coverage or a target')
    for label in ('Unique questions answered','Answer accuracy','Study Time'):
        if label not in home:raise SystemExit(f'Home period metric missing: {label}')
    for fn in ('dashboard','bottomNav','testsPage','examPage','startExamTicker','submitExam'):
        if updated.count(f'function {fn}(')!=1:raise SystemExit(f'{fn} duplicated or missing')
    if "function untouchedQuestionEngine(){return 'protected';}" not in updated:raise SystemExit('Protected question engine mutated')
    for bad in ('Membership','Premium Member','Rank'):
        if bad in updated:raise SystemExit(f'Personal QBank introduced prohibited UI: {bad}')

    helpers=updated.split('function nkHomeRangeStart(',1)[1].split('function nkSetHomeProgressRange(',1)[0]
    stats_js='function nkHomeRangeStart('+helpers
    behavior=r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const now=Date.now(),state={attempts:{a:[{at:now-1000,correct:true,timeSpent:30000,source:'practice'},
  {at:now-900,correct:false,timeSpent:10000,source:'practice'}],
  b:[{at:now-800,correct:false,timeSpent:20000,source:'exam'}],
  c:[{at:now-700,correct:true,timeSpent:5000,source:'practice',isUndo:true}]},
  tests:[{kind:'exam',createdAt:now-100,totalTimeMs:30000}]};
const context={state,Date,Math,Number,Object,Set};vm.createContext(context);vm.runInContext(SOURCE,context);
let stats=vm.runInContext('nkHomeProgressStats("today")',context);
assert.equal(stats.attempted,2);assert.equal(Math.round(stats.accuracy),33);
assert.equal(stats.studyMs,70000,'Practice attempt time plus one completed test, without exam double count');
state.attempts={};state.tests=[];stats=vm.runInContext('nkHomeProgressStats("today")',context);
assert.equal(stats.attempted,0);assert.equal(stats.accuracy,null);assert.equal(stats.studyMs,0);
console.log('HOME_PERIOD_METRICS_OK unique=true denominator=answered time=true empty=true');
'''.replace('SOURCE',json.dumps(stats_js),1)
    subprocess.run(['node','-e',behavior],check=True)


    streak_helpers=updated.split('/* NK_HOME_STREAK_MILESTONES_V1 */',1)[1].split('function nkHomeRangeStart(',1)[0]
    streak_behavior=r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const today=new Date('2026-10-01T12:00:00Z');
class Clock extends Date{constructor(...args){super(...(args.length?args:[today.getTime()]));}static now(){return today.getTime();}}
const dayKey=d=>new Date(d).toISOString().slice(0,10),days=new Set(['2026-09-28','2026-09-29','2026-10-01']);
const context={Date:Clock,currentStreak:()=>1,studyDayKeys:()=>days,dayKey,esc:String,fmtNum:String,navIcon:()=>''};
vm.createContext(context);vm.runInContext(SOURCE,context);
for(const [count,level] of [[0,'rest'],[1,'spark'],[2,'spark'],[3,'warm'],[6,'warm'],[7,'fire'],[13,'fire'],[14,'blaze'],[29,'blaze'],[30,'radiant'],[100,'radiant']])assert.equal(vm.runInContext(`nkHomeStreakPresentation(${count}).level`,context),level);
let markup=vm.runInContext('nkHomeStreakMarkup()',context);
assert.equal((markup.match(/is-linked/g)||[]).length,1,'only consecutive studied days connect; a missed day breaks the line');
assert(markup.includes('data-streak-level="spark"'));
assert(markup.includes('not studied')&&markup.includes('upcoming')&&markup.includes('today'));
assert.equal((markup.match(/is-done/g)||[]).length,3);
assert.equal((markup.match(/is-today/g)||[]).length,1);
console.log('HOME_STREAK_MILESTONES_OK thresholds=true connections=true gaps=true accessible=true');
'''.replace('SOURCE',json.dumps(streak_helpers),1)
    subprocess.run(['node','-e',streak_behavior],check=True)
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
