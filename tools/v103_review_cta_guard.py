from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')
marker = '<!-- V103_REVIEW_CTA_GUARD -->'
if marker not in s:
    js = r'''<script id="v103-review-cta-guard">
(function(){
  'use strict';
  document.addEventListener('click', function(e){
    const el=e.target.closest('[data-v102-review-cta="1"],.v102-review-action');
    if(!el || !window.QB || typeof window.QB.reviewTest!=='function') return;
    const id=el.getAttribute('data-test-id')||el.getAttribute('data-test')||el.dataset.testId||el.dataset.test;
    if(!id) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    window.QB.reviewTest(String(id));
  }, true);
})();
</script>
'''
    s = s.replace('</body>', js + '\n' + marker + '\n</body>', 1)
    p.write_text(s, encoding='utf-8')
    print('V10.3 Review CTA guard installed')
else:
    print('V10.3 Review CTA guard already present')
