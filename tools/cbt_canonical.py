from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Keep cbt-final-lock-v2 as the single live Review Solutions engine. This
# canonical step must never wrap/reassign that engine because doing so can
# recurse through window.QB.reviewTest -> __QB_OPEN_REVIEW.
for script_id in ('cbt-canonical-review','cbt-final-lock-v3','final-cbt-review-fix'):
    s = re.sub(rf'<script id="{re.escape(script_id)}">.*?</script>\s*', '', s, flags=re.S)

s = s.replace("onclick=\"window.QB.reviewTest(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")
s = s.replace('data-v102-review-cta="1" data-review-test-id="${esc(t.id)}">Review Solutions</button>', 'data-review-test-id="${esc(t.id)}" onclick="return window.__QB_OPEN_REVIEW(this.getAttribute(\'data-review-test-id\'))">Review Solutions</button>')

lock = r'''<script id="cbt-canonical-review">
(function(){
  'use strict';
  // The live engine was installed by cbt-final-lock-v2 immediately before
  // this canonical step. Preserve that function exactly; do not delegate
  // back through window.QB.reviewTest because that would recurse.
  if(typeof window.__QB_OPEN_REVIEW!=='function'){
    console.error('Canonical CBT Review: live __QB_OPEN_REVIEW API unavailable');
  }
})();
</script>'''
s=s.replace('</body>',lock+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('Canonical Review Solutions entry now preserves the single live CBT review engine without recursive delegation.')
