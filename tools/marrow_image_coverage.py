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

from marrow_images import DATA, ROOT, binding_is_released, validate

AUDIT_PATH = ROOT / 'build/marrow-images/audit.json'
DEFAULT_OUTPUT = DATA / 'images/coverage.json'
DEFAULT_ADJUDICATIONS = DATA / 'images/source_reference_adjudications.json'
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


def build_coverage(audit, registry, adjudications=None):
    adjudications = adjudications or {'schemaVersion': 1, 'entries': []}
    actual_by_question = defaultdict(list)
    for asset in registry['assets']:
        for binding in asset.get('bindings', []):
            actual_by_question[binding.get('questionId')].append((asset, binding))

    used = set()
    rows = []
    cue_rows = []
    matched_adjudications = set()
    for expected in audit.get('bindings', []):
        if not expected.get('metadata'):
            cue_rows.append({
                'id': expected.get('id'),
                'questionId': expected.get('questionId'),
                'subject': expected.get('subject'),
                'status': 'TEXT_CUE_REVIEW_REQUIRED',
                'reason': expected.get('reason', 'Text cue without source visual metadata'),
            })
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
        for asset, binding in actual_by_question.get(expected.get('questionId'), []):
            key = (asset.get('id'), binding.get('questionId'), binding.get('role'), binding.get('order'), actual_page(asset, binding))
            if key in used:
                continue
            score = match_score(expected, asset, binding)
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
    unmatched_adjudications = sorted(declared_adjudications - matched_adjudications)
    if unmatched_adjudications:
        raise AssertionError('Source-reference adjudication no longer matches audit: ' + ', '.join(unmatched_adjudications))

    subject_summary = {}
    for subject in SUBJECTS:
        subject_rows = [row for row in rows if row.get('subject') == subject]
        subject_cues = [row for row in cue_rows if row.get('subject') == subject]
        released = sum(row['coverageStatus'] == 'RELEASED' for row in subject_rows)
        invalid = sum(row['coverageStatus'] == ADJUDICATION_STATUS for row in subject_rows)
        tracked_unreleased = sum(row['coverageStatus'] == 'UNRELEASED_TRACKED' for row in subject_rows)
        untracked = sum(row['coverageStatus'] == 'UNTRACKED_SOURCE_VISUAL' for row in subject_rows)
        resolved = released + invalid
        subject_summary[subject] = {
            'sourceVisualReferences': len(subject_rows),
            'effectiveLearnerVisualReferences': len(subject_rows) - invalid,
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
    coverage = build_coverage(audit, registry, adjudications)
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
