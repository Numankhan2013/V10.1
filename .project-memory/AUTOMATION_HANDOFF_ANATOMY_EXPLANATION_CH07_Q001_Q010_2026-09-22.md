# Anatomy explanation automation handoff — Ch7 Q1–Q10

State: **STATIC_VALIDATED candidate / exact-head CI pending**.

- Subject: Anatomy.
- Canonical base at acquisition and immediately before first mutation: `105cf02e358d8f869d745e698fc4faa32d777c92` on `feature/marrow-canonical-full-current`.
- Batch branch: `feature/marrow-explanations-anatomy-20260922-ch07-r2`.
- Batch: Chapter 7 `Alimentary, Hepatobiliary systems, Pancreas and Spleen`, Q1–Q10, 10 contiguous questions.
- Workload score: **15.5**. Figure-dependent Q2/Q5/Q6/Q7 add +1 each; Q10 has source figures plus a retained normalization/provenance note (+1.5 total modifier). No question was skipped.
- Source audit used the exact generated full-corpus artifact for canonical SHA `105cf02e...`, which contains Anatomy 1,115 / Biochemistry 582 / Physiology 1,014 = 2,711 Marrow records. All Q1–Q10 source IDs, options, keys, structured explanation/figure metadata and review status were inspected before authoring.
- Raw Anatomy source SHA remains `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`; raw source was not mutated.
- Reconstruction: none. Q10 retains the source's `pass_with_normalization_note` discrepancy: the stem says return by week 11 while source explanation describes the 6th–10th-week interval. Learner text preserves that distinction without changing the source key.
- Augmentation: `data/marrow/explanation_anatomy_ch07_q001_q010_v1.json`.
- Inventory before: **625 enhanced / 2,086 pending / 2,711 total**, fingerprint `27bd5f2e3da1e4eafd286a062e0784d21189d31a1cf0a09149e7359c8bad013e`.
- Inventory candidate after: **635 enhanced / 2,076 pending / 2,711 total**, fingerprint `4f2f313f29f8cd726eaa0e6bc7765590299d4c74415875b0121edb3cb53a3c1b`.
- Anatomy rollout validator now covers Ch6 Q1–Q25 plus Ch7 Q1–Q10 and preserves the existing Q2/Q24 `needs_manual_review` assertions.
- Representative stable-ID browser regression: `marrow__ANAT_CH07_Q010`, checking Chapter 7 count 21, omphalocele/gastroschisis discriminators, exactly three wrong-option rows and the shared FSRS dock.
- Current candidate head after content/inventory/validator/browser wiring must be resolved live from Git before certification; do not certify an earlier neighboring SHA.
- Production promotion is prohibited.

Exact next action: open/refresh the bounded PR to `feature/marrow-canonical-full-current`, require Engineering Gate and full Android/PWA/APK/package/reproducibility/preview success on the exact PR head, repair at most two failures per class, then reconcile the verified result into canonical before releasing the explanation lane. Do not start Ch7 Q11+ while this batch is unverified.
