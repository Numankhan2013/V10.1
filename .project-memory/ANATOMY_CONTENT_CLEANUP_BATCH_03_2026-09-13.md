# Anatomy learner-content cleanup — batch 03 — 2026-09-13

- Status: **CLEANED / VERIFIED**.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup head before proposal mutation: `60f2d19f4f36b6f713972d984ec04330f44e8e19`.
- Canonical head checked before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; it remained unchanged during this batch and did not intersect Anatomy Chapter 13 cleanup work.
- Reviewed proposal commit: `20183917e29c0d0eb63b283382aa296e6409d02e`.
- Verified promotion commit: `baf30f7584f130597ee5587efef87a2cf65e86d0`.
- Promotion/validation workflow: `34750597830`, **SUCCESS**.
- Source reviewed: exact verified Marrow ED8 Anatomy `marrow ed 8 qbank_compressed.pdf`; rendered explanation pages 236–243 for Chapter 13 `Nervous and Endocrine Systems`. Candidate-specific source pages: Q1 p236; Q3 p238; Q5 pp238–239; Q6 p239; Q7 pp239–240; Q8 pp240–241; Q10 pp242–243. Q2, Q4 and Q9 were not edited because they were not in the current effective debris queue.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/anatomy/chapter_013.json`.
- CLEANED IDs: `marrow__ANAT_CH13_Q001`, `marrow__ANAT_CH13_Q003`, `marrow__ANAT_CH13_Q005`, `marrow__ANAT_CH13_Q006`, `marrow__ANAT_CH13_Q007`, `marrow__ANAT_CH13_Q008`, `marrow__ANAT_CH13_Q010`.
- Cleanup was source-faithful only: OCR corruption, flattened diagram-label spillover, footer/branding debris and meaningless symbol runs were removed while retaining readable medical content. No gold-standard enhancement, Key Takeaway authoring, new rationale sections or stylistic teaching expansion was introduced.
- The successful promotion workflow validated every active v2 override, rebuilt and rescanned the complete **2,711-question** effective bank, preserved raw/effective `correctOption` indexes and answer mappings, and kept learner-visible question/option candidates at **0**.
- All seven Chapter 13 batch IDs are absent from the post-promotion explanation debris queue.
- Anatomy explanation residual decreased **51 → 44** in this batch; global candidate-question residual decreased **504 → 497** (Biochemistry 104, Physiology 350 unchanged in this batch).
- No candidate in this batch required deferral.
- Exact next Anatomy source-order cleanup target: `marrow__ANAT_CH14_Q001`, Chapter 14 `Cardiovascular, Lymphatic and Respiratory Systems`, source question page 246 and explanation pages **251–253**. Chapter 14 currently has 5 explanation candidates and 0 question/option candidates.
- Production, `main`, and `feature/marrow-canonical-full-current` were not mutated by this cleanup batch.
