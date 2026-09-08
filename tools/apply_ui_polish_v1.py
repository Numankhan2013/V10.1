from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Idempotent layer: replace only our previous polish block.
import re
s = re.sub(r'<style id="qbank-ui-polish-v1">.*?</style>\s*', '', s, flags=re.S)

# 1) Question stem: make the paragraph read as a visually complete block while
# retaining the existing V10.3.5 font size, weight, and line height.
css = r'''<style id="qbank-ui-polish-v1">
/* V10.3.7 UI polish — presentation only. */
.question-card .question-text {
  text-align: justify !important;
  text-justify: inter-word;
  text-wrap: pretty;
  hyphens: auto;
}

/* Chapter mode cards: prevent the title/description from collapsing into one
   inline line. Keep the existing warm, soft color language and click behavior. */
.chapter-action > span:last-child { flex:1 1 auto; min-width:0; }
.chapter-action .t,
.chapter-action .d { display:block !important; white-space:normal !important; overflow-wrap:anywhere; }
.chapter-action .t { line-height:1.25 !important; }
.chapter-action .d { line-height:1.35 !important; }
.chapter-action { align-items:center; }
.chapter-action .ico { width:36px !important; height:36px !important; border-radius:11px !important; }

/* Compact result overview: one glance for total/correct/incorrect/missed. */
.result-summary {
  margin-top:14px;
  padding:17px 18px 15px !important;
  border-radius:18px !important;
}
.result-summary-top {
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:16px;
}
.result-summary-total-label { font-size:11px; color:var(--muted); font-weight:700; }
.result-summary-total { margin-top:2px; font-size:24px; line-height:1.1; font-weight:880; letter-spacing:-.45px; }
.result-summary-score { text-align:right; flex:none; }
.result-summary-score .pct { font-size:31px; line-height:1; font-weight:900; letter-spacing:-.8px; }
.result-summary-score .lbl { margin-top:3px; font-size:12px; font-weight:760; }
.result-summary-counts {
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:14px;
  margin-top:13px;
}
.result-summary-count { display:flex; align-items:baseline; gap:7px; min-width:0; }
.result-summary-count .n { font-size:23px; line-height:1; font-weight:850; font-variant-numeric:tabular-nums; }
.result-summary-count .l { font-size:11px; color:var(--muted); font-weight:650; }
.result-summary-count.correct .n { color:var(--success); }
.result-summary-count.incorrect .n { color:var(--danger); }
.result-summary-count.missed .n { color:var(--warning); }
.result-summary-bar {
  display:flex;
  width:100%;
  height:7px;
  margin-top:14px;
  overflow:hidden;
  border-radius:999px;
  background:#eceef4;
}
.result-summary-bar span { display:block; height:100%; min-width:0; }
.result-summary-bar .correct { background:var(--success); }
.result-summary-bar .incorrect { background:var(--danger); }
.result-summary-bar .missed { background:var(--warning); }

/* Separate the compact overview from the timing/depth metrics. */
.analysis-heading {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin:20px 2px 0;
}
.analysis-heading h2 { margin:0; font-size:20px; line-height:1.2; font-weight:880; letter-spacing:-.35px; }
.analysis-heading .sub { color:var(--muted); font-size:10.5px; font-weight:650; }

/* Keep the four timing cards compact and visually distinct. */
.result-stat-grid { margin-top:11px !important; }
.result-stat { min-height:116px !important; }

@media(max-width:640px){
  .result-summary { padding:15px !important; }
  .result-summary-counts { gap:8px; }
  .result-summary-count { gap:5px; }
  .result-summary-count .n { font-size:21px; }
  .result-summary-count .l { font-size:10px; }
  .result-summary-score .pct { font-size:28px; }
  .analysis-heading { margin-top:17px; }
  .analysis-heading h2 { font-size:18px; }
  .analysis-heading .sub { display:none; }
}
@media(max-width:390px){
  .result-summary-counts { gap:6px; }
  .result-summary-count .n { font-size:19px; }
  .result-summary-count .l { font-size:9.5px; }
  .result-summary-total { font-size:22px; }
}
</style>'''

if '</head>' not in s:
    raise SystemExit('Cannot apply UI polish: </head> missing')
s = s.replace('</head>', css + '\n</head>', 1)

# 2) Replace the tall result hero with the compact overview requested in the
# supplied reference. Data and calculations remain exactly the existing ones.
start = s.find('      <div class="card result-hero">')
marker = '\n      <div class="result-stat-grid"'
end = s.find(marker, start)
if start < 0 or end < 0:
    raise SystemExit('Expected result hero/stat boundary not found')

compact = '''      <div class="card result-summary">
        <div class="result-summary-top">
          <div><div class="result-summary-total-label">Total questions</div><div class="result-summary-total">${fmtNum(t.total)}</div></div>
          <div class="result-summary-score"><div class="pct">${fmtPct(score)}</div><div class="lbl">correct</div></div>
        </div>
        <div class="result-summary-counts">
          <div class="result-summary-count correct"><span class="n">${fmtNum(t.correct)}</span><span class="l">Correct</span></div>
          <div class="result-summary-count incorrect"><span class="n">${fmtNum(t.incorrect)}</span><span class="l">Incorrect</span></div>
          <div class="result-summary-count missed"><span class="n">${fmtNum(t.unattempted)}</span><span class="l">Missed</span></div>
        </div>
        <div class="result-summary-bar" aria-label="${fmtNum(t.correct)} correct, ${fmtNum(t.incorrect)} incorrect, ${fmtNum(t.unattempted)} missed">
          <span class="correct" style="width:${Math.max(0,Math.min(100,t.total?t.correct/t.total*100:0))}%"></span>
          <span class="incorrect" style="width:${Math.max(0,Math.min(100,t.total?t.incorrect/t.total*100:0))}%"></span>
          <span class="missed" style="width:${Math.max(0,Math.min(100,t.total?t.unattempted/t.total*100:0))}%"></span>
        </div>
      </div>
      <div class="analysis-heading"><h2>In-depth performance analysis</h2><span class="sub">Timing &amp; completion</span></div>'''
s = s[:start] + compact + s[end:]

HTML.write_text(s, encoding='utf-8')
print('V10.3.7 UI polish applied.')
