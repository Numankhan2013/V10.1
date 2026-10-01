#!/usr/bin/env python3
"""Remove redundant navigation copy after all page owners; keep study behavior intact."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'app/src/main/assets/index.html'
MARKER = 'NK_APP_CLARITY_V1_START'

def transform(source):
    if MARKER in source:
        return source
    if 'NK_LEARNING_INSIGHTS_V1_START' not in source:
        raise SystemExit('App clarity must follow learning Insights')
    for name in ['dashboard','nkRevisionDeskPage','testsPage','morePage','nkFsrsReviewPage','nkFsrsSettingsMarkup','nkStudyLibraryPage','nkQuestionSearchPage','nkNotesPage','nkRevisionCards','nkCbtBuilderPage','studyModuleBuilderPage']:
        if 'function '+name+'(' not in source:
            raise SystemExit('Missing clarity renderer: '+name)
    assert source.count('  window.QB={') == 1
    assert source.count('</head>') == 1
    source=source.replace('</head>', '<style id="nk-app-clarity-v1">\n'+(ROOT/'tools/app_clarity.css').read_text()+'\n</style>\n</head>',1)
    return source.replace('  window.QB={',(ROOT/'tools/app_clarity_core.js').read_text()+'\n  window.QB={',1)

if __name__ == '__main__':
    HTML.write_text(transform(HTML.read_text()),encoding='utf-8')
    print('APP_CLARITY_INSTALLED navigation=true study_behavior=preserved')
