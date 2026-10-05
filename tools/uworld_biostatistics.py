"""Source-reviewed Block 1 and the first 20 questions of Block 2."""
from uworld_imported_collection import ImportedCollection

OWNER = ImportedCollection(
    'biostatistics_epidemiology', 'Biostatistics & Epidemiology',
    'data/uworld/Source_pdfs/biostatistics_epidemiology/UW 2024 - Biostatistics & Epidemiology - 3 blocks - OCR.pdf',
    '82c97582c1a6fd7ac47570183cc80c7cd232ad3557203e3cc4b4d2c6a55b16c9', 60, 277, {1: 40, 2: 20})
OWNER.PAGE_SIZE = (1416.96, 727.08)
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents


def bank_record():
    record = OWNER.bank_record()
    # Keep stable block/question identities; label the bounded reviewed scope.
    record['topics'][1]['title'] = 'Block 2 · Questions 1–20'
    for question in record['questions']:
        if question['chapterId'] == record['topics'][1]['id']:
            question['chapter'] = record['topics'][1]['title']
    return record
