# Biochemistry learner-content cleanup — Batch 08 — 2026-09-13

Status: **CLEANED / VERIFIED**

- Cleanup lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical head checked before mutation: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0` on `feature/marrow-canonical-full-current`.
- Cleanup head immediately before proposal mutation: `1413683b11e69d0ae8df1cdffd90fb86203e97c1`.
- Subject/chapter: Biochemistry Ch19, *Enzyme Kinetics and Regulation of Activity*.
- Stable IDs cleaned: `marrow__BIOCHEM_CH19_Q018`, `marrow__BIOCHEM_CH19_Q019`, `marrow__BIOCHEM_CH19_Q020`.
- Authoritative Marrow ED8 source pages reviewed: explanation pp314–317 from `biochemistryed8.pdf`; rendered source was used because embedded/extracted text was corrupted.
- Cleanup was source-faithful only: removed OCR/symbol/diagram-label spillover and preserved readable medical prose. No Key Takeaway/rationale expansion or stylistic fine-tuning was introduced. Raw source was not mutated.
- Q18: retained the source description of noncompetitive inhibition and omitted diagram OCR debris.
- Q19: reconstructed only the readable source prose around Gibbs free-energy/transition-state diagrams; diagram label OCR was omitted while source relationships and Graph A/B/C/D explanations were retained.
- Q20: restored readable catalytic-efficiency prose and normalized scientific notation without altering the source relationships.
- Reviewed proposal: `data/marrow/content_hygiene_proposals/biochemistry/chapter_019_reviewed_20260913_batch08.json`.
- Proposal commit: `5333af06376c9f9269f714b25e951c5b2dea8008`.
- Promotion workflow: `34767959982` — SUCCESS.
- Verified promoted cleanup commit: `aed302f7a71b49fc753b427d5f07af5d1830d56e`.
- Promotion validation passed the global v2 override validator, full 2,711-question effective-bank rebuild/debris scan, raw/effective answer-index equality, and `questionOptionCandidateQuestions == 0`.
- Post-promotion effective residuals: Anatomy 19, Biochemistry 56, Physiology 314; global explanation candidates 389; learner-visible question/option candidates 0.
- Chapter 19 no longer appears in the Biochemistry explanation queue.
- Exact next deterministic Biochemistry target: Ch25 Q1 (`marrow__BIOCHEM_CH25_Q001`), question page 381, answer-key pp388–389, explanation pp389–390. Ch25 currently contains 27 explanation candidates.

No merge to canonical or `main` was performed.
