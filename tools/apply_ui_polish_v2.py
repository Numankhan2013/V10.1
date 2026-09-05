from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Remove this layer if the workflow is re-run.
s = re.sub(r'<style id="qbank-ui-polish-v2">.*?</style>\s*', '', s, flags=re.S)

css = r'''<style id="qbank-ui-polish-v2">
/* Question stems are PDF line-wrap extraction, not intentional paragraphs. */
.question-card .question-text {
  white-space: normal !important;
  text-align: justify !important;
  text-justify: inter-word !important;
  overflow-wrap: break-word !important;
  hyphens: none !important;
}

/* Chapter mode actions: title and subtitle are independent blocks. */
.chapter-action { min-width: 0 !important; }
.chapter-action > span:last-child { min-width: 0 !important; flex: 1 1 0 !important; }
.chapter-action .t, .chapter-action .d {
  display: block !important;
  white-space: normal !important;
  overflow-wrap: anywhere !important;
}
.chapter-action .t { line-height: 1.22 !important; }
.chapter-action .d { line-height: 1.32 !important; margin-top: 4px !important; }

/* Keep the compact analysis overview visually dominant without making it tall. */
.result-summary { box-shadow: 0 2px 10px rgba(24,30,58,.035) !important; }
.result-summary-bar { height: 8px !important; }

@media(max-width:640px) {
  .chapter-actions { grid-template-columns: 1fr 1fr !important; }
  .chapter-action { min-height: 68px !important; padding: 10px !important; gap: 8px !important; }
  .chapter-action .ico { width: 34px !important; height: 34px !important; }
  .chapter-action .t { font-size: 12px !important; }
  .chapter-action .d { font-size: 10px !important; }
}
</style>'''

if '</head>' not in s:
    raise SystemExit('Cannot apply UI polish v2: </head> missing')
s = s.replace('</head>', css + '\n</head>', 1)

# Product terminology: Practice, not Guide Mode / Guide Practice.
s = s.replace('<div class="mode-pill">Guide Mode</div>', '<div class="mode-pill">Practice Mode</div>')
s = s.replace('<span class="t">Guide Practice</span>', '<span class="t">Practice</span>')

HTML.write_text(s, encoding='utf-8')
print('UI polish v2 applied.')
