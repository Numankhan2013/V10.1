from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# Review Solutions must be a real button. Do not depend on URL/hash navigation,
# because Android WebView wrappers can intercept anchors before the app router.
cta_pat = re.compile(r'<(?:a|button)\b[^>]*data-v102-review-cta="1"[^>]*>Review Solutions</(?:a|button)>')
replacement = '<button class="primary-btn" type="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}">Review Solutions</button>'
s, n = cta_pat.subn(replacement, s, count=1)
if n != 1:
    # Accept the known source form if the generic expression missed it.
    old = '<a class="primary-btn" role="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" href="#review-test/${encodeURIComponent(t.id)}">Review Solutions</a>'
    if old in s:
        s = s.replace(old, replacement, 1)
    elif 'data-v102-review-cta="1"' not in s:
        raise SystemExit(f'Review CTA replacement count={n}')

# Build the review session from the exact saved test record.
if 'function buildReviewSession(t)' not in s:
    marker = '  function reviewTest(testId) {'
    i = s.find(marker)
    if i < 0:
        raise SystemExit('reviewTest function not found')
    builder = '''  function buildReviewSession(t) {
    return { id:`review_${t.id}`, mode:'review', sourceTestId:t.id, title:`Review · ${t.title}`, questionIds:[...t.questionIds], index:0, answers:{...(t.answers||{})}, submitted:Object.fromEntries(t.questionIds.map(id=>[id,Boolean(t.answers?.[id])])), startedAt:t.createdAt, questionTimes:{...(t.questionTimes||{})} };
  }

'''
    s = s[:i] + builder + s[i:]

# Replace the review constructor with a deterministic saved-test lookup.
pat = re.compile(r"  function reviewTest\(testId\) \{.*?\n  \}\n", re.S)
if not pat.search(s):
    raise SystemExit('reviewTest function not found for replacement')
review_fn = '''  function reviewTest(testId) {
    const wanted=String(testId ?? '');
    const t=state.tests.find(x=>String(x.id)===wanted);
    if(!t){ showToast('That test could not be found in saved history.','bad'); return; }
    state.activeSession=buildReviewSession(t);
    saveState();
    route={page:'review-test',id:String(t.id)};
    render();
  }
'''
s = pat.sub(review_fn, s, count=1)

# Ensure direct review routes can reconstruct the exact saved session if needed.
old_page = "  function reviewTestPage() {\n    const s=state.activeSession; if(!s || s.mode!=='review') return testsPage();"
new_page = '''  function reviewTestPage() {
    let s=state.activeSession;
    if(!s || s.mode!=='review' || (route.id && String(s.sourceTestId)!==String(route.id))) {
      const t=state.tests.find(x=>String(x.id)===String(route.id));
      if(!t) return testsPage();
      s=buildReviewSession(t);
      state.activeSession=s;
      saveState();
    }'''
if old_page in s:
    s = s.replace(old_page, new_page, 1)

# Install one capture-phase handler after the app code. This is deliberately
# independent of inline onclick, hashchange, and router interception.
handler = '''
<script id="v102-review-direct-handler">
(function(){
  document.addEventListener('click', function(event){
    var el = event.target && event.target.closest ? event.target.closest('[data-v102-review-cta]') : null;
    if(!el) return;
    var id = el.getAttribute('data-review-test-id');
    if(!id || !window.QB || typeof window.QB.reviewTest !== 'function') return;
    event.preventDefault();
    event.stopImmediatePropagation();
    window.QB.reviewTest(id);
  }, true);
})();
</script>
'''
s = re.sub(r'<script id="v102-review-direct-handler">.*?</script>', '', s, flags=re.S)
s = s.replace('</body>', handler + '</body>') if '</body>' in s else s + handler

# Remove any obsolete duplicate review CTA guards.
s = re.sub(r'<script id="v102-review-cta-guard">.*?</script>', '', s, flags=re.S)

# Clean literal escaped separators accidentally introduced by earlier patches.
s = s.replace('</script>n\n', '</script>\n')
s = s.replace('</script>\\n', '</script>\n').replace('</style>\\n', '</style>\n')

p.write_text(s, encoding='utf-8')
print('repaired', p)
