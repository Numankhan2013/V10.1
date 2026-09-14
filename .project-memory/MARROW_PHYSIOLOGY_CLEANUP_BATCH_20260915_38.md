# Marrow Physiology learner-visible cleanup — Batch 38 handoff

- Subject: Physiology.
- Cleanup lane before memory write: `fix/marrow-full-content-cleanup-20260913` at verified promotion commit `afac56ccad0a223a6eb0ebc73c5dc4cd0e4d7f8a`.
- Canonical comparison at the same checkpoint: `feature/marrow-canonical-full-current` at `94edb3af43eb38a1ef762b08c1bdb152c15b3359`. Canonical did not advance during this batch and was not mutated or merged.
- Scope: Chapter 34 — Glomerular Filtration Rate, Renal Blood Flow, and Renal Clearance; explanation-only cleanup for stable IDs `marrow__PHYSIO_CH34_Q001`, `Q002`, `Q003`, `Q004`, `Q006`, `Q008`, `Q011`, and `Q013`.
- Authoritative rendered ED8 explanation pages reviewed: 632–639. Question pages span 622–625; answer-key pages 631–632.
- Cleanup only: removed OCR/serialization debris, source branding/page markers, flattened diagram-label spillover, malformed separators/symbol runs, and garbled table/formula text while retaining source-faithful readable medical prose. Meaningful source table/formula relationships for Q1, Q2, Q4, Q6, and Q13 were retained as readable text; non-prose diagrams were omitted where the prose already stated the relationship. No teaching expansion, beautification, rationale expansion, or stylistic rewrite was added.
- Reviewed proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_034_cleanup_batch_20260915_38.json`; proposal commit `be6320e04865fc41d76a0f80e6b55a0eab665716`.
- Promotion workflow: `34893906361` (`Promote Marrow content cleanup proposals`), promote job `104142998089`, conclusion `success`; every workflow step passed.
- Verified final promotion commit: `afac56ccad0a223a6eb0ebc73c5dc4cd0e4d7f8a`.
- Active Chapter 34 v2 source fingerprint after promotion: `32ec894d7d3bba116ce23b345cb64018bc26f796b07d04d4d375f62b7c790be7`.
- Validation: exact source-fingerprint promotion passed; syntax checks passed; global active-v2 validation passed; complete effective learner-bank rebuild and learner-visible debris scan passed; full 2,711-question raw/effective `correctOption` invariants passed; four-option and correct-answer mapping invariants remained intact because this batch was explanation-only; `questionOptionCandidateQuestions == 0`.
- All eight cleaned Batch 38 IDs disappeared from the regenerated explanation queue. Chapter 34 decreased from 18 to 10 explanation candidates, with 0 question/option candidates.
- Effective residual explanation candidates after final promotion: global 102; Anatomy 1; Biochemistry 6; Physiology 95. Question/option candidates: 0 globally.
- Deferred items in this batch: none among the processed IDs. The batch stopped before Q14 because the first eight candidates already required multiple cross-page tables, diagrams, and formulas; later candidates were not cherry-picked.
- Exact next unresolved Physiology item is `marrow__PHYSIO_CH34_Q014`; question page 625, answer-key pages 631–632, explanation starts page 639 and continues on page 640. Chapter 34 currently has 10 explanation candidates and 0 question/option candidates.
- Nothing was merged to canonical or `main`.
