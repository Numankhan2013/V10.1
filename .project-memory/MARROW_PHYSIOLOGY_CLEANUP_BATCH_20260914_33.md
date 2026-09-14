# Marrow Physiology learner-visible cleanup — Batch 33 handoff

- Subject: Physiology.
- Cleanup lane before memory write: `fix/marrow-full-content-cleanup-20260913` at verified promotion commit `51700076c2785280f25da56d3986c1804645351e`.
- Canonical comparison at the same checkpoint: `feature/marrow-canonical-full-current` at `94edb3af43eb38a1ef762b08c1bdb152c15b3359`. Canonical did not advance during this batch and was not mutated or merged.
- Reviewed proposal commit: `f1ad16e85e28ab44c065be8d9a8a391216691296`.
- Promotion workflow: `34862692808` (`Promote Marrow content cleanup proposals`), conclusion `success`.
- Verified promotion commit: `51700076c2785280f25da56d3986c1804645351e`.
- Scope: Chapter 25 — Regulation of Respiration; explanation-only cleanup for stable IDs `marrow__PHYSIO_CH25_Q019`, `marrow__PHYSIO_CH25_Q021`, `marrow__PHYSIO_CH25_Q024`, `marrow__PHYSIO_CH25_Q025`, and `marrow__PHYSIO_CH25_Q027`.
- Authoritative rendered ED8 explanation pages reviewed: 463–466. Question pages: Q19 p450; Q21 p451; Q24 pp451–452; Q25 p452; Q27 p452. Answer-key pages for all five: pp453–454.
- Cleanup only: removed OCR/diagram/serialization debris and source branding/footer material while preserving readable source medical content. No raw source, stable IDs, chapter ownership, figures, option count, `correctOption`, or answer mapping changed.
- Active Chapter 25 v2 source fingerprint after promotion: `19f7ecfe4245804599a9ea3f48df4863300ce3d7ee26dec6bfd46df826f70250`.
- Validation: global v2 validator passed (`files=39`, `questions=493`, `changed_fields=977`, `explanations=469`); full effective audit rebuilt at 2,711 questions; raw/effective `correctOption` maps were identical; `questionOptionCandidateQuestions == 0`; Chapter 25 disappeared from the regenerated explanation review queue; no runtime-output path was changed, so no product/browser build regression was required for this content-only batch.
- Effective residual explanation candidates after promotion: global 146; Anatomy 1; Biochemistry 6; Physiology 139. Question/option candidates: 0 globally.
- Deferred items in this batch: none.
- Exact next ordinary actionable Physiology cleanup target: `marrow__PHYSIO_CH26_Q003` — Chapter 26 Vascular System and Regional Circulation I, question page 468, answer-key page 473, explanation page 474. Chapter 26 currently has 7 explanation candidates and 0 question/option candidates.
- Earlier detector-only false positives in already reviewed chapters remain historical/documented and are not permission to distort valid source notation.
- Nothing was merged to canonical or `main`.
