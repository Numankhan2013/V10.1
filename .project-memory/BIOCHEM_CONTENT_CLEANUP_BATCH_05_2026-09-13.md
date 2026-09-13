# Biochemistry learner-content cleanup — Batch 05 — 2026-09-13

- Status: `CLEANED`.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup head immediately before the reviewed proposal: `7a83ba29441c33afa709b03646338b0e668c0809`.
- Canonical head checked immediately before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; canonical remained Anatomy-only at that checkpoint and did not intersect this Biochemistry Chapter 18 batch.
- Reviewed proposal commit: `11d1962efa7e795ebdfff6419807b2f3a701bda5`.
- Verified promotion commit: `8ce27142e72b8461b1a213858ce223ae61b9c26b` (`Promote reviewed Marrow content cleanup`).
- Promotion/validation workflow: `34756630261` — SUCCESS.
- Source reviewed: verified Marrow ED8 Biochemistry `biochemistryed8.pdf`; rendered explanation pages 289–296 for Chapter 18 `Enzymes - Mechanism of Action & Clinical Importance`.
- CLEANED IDs: `marrow__BIOCHEM_CH18_Q001`, `marrow__BIOCHEM_CH18_Q003`, `marrow__BIOCHEM_CH18_Q005`, `marrow__BIOCHEM_CH18_Q006`, `marrow__BIOCHEM_CH18_Q007`, `marrow__BIOCHEM_CH18_Q008`, `marrow__BIOCHEM_CH18_Q010`, `marrow__BIOCHEM_CH18_Q012`, `marrow__BIOCHEM_CH18_Q013`, `marrow__BIOCHEM_CH18_Q014`, `marrow__BIOCHEM_CH18_Q015`, `marrow__BIOCHEM_CH18_Q016`.
- Cleanup was explanation-only. It removed OCR/symbol debris, flattened diagram/table spillover and malformed source-transcription fragments. Where Chapter 18 source tables carried medically meaningful LDH isoenzyme relationships, those relationships were reconstructed as plain source-faithful prose rather than retaining corrupted flattened table OCR. No gold-standard tuning, new takeaway, teaching expansion or answer correction was added.
- No question, option, `correctOption`, correct-answer mapping, stable ID, subject/chapter ownership, figure provenance, or immutable raw bundle was changed.
- The promotion workflow passed every active v2 override validator, rebuilt and rescanned the complete 2,711-question effective bank, proved the raw/effective correct-option dictionaries identical, and kept `questionOptionCandidateQuestions` exactly 0.
- Verified effective residual after promotion: 452 explanation candidates globally; Anatomy 36, Biochemistry 72, Physiology 344. Biochemistry fell from 84 to 72 in this batch.
- Chapter 18 now has exactly one remaining explanation candidate and zero question/option candidates.
- Exact next unresolved Biochemistry source-order item: `marrow__BIOCHEM_CH18_Q017`, question pages 287–288 / explanation page 296. Continue from Q17 next run; do not skip it.
