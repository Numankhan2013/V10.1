#!/usr/bin/env python3
"""Check update identity, quiet idle pages, dismissal and explicit reloads."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
core = (ROOT / 'tools/pwa_update_core.js').read_text()
program = r'''
const vm=require('node:vm'),assert=require('node:assert/strict');
async function scenario(pageVersion,workerVersion,mode=null){
  const events={},swEvents={},registrationEvents={},workerEvents={},storage=new Map(),timers=new Map();
  let banner=null,reloads=0,appends=0,timerId=0;
  const worker=workerVersion===undefined?null:{state:'installed',addEventListener:(n,f)=>workerEvents[n]=f,postMessage:(data,ports)=>{
    if(data==='SKIP_WAITING'){swEvents.controllerchange();swEvents.controllerchange();}
    else {assert.equal(data.type,'NK_QBANK_VERSION');ports[0].postMessage({version:workerVersion});}
  }};
  class Channel{constructor(){this.port1={close:()=>{}};this.port2={postMessage:data=>queueMicrotask(()=>this.port1.onmessage({data}))};}}
  const registration={waiting:worker,installing:worker,addEventListener:(n,f)=>registrationEvents[n]=f};
  const ctx={window:{addEventListener:(n,f)=>events[n]=f,QB:{getState:()=>({activeSession:mode?{mode}:null})}},
    navigator:{serviceWorker:{controller:{},register:async()=>registration,addEventListener:(n,f)=>swEvents[n]=f}},
    document:{querySelector:q=>q.startsWith('meta')?{content:pageVersion}:banner,createElement:()=>{
      const buttons={};return {buttons,setAttribute:()=>{},querySelector:q=>buttons[q]??={},remove:()=>banner=null};
    },body:{appendChild:b=>{banner=b;appends++;}}},location:{hostname:'example.test',reload:()=>reloads++},
    sessionStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},MessageChannel:Channel,
    setTimeout:fn=>{timers.set(++timerId,fn);return timerId;},clearTimeout:id=>timers.delete(id),console};
  vm.runInNewContext(CORE,ctx);await events.load();await new Promise(resolve=>setImmediate(resolve));
  return {events,registrationEvents,workerEvents,registration,ctx,worker,storage,timers,banner:()=>banner,reloads:()=>reloads,appends:()=>appends};
}
(async()=>{
  let s=await scenario('current',undefined);assert.equal(s.banner(),null);assert.equal(s.timers.size,0,'idle pages have no update timer');
  s=await scenario('current','current');assert.equal(s.banner(),null,'waiting build already on screen must not prompt');
  s=await scenario('current',null);assert.equal(s.banner(),null,'unknown worker version is not a verified update');
  s=await scenario('old','new');assert(s.banner(),'a different waiting build offers an update');
  s.ctx.navigator.serviceWorker.controller={};s.worker.postMessage('SKIP_WAITING');assert.equal(s.reloads(),0,'unrequested activation must not reload');
  s.banner().buttons['.nk-pwa-apply'].onclick();assert.equal(s.reloads(),1,'explicit update reloads once');
  s=await scenario('old','new');s.banner().buttons['.nk-pwa-later'].onclick();assert.equal(s.banner(),null);
  s.registrationEvents.updatefound();s.workerEvents.statechange();await new Promise(resolve=>setImmediate(resolve));
  assert.equal(s.appends(),1,'dismissed update must not reappear while studying');
  s=await scenario('old','new','exam');assert.equal(s.banner(),null,'active tests must not be interrupted');
  s.ctx.window.QB.getState=()=>({activeSession:null});s.events.hashchange();await new Promise(resolve=>setImmediate(resolve));assert(s.banner(),'offer update after leaving the test');
  const swEvents={};let skipped=0,replied;
  vm.runInNewContext(WORKER,{self:{addEventListener:(n,f)=>swEvents[n]=f,skipWaiting:()=>skipped++}});
  swEvents.message({data:{type:'NK_QBANK_VERSION'},ports:[{postMessage:data=>replied=data}]});assert.equal(replied.version,'dev');assert.equal(skipped,0);
  swEvents.message({data:'SKIP_WAITING'});assert.equal(skipped,1);
  console.log('PWA_UPDATE_V2_OK idle_quiet=true matching_build_quiet=true real_update=true dismissal=true study_deferral=true explicit_reload=true');
})().catch(error=>{console.error(error);process.exitCode=1});
'''.replace('CORE', json.dumps(core)).replace('WORKER', json.dumps((ROOT / 'app/src/main/assets/sw.js').read_text()))
subprocess.run(['node'], input=program, text=True, check=True)
