"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/pulmonary_critical_care/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'pulmonary_critical_care', 'Pulmonary & Critical Care',
    'data/uworld/Source_pdfs/pulmonary_and_criticalcare/Pulmonary & Critical Care - 7 blocks - OCR.pdf',
    'c36bc64e0dff882ae6bd8063d5405a3607c1ac46b7e2f842fc3b3499b5fd5340', 226, 1692, {1: 34, 2: 34, 3: 32, 4: 36, 5: 31, 6: 34, 7: 19, 8: 6})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
