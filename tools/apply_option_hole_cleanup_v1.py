from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Deterministic: remove any prior copy of this layer.
s = re.sub(r'<style id="qbank-option-hole-cleanup-v1">.*?</style>\s*', '', s, flags=re.S)

# Practice option circles are redundant once the option card + A/B/C/D letter provide
# the selection/correctness affordance. Hide only the Practice-session radio slot;
# CBT keeps its existing answer-control behavior untouched.
css = r'''<style id="qbank-option-hole-cleanup-v1">
/* V10.3.11 — remove redundant radio holes from Practice options. */
.qbank-session-page .question-card .option .radio {
  display:none !important;
}
.qbank-session-page .question-card .option {
  gap:10px !important;
}
.qbank-session-page .question-card .option-letter {
  margin-left:0 !important;
}
</style>'''

if '</head>' not in s:
    raise SystemExit('</head> missing')
s = s.replace('</head>', css + '\n</head>', 1)

# The navigator is appended to <body>, while route rendering replaces #app.
# Explicitly close it before session completion so End session / Submit Test cannot
# leave the old navigator overlay or its CTA visible over the result screen.
old = "function finishPracticeSession() {\n    const s=state.activeSession;"
new = "function finishPracticeSession() {\n    closeQuestionNavigator();\n    const s=state.activeSession;"
if old not in s:
    raise SystemExit('finishPracticeSession anchor not found')
s = s.replace(old, new, 1)

old = "function submitExam(auto=false){const s=state.activeSession;"
new = "function submitExam(auto=false){closeQuestionNavigator();const s=state.activeSession;"
if old not in s:
    raise SystemExit('submitExam anchor not found')
s = s.replace(old, new, 1)

HTML.write_text(s, encoding='utf-8')
print('V10.3.11 option-hole cleanup and navigator close fix applied.')
