# Biochemistry learner-visible cleanup handoff — 2026-09-13

## Verified completed batches

### Batch 02 — Chapter 3: Glycogen metabolism and glycogen storage disorders

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Reviewed proposal commit: `b0db23b2582a2530836775495eca95ba40c0f2e6`.
- Verified promotion commit: `1fbc0d94ba4be8b5695574007ac5c2d4e5043865`.
- Promotion/validation workflow: `34749172112` — SUCCESS.
- Stable IDs cleaned: `marrow__BIOCHEM_CH03_Q003`, `Q007`, `Q010`, `Q011`, `Q012`, `Q014`, `Q017`, `Q020`.
- Effective Biochemistry explanation residual count after promotion: **104**, down from **112**.

### Batch 03 — Chapter 17: Porphyrins and bile pigments, Q1–Q12

- Reviewed proposal commit: `c0322b9e7f0157cad452df1ab55e30b2c4e3ba5d`.
- Verified promotion commit: `22fef0823f0e0c87702403c2261772924151b244`.
- Promotion/validation workflow: `34751308008` — SUCCESS.
- Stable IDs cleaned: `marrow__BIOCHEM_CH17_Q001` through `marrow__BIOCHEM_CH17_Q012`.
- Rendered source pages: 270–276 from verified `biochemistryed8.pdf`.
- Effective Biochemistry explanation residual count: **94**, down from **104**.

### Batch 04 — Chapter 17 remainder

- Verified promotion commit: `dae5f6b5ea85728da58a3081f129a4635b12365c`.
- CLEANED IDs: `marrow__BIOCHEM_CH17_Q013`, `Q014`, `Q016`, `Q017`, `Q018`, `Q019`, `Q020`, `Q022`, `Q023`, `Q024`.
- Effective Biochemistry explanation residual count: **84**, down from **94**.
- Chapter 17 cleared from the effective debris queue.

### Batch 05 — Chapter 18: Enzymes - Mechanism of Action & Clinical Importance

- Cleanup head before reviewed proposal: `7a83ba29441c33afa709b03646338b0e668c0809`.
- Canonical head checked before mutation: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no intersecting Biochemistry cleanup mutation.
- Reviewed proposal commit: `11d1962efa7e795ebdfff6419807b2f3a701bda5`.
- Verified promotion commit: `8ce27142e72b8461b1a213858ce223ae61b9c26b`.
- Promotion/validation workflow: `34756630261` — SUCCESS.
- Rendered source pages inspected: 289–296 of verified `biochemistryed8.pdf`.
- CLEANED IDs: `marrow__BIOCHEM_CH18_Q001`, `Q003`, `Q005`, `Q006`, `Q007`, `Q008`, `Q010`, `Q012`, `Q013`, `Q014`, `Q015`, `Q016`.
- Cleanup-only: OCR/symbol debris and malformed flattened diagram/table transcription removed; source-verifiable LDH table relationships were retained as clean prose. No explanation tuning or medical expansion.
- Full 2,711-question effective-bank validation passed; raw/effective answer indices identical; `questionOptionCandidateQuestions` remains **0**.
- Effective Biochemistry explanation residual count: **72**, down from **84**. Global explanation residuals: Anatomy 36, Biochemistry 72, Physiology 344; total 452.
- Chapter 18 now has one explanation candidate remaining and zero question/option candidates.

## Exact next Biochemistry cleanup point

- Chapter 18 — `Enzymes - Mechanism of Action & Clinical Importance`.
- Next deterministic source-order candidate: `marrow__BIOCHEM_CH18_Q017`.
- Question source pages 287–288; explanation source page 296.
- Do not skip Q17. After it is resolved, rebuild the effective queue and continue to the next source-order chapter.

## Coordination rule

Before every mutation, resolve the live heads of both the cleanup lane and `feature/marrow-canonical-full-current`, rebuild/re-read the effective debris audit, and avoid overlapping writes with another cleanup worker. Do not merge this cleanup lane to canonical/main automatically.
