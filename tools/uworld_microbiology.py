"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/microbiology/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'microbiology', 'Microbiology',
    'data/uworld/Source_pdfs/microbiology/Microbiology - 8 blocks.pdf',
    '8765cdc021c9813801b47411eeb7d9e349f989ebb8bc0bf28946cf8b4c9d69b5', 300, 1562, {1: 35, 2: 40, 3: 48, 4: 40, 5: 38, 6: 38, 7: 30, 8: 31})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
