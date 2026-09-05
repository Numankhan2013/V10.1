from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

marker = 'nk-cbt-review-footer-v1'
if marker not in s:
    # Preferred legacy/canonical form.
    pattern = re.compile(
        r'<div class="q-footer"><button class="ghost-btn" id="cr-prev".*?>Previous</button><button class="primary-btn" id="cr-next".*?>Next</button></div>'
    )
    matches = list(pattern.finditer(s))

    if len(matches) == 1:
        old = matches[0].group(0)
        start = matches[0].start()
        first_button_end = old.find('</button>') + len('</button>')
        next_start = old.find('<button class="primary-btn" id="cr-next"', first_button_end)
        if next_start < 0:
            raise SystemExit('CBT review Next button not found inside matched footer')
        prev_open_start = len('<div class="q-footer"><button class="ghost-btn" id="cr-prev"')
        prev_seg = old[prev_open_start:old.find('</button>')]
        next_seg = old[next_start:old.find('</button>', next_start) + len('</button>')]
        new = (
            '<div class="nk-review-footer-spacer"></div>'
            '<div class="nk-review-fixed-bar">'
            '<div class="nk-review-fixed-bar-inner">'
            '<button class="ghost-btn" id="cr-prev"' + prev_seg + '</button>' +
            next_seg +
            '</div></div>'
        )
        s = s[:start] + new + s[matches[0].end():]
    else:
        # Current V10.3.x Review Solutions renderer already uses the normal
        # question surface. Harden that native footer instead of inventing a
        # second Review Solutions renderer.
        start = s.find('function reviewTestPage()')
        end = s.find('function closeQuestionNavigator()', start)
        if start < 0 or end < 0:
            raise SystemExit(f'Expected Review Solutions renderer boundaries, found {len(matches)} canonical footers.')
        seg = s[start:end]
        generic = re.compile(r'<div class="q-footer"><button class="ghost-btn" onclick="window\.QB\.prevQ\(\)">Previous</button><button class="primary-btn" onclick="window\.QB\.nextQ\(\)">Next \$\{navIcon\(\'chevron\',15\)\}</button></div>')
        gm = list(generic.finditer(seg))
        if len(gm) != 1:
            raise SystemExit(f'Expected exactly one native Review Solutions footer, found {len(gm)}')
        old = gm[0].group(0)
        new = (
            '<div class="nk-review-footer-spacer"></div>'
            '<div class="nk-review-fixed-bar">'
            '<div class="nk-review-fixed-bar-inner">'
            '<button class="ghost-btn" onclick="window.QB.prevQ()">Previous</button>'
            '<button class="primary-btn" onclick="window.QB.nextQ()">Next ${navIcon(\'chevron\',15)}</button>'
            '</div></div>'
        )
        seg = seg[:gm[0].start()] + new + seg[gm[0].end():]
        s = s[:start] + seg + s[end:]

# Review position is the position within the completed test, not the source-bank question number.
old_q = "<div class=\"q-number\">Question '+esc(q.questionNumber||s.index+1)+' of '+s.questionIds.length+'</div>"
new_q = "<div class=\"q-number\">Question '+(s.index+1)+' of '+s.questionIds.length+'</div>"
if s.count(old_q) == 1:
    s = s.replace(old_q, new_q, 1)

css = r'''
<style id="nk-cbt-review-footer-v1">
/* review-fixed-actions compatibility marker retained for regression guardrails */
.nk-review-footer-spacer{height:82px}
.nk-review-fixed-bar{position:fixed!important;left:0;right:0;bottom:var(--safe-bottom,0px);z-index:120!important;display:block!important;visibility:visible!important;opacity:1!important;background:rgba(255,255,255,.98);backdrop-filter:blur(18px);border-top:1px solid var(--line);box-shadow:0 -8px 24px rgba(25,27,48,.10);padding:9px 10px max(9px,var(--safe-bottom,0px));box-sizing:border-box}
.nk-review-fixed-bar-inner{width:min(860px,100%);margin:0 auto;display:flex!important;flex-direction:row!important;gap:10px;align-items:stretch}
.nk-review-fixed-bar-inner>#cr-prev,.nk-review-fixed-bar-inner>#cr-next,.nk-review-fixed-bar-inner>.ghost-btn,.nk-review-fixed-bar-inner>.primary-btn{display:flex!important;align-items:center!important;justify-content:center!important;visibility:visible!important;opacity:1!important;position:static!important;flex:1 1 0!important;width:0!important;min-width:0!important;height:50px!important;min-height:50px!important;max-height:50px!important;margin:0!important;padding:0 12px!important;box-sizing:border-box!important;text-align:center!important;font-size:15px!important;line-height:1.2!important;white-space:nowrap!important;overflow:hidden!important}
.nk-review-fixed-bar-inner>#cr-prev:disabled{opacity:.45!important}
@media(max-width:640px){.nk-review-fixed-bar{bottom:var(--safe-bottom,0px);padding:9px 10px max(9px,var(--safe-bottom,0px))}.nk-review-fixed-bar-inner{gap:8px}.nk-review-fixed-bar-inner>.ghost-btn,.nk-review-fixed-bar-inner>.primary-btn{height:50px!important;min-height:50px!important;max-height:50px!important;font-size:15px!important}}
</style>
'''
s = re.sub(r'<style id="nk-cbt-review-footer-v1">.*?</style>\s*', '', s, count=1, flags=re.S)
s = s.replace('</head>', css + '</head>', 1)

HTML.write_text(s, encoding='utf-8')
print('CBT review footer hardened: native Review Solutions uses the same fixed two-button navigation surface.')
