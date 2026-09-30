#!/usr/bin/env python3
"""Validate a reviewed multi-subject wave without changing immutable source."""
import hashlib
import json
from pathlib import Path

from inventory_marrow_explanations import BANKS, DATA, enhanced_ids, load_sharded

ROOT = DATA.parents[1]
MANIFEST = DATA / 'explanation_refinement_wave_20260930.json'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def load_wave():
    manifest = json.loads(MANIFEST.read_text())
    sources, hashes = {}, {}
    for subject, prefix in BANKS.items():
        bank, hashes[subject] = load_sharded(prefix)
        sources.update({q['id']: q for q in bank['questions']})
    assert hashes == manifest['sourceRawSha256'], 'Immutable source changed'
    gate_path = ROOT / 'data/question_completeness_reviews_v1.json'
    assert hashlib.sha256(gate_path.read_bytes()).hexdigest() == manifest['completenessLedgerSha256'], 'Source omission/answer guards changed'
    gates = {e['id']: e for e in json.loads(gate_path.read_text())['entries']}
    for qid in manifest.get('withheldSourceLimitedIds', []):
        assert gates[qid]['display'].get('blocked'), 'Source-limited question is not gated: ' + qid
    wave = {}
    for spec in manifest['batches']:
        record = json.loads((DATA / spec['file']).read_text())
        scope, questions = record['scope'], record['questions']
        assert scope['status'] == 'approved-rollout', spec['file']
        assert scope['canonicalBaseSha'] == manifest['canonicalBaseSha'], spec['file']
        assert digest(questions) == spec['questionsSha256'], 'Reviewed augmentation changed: ' + spec['file']
        assert len(questions) == scope['questions'] == spec['count'], spec['file']
        assert set(questions) == set(spec['ids']), spec['file']
        assert not set(wave).intersection(questions), 'Duplicate wave ownership'
        assert (ROOT / spec['auditReport']).is_file(), 'Missing medical/source audit report'
        for qid, cfg in questions.items():
            source = sources[qid]
            assert source['subject'] == scope['subject'], qid
            assert str(source['chapterId']) == str(scope['chapterId']), qid
            assert scope['questionStart'] <= source['questionNumber'] <= scope['questionEnd'], qid
            assert digest(source) == spec['sourceQuestionSha256'][qid], 'Source ownership drift: ' + qid
            assert cfg.get('takeaway', '').strip() and cfg.get('displayText', '').strip(), qid
            assert 'sourceText' not in cfg, qid
            anchors = cfg.get('emphasis', [])
            assert 1 <= len(anchors) <= 4 and len(set(anchors)) == len(anchors), qid
            assert all(a.strip() and a in cfg['displayText'] for a in anchors), 'Invalid emphasis: ' + qid
            key = int(source['correctOption'])
            assert len(source['options']) == 4 and key in (1, 2, 3, 4), qid
            wrong = {str(o.get('letter') or chr(64 + i)).lower()
                     for i, o in enumerate(source['options'], 1) if i != key}
            assert set(cfg.get('rationales', {})) == wrong, 'Wrong-option mapping: ' + qid
            assert all(reason.strip() for reason in cfg['rationales'].values()), qid
            reconstruction = cfg.get('reconstruction')
            if reconstruction:
                assert reconstruction['status'] in {'resolved_reconstruction', 'needs_manual_review', 'contextually_reconstructed'}, qid
                assert all(reconstruction.get(k) for k in ('sourceProblem', 'reconstructedContent', 'evidenceBasis', 'reviewNote')), qid
            if 'displayTables' in cfg:
                assert reconstruction and reconstruction['status'] == 'resolved_reconstruction', 'Unreviewed table reconstruction: ' + qid
                native = source.get('structuredExplanation', {}).get('tables', [])
                assert len(cfg['displayTables']) == len(native), 'Native table ownership changed: ' + qid
                for table, original in zip(cfg['displayTables'], native):
                    assert table['source_page'] == original['source_page'], qid
                    assert table['source_page'] in reconstruction['sourcePages'], 'Reviewed source page not recorded: ' + qid
                    pdf = ROOT / reconstruction['sourcePdf']
                    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == reconstruction['sourcePdfSha256'], 'Reviewed PDF changed: ' + qid
                    assert table.get('columns') and table.get('rows'), 'Empty reconstructed table: ' + qid
                    assert all(isinstance(label, str) and label.strip() for label in table['columns']), qid
                    assert all(len(row) == len(table['columns']) and all(isinstance(cell, str) and cell.strip() for cell in row) for row in table['rows']), qid
            wave[qid] = cfg
    baseline = set(manifest['baselineEnhancedIds'])
    current = enhanced_ids()
    assert len(baseline) == 670 and baseline.isdisjoint(wave), 'Duplicate historical enhancement'
    assert current == baseline | set(wave), 'Enhanced-set dropped or gained unreviewed IDs'
    assert len(wave) == manifest['newEnhancedCount'], 'Wave count drift'
    assert not set(manifest.get('withheldSourceLimitedIds', [])).intersection(wave), 'Incomplete question counted as refined'
    for spec in manifest.get('existingRepairs', []):
        record = json.loads((DATA / spec['file']).read_text())
        assert digest(record['questions']) == spec['questionsSha256'], spec['file']
        assert (ROOT / spec['auditReport']).is_file(), spec['file']
        assert len(spec['ids']) == spec['count'], spec['file']
        for qid in spec['ids']:
            assert qid in baseline and qid not in wave, 'Existing repair counted twice: ' + qid
            cfg = record['questions'][qid]
            assert digest(sources[qid]) == spec['sourceQuestionSha256'][qid], qid
            assert digest({k: v for k, v in cfg.items() if k != 'emphasis'}) == spec['preservedContentSha256'][qid], 'Emphasis-only repair changed content: ' + qid
            anchors = cfg['emphasis']
            assert 1 <= len(anchors) <= 4 and all(a.strip() and a in cfg['displayText'] for a in anchors), qid
            wave[qid] = cfg
    return manifest, sources, wave


def main():
    manifest, _, wave = load_wave()
    new = manifest['newEnhancedCount']
    print(f'MARROW_EXPLANATION_REFINEMENT_WAVE_OK new={new} existing_repairs={len(wave)-new} total={670+new} batches={len(manifest["batches"])} source_pinned=true gates_unchanged=true emphasis=verbatim distractors=source_keyed')


if __name__ == '__main__':
    main()
