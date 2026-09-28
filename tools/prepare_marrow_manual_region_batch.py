#!/usr/bin/env python3
"""Prepare a chapter-bounded source-region review checkpoint for Ubuntu CI."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/marrow'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--subject', choices=['Biochemistry', 'Physiology'], required=True)
    parser.add_argument('--start-chapter', type=int, required=True)
    parser.add_argument('--end-chapter', type=int, required=True)
    parser.add_argument('--batch-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert 1 <= args.start_chapter <= args.end_chapter

    audit = json.loads((ROOT / 'build/marrow-images/audit.json').read_text())
    coverage = json.loads((DATA / 'images/coverage.json').read_text())
    source = audit['sources'][args.subject]
    pdf_path = DATA / 'source_pdfs' / source['file']
    source_hash = source['sha256']
    binding_by_id = {row['id']: row for row in audit['bindings']}
    sys.path.insert(0, str(ROOT / 'tools'))
    from marrow_images import questions
    qmap = questions()
    items = []
    for ref in coverage['sourceVisuals']:
        if ref['subject'] != args.subject or ref['released']:
            continue
        if ref['coverageStatus'] == 'SOURCE_METADATA_INVALID':
            continue
        match = re.search(r'_CH(\d+)_', ref['questionId'])
        if not match or not args.start_chapter <= int(match.group(1)) <= args.end_chapter:
            continue
        audited = binding_by_id.get(ref['id'])
        if not audited:
            raise AssertionError(f"Missing source audit row for {ref['id']}")
        candidates = audited.get('candidateImages') or []
        q = qmap[ref['questionId']]
        metadata = audited.get('metadata') or {}
        if candidates:
            # Candidate XObjects are often tiles of one source figure. Render
            # their union on each cited page so review sees intact source layout.
            by_page = {}
            for candidate in candidates:
                by_page.setdefault(candidate['page'], []).append(candidate)
            for index, (page_number, page_candidates) in enumerate(sorted(by_page.items()), 1):
                regions = [candidate['region'] for candidate in page_candidates]
                region = [min(r[0] for r in regions), min(r[1] for r in regions),
                          max(r[2] for r in regions), max(r[3] for r in regions)]
                import fitz
                with fitz.open(pdf_path) as document:
                    page_rect = document[page_number - 1].rect
                region = [max(float(page_rect.x0), region[0] - 12),
                          max(float(page_rect.y0), region[1] - 28),
                          min(float(page_rect.x1), region[2] + 12),
                          min(float(page_rect.y1), region[3] + 28)]
                items.append({
                    'referenceId': ref['id'], 'questionId': ref['questionId'],
                    'role': metadata.get('role'), 'metadataTitle': metadata.get('title'),
                    'questionText': q.get('question'), 'explanationText': q.get('explanation'),
                    'page': page_number,
                    'xrefs': [candidate.get('xref') for candidate in page_candidates],
                    'region': region, 'candidateIndex': index,
                    'candidateCount': len(by_page), 'candidateObjectCount': len(page_candidates),
                    'method': 'region-render', 'dpi': 300,
                    'coverageStatus': ref['coverageStatus'],
                })
        else:
            # A full source page is needed to determine whether metadata is false
            # or whether the figure is page content without a native image stream.
            import fitz
            with fitz.open(pdf_path) as document:
                page = document[int(ref['sourcePages'][0]) - 1]
                rect = page.rect
            items.append({
                'referenceId': ref['id'], 'questionId': ref['questionId'],
                'role': metadata.get('role'), 'metadataTitle': metadata.get('title'),
                'questionText': q.get('question'), 'explanationText': q.get('explanation'),
                'page': ref['sourcePages'][0], 'xref': None,
                'region': [float(rect.x0), float(rect.y0), float(rect.x1), float(rect.y1)],
                'candidateIndex': 1, 'candidateCount': 0,
                'method': 'region-render', 'dpi': 300, 'coverageStatus': ref['coverageStatus'],
            })
    cue_contexts = {}
    for cue in coverage['textCueReview']:
        if cue['subject'] != args.subject:
            continue
        match = re.search(r'_CH(\d+)_', cue['questionId'])
        if not match or not args.start_chapter <= int(match.group(1)) <= args.end_chapter:
            continue
        q = qmap[cue['questionId']]
        provenance = q.get('provenance') or {}
        pages = sorted(set((provenance.get('questionPages') or []) +
                           (provenance.get('explanationPages') or [])))
        for page_number in pages:
            key = (args.subject, page_number)
            item = cue_contexts.get(key)
            if item is None:
                page_data = source['pages'][page_number - 1]
                item = {
                    'referenceId': f"source-context:{args.subject}:page:{page_number}",
                    'questionId': cue['questionId'], 'questionIds': [],
                    'cueIds': [], 'role': 'text-cue-review',
                    'page': page_number, 'xref': None,
                    'region': [0.0, 0.0, page_data['width'], page_data['height']],
                    'candidateIndex': 1, 'candidateCount': 0,
                    'method': 'region-render', 'dpi': 144,
                }
                cue_contexts[key] = item
            if cue['questionId'] not in item['questionIds']:
                item['questionIds'].append(cue['questionId'])
            if cue['id'] not in item['cueIds']:
                item['cueIds'].append(cue['id'])
    items.extend(cue_contexts[key] for key in sorted(cue_contexts))
    checkpoint = {
        'schemaVersion': 1, 'batchId': args.batch_id,
        'subject': args.subject, 'sourceFile': source['file'],
        'sourceSha256': source_hash,
        'chapterRange': [args.start_chapter, args.end_chapter],
        'items': items,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checkpoint, indent=2) + '\n')
    print(f"MARROW_MANUAL_CHECKPOINT_OK refs={len({x['referenceId'] for x in items})} renders={len(items)} textCuePages={len(cue_contexts)} output={output}")


if __name__ == '__main__':
    main()
