"""Hash-verified adapter for the bounded UWorld Biochemistry source, never a study engine."""
from pathlib import Path
import hashlib,json
from uworld_source_text import source_transcript
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/uworld/automation_ingest/biochemistry/blocks_001_003'
# Deferred image-dependent records stay available as unscored reference text.
# This is a conservative OCR-only gate, not a completed medical content audit.
MISSING_VISUAL_IDS=set('12066 1378 1244 1022 1473 8328 1032 1036 1599 12263 2029 1071 2039 8276 11595 11914 1790 2030 1428 11950 1247 1727 1417 1436 1412 11960 1728'.split())
PDF=ROOT/'data/uworld/Source_pdfs/biochemistry/UW 2024 - Biochemistry - 3 blocks - OCR.pdf'

def load_source():
    manifest=json.loads((SOURCE/'manifest.json').read_text())
    rows=[]
    for field,count,sha in [('canonical_main_file','canonical_main_record_count','canonical_main_sha256'),('supplemental_file','supplemental_record_count','supplemental_sha256')]:
        raw=(SOURCE/manifest[field]).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=manifest[sha]:raise ValueError('UWorld source hash mismatch: '+field)
        chunk=[json.loads(line) for line in raw.decode().splitlines() if line.strip()]
        if len(chunk)!=manifest[count]:raise ValueError('UWorld source count mismatch: '+field)
        rows.extend(chunk)
    ids=set();pages=[]
    for row in rows:
        qid=row['question_id'];options=row['options'];labels=[o['label'] for o in options]
        if qid in ids or qid!=('uw2024_biochem_' if row['block_number'] else 'uw2024_biochem_supp_')+row['source_question_id']:raise ValueError('UWorld stable identity mismatch')
        ids.add(qid)
        if row['subject']!='Biochemistry' or row['source']['bank']!='UWorld':raise ValueError('Pilot subject/bank mismatch')
        if not 4<=len(options)<=8 or labels!=list('ABCDEFGH')[:len(options)] or not all(o['text'].strip() for o in options):raise ValueError('UWorld choice contract mismatch: '+qid)
        if row['correct_option'] not in labels or row['correct_answer_text']!=options[labels.index(row['correct_option'])]['text']:raise ValueError('UWorld answer mismatch: '+qid)
        if not row['question_text'].strip() or not row['explanation']['text'].strip():raise ValueError('UWorld empty source: '+qid)
        pages.extend(row['source']['source_pages'])
    if len(rows)!=132 or sorted(pages)!=list(range(1,730)):raise ValueError('UWorld complete source coverage mismatch')
    return manifest,rows

def bank_record():
    manifest,rows=load_source()
    topics=[{'id':'uworld_biochem_block_'+str(n),'title':'Block '+str(n),'number':n} for n in range(1,4)]
    topics.append({'id':'uworld_biochem_supplemental','title':'Supplemental source questions','number':4})
    questions=[]
    for row in rows:
        block=row['block_number'];topic=topics[block-1] if block else topics[3]
        options=[{'letter':o['label'],'text':('Pedigree '+o['label']) if row['source_question_id']=='11914' else ('Arrow '+o['label']) if row['source_question_id'] in ['1032','1036'] else o['text']} for o in row['options']]
        correct=ord(row['correct_option'])-64
        questions.append({'id':row['question_id'],'subject':'Biochemistry','bank':'UWorld','chapterId':topic['id'],'chapter':topic['title'],
            'questionNumber':row['question_number'] or row.get('block_sequence') or len(questions)+1,'question':row['question_text'],
            'options':options,'correctOption':correct,'correctAnswerText':options[correct-1]['text'],'explanation':row['explanation']['text'],
            'sourcePage':min(row['source']['source_pages']),'sourcePageEnd':max(row['source']['source_pages']),
            'provenance':{'bank':'UWorld','edition':'2024','sourcePdfSha256':manifest['source_sha256'],'sourcePages':row['source']['source_pages']},
            'uworldSource':row,'uworldTranscript':source_transcript(row),
            'uworldPilot':{'status':'ocr-unverified','requiresVisual':row['source_question_id'] in MISSING_VISUAL_IDS}})
    return {'subject':'Biochemistry','bank':'UWorld','edition':'2024','topics':topics,'questions':questions}
