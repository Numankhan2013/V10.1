# Marrow Physiology learner-visible cleanup — Batch 34 handoff

- Subject: Physiology.
- Cleanup lane before memory write: `fix/marrow-full-content-cleanup-20260913` at verified promotion commit `211132a889bae66de81277b266bddf0767be45cf`.
- Canonical comparison at the same checkpoint: `feature/marrow-canonical-full-current` at `94edb3af43eb38a1ef762b08c1bdb152c15b3359`. Canonical did not advance during this batch and was not mutated or merged.
- Reviewed proposal commit: `95ce2cfb70cf69a55f6098cd7c19a49fd03126ff`.
- Promotion workflow: `34869201743` (`Promote Marrow content cleanup proposals`), conclusion `success`.
- Verified promotion commit: `211132a889bae66de81277b266bddf0767be45cf`.
- Scope: Chapter 26 — Vascular System and Regional Circulation I; explanation-only cleanup for stable IDs `marrow__PHYSIO_CH26_Q003`, `Q004`, `Q005`, `Q006`, `Q007`, `Q016`, and `Q018`.
- Authoritative rendered ED8 explanation pages reviewed: 474–476, 480–482. Question pages span 468–472; answer-key page 473.
- Cleanup only: removed OCR/diagram-label spillover, source branding/footer/page markers, malformed equation/table text, and meaningless symbol debris while preserving source medical prose and verifiable table/equation relationships. Q16 and Q18 diagram OCR was omitted because the readable source prose fully stated the required relationship. No raw source, stable IDs, chapter ownership, figures, option count, `correctOption`, or answer mapping changed.
- Active Chapter 26 v2 source fingerprint after promotion: `9e14d297a9d3f7abd22a51d85de3c6de7c85ed0cd587d645a6895d10a00d7edd`.
- Validation: promotion workflow passed exact source-fingerprint promotion, global active-v2 validation, complete effective learner-bank rebuild/debris scan, and full 2,711-question raw/effective answer-index invariants. `questionOptionCandidateQuestions == 0`. All seven Chapter 26 candidates disappeared from the regenerated explanation queue. No runtime-output path was changed, so no additional product/browser build regression was required for this content-only batch.
- Effective residual explanation candidates after promotion: global 139; Anatomy 1; Biochemistry 6; Physiology 132. Question/option candidates: 0 globally.
- Deferred items in this batch: none.
- Exact next ordinary actionable Physiology cleanup target: `marrow__PHYSIO_CH27_Q002` — Chapter 27 Vascular System and Regional Circulation II, question page 483, answer-key pages 488–489, explanation pages 489–490. Chapter 27 currently has 11 explanation candidates and 0 question/option candidates.
- Earlier detector-only false positives in already reviewed chapters remain historical/documented and are not permission to distort valid source notation.
- Nothing was merged to canonical or `main`.
