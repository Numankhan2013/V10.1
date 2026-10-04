"""PDF-extracted, source-pinned Ophthalmology records using the shared UWorld UI."""
from pathlib import Path
import hashlib
import json
from uworld_reviewed_document import load_reviewed

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/uworld/automation_ingest/ophthalmology/block_001'
PDF = ROOT / 'data/uworld/Source_pdfs/opthalmology/UW 2024 - Ophthalmology - block 1 - OCR.pdf'
REVIEWED = ROOT / 'data/uworld/reviewed/ophthalmology'
COLLECTION = 'Ophthalmology'
COLLECTION_SCOPE = 'UWorld · ' + COLLECTION
PDF_SHA = 'ab4aadac54fbc78c9db9fca4b561cb5d0ee0ba4ade3f72066c72bf64021843dc'
PAGE_SIZE = (1349.28, 720.72)


def load_source():
    manifest = json.loads((SOURCE / 'manifest.json').read_text())
    raw = (SOURCE / manifest['jsonl_file']).read_bytes()
    if (manifest['source_sha256'] != PDF_SHA or
            manifest['extraction_method'] != 'pdf-text-and-page-image-review' or
            hashlib.sha256(raw).hexdigest() != manifest['jsonl_sha256']):
        raise ValueError('Ophthalmology source pin mismatch')
    rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    pages, ids = [], set()
    for number, row in enumerate(rows, 1):
        labels = [o['label'] for o in row['options']]
        qid = row['question_id']
        if (qid != 'UWORLD_' + str(row['uworld_question_id']) or qid in ids or
                row['bank'] != 'UWorld' or row['collection'] != COLLECTION or
                row['block_number'] != 1 or row['question_number'] != number):
            raise ValueError('Ophthalmology source identity mismatch')
        ids.add(qid)
        if not 4 <= len(labels) <= 9 or labels != list('abcdefghi')[:len(labels)]:
            raise ValueError('Ophthalmology choice contract mismatch: ' + qid)
        if (row['correct_option'] not in labels or row['correct_answer_text'] !=
                row['options'][labels.index(row['correct_option'])]['text']):
            raise ValueError('Ophthalmology answer mismatch: ' + qid)
        if not row['question_text'].strip() or not row['explanation']['text'].strip():
            raise ValueError('Empty Ophthalmology source: ' + qid)
        source = row['source']
        owned = source['all_question_id_pages']
        if (source['source_pdf_sha256'] != PDF_SHA or
                owned != list(range(min(owned), max(owned) + 1)) or
                [p['page'] for p in row['source_page_ocr']] != owned or
                any(not isinstance(p['text'], str) for p in row['source_page_ocr'])):
            raise ValueError('Ophthalmology original page coverage mismatch: ' + qid)
        pages.extend(owned)
    if len(rows) != 30 or pages != list(range(1, 205)):
        raise ValueError('Ophthalmology complete source coverage mismatch')
    return manifest, rows


def reviewed_documents(rows=None):
    if rows is None:
        _, rows = load_source()
    docs = load_reviewed(rows, PDF_SHA, REVIEWED, page_size=PAGE_SIZE)
    if set(docs) != {r['question_id'] for r in rows}:
        raise ValueError('Finish every Ophthalmology source review before shipping')
    return docs


def bank_record():
    _, rows = load_source()
    docs = reviewed_documents(rows)
    topic = {'id': 'uworld_ophthalmology_block_1', 'title': 'Block 1', 'number': 1}
    questions = []
    for row in rows:
        doc = docs[row['question_id']]
        pages = row['source']['all_question_id_pages']
        correct = ord(row['correct_option'].upper()) - 64
        questions.append({
            'id': row['question_id'], 'subject': COLLECTION_SCOPE, 'collection': COLLECTION,
            'bank': 'UWorld', 'chapterId': topic['id'], 'chapter': topic['title'],
            'questionNumber': row['question_number'], 'question': row['question_text'],
            'options': doc['options'], 'correctOption': correct,
            'correctAnswerText': doc['options'][correct - 1]['text'],
            'explanation': row['explanation']['text'], 'sourcePage': min(pages), 'sourcePageEnd': max(pages),
            'provenance': {'bank': 'UWorld', 'edition': '2024', 'sourcePdfSha256': PDF_SHA,
                           'sourcePages': pages, 'sourceRecordSha256': doc['source_record_sha256']},
            # Screenshot OCR is retained in the pinned import archive, not shipped
            # again inside every runtime record. Learner content stays complete.
            'uworldSource': {key: value for key, value in row.items() if key != 'source_page_ocr'},
            'uworldDocument': doc,
            'uworldPilot': {'status': 'source-reviewed' if doc['status'] == 'verified' else 'source-blocked',
                            'requiresVisual': doc['status'] != 'verified'},
        })
    return {'subject': COLLECTION_SCOPE, 'collection': COLLECTION, 'organization': 'UWorld',
            'bank': 'UWorld', 'edition': '2024', 'topics': [topic], 'questions': questions}
