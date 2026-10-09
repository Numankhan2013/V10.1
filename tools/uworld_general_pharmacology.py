"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/general_pharmacology/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'general_pharmacology', 'General Pharmacology',
    'data/uworld/Source_pdfs/general_pharmacology/UW 2024 - General Pharmacology - 2 block - OCR.pdf',
    '62ea92d4571aa553754c1fe9c78259942ff2c26a051cb1753a3af8a82b21025b', 42, 222, {1: 8, 2: 27, 3: 7})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
