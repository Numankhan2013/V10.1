# Marrow learner-content cleanup progress

## 2026-09-13 — Physiology cleanup batch 01

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical comparison immediately before/after the batch: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; the concurrent canonical advance is Anatomy-only (`Checkpoint Anatomy Q8-Q18 canonical certification`) and does not intersect this Physiology batch.
- Reviewed proposal commit: `cb09558bd8deb55369d33516f79e5174fce6f82a`.
- Verified promotion commit: `3c47ef5d898af81c0ef7fc871f5b2a193487c913`.
- Promotion/validation workflow: `34745656328`, SUCCESS.
- Source reviewed: verified Marrow ED8 Physiology rendered pages 41-43 for Chapter 3 `Transport Across Cell Membrane`.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_003.json`.
- Reviewed IDs: `marrow__PHYS_CH03_Q001`, `marrow__PHYS_CH03_Q002`, `marrow__PHYS_CH03_Q004`, `marrow__PHYS_CH03_Q005`.
- Q1, Q2 and Q5 are detector-clean after source-faithful explanation reconstruction; no learner-visible stem/option regressions were introduced.
- Q4 is also source-reviewed and learner-clean, but remains in the broad explanation review queue as a documented detector false-positive: the detector flags legitimate diffusion equations / isolated formula symbols (`many_isolated_letters`, `symbol_dense_line`) and short equation/result lines (`edge_noise`). Do not rewrite or delete these medically meaningful equations merely to satisfy the heuristic detector.
- Effective residual after promotion: 545 explanation candidates globally; Anatomy 59, Biochemistry 120, Physiology 366. `questionOptionCandidateQuestions` remains exactly 0.
- Correct-option indexes remain immutable; the promotion workflow rebuilt the complete 2,711-question effective bank and passed the global answer-index and v2 validation gates.
- Exact next unresolved Physiology source-order item requiring cleanup: `marrow__PHYS_CH03_Q006`, explanation pages 43-44. Continue in Chapter 3 source order; Q4 may be skipped only as the documented detector false-positive above.
