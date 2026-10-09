"""Collections produced by the deterministic screenshot extractor (tools/uworld_auto).

The extractor writes the same source-native display documents the hand review
did (paragraphs and source crops pinned to PDF page + bbox), plus a QA ledger.
Questions that pass every automatic check ship as verified; flagged ones ship
as source-blocked until they are corrected in reviewed/fixes.json. Figure crops
are committed beside the data so CI never downloads the (multi-GB) PDFs.
"""
import hashlib
import json
from uworld_imported_collection import ImportedCollection, ROOT
from uworld_reviewed_document import record_hash, percentage, load_reviewed


class AutoCollection(ImportedCollection):
    AUTO = True

    def __init__(self, slug, collection, pdf, pdf_sha, count, pages, blocks):
        super().__init__(slug, collection, pdf, pdf_sha, count, pages, blocks)
        self.FIGURES = self.SOURCE / 'figures'

    def load_source(self):
        manifest = json.loads((self.SOURCE / 'manifest.json').read_text())
        raw = (self.SOURCE / manifest['jsonl_file']).read_bytes()
        if (manifest['source_sha256'] != self.PDF_SHA or manifest['collection'] != self.COLLECTION or
                manifest['record_count'] != self.count or manifest['page_count'] != self.pages or
                manifest.get('source_extraction_method') != 'uworld-auto-extract' or
                hashlib.sha256(raw).hexdigest() != manifest['jsonl_sha256']):
            raise ValueError('Auto UWorld source pin mismatch: ' + self.slug)
        rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
        ids, owned_pages, block_counts = set(), [], {}
        for row in rows:
            qid, source, options = row['question_id'], row['source'], row['options']
            labels = [o['label'] for o in options]
            owned = source['source_pages']
            if (qid != 'UWORLD_' + str(row['uworld_question_id']) or qid in ids or
                    row['bank'] != 'UWorld' or row['collection'] != self.COLLECTION or
                    source['source_pdf_sha256'] != self.PDF_SHA or
                    owned != list(range(min(owned), max(owned) + 1))):
                raise ValueError('Auto UWorld ownership mismatch: ' + qid)
            if (not 4 <= len(labels) <= 9 or labels != list('abcdefghi')[:len(labels)] or
                    row['correct_option'] not in labels or not row['question_text'].strip()):
                raise ValueError('Auto UWorld question contract mismatch: ' + qid)
            for option in options:
                percentage(option.get('selection_percent'))
            percentage(row['statistics'].get('answered_correctly_percent'))
            ids.add(qid); owned_pages.extend(owned)
            block_counts[row['block_number']] = block_counts.get(row['block_number'], 0) + 1
        # Every page is owned by a question or listed as unusable with a reason.
        skipped = [p for entry in manifest.get('unowned_pages', []) for p in entry['pages']]
        if (len(rows) != self.count or sorted(owned_pages + skipped) != list(range(1, self.pages + 1)) or
                block_counts != self.blocks):
            raise ValueError('Incomplete auto UWorld source: ' + self.slug)
        expected = {str(p): r['question_id'] for r in rows for p in r['source']['source_pages']}
        if json.loads((self.SOURCE / 'page_to_question_manifest.json').read_text()) != expected:
            raise ValueError('Auto UWorld page map mismatch: ' + self.slug)
        return manifest, rows

    def reviewed_documents(self, rows=None):
        # Auto collections ship WebP crops (visually lossless, ~10x smaller); they are
        # fetched on demand and runtime-cached rather than precached by the app shell.
        if rows is None:
            _, rows = self.load_source()
        docs = load_reviewed(rows, self.PDF_SHA, self.SOURCE / 'reviewed', self.PAGE_SIZE, ext='webp')
        if set(docs) != {r['question_id'] for r in rows}:
            raise ValueError('Finish source review before shipping: ' + self.slug)
        return docs
