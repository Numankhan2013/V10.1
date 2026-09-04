from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# The old delegated review guards are intentionally bypassed. The CTA calls one
# stable entry point owned by this final layer, so future wrapper order cannot
# silently break CBT review navigation.
s = s.replace(' data-v102-review-cta="1"', '')
s = s.replace(
    'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))"',
    'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))"'
)
s = s.replace(
    'data-review-test-id="${esc(t.id)}">Review Solutions</button>',
    'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>'
)

# A last-resort submit lock: remove the exam submit control before the original
# function runs, then clean any stale toast/control after navigation. This makes
# the UI transition deterministic even if a later render/ticker fires.
lock = r'''<script id="cbt-final-lock">
(function(){
  function cleanExamUi(){
    document.querySelectorAll('.navigator .primary-btn').forEach(function(b){
      if(/submit\s*test/i.test(String(b.textContent||''))){b.disabled=true;b.remove();}
    });
    document.querySelectorAll('#toast-root .toast').forEach(function(e){e.remove();});
  }

  function openReview(testId){
    try{
      const qb=window.QB;
      if(!qb||typeof qb.getState!=='function')return false;
      const st=qb.getState();
      const wanted=decodeURIComponent(String(testId||''));
      const tests=Array.isArray(st.tests)?st.tests:[];
      const t=tests.find(function(x){return String(x.id)===wanted;});
      if(!t||!Array.isArray(t.questionIds)||!t.questionIds.length){
        console.error('CBT Review: completed test not found',wanted);
        return false;
      }
      const answers=Object.assign({},t.answers||{});
      const submitted={};
      t.questionIds.forEach(function(id){submitted[id]=Object.prototype.hasOwnProperty.call(answers,id);});
      st.activeSession={
        id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),
        title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),
        index:0,answers:answers,submitted:submitted,startedAt:t.createdAt||Date.now(),
        questionEnteredAt:Date.now(),questionTimes:Object.assign({},t.questionTimes||{})
      };
      localStorage.setItem('qbank_state_v1',JSON.stringify(st));
      cleanExamUi();
      if(typeof qb.nav==='function')qb.nav('review-test',String(t.id));
      else location.hash='#review-test/'+encodeURIComponent(String(t.id));
      return false;
    }catch(e){console.error('CBT Review final lock failed',e);return false;}
  }

  window.__QB_OPEN_REVIEW=openReview;
  if(window.QB)window.QB.reviewTest=openReview;

  // Wrap the already-defined submit function without changing its scoring or
  // persistence logic. The wrapper only owns the visual transition.
  if(window.QB&&typeof window.QB.submitExam==='function'&&!window.QB.submitExam.__cbtFinalLock){
    const original=window.QB.submitExam;
    function submitExamFinalLock(){
      cleanExamUi();
      try{return original.apply(this,arguments);}
      finally{setTimeout(cleanExamUi,0);setTimeout(cleanExamUi,80);}
    }
    submitExamFinalLock.__cbtFinalLock=true;
    window.QB.submitExam=submitExamFinalLock;
  }

  // Remove a submit control if an old exam render briefly survives the route
  // transition. This observer is narrowly scoped to the exam navigator.
  const mo=new MutationObserver(function(){
    if(document.querySelector('.navigator'))cleanExamUi();
  });
  mo.observe(document.body,{subtree:true,childList:true});
})();
</script>'''

s = s.replace('</body>', lock + '\n</body>', 1)
HTML.write_text(s, encoding='utf-8')
print('CBT final lock installed: stable Review Solutions entry point and deterministic Submit Test cleanup.')
