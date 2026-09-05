from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# The final deterministic review renderer owns this exact review header. Add the
# navigator there so Review Solutions gets the same question grid used elsewhere.
needle = '<button class="ghost-btn" id="cr-back">Back to Tests</button>'
replacement = '<div class="nk-review-header-actions"><button class="icon-btn" id="cr-grid" aria-label="Question Navigator" title="Question Navigator">${navIcon(\'grid\')}</button><button class="ghost-btn" id="cr-back">Back to Tests</button></div>'
if 'id="cr-grid"' in s:
    print('Review Solutions grid already present; no change needed.')
else:
    count = s.count(needle)
    if count != 1:
        raise SystemExit(f'Expected exactly one deterministic Review Solutions header target; found {count}. Refusing ambiguous patch.')
    s = s.replace(needle, replacement, 1)

# Wire the button after the deterministic review renderer creates the DOM.
needle2 = "document.getElementById('cr-back').onclick=()=>window.QB.nav('tests');"
replacement2 = "document.getElementById('cr-back').onclick=()=>window.QB.nav('tests');document.getElementById('cr-grid').onclick=()=>window.QB.openQuestionNavigator();"
if 'document.getElementById(\'cr-grid\').onclick' not in s:
    count = s.count(needle2)
    if count != 1:
        raise SystemExit(f'Expected exactly one Review Solutions back-button wiring target; found {count}. Refusing ambiguous patch.')
    s = s.replace(needle2, replacement2, 1)

# Small, isolated header layout rule; does not alter the existing review footer.
style = '''\n<style id="nk-review-solution-grid-style">\n.nk-review-header-actions{display:flex;align-items:center;gap:10px}.nk-review-header-actions .icon-btn{flex:0 0 auto}\n@media(max-width:640px){.nk-review-header-actions{gap:7px}.nk-review-header-actions .ghost-btn{padding-inline:14px}}\n</style>\n'''
if 'id="nk-review-solution-grid-style"' not in s:
    pos = s.find('</head>')
    if pos < 0:
        raise SystemExit('Could not locate </head>; refusing patch.')
    s = s[:pos] + style + s[pos:]

p.write_text(s, encoding='utf-8')
print('Review Solutions question-grid control added.')
