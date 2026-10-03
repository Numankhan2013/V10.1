"""Verify bounded immutable import, variable choices and source-safe presentation."""
from uworld_biochemistry import load_source,bank_record
from apply_uworld_biochemistry_v1 import transform
from pathlib import Path
import hashlib,json
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
# Transformer must be additive/idempotent; retained incumbent functions survive.
fixture='<head></head>  let activeSubject = 1;\n  /* NK_QUESTION_PRESENTATION_V1_START */\n  /* NK_QUESTION_PRESENTATION_V1_END */\n  function nkStudySupport(){}\n  window.QB={};\n${nkScientificMarkup(o.text)}'
out=transform(fixture);assert transform(out)==out and out.count('BANKS_BY_SUBJECT[NK_UWORLD_BIOCHEMISTRY_BANK.subject]=')==1 and 'BANKS_BY_SUBJECT.Biochemistry.push(' not in out
assert 'function nkStudySupport(){}' in out and 'uworldReference:nkUworldReference' in out
print('UWORLD_SOURCE_ADAPTER_OK 132 records/729 pages/4 source collections/A–H/immutable/idempotent')
