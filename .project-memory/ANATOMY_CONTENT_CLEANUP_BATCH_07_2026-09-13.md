# Anatomy learner-content cleanup — Batch 07 — 2026-09-13

- Status: `CLEANED` / fully verified.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup branch head before reviewed proposal mutation: `89986dd3157612e9ce9112eca841c18d088268f1`.
- Canonical head checked before mutation and again after promotion: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; it did not advance during this batch. The canonical branch is diverged from the cleanup lane, but its recent Anatomy explanation scope is Chapter 6 and does not intersect this Chapter 24 cleanup.
- Exact source: verified Marrow ED8 Anatomy `marrow ed 8 qbank_compressed.pdf`.
- Rendered source reviewed directly: Chapter 24 `Brainstem`, question/answer-key provenance pages 408–409 and explanation pages 418–420.
- CLEANED IDs: `marrow__ANAT_CH24_Q012`, `marrow__ANAT_CH24_Q014`.
- Q12: reconstructed the source medullary cross-section table into readable level-by-level text while preserving the source-listed cavities, nuclei, motor tracts and sensory tracts; omitted only the unrelated flattened image/diagram OCR and source branding.
- Q14: restored the source Wallenberg/lateral medullary syndrome prose and the six source sign/affected-structure rows; omitted diagram-label and OCR spillover only.
- No question text, option text, correctOption, answer mapping, stable ID, chapter ownership, figure provenance, or immutable raw source was changed.
- Reviewed proposal commit: `9eadae1a324b5a77e13050ac3c8c6ac78d370573`.
- Verified source-fingerprinted promotion commit: `e90fa4ff21aa364939b7dc8e8f7b7f447e1f9920` (`Promote reviewed Marrow content cleanup`).
- The promotion workflow completed the fail-closed v2 validation, rebuilt and rescanned the complete 2,711-question effective learner-visible bank, preserved all raw/effective correctOption indexes, and kept `questionOptionCandidateQuestions` exactly `0` before creating the promotion commit.
- Effective residual after verified promotion: `425` explanation candidates globally — Anatomy `31`, Biochemistry `71`, Physiology `323`; stem/option candidates `0`.
- Chapter 24 is absent from the rebuilt explanation review index after this promotion; Q12 and Q14 are no longer detector candidates.
- Anatomy Chapter 14 still has one documented legitimate-table detector false-positive from the prior run and must not be rewritten merely to satisfy the heuristic.
- Exact next real unresolved Anatomy source-order item after that documented false-positive: `marrow__ANAT_CH25_Q003` in Chapter 25 `Cerebellum`, question page 423, answer-key page 428, explanation pages 429–430. Chapter 25 currently has five explanation candidates: Q3, Q4, Q7, Q8 and Q11.
