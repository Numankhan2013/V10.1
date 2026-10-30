#!/usr/bin/env python3
"""Verify Insights subject focus and the FSRS insights page against hand-counted totals."""

from pathlib import Path
import subprocess
from app_page import app_css, app_source

ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / 'app/src/main/modules/memory_insights.js').read_text(encoding='utf-8')


def main() -> None:
    page = app_source()
    assert page.count(CORE.strip()) == 1, 'memory insights core ships verbatim once'
    css = app_css()
    for rule in ('.nk-li-focus {', '.nk-li-weak {', '.nk-mi-forecast {', '.nk-mi-stack {', '.nk-mi-is-relearning'):
        assert rule in css, rule
    for marker in ("else if(route.page==='fsrs-insights') out=nkMemoryInsightsPage();",
                   '${nkFocusSection(model)}', "window.QB.nav('fsrs-insights')"):
        assert marker in page, marker
    qb = page[page.index('  window.QB={'):]
    assert ('nkFocusRevise,nkFocusOpen,nkMemorySetGroup,nkMemorySelectDay,nkMemoryReview,'
            'nkMemoryOpenQuestion,nkMemoryPractiseHardest,') in qb[:qb.index('};')]

    program = r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
// Values come from another vm realm, so compare their JSON.
const eq=(a,b,m)=>assert.equal(JSON.stringify(a),JSON.stringify(b),m);
const DAY=86400000,now=+new Date(2026,9,30,12),ago=d=>now-d*DAY;
const q=(id,subject,bank='Marrow')=>({id,subject,bank,question:'Q '+id});
const qs=[q('a1','Anatomy'),q('a2','Anatomy'),q('p1','Physiology'),q('p2','Physiology'),q('b1','Biochemistry'),q('u1','Immunology','UWorld')];
const events=[];
const add=(qq,n,right,day)=>{for(let i=0;i<n;i++)events.push({q:qq,at:ago(day)+i,correct:i<right});};
add(qs[0],10,8,2);   // Anatomy 80%
add(qs[2],10,4,3);   // Physiology 40% -> weakest
add(qs[4],12,6,35);  // Biochemistry: quiet for 35 days, nothing in the window
add(qs[5],3,3,1);    // UWorld: too few answers to be rated
events.push({q:qs[1],at:now+DAY,correct:false}); // future answers are ignored
const reviews={
  a1:{schemaVersion:2,state:2,stability:30,lapses:0,due:now+3*DAY,lastReview:ago(2)},
  a2:{schemaVersion:2,state:2,stability:5,lapses:2,difficulty:7,due:now-2*DAY,lastReview:ago(9)},
  p1:{schemaVersion:2,state:3,stability:1,lapses:3,difficulty:9,due:now-DAY,lastReview:ago(3)},
  p2:{schemaVersion:2,state:1,stability:.5,lapses:0,due:now+40*DAY,lastReview:ago(1)},
  b1:{schemaVersion:2,state:2,stability:22,lapses:1,due:now+10*DAY,lastReview:ago(20)}
};
const attempts={
  a1:[{correct:false,at:ago(10)},{correct:true,at:ago(6)},{correct:true,at:ago(2)}],
  a2:[{correct:false,at:ago(12)},{correct:false,at:ago(9)}],
  p1:[{correct:true,at:ago(40)},{correct:false,at:ago(3)}],
  p2:[{correct:true,at:ago(1)},{correct:true,at:ago(1)+3600000}],
  b1:[{correct:false,at:ago(20)}]
};
const ctx={state:{reviews},Date,Math,JSON,Map,Set,Number,String,Object,Array,
  nkLearningMatches:()=>true,nkLearningSubjectGroup:x=>x.bank==='UWorld'?'UWorld':x.subject,
  nkLearningDay:n=>{const d=new Date(n);d.setHours(0,0,0,0);return d;},fmtNum:String,
  nkAllStudyQuestions:()=>qs,nkFsrsEligibility:x=>x.id!=='u1',nkFsrsPreferences:()=>({desiredRetention:.9}),nkFsrsEngine:()=>({}),
  nkFsrsIsDue:(r,t)=>!!r&&Number(r.due)<=t,nkFsrsRetrievability:r=>Number(r.stability)>=20?.97:Number(r.stability)>=5?.85:.6,
  nkFsrsActiveAttempts:id=>attempts[id]||[]};
vm.createContext(ctx);vm.runInContext(CORE,ctx);const run=s=>vm.runInContext(s,ctx);ctx.now=now;ctx.events=events;

const f=run('nkFocusData({data:{events}},now)');
assert.equal(f.studied,4);
eq(f.rated.map(r=>r.subject),['Physiology','Anatomy'],'only subjects with 10+ answers in 30 days are compared');
assert.equal(f.weakest.subject,'Physiology');assert.equal(f.weakest.accuracy,40);
assert.equal(f.average,15/23*100,'average covers every answer in the window');
eq(f.quiet.map(r=>[r.subject,r.idle]),[['Biochemistry',35]]);
const lone=run('nkFocusData({data:{events:events.filter(e=>e.q.subject!=="Physiology")}},now)');
assert.equal(lone.weakest,null,'a single rated subject is never called weakest');

const d=run('nkMemoryData("",now)');
assert.equal(d.cards,5,'UWorld question without FSRS eligibility is not a card');
eq({...d.stages},{mature:2,young:1,learning:1,relearning:1,new:0});
assert.equal(d.due,2);assert.equal(d.forecast[0],2,'today includes overdue');assert.equal(d.forecast[3],1);assert.equal(d.forecast[10],1);
assert.equal(d.forecast.reduce((a,b)=>a+b,0),4,'cards due beyond 30 days stay out');
eq(d.buckets,[1,0,1,0,2]);assert.equal(d.recallN,4);
// Recall tests: a1 day 6 (ok), a1 day 2 (ok), a2 day 9 (miss), p1 day 3 (miss); p2's second answer came within the hour.
assert.equal(d.tests,4);assert.equal(d.retention,50);assert.equal(d.target,90);
eq(d.subjects.map(s=>[s.subject,s.tests,s.retention]),[["Anatomy",3,2/3*100],['Physiology',1,0]]);
assert.equal(d.comeback.recovered,1);assert.equal(d.comeback.again,1);assert.equal(d.comeback.pending,2);
assert.equal(d.comeback.rate,50);assert.equal(d.comeback.median,4);
eq(d.hardest.map(h=>h.q.id),['p1','a2']);assert.equal(d.hardestTotal,2);
const phys=run('nkMemoryData("Physiology",now)');
assert.equal(phys.cards,2);assert.equal(phys.due,1);eq(phys.hardest.map(h=>h.q.id),['p1']);
assert.equal(run('nkFocusScope("UWorld","Marrow")').bank,'UWorld');
eq({...run('nkFocusScope("Anatomy","UWorld")')},{subject:'Anatomy',bank:'',topic:''});
console.log('MEMORY_INSIGHTS_OK');
'''
    program = program.replace('vm.runInContext(CORE,ctx)', 'vm.runInContext(require("fs").readFileSync(process.argv[1],"utf8"),ctx)')
    subprocess.run(['node', '-e', program, str(ROOT / 'app/src/main/modules/memory_insights.js')], check=True)


if __name__ == '__main__':
    main()
