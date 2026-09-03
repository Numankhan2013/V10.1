from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# Make Review Solutions a stable CTA. The delegated handler does not depend
# on inline onclick execution or hashchange delivery inside Android WebView.
cta = re.compile(r'<button class="primary-btn"\s+type="button" data-v102-review-cta="1" data-review-test-id="\$\{esc\(t\.id\)\}" onclick="window\.QB\.reviewTest\(\'\$\{esc\(t\.id\)\}\'\)">Review Solutions</button>')
replacement = '<a class="primary-btn" role="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" href="#review-test/${encodeURIComponent(t.id)}">Review Solutions</a>'
s, _ = cta.subn(replacement, s, count=1)

if 'function buildReviewSession(t)' not in s:
    marker = '  function reviewTest(testId) {'
    i = s.find(marker)
    if i < 0:
        raise SystemExit('reviewTest function not found')
    builder = """  function buildReviewSession(t) {\n    return { id:`review_${t.id}`, mode:'review', sourceTestId:t.id, title:`Review · ${t.title}`, questionIds:[...t.questionIds], index:0, answers:{...(t.answers||{})}, submitted:Object.fromEntries(t.questionIds.map(id=>[id,Boolean(t.answers?.[id])])), startedAt:t.createdAt, questionTimes:{...(t.questionTimes||{})} };\n  }\n\n"""
    s = s[:i] + builder + s[i:]

pat = re.compile(r"  function reviewTest\(testId\) \{.*?\n  \}\n", re.S)
review_fn = """  function reviewTest(testId) {\n    let wanted=String(testId ?? '');\n    try { wanted=decodeURIComponent(wanted); } catch(_) {}\n    const t=state.tests.find(x=>String(x.id)===wanted || String(x.id)===String(testId));\n    if(!t){ showToast('That test could not be found in saved history.','bad'); return; }\n    const session=buildReviewSession(t);\n    session.questionEnteredAt=Date.now();\n    state.activeSession=session;\n    saveState();\n    route={page:'review-test',id:String(t.id)};\n    render();\n    history.replaceState(null,'',`#review-test/${encodeURIComponent(t.id)}`);\n  }\n"""
s, n = pat.subn(review_fn, s, count=1)
if n != 1:
    raise SystemExit('reviewTest replacement failed')

old_page = "  function reviewTestPage() {\n    let s=state.activeSession;\n    if(!s || s.mode!=='review' || (route.id && String(s.sourceTestId)!==String(route.id))) {\n      const t=state.tests.find(x=>String(x.id)===String(route.id));"
new_page = """  function reviewTestPage() {\n    let s=state.activeSession;\n    const routeId=(()=>{try{return decodeURIComponent(String(route.id||''));}catch(_){return String(route.id||'');}})();\n    if(!s || s.mode!=='review' || (routeId && String(s.sourceTestId)!==routeId)) {\n      const t=state.tests.find(x=>String(x.id)===routeId || String(x.id)===String(route.id));"""
if old_page in s:
    s = s.replace(old_page, new_page, 1)

# Remove any earlier review guard then install one deterministic capture handler.
s = re.sub(r'<script id="v102-review-cta-guard">.*?</script>\\?', '', s, flags=re.S, count=1)
handler = """<script id="v102-review-cta-safe">\n/* Android WebView-safe review CTA. */\ndocument.addEventListener('click', function (event) {\n  const el = event.target && event.target.closest ? event.target.closest('[data-v102-review-cta]') : null;\n  if (!el) return;\n  const id = el.getAttribute('data-review-test-id');\n  if (!id || !window.QB || typeof window.QB.reviewTest !== 'function') return;\n  event.preventDefault();\n  event.stopPropagation();\n  window.QB.reviewTest(id);\n}, true);\n</script>"""
s=re.sub(r'<script id="v102-review-cta-safe">.*?</script>', '', s, flags=re.S)
if '</body>' in s:
    s=s.replace('</body>',handler+'\n</body>',1)
else:
    s += handler

p.write_text(s, encoding='utf-8')
print('repaired', p)
