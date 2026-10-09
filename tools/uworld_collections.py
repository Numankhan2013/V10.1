"""Explicit bounded collection registry; no automatic whole-corpus import."""
import uworld_biochemistry
import uworld_poisoning
import uworld_ophthalmology
import uworld_male_reproductive
import uworld_female_reproductive
import uworld_biostatistics
import uworld_general_pharmacology
import uworld_psychiatric_behavioral_substance_use
import uworld_pregnancy_childbirth_puerperium
import uworld_endocrine_diabetes_metabolism
import uworld_pathology_general_principles
import uworld_cardiovascular_system
import uworld_renal_urinary_electrolytes
from uworld_content_hygiene import learner_question

COLLECTIONS = (uworld_biochemistry, uworld_poisoning, uworld_ophthalmology,
               uworld_male_reproductive, uworld_female_reproductive, uworld_biostatistics,
               uworld_general_pharmacology,
               uworld_pathology_general_principles, uworld_endocrine_diabetes_metabolism, uworld_pregnancy_childbirth_puerperium, uworld_psychiatric_behavioral_substance_use,
               uworld_cardiovascular_system, uworld_renal_urinary_electrolytes)


def bank_records():
    records = [owner.bank_record() for owner in COLLECTIONS]
    ids = [q['id'] for record in records for q in record['questions']]
    if len(ids) != len(set(ids)):
        raise ValueError('UWorld stable question identity collision')
    for record in records:
        record['questions'] = [learner_question(q) for q in record['questions']]
    return records


def media_sources():
    for owner in COLLECTIONS:
        manifest, rows = owner.load_source()
        docs = (uworld_biochemistry.load_reviewed(rows, manifest['source_sha256'])
                if owner is uworld_biochemistry else owner.reviewed_documents(rows))
        yield owner.PDF, manifest, docs
