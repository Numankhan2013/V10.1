# Marrow Physiology learner-visible cleanup — Batch 37 handoff

- Subject: Physiology.
- Cleanup lane before memory write: `fix/marrow-full-content-cleanup-20260913` at verified promotion commit `07276cbc24a5164a925ac8e08510d49d7a03bec7`.
- Canonical comparison at the same checkpoint: `feature/marrow-canonical-full-current` at `94edb3af43eb38a1ef762b08c1bdb152c15b3359`. Canonical did not advance during this batch and was not mutated or merged.
- Scope: Chapter 28 — Cardiac Cycle and Cardiac Output; explanation-only cleanup for stable IDs `marrow__PHYSIO_CH28_Q021`, `Q022`, `Q023`, `Q024`, `Q025`, `Q026`, and `Q027`.
- Authoritative rendered ED8 explanation pages reviewed: 514–518. Question pages span 503–504; answer-key page 505.
- Cleanup only: removed OCR/serialization debris, page markers, graph/diagram-label spillover, source branding/footer material, malformed symbol runs, and cross-question contamination while retaining source-faithful readable medical prose. Diagram material was omitted where source prose already stated the same relationship. Q27's medically meaningful cardiac-output table relationships were retained as plain readable source-faithful text. No teaching expansion, beautification, or stylistic rewrite was added.
- Reviewed proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_028_cleanup_batch_20260915_37.json`; proposal commit `9c7dc5342434db0eb218e984955bb3952525c79d`.
- Promotion workflow: `34887788038` (`Promote Marrow content cleanup proposals`), promote job `104122609195`, conclusion `success`; every workflow step passed.
- Verified final promotion commit: `07276cbc24a5164a925ac8e08510d49d7a03bec7`.
- Active Chapter 28 v2 source fingerprint after promotion: `8482f863a910e87991203b5418cfe49b6de1e269f92646b5db80511acf3d22e1`.
- Validation: exact source-fingerprint promotion passed; syntax checks passed; global active-v2 validation passed; complete effective learner-bank rebuild and debris scan passed; full 2,711-question raw/effective `correctOption` invariants passed; four-option and correct-answer mapping invariants remained intact because this batch was explanation-only; `questionOptionCandidateQuestions == 0`.
- All seven cleaned Batch 37 IDs disappeared from the regenerated explanation queue; Chapter 28 now has no review packet.
- Effective residual explanation candidates after final promotion: global 110; Anatomy 1; Biochemistry 6; Physiology 103. Question/option candidates: 0 globally.
- Deferred items in this batch: none. Earlier low-chapter Physiology residuals already documented as detector false positives/review deferrals remain untouched; this run completed the existing deterministic Chapter 28 continuation rather than skipping an unresolved Chapter 28 item.
- Next ordinary actionable source-order target after the completed Chapter 28 continuation is `marrow__PHYSIO_CH34_Q001` — Chapter 34 Glomerular Filtration Rate, Renal Blood Flow, and Renal Clearance; question page 622, answer-key pages 631–632, explanation start page 632. Chapter 34 currently has 18 explanation candidates and 0 question/option candidates.
- Nothing was merged to canonical or `main`.
