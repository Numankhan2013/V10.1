"""Explicit bounded collection registry; no automatic whole-corpus import."""
import uworld_biochemistry
import uworld_poisoning

COLLECTIONS = (uworld_biochemistry, uworld_poisoning)


def bank_records():
    records = [owner.bank_record() for owner in COLLECTIONS]
    ids = [q['id'] for record in records for q in record['questions']]
    if len(ids) != len(set(ids)):
        raise ValueError('UWorld stable question identity collision')
    return records


def media_sources():
    for owner in COLLECTIONS:
        manifest, rows = owner.load_source()
        docs = (owner.reviewed_documents(rows) if owner is uworld_poisoning else
                uworld_biochemistry.load_reviewed(rows, manifest['source_sha256']))
        yield owner.PDF, manifest, docs
