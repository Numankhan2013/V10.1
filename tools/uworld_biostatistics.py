"""First ten source-reviewed items; the remaining original import stays archival."""
from uworld_imported_collection import ImportedCollection

OWNER = ImportedCollection(
    'biostatistics_epidemiology', 'Biostatistics & Epidemiology',
    'data/uworld/Source_pdfs/biostatistics_epidemiology/UW 2024 - Biostatistics & Epidemiology - 3 blocks - OCR.pdf',
    '82c97582c1a6fd7ac47570183cc80c7cd232ad3557203e3cc4b4d2c6a55b16c9', 10, 45, {1: 10})
OWNER.PAGE_SIZE = (1416.96, 727.08)
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents


def bank_record():
    record = OWNER.bank_record()
    record['topics'][0]['title'] = 'Block 1 · Questions 1–10'
    for question in record['questions']:
        question['chapter'] = record['topics'][0]['title']
    return record
