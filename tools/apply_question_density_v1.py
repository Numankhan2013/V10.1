from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Keep this pass deterministic: rebuilding the same source produces the same UI.
# Remove an earlier copy if the workflow is re-run on an already-patched tree.
s = re.sub(r'<style id="qbank-question-density-v1">.*?</style>\s*', '', s, flags=re.S)

css = r'''<style id="qbank-question-density-v1">
/* QBank Question Density v1
   Goal: professional mobile density inspired by modern medical QBanks.
   Scoped to question cards so dashboards, explanations, PDFs and controls keep
   their existing visual language. */
@media (max-width: 700px) {
  .question-card {
    padding: 16px !important;
  }

  .question-card .q-number,
  .question-card .crumb {
    font-size: 12px !important;
    line-height: 1.35 !important;
  }

  .question-card .question-text {
    font-size: 18px !important;
    line-height: 1.45 !important;
    letter-spacing: -0.01em !important;
    margin-top: 10px !important;
    margin-bottom: 14px !important;
  }

  .question-card .option-list {
    gap: 8px !important;
  }

  .question-card .option {
    min-height: 48px !important;
    padding: 10px 12px !important;
    border-radius: 11px !important;
    line-height: 1.35 !important;
  }

  .question-card .option-text {
    font-size: 16px !important;
    line-height: 1.35 !important;
    letter-spacing: -0.005em !important;
  }

  .question-card .option-letter,
  .question-card .radio {
    flex: 0 0 auto !important;
  }

  .question-card .q-footer {
    margin-top: 14px !important;
    gap: 10px !important;
  }
}

@media (min-width: 701px) {
  .question-card .question-text {
    font-size: 19px !important;
    line-height: 1.48 !important;
  }
}
</style>'''

if '</head>' not in s:
    raise SystemExit('Cannot apply question density: </head> not found')
s = s.replace('</head>', css + '\n</head>', 1)
HTML.write_text(s, encoding='utf-8')
print('Question Density v1 applied.')
