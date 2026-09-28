#!/usr/bin/env python3
"""Build a focused source-review packet for the 14 remaining Physiology claim refs."""
from __future__ import annotations

import json
from pathlib import Path

from marrow_images import DATA, ROOT, questions

AUDIT = ROOT / 'build/marrow-images/audit.json'
COVERAGE = DATA / 'images/coverage.json'
OUTPUT = DATA / 'images/review_requests/MANUAL_PHYS_AMBIGUOUS_14_PLAN_20260928.json'
REFS = [
    'marrow__PHYS_CH03_Q013:figure:2',
    'marrow__PHYS_CH05_Q023:figure:1',
    'marrow__PHYS_CH06_Q001:figure:1',
    'marrow__PHYS_CH06_Q003:figure:1',
    'marrow__PHYS_CH06_Q007:figure:1',
    'marrow__PHYS_CH06_Q010:figure:1',
    'marrow__PHYS_CH06_Q010:figure:2',
    'marrow__PHYS_CH06_Q034:figure:1',
    'marrow__PHYS_CH07_Q001:figure:1',
    'marrow__PHYS_CH07_Q002:figure:1',
    'marrow__PHYS_CH07_Q009:figure:2',
    'marrow__PHYS_CH07_Q011:figure:1',
    'marrow__PHYS_CH07_Q016:figure:2',
    'marrow__PHYS_CH07_Q019:figure:2',
]


def main() -> None:
    audit = json.loads(AUDIT.read_text())
    coverage = json.loads(COVERAGE.read_text())
    qs = questions()
    audit_by_id = {row['id']: row for row in audit['bindings']}
    coverage_by_id = {row['id']: row for row in coverage['sourceVisuals']}
    entries = []
    for pos, ref in enumerate(REFS, 1):
        a = audit_by_id[ref]
        c = coverage_by_id[ref]
        if c['coverageStatus'] in {'RELEASED', 'SOURCE_METADATA_INVALID'}:
            raise AssertionError(f'Ref already resolved unexpectedly: {ref}')
        q = qs[a['questionId']]
        entries.append({
            'position': pos,
            'sourceReferenceId': ref,
            'questionId': a['questionId'],
            'coverage': c,
            'metadata': a.get('metadata', {}),
            'candidateImages': a.get('candidateImages', []),
            'question': q.get('question', ''),
            'explanation': q.get('explanation', ''),
            'structuredExplanation': q.get('structuredExplanation', {}),
            'provenance': q.get('provenance', {}),
            'decision': None,
            'review': {
                'sourcePageInspected': False,
                'questionOwnershipChecked': False,
                'roleOrderChecked': False,
                'answerSafetyChecked': False,
                'notes': ''
            }
        })
    value = {
        'schemaVersion': 1,
        'kind': 'MARROW_IMAGE_FOCUSED_AMBIGUOUS_REVIEW_PLAN',
        'batchId': 'MANUAL_PHYS_AMBIGUOUS_14_20260928',
        'subject': 'Physiology',
        'referenceCount': len(entries),
        'source': audit['sources']['Physiology'],
        'entries': entries,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print('PHYS_AMBIGUOUS_REVIEW_PLAN_OK', len(entries))


if __name__ == '__main__':
    main()
