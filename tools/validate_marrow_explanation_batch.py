#!/usr/bin/env python3
"""Validate worker-owned batches before global inventory reconciliation."""
import argparse
import hashlib
import json
from pathlib import Path

from apply_canonical_bank_explanation_wiring_v1 import canonical_source_questions, validate_augmented_question
from test_marrow_explanation_refinement_wave import validate_source_retention

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--base-sha', required=True)
    args = parser.parse_args()
    sources = canonical_source_questions()
    queue = json.loads((ROOT / 'data/marrow/explanation_refinement_queue_20261001.json').read_text())
    protected = set(queue['baselineEnhancedIds']) | {qid for lane in queue['subjects'].values() for qid in lane['blockedIds']}
    seen, paths, errors = set(), [], []
    for path in sorted((args.root / 'data/marrow').glob('explanation*_v1.json')):
        record = json.loads(path.read_text())
        scope, questions = record.get('scope', {}), record.get('questions', {})
        if scope.get('canonicalBaseSha') != args.base_sha:
            continue
        assert scope['bank'] == 'Marrow' and scope['status'] == 'approved-rollout', path.name
        assert scope['questions'] == len(questions), path.name
        assert 0 < len(questions) <= (14 if scope['subject'] == 'Anatomy' else 18), path.name
        assert set(questions).isdisjoint(protected | seen), path.name
        for qid, cfg in questions.items():
            try:
                source = sources[qid]
                assert source['subject'] == scope['subject'] and str(source['chapterId']) == str(scope['chapterId']), qid
                assert scope['questionStart'] <= source['questionNumber'] <= scope['questionEnd'], qid
                validate_augmented_question(qid, cfg, source, path.name)
                validate_source_retention(qid, source, cfg)
                reconstruction = cfg.get('reconstruction')
                if reconstruction:
                    assert reconstruction['status'] in {'resolved_reconstruction', 'needs_manual_review', 'contextually_reconstructed'}, qid
                    assert all(reconstruction.get(k) for k in ('sourceProblem', 'reconstructedContent', 'evidenceBasis', 'reviewNote')), qid
                if 'displayTables' in cfg:
                    reconstruction = cfg['reconstruction']
                    assert reconstruction['status'] == 'resolved_reconstruction', qid
                    pdf = args.root / reconstruction['sourcePdf']
                    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == reconstruction['sourcePdfSha256'], qid
                    assert all(table['source_page'] in reconstruction['sourcePages'] for table in cfg['displayTables']), qid
            except (AssertionError, KeyError, SystemExit) as error:
                errors.append(f'{qid}: {error}')
        seen.update(questions)
        paths.append(path)
    assert paths, 'No authored batches at requested base'
    if errors:
        raise SystemExit('MARROW_WORKER_BATCHES_FAILED:\n' + '\n'.join(errors))
    print(f'MARROW_WORKER_BATCHES_OK files={len(paths)} questions={len(seen)} source_keyed=true detail_retention=true baseline_and_gates_preserved=true')


if __name__ == '__main__':
    main()
