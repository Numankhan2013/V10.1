#!/usr/bin/env python3
"""Fail-closed coverage audit for learner-facing Marrow source visuals.

Coverage uses two independent denominators:
1) source-recorded visual references retained in the normalized bank; and
2) every non-background PDF image placement on canonical question/solution pages.
A subject is learner-image complete only when both gates are fully accounted for.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, Counter
import json
from pathlib import Path
import re

from marrow_images import DATA, ROOT, binding_is_released, validate, questions, RELEASE_STATUSES
from marrow_visual_inventory import source_image_occurrences

AUDIT_PATH = ROOT / 'build/marrow-images/audit.json'
DEFAULT_OUTPUT = DATA / 'images/coverage.json'
SUBJECTS = ('Anatomy', 'Biochemistry', 'Physiology')


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


def build_coverage(audit, registry):
    """Preserve the existing source-reference coverage gate."""
    actual_by_question = defaultdict(list)
    for asset in registry['assets']:
        for binding in asset.get('bindings', []):
            actual_by_question[binding.get('questionId')].append((asset, binding))

    used = set()
    rows = []
    cue_rows = []
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

        candidates = []
        for asset, binding in actual_by_question.get(expected.get('questionId'), []):
            key = (asset.get('id'), binding.get('questionId'), binding.get('role'), binding.get('order'), actual_page(asset, binding))
            if key in used:
                continue
            score = match_score(expected, asset, binding)
            if score is not None:
                candidates.append((score, key, asset, binding))
        candidates.sort(key=lambda row: (-row[0], str(row[2].get('id'))))

        matched = candidates[0] if candidates else None
        row = {
            'id': expected.get('id'),
            'questionId': expected.get('questionId'),
            'subject': expected.get('subject'),
            'role': expected_role(expected),
            'order': expected_order(expected),
            'sourcePages': list(expected_pages(expected)),
            'nativeCandidateCount': len(expected.get('candidateImages', [])),
        }
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

    subject_summary = {}
    for subject in SUBJECTS:
        subject_rows = [row for row in rows if row.get('subject') == subject]
        subject_cues = [row for row in cue_rows if row.get('subject') == subject]
        released = sum(row['coverageStatus'] == 'RELEASED' for row in subject_rows)
        tracked_unreleased = sum(row['coverageStatus'] == 'UNRELEASED_TRACKED' for row in subject_rows)
        untracked = sum(row['coverageStatus'] == 'UNTRACKED_SOURCE_VISUAL' for row in subject_rows)
        subject_summary[subject] = {
            'sourceVisualReferences': len(subject_rows),
            'releasedSourceVisualReferences': released,
            'trackedButUnreleasedReferences': tracked_unreleased,
            'untrackedSourceVisualReferences': untracked,
            'textCueReviewItems': len(subject_cues),
            'sourceVisualCoverageComplete': bool(subject_rows) and released == len(subject_rows),
            'humanCompletenessClaimAllowed': bool(subject_rows) and released == len(subject_rows) and not subject_cues,
        }

    return {
        'schemaVersion': 1,
        'definition': 'Coverage denominator includes source-recorded references; PDF placement coverage is layered on by augment_with_pdf_placements().',
        'summary': subject_summary,
        'sourceVisuals': rows,
        'textCueReview': cue_rows,
    }


def _region(value):
    return tuple(round(float(x), 3) for x in (value or []))


def _registry_rows(registry):
    rows=[]
    for asset in registry.get('assets', []):
        asset_status=asset.get('status','REVIEW_REQUIRED')
        asset_source=asset.get('source') or {}
        for binding in asset.get('bindings', []):
            source=binding.get('source') or asset_source
            rows.append({
                'subject':asset.get('subject'),
                'questionId':binding.get('questionId'),
                'role':binding.get('role','explanation'),
                'page':source.get('page'),
                'xref':source.get('xref'),
                'region':_region(source.get('region')),
                'assetId':asset.get('id'),
                'assetStatus':asset_status,
                'bindingStatus':binding.get('status',asset_status),
            })
    return rows


def _classify_occurrence(occurrence, rows):
    owner_keys={(o['questionId'],o['role']) for o in occurrence.get('candidateOwners',[])}
    region=_region(occurrence.get('region'))
    matches=[r for r in rows if
             r['subject']==occurrence['subject'] and
             r.get('page')==occurrence.get('page') and
             r.get('xref')==occurrence.get('xref') and
             r.get('region')==region and
             (not owner_keys or (r['questionId'],r['role']) in owner_keys)]
    if not matches:
        return 'UNACCOUNTED', []
    released=[r for r in matches if r['assetStatus'] in RELEASE_STATUSES and r['bindingStatus'] in RELEASE_STATUSES]
    if released:
        return 'RELEASED', released
    rejected=[r for r in matches if r['bindingStatus']=='REJECTED' or r['assetStatus']=='REJECTED']
    if rejected:
        return 'REJECTED', rejected
    return 'REVIEW_REQUIRED', matches


def build_pdf_placement_coverage(audit, registry, subject=None):
    qmap=questions()
    rows=_registry_rows(registry)
    occurrences=source_image_occurrences(audit,qmap,subject)
    results=[]
    for occurrence in occurrences:
        status,matches=_classify_occurrence(occurrence,rows)
        results.append({**occurrence,'coverageStatus':status,
            'registryMatches':[{'assetId':m['assetId'],'questionId':m['questionId'],'role':m['role'],
                                'assetStatus':m['assetStatus'],'bindingStatus':m['bindingStatus']} for m in matches]})
    summary={}
    for name in SUBJECTS:
        subset=[r for r in results if r['subject']==name]
        counts=Counter(r['coverageStatus'] for r in subset)
        summary[name]={
            'sourceImagePlacements':len(subset),
            'uniqueSourceImageStreams':len({r['streamSha256'] for r in subset}),
            'releasedPlacements':counts.get('RELEASED',0),
            'reviewRequiredPlacements':counts.get('REVIEW_REQUIRED',0),
            'rejectedPlacements':counts.get('REJECTED',0),
            'unaccountedPlacements':counts.get('UNACCOUNTED',0),
            'sourcePlacementCoverageComplete':bool(subset) and counts.get('UNACCOUNTED',0)==0,
        }
    return {'summary':summary,'placements':results}


def augment_with_pdf_placements(coverage, audit, registry, subject=None):
    placement=build_pdf_placement_coverage(audit,registry,subject)
    coverage['schemaVersion']=2
    coverage['definition']='Completion requires both source-recorded reference coverage and source-PDF image-placement coverage.'
    coverage['sourceImagePlacements']=placement['placements']
    for name in SUBJECTS:
        coverage['summary'][name].update(placement['summary'][name])
        coverage['summary'][name]['humanCompletenessClaimAllowed'] = bool(
            coverage['summary'][name]['humanCompletenessClaimAllowed'] and
            placement['summary'][name]['sourcePlacementCoverageComplete']
        )
    return coverage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, default=AUDIT_PATH)
    parser.add_argument('--registry', type=Path, default=DATA / 'images/registry.json')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--subject', choices=SUBJECTS)
    parser.add_argument('--require-complete', action='store_true', help='Fail unless both source-reference and PDF-placement coverage are complete.')
    args = parser.parse_args()

    if not args.audit.exists():
        raise SystemExit('Marrow image audit missing; run: python3 tools/marrow_images.py audit')
    audit = json.loads(args.audit.read_text())
    registry = validate(args.registry)
    coverage = augment_with_pdf_placements(build_coverage(audit, registry), audit, registry, args.subject)
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
                f"refs_released={summary['releasedSourceVisualReferences']}/{summary['sourceVisualReferences']} "
                f"refs_untracked={summary['untrackedSourceVisualReferences']} cues={summary['textCueReviewItems']} "
                f"placements_released={summary['releasedPlacements']}/{summary['sourceImagePlacements']} "
                f"placements_review={summary['reviewRequiredPlacements']} "
                f"placements_rejected={summary['rejectedPlacements']} "
                f"placements_unaccounted={summary['unaccountedPlacements']}"
            )
    else:
        print(json.dumps(coverage['summary'], indent=2))


if __name__ == '__main__':
    main()
