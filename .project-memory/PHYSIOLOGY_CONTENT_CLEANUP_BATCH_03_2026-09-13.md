# Physiology learner-content cleanup — batch 03 — 2026-09-13

- Status: **CLEANED / VERIFIED**.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup head immediately before proposal mutation: `8df66817e8c41b75e71d8d5287b4e2fa10f44068`.
- Canonical head before mutation and after verified promotion remained `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; canonical's current checkpoint is Anatomy-only and does not intersect this Physiology Chapter 3 batch.
- Reviewed proposal commit: `a018747900d8caa431dd92f7c0614b6b45840365`.
- Verified promotion commit: `f346266be5fb2e1c8efb304fef2419cba6ab0e8a`.
- Promotion/validation workflow: `34749785740`, **SUCCESS**.
- Source reviewed: verified Marrow ED8 Physiology rendered explanation pages **48–54** for Chapter 3 `Transport Across Cell Membrane`.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_003.json`.
- CLEANED IDs: `marrow__PHYS_CH03_Q014`, `marrow__PHYS_CH03_Q016`, `marrow__PHYS_CH03_Q017`, `marrow__PHYS_CH03_Q018`, `marrow__PHYS_CH03_Q019`, `marrow__PHYS_CH03_Q020`, `marrow__PHYS_CH03_Q021`, `marrow__PHYS_CH03_Q022`, `marrow__PHYS_CH03_Q024`.
- Q15 and Q23 were not changed because they were not in the current effective debris queue. Q4 remains the previously documented source-reviewed learner-clean **detector false-positive** because its legitimate diffusion equations trigger broad symbol/isolated-letter heuristics; do not delete or rewrite those medically meaningful equations merely to make the heuristic count zero.
- Cleanup was source-faithful only: OCR noise, flattened diagram/table debris, brand/footer remnants and meaningless symbol runs were removed; readable medical prose and source relationships were preserved. No gold-standard enhancement, Key Takeaway authoring, distractor-rationale authoring or stylistic expansion was introduced.
- The promotion workflow validated every active v2 override, rebuilt and rescanned the complete **2,711-question** effective bank, proved raw/effective `correctOption` indexes identical, and kept `questionOptionCandidateQuestions` exactly **0**.
- Post-promotion Chapter 3 review packet contains only Q4, the documented legitimate-equation false-positive. All nine batch-03 IDs are absent from the explanation debris queue.
- Physiology explanation residual decreased from **359 → 350** for this batch. Current global residual after concurrent subject workers is **504**: Anatomy 50, Biochemistry 104, Physiology 350. Question/option residual remains 0 in all three subjects.
- No cleanup candidate in this batch required deferral or REVIEW_REQUIRED status.
- Exact next real Physiology source-order cleanup target after skipping only documented Ch3 Q4 false-positive: `marrow__PHYS_CH04_Q001`, Chapter 4 `Membrane Potentials`, source question page 55 and explanation pages **59–60**. Chapter 4 currently has 9 explanation candidates and 0 question/option candidates.
- Production, `main`, and `feature/marrow-canonical-full-current` were not mutated by this cleanup batch.
