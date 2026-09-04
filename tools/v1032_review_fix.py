from pathlib import Path

INDEX = Path('app/src/main/assets/index.html')
MARKER = '<!-- V1032_REVIEW_FIX -->'

PATCH = r'''<!-- V1032_REVIEW_FIX -->
<style id="v1032-review-fix-css">
  .v1032-review-bar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 14px;padding:12px 14px;border:1px solid #e6eaf0;border-radius:14px;background:#fff}
  .v1032-review-count{font-size:13px;color:#667085;font-weight:700}
  .v1032-review-nav{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}
  .v1032-review-nav button{min-width:34px;height:34px;border:1px solid #d9dee7;border-radius:9px;background:#fff;font-weight:800;cursor:pointer}
  .v1032-review-nav button.active{background:#111827;color:#fff;border-color:#111827}
  .v1032-review-nav button.correct{box-shadow:inset 0 -3px 0 #16a34a}
  .v1032-review-nav button.wrong{box-shadow:inset 0 -3px 0 #dc2626}
</style>
<script id="v1032-review-fix-script">
(function(){
  'use strict';
  const LS='qbank_state_v1';
  const state=()=>{try{return window.QB&&window.QB.getState?window.QB.getState():null}catch(_){return null}};
  const persist=s=>{try{localStorage.setItem(LS,JSON.stringify(s))}catch(_){}};
  const getTest=(id)=>{const s=state();if(!s)return null;const wanted=decodeURIComponent(String(id??''));return (Array.isArray(s.tests)?s.tests:[]).find(t=>String(t.id)===wanted)||null};

  function makeReview(id){
    const s=state(),t=getTest(id); if(!s||!t||!Array.isArray(t.questionIds)||!t.questionIds.length)return false;
    s.activeSession={id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),index:0,answers:Object.assign({},t.answers||{}),submitted:Object.fromEntries(t.questionIds.map(qid=>[qid,Object.prototype.hasOwnProperty.call(t.answers||{},qid)])),startedAt:t.createdAt||Date.now(),questionTimes:Object.assign({},t.questionTimes||{})};
    persist(s);
    const h='#review-test/'+encodeURIComponent(String(t.id));
    if(location.hash!==h) location.hash=h; else {location.hash='';location.hash=h;}
    return true;
  }

  function patchNavigation(){
    if(!window.QB||window.QB.__v1032ReviewNav)return;
    const originalNext=window.QB.nextQ,originalPrev=window.QB.prevQ,originalGo=window.QB.goIndex;
    window.QB.nextQ=function(){const s=state(),a=s&&s.activeSession;if(a&&a.mode==='review'){if(a.index<a.questionIds.length-1){a.index++;persist(s);location.hash='#review-test/'+encodeURIComponent(String(a.sourceTestId));}return false}return originalNext&&originalNext.apply(this,arguments)};
    window.QB.prevQ=function(){const s=state(),a=s&&s.activeSession;if(a&&a.mode==='review'){if(a.index>0){a.index--;persist(s);location.hash='#review-test/'+encodeURIComponent(String(a.sourceTestId));}return false}return originalPrev&&originalPrev.apply(this,arguments)};
    window.QB.goIndex=function(i){const s=state(),a=s&&s.activeSession,n=Number(i);if(a&&a.mode==='review'){if(Number.isInteger(n)&&n>=0&&n<a.questionIds.length){a.index=n;persist(s);location.hash='#review-test/'+encodeURIComponent(String(a.sourceTestId));}return false}return originalGo&&originalGo.apply(this,arguments)};
    window.QB.__v1032ReviewNav=true;
  }

  function clickHandler(e){
    const el=e.target&&e.target.closest?e.target.closest('[data-v102-review-cta],[data-review-test-id],.v102-review-action'):null;
    if(!el)return;
    const id=el.getAttribute('data-review-test-id')||el.dataset.reviewTestId;if(!id)return;
    e.preventDefault();e.stopImmediatePropagation();
    if(!makeReview(id)&&window.QB&&window.QB.reviewTest)try{window.QB.reviewTest(id)}catch(_){}
  }

  function verify(){
    patchNavigation();
    const s=state(),a=s&&s.activeSession;
    if(!a||a.mode!=='review')return;
    const expected='#review-test/'+encodeURIComponent(String(a.sourceTestId));
    if(location.hash!==expected)location.hash=expected;
    requestAnimationFrame(function(){
      const text=(document.body&&document.body.innerText||'');
      if(!text.includes('Test Review') && window.QB&&window.QB.reviewTest){try{window.QB.reviewTest(a.sourceTestId)}catch(_) {}}
      if(location.hash!==expected)location.hash=expected;
    });
  }

  document.addEventListener('click',clickHandler,true);
  window.addEventListener('hashchange',function(){setTimeout(verify,0)});
  const boot=setInterval(function(){patchNavigation();if(window.QB&&window.QB.getState)clearInterval(boot);},100);
  setTimeout(verify,50);setTimeout(verify,300);setTimeout(verify,1000);
})();
</script>
'''

text = INDEX.read_text(encoding='utf-8')
if MARKER not in text:
    INDEX.write_text(text.rstrip()+"\n\n"+PATCH, encoding='utf-8')
    print('V1032 review fix appended')
else:
    print('V1032 review fix already present')
