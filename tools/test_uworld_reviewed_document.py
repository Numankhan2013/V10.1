"""Reviewed display documents are complete, source-pinned and fail closed on drift."""
from copy import deepcopy
import json
import re
from pathlib import Path
import tempfile
import uworld_reviewed_document as owner
from uworld_biochemistry import load_source, bank_record


def main():
    manifest, rows = load_source()
    documents = owner.load_reviewed(rows, manifest['source_sha256'])
    assert len(documents) == 132, 'Finish the complete Biochemistry review before shipping'
    assert set(documents) == {r['question_id'] for r in rows}
    assert all(doc['reviewed_pages'] for doc in documents.values())
    for doc in documents.values():
        text=' '.join([doc['question'],doc.get('educational_objective') or '']+[o['text'] for o in doc['options']]+[n.get('text','') for n in doc['explanation']])
        assert not re.search(r'Tfflle|Exhibit Display|Answered correctly|Collecting Statistics|\bBand T\b',text,re.I),doc['id']
        windows={}
        for index,node in enumerate(doc['explanation']):
            words=re.findall(r'\w+',node.get('text','').lower())
            for offset in range(max(0,len(words)-29)):
                run=tuple(words[offset:offset+30]);prior=windows.get(run)
                assert prior is None or (prior[0]==index and offset-prior[1]<30),'OCR overlap returned: '+doc['id']
                windows[run]=(index,offset)

    record = bank_record()
    assert all(q['subject'] == 'UWorld · Biochemistry' and q['collection'] == 'Biochemistry' for q in record['questions'])
    assert all(q['uworldDocument']['id'] == q['id'] for q in record['questions'])
    source_dir = owner.REVIEWED
    first = deepcopy(documents[rows[0]['question_id']])
    assert first['options'][2]['text'] == 'Caspases', 'Prevent the observed cross-question option contamination'
    batch = {'schema_version': 1, 'source_pdf_sha256': manifest['source_sha256'], 'records': [first]}
    changes = [
        lambda d: d['records'][0].update(source_record_sha256='0'*64),
        lambda d: d['records'][0].update(reviewed_pages=[]),
        lambda d: d['records'][0].update(correct_label='A'),
        lambda d: d['records'][0]['options'][0].update(letter='Z'),
        lambda d: d['records'][0]['statistics'].update(answered_correctly_percent=101),
        lambda d: d['records'][0]['explanation'].append({'type':'table','columns':['One','Two'],'rows':[['Incomplete']]}),
        lambda d: d['records'][0]['explanation'].append({'type':'figure','page':1,'bbox':[0,0,2000,100],'role':'explanation'}),
        lambda d: d['records'][0].update(status='maybe'),
    ]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            owner.REVIEWED = Path(tmp)
            path = owner.REVIEWED / 'batch-test.json'
            for change in changes:
                bad = deepcopy(batch)
                change(bad)
                path.write_text(json.dumps(bad))
                try:
                    owner.load_reviewed(rows, manifest['source_sha256'])
                except ValueError:
                    continue
                raise AssertionError('Unsafe reviewed document accepted')
    finally:
        owner.REVIEWED = source_dir
    print('UWORLD_REVIEWED_DOCUMENT_OK questions=132 source_pins=true choice_contract=true fail_closed=true')


if __name__ == '__main__':
    main()
