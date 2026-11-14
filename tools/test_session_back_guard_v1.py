#!/usr/bin/env python3
"""System Back during a session asks to abandon it (session_abandon.js).

Browser / PWA: a guard history entry sits on top while a Practice session or a
timed test is live. Back pops the guard; the page puts it back and opens the
in-app "Abandon this session/test?" dialog (Cancel keeps the session, Abandon
runs the abandon flow, Back again cancels). Leaving the session any other way
(submit, pause, abandon, in-app navigation) pops the guard before that
navigation runs, so the history stack is identical to a run without the guard.
Scheduled mocks (cannot be abandoned) and paused sessions get no guard and keep
the existing exit warning. Android shell: no guard; MainActivity asks
window.QB.nkSessionBack, which opens the native dialog via confirmAction.

Runs in Node: the page's real navigate() and the real abandon module over a
fake history (entries, pushState/replaceState, async back with popstate then
hashchange), each run in a fresh VM context.
"""

from pathlib import Path
import json
import subprocess

from app_page import app_page
from js_extract import extract_function

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/session_abandon.js"
INTERACTION = ROOT / "app/src/main/modules/question_interaction.js"
JAVA = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"

PAGE = app_page()
WORLD = r'''
let state={activeSession:null,tests:[],attempts:{},abandonedSessions:[],bookmarks:{}};
const entries=[{url:'#topics',state:null}];let at=0;const tasks=[];const timers=[];
const listeners={popstate:[],hashchange:[]};
function fire(type){const event={stopped:false,stopImmediatePropagation(){this.stopped=true;}};for(const fn of [...listeners[type]]){fn(event);if(event.stopped)break;}}
const hashOf=href=>{const s=String(href);const i=s.indexOf('#');return i<0?entries[at].url:s.slice(i);};
const location={hostname:OPTS.hostname||'nk-qbank.pages.dev',
  get hash(){return entries[at].url==='#'?'':entries[at].url;},
  set hash(v){const u='#'+String(v).replace(/^#/,'');if(u===entries[at].url)return;entries.splice(at+1);entries.push({url:u,state:null});at++;tasks.push(()=>fire('hashchange'));},
  get href(){return 'https://nk-qbank.pages.dev/'+entries[at].url;}};
const history={get state(){return entries[at].state;},get length(){return entries.length;},
  pushState(st,_,href){entries.splice(at+1);entries.push({url:hashOf(href),state:st});at++;},
  replaceState(st,_,href){entries[at]={url:hashOf(href),state:st};},
  back(){tasks.push(()=>{if(at===0)return;const prev=entries[at].url;at--;fire('popstate');if(entries[at].url!==prev)fire('hashchange');});}};
const dom={};
const document={body:{insertAdjacentHTML(_,html){if(html.includes('id="nk-abandon-confirm"'))dom['nk-abandon-confirm']={html,remove(){delete dom['nk-abandon-confirm'];},addEventListener(){},querySelector(){return {focus(){}};},querySelectorAll(){return [];}};}},
  getElementById:id=>dom[id]||null,querySelector:()=>null,querySelectorAll:()=>[],activeElement:null,contains:()=>false};
const window={history,location,addEventListener(type,fn){(listeners[type]||(listeners[type]=[])).push(fn);},QBankShell:OPTS.shell||undefined};
const setTimeout=(fn,ms)=>{timers.push(fn);return timers.length;},clearTimeout=()=>{};
function requestAnimationFrame(){} function resetScrollPosition(){}
let nkForwardNav=false,nkSessionEntry=null,nkResultBackable=null;
let route={page:'topics',id:null};
const toasts=[],prompts=[];let renders=0,overlayOpen=false,overlaysClosed=0;
%(parse)s
let render=function(){renders++;};
// The page's own hashchange: route, then render.
window.addEventListener('hashchange',()=>{route=parseHash();render();});
// Stand-in for question_interaction.js's popstate boundary (registered before the
// abandon module): it asks "Do you want to exit?" when Back really left the route.
window.addEventListener('popstate',()=>{
  if(location.hostname==='qbank.local'||window.QBankShell)return;
  const s=state.activeSession;if(!s||!['practice','exam'].includes(s.mode)||route.page!==s.mode)return;
  if(parseHash().page===route.page)return;
  prompts.push(s.mode);history.pushState(null,'','#'+route.page);   // Stay
},true);
%(navigate)s
const nkNavigateBase=navigate;
let nkFsrsActiveAttempts=()=>[];
function openSessionReview(){} function openQuestionNavigator(){}
function closeQuestionNavigator(){} function closeSessionReview(){}
function saveState(){return true;} function showToast(m){toasts.push(m);} const esc=s=>String(s);
function nkSessionBackOverlay(){return overlayOpen?()=>{overlayOpen=false;overlaysClosed++;}:null;}
const BY_ID={};const fmtNum=String,fmtDate=()=>'',navIcon=()=>'',testRow=()=>'';
%(module)s
function flush(){let n=0;while(tasks.length){if(++n>50)throw new Error('history loop');tasks.shift()();}}
function urls(){return entries.slice(0,at+1).map(e=>e.url+(e.state&&e.state.nkSessionGuard?'{guard}':''));}
function start(mode,extra={}){state.activeSession={id:'s1',mode,title:'Upper limb',questionIds:['a','b','c'],sessionQuestionIds:['a','b','c'],answers:{a:1},index:0,startedAt:1,...extra};navigate(mode);flush();}
function back(){history.back();flush();}
function answer(confirmed){return nkAbandonAnswer(nkAbPending.requestId,confirmed);}
globalThis.api={get state(){return state;},set state(v){state=v;},entries,get at(){return at;},urls,flush,start,back,answer,navigate,dom,toasts,prompts,
  render:()=>render(),nkSessionBack,setOverlay(v){overlayOpen=v;},get overlaysClosed(){return overlaysClosed;},get pending(){return nkAbPending;},
  get route(){return route;},timers,dropTasks(){tasks.length=0;}};
'''

TESTS = r'''
const vm=require('vm');const assert=require('assert');
const WORLD=%(world)s;
function world(opts={}){const ctx=vm.createContext({OPTS:opts,console});vm.runInContext(WORLD,ctx);return ctx.api;}
const results=[];function check(name,fn){fn();results.push(name);}
const same=(a,b,msg)=>assert.deepStrictEqual(JSON.parse(JSON.stringify(a)),JSON.parse(JSON.stringify(b)),msg);
// The same flow without the guard (Android shell host): the history every guarded run must end with.
function compare(flow){const g=world(),plain=world({hostname:'qbank.local'});flow(g);flow(plain);
  same(g.urls(),plain.urls(),'history after the session matches a run without the guard');
  same(g.urls().filter(u=>u.includes('{guard}')),[],'no guard entry is left behind');return g;}

check('a live Practice session gets one guard entry on top of its own',()=>{
  const w=world();w.start('practice');same(w.urls(),['#topics','#practice','#practice{guard}']);
  w.render();w.render();same(w.urls(),['#topics','#practice','#practice{guard}'],'renders do not stack guards');
});
check('Back opens "Abandon this session?" and keeps the learner on the question',()=>{
  const w=world();w.start('practice');w.back();
  assert(w.dom['nk-abandon-confirm'],'the abandon dialog opens');
  assert(w.dom['nk-abandon-confirm'].html.includes('Abandon this session?'));
  assert(w.dom['nk-abandon-confirm'].html.includes('>Cancel<')&&w.dom['nk-abandon-confirm'].html.includes('>Abandon<'));
  same(w.urls(),['#topics','#practice','#practice{guard}'],'the guard is back');assert.strictEqual(w.route.page,'practice');
  same(w.prompts,[],'no browser confirm()');
});
check('Cancel keeps the session and the guard',()=>{
  const w=world();w.start('practice');w.back();w.answer(false);
  assert(!w.dom['nk-abandon-confirm']);assert.strictEqual(w.state.activeSession.id,'s1');
  same(w.urls(),['#topics','#practice','#practice{guard}']);
  w.back();assert(w.dom['nk-abandon-confirm'],'Back asks again after Cancel');
});
check('Back while the dialog is open cancels it',()=>{
  const w=world();w.start('practice');w.back();w.back();
  assert(!w.dom['nk-abandon-confirm']);assert.strictEqual(w.state.activeSession.id,'s1');
  same(w.urls(),['#topics','#practice','#practice{guard}']);
});
check('Abandon from Back: session gone, history entry, toast, then Back leaves normally',()=>{
  const g=world();g.start('practice');g.back();assert.strictEqual(g.answer(true),true);g.flush();
  assert.strictEqual(g.state.activeSession,null);assert.strictEqual(g.state.abandonedSessions.length,1);
  assert(g.toasts.some(t=>/Session abandoned/.test(t)));
  // Unguarded reference: the same abandon from the session sheet.
  const p=world({hostname:'qbank.local'});p.start('practice');p.nkSessionBack();p.answer(true);p.flush();
  same(g.urls(),p.urls(),'abandon leaves the history the unguarded app leaves');same(g.urls(),['#topics','#practice','#topics'],'back where the session started');
  g.back();p.back();same(g.urls(),p.urls(),'the next Back is not doubled');
});
check('timed test: Back asks "Abandon this test?"; Abandon goes to Tests',()=>{
  const w=world();w.start('exam');same(w.urls(),['#topics','#exam','#exam{guard}']);w.back();
  assert(w.dom['nk-abandon-confirm'].html.includes('Abandon this test?'));
  w.answer(true);w.flush();assert.strictEqual(w.state.activeSession,null);same(w.urls(),['#topics','#exam','#tests']);
});
check('Submit to Results: the guard is popped first, Results sits in the session entry, Back returns once',()=>{
  const flow=w=>{w.start('practice');w.state.tests.push({id:'practice_s1',originRoute:'topics'});w.state.activeSession=null;w.navigate('result','practice_s1');w.flush();};
  const g=compare(flow);same(g.urls(),['#topics','#result/practice_s1']);
  g.back();same(g.urls(),['#topics']);
});
check('Pause (or any in-app navigation away) leaves no guard and no extra Back press',()=>{
  const g=compare(w=>{w.start('practice');w.state.activeSession.lifecycle='paused';w.navigate('dashboard');w.flush();});
  same(g.urls(),['#topics','#practice','#dashboard']);
  compare(w=>{w.start('exam');w.navigate('dashboard');w.flush();});
});
check('two navigations while the guard is popping pop it once; the last one wins',()=>{
  const w=world();w.start('practice');w.navigate('dashboard');w.navigate('tests');w.flush();
  same(w.urls(),['#topics','#practice','#tests']);
});
check('a navigation whose popstate never arrives still runs',()=>{
  const w=world();w.start('practice');w.navigate('dashboard');
  w.dropTasks();w.timers.forEach(fn=>fn());w.flush();assert.strictEqual(w.route.page,'dashboard');
});
check('Back closes an open sheet or viewer first',()=>{
  const w=world();w.start('practice');w.setOverlay(true);w.back();
  assert.strictEqual(w.overlaysClosed,1);assert(!w.dom['nk-abandon-confirm']);same(w.urls(),['#topics','#practice','#practice{guard}']);
  w.back();assert(w.dom['nk-abandon-confirm']);
});
check('scheduled mock: no guard, Back keeps the existing exit warning',()=>{
  const w=world();w.start('exam',{scheduledMockId:'m1'});same(w.urls(),['#topics','#exam']);
  w.back();same(w.prompts,['exam']);assert(!w.dom['nk-abandon-confirm']);assert.strictEqual(w.state.activeSession.id,'s1');
  assert.strictEqual(w.nkSessionBack(),'exam','the shell shows its exit dialog for a scheduled mock');
});
check('paused session: no guard, Back is normal',()=>{
  const w=world();w.start('practice',{lifecycle:'paused'});same(w.urls(),['#topics','#practice']);
  assert.strictEqual(w.nkSessionBack(),'');
});
check('a session ended elsewhere drops its guard quietly; one Back then leaves',()=>{
  const w=world();w.start('practice');w.state.activeSession=null;w.render();w.flush();
  same(w.urls(),['#topics','#practice']);w.back();same(w.urls(),['#topics']);same(w.prompts,[]);
});
check('Android shell: no guard; nkSessionBack opens the native Abandon dialog',()=>{
  const calls=[];const shell={platform:()=>'android',confirmAction:(...a)=>{calls.push(a);return true;}};
  const w=world({shell});w.start('practice');same(w.urls(),['#topics','#practice'],'the shell answers Back natively');
  assert.strictEqual(w.nkSessionBack(),'handled');assert.strictEqual(calls.length,1);
  same(calls[0].slice(1,2),['Abandon this session?']);same(calls[0].slice(3),['Abandon','Cancel']);
  w.answer(true);assert.strictEqual(w.state.activeSession,null);
  assert.strictEqual(w.nkSessionBack(),'','no session: Back navigates');
  const e=world({shell});e.start('exam');e.setOverlay(true);assert.strictEqual(e.nkSessionBack(),'handled');assert.strictEqual(e.overlaysClosed,1);
  assert.strictEqual(e.nkSessionBack(),'handled');same(calls[1].slice(1,2),['Abandon this test?']);
});
console.log(results.map(n=>'  ok · '+n).join('\n'));
console.log('SESSION_BACK_GUARD_OK');
'''


def main() -> None:
    world = WORLD % {
        "parse": extract_function(PAGE, "parseHash"),
        "navigate": extract_function(PAGE, "navigate"),
        "module": MODULE.read_text(encoding="utf-8"),
    }
    script = TESTS % {"world": json.dumps(world)}
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    print(out.stdout, end="")
    if out.returncode:
        raise SystemExit(out.stderr or "session back guard tests failed")

    # Source contracts: the page routes Back through the guard; the shell asks the page.
    assert "nkBackGuardHold(page,id)" in extract_function(PAGE, "navigate"), "navigate() must hold for the Back guard"
    assert "const nkNavigateBase=navigate;" in PAGE
    assert "nkSessionBack," in PAGE, "window.QB must expose nkSessionBack for the Android shell"
    assert "function nkSessionBackOverlay(" in INTERACTION.read_text(encoding="utf-8")
    java = JAVA.read_text(encoding="utf-8")
    assert "NATIVE_BACK_ABANDON_V1" in java and "q.nkSessionBack()" in java
    assert '"\\"handled\\"".equals(value)' in java, "MainActivity must stop when the page handled Back"
    assert 'setTitle("Do you want to exit?")' in java, "scheduled mocks keep the native exit warning"
    print("SESSION_BACK_GUARD_CONTRACT_OK")


if __name__ == "__main__":
    main()
