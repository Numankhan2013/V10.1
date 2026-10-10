"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/pulmonary_critical_care/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'pulmonary_critical_care', 'Pulmonary & Critical Care',
    'data/uworld/Source_pdfs/pulmonary_and_criticalcare/Pulmonary & Critical Care - 7 blocks - OCR.pdf',
    'c36bc64e0dff882ae6bd8063d5405a3607c1ac46b7e2f842fc3b3499b5fd5340', 252, 1692, {1: 38, 2: 39, 3: 35, 4: 39, 5: 36, 6: 39, 7: 20, 8: 6})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
