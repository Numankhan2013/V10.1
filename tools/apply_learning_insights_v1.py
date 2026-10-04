#!/usr/bin/env python3
"""Install the read-only, period-aware Insights dashboard after existing owners."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'app/src/main/assets/index.html'
MARKER = 'NK_LEARNING_INSIGHTS_V1_START'


def replace_once(source, old, new, label):
    if source.count(old) != 1:
        raise SystemExit(f'{label}: expected one anchor, found {source.count(old)}')
    return source.replace(old, new, 1)


def transform(source):
    if MARKER in source:
        return source
    for required in ('NK_QBANK_COVERAGE_V1_START', 'NK_PRACTICE_CORRECTION_V1_START'):
        if required not in source:
            raise SystemExit(f'Learning Insights must follow {required}')
    # Remove only the old analytics function; retain existing coverage/focus APIs.
    pattern = r'function analytics\(\)\s*\{.*?\n  \}'
    if len(re.findall(pattern, source, re.S)) != 1:
        raise SystemExit('Expected one existing analytics renderer')
    source = re.sub(pattern, '', source, count=1, flags=re.S)
    # Optional provenance for future results. Existing records stay untouched.
    source = replace_once(source, "kind:'practice', studyModuleId:s.studyModuleId||null,", "kind:'practice', studyModuleId:s.studyModuleId||null, sessionId:s.id,", 'Practice result identity')
    source = replace_once(source, 'title:s.title,questionIds:[...s.questionIds],answers:{...s.answers},questionTimes:{...qt},correct,incorrect,unattempted,total:', 'title:s.title,sessionId:s.id,questionIds:[...s.questionIds],answers:{...s.answers},questionTimes:{...qt},correct,incorrect,unattempted,total:', 'CBT result identity')
    css = (ROOT / 'tools/learning_insights.css').read_text()
    source = replace_once(source, '</head>', '<style id="nk-learning-insights-v1">\n' + css + '\n</style>\n</head>', 'Insights styles')
    core = (ROOT / 'tools/learning_insights_core.js').read_text().rstrip()
    actions = 'nkLearningSetPeriod,nkLearningMove,nkLearningSetScope,nkLearningSelectBin,nkLearningSetTopics,nkLearningOpenTopic,nkLearningSetHeatYear,nkLearningYearDetail,'
    return replace_once(source, '  window.QB={', core + '\n\n  window.QB={' + actions, 'Insights actions')


if __name__ == '__main__':
    HTML.write_text(transform(HTML.read_text()), encoding='utf-8')
    print('LEARNING_INSIGHTS_INSTALLED periods=true comparisons=true timing=true topics=true fsrs=true recovery=true modules=true activity=true')
