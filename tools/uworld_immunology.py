"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/immunology/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'immunology', 'Immunology',
    'data/uworld/Source_pdfs/immunology/Immunology - 2 blocks.pdf',
    '6919bce5b568c6fb2ce1d5f1d5f89fcf7a75a7662192007e1d7c62b2ac2c31a3', 101, 592, {1: 37, 2: 38, 3: 26})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
