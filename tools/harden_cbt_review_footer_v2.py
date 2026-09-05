from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# The canonical review renderer builds this footer inside a template string. Give
# it a completely unique class so generic .fixed-actions rules cannot interfere.
old = '<div class="action-spacer"></div><div class="fixed-actions review-fixed-actions"><div class="review-fixed-actions-inner">'
new = '<div class="nk-review-footer-spacer"></div><div class="nk-review-fixed-bar"><div class="nk-review-fixed-bar-inner">'
if s.count(old) != 1:
    raise SystemExit(f'Expected exactly one canonical review footer markup, found {s.count(old)}')
s = s.replace(old, new, 1)

# The session position is the authoritative review position. Do not display the
# source-bank question number here (which can be outside the session range).
old_q = "<div class=\"q-number\">Question '+esc(q.questionNumber||s.index+1)+' of '+s.questionIds.length+'</div>"
new_q = "<div class=\"q-number\">Question '+(s.index+1)+' of '+s.questionIds.length+'</div>"
if s.count(old_q) != 1:
    raise SystemExit(f'Expected exactly one review question-number expression, found {s.count(old_q)}')
s = s.replace(old_q, new_q, 1)

css = r'''
<style id="nk-cbt-review-footer-v2">
.nk-review-footer-spacer{height:112px}
.nk-review-fixed-bar{position:fixed!important;left:0;right:0;bottom:calc(82px + var(--safe-bottom));z-index:120!important;display:block!important;visibility:visible!important;opacity:1!important;background:rgba(255,255,255,.98);backdrop-filter:blur(18px);border-top:1px solid var(--line);box-shadow:0 -8px 24px rgba(25,27,48,.10);padding:9px 10px}
.nk-review-fixed-bar-inner{width:min(860px,100%);margin:0 auto;display:flex!important;flex-direction:row!important;gap:10px;align-items:stretch}
.nk-review-fixed-bar-inner>#cr-prev,.nk-review-fixed-bar-inner>#cr-next{display:flex!important;visibility:visible!important;opacity:1!important;position:static!important;flex:1 1 0!important;width:0!important;min-width:0!important;min-height:50px!important;margin:0!important}
.nk-review-fixed-bar-inner>#cr-prev:disabled{opacity:.45!important}
@media(max-width:640px){.nk-review-fixed-bar{bottom:calc(82px + var(--safe-bottom));padding:9px 10px}.nk-review-fixed-bar-inner{gap:8px}.nk-review-fixed-bar-inner>#cr-prev,.nk-review-fixed-bar-inner>#cr-next{min-height:50px!important}}
</style>
'''
if 'id="nk-cbt-review-footer-v2"' not in s:
    s = s.replace('</head>', css + '</head>', 1)

HTML.write_text(s, encoding='utf-8')
print('CBT review footer v2 installed: isolated two-button fixed bar + session-relative numbering.')
