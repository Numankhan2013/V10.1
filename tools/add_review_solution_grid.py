from pathlib import Path
import re

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

start = s.find('function reviewTestPage()')
end = s.find('function closeQuestionNavigator()', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate Review Solutions renderer boundaries; refusing ambiguous UI patch.')
seg = s[start:end]

# Remove review-only title/header chrome. The question itself already tells us
# the chapter and the user explicitly entered Review Solutions from Tests.
seg, n = re.subn(
    r'\n\s*<div class="page-head"><div><div class="mode-pill">Test Review</div><h1 class="page-title" style="margin-top:9px">\$\{esc\(s\.title\)\}</h1><div class="page-sub">Question \$\{q\.questionNumber\} of \$\{s\.questionIds\.length\}</div></div><button class="ghost-btn" onclick="window\.QB\.nav\(\'tests\'\)">Back to Tests</button></div>',
    '', seg, count=1
)
if n != 1:
    raise SystemExit(f'Expected exactly one Review Solutions page header; found {n}. Refusing ambiguous patch.')

# Use the exact same session question surface as Practice/CBT: no topbar and no
# redundant Review · Chapter heading.
seg, n = re.subn(r'\breturn shell\(`', 'return sessionShell(`', seg, count=1)
if n != 1:
    raise SystemExit('Expected exactly one Review Solutions shell() call; refusing ambiguous patch.')

# Use the same bookmark + sleek SVG grid controls as the normal question UI.
old_actions = '<div class="q-actions"><button class="icon-btn" aria-label="Question Navigator" onclick="window.QB.openQuestionNavigator()">${navIcon(\'grid\')}</button></div>'
new_actions = '<div class="q-actions">${bookmarkButton(q.id,21)}<button class="icon-btn" aria-label="Question Navigator" onclick="window.QB.openQuestionNavigator()">${navIcon(\'grid\')}</button></div>'
if old_actions not in seg:
    raise SystemExit('Could not locate Review Solutions question actions; refusing ambiguous patch.')
seg = seg.replace(old_actions, new_actions, 1)

s = s[:start] + seg + s[end:]

# Remove the obsolete custom header/grid styling; standard icon-btn styling is
# now used, exactly as on the normal question interface.
s = re.sub(r'\n<style id="nk-review-solution-grid-style">.*?</style>\n', '\n', s, flags=re.S)

p.write_text(s, encoding='utf-8')
print('Review Solutions now uses the normal compact question UI with bookmark + native grid controls.')
