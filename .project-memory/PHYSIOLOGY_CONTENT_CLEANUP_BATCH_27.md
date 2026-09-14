# Physiology learner-visible cleanup — Batch 27

## Scope

- Subject: Physiology
- Cleanup-only campaign on `fix/marrow-full-content-cleanup-20260913`.
- Source-order review began with Chapter 21 — Alveolar Gas Exchange. Rendered Marrow ED8 Physiology source established that the three remaining Chapter 21 detector hits are legitimate scientific notation rather than learner-visible corruption:
  - `marrow__PHYSIO_CH21_Q001`: Fick-law equation is genuine source notation.
  - `marrow__PHYSIO_CH21_Q003`: R→L anatomic-shunt notation is legitimate.
  - `marrow__PHYSIO_CH21_Q012`: `~0.8` ventilation/perfusion notation is legitimate.
- These Chapter 21 items were preserved unchanged and documented as detector false-positives rather than rewritten merely to satisfy the heuristic.
- The bounded cleanup batch then proceeded to the next source-order chapter, Chapter 22 — Gas Transport in Blood, and cleaned all eleven genuine explanation-corruption candidates:
  - `marrow__PHYSIO_CH22_Q002`
  - `marrow__PHYSIO_CH22_Q004`
  - `marrow__PHYSIO_CH22_Q005`
  - `marrow__PHYSIO_CH22_Q008`
  - `marrow__PHYSIO_CH22_Q010`
  - `marrow__PHYSIO_CH22_Q011`
  - `marrow__PHYSIO_CH22_Q012`
  - `marrow__PHYSIO_CH22_Q014`
  - `marrow__PHYSIO_CH22_Q018`
  - `marrow__PHYSIO_CH22_Q019`
  - `marrow__PHYSIO_CH22_Q020`
- Rendered Marrow ED8 Physiology explanation pages reviewed for Chapter 22: **405–415**. Rendered source, not corrupted embedded PDF text, was authoritative.
- No raw Marrow bundle mutation. No stable ID, chapter ownership, figure, option order, `correctOption`, or answer mapping changes.
- No teaching expansion, Key Takeaway, new rationale section, medical correction, or stylistic rewrite was added. Cleanup was limited to source-faithful readable explanation content and removal/omission of OCR-flattened diagram/graph/branding debris.

## Source/proposal/promotion

- Proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_022_cleanup_batch_20260914_27.json`
- Reviewed proposal commit: `056731f2309d83704b6fb67ee318a3af510522be`
- Promotion workflow: `34829044291`
- Verified promotion commit: `7cd3ba5488a63731989d5bc4ee518564c560d085`

## Validation

Promotion workflow passed all required gates:

- Reviewed proposal promotion with exact raw-source fingerprints: PASS.
- Global v2 override validator: PASS.
- Full effective-bank rebuild: PASS, exactly **2,711 questions** by workflow invariant.
- Raw/effective `correctOption` maps: identical for all **2,711 questions** by workflow invariant.
- Effective learner-visible debris audit: PASS.
- `questionOptionCandidateQuestions == 0` globally.
- Effective explanation candidates after promotion: **175 globally**.
  - Anatomy: **1**
  - Biochemistry: **6**
  - Physiology: **168**
- Chapter 22 is absent from the regenerated explanation review queue; all eleven targeted IDs cleared the detector.
- Four-option counts and correct-answer mappings remain preserved; this batch changed explanations only.
- No source footer/branding/serialization/code marker remains in the cleaned Chapter 22 learner-visible explanations.
- Runtime output paths were not touched, so an additional browser/build regression was not required for this batch.

## Source-specific notes

- Chapter 21 Q1/Q3/Q12 were deliberately not changed: rendered-source review confirmed the detector was flagging legitimate notation, not debris.
- Chapter 22 Q5: source flowchart relationships were reconstructed only as readable source-faithful text; malformed diagram labels/branding were omitted.
- Q8: the prior effective explanation had OCR-concatenated material from later questions; only the rendered-source Q8 explanation prose was retained.
- Q10/Q11/Q12: graph/curve OCR debris was omitted while the readable source prose and relationships were preserved.
- Q19: a rendered equation operator was not confidently readable; the unreadable non-prose equation debris was omitted rather than inferred, while surrounding source prose and verifiable relationships were preserved.
- Q20: graph OCR debris was omitted; readable source prose and source numerical values were retained.

## Exact next Physiology target

The next ordinary source-order actionable Physiology item in the regenerated queue is:

`marrow__PHYSIO_CH23_Q002` — Chapter 23, Lung Volumes and Lung Function Tests

- Question page: **416**
- Answer-key page: **423**
- Explanation page: **424**
- Chapter 23 currently has **14 explanation candidates** and **0 question/option candidates**.

## Lineage/coordination

Immediately before this memory write:

- Cleanup head: `7cd3ba5488a63731989d5bc4ee518564c560d085`
- Canonical head: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`

Canonical did not advance into an intersecting Chapter 21/22 cleanup scope. No competing unfinished Physiology Chapter 22 cleanup write was observed. Nothing was merged to canonical or `main`.
