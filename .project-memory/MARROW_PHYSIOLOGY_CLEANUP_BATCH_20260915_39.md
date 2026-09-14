# Marrow Physiology learner-visible cleanup — Batch 39 handoff

- Subject: Physiology.
- Cleanup lane before memory write: `fix/marrow-full-content-cleanup-20260913` at verified promotion commit `27b8cca27ca1f44faeafc95a5993e8ac1640989f`.
- Canonical comparison at the same checkpoint: `feature/marrow-canonical-full-current` at `94edb3af43eb38a1ef762b08c1bdb152c15b3359`. Canonical did not advance during this batch and was not mutated or merged.
- Scope: Chapter 34 — Glomerular Filtration Rate, Renal Blood Flow, and Renal Clearance; explanation-only cleanup for stable IDs `marrow__PHYSIO_CH34_Q014`, `Q015`, `Q018`, `Q021`, `Q023`, `Q024`, `Q026`, `Q028`, and `Q035`.
- Authoritative rendered ED8 pages reviewed for the remaining Chapter 34 queue: 639–651. Cleaned explanation source spans: Q14 pages 639–640; Q15 pages 640–641; Q18 page 643; Q21 page 644; Q23 pages 645–646; Q24 page 646; Q26 pages 646–647; Q28 page 648; Q35 pages 650–651. Q30 was also reviewed on page 649 and deliberately deferred as described below. Question pages for this batch span 625–630; answer-key pages 631–632.
- Cleanup only: removed OCR/serialization debris, source branding/page markers, malformed separators/symbol noise, and flattened diagram/table spillover while retaining source-faithful readable medical prose. Verifiable formula/table/diagram relationships were retained textually where needed; non-prose diagram debris was omitted where the source prose already carried the same relationship. No teaching expansion, beautification, rationale expansion, or stylistic rewrite was added.
- Reviewed proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_034_cleanup_batch_20260915_39.json`; proposal commit `e2ed28ef6002f27cc40fc746b9a37d388fcc3225`.
- Promotion workflow: `34900167717` (`Promote Marrow content cleanup proposals`), promote job `104163962298`, conclusion `success`; every workflow step passed.
- Verified final promotion commit: `27b8cca27ca1f44faeafc95a5993e8ac1640989f`.
- Active Chapter 34 v2 source fingerprint after promotion: `4480913f05369d571e6c7fb0165e9516a39e8f0840e5dc7a969770fe8e02b511`.
- Validation: exact source-fingerprint promotion passed; syntax checks passed; global active-v2 validation passed; complete effective 2,711-question learner-bank rebuild and learner-visible debris scan passed; full raw/effective `correctOption` invariants passed; four-option and correct-answer mapping invariants remained intact because this batch was explanation-only; `questionOptionCandidateQuestions == 0`.
- All nine cleaned Batch 39 IDs disappeared from the regenerated explanation queue. Chapter 34 decreased from 10 to 1 explanation candidate, with 0 question/option candidates.
- Effective residual explanation candidates after final promotion: global 93; Anatomy 1; Biochemistry 6; Physiology 86. Question/option candidates: 0 globally.
- Deferred item: `marrow__PHYSIO_CH34_Q030`. On authoritative rendered ED8 page 649 the key word appears twice with an unreadable missing-glyph block immediately before `ow`; the exact source letters cannot be established from the rendered page without inference. Per fail-closed policy, no reconstruction from medical context was made. Status: `REVIEW_REQUIRED` pending a source rendering/font recovery or other authoritative visual evidence.
- Exact next unresolved Physiology item remains `marrow__PHYSIO_CH34_Q030`; question page 629, answer-key pages 631–632, explanation page 649. Chapter 34 currently has 1 explanation candidate and 0 question/option candidates.
- Nothing was merged to canonical or `main`.
