#!/usr/bin/env python3
"""Verify analytics against independent totals, calendar boundaries and source identity."""
import json
import os
from pathlib import Path
import subprocess
from apply_learning_insights_v1 import transform

ROOT = Path(__file__).resolve().parents[1]
core = (ROOT / 'tools/learning_insights_core.js').read_text()
fsrs = (ROOT / 'tools/fsrs_scheduler_core.js').read_text()
active = fsrs[fsrs.index('  function nkFsrsActiveAttempts('):fsrs.index('  function nkFsrsUnresolvedMistake(')]
fixture = '''<html><head></head><script>
/* NK_QBANK_COVERAGE_V1_START NK_PRACTICE_CORRECTION_V1_START */
function analytics() { return 'old';
  }
function practice(s){const test={kind:'practice', studyModuleId:s.studyModuleId||null,};return test;}
function exam(s,qt){const test={title:s.title,questionIds:[...s.questionIds],answers:{...s.answers},questionTimes:{...qt},correct,incorrect,unattempted,total:1};return test;}
  window.QB={};
</script></html>'''
generated = transform(fixture)
assert transform(generated) == generated
assert generated.count('function analytics(') == 1
assert generated.count('sessionId:s.id') == 2
subprocess.run(['node', '--check'], input=generated.split('<script>')[1].split('</script>')[0], text=True, check=True)
program = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
const at=(y,m,d,h=12)=>+new Date(y,m-1,d,h),now=at(2026,10,1);
const qs=[{id:'a',subject:'Anatomy',bank:'Marrow',chapterId:'1'},{id:'b',subject:'Anatomy',bank:'PrepLadder',chapterId:'1'},{id:'c',subject:'Physiology',bank:'Marrow',chapterId:'1'}];
const state={attempts:{a:[
 {id:'prior',correct:false,selected:2,at:at(2026,9,21),timeSpent:120000},
 {id:'wrong',correct:false,selected:2,at:at(2026,9,28),sessionId:'s1',timeSpent:60000},
 {id:'right',correct:true,selected:1,at:at(2026,9,29),source:'spaced-review',sessionId:'s2',timeSpent:120000},
 {id:'undone',correct:false,selected:2,at:at(2026,9,30),timeSpent:300000},
 {id:'undo',isUndo:true,undoOf:'undone',at:at(2026,10,1)}
],b:[{id:'b1',correct:true,selected:1,at:at(2026,9,30),sessionId:'s1',timeSpent:180000}],c:[{id:'c1',correct:false,selected:2,at:at(2026,10,1,9),source:'exam',sessionId:'e1',timeSpent:30000}]},
fsrsRatingRevisions:{a:[{id:'edit',isRatingRevision:true,ratingOf:'right',rating:4,at:at(2026,10,1)}]},
tests:[{id:'p1',kind:'practice',sessionId:'s1',createdAt:at(2026,9,30),questionIds:['a','b'],answers:{a:2,b:1},questionTimes:{a:120000,b:180000},totalTimeMs:300000},
 {id:'t1',kind:'exam',sessionId:'e1',createdAt:at(2026,10,1,10),questionIds:['c','b'],answers:{c:2},questionTimes:{c:30000,b:30000},totalTimeMs:60000}],
studyModules:[{id:'m1',questionIds:['a'],isCompleted:true,completedAt:at(2026,9,30)}],reviews:{a:{due:now-1000},b:{due:at(2026,10,2)},c:{due:at(2026,10,9)}}};
const ctx={state,Date,Math,JSON,Set,Map,Number,Intl,encodeURIComponent,decodeURIComponent,nkAllStudyQuestions:()=>qs,nkModuleBankRecords:()=>[
 {subject:'Anatomy',bank:'Marrow',topics:[{id:'1',title:'Marrow topic'}]},
 {subject:'Anatomy',bank:'PrepLadder',topics:[{id:'1',title:'Prep topic'}]},
 {subject:'Physiology',bank:'Marrow',topics:[{id:'1',title:'Phys topic'}]}],nkModuleBankName:r=>r.bank,nkModuleTopics:r=>r.topics,nkFsrsEligibility:()=>true,dayKey:n=>{const d=new Date(n);return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;},fmtNum:String,esc:String,navIcon:()=>'',render:()=>{},document:{querySelector:()=>null},nkOpenSubjectChapter:()=>{}};
vm.createContext(ctx);vm.runInContext(ACTIVE+'\n'+CORE,ctx);const run=s=>vm.runInContext(s,ctx);ctx.now=now;
const before=JSON.stringify(state),model=run('nkLearningModel(now)');
assert.equal(model.current.attempts,4);assert.equal(model.current.correct,2);assert.equal(model.current.incorrect,2);assert.equal(model.current.skipped,1);assert.equal(model.current.accuracy,50);
assert.equal(model.current.time,480000,'5 minute Practice + 2 minute separate review + 1 minute CBT, counted once');
assert.equal(model.current.reviews,1);assert.equal(model.current.reviewAccuracy,100);assert.equal(model.current.unique,3);
assert.equal(model.current.missed,2);assert.equal(model.current.corrected,1);assert.equal(model.unresolved,1);assert.equal(model.current.completed,1);
assert.equal(model.previous.attempts,1);assert.equal(model.previous.time,120000);
assert.equal(model.topicRows.length,3,'same topic number in two banks is distinct');
assert.equal(model.forecast.total,3);assert.equal(model.forecast.due,1);assert.equal(model.forecast.counts[0],1);assert.equal(model.forecast.counts[1],1);
assert.equal(model.bins.reduce((n,b)=>n+b.current.attempts,0),4);assert.equal(model.bins.reduce((n,b)=>n+b.current.time,0),480000);
assert.equal(JSON.stringify(state),before,'dashboard reads must never mutate learner state');
// Continuous comparative color: 40/60 differs, and a new high lightens old days.
const shade=(n,max)=>run(`nkLearningHeatStyle(${n},${max})`);
const light=style=>Number(style.match(/--heat-fill:hsl\(258 [\d.]+% ([\d.]+)%\)/)[1]);
assert.notEqual(shade(40,60),shade(60,60));
assert(light(shade(40,120))>light(shade(40,60)));
assert.equal(shade(40,60),shade(80,120),'relative intensity scales with actual workload');
assert.equal(shade(30,30),shade(600,600),'the busiest day always anchors the scale');
assert(!shade(0,0).includes('NaN'));
assert(run('nkLearningYearActivity(nkLearningModel(now),now)').includes('one tile per day'));
assert(!run('nkLearningYearActivity(nkLearningModel(now),now)').includes('30+'));

assert.equal(run("nkLearningDelta(5,0)" ).includes('Infinity'),false);
assert.equal(run("nkLearningDelta(null,0)" ).includes('No comparison'),true);
run("nkLearningSubject='Anatomy';nkLearningBank='Marrow'");
const scoped=run('nkLearningModel(now)');assert.equal(scoped.current.attempts,2);assert.equal(scoped.topicRows.length,1);assert.equal(scoped.current.time,240000,'allocated Practice share + separate review');
run("nkLearningSubject='';nkLearningBank='';nkLearningPeriod='month'");
const month=run('nkLearningModel(now)');assert.equal(month.current.attempts,1);assert.equal(month.current.time,60000);assert.equal(month.range.previous,new Date(2026,8,1).getTime());
// Legacy sessions must also replace (not duplicate) answer time.
delete state.tests[0].sessionId;delete state.tests[1].sessionId;
run("nkLearningPeriod='week'");assert.equal(run('nkLearningModel(now)').current.time,480000);
// A re-miss restores unresolved/recovery state; rating edits never do.
state.attempts.a.push({id:'newmiss',correct:false,selected:2,at:at(2026,10,1,11),timeSpent:10000});
assert.equal(run('nkLearningModel(now)').current.corrected,0);assert.equal(run('nkLearningModel(now)').unresolved,2);
// DST: all seven bins follow local dates, not fixed 24-hour steps.
ctx.dst=at(2026,11,2);run("nkLearningOffset=-1");const dst=run('nkLearningRange(dst)');assert.equal(dst.bins.length,7);dst.bins.forEach((b,i)=>{assert.equal(new Date(b.start).getHours(),0);if(i){const next=new Date(dst.bins[i-1].start);next.setDate(next.getDate()+1);assert.equal(+new Date(b.start),+next);}});
ctx.short=at(2026,3,31);run("nkLearningOffset=0;nkLearningPeriod='month'");const short=run('nkLearningRange(short)');assert.equal(new Date(short.previousCut).getMonth(),1);assert.equal(new Date(short.previousCut).getDate(),28);
ctx.leap=at(2024,2,29);run("nkLearningPeriod='year'");const leap=run('nkLearningRange(leap)');assert.equal(new Date(leap.previousCut).getFullYear(),2023);assert.equal(new Date(leap.previousCut).getDate(),28);
run("nkLearningOffset=-1");assert.equal(run('nkLearningRange(now)').partial,false);
state.attempts={};state.tests=[];state.studyModules=[];run("nkLearningOffset=0");const empty=run('nkLearningModel(now)');assert.equal(empty.current.accuracy,null);assert.equal(empty.current.reviewAccuracy,null);assert.equal(empty.current.time,0);assert(!run('nkLearningContent(nkLearningModel(now))').includes('NaN'));
console.log('LEARNING_INSIGHTS_BEHAVIOR_OK calendar=true DST=true elapsed_comparison=true answer_identity=true undo=true rating_edits=true timing_once=true legacy=true scopes=true topic_identity=true recovery=true modules=true read_only=true');
'''
program = 'const CORE=' + json.dumps(core) + ',ACTIVE=' + json.dumps(active) + ';\n' + program
for tz in ['UTC', 'America/New_York']:
    subprocess.run(['node', '-'], input=program, text=True, env={**os.environ, 'TZ': tz}, check=True)
print('LEARNING_INSIGHTS_INSTALL_OK idempotent=true')
