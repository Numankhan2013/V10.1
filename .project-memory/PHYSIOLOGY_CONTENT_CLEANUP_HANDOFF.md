# Physiology learner-visible content cleanup handoff

## 2026-09-13 — Batch 04 (Chapter 4 Q1–Q3)

- Cleanup lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical head checked before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no intersecting Chapter 4 cleanup ownership was identified.
- Source of truth reviewed: rendered Marrow ED8 Physiology pages 59–62 in `physiologyed8.pdf`.
- Cleaned stable IDs: `marrow__PHYS_CH04_Q001`, `marrow__PHYS_CH04_Q002`, `marrow__PHYS_CH04_Q003`.
- Scope was explanation cleanup only. Raw corpus, stems, options, `correctOption`, answer mapping, figures, provenance and chapter ownership were not mutated.
- Reviewed proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_004_cleanup_batch_20260913_01.json`, initial proposal commit `4d1e9d9cfce123d528627c334284c4ecaf46aeb4`.
- Promoted source-fingerprinted v2 override: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_004.json`, promotion commit `4673000a5d9cc25178ac4405650720b9415cb097`.
- Override source fingerprint: `e4793b6c4ac51bc500f02212462ca27d346449de1a4bd4cbcd11feb25ace5a15`.
- Validation: `Test Marrow content overrides v2` run `34752012345` PASS; `Report Marrow v2 validator issues` run `34752012444` PASS; `Effective Marrow content audit` run `34752012366` PASS.
- Effective audit invariants: 2,711 questions rebuilt; answer-index identity PASS; `questionOptionCandidateQuestions=0`; immutable source untouched.
- Residual effective explanation queue after the batch and concurrent subject cleanup: global `486` explanation-candidate questions; Anatomy `43`, Biochemistry `94`, Physiology `349` in the compact explanation packets. Broad field scan shows one additional Anatomy structured-explanation-only flag.
- Chapter 4 now has 8 explanation candidates and 0 question/option candidates.
- Detector-review note: Q1 remains detector-flagged only because legitimate `(+/-)` notation triggers `punctuation_run`; Q3 remains detector-flagged only because the source-faithful Gibbs-Donnan equations trigger `many_isolated_letters` / `symbol_dense_line`. These are reviewed false positives and must not be "cleaned" by deleting medically meaningful notation. Q2 is absent from the residual packet and is clean by detector.
- Current derived-audit head after workflow rebase/push: `4b0c8312e25d4a4e52856b92ce2f965c04c1fb74`.
- Exact next unresolved real cleanup target: `marrow__PHYS_CH04_Q004` (solution on rendered ED8 pages 62–63). Continue in source order, treating Q1/Q3 as documented detector false positives rather than unresolved corruption.
