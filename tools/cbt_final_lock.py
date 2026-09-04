from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# The old delegated review guards are intentionally bypassed. The CTA calls one
# stable entry point owned by this final layer, so wrapper order cannot silently
# break CBT review navigation.
s = s.replace(' data-v102-review-cta="1"', '')
s = s.replace(
    'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))"',
    'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))"'
)
s = s.replace(
    'data-review-test-id="${esc(t.id)}">Review Solutions</button>',
    'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>'
)

# Final CBT runtime layer. This deliberately owns the Review Solutions entry
# point and the navigator lifecycle instead of depending on earlier wrappers.
lock = r'''<script id="cbt-final-lock-v2">
(function(){
  function cleanExamUi(){
    document.querySelectorAll('.navigator .primary-btn, .qb-nav-submit').forEach(function(b){
      if(/submit\s*test/i.test(String(b.textContent||''))){b.disabled=true;b.remove();}
    });
    // The direct question navigator lives outside #app. Remove it on submit so
    // it cannot remain over Test Analysis after the route changes.
    document.getElementById('qb-question-navigator')?.remove();
    document.querySelectorAll('#toast-root .toast').forEach(function(e){e.remove();});
  }

  function loadStateFallback(){
    try{
      const raw=localStorage.getItem('qbank_state_v1');
      return raw?JSON.parse(raw):null;
    }catch(e){console.error('CBT Review state read failed',e);return null;}
  }

  function openReview(testId){
    try{
      const qb=window.QB;
      const wanted=decodeURIComponent(String(testId||''));
      // Prefer the live QB state, but fall back to persisted state. This avoids
      // making Review Solutions depend on a particular wrapper's getState shape.
      let st=(qb&&typeof qb.getState==='function')?qb.getState():null;
      if(!st||!Array.isArray(st.tests))st=loadStateFallback();
      if(!st)return false;
      const tests=Array.isArray(st.tests)?st.tests:[];
      const t=tests.find(function(x){return String(x.id)===wanted||String(x.id)===String(testId);});
      if(!t||!Array.isArray(t.questionIds)||!t.questionIds.length){
        console.error('CBT Review: completed test not found',wanted);
        return false;
      }

      const answers=Object.assign({},t.answers||{});
      const submitted={};
      t.questionIds.forEach(function(id){submitted[id]=Object.prototype.hasOwnProperty.call(answers,id);});
      st.activeSession={
        id:'review_'+String(t.id),
        mode:'review',
        sourceTestId:String(t.id),
        title:'Review · '+String(t.title||'Completed Test'),
        questionIds:t.questionIds.slice(),
        index:0,
        answers:answers,
        submitted:submitted,
        startedAt:t.createdAt||Date.now(),
        questionEnteredAt:Date.now(),
        questionTimes:Object.assign({},t.questionTimes||{})
      };
      localStorage.setItem('qbank_state_v1',JSON.stringify(st));
      cleanExamUi();

      // Use the public navigation API when available, then explicitly set the
      // hash as a second path. This makes the route deterministic on older
      // Android WebViews where history/hash handling can be inconsistent.
      const target='#review-test/'+encodeURIComponent(String(t.id));
      let navigated=false;
      if(qb&&typeof qb.nav==='function'){
        try{qb.nav('review-test',String(t.id));navigated=true;}catch(e){console.error('CBT Review nav API failed',e);}
      }
      if(String(location.hash)!==target){location.hash=target;}
      else if(!navigated){window.dispatchEvent(new HashChangeEvent('hashchange'));}
      return false;
    }catch(e){
      console.error('CBT Review final lock failed',e);
      return false;
    }
  }

  window.__QB_OPEN_REVIEW=openReview;
  if(window.QB)window.QB.reviewTest=openReview;

  // Wrap the already-defined submit function without changing scoring or
  // persistence. The wrapper owns only cleanup/transition presentation.
  if(window.QB&&typeof window.QB.submitExam==='function'&&!window.QB.submitExam.__cbtFinalLock){
    const original=window.QB.submitExam;
    function submitExamFinalLock(){
      cleanExamUi();
      try{return original.apply(this,arguments);}
      finally{setTimeout(cleanExamUi,0);setTimeout(cleanExamUi,80);setTimeout(cleanExamUi,250);}
    }
    submitExamFinalLock.__cbtFinalLock=true;
    window.QB.submitExam=submitExamFinalLock;
  }

  // If an old exam navigator is rendered by a legacy layer, remove only the
  // Submit Test control. The direct navigator overlay is cleaned on submit.
  const mo=new MutationObserver(function(){
    if(document.querySelector('.navigator'))cleanExamUi();
  });
  mo.observe(document.body,{subtree:true,childList:true});
})();
</script>'''

s = s.replace('</body>', lock + '\n</body>', 1)
HTML.write_text(s, encoding='utf-8')
print('CBT final lock v2 installed: persistent-state Review Solutions route plus navigator cleanup.')
