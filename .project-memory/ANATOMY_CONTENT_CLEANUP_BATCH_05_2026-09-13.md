# Anatomy learner-content cleanup — Batch 05 — 2026-09-13

- Status: `CLEANED` / fully verified.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup branch head immediately before the reviewed proposal mutation: `75514e1ff6345f46370bbbb24300fa59b70a1b7c`.
- Canonical head immediately before the proposal and again before this handoff: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; it did not advance during this batch. The cleanup was authored as source-fingerprinted display overrides and no canonical/main merge was performed.
- Chapter 14 Q3 (`marrow__ANAT_CH14_Q003`) was rechecked first because it is earlier in the current detector queue. The rendered ED8 source pages 254-255 confirm that the remaining detector flags come only from legitimate `|` table separators in a source-faithful comparison table. This remains a documented detector false-positive and was not rewritten merely to satisfy the heuristic.
- Real cleanup batch: Chapter 24 `Brainstem`, IDs `marrow__ANAT_CH24_Q001`, `marrow__ANAT_CH24_Q002`, `marrow__ANAT_CH24_Q003`.
- Exact source: verified Marrow ED8 Anatomy `marrow ed 8 qbank_compressed.pdf`.
- Rendered source reviewed: answer key / Q1 explanation page 409 and explanation pages 410-412. Q1/Q3 table content was reconstructed into readable labeled text; diagram-label OCR was omitted instead of flattened into learner prose. Q2 retained only the readable source prose and omitted diagram-label debris.
- Proposal file: `data/marrow/content_hygiene_proposals/anatomy/chapter_024.json`.
- Reviewed proposal commit: `0460f105abcfc1e316979d2da5fe4f8c929b3640`.
- Promotion/validation workflow: `34755647228` — `SUCCESS`.
- Verified source-fingerprinted promotion commit: `b7238f32fee805a664396d10bb908b028ea46f02`.
- Mandatory gates passed in the repository workflow: every active v2 override validated; complete 2,711-question effective learner bank rebuilt; raw/effective `correctOption` indexes identical; learner-visible debris rescan completed; `questionOptionCandidateQuestions` remains exactly `0`.
- No question text, option text, answer index, answer mapping, stable ID, chapter ownership, or source provenance was changed by this batch.
- Effective residual after verified promotion: `464` explanation candidates globally — Anatomy `36`, Biochemistry `84`, Physiology `344`; stem/option candidates `0`.
- Chapter 24 residual is now `5` candidates. The cleaned Q1-Q3 IDs are absent from the rebuilt explanation debris queue.
- Exact next unresolved Anatomy source-order item: `marrow__ANAT_CH24_Q008`, question page 406, answer-key page 409, explanation pages 415-416. Continue Chapter 24 in source order: Q8, Q10, Q11, Q12, Q14, unless a source-backed deferral is required.
