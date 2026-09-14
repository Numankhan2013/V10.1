# Biochemistry learner-visible content cleanup — Batch 15 (2026-09-14)

## Scope

- Subject: Biochemistry
- Cleanup lane: `fix/marrow-full-content-cleanup-20260913`
- Proposal commit: `3d21d0de29419096d81e4b8477f49b100c20a91e`
- Verified promotion commit: `3f20806e7d959d0ebd4051291c3763eb7e02bac5`
- Promotion workflow: `34792214034`
- Stable ID cleaned: `marrow__BIOCHEM_CH28_Q023`
- Chapter: 28 — Molecular genetics, recombinant DNA & genomic technologies
- Source provenance: question pages 436–437; answer-key pages 438–439; explanation pages 446–447.

## Cleanup performed

Q23 had intact explanatory prose followed by clearly separable OCR spillover from the karyotype image. The reviewed proposal preserved the explanatory prose exactly as present in the effective source and removed only the non-prose karyotype OCR tail. No stem, option, figure, stable ID, source provenance, correctOption, correctAnswerText, chapter ownership, or immutable raw bundle was changed.

Proposal path:
`data/marrow/content_hygiene_proposals/biochemistry/chapter_028_reviewed_20260914_batch15.json`

## Validation

Promotion workflow `34792214034` completed successfully.

- v2 override validator: PASS — 32 files / 389 questions / 872 changed fields / 364 explanation overrides.
- Full effective audit rebuild: PASS — 2,711 questions.
- Raw/effective correctOption invariant: PASS — all 2,711 IDs identical.
- Learner-visible debris audit: PASS.
- `questionOptionCandidateQuestions == 0`: PASS.
- Q23 is absent from the post-promotion explanation debris queue.
- Four-option count and `correctAnswerText` were unchanged because the proposal is explanation-only.
- No runtime output path was modified, so no browser/build regression was required for this batch.

Post-promotion residual explanation candidates:
- Anatomy: 1
- Biochemistry: 6
- Physiology: 241
- Global: 248

Biochemistry residual composition:
- Chapter 25: 2 previously documented legitimate detector false positives.
- Chapter 28: 4 real unresolved candidates (Q24–Q27).

## Deferral / next target

Exact next unresolved Biochemistry item: `marrow__BIOCHEM_CH28_Q024`, source question page 437, explanation pages 447–448.

Q24 and Q25 contain OCR corruption embedded inside medically meaningful prose. This run did not infer or silently repair that wording because the binary PDF could not be rendered through the current repository connector. They remain `REVIEW_REQUIRED` until the rendered ED8 pages can be inspected. Q26 and Q27 remain later in deterministic source order and were not cherry-picked past Q24/Q25.

The repository copy of `data/marrow/source_pdfs/biochemistryed8.pdf` remains the authoritative source (blob `d8289d237572150efd636e22abea31e32da67ba6`).
