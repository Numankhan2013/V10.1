# Anatomy explanation handoff — 2026-09-13

## FULLY_VERIFIED_HISTORY

- Anatomy Ch6 Q1–Q7 (`marrow__ANAT_CH06_Q001..Q007`) is reconciled into canonical and exact-head verified at canonical checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1`.
- Deterministic inventory at that checkpoint: 588 enhanced / 2,123 pending / 2,711 total; fingerprint `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- Q2 remains `needs_manual_review`; the absent numbered 1–4 legend was not invented.

## CURRENT_UNVERIFIED

- Subject: Anatomy.
- Batch ID: `anatomy-20260913-ch6-q8-q18`.
- Exact canonical base SHA: `58bb99d5c1fc96a98b4f922a963dba16105487d1`.
- Branch: `automation/marrow-explanations-anatomy-20260913-ch06-q008-q018`.
- PR: #56.
- Current content/verification head before this handoff commit: `2c68863e8fe94a83797547886de8ebb98406a336`.
- Stable-ID scope: `marrow__ANAT_CH06_Q008..Q018`, 11 contiguous questions, workload score 16.5.
- Source chapter: Anatomy Ch6 — Cardiovascular and Respiratory Systems. Legacy derived audit view was used only after confirming the canonical Ch6 source remains byte/object-equivalent for the validated chapter lineage; canonical Anatomy source SHA is `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`.
- Raw imported source was not changed. Source tables/figures/provenance remain owned by canonical source. Q12, Q16, Q17 and Q18 are figure-dependent; Q18 also has a structured table and received a dedicated stable-ID browser/table regression.
- Content file: `data/marrow/explanation_anatomy_ch06_q008_q018_v1.json`.
- Validator: `tools/test_marrow_anatomy_explanation_rollout.py` now validates both Ch6 Q1–Q7 and Q8–Q18 against canonical/legacy source equivalence, emphasis anchors, answer/distractor mapping and stable IDs.
- Browser regression: `tools/verify_marrow_anatomy_ch06_q018_browser.py`, wired through `tools/verify_marrow_bank_browser.py`; it checks stable ID, three distractor rationales, Q18 structured-table cells, no `[object Object]`, and the shared FSRS dock.
- Inventory is intentionally not hand-forged on the side branch. Expected deterministic count after regeneration is 599 enhanced / 2,112 pending / 2,711 total; the new fingerprint must be produced by `tools/inventory_marrow_explanations.py --write` from the canonical corpus.
- PR Engineering Gate run `34721119447` started on head `2c68863e...`; because the side branch does not contain a regenerated inventory, inventory validation is expected to remain the gating reconciliation step. Do not treat this batch as STATIC_VALIDATED or FULLY_VERIFIED until the deterministic inventory and exact-current-head gates pass.

## Exact next action

1. Resolve live canonical head and authoritative explanation ownership again.
2. If canonical is unchanged and no competing explanation writer exists, reconcile PR #56 / the stable-ID-scoped batch into canonical without overwriting newer product/image work.
3. Allow the canonical `Refresh full-corpus explanation inventory` workflow to regenerate the inventory; verify 599 / 2,112 / 2,711 and record its new fingerprint.
4. Require exact-current-head Engineering Gate plus full Android/PWA/browser/APK/package/reproducibility/preview verification. The Q18 stable-ID browser/table regression must pass in the generated learner path.
5. Only after those exact-head gates pass mark Q8–Q18 FULLY_VERIFIED and release the explanation lane. Do not start Q19+ in the same run that reaches FULLY_VERIFIED.
6. Production promotion remains prohibited.
