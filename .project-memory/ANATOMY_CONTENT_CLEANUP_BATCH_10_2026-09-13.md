# Anatomy content cleanup — Batch 10 — 2026-09-13

Status: **CLEANED / VERIFIED**

## Scope
- Subject: Anatomy
- Chapter 26: Vascular supply of Brain
- Stable IDs cleaned:
  - `marrow__ANAT_CH26_Q015`
  - `marrow__ANAT_CH26_Q016`
  - `marrow__ANAT_CH26_Q017`
- Authoritative source: `marrow ed 8 qbank_compressed.pdf`
- Rendered source pages reviewed: 453–456
- Question pages: Q15–Q16 p441; Q17 p442
- Answer-key page: p443

## Cleanup performed
- Q15: preserved the readable posterior-limb internal-capsule blood-supply prose and removed OCR-flattened labels from the horizontal/coronal brain figures.
- Q16: preserved the single readable source sentence and removed OCR-flattened basal-ganglia figure labels.
- Q17: reconstructed only the readable source prose on acute subdural hematoma and superficial/deep cerebral venous drainage; removed the flattened venous-drainage diagram labels.
- No stem, option, correctOption, correctAnswerText mapping, stable ID, provenance, chapter ownership, figure binding, or immutable raw source was intentionally changed.

## Git / promotion
- Reviewed proposal commit: `3575bea58fb8b1bbdbfa240c711317da0f63f6af`
- Promotion workflow: `34770004242` — **SUCCESS**
- Verified promotion commit: `871354bca6bb270922856ace925259a8ea8edecf`
- Promotion gate included source-fingerprint promotion, global v2 validation, full effective-bank rebuild/debris scan, 2,711-question corpus invariant, raw/effective answer-index identity, and `questionOptionCandidateQuestions == 0`.

## Effective residual after promotion
- Question/option candidates: **0**
- Explanation candidates: **381 total**
  - Anatomy: **16**
  - Biochemistry: **56**
  - Physiology: **309**
- Chapter 26 is no longer present in the Anatomy explanation-review directory.
- Anatomy Ch14 retains the previously reviewed legitimate-table-separator detector false-positive and must not be source-distorted merely to satisfy the heuristic.

## Exact next Anatomy work
- Next real source-order candidate: `marrow__ANAT_CH51_Q002` — Chapter 51 `KUB & Adrenal Gland`
- Question page: 940
- Answer-key page: 950
- Explanation page: 951
- Chapter 51 currently has 10 explanation candidates and 0 question/option candidates.

Do not merge this cleanup campaign into canonical or main automatically. Re-resolve live cleanup and canonical heads before the next mutation.
