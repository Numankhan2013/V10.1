#!/usr/bin/env python3
"""Surface the saved active timed test on Home and Tests after Exit."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'
CORE=ROOT/'tools/timed_resume_card_core.js'
MARKER='NK_TIMED_RESUME_CARD_V1_START'

CSS='''<style id="nk-timed-resume-card-v1">
.nk-timed-resume{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:15px 0;padding:17px 18px;border:1px solid #d0d8ee;border-radius:16px;background:linear-gradient(115deg,#f2f5ff,#fff);box-shadow:0 5px 18px #21336a0c}
.nk-timed-resume-copy{min-width:0}.nk-timed-resume-copy>span{font-size:10px;font-weight:850;letter-spacing:.09em;color:#5265a9}.nk-timed-resume h2{margin:5px 0 6px;font-size:16px;line-height:1.3;color:#1d2a61;overflow-wrap:anywhere}
.nk-timed-resume p{margin:0;color:#34446c;font-size:12px;font-weight:750}.nk-timed-resume small{display:block;margin-top:5px;color:#65718b;font-size:11px;line-height:1.45}
.nk-timed-resume button{min-height:46px;flex:none;display:flex;align-items:center;justify-content:center;gap:5px;padding:0 14px;border:0;border-radius:11px;background:#40398f;color:#fff;font:inherit;font-size:12px;font-weight:800;cursor:pointer}
.nk-timed-resume button:focus-visible{outline:3px solid #9cace9;outline-offset:2px}
@media(max-width:560px){.nk-timed-resume{align-items:stretch;flex-direction:column;padding:15px}.nk-timed-resume button{width:100%}}
</style>'''

def replace_once(source,old,new,label):
    count=source.count(old)
    if count!=1:raise SystemExit(f'{label}: expected one anchor, found {count}')
    return source.replace(old,new,1)

def transform(source):
    if MARKER in source:return source
    if 'NK_EXAM_REVIEW_FLAGS_V1_START' not in source:
        raise SystemExit('Timed resume card must follow saved CBT and review marks')
    source=replace_once(source,'</head>',CSS+'\n</head>','resume card styles')
    source=replace_once(source,'<section class="nk-home-focus-card">',
        '${nkTimedResumeCard(\'home\')}<section class="nk-home-focus-card">','Home card position')
    source=replace_once(source,'<section class="nk-v3-section nk-test-main-action">',
        '${nkTimedResumeCard(\'tests\')}<section class="nk-v3-section nk-test-main-action">','Tests card position')
    source=replace_once(source,'  window.QB={',CORE.read_text(encoding='utf-8').rstrip()+'\n\n  window.QB={nkResumeTimedTest,','resume action')
    return source

if __name__=='__main__':
    HTML.write_text(transform(HTML.read_text(encoding='utf-8')),encoding='utf-8')
    print('TIMED_RESUME_CARD_INSTALLED: Home and Tests reveal the active timed test')
