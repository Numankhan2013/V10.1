"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/dermatology/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'dermatology', 'Dermatology',
    'data/uworld/Source_pdfs/dermatology/UW 2024 - Dermatology - 3 blocks - OCR.pdf',
    '9864e5e78d4aa38485f2c07ecb52f4ecbd9c28e2659d4aef8c410cd37c0679a7', 99, 917, {1: 40, 2: 41, 3: 18})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
