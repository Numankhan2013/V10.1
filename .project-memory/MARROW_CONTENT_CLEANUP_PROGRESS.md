# Marrow learner-content cleanup progress

## 2026-09-13 — Physiology cleanup batch 01

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical comparison immediately before/after the batch: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; the concurrent canonical advance is Anatomy-only (`Checkpoint Anatomy Q8-Q18 canonical certification`) and does not intersect this Physiology batch.
- Reviewed proposal commit: `cb09558bd8deb55369d33516f79e5174fce6f82a`.
- Verified promotion commit: `3c47ef5d898af81c0ef7fc871f5b2a193487c913`.
- Promotion/validation workflow: `34745656328`, SUCCESS.
- Source reviewed: verified Marrow ED8 Physiology rendered pages 41-43 for Chapter 3 `Transport Across Cell Membrane`.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_003.json`.
- Reviewed IDs: `marrow__PHYS_CH03_Q001`, `marrow__PHYS_CH03_Q002`, `marrow__PHYS_CH03_Q004`, `marrow__PHYS_CH03_Q005`.
- Q1, Q2 and Q5 are detector-clean after source-faithful explanation reconstruction; no learner-visible stem/option regressions were introduced.
- Q4 is also source-reviewed and learner-clean, but remains in the broad explanation review queue as a documented detector false-positive: the detector flags legitimate diffusion equations / isolated formula symbols (`many_isolated_letters`, `symbol_dense_line`) and short equation/result lines (`edge_noise`). Do not rewrite or delete these medically meaningful equations merely to satisfy the heuristic detector.
- Effective residual after promotion: 545 explanation candidates globally; Anatomy 59, Biochemistry 120, Physiology 366. `questionOptionCandidateQuestions` remains exactly 0.
- Correct-option indexes remain immutable; the promotion workflow rebuilt the complete 2,711-question effective bank and passed the global answer-index and v2 validation gates.
- Exact next unresolved Physiology source-order item requiring cleanup: `marrow__PHYS_CH03_Q006`, explanation pages 43-44. Continue in Chapter 3 source order; Q4 may be skipped only as the documented detector false-positive above.

## 2026-09-13 — Anatomy cleanup batch 01

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical head checked before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`. Its active/recent Anatomy explanation scope is Chapter 6 Q8-Q18; this cleanup batch is Chapter 12 and does not overlap that canonical content scope.
- Reviewed proposal commit: `d38c1dc1c460a7aea9324292143e91ca29c7b354`.
- Verified promotion commit: `c81435ded14842b1cffc672eaa13a50d9779142e`.
- Promotion/validation workflow: `34746307638`, SUCCESS.
- Source reviewed: exact verified Marrow ED8 Anatomy `marrow ed 8 qbank_compressed.pdf`; rendered explanation pages 219, 220, 222, 223 and 225 for Chapter 12 `Bone, Cartilage & Muscular Tissue`.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/anatomy/chapter_012.json`.
- CLEANED IDs: `marrow__ANAT_CH12_Q001`, `marrow__ANAT_CH12_Q002`, `marrow__ANAT_CH12_Q004`, `marrow__ANAT_CH12_Q005`, `marrow__ANAT_CH12_Q007`.
- Cleanup removed only OCR/diagram/footer debris and retained source-faithful medical prose. No question or option text was changed in this batch; no answer index or mapping changed. No items were deferred in this batch.
- The promotion workflow validated all active v2 overrides, rebuilt the complete 2,711-question effective bank, re-ran learner-visible debris detection, proved raw/effective correct-option indexes identical, and kept `questionOptionCandidateQuestions` exactly 0.
- Effective residual after promotion: 540 explanation candidates globally; Anatomy 54, Biochemistry 120, Physiology 366. Chapter 12 now has four residual explanation candidates.
- Exact next unresolved Anatomy source-order item requiring cleanup: `marrow__ANAT_CH12_Q008`, explanation page 225. Continue in Chapter 12 source order.

## 2026-09-13 — Biochemistry cleanup batch 01

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical head checked immediately before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; the concurrent canonical work is Anatomy-only and does not overlap this Biochemistry Chapter 1 batch.
- Reviewed proposal commit: `83536341688c9d39f1cafab8a10cd32802d8d2d7`.
- Verified promotion commit: `12f7a204ce60514ec3540d0dd92d28dba24e4d71`.
- Promotion/validation workflow: `34747048098`, SUCCESS.
- Source reviewed: verified Marrow ED8 Biochemistry `biochemistryed8.pdf`; rendered explanation pages 11-18 for Chapter 1 `Chemistry of Carbohydrates, Amino sugars and Mucopolysaccharides`.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/biochemistry/chapter_001.json`.
- CLEANED IDs: `marrow__BIOCHEM_CH01_Q001`, `marrow__BIOCHEM_CH01_Q004`, `marrow__BIOCHEM_CH01_Q006`, `marrow__BIOCHEM_CH01_Q007`, `marrow__BIOCHEM_CH01_Q009`, `marrow__BIOCHEM_CH01_Q018`, `marrow__BIOCHEM_CH01_Q020`, `marrow__BIOCHEM_CH01_Q021`.
- Cleanup reconstructed only readable source prose/tables from the rendered pages and removed OCR/diagram/footer debris. No question or option text was changed in this batch; no answer index or mapping changed. No items were deferred in this batch.
- The promotion workflow validated every active v2 override, rebuilt the complete 2,711-question effective bank, re-ran learner-visible debris detection, proved raw/effective correct-option indexes identical, and kept `questionOptionCandidateQuestions` exactly 0.
- Effective residual after promotion: 532 explanation candidates globally; Anatomy 54, Biochemistry 112, Physiology 366. Biochemistry Chapter 1 has no remaining detector-flagged explanation candidates.
- Exact next unresolved Biochemistry source-order item requiring cleanup: `marrow__BIOCHEM_CH03_Q003`, explanation page 52. Continue in Chapter 3 source order.

## 2026-09-13 — Physiology cleanup batch 02

- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup branch head immediately before proposal mutation: `544f02fcf3183a99c8c958c882875b9dad16575c`; canonical head immediately before and after promotion remained `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`. The canonical advance remains Anatomy-only and does not intersect Physiology Chapter 3.
- Reviewed proposal commit: `30ee16e69b3ed4cd45311c4ca7b4456754630259`.
- Verified promotion commit: `41b2c79b26659463779a6927207e16f34dd023a3`.
- Promotion/validation workflow: `34747955253`, SUCCESS.
- Source reviewed: verified Marrow ED8 Physiology rendered pages 43-47 for Chapter 3 `Transport Across Cell Membrane`.
- Active source-fingerprinted v2 cleanup file: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_003.json`.
- CLEANED IDs: `marrow__PHYS_CH03_Q006`, `marrow__PHYS_CH03_Q007`, `marrow__PHYS_CH03_Q009`, `marrow__PHYS_CH03_Q010`, `marrow__PHYS_CH03_Q011`, `marrow__PHYS_CH03_Q012`, `marrow__PHYS_CH03_Q013`.
- Cleanup reconstructed only readable source prose and source-listed examples from the rendered pages, removing OCR noise, footer/brand text and flattened diagram/table debris. Q8 was not touched because it was not in the current debris queue. No question or option text was changed; no answer index or answer mapping changed.
- The promotion workflow validated every active v2 override, rebuilt and rescanned the complete 2,711-question effective bank, proved raw/effective correct-option indexes identical, and kept `questionOptionCandidateQuestions` exactly 0.
- Effective residual after promotion: 525 explanation candidates globally; Anatomy 54, Biochemistry 112, Physiology 359. Chapter 3 now has 10 detector-flagged explanation candidates; Q4 remains the previously documented legitimate-equation false-positive.
- Exact next unresolved Physiology source-order item requiring cleanup after skipping documented Q4 false-positive: `marrow__PHYS_CH03_Q014`, explanation page 48. Continue in Chapter 3 source order.
