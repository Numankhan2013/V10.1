# Biochemistry learner-visible cleanup handoff — 2026-09-13

## Verified completed batches

### Batch 02 — Chapter 3: Glycogen metabolism and glycogen storage disorders

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Reviewed proposal commit: `b0db23b2582a2530836775495eca95ba40c0f2e6`.
- Verified promotion commit: `1fbc0d94ba4be8b5695574007ac5c2d4e5043865`.
- Promotion/validation workflow: `34749172112` — SUCCESS.
- Stable IDs cleaned: `marrow__BIOCHEM_CH03_Q003`, `Q007`, `Q010`, `Q011`, `Q012`, `Q014`, `Q017`, `Q020`.
- Source pages represented by the reviewed candidate provenance: question pages 45–50; explanation pages 52–59.
- Cleanup only: removed OCR/code-like debris, flattened diagram spillover, and adjacent-solution leakage. No explanation enhancement campaign was performed.
- `correctOption`, answer mapping, question/options, subject/chapter ownership, and immutable raw source were not changed.
- Global effective-bank validation passed through the promotion workflow: full corpus 2,711; exact answer-index invariant; learner-visible question/option candidate count remains 0.
- Effective Biochemistry explanation residual count after promotion: **104**, down from **112** at run start.
- Chapter 3 now has no remaining explanation candidates in the effective debris summary.

## Exact next Biochemistry cleanup point

- Chapter 17 — `Porphyrins and bile pigments`.
- Next deterministic source-order candidate: `marrow__BIOCHEM_CH17_Q001`.
- Question source page 262; explanation source page 270.
- Chapter 17 currently contains 20 explanation candidates and 0 question/option candidates.

## Coordination rule

Before the next mutation, resolve the live heads of both the cleanup lane and `feature/marrow-canonical-full-current`, rebuild/re-read the effective debris audit, and avoid overlapping writes with another cleanup worker. Do not merge this cleanup lane to canonical/main automatically.
