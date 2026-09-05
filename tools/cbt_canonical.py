from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Remove every previous canonical CBT runtime layer. The normal app renderer is
# the sole owner of the Review Solutions screen; this layer only enters it.
s = re.sub(r'<script id="cbt-canonical-review">.*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="cbt-final-lock-v3">.*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="cbt-final-lock-v2">.*?</script>\s*', '', s, flags=re.S)

# Normalize all known Review Solutions CTA forms to one stable entry point.
s = s.replace("onclick=\"window.QB.reviewTest(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")
s = s.replace("onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")

# Canonical entry point delegates to the live QBank review engine.  Crucially,
# it does NOT replace QB.reviewTest and does NOT depend on window.render(), which
# is intentionally lexical inside the main QBank renderer.  QB.nav() is the
# public route transition and therefore works on Android WebView as well.
lock = r'''<script id="cbt-canonical-review">
(function(){
  'use strict';
  function openReview(testId){
    try{
      var qb=window.QB;
      if(qb&&typeof qb.reviewTest==='function'&&qb.reviewTest!==openReview){
        return qb.reviewTest(testId);
      }
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
print('Canonical Review Solutions now delegates to the live QBank review engine; no duplicate renderer or render() dependency.')
