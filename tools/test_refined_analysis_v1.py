#!/usr/bin/env python3
"""Verify exact-set mocks, truthful result groups, timing and deterministic install."""
from pathlib import Path
import json
import subprocess
from apply_refined_analysis_v1 import transform

ROOT = Path(__file__).resolve().parents[1]
core = (ROOT / 'tools/refined_analysis_core.js').read_text()
fixture = '<html><head></head><script>/* NK_APP_CLARITY_V1_START NK_CBT_RESULT_ANALYSIS_V1_START NK_PRACTICE_CORRECTION_V1_START */\n  window.QB={};</script></html>'
generated = transform(fixture)
assert transform(generated) == generated
subprocess.run(['node', '--check'], input=core, text=True, check=True)
program = r'''
const vm=require('vm'),assert=require('node:assert/strict');
const questions=[{id:'a',correctOption:2},{id:'b',correctOption:1},{id:'c',correctOption:3}];
let launched=null,saved=0,fail=false;
const ctx={state:{tests:[],savedMocks:[]},Date,Math,JSON,Map,Set,Number,String,document:{getElementById:()=>({value:'Renamed mock'})},esc:String,fmtNum:String,fmtPct:n=>Math.round(n)+'%',showToast:()=>{},navigate:()=>{},render:()=>{},nkAllStudyQuestions:()=>questions,nkQuestionPresentationFor:()=>({valid:true}),BY_ID:{},saveState:()=>{saved++;return !fail;},startSession:(ids,mode,title,context)=>{launched={ids,mode,title,context};return true;},nkCbtSameQuestions:(a,b)=>JSON.stringify(a.questionIds)===JSON.stringify(b.questionIds),nkCbtTitle:()=> 'Auto mock',nkCbtPool:()=>questions,nkCbtDraft:{count:2,name:'Named mock'},nkCbtStart:()=>{},nkCbtQuestionsMarkup:()=>'',nkCbtBuilderPage:()=>'',testsPage:()=>'',resultPage:()=>{},navIcon:()=>'',nkCbtResultAnalysis:()=>({rows:[{title:'A topic',subject:'Anatomy',bank:'Marrow',total:2,correct:1,incorrect:1,unattempted:0},{title:'Other topic',subject:'Anatomy',bank:'PrepLadder',total:3,correct:0,incorrect:0,unattempted:3},{title:'Phys topic',subject:'Physiology',bank:'Marrow',total:1,correct:1,incorrect:0,unattempted:0}],missedIds:['b'],unavailable:0})};
vm.createContext(ctx);vm.runInContext(CORE,ctx);const run=s=>vm.runInContext(s,ctx);
const grouped=run("nkAnalysisRows({},'subject')");assert.equal(grouped.rows.length,2);assert.equal(grouped.rows[0].total,5);assert.equal(grouped.rows[0].unattempted,3);assert.equal(grouped.rows[0].correct,1);
ctx.t={questionIds:['a','b','c','d','e','f','g'],questionTimes:{a:0,b:29999,c:30000,d:60000,e:120000,f:180001}};
let time=run('nkAnalysisTimeData(t)');assert.deepEqual(Array.from(time.counts),[2,1,1,1,1]);assert.equal(time.missing,1);assert.equal(time.recorded,6);
run("nkAnalysisTimeMode='cumulative'");assert.deepEqual(Array.from(run('nkAnalysisTimeData(t)').counts),[2,3,4,5,6]);
assert.equal(run('nkAnalysisDuration(null)'), '—');assert.equal(run('nkAnalysisDuration(0)'), '0m 0s');
ctx.row={title:'Zero',subject:'Anatomy',bank:'Marrow',total:2,correct:0,incorrect:2,unattempted:0};assert.match(run('nkAnalysisRow(row)'),/is-incorrect.*width:100%/);
ctx.row.incorrect=0;ctx.row.unattempted=2;assert.match(run('nkAnalysisRow(row)'),/is-omitted.*width:100%/);
ctx.row={title:'Mixed',subject:'Anatomy',bank:'Marrow',total:2,correct:1,incorrect:0,unattempted:1};
const mixed=run('nkAnalysisRow(row)');assert.match(mixed,/is-correct.*width:50%/);assert.match(mixed,/is-omitted.*width:50%/);assert.doesNotMatch(mixed,/is-muted/);
assert.match(mixed,/>1<\/b> Correct/);assert.match(mixed,/>1<\/b> Unattempted/);
ctx.t={questionIds:['a','b','c','d','e','e'],questionTimes:{a:1000,b:3000,c:5000,d:15000}};
const short=run('nkAnalysisTimeData(t)');assert.deepEqual(Array.from(short.counts),[4,4,4,4,4]);assert.equal(short.missing,1);
assert.match(run('nkAnalysisTimeChart(t)'),/All 4 recorded questions took under 30 seconds/);
assert.match(run('nkAnalysisTimeChart(t)'),/Timing saved for 4 of 5 questions/);
ctx.t={questionIds:['x','y','z'],questionTimes:{x:NaN,y:-1,z:'1000'}};assert.equal(run('nkAnalysisTimeData(t)').recorded,0);
const mock=run("nkMockStore('Mock <01>', ['a','b'])");ctx.mockId=mock.id;
run('nkMockStart(mockId)');assert.deepEqual(Array.from(launched.ids),['a','b']);assert.equal(launched.mode,'exam');assert.equal(launched.title,'Mock <01>');
ctx.state.tests.push({id:'first',title:'Initial',questionIds:['a','b'],createdAt:1});run('nkMockStart(mockId)');assert.equal(launched.context,'cbt-retake:first');
ctx.state.savedMocks[0].questionIds.push('missing');launched=null;assert.equal(run('nkMockStart(mockId)'),false);assert.equal(launched,null,'unavailable exact sets must never be shortened');
fail=true;assert.equal(run("nkMockStore('unsaved',['a'])"),null);assert.equal(ctx.state.savedMocks.length,1);
fail=false;run('nkMockRemove(mockId)');assert.equal(ctx.state.savedMocks.length,0);
ctx.state.tests=[{id:'named',title:'Old',correct:2,total:3}];run("nkAnalysisRename('named')");assert.equal(ctx.state.tests[0].title,'Renamed mock');assert.equal(ctx.state.tests[0].correct,2);
console.log('REFINED_ANALYSIS_BEHAVIOR_OK exact_sets=true missing_questions=true save_failure=true timing_boundaries=true subject_totals=true truthful_zero=true');
'''.replace('CORE', json.dumps(core))
subprocess.run(['node'], input=program, text=True, check=True)
print('REFINED_ANALYSIS_INSTALL_OK idempotent=true')
