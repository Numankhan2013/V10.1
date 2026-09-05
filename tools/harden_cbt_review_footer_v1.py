from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

marker = 'nk-cbt-review-footer-v1'
if marker not in s:
    pattern = re.compile(
        r'<div class=\\"q-footer\\"><button class=\\"ghost-btn\\" id=\\"cr-prev\\"[^>]*>Previous</button><button class=\\"primary-btn\\" id=\\"cr-next\\"[^>]*>Next</button></div>'
    )
    matches = list(pattern.finditer(s))
    if len(matches) != 1:
        raise SystemExit(f'Expected exactly one CBT review footer, found {len(matches)}')
    old = matches[0].group(0)
    new = '<div class=\\"action-spacer\\"></div><div class=\\"fixed-actions review-fixed-actions\\"><div class=\\"review-fixed-actions-inner\\"><button class=\\"ghost-btn\\" id=\\"cr-prev\\"'
    start = matches[0].start()
    # Preserve the existing disabled attribute on Previous and Next exactly.
    new += old.split('<button class=\\"ghost-btn\\" id=\\"cr-prev\\"', 1)[1]
    new = new.replace('</button></div>', '</button><button class=\\"primary-btn\\" id=\\"cr-next\\"', 1)
    # Rebuild from the two button segments to avoid accidentally changing attributes.
    prev_seg = old[len('<div class=\\"q-footer\\"><button class=\\"ghost-btn\\" id=\\"cr-prev\\"'):old.find('</button>')]
    first_button_end = old.find('</button>') + len('</button>')
    next_start = old.find('<button class=\\"primary-btn\\" id=\\"cr-next\\"', first_button_end)
    next_seg = old[next_start:old.find('</button>', next_start) + len('</button>')]
    new = (
        '<div class=\\"action-spacer\\"></div>'
        '<div class=\\"fixed-actions review-fixed-actions\\">'
        '<div class=\\"review-fixed-actions-inner\\">'
        '<button class=\\"ghost-btn\\" id=\\"cr-prev\\"' + prev_seg +
        next_seg +
        '</div></div>'
    )
    s = s[:start] + new + s[matches[0].end():]

css = r'''
<style id="nk-cbt-review-footer-v1">
.review-fixed-actions{bottom:calc(82px + var(--safe-bottom));z-index:46;padding:9px 10px}
.review-fixed-actions-inner{width:min(860px,100%);margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:center}
.review-fixed-actions .ghost-btn,.review-fixed-actions .primary-btn{width:100%;min-height:48px}
.review-fixed-actions .ghost-btn:disabled{opacity:.45}
.action-spacer{height:112px}
@media(max-width:640px){.review-fixed-actions{bottom:calc(82px + var(--safe-bottom));padding:9px 10px}.review-fixed-actions-inner{gap:8px}.review-fixed-actions .ghost-btn,.review-fixed-actions .primary-btn{min-height:50px}}
</style>
'''
if marker not in s:
    s = s.replace('</head>', css.replace('id="nk-cbt-review-footer-v1"', 'id="nk-cbt-review-footer-v1"') + '</head>', 1)

HTML.write_text(s, encoding='utf-8')
print('CBT review footer hardened into a two-button fixed navigation bar.')
