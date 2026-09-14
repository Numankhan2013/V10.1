# Marrow Physiology learner-visible cleanup — Batch 36 handoff

- Subject: Physiology.
- Cleanup lane before memory write: `fix/marrow-full-content-cleanup-20260913` at verified promotion commit `b0d805b1ffef7524f4dfaa882d30f72b388610ca`.
- Canonical comparison at the same checkpoint: `feature/marrow-canonical-full-current` at `94edb3af43eb38a1ef762b08c1bdb152c15b3359`. Canonical did not advance during this batch and was not mutated or merged.
- Scope: Chapter 28 — Cardiac Cycle and Cardiac Output; explanation-only cleanup for stable IDs `marrow__PHYSIO_CH28_Q002`, `Q003`, `Q005`, `Q006`, `Q007`, `Q008`, `Q012`, `Q013`, `Q016`, `Q018`, `Q019`, and `Q020`.
- Authoritative rendered ED8 explanation pages reviewed: 506–513. Question pages span 498–503; answer-key page 505.
- Cleanup only: removed OCR/serialization debris, page markers, graph/diagram-label spillover, source branding/footer material, malformed symbol runs, and cross-question contamination while retaining source-faithful readable medical prose and verifiable relationships. Flattened diagrams/tables were omitted where their readable prose already conveyed the necessary source relationship. No teaching expansion, beautification, or restructuring was added.
- Existing reviewed Chapter 28 question/options fields were preserved exactly. Because `Q005`, `Q006`, and `Q016` were already owned by the legacy reviewed proposal `data/marrow/content_hygiene_proposals/physiology/chapter_028.json`, their new explanation fields were added there; the other nine IDs were recorded in `data/marrow/content_hygiene_proposals/physiology/chapter_028_cleanup_batch_20260915_36.json`.
- Initial proposal commit `fe3df7e9ddd87cd2501c84af28fbcc2f84c6f3ae` failed closed at promotion workflow `34881856920` because the promoter correctly rejected duplicate proposal stable IDs. No validator was weakened. The batch proposal was split at repair commit `91c6ee141e2da8a3022b2228e01b603ba34979c8`, and the already-owned Q005/Q006/Q016 entries were updated at commit `44fa03d9494a47580397de534e940e598b346bfe`.
- Final promotion workflow: `34882031128` (`Promote Marrow content cleanup proposals`), promote job `104103389310`, conclusion `success`; every workflow step passed.
- Verified final promotion commit: `b0d805b1ffef7524f4dfaa882d30f72b388610ca`.
- Active Chapter 28 v2 source fingerprint after promotion: `daf5b64fc649e88b75d88d2a5f6908e73ac61af4f01e409ba2f6dece33f2b0be`.
- Validation: exact source-fingerprint promotion passed; syntax checks passed; global active-v2 validation passed; complete effective learner-bank rebuild and debris scan passed; full 2,711-question raw/effective answer-index invariants passed; four-option and answer mapping invariants remained intact; `questionOptionCandidateQuestions == 0`.
- All twelve cleaned Batch 36 IDs disappeared from the regenerated Chapter 28 explanation queue.
- Effective residual explanation candidates after final promotion: global 117; Anatomy 1; Biochemistry 6; Physiology 110. Question/option candidates: 0 globally.
- Deferred items in this batch: none.
- Exact next unresolved Physiology cleanup target: `marrow__PHYSIO_CH28_Q021` — Chapter 28 Cardiac Cycle and Cardiac Output, question page 503, answer-key page 505, explanation page 514. Chapter 28 now has 7 explanation candidates and 0 question/option candidates.
- Nothing was merged to canonical or `main`.
