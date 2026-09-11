#!/usr/bin/env python3
"""Regression tests for source-reference image coverage accounting."""
from marrow_image_coverage import build_coverage


def main():
    audit = {
        'bindings': [
            {
                'id': 'marrow__BIOCHEM_CH18_Q003:figure:1',
                'questionId': 'marrow__BIOCHEM_CH18_Q003',
                'subject': 'Biochemistry',
                'metadata': {'role': 'explanation', 'source_page': 290},
                'candidateImages': [],
            },
            {
                'id': 'marrow__BIOCHEM_CH19_Q002:figure:1',
                'questionId': 'marrow__BIOCHEM_CH19_Q002',
                'subject': 'Biochemistry',
                'metadata': {'role': 'question', 'source_page': 298},
                'candidateImages': [{'page': 298}],
            },
            {
                'id': 'marrow__BIOCHEM_CH19_Q011:figure:1',
                'questionId': 'marrow__BIOCHEM_CH19_Q011',
                'subject': 'Biochemistry',
                'metadata': {'role': 'question', 'source_page': 301},
                'candidateImages': [{'page': 301}],
            },
            {
                'id': 'marrow__BIOCHEM_CH19_Q011:figure:2',
                'questionId': 'marrow__BIOCHEM_CH19_Q011',
                'subject': 'Biochemistry',
                'metadata': {'role': 'explanation', 'source_page': 311},
                'candidateImages': [],
            },
            {
                'id': 'marrow__BIOCHEM_CH20_Q001:unmapped',
                'questionId': 'marrow__BIOCHEM_CH20_Q001',
                'subject': 'Biochemistry',
                'status': 'REVIEW_REQUIRED',
                'reason': 'Text cue without figure metadata',
            },
        ]
    }
    registry = {
        'assets': [
            {
                'id': 'released-question-figure',
                'status': 'PASS',
                'bindings': [
                    {
                        'questionId': 'marrow__BIOCHEM_CH19_Q002',
                        'role': 'question',
                        'order': 1,
                        'status': 'PASS',
                        'source': {'page': 298},
                    }
                ],
            },
            {
                'id': 'held-explanation-figure',
                'status': 'REVIEW_REQUIRED',
                'source': {'page': 311},
                'bindings': [
                    {
                        'questionId': 'marrow__BIOCHEM_CH19_Q011',
                        'role': 'explanation',
                        'order': 2,
                        'status': 'REVIEW_REQUIRED',
                        'source': {'page': 311},
                    }
                ],
            },
        ]
    }
    coverage = build_coverage(audit, registry)
    summary = coverage['summary']['Biochemistry']
    assert summary['sourceVisualReferences'] == 4
    assert summary['releasedSourceVisualReferences'] == 1
    assert summary['trackedButUnreleasedReferences'] == 1
    assert summary['untrackedSourceVisualReferences'] == 2
    assert summary['textCueReviewItems'] == 1
    assert summary['sourceVisualCoverageComplete'] is False
    assert summary['humanCompletenessClaimAllowed'] is False

    q11 = [row for row in coverage['sourceVisuals'] if row['questionId'] == 'marrow__BIOCHEM_CH19_Q011']
    assert len(q11) == 2
    assert {row['coverageStatus'] for row in q11} == {'UNTRACKED_SOURCE_VISUAL', 'UNRELEASED_TRACKED'}

    # A registry with one released binding must never accidentally satisfy two
    # source references for the same question; matching is one-to-one.
    duplicate_audit = {'bindings': [dict(audit['bindings'][1]), dict(audit['bindings'][1])]}
    duplicate_audit['bindings'][1]['id'] = 'marrow__BIOCHEM_CH19_Q002:figure:2'
    duplicate_audit['bindings'][1]['metadata'] = {'role': 'question', 'source_page': 298}
    dup = build_coverage(duplicate_audit, registry)
    dup_summary = dup['summary']['Biochemistry']
    assert dup_summary['sourceVisualReferences'] == 2
    assert dup_summary['releasedSourceVisualReferences'] == 1
    assert dup_summary['untrackedSourceVisualReferences'] == 1

    print('MARROW_IMAGE_COVERAGE_TEST_OK')


if __name__ == '__main__':
    main()
