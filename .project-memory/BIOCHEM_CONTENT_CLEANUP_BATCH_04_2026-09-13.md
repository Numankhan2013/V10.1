# Biochemistry learner-content cleanup — Batch 04 — 2026-09-13

- Status: `CLEANED`.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup head before this proposal: `bb4be17209bd46e11b559d4d8afded4da460706e`.
- Canonical head checked before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`. Branches are diverged; this batch changed only Biochemistry Chapter 17 cleanup proposal/override content and did not merge to canonical.
- Reviewed proposal commit: `bed7623bf3cb7d5676ef6ea09cf8dbbc353aaff0`.
- Verified promotion commit: `dae5f6b5ea85728da58a3081f129a4635b12365c` (`Promote reviewed Marrow content cleanup`).
- Source/provenance reviewed from the current effective Chapter 17 review packet and Marrow ED8 Biochemistry provenance: question pages 265-269, explanation pages 277-282, source `biochemistryed8.pdf`. Cleanup was restricted to restoring readable source prose and removing OCR/diagram/serialization debris; malformed flattened bilirubin-metabolism/table text was omitted where the readable prose already carried the explanation.
- CLEANED IDs: `marrow__BIOCHEM_CH17_Q013`, `marrow__BIOCHEM_CH17_Q014`, `marrow__BIOCHEM_CH17_Q016`, `marrow__BIOCHEM_CH17_Q017`, `marrow__BIOCHEM_CH17_Q018`, `marrow__BIOCHEM_CH17_Q019`, `marrow__BIOCHEM_CH17_Q020`, `marrow__BIOCHEM_CH17_Q022`, `marrow__BIOCHEM_CH17_Q023`, `marrow__BIOCHEM_CH17_Q024`.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/biochemistry/chapter_017.json`; current source fingerprint after promotion: `1b46b9fe50b705b9b107b7b3430df348e0866614e5e5b0e48f62e7f803199513`.
- Promotion workflow completed its required v2 validation, full 2,711-question effective-bank rebuild, learner-visible debris rescan, and raw/effective answer-index invariant before producing the promotion commit.
- Verified effective residual after promotion: 472 explanation candidates globally; Anatomy 39, Biochemistry 84, Physiology 349. `questionOptionCandidateQuestions` remains exactly 0.
- Chapter 17 is absent from the rebuilt Biochemistry review-packet directory after promotion, so all detector-flagged Chapter 17 explanation candidates are cleared.
- No stem, option, `correctOption`, answer mapping, stable ID, chapter ownership, or immutable raw source bundle was changed in this batch.
- Exact next unresolved Biochemistry source-order item: `marrow__BIOCHEM_CH18_Q001`, Chapter 18 `Enzymes - Mechanism of Action & Clinical Importance`, question page 283 / explanation page 289. Chapter 18 currently has 13 explanation candidates and zero question/option candidates.
