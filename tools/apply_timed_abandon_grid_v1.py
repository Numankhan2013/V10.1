#!/usr/bin/env python3
"""Add confirmed Abandon to the two timed-test grids, never the question page."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'
CORE=ROOT/'tools/timed_abandon_grid_core.js'
MARKER='NK_TIMED_ABANDON_GRID_V1_START'

CSS='''<style id="nk-timed-abandon-grid-v1">
.nk-timed-abandon-grid .qb-nav-submit{position:static!important;box-shadow:none!important}
.nk-timed-abandon-grid .nk-abandon-test{width:100%;min-height:48px;margin-top:9px;padding:0 14px;border:1px solid #c6828b;border-radius:11px;background:#fff;color:#9b3341;font:inherit;font-size:12px;font-weight:800;cursor:pointer}
#nk-session-review.nk-timed-abandon-grid .nk-session-review-actions .nk-abandon-test{grid-column:1/-1;margin-top:0}
.nk-timed-abandon-grid .nk-abandon-test:focus-visible{outline:3px solid #dfa9b0;outline-offset:2px}
</style>'''

def transform(source):
    if MARKER in source:return source
    if 'NK_EXAM_REVIEW_FLAGS_V1_START' not in source:
        raise SystemExit('Timed abandon grid must follow exam review flags')
    if source.count('</head>')!=1 or source.count('  window.QB={')!=1:
        raise SystemExit('Timed abandon grid anchors missing or ambiguous')
    source=source.replace('</head>',CSS+'\n</head>',1)
    source=source.replace('  window.QB={',CORE.read_text(encoding='utf-8').rstrip()+'\n\n  window.QB={nkAbandonTimedTest,',1)
    return source

if __name__=='__main__':
    HTML.write_text(transform(HTML.read_text(encoding='utf-8')),encoding='utf-8')
    print('TIMED_ABANDON_GRID_INSTALLED: navigator and final review grid')
