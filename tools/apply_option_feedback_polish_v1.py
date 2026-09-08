from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')
s = re.sub(r'<style id="qbank-option-feedback-polish-v1">.*?</style>\s*', '', s, flags=re.S)

css = r'''<style id="qbank-option-feedback-polish-v1">
/* V10.3.9 — remove duplicate correctness symbols and strengthen answer letters. */
.question-card .option.correct:after,
.question-card .option.wrong:after { display:none !important; content:none !important; }
.question-card .option-letter {
  width:26px !important;
  height:26px !important;
  min-width:26px !important;
  padding:0 !important;
  margin-top:0 !important;
  border-radius:8px !important;
  display:grid !important;
  place-items:center !important;
  background:#f0f1f5 !important;
  color:#686b78 !important;
  font-size:11px !important;
  font-weight:850 !important;
  line-height:1 !important;
}
.question-card .option.selected:not(.correct):not(.wrong) .option-letter {
  background:#dfe5ff !important;
  color:var(--primary-2) !important;
}
.question-card .option.correct .option-letter {
  background:#159a74 !important;
  color:#fff !important;
}
.question-card .option.wrong .option-letter {
  background:#c94b57 !important;
  color:#fff !important;
}
.question-card .option.correct .radio,
.question-card .option.wrong .radio { opacity:.68 !important; }
@media(max-width:640px){
  .question-card .option-letter { width:25px !important; height:25px !important; min-width:25px !important; border-radius:7px !important; }
}
</style>'''
if '</head>' not in s:
    raise SystemExit('</head> missing')
s = s.replace('</head>', css + '\n</head>', 1)
HTML.write_text(s, encoding='utf-8')
print('V10.3.9 option feedback polish applied.')
