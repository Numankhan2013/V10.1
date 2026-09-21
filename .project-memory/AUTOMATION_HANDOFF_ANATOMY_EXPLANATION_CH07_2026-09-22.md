# Anatomy explanation automation handoff — Chapter 7 acquisition

- State: PREAUDITED.
- Subject: Anatomy.
- Canonical integration trunk: `feature/marrow-canonical-full-current`.
- Exact canonical base at acquisition: `8378ba6db8c7c0f95bfcc3a9b71efbf2ccebbe78`.
- Batch branch: `feature/marrow-explanations-anatomy-20260922-ch07`.
- Previous Anatomy content through Ch6 Q25 is FULLY_VERIFIED_HISTORY; the follow-up validator repair was reconciled by canonical merge `8378ba6db8c7c0f95bfcc3a9b71efbf2ccebbe78`.
- Deterministic canonical inventory at acquisition: 622 enhanced-reference / 2,089 pending / 2,711 total. Anatomy source raw SHA-256: `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`.
- Canonical `STATE.md` explanation-lane paragraph is stale (it still reports 615/2096 and predates the Q19-Q25 reconciliation); it is treated as derived handoff drift, not as a blocker. Live canonical Git + `data/marrow/explanation_inventory_v1.json` + the Q19-Q25 handoff govern this acquisition.
- No learner-facing content or raw source has been changed yet.
- Exact next source-order start: resolve the first pending stable Anatomy ID after `marrow__ANAT_CH06_Q025` from the canonical 1,115-question source. Expected chapter transition is Chapter 7, but do not author until source ID/key/ownership is read and verified.
- Next action: complete source audit for the contiguous Chapter 7 prefix, calculate workload score (target 16, max 20, max 18 questions), then author exactly one bounded augmentation batch. Preserve raw source, figures/tables/provenance and reconstruction metadata.
- Full-CI liveness: this branch uses `feature/marrow-explanations-*`, so pushes are eligible for the required full Android/PWA workflow. Exact-SHA Engineering + full Android/PWA/APK/package/reproducibility/preview certification are required before canonical reconciliation.
- Production promotion prohibited.
