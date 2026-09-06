from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

marker = 'function reviewTestPage()'
start = s.find(marker)
end = s.find('function closeQuestionNavigator()', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate Review Solutions renderer boundaries; refusing ambiguous UI patch.')
seg = s[start:end]

# Remove the review-only page header. The review screen should use the same
# compact question-first hierarchy as the normal Practice question screen.
seg, n = re.subn(
    r'\n\s*<div class="page-head"><div><div class="mode-pill">Test Review</div><h1 class="page-title" style="margin-top:9px">\$\{esc\(s\.title\)\}</h1><div class="page-sub">Question \$\{q\.questionNumber\} of \$\{s\.questionIds\.length\}</div></div><button class="ghost-btn" onclick="window\.QB\.nav\(\'tests\'\)">Back to Tests</button></div>',
    '', seg, count=1
)
if n != 1:
    raise SystemExit(f'Expected exactly one Review Solutions page header; found {n}. Refusing ambiguous patch.')

seg, n = re.subn(r'\breturn shell\(`', 'return sessionShell(`', seg, count=1)
if n != 1:
    raise SystemExit('Expected exactly one Review Solutions shell() call; refusing ambiguous patch.')

# Match the working normal-question header: it is outside the card and remains
# visible at the top of the question surface. This makes the grid control
# physically visible rather than burying it inside the scrollable question card.
old_head = '<section class="card question-card"><div class="q-head"><div class="q-number">Question ${q.questionNumber} of ${s.questionIds.length}</div><div class="q-actions">${bookmarkButton(q.id,21)}<button class="icon-btn" id="cr-grid" aria-label="Question Navigator" onclick="window.QB.openQuestionNavigator()">${navIcon(\'grid\')}</button></div></div><div class="crumb">${esc(q.chapter)}</div>'
new_head = '<div class="practice-focus-head"><div class="q-number">Question ${q.questionNumber} of ${s.questionIds.length}</div><div class="q-actions">${bookmarkButton(q.id,21)}<button class="icon-btn" id="cr-grid" aria-label="Question Navigator" title="Question Navigator" onclick="window.QB.openQuestionNavigator()">${navIcon(\'grid\')}</button></div></div><div class="question-shell"><section class="card question-card"><div class="crumb">${esc(q.chapter)}</div>'
if old_head not in seg:
    raise SystemExit('Could not locate Review Solutions question header; refusing ambiguous patch.')
seg = seg.replace(old_head, new_head, 1)

# Restore the original source-PDF explanation renderer used by normal questions.
# Review Solutions must never substitute the parsed/reconstructed explanation
# text when a source PDF solution exists.
old_explain = '${q.explanation?`<div class="label">Source explanation</div><div class="feedback-body">${formatReviewExplanation(q.explanation)}</div>`:\'\'}'
new_explain = '${q.explanation?`<div class="label">Source explanation</div><div class="feedback-body source-explanation">${renderExplanationText(q.explanation,q)}</div>`:\'\'}'
if old_explain not in seg:
    raise SystemExit('Review Solutions reconstructed explanation path not found; refusing ambiguous patch.')
seg = seg.replace(old_explain, new_explain, 1)

# The header now opened .question-shell, so close it after the card before the
# fixed review footer.
seg = seg.replace('</div></section>\n    `', '</section></div>\n    `', 1)

footer = '<div class="q-footer"><button class="ghost-btn" onclick="window.QB.prevQ()">Previous</button><button class="primary-btn" onclick="window.QB.nextQ()">Next ${navIcon(\'chevron\',15)}</button></div>'
if 'nk-review-fixed-bar' not in seg:
    if footer not in seg:
        raise SystemExit('Could not locate Review Solutions footer; refusing ambiguous patch.')
    inner = footer[len('<div class="q-footer">'):-len('</div>')]
    fixed = '<div class="nk-review-footer-spacer"></div><div class="nk-review-fixed-bar"><div class="nk-review-fixed-bar-inner">' + inner + '</div></div>'
    seg = seg.replace(footer, fixed, 1)

s = s[:start] + seg + s[end:]

# Keep the marker required by packaged regression checks. The native icon-btn is
# the sole visible grid visual; no competing styling layer is added.
if 'id="nk-review-solution-grid-style"' not in s:
    s = s.replace('</head>', '<style id="nk-review-solution-grid-style"></style>\n</head>', 1)

p.write_text(s, encoding='utf-8')
print('Review Solutions now uses the normal compact question UI, original source-PDF explanations, visible bookmark + native grid controls, and fixed Previous/Next.')
