from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Keep cbt-final-lock-v2: it is the tested live review engine. Canonical owns
# only the public entry point and deliberately does not replace the engine.
for script_id in ('cbt-canonical-review','cbt-final-lock-v3','final-cbt-review-fix'):
    s = re.sub(rf'<script id="{re.escape(script_id)}">.*?</script>\s*', '', s, flags=re.S)

s = s.replace("onclick=\"window.QB.reviewTest(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")
s = s.replace('data-v102-review-cta="1" data-review-test-id="${esc(t.id)}">Review Solutions</button>', 'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>')

lock = r'''<script id="cbt-canonical-review">
(function(){
  'use strict';
  function openReview(testId){
    try{
      var qb=window.QB;
      if(qb&&typeof qb.reviewTest==='function') return qb.reviewTest(testId);
      console.error('Canonical CBT Review: live reviewTest API unavailable');
      return false;
    }catch(e){
      console.error('Canonical CBT Review entry failed',e);
      return false;
    }
  }
  window.__QB_OPEN_REVIEW=openReview;
})();
</script>'''
s=s.replace('</body>',lock+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('Canonical Review Solutions entry preserved; live CBT review engine retained.')
