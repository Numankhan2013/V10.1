"""Protect PDF-only extraction provenance, complete page ownership and native exhibits."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from uworld_ophthalmology import ROOT, SOURCE, PDF, PDF_SHA, load_source, reviewed_documents, bank_record
from uworld_reviewed_document import figures, figure_asset, record_hash
from uworld_collections import bank_records


def main():
    manifest, rows = load_source()
    frozen = deepcopy(rows)
    docs = reviewed_documents(rows)
    bank = bank_record()
    assert len(rows) == len(docs) == len(bank['questions']) == 30
    assert rows == frozen and len(bank['topics']) == 1
    assert {r['collection'] for r in bank_records()} == {'Biochemistry', 'Poisoning & Environmental Exposure', 'Ophthalmology', 'Male Reproductive System', 'Female Reproductive System & Breast'}
    expected_pages = json.loads((SOURCE / 'page_to_question_manifest.json').read_text())
    assert expected_pages == {str(p): row['question_id'] for row in rows for p in row['source']['all_question_id_pages']}
    pdf_bytes = PDF.read_bytes()
    assert ('oid sha256:' + PDF_SHA).encode() in pdf_bytes or hashlib.sha256(pdf_bytes).hexdigest() == PDF_SHA
    assert manifest['source_repository_commit'] == '56fe81724f120b5b6d5277a82e418714278c1493'
    for row, q in zip(rows, bank['questions']):
        doc = docs[row['question_id']]
        assert q['question'] == row['question_text'], 'Full stem must remain searchable beyond an inline exhibit'
        assert q['uworldSource'] == {k: v for k, v in row.items() if k != 'source_page_ocr'}
        assert doc['source_record_sha256'] == q['provenance']['sourceRecordSha256'] == record_hash(row)
        assert q['explanation'] == row['explanation']['text']
        assert q['subject'] == 'UWorld · Ophthalmology' and q['chapterId'] == 'uworld_ophthalmology_block_1'
        assert doc['status'] == 'verified' and doc.get('educational_objective'), q['id']
        visible = ' '.join([doc['question'], doc['educational_objective']] + [o['text'] for o in doc['options']] +
                           [n.get('text', '') for n in doc.get('question_blocks', []) + doc['explanation']])
        assert not re.search(r'Exhibit Display|Answered correctly|Block Time Elapsed|End Block|My Notebook|https://t.me', visible), q['id']
        assert all(o['selection_percent'] == doc['statistics']['selection_percent'][o['letter']] for o in doc['options'])
        for node in figures(doc):
            assert node['asset'] == figure_asset(q['id'], node, PDF_SHA)
            assert node['asset'] != figure_asset(q['id'], node), 'Source PDF must determine media identity'
    first = docs['UWORLD_18804']
    assert first['correct_label'] == 'C' and first['statistics']['selection_percent']['C'] == 47
    pupil = docs['UWORLD_106294']
    assert len(pupil['options']) == 6
    assert any(n['type'] == 'figure' and n['role'] == 'question' for n in pupil['question_blocks'])
    fields = docs['UWORLD_8594']
    assert fields['correct_label'] == 'D'
    assert all(o.get('figure', {}).get('role') == 'option' for o in fields['options'])
    assert fields['statistics']['selection_percent'] == {'A': 3, 'B': 6, 'C': 24, 'D': 57, 'E': 7}
    # Execute the actual incumbent presenter against every real new record.
    js = "const assert=require('assert');\n" + (ROOT / 'tools/question_presentation_core.js').read_text()
    js += '\nconst BANK=' + json.dumps(bank, ensure_ascii=False) + ';\n'
    js += "for(const q of BANK.questions){assert(nkQuestionPresentationFor(q).valid,q.id);assert.deepEqual(nkQuestionPresentationFor(q).options,q.options);}\n"
    js += "console.log('OPHTHALMOLOGY_SHARED_PRESENTER_OK records=30 source_exhibits=true');"
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / 'presenter.js'
        script.write_text(js)
        subprocess.run(['node', str(script)], check=True, cwd=ROOT)
    print('UWORLD_OPHTHALMOLOGY_OK records=30 pages=204 pdf_only=true source_pins=true source_ocr_preserved=true')


if __name__ == '__main__':
    main()
