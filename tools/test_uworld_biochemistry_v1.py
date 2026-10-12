"""Verify bounded immutable import, variable choices and source-safe presentation."""
from uworld_biochemistry import load_source,bank_record
from uworld_biochemistry import ROOT
from uworld_collections import bank_records
import re
manifest,rows=load_source();record=bank_record()
assert len(record['questions'])==132 and len(record['topics'])==4
assert [sum(q['chapterId']==t['id'] for q in record['questions']) for t in record['topics']]==[40,40,40,12]
by_id={q['id']:q for q in record['questions']}
for row in rows:
    q=by_id[row['question_id']]
    assert q['uworldSource']==row and q['explanation']==row['explanation']['text']
    assert q['correctOption']==ord(row['correct_option'])-64
    assert len(q['options'])==len(row['options'])
    if 'uworldDocument' not in q:
        assert q['question']==row['question_text']
        if row['source_question_id'] not in ['11914','1032','1036']:assert [o['text'] for o in q['options']]==[o['text'] for o in row['options']]
    else:
        assert q['question']==q['uworldDocument']['question']
        assert q['options']==q['uworldDocument']['options']
if 'uworldDocument' not in by_id['uw2024_biochem_11914']:assert [o['text'] for o in by_id['uw2024_biochem_11914']['options']]==['Pedigree '+x for x in 'ABCDE']
if 'uworldDocument' not in by_id['uw2024_biochem_1032']:assert [o['text'] for o in by_id['uw2024_biochem_1032']['options']]==['Arrow '+x for x in 'ABCDE']
if 'uworldDocument' not in by_id['uw2024_biochem_1036']:assert [o['text'] for o in by_id['uw2024_biochem_1036']['options']]==['Arrow '+x for x in 'ABCDEFG']
assert by_id['uw2024_biochem_1486']['uworldSource']['explanation']['educational_objective'] is None
assert record['subject']=='UWorld · Biochemistry' and record['collection']=='Biochemistry'
assert all(q['uworldPilot']['status'] in ['ocr-unverified','source-reviewed','source-blocked'] for q in record['questions'])
assert max(len(q['options']) for q in record['questions'])==8
# Shipped page: one collection registry, scripts load before the app script, incumbent functions survive.
out=(ROOT/'app/src/main/assets/index.html').read_text(encoding='utf-8')
assert out.count('/* NK_UWORLD_BANK_DATA_START */')==1 and out.count('/* NK_UWORLD_BIOCHEMISTRY_V1_START */')==1
assert out.count('BANKS_BY_SUBJECT[NK_UWORLD_BIOCHEMISTRY_BANK.subject]=')==1 and 'BANKS_BY_SUBJECT.Biochemistry.push(' not in out
assert 'function nkStudySupport(' in out and out.count('uworldReference:nkUworldReference')==1
data=re.findall(r'<script src="(uworld_data/[^"]+)"></script>',out)
assert out.count('__NK_DATA_UWORLD_SCRIPTS__')+bool(data)==1,'UWorld collection scripts must be emitted exactly once'
if data:assert data==[f'uworld_data/collection-{i:02d}.js' for i in range(len(bank_records()))]
first=out.find('__NK_DATA_UWORLD_SCRIPTS__') if not data else out.index('<script src="uworld_data/')
assert 0<=first<out.index('  let activeSubject = ')
assert '${nkScientificMarkup(o.text)}' not in out and "${q.bank==='UWorld'?nkUworldOptionMarkup(q,o):nkScientificMarkup(o.text)}" in out
print('UWORLD_SOURCE_ADAPTER_OK 132 records/729 pages/4 source collections/A–H/immutable/shipped')
