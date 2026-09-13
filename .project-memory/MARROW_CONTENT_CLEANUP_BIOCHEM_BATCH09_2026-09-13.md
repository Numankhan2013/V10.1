# Marrow learner-content cleanup — Biochemistry Batch 09 — 2026-09-13

- Integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical comparison head at final pre-write check: `feature/marrow-canonical-full-current` = `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; canonical/main were not mutated.
- Subject/chapter: Biochemistry, Chapter 25 — DNA organization, replication and repair.
- Reviewed stable IDs: `marrow__BIOCHEM_CH25_Q001` through `marrow__BIOCHEM_CH25_Q012` (12 questions).
- Rendered Marrow ED8 explanation pages reviewed: 389–395 from `biochemistryed8.pdf`. Embedded/extracted text was treated only as a helper.
- Cleanup scope: explanations only. Removed page markers, OCR symbol garbage, diagram-label spillover and source branding/noise while preserving readable source medical prose. No stem, option, stable ID, `correctOption`, `correctAnswerText` mapping, chapter ownership, provenance or raw source bundle was changed.
- Reviewed proposal path: `data/marrow/content_hygiene_proposals/biochemistry/chapter_025_reviewed_20260913_batch09.json`.
- Proposal commit: `80f20bd3bc45dc47ca2c16cde6edf9d74c967727`.
- Promotion workflow: `34770970305` — SUCCESS.
- Verified promotion commit: `b3c2d3441c21a3314147aed4ae40b1d04c2a0ad2`.
- Validation: global v2 override validation passed; effective 2,711-question audit rebuilt; raw/effective answer indices remained identical; learner-visible question/option candidates remained 0; four-option and answer-mapping contracts remained intact.
- Post-promotion residuals: 371 explanation candidates globally — Anatomy 16, Biochemistry 46, Physiology 309. Biochemistry Chapter 25 has 17 detector candidates remaining.
- Detector false positives retained intentionally rather than distorting valid source notation:
  - `marrow__BIOCHEM_CH25_Q003`: legitimate Chargaff notation `A = T and G = C` triggers `many_isolated_letters`.
  - `marrow__BIOCHEM_CH25_Q011`: legitimate approximate size `~16 kbp` triggers the detector's hard-noise tilde rule.
  Both explanations are source-cleaned and active in the v2 override; these heuristic hits are not learner-content corruption.
- Exact next real source-order cleanup target: `marrow__BIOCHEM_CH25_Q013` (Klenow fragment), question page 384, explanation pages 395–396. Continue from Q13; do not re-clean Q3/Q11 solely to satisfy the detector.
