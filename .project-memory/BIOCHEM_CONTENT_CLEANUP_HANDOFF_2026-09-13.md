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

### Batch 03 — Chapter 17: Porphyrins and bile pigments, Q1–Q12

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Live cleanup head before mutation: `643291a8b65b2bee803670f5c9623774b9192613`.
- Live canonical head checked before mutation: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no overlapping Biochemistry cleanup mutation was present.
- Reviewed proposal commit: `c0322b9e7f0157cad452df1ab55e30b2c4e3ba5d`.
- Verified promotion commit: `22fef0823f0e0c87702403c2261772924151b244`.
- Promotion/validation workflow: `34751308008` — SUCCESS.
- Stable IDs cleaned: `marrow__BIOCHEM_CH17_Q001` through `marrow__BIOCHEM_CH17_Q012`.
- Rendered source pages inspected directly from verified `biochemistryed8.pdf`: explanation pages 270–276; embedded text was treated as unreliable where corrupted.
- Cleanup only: removed OCR symbol noise, footer/brand spillover, diagram OCR flattening, malformed separators, and corrupted source-transcription fragments. Diagram relationships were retained as prose only where they were medically meaningful and visually verifiable from the rendered source.
- No gold-standard tuning, new Key Takeaways, added teaching content, or answer changes were introduced.
- `correctOption`, answer mapping, question/options, subject/chapter ownership, figure ownership, and immutable raw source were not changed.
- Global promotion validation passed: full corpus 2,711; exact answer-index invariant; learner-visible question/option candidate count remains **0**.
- Effective Biochemistry explanation residual count after promotion: **94**, down from **104** at run start.
- Global explanation residuals after this promotion: Anatomy 43, Biochemistry 94, Physiology 350; total 487.
- Chapter 17 residual explanation candidates: **10**.

## Exact next Biochemistry cleanup point

- Chapter 17 — `Porphyrins and bile pigments`.
- Next deterministic source-order candidate: `marrow__BIOCHEM_CH17_Q013`.
- Question source page 265; explanation source page 277.
- Chapter 17 currently contains 10 remaining explanation candidates and 0 question/option candidates.

## Coordination rule

Before the next mutation, resolve the live heads of both the cleanup lane and `feature/marrow-canonical-full-current`, rebuild/re-read the effective debris audit, and avoid overlapping writes with another cleanup worker. Do not merge this cleanup lane to canonical/main automatically.
