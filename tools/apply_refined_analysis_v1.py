#!/usr/bin/env python3
"""Install compact result analysis and reusable named mocks after screen clarity."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'app/src/main/assets/index.html'
MARKER = 'NK_REFINED_ANALYSIS_V1_START'


def transform(source):
    if MARKER in source:
        return source
    for required in ('NK_APP_CLARITY_V1_START', 'NK_CBT_RESULT_ANALYSIS_V1_START', 'NK_PRACTICE_CORRECTION_V1_START'):
        if required not in source:
            raise SystemExit(f'Refined analysis must follow {required}')
    for anchor in ('</head>', '  window.QB={'):
        if source.count(anchor) != 1:
            raise SystemExit(f'Expected one refined analysis anchor: {anchor}')
    source = source.replace('</head>', '<style id="nk-refined-analysis-v1">\n' + (ROOT / 'tools/refined_analysis.css').read_text() + '\n</style>\n</head>', 1)
    actions = 'nkAnalysisSetTab,nkAnalysisSetTime,nkAnalysisRename,nkMockName,nkMockSaveDraft,nkMockStart,nkMockSaveResult,nkMockRemove,'
    return source.replace('  window.QB={', (ROOT / 'tools/refined_analysis_core.js').read_text().rstrip() + '\n\n  window.QB={' + actions, 1)


if __name__ == '__main__':
    HTML.write_text(transform(HTML.read_text()), encoding='utf-8')
    print('REFINED_ANALYSIS_INSTALLED named_mocks=true test_tabs=true timing=true')
