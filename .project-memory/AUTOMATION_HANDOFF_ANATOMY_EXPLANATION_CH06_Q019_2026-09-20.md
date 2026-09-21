# Anatomy explanation automation handoff — Ch6 Q19–Q25

- State: FULLY_VERIFIED_HISTORY for the content batch; PR_OPEN_CI_PENDING for the follow-up validator repair.
- Subject: Anatomy.
- Canonical integration trunk: `feature/marrow-canonical-full-current`.
- Live canonical base at validator-repair acquisition: `8aa1c22b8e622a28ef0781f73991160e14f6907d`.
- Completed content range: `marrow__ANAT_CH06_Q019` through `marrow__ANAT_CH06_Q025` (7 contiguous questions; Chapter 6 tail).
- Raw source remains immutable.
- Content batch history: candidate `b678e8c40c63c7ea1f845cf3c113d94b7d689c94`; exact-head Engineering run `35556462094` green; SHA-identical full Android/PWA/browser/APK/package/reproducibility/preview run `35592728095` green with production promotion skipped; PR #61 reconciled through canonical merge `e382f7468e8b6e5358af86cfb7106dc35e904751`.
- Deterministic post-merge inventory refresh advanced canonical to `8aa1c22b8e622a28ef0781f73991160e14f6907d`: 622 enhanced-reference / 2,089 pending / 2,711 total; question-record fingerprint `3f93a5cc4571d5f33f816e1482e824d3065cd24d4a8d6355704ce698a96d80a0`; raw source hashes unchanged.
- Reconstruction: Q24 remains explicitly `needs_manual_review`. The source preserves the medical chronology and keyed answer `2-4-3-1` but omits the numbered mapping assigning phases to 1–4; no mapping was invented.
- Follow-up architecture defect found after reconciliation: `tools/test_marrow_anatomy_explanation_rollout.py` still validated only Ch6 Q1–Q18 even though deterministic inventory and runtime augmentation already included Q19–Q25. This stale validator coverage is a fixable derived-validation defect, not a content rollback.
- Validator repair branch: `feature/marrow-explanations-anatomy-validator-repair-20260921`, created from exact canonical `8aa1c22b8e622a28ef0781f73991160e14f6907d`.
- Validator repair authored commit: `a4a35e8a53be8d583a99905610032d0b29825708`; it adds Q19–Q25 source/key/rationale/emphasis coverage and explicit Q24 reconstruction-schema validation without changing raw source or learner content.
- Repair PR: #63 against `feature/marrow-canonical-full-current`.
- CURRENT_UNVERIFIED ownership: validator repair only; no new Anatomy content batch has been started in this run.
- Exact next action: inspect exact-head CI for the current PR #63 head. If the Q24 source review-status assertion is too strict for canonical source metadata, repair the validator to require augmentation reconstruction metadata without fabricating raw-source status; otherwise proceed through Engineering and full exact-SHA CI. Reconcile the verified validator repair into canonical before acquiring the next Anatomy content batch.
- Next Anatomy content after lane release: exact next incomplete source-order question following Chapter 6 Q25, resolved from the live 1,115-question canonical bundle; do not hardcode from historical Phase-A state.
- Production promotion prohibited.
