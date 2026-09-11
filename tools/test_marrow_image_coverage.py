#!/usr/bin/env python3
"""Regression tests for source-reference image coverage accounting."""
from marrow_image_coverage import ADJUDICATION_STATUS, build_coverage


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
    assert summary['effectiveLearnerVisualReferences'] == 4
    assert summary['releasedSourceVisualReferences'] == 1
    assert summary['invalidSourceMetadataReferences'] == 0
    assert summary['resolvedSourceVisualReferences'] == 1
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

    # A demonstrably false source-reference record is resolved only through an
    # exact evidence-backed adjudication. It remains visible in the raw source
    # denominator and is never misreported as a released learner image.
    invalid_audit = {
        'bindings': [{
            'id': 'marrow__BIOCHEM_CH02_Q010:figure:1',
            'questionId': 'marrow__BIOCHEM_CH02_Q010',
            'subject': 'Biochemistry',
            'metadata': {'role': 'explanation', 'source_page': 33},
            'candidateImages': [],
        }]
    }
    adjudications = {
        'schemaVersion': 1,
        'entries': [{
            'id': 'marrow__BIOCHEM_CH02_Q010:figure:1',
            'questionId': 'marrow__BIOCHEM_CH02_Q010',
            'subject': 'Biochemistry',
            'role': 'explanation',
            'sourcePages': [33],
            'status': ADJUDICATION_STATUS,
            'source': {'file': 'biochemistryed8.pdf', 'sha256': '0' * 64},
            'reason': 'Authoritative page has no figure.',
            'evidence': 'Full source page visually inspected.',
        }]
    }
    invalid = build_coverage(invalid_audit, {'assets': []}, adjudications)
    invalid_summary = invalid['summary']['Biochemistry']
    assert invalid_summary['sourceVisualReferences'] == 1
    assert invalid_summary['effectiveLearnerVisualReferences'] == 0
    assert invalid_summary['releasedSourceVisualReferences'] == 0
    assert invalid_summary['invalidSourceMetadataReferences'] == 1
    assert invalid_summary['resolvedSourceVisualReferences'] == 1
    assert invalid_summary['untrackedSourceVisualReferences'] == 0
    assert invalid_summary['sourceVisualCoverageComplete'] is True
    row = invalid['sourceVisuals'][0]
    assert row['coverageStatus'] == ADJUDICATION_STATUS and row['released'] is False

    # Adjudications are fail-closed: wrong page, role or orphaned IDs cannot
    # suppress a real source visual.
    wrong = {'schemaVersion': 1, 'entries': [dict(adjudications['entries'][0])]}
    wrong['entries'][0]['sourcePages'] = [34]
    try:
        build_coverage(invalid_audit, {'assets': []}, wrong)
    except AssertionError as exc:
        assert 'no longer matches audit' in str(exc)
    else:
        raise AssertionError('Mismatched adjudication incorrectly suppressed a source reference')

    print('MARROW_IMAGE_COVERAGE_TEST_OK')


if __name__ == '__main__':
    main()
