"""Protect the bounded source scope, numerical matrices and reviewed formula repairs."""
import hashlib
import json
from copy import deepcopy
from uworld_biostatistics import OWNER, PDF, PDF_SHA, load_source, reviewed_documents, bank_record
from uworld_reviewed_document import figures, record_hash
from uworld_content_hygiene import validate_display


def main():
    manifest, rows = load_source()
    before = deepcopy(rows)
    docs, bank = reviewed_documents(rows), bank_record()
    assert len(rows) == len(docs) == len(bank['questions']) == 10
    assert manifest['source_pdf_total_pages'] == 548 and manifest['source_block_record_count'] == 40
    assert [r['question_number'] for r in rows] == list(range(1, 11))
    assert bank['topics'][0]['title'] == 'Block 1 · Questions 1–10'
    assert bank['topics'][0]['id'] == 'uworld_biostatistics_epidemiology_block_1'
    pdf = PDF.read_bytes()
    assert ('oid sha256:' + PDF_SHA).encode() in pdf or hashlib.sha256(pdf).hexdigest() == PDF_SHA
    originals = [json.loads(l) for l in (OWNER.SOURCE/'source'/manifest['original_jsonl']).read_text().splitlines()]
    assert len(originals) == 120
    for row, original, question in zip(rows, originals, bank['questions']):
        doc = docs[row['question_id']]
        assert row['source']['original_record_sha256'] == record_hash(original)
        assert doc['source_record_sha256'] == question['provenance']['sourceRecordSha256'] == record_hash(row)
        assert doc['correct_label'] == original['correct_option']
        assert doc['reviewed_pages'] == original['source']['source_pages']
        assert doc['status'] == 'verified' and doc['educational_objective']
        assert doc['statistics']['answered_correctly_percent'] == original['statistics']['answered_correctly_percent']
        assert doc['options'] == [{'letter':o['label'],'text':o['text'],'selection_percent':o['selection_percent']} for o in original['options']]
        validate_display(doc)
    assert rows == before
    hcc = docs['UWORLD_19445']['question_blocks'][0]
    assert hcc['columns'] == ['HCC', 'Present', 'Not Present', '']
    assert hcc['rows'] == [['Test positive','45','30','75'],['Test negative','5','120','125'],['','50','150','200']]
    yogurt = docs['UWORLD_19806']
    assert yogurt['question_blocks'][0]['rows'][0] == ['Low','82','60','142']
    assert yogurt['explanation'][1]['rows'][0] == ['High','41 (a)','66 (b)','107']
    or_text = '\n'.join(n.get('text','') for n in docs['UWORLD_1205']['explanation'])
    assert '(20 × 40) / (70 × 30) = 0.38' in or_text and 'ad/bc' in or_text
    assert 'ad/be' not in docs['UWORLD_1205']['educational_objective']
    assert '≥2 groups' in docs['UWORLD_19308']['explanation'][2]['text']
    assert len(figures(docs['UWORLD_14853'])) == 1
    assert figures(docs['UWORLD_14853'])[0]['role'] == 'question'
    assert sum(len(figures(d)) for d in docs.values()) == 6
    print('UWORLD_BIOSTATISTICS_OK reviewed=10 pages=45 source_block_items=40 archival_items=120 figures=6')


if __name__ == '__main__':
    main()
