# Anatomy explanation handoff — 2026-09-13

## FULLY_VERIFIED_HISTORY

- Anatomy Ch6 Q1–Q7 (`marrow__ANAT_CH06_Q001..Q007`) is reconciled into canonical and exact-head verified at canonical checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1`.
- Deterministic inventory at that checkpoint: 588 enhanced / 2,123 pending / 2,711 total; fingerprint `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- Q2 remains `needs_manual_review`; the absent numbered 1–4 legend was not invented.

## CURRENT_UNVERIFIED

- Subject: Anatomy.
- Batch ID: `anatomy-20260913-ch6-q8-q18`.
- State: `PR_OPEN_CI_PENDING` after bounded deterministic-inventory repair.
- Exact canonical base SHA: `58bb99d5c1fc96a98b4f922a963dba16105487d1`; live canonical was rechecked unchanged immediately before the repair checkpoint.
- Branch: `automation/marrow-explanations-anatomy-20260913-ch06-q008-q018`.
- PR: #56.
- Stable-ID scope: `marrow__ANAT_CH06_Q008..Q018`, 11 contiguous questions, workload score 16.5.
- Source chapter: Anatomy Ch6 — Cardiovascular and Respiratory Systems. Canonical Anatomy source SHA remains `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`; raw imported source was not changed.
- Q12, Q16, Q17 and Q18 remain figure-dependent. Q18 also has a structured table and a dedicated stable-ID browser/table regression that checks meaningful cells, rejects `[object Object]`, requires three distractor rows, and protects the shared FSRS dock.
- Content file: `data/marrow/explanation_anatomy_ch06_q008_q018_v1.json`.
- Validator: `tools/test_marrow_anatomy_explanation_rollout.py` validates Ch6 Q1–Q7 and Q8–Q18 against the pinned canonical source, stable IDs, emphasis anchors, source answer keys and exact distractor mapping.
- Browser regression: `tools/verify_marrow_anatomy_ch06_q018_browser.py`, wired through `tools/verify_marrow_bank_browser.py`.
- Initial exact-head Engineering Gate `34721151621` failed only at deterministic explanation-inventory equality; preceding shared Practice/Continue Practice/sync/FSRS/source/image/taxonomy checks passed.
- A bounded diagnostic commit `621b6237833bab8cb1d4b063f8a61c205ada68be` exposed the exact generated manifest. Diagnostic Engineering run `34726572358` confirmed deterministic inventory **599 enhanced / 2,112 pending / 2,711 total**, fingerprint `549af134d84553c1227a9994de67c35bcdae216ad30d7c8be2bcfb844754c902`, with unchanged source hashes/flag counts.
- The exact generated inventory was then written at commit `1dca0ec4c2c04f413886575e0e6b28c4cdb7138d`, and the temporary diagnostic was removed. Content/inventory/validator head before this handoff commit: `43b2e4963fcd15aa0a4caae0a68fb7a827b305bd`.
- Engineering Gate `34726649829` was launched for `43b2e496...`; this handoff update supersedes that SHA, so only CI attached to the final post-handoff PR head may certify the batch.
- No Q19+ content has been started. Anatomy continues to own the explanation lane until this batch is reconciled into canonical and exact-current-head certification completes.
- Production promotion remains prohibited.

## Exact next action

1. Resolve the final PR #56 head after this memory checkpoint and require a fresh Engineering Gate for that exact SHA.
2. If Engineering is green, run/obtain the full Android/PWA/browser/APK/package/reproducibility/preview workflow on the same exact candidate head; Q18 stable-ID table/browser regression must pass in the generated learner path.
3. If the exact candidate is fully green and canonical still equals the recorded base, reconcile PR #56 into `feature/marrow-canonical-full-current` without overwriting newer product/image work.
4. Re-read the resulting exact canonical head and require exact-current-head Engineering plus full Android/PWA certification. Only then move Q8–Q18 from `CURRENT_UNVERIFIED` to `FULLY_VERIFIED_HISTORY` and release the explanation lane.
5. Stop after `FULLY_VERIFIED`; do not start Q19+ in the same run.
6. Production promotion remains prohibited.
