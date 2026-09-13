# Physiology learner-visible content cleanup — Batch 05

- Cleanup lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup branch immediately before mutation: `d2630536cb39f612f8560fe0476139c9d31a6c44`.
- Canonical head checked immediately before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no intersecting Physiology Chapter 4 cleanup ownership was identified.
- Source of truth: verified Marrow ED8 Physiology `physiologyed8.pdf`, rendered pages 62–67.
- CLEANED stable IDs: `marrow__PHYS_CH04_Q004`, `marrow__PHYS_CH04_Q005`, `marrow__PHYS_CH04_Q009`, `marrow__PHYS_CH04_Q010`, `marrow__PHYS_CH04_Q012`, `marrow__PHYS_CH04_Q014`.
- Scope: explanation cleanup only. Removed OCR/flattened-diagram/footer debris and reconstructed only readable source-faithful prose/formula text. Raw corpus, stems, options, `correctOption`, correct-answer mapping, figures, provenance, stable IDs and chapter ownership were not mutated.
- Reviewed proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_004_cleanup_batch_20260913_02.json`, commit `970e8e93d04d29d32a12a0c885204924bc2fef31`.
- Promotion/validation workflow: `34754763360`, SUCCESS. Every job/step passed, including v2 validation, effective-bank rebuild/debris scan, 2,711-corpus assertion, raw/effective answer-index equality and `questionOptionCandidateQuestions == 0`.
- Verified promotion commit: `6e6fe4476d694381523f1db417772d8cbea7c3fe`.
- Effective residual after this batch and concurrent subject cleanup: 467 explanation-candidate questions globally; Anatomy 39, Biochemistry 84, Physiology 344; question/option candidates remain 0 across all subjects.
- Chapter 4 now has only three detector entries. Q1 and Q3 are previously reviewed legitimate-notation/equation false positives. Q4 is now source-clean but remains detector-flagged solely because the valid source phrase `(+/-)` triggers the broad `punctuation_run` heuristic. Do not delete or rewrite medically meaningful notation merely to satisfy the detector. Q5, Q9, Q10, Q12 and Q14 are absent from the residual Chapter 4 packet.
- Chapter 3 has one previously reviewed legitimate-equation false positive (Q4), so the next genuine unresolved source-order cleanup target is `marrow__PHYS_CH05_Q001` in Chapter 5 `Body Fluids`, source question page 68 and explanation pages 77–78. Continue from the newly rebuilt effective audit rather than stale counts.
- Production/main/canonical were not promoted or mutated by this batch.
