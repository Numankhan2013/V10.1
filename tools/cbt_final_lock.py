from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Keep the original, already-tested Review Solutions engine as the source of truth.
# This layer must never replace window.QB.reviewTest: doing that makes the public
# entry point recursive on some build orders. We capture the live function once
# and expose a stable alias instead.
s = s.replace(' data-v102-review-cta="1"', '')
s = s.replace(
    'data-review-test-id="${esc(t.id)}" onclick="window.QB.reviewTest(this.getAttribute(\'data-review-test-id\'))"',
    'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))"'
)
s = s.replace(
    'data-review-test-id="${esc(t.id)}">Review Solutions</button>',
    'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>'
)

lock = r'''<script id="cbt-final-lock-v2">
(function(){
  function cleanExamUi(){
    document.querySelectorAll('.navigator .primary-btn, .qb-nav-submit').forEach(function(b){
      if(/submit\s*test/i.test(String(b.textContent||''))){b.disabled=true;b.remove();}
    });
    document.getElementById('qb-question-navigator')?.remove();
    document.querySelectorAll('#toast-root .toast').forEach(function(e){e.remove();});
  }

  // Preserve the original Review Solutions function exported by the main app.
  // Do not reassign window.QB.reviewTest here. Capturing the live function before
  // other layers run prevents wrapper recursion while keeping the tested engine.
  var liveReview=(window.QB&&typeof window.QB.reviewTest==='function')
    ? window.QB.reviewTest
    : null;

  function openReview(testId){
    try{
      if(typeof liveReview==='function') return liveReview.call(window.QB,testId);
      console.error('CBT Review: live reviewTest API unavailable');
      return false;
    }catch(e){
      console.error('CBT Review entry failed',e);
      return false;
    }
  }

  window.__QB_OPEN_REVIEW=openReview;
  if(window.QB) window.QB.openReviewSolutions=openReview;

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

  const mo=new MutationObserver(function(){
    if(document.querySelector('.navigator'))cleanExamUi();
  });
  mo.observe(document.body,{subtree:true,childList:true});
})();
</script>'''

s = s.replace('</body>', lock + '\n</body>', 1)
HTML.write_text(s, encoding='utf-8')
print('CBT final lock v3 installed: original live Review Solutions engine preserved; stable non-recursive entry alias exposed.')
