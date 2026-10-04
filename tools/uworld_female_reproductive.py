"""Both distinct Item40 IDs are preserved in the source's 41-question first block."""
from uworld_imported_collection import ImportedCollection

OWNER = ImportedCollection(
    'female_reproductive_system_breast', 'Female Reproductive System & Breast',
    'data/uworld/Source_pdfs/Female_reproductive_system_breast/UW_2024_Female_Reproductive_System_&_Breast_2_blocks_OCR.pdf',
    'ab85991bc3089c7f3936dfe40e7b7d3f31440d3023b83df54b19ec761b75423b', 81, 595, {1: 41, 2: 40})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
