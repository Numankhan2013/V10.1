#!/usr/bin/env python3
"""Fail-closed coverage audit for learner-facing Marrow source visuals.

The reviewed image registry is not the source-of-truth denominator for coverage.
The source-derived audit is. A source reference is resolved only by a released
PASS/SOURCE_LIMITED binding or by an exact, evidence-backed source-metadata
adjudication kept outside the immutable imported Marrow records. Text-cue-only
items are reported separately and must be cleared before a human completeness
claim.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

from marrow_images import DATA, ROOT, binding_is_released, questions, validate

AUDIT_PATH = ROOT / 'build/marrow-images/audit.json'
DEFAULT_OUTPUT = DATA / 'images/coverage.json'
DEFAULT_ADJUDICATIONS = DATA / 'images/source_reference_adjudications.json'
DEFAULT_PAGE_REVIEWS = DATA / 'images/source_reference_page_reviews.json'
DEFAULT_CUE_REVIEWS = DATA / 'images/source_text_cue_reviews.json'
DEFAULT_DISCOVERY_REVIEWS = DATA / 'images/source_visual_discoveries.json'
SUBJECTS = ('Anatomy', 'Biochemistry', 'Physiology')
ADJUDICATION_STATUS = 'SOURCE_METADATA_INVALID'


def expected_order(binding):
    match = re.search(r':figure:(\d+)$', str(binding.get('id', '')))
    return int(match.group(1)) if match else None


def expected_role(binding):
    metadata = binding.get('metadata') or {}
    role = str(metadata.get('role') or '').strip().lower()
    if role.startswith('question'):
        return 'question'
    if role == 'explanation':
        return 'explanation'
    return None


def expected_pages(binding):
    metadata = binding.get('metadata') or {}
    pages = metadata.get('source_pages')
    if not isinstance(pages, list):
        page = metadata.get('source_page')
        pages = [page] if isinstance(page, int) else []
    return tuple(sorted({int(page) for page in pages if isinstance(page, int) and page > 0}))


def actual_page(asset, binding):
    source = binding.get('source') or asset.get('source') or {}
    page = source.get('page')
    return int(page) if isinstance(page, int) and page > 0 else None


def match_score(expected, asset, binding):
    if binding.get('questionId') != expected.get('questionId'):
        return None
    role = expected_role(expected)
    if role and binding.get('role') != role:
        return None
    order = expected_order(expected)
    if order is not None and binding.get('order') != order:
        return None
    pages = expected_pages(expected)
    page = actual_page(asset, binding)
    if pages and page not in pages:
        return None
    score = 0
    if role and binding.get('role') == role:
        score += 4
    if order is not None and binding.get('order') == order:
        score += 4
    if pages and page in pages:
        score += 2
    return score


def load_adjudications(path):
    if not path.exists():
        return {'schemaVersion': 1, 'entries': []}
    value = json.loads(path.read_text())
    assert value.get('schemaVersion') == 1, 'Unsupported source-reference adjudication schema'
    seen = set()
    for entry in value.get('entries', []):
        assert entry.get('status') == ADJUDICATION_STATUS
        assert entry.get('id') and entry.get('questionId') and entry.get('subject') in SUBJECTS
        assert entry.get('role') in {'question', 'explanation'}
        pages = entry.get('sourcePages')
        assert isinstance(pages, list) and pages and all(isinstance(page, int) and page > 0 for page in pages)
        assert entry.get('reason') and entry.get('evidence')
        source = entry.get('source') or {}
        assert source.get('file') and re.fullmatch(r'[0-9a-f]{64}', str(source.get('sha256', '')))
        key = entry['id']
        assert key not in seen, f'Duplicate source-reference adjudication: {key}'
        seen.add(key)
    return value


def load_cue_reviews(path):
    """Load exact, source-fingerprinted reviews for metadata-free text cues."""
    if not path.exists():
        return {'schemaVersion': 1, 'entries': []}
    value = json.loads(path.read_text())
    assert value.get('schemaVersion') == 1, 'Unsupported text-cue review schema'
    seen = set()
    for entry in value.get('entries', []):
        assert entry.get('id') and entry.get('questionId')
        assert entry.get('subject') in SUBJECTS
        assert entry.get('status') in {'NO_SOURCE_VISUAL', 'VISUAL_REFERENCE_REQUIRED'}
        pages = entry.get('sourcePages')
        assert isinstance(pages, list) and all(isinstance(page, int) and page > 0 for page in pages)
        reviewed_visual_pages = entry.get('reviewedVisualPages', [])
        assert isinstance(reviewed_visual_pages, list)
        assert reviewed_visual_pages == sorted(set(reviewed_visual_pages))
        assert all(isinstance(page, int) and page > 0 for page in reviewed_visual_pages)
        assert entry.get('evidence'), 'Out-of-provenance visual pages require source-review evidence'
        assert entry.get('source') and entry['source'].get('file')
        assert re.fullmatch(r'[0-9a-f]{64}', str(entry['source'].get('sha256', '')))
        assert entry.get('reason') and entry.get('evidence')
        visual_references = entry.get('visualReferences', [])
        assert isinstance(visual_references, list)
        for reference in visual_references:
            assert reference.get('id') and reference.get('role') in {'question', 'explanation'}
            pages = reference.get('sourcePages')
            assert isinstance(pages, list) and pages and pages == sorted(set(pages))
            assert all(isinstance(page, int) and page > 0 for page in pages)
        if entry['status'] == 'VISUAL_REFERENCE_REQUIRED':
            assert visual_references, 'A visual cue must link its explicit source-reference IDs'
        else:
            assert not visual_references, 'NO_SOURCE_VISUAL cannot be used for a visual reference'
        assert entry['id'] not in seen, f"Duplicate text-cue review: {entry['id']}"
        seen.add(entry['id'])
    return value


def adjudication_for(expected, adjudications):
    matches = []
    for entry in adjudications.get('entries', []):
        if entry.get('id') != expected.get('id'):
            continue
        if entry.get('questionId') != expected.get('questionId'):
            continue
        if entry.get('subject') != expected.get('subject'):
            continue
        if entry.get('role') != expected_role(expected):
            continue
        if tuple(sorted(entry.get('sourcePages', []))) != expected_pages(expected):
            continue
        matches.append(entry)
    assert len(matches) <= 1, f'Ambiguous source-reference adjudication: {expected.get("id")}'
    return matches[0] if matches else None


def load_page_reviews(path):
    if not path.exists():
        return {'schemaVersion': 1, 'entries': []}
    value = json.loads(path.read_text())
    assert value.get('schemaVersion') == 1
    return value


def reviewed_reference(expected, audit, page_reviews):
    """Correct a cited page only after exact, source-fingerprinted ownership review."""
    entries = [entry for entry in page_reviews.get('entries', [])
               if entry.get('id') == expected.get('id')]
    assert len(entries) <= 1, f'Duplicate source-page review: {expected.get("id")}'
    if not entries:
        return expected
    entry = entries[0]
    assert entry.get('questionId') == expected.get('questionId')
    assert entry.get('subject') == expected.get('subject')
    assert entry.get('role') == expected_role(expected)
    assert entry.get('originalSourcePages') == list(expected_pages(expected))
    assert entry.get('reason') and entry.get('evidence')
    source = audit.get('sources', {}).get(entry['subject'], {})
    assert source.get('file') == entry.get('source', {}).get('file')
    assert source.get('sha256') == entry.get('source', {}).get('sha256')
    pages = entry.get('reviewedSourcePages')
    assert isinstance(pages, list) and pages and pages == sorted(set(pages))
    assert all(isinstance(page, int) and 0 < page <= len(source.get('pages', [])) for page in pages)
    return {**expected, 'metadata': {**expected['metadata'], 'source_pages': pages}}


def discovery_references(audit, reviews, source_questions):
    """Register visually proven references absent from imported figure metadata."""
    from marrow_images import sha
    references = []
    seen = {binding['id'] for binding in audit.get('bindings', [])}
    for entry in reviews.get('entries', []):
        assert entry['id'] not in seen, 'Duplicate discovered source reference'
        seen.add(entry['id'])
        q = source_questions[entry['questionId']]
        assert q['subject'] == entry['subject']
        fingerprint = sha(json.dumps({key: q.get(key) for key in (
            'id', 'question', 'options', 'correctOption', 'sourcePage', 'sourceQuestionId')},
            ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
        assert fingerprint == entry['canonicalSourceFingerprint'], 'Discovered question changed'
        source = audit['sources'][entry['subject']]
        assert entry['source'] == {key: source[key] for key in ('file', 'sha256')}
        assert entry['role'] in {'question', 'explanation'}
        assert entry['reason'] and entry['evidence']
        assert entry['id'] == entry['questionId'] + ':figure:' + str(entry['order'])
        pages = entry['sourcePages']
        assert pages and pages == sorted(set(pages))
        assert all(isinstance(page, int) and 0 < page <= len(source['pages']) for page in pages)
        references.append({'id': entry['id'], 'questionId': entry['questionId'],
            'subject': entry['subject'], 'metadata': {'role': entry['role'], 'source_pages': pages},
            'candidateImages': [], 'sourceOrigin': 'QUESTION_COMPLETENESS_REVIEW'})
    return references


def build_coverage(audit, registry, adjudications=None, cue_reviews=None, page_reviews=None,
                   discovery_reviews=None, source_questions=None):
    adjudications = adjudications or {'schemaVersion': 1, 'entries': []}
    cue_reviews = cue_reviews or {'schemaVersion': 1, 'entries': []}
    page_reviews = page_reviews or {'schemaVersion': 1, 'entries': []}
    actual_by_question = defaultdict(list)
    for asset in registry['assets']:
        for binding in asset.get('bindings', []):
            actual_by_question[binding.get('questionId')].append((asset, binding))

    used = set()
    rows = []
    cue_rows = []
    matched_adjudications = set()
    matched_cue_reviews = set()
    cue_visual_links = {}
    audit_bindings = list(audit.get('bindings', []))
    audit_bindings.extend(discovery_references(audit, discovery_reviews or {'entries': []},
                                              source_questions or {}))
    for entry in cue_reviews.get('entries', []):
        for reference in entry.get('visualReferences', []):
            allowed_pages = set(entry['sourcePages']) | set(entry.get('reviewedVisualPages', []))
            assert set(reference['sourcePages']).issubset(allowed_pages), \
                f"Visual reference pages exceed cue provenance: {reference['id']}"
            audit_bindings.append({
                'id': reference['id'], 'questionId': entry['questionId'],
                'subject': entry['subject'],
                'metadata': {'role': reference['role'], 'source_pages': reference['sourcePages'],
                             'sourceCueId': entry['id']},
                'candidateImages': [], 'status': 'REVIEW_REQUIRED',
                'sourceOrigin': 'TEXT_CUE_REVIEW',
                'reason': 'Visual discovered during source text-cue review',
            })
    audit_by_ref_id = {binding.get('id'): binding for binding in audit_bindings}
    for expected in audit_bindings:
        if not expected.get('metadata'):
            cue_row = {
                'id': expected.get('id'),
                'questionId': expected.get('questionId'),
                'subject': expected.get('subject'),
                'status': 'TEXT_CUE_REVIEW_REQUIRED',
                'reason': expected.get('reason', 'Text cue without source visual metadata'),
            }
            matches = [entry for entry in cue_reviews.get('entries', [])
                       if entry.get('id') == expected.get('id')
                       and entry.get('questionId') == expected.get('questionId')
                       and entry.get('subject') == expected.get('subject')]
            assert len(matches) <= 1, f"Ambiguous text-cue review: {expected.get('id')}"
            if matches:
                entry = matches[0]
                provenance = expected.get('provenance') or {}
                cue_source_pages = sorted(set((provenance.get('questionPages') or []) +
                                              (provenance.get('explanationPages') or [])))
                from marrow_images import SOURCES, sha
                source_file = SOURCES[expected['subject']][1]
                source_hash = sha((DATA / 'source_pdfs' / source_file).read_bytes())
                assert entry.get('sourcePages') == cue_source_pages, f"Text-cue pages changed: {expected.get('id')}"
                assert entry['source'] == {'file': source_file, 'sha256': source_hash}, f"Text-cue source changed: {expected.get('id')}"
                matched_cue_reviews.add(entry['id'])
                visual_reference_ids = [reference['id'] for reference in entry.get('visualReferences', [])]
                if entry['status'] == 'VISUAL_REFERENCE_REQUIRED':
                    for reference_id in visual_reference_ids:
                        linked = audit_by_ref_id.get(reference_id)
                        assert linked, f"Text-cue source reference is missing from audit: {reference_id}"
                        assert linked.get('questionId') == expected.get('questionId')
                        assert linked.get('subject') == expected.get('subject')
                        role = expected_role(linked)
                        pages = expected_pages(linked)
                        assert role in {'question', 'explanation'}
                        allowed_pages = set(cue_source_pages) | set(entry.get('reviewedVisualPages', []))
                        assert pages and set(pages).issubset(allowed_pages)
                    cue_visual_links[entry['id']] = visual_reference_ids
                cue_row.update({
                    'status': ('SOURCE_REVIEWED_NO_VISUAL' if entry['status'] == 'NO_SOURCE_VISUAL'
                               else 'VISUAL_REFERENCE_REQUIRED'),
                    'sourcePages': cue_source_pages,
                    'reviewReason': entry['reason'],
                    'reviewEvidence': entry['evidence'],
                })
            cue_rows.append(cue_row)
            continue

        row = {
            'id': expected.get('id'),
            'questionId': expected.get('questionId'),
            'subject': expected.get('subject'),
            'role': expected_role(expected),
            'order': expected_order(expected),
            'sourcePages': list(expected_pages(expected)),
            'nativeCandidateCount': len(expected.get('candidateImages', [])),
        }
        if expected.get('sourceOrigin'):
            row['sourceOrigin'] = expected['sourceOrigin']

        adjudication = adjudication_for(expected, adjudications)
        if adjudication:
            matched_adjudications.add(adjudication['id'])
            row.update({
                'coverageStatus': ADJUDICATION_STATUS,
                'released': False,
                'adjudicationReason': adjudication['reason'],
                'adjudicationEvidence': adjudication['evidence'],
            })
            rows.append(row)
            continue

        candidates = []
        reviewed_expected = reviewed_reference(expected, audit, page_reviews)
        if reviewed_expected is not expected:
            row['reviewedSourcePages'] = list(expected_pages(reviewed_expected))
        for asset, binding in actual_by_question.get(expected.get('questionId'), []):
            key = (asset.get('id'), binding.get('questionId'), binding.get('role'), binding.get('order'), actual_page(asset, binding))
            if key in used:
                continue
            score = match_score(reviewed_expected, asset, binding)
            if score is not None:
                candidates.append((score, key, asset, binding))
        candidates.sort(key=lambda candidate: (-candidate[0], str(candidate[2].get('id'))))

        matched = candidates[0] if candidates else None
        if matched:
            _, key, asset, binding = matched
            used.add(key)
            binding_status = binding.get('status', asset.get('status'))
            row.update({
                'assetId': asset.get('id'),
                'bindingStatus': binding_status,
                'assetStatus': asset.get('status'),
                'released': bool(binding_is_released(asset, binding)),
                'registryPage': actual_page(asset, binding),
            })
            row['coverageStatus'] = 'RELEASED' if row['released'] else 'UNRELEASED_TRACKED'
        else:
            row['coverageStatus'] = 'UNTRACKED_SOURCE_VISUAL'
            row['released'] = False
        rows.append(row)

    declared_adjudications = {entry['id'] for entry in adjudications.get('entries', [])}
    reviewed_ids = [entry['id'] for entry in page_reviews.get('entries', [])]
    assert len(reviewed_ids) == len(set(reviewed_ids)), 'Duplicate source-page review'
    assert set(reviewed_ids).issubset({row['id'] for row in rows}), 'Orphan source-page review'
    assert not set(reviewed_ids) & declared_adjudications, 'Conflicting page review and invalid metadata'
    unmatched_adjudications = sorted(declared_adjudications - matched_adjudications)
    if unmatched_adjudications:
        raise AssertionError('Source-reference adjudication no longer matches audit: ' + ', '.join(unmatched_adjudications))
    declared_cue_reviews = {entry['id'] for entry in cue_reviews.get('entries', [])}
    unmatched_cue_reviews = sorted(declared_cue_reviews - matched_cue_reviews)
    if unmatched_cue_reviews:
        raise AssertionError('Text-cue review no longer matches audit: ' + ', '.join(unmatched_cue_reviews))
    source_rows_by_id = {row.get('id'): row for row in rows}
    cue_rows_by_id = {row.get('id'): row for row in cue_rows}
    for cue_id, reference_ids in cue_visual_links.items():
        linked_rows = [source_rows_by_id.get(reference_id) for reference_id in reference_ids]
        assert all(linked_rows), f'Text-cue source reference is missing from coverage: {cue_id}'
        cue_rows_by_id[cue_id]['linkedReferenceIds'] = reference_ids
        if all(row.get('coverageStatus') == 'RELEASED' for row in linked_rows):
            cue_rows_by_id[cue_id]['status'] = 'SOURCE_VISUALS_RELEASED'

    subject_summary = {}
    for subject in SUBJECTS:
        subject_rows = [row for row in rows if row.get('subject') == subject]
        subject_cues = [row for row in cue_rows if row.get('subject') == subject
                        and row['status'] not in {'SOURCE_REVIEWED_NO_VISUAL', 'SOURCE_VISUALS_RELEASED'}]
        released = sum(row['coverageStatus'] == 'RELEASED' for row in subject_rows)
        invalid = sum(row['coverageStatus'] == ADJUDICATION_STATUS for row in subject_rows)
        tracked_unreleased = sum(row['coverageStatus'] == 'UNRELEASED_TRACKED' for row in subject_rows)
        untracked = sum(row['coverageStatus'] == 'UNTRACKED_SOURCE_VISUAL' for row in subject_rows)
        resolved = released + invalid
        subject_summary[subject] = {
            'sourceVisualReferences': len(subject_rows),
            'effectiveLearnerVisualReferences': len(subject_rows) - invalid,
            'additionalCueDerivedVisualReferences': sum(row.get('sourceOrigin') == 'TEXT_CUE_REVIEW' for row in subject_rows),
            'additionalCompletenessReviewVisualReferences': sum(row.get('sourceOrigin') == 'QUESTION_COMPLETENESS_REVIEW' for row in subject_rows),
            'releasedSourceVisualReferences': released,
            'invalidSourceMetadataReferences': invalid,
            'resolvedSourceVisualReferences': resolved,
            'trackedButUnreleasedReferences': tracked_unreleased,
            'untrackedSourceVisualReferences': untracked,
            'textCueReviewItems': len(subject_cues),
            'sourceVisualCoverageComplete': bool(subject_rows) and resolved == len(subject_rows),
            'humanCompletenessClaimAllowed': bool(subject_rows) and resolved == len(subject_rows) and not subject_cues,
        }

    return {
        'schemaVersion': 2,
        'definition': 'Coverage denominator is source-recorded visual references from the Marrow audit. A reference is resolved only by a released binding or an exact evidence-backed SOURCE_METADATA_INVALID adjudication.',
        'summary': subject_summary,
        'sourceVisuals': rows,
        'textCueReview': cue_rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, default=AUDIT_PATH)
    parser.add_argument('--registry', type=Path, default=DATA / 'images/registry.json')
    parser.add_argument('--adjudications', type=Path, default=DEFAULT_ADJUDICATIONS)
    parser.add_argument('--cue-reviews', type=Path, default=DEFAULT_CUE_REVIEWS)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--subject', choices=SUBJECTS)
    parser.add_argument('--require-complete', action='store_true', help='Fail unless every source visual is released or explicitly invalid and no cue backlog remains.')
    args = parser.parse_args()

    if not args.audit.exists():
        raise SystemExit('Marrow image audit missing; run: python3 tools/marrow_images.py audit')
    audit = json.loads(args.audit.read_text())
    registry = validate(args.registry)
    adjudications = load_adjudications(args.adjudications)
    cue_reviews = load_cue_reviews(args.cue_reviews)
    coverage = build_coverage(audit, registry, adjudications, cue_reviews,
                              load_page_reviews(DEFAULT_PAGE_REVIEWS),
                              load_page_reviews(DEFAULT_DISCOVERY_REVIEWS),
                              questions())
    rendered = json.dumps(coverage, indent=2, sort_keys=False) + '\n'

    if args.check:
        if not args.output.exists() or args.output.read_text() != rendered:
            raise SystemExit('Marrow image coverage report is stale; regenerate it before continuing')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)

    if args.subject:
        summary = coverage['summary'][args.subject]
        print('MARROW_IMAGE_COVERAGE', args.subject, json.dumps(summary, sort_keys=True))
        if args.require_complete and not summary['humanCompletenessClaimAllowed']:
            raise SystemExit(
                f"{args.subject} learner-image coverage is incomplete: "
                f"resolved={summary['resolvedSourceVisualReferences']}/"
                f"{summary['sourceVisualReferences']} "
                f"released={summary['releasedSourceVisualReferences']} "
                f"invalid_metadata={summary['invalidSourceMetadataReferences']} "
                f"tracked_unreleased={summary['trackedButUnreleasedReferences']} "
                f"untracked={summary['untrackedSourceVisualReferences']} "
                f"text_cues={summary['textCueReviewItems']}"
            )
    else:
        print(json.dumps(coverage['summary'], indent=2))


if __name__ == '__main__':
    main()
