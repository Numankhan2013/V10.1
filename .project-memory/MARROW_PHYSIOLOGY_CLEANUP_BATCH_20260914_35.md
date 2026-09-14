# Marrow Physiology learner-visible cleanup — Batch 35 handoff

- Subject: Physiology.
- Cleanup lane before memory write: `fix/marrow-full-content-cleanup-20260913` at verified promotion commit `533c33fcbacd971d14f6ec7f1f3794818bedd887`.
- Canonical comparison at the same checkpoint: `feature/marrow-canonical-full-current` at `94edb3af43eb38a1ef762b08c1bdb152c15b3359`. Canonical did not advance during this batch and was not mutated or merged.
- Reviewed proposal commit: `e44593b8ecd9ee7368be36bbca60ce16dc65fb4a`.
- Promotion workflow: `34875760759` (`Promote Marrow content cleanup proposals`), conclusion `success`; promote job `104082415552` passed every step.
- Verified promotion commit: `533c33fcbacd971d14f6ec7f1f3794818bedd887`.
- Scope: Chapter 27 — Vascular System and Regional Circulation II; explanation-only cleanup for stable IDs `marrow__PHYSIO_CH27_Q002`, `Q004`, `Q005`, `Q006`, `Q009`, `Q011`, `Q014`, `Q015`, `Q017`, and `Q018`.
- Authoritative rendered ED8 explanation pages reviewed: 489–496. Question pages span 483–488; answer-key pages 488–489.
- Cleanup only: removed page-number/source-footer material, OCR garbage, malformed table/equation text, diagram-label spillover, cross-question solution spillover, meaningless symbol fragments, and source branding while preserving readable source medical prose and verifiable relationships. Q9's readable organ-flow table was retained as plain textual row relationships. Q15 and Q18 diagram OCR was omitted because the readable source prose stated the necessary relationships. No raw source, stable IDs, chapter ownership, figures, option count, `correctOption`, or answer mapping changed.
- `marrow__PHYSIO_CH27_Q012` was reviewed against rendered page 493 and deliberately left unchanged: its sole detector hit is the legitimate source Poiseuille-Hagen formula `F = (PA − PB) × (π/8) × (1/η) × (1/L) × r⁴`. This is a documented detector false-positive, not unresolved learner-visible corruption; do not distort the formula to clear the heuristic.
- Active Chapter 27 v2 source fingerprint after promotion: `a7334a43b238badad932c9a5b1eeb1c2f742e73acbbc7025f1306e6c8ea1905f`.
- Validation: promotion workflow passed exact source-fingerprint promotion, syntax checks, global active-v2 validation, complete effective learner-bank rebuild/debris scan, and full 2,711-question raw/effective answer-index invariants. `questionOptionCandidateQuestions == 0`. All ten cleaned Chapter 27 IDs disappeared from the regenerated explanation queue; only the documented Q12 formula false-positive remains.
- Effective residual explanation candidates after promotion: global 129; Anatomy 1; Biochemistry 6; Physiology 122. Question/option candidates: 0 globally.
- Deferred items in this batch: `marrow__PHYSIO_CH27_Q012` only, detector false-positive/source-faithful notation preserved.
- Exact next ordinary actionable Physiology cleanup target: `marrow__PHYSIO_CH28_Q002` — Chapter 28 Cardiac Cycle and Cardiac Output, question page 498, answer-key page 505, explanation page 506. Chapter 28 currently has 19 explanation candidates and 0 question/option candidates.
- Nothing was merged to canonical or `main`.
