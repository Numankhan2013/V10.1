from pathlib import Path
import re

html = Path('app/src/main/assets/index.html').read_text(encoding='utf-8')

required = [
    'cbt-canonical-review',
    'window.__QB_OPEN_REVIEW=openReview',
    'function openReview(testId)',
    'function reviewTestPage()',
    'return sessionShell(`',
    '${bookmarkButton(q.id,21)}',
    "${navIcon('grid')}",
    'id="cr-grid"',
    "document.getElementById('cr-grid').onclick",
    'nk-cbt-review-footer-v1',
    'nk-review-fixed-bar',
]
for token in required:
    if token not in html:
        raise SystemExit(f'Missing CBT invariant: {token}')

for legacy in ('cbt-final-lock-v2', 'cbt-final-lock-v3'):
    if legacy in html:
        raise SystemExit(f'Forbidden legacy CBT runtime layer resurrected: {legacy}')

if 'id="final-cbt-review-fix"' in html:
    raise SystemExit('Competing final-cbt-review-fix override resurrected; Review Solutions must have one owner')

if html.count('id="cbt-canonical-review"') != 1:
    raise SystemExit('CBT canonical entry point must exist exactly once')

cta = re.findall(r'onclick="[^"]*__QB_OPEN_REVIEW\([^\"]*', html)
if not cta:
    raise SystemExit('No Review Solutions CTA is wired to the canonical entry point')

# The canonical entry must delegate to the already-tested live QB review engine.
canon_start = html.find('<script id="cbt-canonical-review">')
canon_end = html.find('</script>', canon_start)
if canon_start < 0 or canon_end < 0:
    raise SystemExit('Canonical Review Solutions script boundaries missing')
canon = html[canon_start:canon_end]
if 'qb.reviewTest(testId)' not in canon:
    raise SystemExit('Canonical Review Solutions entry does not delegate to live QB.reviewTest')
if 'window.render' in canon:
    raise SystemExit('Canonical Review Solutions must not depend on lexical window.render()')
if 'window.QB.reviewTest=' in canon:
    raise SystemExit('Canonical Review Solutions must not replace the live QB.reviewTest implementation')

# Review Solutions must not resurrect the redundant Test Review/Chapter header.
start = html.find('function reviewTestPage()')
end = html.find('function closeQuestionNavigator()', start)
if start < 0 or end < 0:
    raise SystemExit('Review Solutions renderer boundaries missing')
review = html[start:end]
if 'Test Review</div>' in review or 'Back to Tests' in review:
    raise SystemExit('Redundant Review Solutions header chrome still present')
if 'return shell(`' in review:
    raise SystemExit('Review Solutions still uses the topbar shell instead of the normal session question surface')

if 'qbank.local/anatomy/pdf' not in Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java').read_text(encoding='utf-8'):
    raise SystemExit('Anatomy PDF renderer route missing')

for p in (
    'app/src/main/assets/Biochemistry_QBank_Source.pdf',
    'app/src/main/assets/Physiology_QBank_Source.pdf',
    'app/src/main/assets/Anatomy_QBank_Source.pdf',
    'app/src/main/assets/biochemistry_source_solution_map.js',
    'app/src/main/assets/subject_source_solution_maps.js',
):
    path = Path(p)
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f'Missing/empty CBT source asset: {p}')

print('CBT regression guardrails passed: one Review Solutions owner; entry delegates to live QB.reviewTest; native question UI retained; competing override absent; source assets present.')
