from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')
marker = '<!-- V103_REVIEW_CTA_GUARD -->'
js = r'''<script id="v103-review-cta-guard">
(function(){
  'use strict';
  document.addEventListener('click', function(e){
    const el=e.target.closest('[data-v102-review-cta="1"],.v102-review-action');
    if(!el || !window.QB || typeof window.QB.reviewTest!=='function') return;
    const id=el.getAttribute('data-review-test-id')||el.getAttribute('data-test-id')||el.getAttribute('data-test')||el.dataset.reviewTestId||el.dataset.testId||el.dataset.test;
    if(!id) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    window.QB.reviewTest(String(id));
  }, true);
})();
</script>
'''
if marker not in s:
    s = s.replace('</body>', js + '\n' + marker + '\n</body>', 1)
else:
    # Keep the guard deterministic on subsequent clean workflow applications.
    start=s.find('<script id="v103-review-cta-guard">')
    end=s.find('</script>',start)
    if start!=-1 and end!=-1:
        s=s[:start]+js.rstrip().removesuffix('</script>')+s[end:]
p.write_text(s, encoding='utf-8')
print('V10.3 Review CTA guard updated')
