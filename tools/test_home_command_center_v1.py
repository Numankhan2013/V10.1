#!/usr/bin/env python3
"""Regression contract for the approved Home / Study / Test / FSRS V3 flows."""

from pathlib import Path
import subprocess
import json
import re
from app_page import app_source

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'
FLOW_MARKER='NK_HOME_FLOW_V3'
STYLE_ID='nk-home-command-center-v1'


def main():
    html=app_source()
    script=next(x for x in re.findall(r'<script>(.*?)</script>',html,re.S) if f'{FLOW_MARKER}_START' in x)
    subprocess.run(['node','--check'],input=script,text=True,check=True)

    required=(
        FLOW_MARKER,STYLE_ID,'nk-home-approved-v1',"TODAY'S FOCUS",'Continue Practice','Choose a subject',
        'body:has(.nk-home-approved-v1) .nk-global-header-v114{display:none!important}',
        'nkHomeFocusSection(focus,focusModule)','nkStudySetsSection(focusModule?.id)',
        'FSRS','My Subjects','nkSubjectStatsV3','nkOpenSubjectLibrary',
        'STUDY LIBRARY','study-library','complete topic journey','My Progress','Today','This Week','This Month','This Year',
        'FSRS Review','Choose subject','All Subjects','Every answered question is scheduled here','pausing keeps untouched questions out',
        "['quick-revision','Revision','refresh']",'window.QB.nkOpenRevisionHub()','Timed tests','Choose subjects and topics','Quick test','Wrong questions','Bookmarked questions','Completed tests',
        'openMultiSubjectTestBuilder','Number of questions','[10,20,50,100]',
        "timerMode='global'","timerMode='per-question'",'Topic Test · 60 sec this question','nkExpireTopicQuestion','Time expired','submitExam(true)',
        "state.fsrsReviewEligible", "reason:'skipped'", 'nkReviewEligibility', 'nkReviewDue',
        'function nkFsrsLaunchQueue', 'nkFsrsQueue({subject})', 'queue.cards||[]', 'queue.rolledOver',
        'due reviews roll forward under your daily limit.',
        "if(!answered)state.fsrsReviewEligible[key]", 'nkMarkSkippedFromSession(s)',
        "route.page==='study-library'", "route.page==='fsrs'", "window.QB.nkStartTopicTimedTest('${c.id}')",
        "window.QB.nkOpenSubjectLibrary('${esc(x.subject)}')", '@media(max-width:560px)','@media(prefers-reduced-motion:reduce)'
    )
    missing=[x for x in required if x not in html]
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
    survived=[x for x in prohibited if x in html]
    if survived:raise SystemExit(f'Obsolete Home/Test behavior survived: {survived}')

    if html.count(f'/* ── {STYLE_ID} ── */')!=1:raise SystemExit('Home V3 stylesheet duplicated')
    home=html.split('function dashboard(){',1)[1].split('function testRow(',1)[0]
    tests=html.split('function testsPage(){',1)[1].split('function morePage(',1)[0]
    if '<section class="nk-home-quick-grid"' in home or 'Strongest Chapters' in home or "Today's Review" in home:raise SystemExit('Home retained duplicate launch surfaces')
    if not home.index('${nkHomeStreakMarkup()}') < home.index('${nkHomeFocusSection(focus,focusModule)}') < home.index('${nkStudySetsSection(focusModule?.id)}') < home.index('nk-home-subjects'):
        raise SystemExit('Home lost its streak, Today focus, study sets, subjects hierarchy')
    if 'nk-test-mode-tabs' in tests or 'Custom Module' in tests or 'Full Question Bank' in tests:raise SystemExit('Tests retained duplicate setup paths')
    if 'Questions Attempted' in home or ' / ${fmtNum(total)}' in home or 'nk-home-progress-track' in home:
        raise SystemExit('Home period metrics still imply full-bank coverage or a target')
    for label in ('Unique questions answered','Answer accuracy','Study Time'):
        if label not in home:raise SystemExit(f'Home period metric missing: {label}')
    for fn in ('dashboard','bottomNav','testsPage','examPage','startExamTicker','submitExam'):
        if html.count(f'function {fn}(')!=1:raise SystemExit(f'{fn} duplicated or missing')
    for bad in ('Membership','Premium Member','Rank'):
        if re.search(rf'\b{bad}\b',html):raise SystemExit(f'Personal QBank introduced prohibited UI: {bad}')

    helpers=html.split('function nkHomeRangeStart(',1)[1].split('function nkSetHomeProgressRange(',1)[0]
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


    streak_helpers=html.split('/* NK_HOME_STREAK_MILESTONES_V1 */',1)[1].split('function nkHomeRangeStart(',1)[0]
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
    print('HOME_V3_CONTRACT_OK: hybrid Home, subject→Topics, answered-plus-submitted-skip FSRS, global Test budget, strict topic timer')


if __name__=='__main__':main()
