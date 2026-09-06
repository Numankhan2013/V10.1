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

# Remove any review-only page header chrome if present.
seg, _ = re.subn(
    r'\n\s*<div class="page-head">.*?<button class="ghost-btn" onclick="window\.QB\.nav\(\'tests\'\)"[^>]*>Back to Tests</button></div>',
    '', seg, count=1, flags=re.S
)

# The Review Solutions screen uses the same compact session surface as Practice.
seg, n = re.subn(r'\breturn shell\(`', 'return sessionShell(`', seg, count=1)
if n != 1:
    raise SystemExit('Review Solutions session shell could not be established.')

# Replace the current question-card opening/header with the exact visible
# normal-question focus header plus the card. This deliberately places the
# grid control outside the scrollable card so it cannot disappear from view.
head_pat = re.compile(
    r'<section class="card question-card"><div class="q-head">.*?</div><div class="crumb">',
    re.S
)
head_repl = (
    '<div class="practice-focus-head">'
    '<div class="q-number">Question ${q.questionNumber} of ${s.questionIds.length}</div>'
    '<div class="q-actions">'
    '${bookmarkButton(q.id,21)}'
    '<button class="icon-btn" id="cr-grid" aria-label="Question Navigator" title="Question Navigator" onclick="window.QB.openQuestionNavigator()">${navIcon(\'grid\')}</button>'
    '</div></div>'
    '<div class="question-shell"><section class="card question-card"><div class="crumb">'
)
seg, n = head_pat.subn(head_repl, seg, count=1)
if n != 1:
    raise SystemExit('Review Solutions question header could not be replaced.')

# The normal question renderer displays the source-PDF solution via
# renderExplanationText(). Reuse that exact renderer here; never reconstruct
# explanation paragraphs from q.explanation text.
explain_pat = re.compile(
    r'\$\{q\.explanation\?`<div class="label">Source explanation</div><div class="feedback-body">.*?</div>`:\'\'\}',
    re.S
)
explain_repl = '${q.explanation?`<div class="label">Source explanation</div><div class="feedback-body source-explanation">${renderExplanationText(q.explanation,q)}</div>`:\'\'}'
seg, n = explain_pat.subn(explain_repl, seg, count=1)
if n != 1:
    raise SystemExit('Review Solutions explanation block could not be replaced.')
if 'renderExplanationText(q.explanation,q)' not in seg:
    raise SystemExit('Review Solutions source-PDF explanation renderer is missing.')

# Close the question shell opened by the new header before the fixed footer.
seg = seg.replace('</div></section>\n    `', '</section></div>\n    `', 1)

# Preserve the existing fixed Previous/Next footer; only create it if an older
# version of this renderer has not already installed it.
footer = '<div class="q-footer"><button class="ghost-btn" onclick="window.QB.prevQ()">Previous</button><button class="primary-btn" onclick="window.QB.nextQ()">Next ${navIcon(\'chevron\',15)}</button></div>'
if 'nk-review-fixed-bar' not in seg:
    if footer not in seg:
        raise SystemExit('Could not locate Review Solutions footer; refusing ambiguous patch.')
    inner = footer[len('<div class="q-footer">'):-len('</div>')]
    fixed = '<div class="nk-review-footer-spacer"></div><div class="nk-review-fixed-bar"><div class="nk-review-fixed-bar-inner">' + inner + '</div></div>'
    seg = seg.replace(footer, fixed, 1)

s = s[:start] + seg + s[end:]

if 'id="nk-review-solution-grid-style"' not in s:
    s = s.replace('</head>', '<style id="nk-review-solution-grid-style"></style>\n</head>', 1)

p.write_text(s, encoding='utf-8')
print('Review Solutions now uses source-PDF explanations plus the visible normal-question bookmark/grid header and fixed Previous/Next.')
