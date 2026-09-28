#!/usr/bin/env python3
"""Prepare a chapter-bounded source-region review checkpoint for Ubuntu CI."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

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
        if candidates:
            for index, candidate in enumerate(candidates, 1):
                items.append({
                    'referenceId': ref['id'], 'questionId': ref['questionId'],
                    'role': audited.get('metadata', {}).get('role'),
                    'page': candidate['page'], 'xref': candidate.get('xref'),
                    'region': candidate['region'], 'candidateIndex': index,
                    'candidateCount': len(candidates), 'method': 'region-render',
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
                'role': audited.get('metadata', {}).get('role'),
                'page': ref['sourcePages'][0], 'xref': None,
                'region': [float(rect.x0), float(rect.y0), float(rect.x1), float(rect.y1)],
                'candidateIndex': 1, 'candidateCount': 0,
                'method': 'region-render', 'coverageStatus': ref['coverageStatus'],
            })
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
    print(f"MARROW_MANUAL_CHECKPOINT_OK refs={len({x['referenceId'] for x in items})} renders={len(items)} output={output}")


if __name__ == '__main__':
    main()
