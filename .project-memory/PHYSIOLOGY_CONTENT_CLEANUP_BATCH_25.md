# Physiology learner-visible cleanup — Batch 25

## Scope

- Subject: Physiology
- Chapter: 19 — Functional Anatomy
- Cleanup-only campaign on `fix/marrow-full-content-cleanup-20260913`.
- Stable IDs reviewed and cleaned in this bounded source-order batch:
  - `marrow__PHYSIO_CH19_Q005`
  - `marrow__PHYSIO_CH19_Q006`
  - `marrow__PHYSIO_CH19_Q010`
- Rendered Marrow ED8 Physiology source pages reviewed: **358, 359, 360, 362**. Relevant question pages were **353–354** and answer-key page **355**. Rendered source, not corrupted embedded PDF text, was authoritative.
- No raw Marrow bundle mutation. No stable ID, chapter ownership, figure, option order, `correctOption`, or answer mapping changes.
- No teaching expansion, Key Takeaway, new rationale section, medical correction, or stylistic rewrite was added. Cleanup was limited to source-faithful readable explanation prose and removal/omission of OCR-flattened diagram/table debris.

## Source/proposal/promotion

- Proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_019_cleanup_batch_20260914_25.json`
- Reviewed proposal commit: `ae085ba2b138c60aa02803c6a396d8b83e4b5328`
- Active v2 override: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_019.json`
- Active source fingerprint: `0ce2dbe082017a41a1793bb1af70ef91c1c1d27c3faff4ab20b73883bd928a55`
- Promotion workflow: `34818873287`
- Verified promotion commit: `c03775b15a62f28424452fd175ca08c1270ed20f`

## Validation

Promotion workflow passed all required gates:

- Reviewed proposal promotion with exact raw-source fingerprints: PASS.
- Global v2 override validator: PASS (`files=35 questions=440 changed_fields=924 explanations=416`).
- Full effective-bank rebuild: PASS, exactly **2,711 questions**.
- Raw/effective `correctOption` maps: identical for all **2,711 questions**.
- Effective learner-visible debris audit: PASS.
- `questionOptionCandidateQuestions == 0` globally.
- Effective explanation candidates: **197 globally**.
  - Anatomy: **1**
  - Biochemistry: **6**
  - Physiology: **190**
- Chapter 19 is absent from the regenerated explanation review queue; all three targeted IDs cleared the detector.
- Four-option counts and correct-answer mappings remain preserved; this batch changed explanations only.
- No source footer/branding/serialization/code marker remains in the reviewed learner-visible content.
- Runtime output paths were not touched, so an additional browser/build regression was not required for this batch.

## Source-specific notes

- Q5: retained the readable salbutamol/VIP/NANC and clinical-relevance prose; omitted the OCR-flattened bronchial-innervation table/diagram debris because its malformed non-prose transcription was not needed for the answer explanation.
- Q6: retained the readable Type I/Type II pneumocyte and other-cell prose; omitted the flattened alveolus diagram labels and OCR garbage.
- Q10: restored the rendered-source relationship `Pulmonary surfactant: ↓ surface tension within alveoli` and retained the readable interdependence explanation.

## Exact next Physiology target

The earlier lower-chapter residuals are already documented deferrals or detector false-positives from prior reviewed batches. The next ordinary actionable source-order target is:

`marrow__PHYSIO_CH20_Q001` — Chapter 20, Lung Mechanics

- Question page: **365**
- Answer-key page: **371**
- Explanation page: **372**
- Chapter 20 currently has **11 explanation candidates** and **0 question/option candidates**.
- Continue in deterministic Chapter 20 source order from Q1 on the next bounded Physiology run.

## Lineage/coordination

Immediately before this memory write:

- Cleanup head: `c03775b15a62f28424452fd175ca08c1270ed20f`
- Canonical head: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`

Canonical did not advance into an intersecting Chapter 19 cleanup scope. Chapter 19 had no pre-existing active v2 override and no competing unfinished shared write was observed. Nothing was merged to canonical or `main`.
