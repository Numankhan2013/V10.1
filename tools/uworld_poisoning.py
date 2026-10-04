"""Immutable second-collection adapter; source-native documents, shared study engines."""
from pathlib import Path
import hashlib
import json
from uworld_reviewed_document import load_reviewed

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/uworld/automation_ingest/poisoning_environmental_exposure/block_001'
PDF = ROOT / 'data/uworld/Source_pdfs/Poisioning_environmental_exposure/UW_2024_Poisoning_&_Environmental_Exposure_1_block_OCR.pdf'
REVIEWED = ROOT / 'data/uworld/reviewed/poisoning_environmental_exposure'
COLLECTION = 'Poisoning & Environmental Exposure'
COLLECTION_SCOPE = 'UWorld · ' + COLLECTION
PDF_SHA = '9f3814a9a5d67e69d498cc4958d3daad61081cb7f328f20b9cd2916822314508'
JSONL_SHA = 'ebdb815fd236afe178128f3488e2439c57c91a165d654a4104e63a7342e13166'
REPOSITORY_JSONL_SHA = 'e54ebb2d98311760899e209ccbe0741ef6888cc6abb3e1d6dd8d0671a291d18c'


def load_source():
    manifest = json.loads((SOURCE / 'manifest.json').read_text())
    raw = (SOURCE / manifest['jsonl_file']).read_bytes()
    # The supplied manifest hashes a final LF; the committed immutable blob has none.
    if (manifest['source_sha256'] != PDF_SHA or manifest['jsonl_sha256'] != JSONL_SHA or
            hashlib.sha256(raw).hexdigest() != REPOSITORY_JSONL_SHA or
            hashlib.sha256(raw + b'\n').hexdigest() != JSONL_SHA):
        raise ValueError('Poisoning source pin mismatch')
    rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    pages, ids = [], set()
    for row in rows:
        labels = [o['label'] for o in row['options']]
        qid = row['question_id']
        if qid != 'UWORLD_' + str(row['uworld_question_id']) or qid in ids or row['bank'] != 'UWorld':
            raise ValueError('Poisoning stable identity mismatch')
        ids.add(qid)
        if not 4 <= len(labels) <= 9 or labels != list('abcdefghi')[:len(labels)]:
            raise ValueError('Poisoning choice contract mismatch: ' + qid)
        if row['correct_option'] not in labels or row['correct_answer_text'] != row['options'][labels.index(row['correct_option'])]['text']:
            raise ValueError('Poisoning answer mismatch: ' + qid)
        if not row['question_text'].strip() or not row['explanation']['text'].strip():
            raise ValueError('Empty Poisoning source: ' + qid)
        pages.extend(row['source']['all_question_id_pages'])
    if len(rows) != 33 or sorted(pages) != list(range(1, 167)):
        raise ValueError('Poisoning complete source coverage mismatch')
    return manifest, rows


def reviewed_documents(rows=None):
    if rows is None:
        _, rows = load_source()
    docs = load_reviewed(rows, PDF_SHA, REVIEWED, page_size=(792, 422))
    if set(docs) != {r['question_id'] for r in rows}:
        raise ValueError('Finish every Poisoning source review before shipping')
    return docs


def bank_record():
    manifest, rows = load_source()
    docs = reviewed_documents(rows)
    topic = {'id': 'uworld_poisoning_block_1', 'title': 'Block 1', 'number': 1}
    questions = []
    for row in rows:
        doc = docs[row['question_id']]
        pages = row['source']['all_question_id_pages']
        correct = ord(row['correct_option'].upper()) - 64
        questions.append({
            'id': row['question_id'], 'subject': COLLECTION_SCOPE, 'collection': COLLECTION,
            'bank': 'UWorld', 'chapterId': topic['id'], 'chapter': topic['title'],
            'questionNumber': row['question_number'], 'question': doc['question'],
            'options': doc['options'], 'correctOption': correct,
            'correctAnswerText': doc['options'][correct - 1]['text'],
            'explanation': row['explanation']['text'], 'sourcePage': min(pages), 'sourcePageEnd': max(pages),
            'provenance': {'bank': 'UWorld', 'edition': '2024', 'sourcePdfSha256': PDF_SHA, 'sourcePages': pages},
            'uworldSource': row, 'uworldDocument': doc,
            'uworldQuestionSet': row.get('question_set'),
            'uworldPilot': {'status': 'source-reviewed' if doc['status'] == 'verified' else 'source-blocked',
                            'requiresVisual': doc['status'] != 'verified'},
        })
    return {'subject': COLLECTION_SCOPE, 'collection': COLLECTION, 'organization': 'UWorld',
            'bank': 'UWorld', 'edition': '2024', 'topics': [topic], 'questions': questions}
