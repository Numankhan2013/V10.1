"""Bounded two-block Male Reproductive System collection."""
from uworld_imported_collection import ImportedCollection

OWNER = ImportedCollection(
    'male_reproductive_system', 'Male Reproductive System',
    'data/uworld/Source_pdfs/Male_reproductive_system/UW 2024 - Male Reproductive System - 2 blocks - OCR.pdf',
    '1b06296226be118da84743cd9cf8abed7c3e669dd260543734dbf27cefcf6c24', 52, 281, {1: 39, 2: 13})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
