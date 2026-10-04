"""Protect native source imports, incomplete-source gates and collection boundaries."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import uworld_male_reproductive as male
import uworld_female_reproductive as female
from uworld_collections import bank_records
from uworld_reviewed_document import figures, record_hash, load_reviewed


def main():
    all_ids = []
    for module, count in [(male, 52), (female, 81)]:
        manifest, rows = module.load_source()
        frozen = deepcopy(rows)
        docs, bank = module.reviewed_documents(rows), module.bank_record()
        assert len(rows) == len(docs) == len(bank['questions']) == count
        assert rows == frozen and len(bank['topics']) == 2
        assert manifest['source_repository_commit'] == '56fe81724f120b5b6d5277a82e418714278c1493'
        pdf = module.PDF.read_bytes()
        assert ('oid sha256:' + module.PDF_SHA).encode() in pdf or hashlib.sha256(pdf).hexdigest() == module.PDF_SHA
        for row, q in zip(rows, bank['questions']):
            doc = docs[q['id']]
            assert q['subject'] == bank['subject'] and q['collection'] == bank['collection']
            assert q['provenance']['sourceRecordSha256'] == record_hash(row)
            assert doc['reviewed_pages'] == row['source']['source_pages']
            assert doc['correct_label'] == row['correct_option'].upper()
            assert q['uworldPilot']['requiresVisual'] == (doc['status'] == 'blocked')
            assert doc['educational_objective'] and doc['explanation']
            for o in doc['options']:
                assert o['selection_percent'] == doc['statistics']['selection_percent'][o['letter']]
                original = next(x for x in row['options'] if x['label'].upper() == o['letter'])
                if original['selection_percent'] is not None:
                    assert o['selection_percent'] == original['selection_percent']
            assert all(n['page'] in doc['reviewed_pages'] for n in figures(doc))
            all_ids.append(q['id'])
        # Incomplete reviews and changed fingerprints must stop installation.
        for mutate in [lambda d: d.update(status='draft'), lambda d: d['reviewed_pages'].pop(),
                       lambda d: d.update(source_record_sha256='0' * 64)]:
            bad = deepcopy(next(iter(docs.values())))
            mutate(bad)
            with tempfile.TemporaryDirectory() as td:
                Path(td, 'batch-01.json').write_text(json.dumps({'schema_version': 1,
                    'source_pdf_sha256': module.PDF_SHA, 'records': [bad]}))
                try:
                    load_reviewed(rows, module.PDF_SHA, td, module.PAGE_SIZE)
                except ValueError:
                    pass
                else:
                    raise AssertionError('Unreviewed or changed source document accepted')
    banks = bank_records()
    assert len(banks) == 6 and len(all_ids) == len(set(all_ids)) == 133
    ids = [q['id'] for bank in banks for q in bank['questions']]
    assert len(ids) == len(set(ids)) == 338
    _, rows = male.load_source()
    assert [r['question_number'] for r in rows if r['block_number'] == 1] == list(range(1, 40))
    assert all(male.reviewed_documents()[f'UWORLD_{id}']['statistics']['selection_percent'][
               male.reviewed_documents()[f'UWORLD_{id}']['correct_label']] is None for id in [343, 580, 839, 11762])
    _, rows = female.load_source()
    duplicate_item = [r['uworld_question_id'] for r in rows if r['block_number'] == 1 and r['question_number'] == 40]
    assert set(duplicate_item) == {'18714', '127'}
    repaired = next(r for r in rows if r['question_id'] == 'UWORLD_1830')
    assert len(repaired['options']) == 6 and repaired['correct_option'] == 'a'
    assert repaired['options'][2]['text'] == '47,XXX'
    assert repaired['options'][4] == {'label': 'e', 'text': '69,XXX', 'selection_percent': 9}
    assert repaired['options'][5] == {'label': 'f', 'text': '69,XXY', 'selection_percent': 20}
    print('UWORLD_IMPORTED_COLLECTIONS_OK collections=2 questions=133 blocks=4 raw_source_preserved=true')


if __name__ == '__main__':
    main()
