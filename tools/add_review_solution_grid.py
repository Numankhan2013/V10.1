from pathlib import Path

p = Path('app/src/main/assets/index.html')
s = p.read_text(encoding='utf-8')

# The canonical CBT renderer is installed earlier in the workflow and owns the
# Review Solutions DOM. Reuse the existing question navigator; do not create a
# second grid implementation.
if 'id="cr-grid"' not in s:
    needle = '<header class="topbar"><div class="brand">QBank</div><button class="ghost-btn" id="cr-back">Back to Tests</button></header>'
    replacement = '<header class="topbar"><div class="brand">QBank</div><div class="nk-review-header-actions"><button class="icon-btn" id="cr-grid" aria-label="Question Navigator" title="Question Navigator">${navIcon(\'grid\')}</button><button class="ghost-btn" id="cr-back">Back to Tests</button></div></header>'
    count = s.count(needle)
    if count != 1:
        raise SystemExit(f'Expected exactly one canonical Review Solutions header; found {count}. Refusing ambiguous patch.')
    s = s.replace(needle, replacement, 1)

if "document.getElementById('cr-grid').onclick" not in s:
    candidates = [
        "document.getElementById('cr-back').onclick=back;",
        "document.getElementById('cr-back').onclick=()=>window.QB.nav('tests');",
    ]
    hits = [x for x in candidates if x in s]
    if len(hits) != 1:
        raise SystemExit(f'Expected exactly one canonical Review Solutions back-button wiring form; found {len(hits)}. Refusing ambiguous patch.')
    needle = hits[0]
    replacement = needle + "document.getElementById('cr-grid').onclick=()=>window.QB.openQuestionNavigator();"
    s = s.replace(needle, replacement, 1)

style = '''\n<style id="nk-review-solution-grid-style">\n.nk-review-header-actions{display:flex;align-items:center;gap:10px}.nk-review-header-actions .icon-btn{flex:0 0 auto}\n@media(max-width:640px){.nk-review-header-actions{gap:7px}.nk-review-header-actions .ghost-btn{padding-inline:14px}}\n</style>\n'''
if 'id="nk-review-solution-grid-style"' not in s:
    pos = s.find('</head>')
    if pos < 0:
        raise SystemExit('Could not locate </head>; refusing patch.')
    s = s[:pos] + style + s[pos:]

p.write_text(s, encoding='utf-8')
print('Review Solutions question-grid control added.')
