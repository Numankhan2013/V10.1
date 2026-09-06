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

# Review-specific end flow. The existing Question Navigator is shared by
# Practice/CBT/Review, so keep its current behavior for those modes and only
# add an End Review action for mode==='review'. The final Review Next opens the
# same navigator automatically instead of wrapping back to question 1.
if 'function endReview()' not in s:
    next_marker = '  function nextQ(){'
    helper = '''  function endReview(){
    const s=state.activeSession;
    if(!s || s.mode!=='review') return;
    state.activeSession=null;
    saveState();
    closeQuestionNavigator();
    navigate('tests');
  }
'''
    if next_marker not in s:
        raise SystemExit('Could not locate nextQ() for Review Solutions end-flow insertion.')
    s = s.replace(next_marker, helper + next_marker, 1)

old_branch = "else if(s.mode==='review'){s.index=0;render();}"
new_branch = "else if(s.mode==='review'){openQuestionNavigator();}"
if old_branch in s:
    s = s.replace(old_branch, new_branch, 1)
elif new_branch not in s:
    raise SystemExit('Could not locate Review Solutions final-question branch.')

old_submit = ":s.mode==='practice'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endSession()\">End session</button>':'';"
new_submit = ":s.mode==='practice'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endSession()\">End session</button>':s.mode==='review'?'<button type=\"button\" class=\"primary-btn qb-nav-submit\" onclick=\"window.QB.endReview()\">End Review</button>':'';"
if old_submit in s:
    s = s.replace(old_submit, new_submit, 1)
elif 'window.QB.endReview()' not in s:
    raise SystemExit('Could not add End Review action to the existing Question Navigator.')

# Expose the lexical helper through the existing public QB object without
# replacing any existing navigator/session APIs.
if 'endReview:endReview' not in s:
    m = re.search(r'window\.QB=\{([^\n]+)\};', s)
    if not m:
        raise SystemExit('Could not locate canonical window.QB object assignment.')
    body = m.group(1)
    body += ',endReview:endReview'
    s = s[:m.start(1)] + body + s[m.end(1):]

if 'id="nk-review-solution-grid-style"' not in s:
    s = s.replace('</head>', '<style id="nk-review-solution-grid-style"></style>\n</head>', 1)

p.write_text(s, encoding='utf-8')
print('Review Solutions hardened: source-PDF explanations + bookmark/grid + fixed Previous/Next + End Review + automatic navigator at final question.')
