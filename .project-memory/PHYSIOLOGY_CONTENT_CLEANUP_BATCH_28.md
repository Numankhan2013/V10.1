# Physiology learner-visible cleanup — Batch 28

## Scope

- Subject: Physiology
- Cleanup-only campaign on `fix/marrow-full-content-cleanup-20260913`.
- Deterministic source-order scope: Chapter 23 — Lung Volumes and Lung Function Tests.
- Cleaned the first three unresolved explanation candidates only because Chapter 23 contains high-complexity OCR spillover and Q4's effective OCR text had swallowed material from later questions:
  - `marrow__PHYSIO_CH23_Q002`
  - `marrow__PHYSIO_CH23_Q004`
  - `marrow__PHYSIO_CH23_Q006`
- Rendered Marrow ED8 Physiology explanation pages reviewed: **424–426**. Rendered source was authoritative; corrupted embedded text/OCR was not used to infer wording.
- Diagram/table OCR debris, branding, malformed labels, and later-question spillover were omitted. Only readable source-faithful explanation prose and verifiable relationships were retained.
- No raw Marrow bundle mutation. No stable ID, chapter ownership, figure, option order, `correctOption`, or answer mapping changes.
- No Key Takeaway, teaching expansion, new rationale section, medical correction, or stylistic rewrite was added.

## Lineage reconciliation before mutation

- Cleanup head immediately before proposal write: `a4aacf014dcdd84c1c0023b7ad33428fb4fffd54`.
- Canonical had advanced from the prior handoff to `cb37f577bd4cbe59e4005018d24dc7ba0f0bad18`.
- The canonical delta from the previous canonical checkpoint changed FSRS/question-presentation/product files and project memory only; it did **not** intersect Chapter 23 Marrow source, cleanup proposals, v2 overrides, or the targeted stable IDs.
- Therefore no stable-ID content transplant/reconciliation was required for this batch, and no newer canonical content was overwritten.

## Source/proposal/promotion

- Proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_023_cleanup_batch_20260914_28.json`
- Reviewed proposal commit: `d2ab90822764eb04d53f82012f007f37f811e8ff`
- Promotion workflow: `34833788960`
- Verified promotion commit: `255914c52b0e8b328999a83554fd21d7e858c428`
- Active Chapter 23 v2 source fingerprint: `9093699259666b3ee04f09a2146b410358d54b84899d690aa9335a55a61c7473`

## Validation

Promotion workflow passed every required gate:

- Reviewed proposal promotion with exact raw-source fingerprints: PASS.
- Syntax/build-owner cleanup-tool check: PASS.
- Global v2 override validator: PASS.
- Full effective-bank rebuild and learner-visible debris scan: PASS.
- Corpus invariant: exactly **2,711 questions**.
- Raw/effective `correctOption` maps: identical for all **2,711 questions**.
- `questionOptionCandidateQuestions == 0` globally.
- Effective explanation candidates after promotion: **172 globally**.
  - Anatomy: **1**
  - Biochemistry: **6**
  - Physiology: **165**
- Chapter 23 explanation candidates: **11**, down from **14**.
- Q2, Q4, and Q6 are absent from the regenerated Chapter 23 explanation queue.
- Four-option count and `correctAnswerText` mapping remain preserved; this batch changed explanations only.
- No source footer/brand/serialized-code marker remains in the three cleaned learner-visible explanations.
- Runtime output paths were not changed, so no additional product/browser build regression was required beyond the deterministic promotion gates.

## Source-specific notes

- Q2: retained the readable FRC definition and lung-capacity prose; omitted the OCR-flattened lung-volume diagram labels and source branding.
- Q4: the prior effective OCR explanation incorrectly contained material belonging to Q5 through Q18. Restored only the rendered-source Q4 spirometry/residual-volume explanation and removed the cross-question spillover.
- Q6: retained the readable Fowler-method/dead-space prose, regions and measurement notes. The malformed rendered table under “Factors affecting dead space” was omitted rather than reconstructed from uncertain OCR because it was supplementary and not required to preserve the verifiable explanation.

## Exact next Physiology target

The regenerated source-order queue now begins with:

`marrow__PHYSIO_CH23_Q007` — Chapter 23, Lung Volumes and Lung Function Tests

- Question page: **418**
- Answer-key page: **423**
- Explanation page: **427**
- Chapter 23 currently has **11 explanation candidates** and **0 question/option candidates**.

## Final coordination state

Immediately before this memory write:

- Cleanup head: `255914c52b0e8b328999a83554fd21d7e858c428`
- Canonical head: `cb37f577bd4cbe59e4005018d24dc7ba0f0bad18`

No competing unfinished Chapter 23 cleanup proposal/override write was observed. Nothing was merged to canonical or `main`.
