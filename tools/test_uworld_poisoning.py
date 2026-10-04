"""Protect second-collection content, context, source pins and shared rendering."""
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import tempfile
from uworld_poisoning import ROOT, load_source, bank_record, reviewed_documents, PDF_SHA
from uworld_reviewed_document import figures, figure_asset
from uworld_collections import bank_records


def main():
    manifest, rows = load_source()
    frozen = deepcopy(rows)
    docs = reviewed_documents(rows)
    bank = bank_record()
    assert rows == frozen and len(docs) == len(bank['questions']) == 33
    assert all(q['uworldSource'] == row for q, row in zip(bank['questions'], rows))
    assert all(q['explanation'] == row['explanation']['text'] for q, row in zip(bank['questions'], rows))
    assert all(q['subject'] == 'UWorld · Poisoning & Environmental Exposure' for q in bank['questions'])
    assert len(bank['topics']) == 1
    assert len(bank_records()) == 2
    assert all(doc['status'] == 'verified' for doc in docs.values())
    for doc in docs.values():
        text = ' '.join([doc['question'], doc.get('educational_objective') or ''] +
                        [o['text'] for o in doc['options']] + [n.get('text', '') for n in doc['explanation']])
        assert not re.search(r'Exhibit Display|Answered correctly|Collecting Statistics|Proceed to Next Item|End Block|\bTfflle\b', text, re.I), doc['id']
        assert doc.get('educational_objective'), doc['id']
        for node in doc.get('question_blocks', []):
            if node['type'] == 'table':
                assert not any(re.search(r'selection|answered correctly|correct answer', cell, re.I) for cell in node['columns']), 'Cohort statistics leaked before answering'
        for node in figures(doc):
            assert node['asset'] == figure_asset(doc['id'], node, PDF_SHA)
            assert node['asset'] != figure_asset(doc['id'], node), 'PDF provenance must affect asset identity'
    nine = docs['UWORLD_1321']
    assert [o['letter'] for o in nine['options']] == list('ABCDEFGHI')
    assert nine['correct_label'] == 'H' and nine['options'][8]['text'] == 'Thiamine'
    assert nine['statistics']['selection_percent']['I'] == 0
    graph = docs['UWORLD_18021']
    assert all(o.get('figure', {}).get('role') == 'option' for o in graph['options'])
    assert graph['statistics']['selection_percent']['D'] is None
    assert graph['statistics']['selection_percent']['E'] is None
    labs = [n for n in docs['UWORLD_15235'].get('question_blocks', []) if n['type'] == 'table']
    assert labs and any('PCO' in cell or 'Pco' in cell or 'PaCO' in cell for n in labs for row in n['rows'] for cell in row)
    for qid in ('UWORLD_2088', 'UWORLD_2089'):
        assert 'ankle clonus' in docs[qid]['question'].lower(), 'Linked item lost its clinical context'
    assert 'antidote' in docs['UWORLD_2089']['question'].lower()
    by_id = {q['id']: q for q in bank['questions']}
    assert by_id['UWORLD_2089']['uworldQuestionSet']['depends_on_question_id'] == 'UWORLD_2088'
    # Execute the actual shared presenter against every real second-collection record.
    js = "const assert=require('assert');\n" + (ROOT / 'tools/question_presentation_core.js').read_text()
    js += '\nconst BANK=' + json.dumps(bank, ensure_ascii=False) + ';\n'
    js += "for(const q of BANK.questions){assert(nkQuestionPresentationFor(q).valid,q.id);assert.equal(nkQuestionPresentationFor(q).options.length,q.options.length);}\n"
    js += "const q=BANK.questions.find(q=>q.id==='UWORLD_1321');assert.equal(nkQuestionPresentationFor(q).options[8].letter,'I');console.log('POISONING_SHARED_PRESENTER_OK records=33 choices=A-I');"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'presenter.js'
        path.write_text(js)
        subprocess.run(['node', str(path)], check=True, cwd=ROOT)
    print('UWORLD_POISONING_OK records=33 pages=166 immutable=true source_pins=true context=true graphs=true')


if __name__ == '__main__':
    main()
