"""Source-pinned imported collections reuse the reviewed document/study engine.

Upstream records remain byte-identical in source/. Normalized records retain
their original row fingerprints and full PDF page ownership; reviewed display
documents are a separate, fail-closed layer.
"""
from pathlib import Path
import hashlib
import json
from uworld_reviewed_document import load_reviewed, record_hash, percentage

ROOT = Path(__file__).resolve().parents[1]


class ImportedCollection:
    def __init__(self, slug, collection, pdf, pdf_sha, count, pages, blocks):
        self.slug, self.COLLECTION = slug, collection
        self.COLLECTION_SCOPE = 'UWorld · ' + collection
        self.SOURCE = ROOT / 'data/uworld/prepared' / slug
        self.PDF, self.PDF_SHA = ROOT / pdf, pdf_sha
        self.count, self.pages, self.blocks = count, pages, blocks
        self.PAGE_SIZE = (1416, 757)

    def load_source(self):
        manifest = json.loads((self.SOURCE / 'manifest.json').read_text())
        raw = (self.SOURCE / manifest['jsonl_file']).read_bytes()
        original = self.SOURCE / 'source' / manifest['original_jsonl']
        if (manifest['source_sha256'] != self.PDF_SHA or
                manifest['collection'] != self.COLLECTION or
                manifest['record_count'] != self.count or
                manifest['page_count'] != self.pages or
                hashlib.sha256(raw).hexdigest() != manifest['jsonl_sha256'] or
                hashlib.sha256(original.read_bytes()).hexdigest() != manifest['original_jsonl_sha256']):
            raise ValueError('Imported UWorld source pin mismatch: ' + self.slug)
        originals = {str(r['source_question_id']): r for r in
                     map(json.loads, original.read_text().splitlines()) if r}
        rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
        repairs = {}
        if manifest.get('source_repairs_sha256'):
            repair_bytes = (self.SOURCE / 'source_repairs.json').read_bytes()
            ledger = json.loads(repair_bytes)
            if (hashlib.sha256(repair_bytes).hexdigest() != manifest['source_repairs_sha256'] or
                    ledger.get('schema_version') != 1 or ledger['source_pdf_sha256'] != self.PDF_SHA):
                raise ValueError('Imported UWorld repair pin mismatch: ' + self.slug)
            repairs = {r['question_id']: r for r in ledger['records']}
            if len(repairs) != len(ledger['records']):
                raise ValueError('Duplicate imported UWorld repair: ' + self.slug)
        ids, pages, block_counts = set(), [], {}
        for row in rows:
            qid, source, options = row['question_id'], row['source'], row['options']
            labels = [o['label'] for o in options]
            original_row = originals.get(str(row['uworld_question_id']))
            owned = source['source_pages']
            if (qid != 'UWORLD_' + str(row['uworld_question_id']) or qid in ids or
                    row['bank'] != 'UWorld' or row['collection'] != self.COLLECTION or
                    source['source_pdf_sha256'] != self.PDF_SHA or
                    original_row is None or source['original_record_sha256'] != record_hash(original_row) or
                    owned != list(range(min(owned), max(owned) + 1)) or
                    [p['page'] for p in row['source_page_ocr']] != owned):
                raise ValueError('Imported UWorld ownership mismatch: ' + qid)
            if (not 4 <= len(labels) <= 9 or labels != list('abcdefghi')[:len(labels)] or
                    row['correct_option'] not in labels or
                    row['correct_answer_text'] != options[labels.index(row['correct_option'])]['text'] or
                    not row['question_text'].strip() or not row['explanation']['text'].strip()):
                raise ValueError('Imported UWorld question contract mismatch: ' + qid)
            male = isinstance(original_row['options'], dict)
            original_options = ([{'label': k.lower(), 'text': v,
                                  'selection_percent': (original_row['option_percentages'] or {}).get(k)}
                                 for k, v in original_row['options'].items()] if male else
                                [{**o, 'label': o['label'].lower()} for o in original_row['options']])
            repair = repairs.get(qid)
            if repair:
                if (repair['original_record_sha256'] != record_hash(original_row) or
                        repair['original_options'] != original_options or
                        not set(repair['source_pages']).issubset(owned) or
                        source.get('normalization_repairs') != ['source_repairs.json:' + qid]):
                    raise ValueError('Imported UWorld repair ownership mismatch: ' + qid)
                original_options = repair['replacement_options']
            if (options != original_options or row['correct_option'] != original_row['correct_option'].lower() or
                    row['question_text'] != original_row['question' if male else 'question_text'] or
                    row['explanation']['text'] != (original_row['explanation'] if male else original_row['explanation']['text']) or
                    owned != (original_row['provenance']['source_pages'] if male else original_row['source']['source_pages'])):
                raise ValueError('Imported UWorld raw content changed: ' + qid)
            for option in options:
                percentage(option.get('selection_percent'))
            percentage(row['statistics'].get('answered_correctly_percent'))
            ids.add(qid); pages.extend(owned)
            block_counts[row['block_number']] = block_counts.get(row['block_number'], 0) + 1
        if len(rows) != self.count or pages != list(range(1, self.pages + 1)) or block_counts != self.blocks:
            raise ValueError('Incomplete imported UWorld source: ' + self.slug)
        if not set(repairs).issubset(ids):
            raise ValueError('Unknown imported UWorld repair: ' + self.slug)
        expected = {str(p): r['question_id'] for r in rows for p in r['source']['source_pages']}
        if json.loads((self.SOURCE / 'page_to_question_manifest.json').read_text()) != expected:
            raise ValueError('Imported UWorld page map mismatch: ' + self.slug)
        return manifest, rows

    def reviewed_documents(self, rows=None):
        if rows is None:
            _, rows = self.load_source()
        docs = load_reviewed(rows, self.PDF_SHA, self.SOURCE / 'reviewed', self.PAGE_SIZE)
        if set(docs) != {r['question_id'] for r in rows}:
            raise ValueError('Finish source review before shipping: ' + self.slug)
        return docs

    def bank_record(self):
        _, rows = self.load_source()
        docs = self.reviewed_documents(rows)
        topics = [{'id': f'uworld_{self.slug}_block_{n}', 'title': f'Block {n}', 'number': n}
                  for n in self.blocks]
        topic_by_number = {t['number']: t for t in topics}
        questions = []
        for row in rows:
            doc, pages = docs[row['question_id']], row['source']['source_pages']
            topic = topic_by_number[row['block_number']]
            correct = ord(row['correct_option'].upper()) - 64
            questions.append({
                'id': row['question_id'], 'subject': self.COLLECTION_SCOPE,
                'collection': self.COLLECTION, 'bank': 'UWorld', 'chapterId': topic['id'],
                'chapter': topic['title'], 'questionNumber': row['question_number'],
                'question': row['question_text'], 'options': doc['options'],
                'correctOption': correct, 'correctAnswerText': doc['options'][correct - 1]['text'],
                'explanation': row['explanation']['text'], 'sourcePage': min(pages), 'sourcePageEnd': max(pages),
                'provenance': {'bank': 'UWorld', 'edition': '2024', 'sourcePdfSha256': self.PDF_SHA,
                               'sourcePages': pages, 'sourceRecordSha256': doc['source_record_sha256']},
                'uworldSource': {k: v for k, v in row.items() if k != 'source_page_ocr'},
                'uworldDocument': doc,
                'uworldPilot': {'status': 'source-reviewed' if doc['status'] == 'verified' else 'source-blocked',
                                'requiresVisual': doc['status'] != 'verified'},
            })
        return {'subject': self.COLLECTION_SCOPE, 'collection': self.COLLECTION,
                'organization': 'UWorld', 'bank': 'UWorld', 'edition': '2024',
                'topics': topics, 'questions': questions}
