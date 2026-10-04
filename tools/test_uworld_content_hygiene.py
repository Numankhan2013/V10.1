"""Protect the observed screenshot leakage and recoveries across every collection."""
from copy import deepcopy
from pathlib import Path
import json
from uworld_collections import bank_records, COLLECTIONS
from uworld_content_hygiene import validate_display, display_texts
from uworld_reviewed_document import record_hash, figures

ROOT = Path(__file__).resolve().parents[1]


def main():
    banks = bank_records()
    questions = {q['id']: q for b in banks for q in b['questions']}
    for q in questions.values():
        validate_display(q['uworldDocument'])
        assert 'uworldTranscript' not in q
        assert 'source_page_ocr' not in q['uworldSource']
        assert q['explanation'] == q['uworldSource']['explanation']['text']
        for node in q['uworldDocument'].get('question_blocks', []):
            if node['type'] == 'table':
                assert all(cell in q['question'] for row in [node['columns']] + node['rows'] for cell in row)
        for node in q['uworldDocument']['explanation']:
            if node['type'] == 'table':
                assert all(cell in q['explanation'] for row in [node['columns']] + node['rows'] for cell in row)
        assert not any(fragment in q['explanation'] for fragment in ['Ela»', 'alee mme', 'Original OCR'])
    first = next(iter(questions.values()))['uworldDocument']
    for mutate in [
        lambda d: d['explanation'].append({'type': 'paragraph', 'text': 'Answered correctly 96% Time Spent 14 secs'}),
        lambda d: d['options'][0].update(text='Yolk sac tumor Correct answer 96%'),
        lambda d: d['explanation'].append({'type': 'table', 'columns': ['One'], 'rows': [['Exhibit Display']]}),
        lambda d: d['explanation'].extend([{'type':'paragraph','text':' '.join('word'+str(i) for i in range(40))}] * 2),
    ]:
        bad = deepcopy(first); mutate(bad)
        try:
            validate_display(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Screenshot debris or overlap accepted')
    # Scientific inequality, nomenclature and brackets must not be censored.
    safe = deepcopy(first)
    safe['explanation'] = [{'type':'paragraph','text':'Age <25; β-hCG >100,000 mIU/mL; Cl−; [GnRH]; 45,X/46,XX. A correct response to therapy.'}]
    validate_display(safe)
    assert questions['UWORLD_20083']['options'][-1]['text'] == 'Yolk sac tumor'
    assert questions['UWORLD_1096']['options'][-1]['text'] == 'Staphylococcus saprophyticus'
    assert 'often caused by infection with HPV types 1-4' in questions['UWORLD_869']['explanation']
    assert 'douching-induced epithelial injury' in questions['UWORLD_869']['explanation']
    assert 'mesoderm, and endoderm' in questions['UWORLD_1928']['explanation']
    assert 'papillae composed of epithelial and myoepithelial cells' in questions['UWORLD_21642']['explanation']
    assert 'high-flow (nonischemic) priapism' in questions['UWORLD_19695']['explanation']
    ledger = json.loads((ROOT / 'data/uworld/display_repairs_v1.json').read_text())
    raw_docs = {d['id']: d for p in list((ROOT/'data/uworld/reviewed').glob('*/batch-*.json')) +
                list((ROOT/'data/uworld/prepared').glob('*/reviewed/batch-*.json'))
                for d in json.loads(p.read_text())['records']}
    ids = set()
    for entry in ledger['records']:
        qid = entry['question_id']; assert qid not in ids; ids.add(qid)
        old, current = entry['before_display'], raw_docs[qid]
        assert record_hash(old) == entry['before_display_sha256']
        assert record_hash(current) == entry['after_display_sha256']
        assert current['source_record_sha256'] == entry['source_record_sha256']
        assert current['reviewed_pages'] == entry['source_pages']
        assert old['correct_label'] == current['correct_label'] and old['statistics'] == current['statistics']
        assert figures(old) == figures(current), 'Content repair moved a protected source figure'
        assert [n for n in old['explanation'] if n['type']=='table'] == [n for n in current['explanation'] if n['type']=='table']
    print(f'UWORLD_CONTENT_HYGIENE_OK questions={len(questions)} pinned_repairs={len(ids)} raw_runtime_removed=true')


if __name__ == '__main__':
    main()
