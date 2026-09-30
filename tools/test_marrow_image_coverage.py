#!/usr/bin/env python3
"""Regression tests for source-reference image coverage accounting."""
from marrow_image_coverage import ADJUDICATION_STATUS, build_coverage
from marrow_images import DATA, SOURCES, sha


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
                'provenance': {'questionPages': [500], 'explanationPages': [501]},
            },
            {
                'id': 'marrow__BIOCHEM_CH20_Q002:unmapped',
                'questionId': 'marrow__BIOCHEM_CH20_Q002',
                'subject': 'Biochemistry',
                'status': 'REVIEW_REQUIRED',
                'reason': 'Text cue without figure metadata',
                'provenance': {'questionPages': [502], 'explanationPages': [503]},
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
    bio_file = SOURCES['Biochemistry'][1]
    bio_hash = sha((DATA / 'source_pdfs' / bio_file).read_bytes())
    cue_reviews = {'schemaVersion': 1, 'entries': [
        {
            'id': 'marrow__BIOCHEM_CH20_Q001:unmapped',
            'questionId': 'marrow__BIOCHEM_CH20_Q001', 'subject': 'Biochemistry',
            'sourcePages': [500, 501], 'source': {'file': bio_file, 'sha256': bio_hash},
            'status': 'NO_SOURCE_VISUAL', 'reason': 'No additional figure is present on the cited question or explanation pages.',
            'evidence': 'Reviewed source pages 500 and 501 against the question and explanation text.',
        },
        {
            'id': 'marrow__BIOCHEM_CH20_Q002:unmapped',
            'questionId': 'marrow__BIOCHEM_CH20_Q002', 'subject': 'Biochemistry',
            'sourcePages': [502, 503], 'source': {'file': bio_file, 'sha256': bio_hash},
            'status': 'VISUAL_REFERENCE_REQUIRED', 'reason': 'The source page contains an untracked question-time figure.',
            'evidence': 'Reviewed the exact source page and confirmed the figure matches the question prompt.',
            'visualReferences': [{
                'id': 'marrow__BIOCHEM_CH20_Q002:figure:1',
                'role': 'question', 'sourcePages': [502],
            }],
        },
    ]}
    coverage = build_coverage(audit, registry, cue_reviews=cue_reviews)
    summary = coverage['summary']['Biochemistry']
    assert summary['sourceVisualReferences'] == 5
    assert summary['effectiveLearnerVisualReferences'] == 5
    assert summary['releasedSourceVisualReferences'] == 1
    assert summary['invalidSourceMetadataReferences'] == 0
    assert summary['resolvedSourceVisualReferences'] == 1
    assert summary['trackedButUnreleasedReferences'] == 1
    assert summary['untrackedSourceVisualReferences'] == 3
    assert summary['additionalCueDerivedVisualReferences'] == 1
    assert summary['textCueReviewItems'] == 1
    assert summary['sourceVisualCoverageComplete'] is False
    assert summary['humanCompletenessClaimAllowed'] is False
    cue_rows = coverage['textCueReview']
    assert {row['status'] for row in cue_rows} == {'SOURCE_REVIEWED_NO_VISUAL', 'VISUAL_REFERENCE_REQUIRED'}
    assert next(row for row in cue_rows if row['questionId'].endswith('Q002'))['linkedReferenceIds'] == [
        'marrow__BIOCHEM_CH20_Q002:figure:1']

    released_registry = {'assets': registry['assets'] + [{
        'id': 'cue-discovered-released-figure', 'status': 'PASS',
        'source': {'page': 502},
        'bindings': [{
            'questionId': 'marrow__BIOCHEM_CH20_Q002', 'role': 'question', 'order': 1,
            'status': 'PASS', 'source': {'page': 502},
        }],
    }]}
    released_cue = build_coverage(audit, released_registry, cue_reviews=cue_reviews)
    released_q2 = next(row for row in released_cue['textCueReview'] if row['questionId'].endswith('Q002'))
    assert released_q2['status'] == 'SOURCE_VISUALS_RELEASED'
    assert released_cue['summary']['Biochemistry']['textCueReviewItems'] == 0

    wrong_role_registry = {'assets': registry['assets'] + [{
        'id': 'cue-discovered-wrong-role', 'status': 'PASS',
        'source': {'page': 502},
        'bindings': [{
            'questionId': 'marrow__BIOCHEM_CH20_Q002', 'role': 'explanation', 'order': 1,
            'status': 'PASS', 'source': {'page': 502},
        }],
    }]}
    wrong_role = build_coverage(audit, wrong_role_registry, cue_reviews=cue_reviews)
    wrong_role_q2 = next(row for row in wrong_role['textCueReview'] if row['questionId'].endswith('Q002'))
    assert wrong_role_q2['status'] == 'VISUAL_REFERENCE_REQUIRED'
    assert wrong_role['summary']['Biochemistry']['textCueReviewItems'] == 1

    wrong_page_registry = {'assets': registry['assets'] + [{
        'id': 'cue-discovered-wrong-page', 'status': 'PASS',
        'source': {'page': 503},
        'bindings': [{
            'questionId': 'marrow__BIOCHEM_CH20_Q002', 'role': 'question', 'order': 1,
            'status': 'PASS', 'source': {'page': 503},
        }],
    }]}
    wrong_page = build_coverage(audit, wrong_page_registry, cue_reviews=cue_reviews)
    wrong_page_q2 = next(row for row in wrong_page['textCueReview'] if row['questionId'].endswith('Q002'))
    assert wrong_page_q2['status'] == 'VISUAL_REFERENCE_REQUIRED'

    pending_registry = {'assets': registry['assets'] + [{
        'id': 'cue-discovered-pending-figure', 'status': 'REVIEW_REQUIRED',
        'source': {'page': 502},
        'bindings': [{
            'questionId': 'marrow__BIOCHEM_CH20_Q002', 'role': 'question', 'order': 1,
            'status': 'REVIEW_REQUIRED', 'source': {'page': 502},
        }],
    }]}
    pending_cue = build_coverage(audit, pending_registry, cue_reviews=cue_reviews)
    pending_q2 = next(row for row in pending_cue['textCueReview'] if row['questionId'].endswith('Q002'))
    assert pending_q2['status'] == 'VISUAL_REFERENCE_REQUIRED'

    # A source-reviewed adjacent continuation page can bind a cue visual while
    # retaining the immutable question/explanation provenance union. Unlisted
    # pages remain rejected at coverage construction.
    continuation_audit = {'bindings': [{
        'id': 'marrow__PHYSIO_CH20_Q018:unmapped',
        'questionId': 'marrow__PHYSIO_CH20_Q018', 'subject': 'Physiology',
        'status': 'REVIEW_REQUIRED', 'reason': 'Text cue without figure metadata',
        'provenance': {'questionPages': [370], 'explanationPages': [382]},
    }]}
    continuation_review = {'schemaVersion': 1, 'entries': [{
        'id': 'marrow__PHYSIO_CH20_Q018:unmapped',
        'questionId': 'marrow__PHYSIO_CH20_Q018', 'subject': 'Physiology',
        'sourcePages': [370, 382], 'reviewedVisualPages': [371],
        'source': {'file': SOURCES['Physiology'][1],
                   'sha256': sha((DATA / 'source_pdfs' / SOURCES['Physiology'][1]).read_bytes())},
        'status': 'VISUAL_REFERENCE_REQUIRED', 'reason': 'Stem continues to following-page figure.',
        'evidence': 'Inspected source pages 370–371; page 371 is the visual continuation of the prompt on 370.',
        'visualReferences': [{'id': 'marrow__PHYSIO_CH20_Q018:figure:1',
                              'role': 'question', 'sourcePages': [371]}],
    }]}
    continuation = build_coverage(continuation_audit, {'assets': []}, cue_reviews=continuation_review)
    assert continuation['sourceVisuals'][0]['sourcePages'] == [371]
    unlisted_review = {'schemaVersion': 1, 'entries': [{
        **continuation_review['entries'][0], 'reviewedVisualPages': [],
    }]}
    try:
        build_coverage(continuation_audit, {'assets': []}, cue_reviews=unlisted_review)
    except AssertionError as exc:
        assert 'exceed cue provenance' in str(exc)
    else:
        raise AssertionError('Unlisted continuation pages must fail closed')

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

    # A reviewed false-positive cue clears only with exact source pages and PDF
    # fingerprint. New or changed cues stay visible and fail closed.
    stale_cue_reviews = {'schemaVersion': 1, 'entries': [dict(cue_reviews['entries'][0])]}
    stale_cue_reviews['entries'][0]['sourcePages'] = [500]
    try:
        build_coverage(audit, registry, cue_reviews=stale_cue_reviews)
    except AssertionError as exc:
        assert 'Text-cue pages changed' in str(exc)
    else:
        raise AssertionError('A source-page change must invalidate text-cue review')

    unmatched_cue_reviews = {'schemaVersion': 1, 'entries': [dict(cue_reviews['entries'][0])]}
    unmatched_cue_reviews['entries'][0]['id'] = 'marrow__BIOCHEM_CH20_Q099:unmapped'
    try:
        build_coverage(audit, registry, cue_reviews=unmatched_cue_reviews)
    except AssertionError as exc:
        assert 'no longer matches audit' in str(exc)
    else:
        raise AssertionError('Orphaned text-cue reviews must fail closed')

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

    # A real continuation image is not resolved against the wrong imported page.
    from copy import deepcopy
    continuation_audit = deepcopy(invalid_audit)
    continuation_audit['sources'] = {'Biochemistry': {
        'file': 'biochemistryed8.pdf', 'sha256': 'a' * 64,
        'pages': [{}] * 40,
    }}
    expected = continuation_audit['bindings'][0]
    continuation_registry = {'assets': [{
        'id': 'continuation', 'status': 'PASS', 'source': {'page': 34},
        'bindings': [{'questionId': expected['questionId'], 'role': 'explanation', 'order': 1}],
    }]}
    assert build_coverage(continuation_audit, continuation_registry)['sourceVisuals'][0]['released'] is False
    page_review = {'schemaVersion': 1, 'entries': [{
        'id': expected['id'], 'questionId': expected['questionId'], 'subject': 'Biochemistry',
        'role': 'explanation', 'originalSourcePages': [33], 'reviewedSourcePages': [34],
        'source': {'file': 'biochemistryed8.pdf', 'sha256': 'a' * 64},
        'reason': 'The visual continues on the following source page.',
        'evidence': 'Both authoritative pages inspected; visual occurs before the next solution.',
    }]}
    corrected = build_coverage(continuation_audit, continuation_registry, page_reviews=page_review)
    row = corrected['sourceVisuals'][0]
    assert row['released'] and row['sourcePages'] == [33] and row['reviewedSourcePages'] == [34]
    assert continuation_audit['bindings'][0] == expected
    for field, bad_value in [('questionId', 'wrong-owner'), ('role', 'question'),
                             ('originalSourcePages', [32]), ('reviewedSourcePages', [41]),
                             ('source', {'file': 'biochemistryed8.pdf', 'sha256': 'b' * 64})]:
        wrong_review = deepcopy(page_review)
        wrong_review['entries'][0][field] = bad_value
        try:
            build_coverage(continuation_audit, continuation_registry, page_reviews=wrong_review)
        except AssertionError:
            pass
        else:
            raise AssertionError(f'Unsafe continuation review accepted: {field}')

    print('MARROW_IMAGE_COVERAGE_TEST_OK')


if __name__ == '__main__':
    main()
