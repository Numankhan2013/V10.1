from pathlib import Path

INDEX = Path('app/src/main/assets/index.html')
s = INDEX.read_text(encoding='utf-8')

MARKER = 'nk-home-actions-v1'
if MARKER in s:
    print('Home actions v1 already present; no-op.')
    raise SystemExit(0)

# Home-only composition change. The header keeps the greeting clean; all three
# primary study actions live together inside Today's Focus.
old_header = '<button class="nk-home-v4-continue" onclick="window.QB.continuePractice()">Continue <span>→</span></button>'
if old_header not in s:
    raise SystemExit('Home Continue button target not found; refusing ambiguous patch.')
s = s.replace(old_header, '', 1)

old_actions = '''          <div class="nk-home-v4-actions">\n            ${due?`<button class="nk-home-v4-primary" onclick="window.QB.startLibrary('review')">Review ${fmtNum(due)} <span>→</span></button>`:`<button class="nk-home-v4-primary" onclick="window.QB.startAllPractice()">Practice 20 <span>→</span></button>`}\n            <button class="nk-home-v4-secondary" onclick="window.QB.openTestBuilder()">Timed CBT <span>↗</span></button>\n          </div>'''
new_actions = '''          <div class="nk-home-v4-actions" id="nk-home-actions-v1">\n            <button class="nk-home-v4-action nk-home-v4-action-continue" onclick="window.QB.continuePractice()">Continue Practice <span>→</span></button>\n            ${due?`<button class="nk-home-v4-action nk-home-v4-action-practice" onclick="window.QB.startLibrary('review')">Review ${fmtNum(due)} <span>→</span></button>`:`<button class="nk-home-v4-action nk-home-v4-action-practice" onclick="window.QB.startAllPractice()">Practice 20 Random Questions <span>→</span></button>`}\n            <button class="nk-home-v4-action nk-home-v4-action-timed" onclick="window.QB.openTestBuilder()">Timed CBT <span>↗</span></button>\n          </div>'''
if old_actions not in s:
    raise SystemExit('Home action group target not found; refusing ambiguous patch.')
s = s.replace(old_actions, new_actions, 1)

css = '''<style id="nk-home-actions-v1-style">\n/* HOME ACTIONS V1 — three distinct study actions, kept on the same axis. */\n.nk-home-v4-continue{display:none!important}\n#nk-home-actions-v1{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr) minmax(0,.9fr);gap:8px;width:min(100%,620px);align-items:stretch}\n#nk-home-actions-v1 .nk-home-v4-action{min-height:48px;padding:8px 13px;border-radius:7px;font-size:12px;font-weight:850;line-height:1.15;white-space:normal;display:flex;align-items:center;justify-content:center;gap:7px;text-align:center;cursor:pointer;transition:transform .16s ease,background .16s ease,border-color .16s ease,box-shadow .16s ease}\n#nk-home-actions-v1 .nk-home-v4-action span{margin-left:0;font-size:15px;line-height:1}\n#nk-home-actions-v1 .nk-home-v4-action:hover{transform:translateY(-1px)}\n#nk-home-actions-v1 .nk-home-v4-action-continue{background:#fff;color:#302d63;border:1px solid rgba(255,255,255,.96);box-shadow:0 4px 12px rgba(20,24,60,.13)}\n#nk-home-actions-v1 .nk-home-v4-action-practice{background:rgba(255,255,255,.13);color:#fff;border:1px solid rgba(255,255,255,.46);box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}\n#nk-home-actions-v1 .nk-home-v4-action-timed{background:rgba(28,29,72,.48);color:#fff;border:1px solid rgba(255,255,255,.24);box-shadow:inset 0 1px 0 rgba(255,255,255,.06)}\n@media(max-width:760px){#nk-home-actions-v1{width:100%;grid-template-columns:minmax(0,.95fr) minmax(0,1.3fr) minmax(0,.9fr);gap:7px}.nk-home-v4-today{gap:14px}}\n@media(max-width:430px){#nk-home-actions-v1 .nk-home-v4-action{min-height:54px;padding:7px 7px;font-size:10px;line-height:1.12}#nk-home-actions-v1 .nk-home-v4-action span{font-size:13px}}\n@media(prefers-reduced-motion:reduce){#nk-home-actions-v1 .nk-home-v4-action{transition:none}}\n</style>'''
pos = s.rfind('</head>')
if pos == -1:
    raise SystemExit('No </head> in index.html')
s = s[:pos] + css + '\n' + s[pos:]

INDEX.write_text(s, encoding='utf-8')
print('Home actions v1 applied: header Continue removed; Continue Practice, Practice 20 Random Questions, and Timed CBT now share Today’s Focus with distinct treatments.')
