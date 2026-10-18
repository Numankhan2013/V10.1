"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/ent/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    'ent', 'Ear, Nose & Throat',
    'data/uworld/Source_pdfs/ent/Ear, Nose & Throat (ENT) - 1 block.pdf',
    'e4e1218e96beced952c77a630c01734121f5ef297d2afb6f743902195441d16c', 15, 261, {1: 15})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
