"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/renal_urinary_electrolytes/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'renal_urinary_electrolytes', 'Renal, Urinary Systems & Electrolytes',
    'data/uworld/Source_pdfs/renal_urinary_systems_electrolytes/UW_2024_Renal,_Urinary_Systems_&_Electrolytes_6_blocks_OCR.pdf',
    'd1e0ddd1926f85c24188fe067610055805753eb27d92b55c14270e81f6bd6f81', 223, 1441, {1: 4, 2: 1, 3: 3, 4: 6, 5: 56, 6: 56, 7: 20, 8: 33, 9: 13, 10: 31})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
