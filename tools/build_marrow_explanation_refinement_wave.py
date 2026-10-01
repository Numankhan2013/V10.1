#!/usr/bin/env python3
"""Pin a user-directed refinement wave to its resume queue and reviewed files."""
import argparse
import hashlib
import json
from pathlib import Path

from inventory_marrow_explanations import BANKS, DATA, enhanced_ids, load_sharded
from test_marrow_explanation_refinement_wave import digest

ROOT = DATA.parents[1]


def build(queue_path):
    queue = json.loads(queue_path.read_text())
    ledger_hash = hashlib.sha256((ROOT / 'data/question_completeness_reviews_v1.json').read_bytes()).hexdigest()
    released_wave = json.loads((DATA / 'explanation_refinement_wave_20260930.json').read_text())
    assert ledger_hash == released_wave['completenessLedgerSha256'], 'Released source omission/answer guards changed'
    baseline = set(queue['baselineEnhancedIds'])
    sources, hashes = {}, {}
    for subject, prefix in BANKS.items():
        bank, hashes[subject] = load_sharded(prefix)
        assert hashes[subject] == queue['subjects'][subject]['sourceRawSha256']
        sources.update({q['id']: q for q in bank['questions']})
    deferred = sorted(qid for lane in queue['subjects'].values() for qid in lane['blockedIds'])
    batches, new = [], set()
    audit_names = {'Anatomy': 'anatomy', 'Biochemistry': 'biochemistry', 'Physiology': 'physiology'}
    for pattern in ('explanation_anatomy_ch*_v1.json', 'explanation_biochem_*_v1.json', 'explanation_physio_ch*_v1.json'):
        for path in sorted(DATA.glob(pattern)):
            record = json.loads(path.read_text())
            scope, questions = record['scope'], record['questions']
            if scope.get('canonicalBaseSha') != queue['canonicalBaseSha']:
                continue
            assert scope['status'] == 'approved-rollout', path.name
            ids = set(questions)
            assert ids.isdisjoint(baseline | new | set(deferred)), path.name
            assert 0 < len(ids) <= (14 if scope['subject'] == 'Anatomy' else 18), path.name
            assert ids <= set(sources), path.name
            audit = scope.get('auditReport', f'docs/question-explanations/{audit_names[scope["subject"]]}-remaining-20261001.md')
            assert (ROOT / audit).is_file(), audit
            # The longest source and every table owner are exercised by browser QA.
            representative = max(ids, key=lambda qid: len(sources[qid].get('explanation') or ''))
            batches.append({'file': path.name, 'count': len(ids), 'ids': sorted(ids),
                            'questionsSha256': digest(questions),
                            'sourceQuestionSha256': {qid: digest(sources[qid]) for qid in sorted(ids)},
                            'browserId': representative, 'auditReport': audit})
            new.update(ids)
    assert new, 'No newly authored batch files'
    assert enhanced_ids() == baseline | new, 'Unclaimed or duplicated enhancement'
    expected = set(sources) - baseline - set(deferred)
    unprocessed = sorted(expected - new)
    return {'schemaVersion': 1, 'purpose': 'Source-pinned continuation of the verified 753-question checkpoint.',
            'canonicalBaseSha': queue['canonicalBaseSha'], 'sourceRawSha256': hashes,
            'completenessLedgerSha256': ledger_hash,
            'baselineEnhancedIds': sorted(baseline), 'newEnhancedCount': len(new),
            'withheldSourceLimitedIds': deferred, 'unprocessedActionableIds': unprocessed,
            'queueFile': str(queue_path.relative_to(ROOT)), 'queueSha256': digest(queue),
            'batches': batches, 'existingRepairs': []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue', default='data/marrow/explanation_refinement_queue_20261001.json')
    parser.add_argument('--output', default='data/marrow/explanation_refinement_wave_20261001.json')
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    wave = build(ROOT / args.queue)
    if args.require_complete:
        assert not wave['unprocessedActionableIds'], f"Unprocessed actionable IDs: {len(wave['unprocessedActionableIds'])}"
    (ROOT / args.output).write_text(json.dumps(wave, ensure_ascii=False, indent=2) + '\n')
    print(f"MARROW_EXPLANATION_WAVE_PINNED new={wave['newEnhancedCount']} batches={len(wave['batches'])} deferred={len(wave['withheldSourceLimitedIds'])} unprocessed={len(wave['unprocessedActionableIds'])}")


if __name__ == '__main__':
    main()
