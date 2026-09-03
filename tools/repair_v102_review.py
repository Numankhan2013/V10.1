from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# Make Review Solutions a real hash link. The page itself reconstructs the
# saved test session, so this remains functional even if inline click JS fails.
cta = re.compile(r'<button class="primary-btn"\s+type="button" data-v102-review-cta="1" data-review-test-id="\$\{esc\(t\.id\)\}" onclick="window\.QB\.reviewTest\(\'\$\{esc\(t\.id\)\}\'\)">Review Solutions</button>')
if 'href="#review-test/${encodeURIComponent(t.id)}"' not in s:
    replacement = '<a class="primary-btn" role="button" data-v102-review-cta="1" data-review-test-id="${esc(t.id)}" href="#review-test/${encodeURIComponent(t.id)}">Review Solutions</a>'
    s, n = cta.subn(replacement, s, count=1)
    if n != 1:
        raise SystemExit(f'Review CTA replacement count={n}')

# Build the review session from the exact saved test record.
if 'function buildReviewSession(t)' not in s:
    marker = '  function reviewTest(testId) {'
    i = s.find(marker)
    if i < 0:
        raise SystemExit('reviewTest function not found')
    builder = '''  function buildReviewSession(t) {\n    return { id:`review_${t.id}`, mode:'review', sourceTestId:t.id, title:`Review · ${t.title}`, questionIds:[...t.questionIds], index:0, answers:{...(t.answers||{})}, submitted:Object.fromEntries(t.questionIds.map(id=>[id,Boolean(t.answers?.[id])])), startedAt:t.createdAt, questionTimes:{...(t.questionTimes||{})} };\n  }\n\n'''
    s = s[:i] + builder + s[i:]

# Replace the old review constructor with the canonical builder.
pat = re.compile(r"  function reviewTest\(testId\) \{.*?\n  \}\n", re.S)
if not pat.search(s):
    raise SystemExit('reviewTest function not found for replacement')
review_fn = '''  function reviewTest(testId) {\n    const t=state.tests.find(x=>String(x.id)===String(testId));\n    if(!t){ showToast('That test could not be found in saved history.','bad'); return; }\n    state.activeSession=buildReviewSession(t);\n    saveState();\n    route={page:'review-test',id:String(t.id)};\n    render();\n    const hash=`review-test/${encodeURIComponent(t.id)}`;\n    if(location.hash!==`#${hash}`) history.replaceState(null,'',`#${hash}`);\n  }\n'''
s = pat.sub(review_fn, s, count=1)

# Ensure direct #review-test/<id> navigation can reconstruct a missing session,
# while preserving the current review index on ordinary re-renders.
old_page = "  function reviewTestPage() {\n    const s=state.activeSession; if(!s || s.mode!=='review') return testsPage();"
new_page = """  function reviewTestPage() {\n    let s=state.activeSession;\n    if(!s || s.mode!=='review' || (route.id && String(s.sourceTestId)!==String(route.id))) {\n      const t=state.tests.find(x=>String(x.id)===String(route.id));\n      if(!t) return testsPage();\n      s=buildReviewSession(t);\n      state.activeSession=s;\n      saveState();\n    }"""
if old_page in s:
    s = s.replace(old_page, new_page, 1)
elif "String(s.sourceTestId)!==String(route.id)" not in s:
    raise SystemExit('reviewTestPage guard not found')

# Remove obsolete duplicate click guard if present.
s = re.sub(r'<script id="v102-review-cta-guard">.*?</script>\\?', '', s, flags=re.S, count=1)
# Clean literal escaped separators accidentally introduced by earlier patches.
s = s.replace('</script>n\n', '</script>\n')
s = s.replace('</script>\\n', '</script>\n').replace('</style>\\n', '</style>\n')

p.write_text(s, encoding='utf-8')
print('repaired', p)
