#!/usr/bin/env python3
"""Add durable Mark for review and a saved-test follow-up to timed CBT."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'
CORE=ROOT/'tools/exam_review_flags_core.js'
MARKER='NK_EXAM_REVIEW_FLAGS_V1_START'

CSS='''<style id="nk-exam-review-flags-v1">
.nk-exam-review-row{display:flex;align-items:center;flex-wrap:wrap;gap:8px 12px;margin:18px 0 2px;padding-top:15px;border-top:1px solid #e6e9f0}
.nk-exam-review-toggle{display:inline-flex;align-items:center;justify-content:center;gap:7px;min-height:46px;padding:0 15px;border:1px solid #d8b777;border-radius:11px;background:#fffaf0;color:#76531d;font:inherit;font-size:12px;font-weight:800;cursor:pointer}
.nk-exam-review-toggle span{font-size:20px;line-height:1}.nk-exam-review-toggle.is-marked{background:#fff0cb;border-color:#b77f22;color:#67440f}
.nk-exam-review-row small{color:#758096;font-size:11px;line-height:1.4}.nk-exam-review-toggle:focus-visible,.nk-cbt-marked button:focus-visible{outline:3px solid #e7b75d;outline-offset:2px}
.nk-session-review-q.is-marked{border-color:#c28b2a!important;box-shadow:inset 0 0 0 2px #d7a241}.nk-session-review-q.is-marked small{color:#855a15;font-weight:800}
.nk-session-review-q.is-marked.active{outline:2px solid var(--primary);outline-offset:1px}.nk-review-dot.is-marked,.qb-legend-dot.is-marked{background:#edbe64!important;border-color:#bd8224!important}
.qb-nav-q.is-marked{border-color:#bf8122!important;box-shadow:inset 0 0 0 2px #dfad4c!important}.qb-nav-q.is-marked.active{outline:2px solid var(--primary);outline-offset:1px}
.nk-cbt-marked{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px;border:1px solid #ebd6aa;border-radius:14px;background:#fff9ec}
.nk-cbt-marked strong,.nk-cbt-marked small{display:block}.nk-cbt-marked strong{color:#6e4a18;font-size:14px}.nk-cbt-marked small{margin-top:4px;color:#756d60;font-size:11px;line-height:1.4}
.nk-cbt-marked button{min-height:48px;padding:9px 14px;border:0;border-radius:10px;background:#7c531d;color:#fff;font:inherit;font-size:14px;font-weight:800;display:flex;align-items:center;justify-content:center;gap:5px;white-space:normal;text-align:center;cursor:pointer}
@media(max-width:560px){.nk-cbt-marked{align-items:stretch;flex-direction:column}.nk-cbt-marked button{width:100%;min-height:46px}}
</style>'''

def replace_once(source,old,new,label):
    count=source.count(old)
    if count!=1:raise SystemExit(f'{label}: expected one anchor, found {count}')
    return source.replace(old,new,1)

def transform(source):
    if MARKER in source:return source
    if 'NK_CBT_RESULT_ANALYSIS_V1_START' not in source or 'NK_QUESTION_INTERACTION_INTEGRITY_V1_START' not in source:
        raise SystemExit('Exam review flags must follow durable question interaction and CBT result analysis')
    source=replace_once(source,'</head>',CSS+'\n</head>','review flag styles')
    source=replace_once(source,'<div class="option-list">${options}</div></section>',
        '<div class="option-list">${options}</div>${nkExamReviewButton(q,s)}</section>','exam question control')
    source=replace_once(source,
        'questionTimes:qt,correct,incorrect,unattempted,total:s.questionIds.length,attempted,totalTimeMs,createdAt:now',
        'questionTimes:qt,markedForReview:{...(s.markedForReview||{})},correct,incorrect,unattempted,total:s.questionIds.length,attempted,totalTimeMs,createdAt:now',
        'durable saved-test snapshot')
    source=replace_once(source,'  window.QB={',CORE.read_text(encoding='utf-8').rstrip()+'\n\n  window.QB={nkToggleExamReviewFlag,nkCbtPracticeMarked,','review flag actions')
    return source

if __name__=='__main__':
    HTML.write_text(transform(HTML.read_text(encoding='utf-8')),encoding='utf-8')
    print('EXAM_REVIEW_FLAGS_INSTALLED: timed CBT marks, grids, saved follow-up')
