# Anatomy Explanation Ch6 Q1–Q7 Handoff

## CURRENT_UNVERIFIED

- Owner: Anatomy
- BATCH_ID: `anatomy-20260912-ch6-q1-q7`
- Range: Anatomy Ch6 Q1–Q7, 7 contiguous questions, workload score 16.5
- Sole integration trunk: `feature/marrow-canonical-full-current`
- Exact canonical base for this reconciliation: `a3a4dbe80504c9214f8ffb8c7ac9479cb2798be1`
- Active batch branch: `feature/marrow-explanation-rollout-anatomy-ch06-q001-q007-canonical-r4`
- State: `STATIC_VALIDATED`; deterministic inventory and durable browser regression are prepared, exact-head r4 certification is pending.
- Reconstruction: `marrow__ANAT_CH06_Q002` remains `needs_manual_review`; source-rendered numbered 1–4 legend is missing. Teach only the recoverable named cranial→caudal order and preserve source key D; do not invent the number mapping.
- Canonical Anatomy source bundle SHA: `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`
- Deterministic inventory after this batch: 2,711 total / 588 enhanced / 2,123 pending; fingerprint `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- Durable browser regression: `tools/verify_marrow_anatomy_ch06_q002_browser.py`, routed through the shared Marrow browser gate. It requires the stable ID in generated PWA bytes, navigates Anatomy → Marrow → Ch6 → Q2, verifies the safe learner-facing reconstruction, exactly three distractor rationales, and shared FSRS recall dock.
- Previous r3 exact-head Engineering Gate `34695148863` passed. Previous r3 full run `34695122510` reached the new browser regression and failed only because its first version incorrectly required the stable ID to occur exactly once in generated PWA bytes; the generated runtime correctly contained it twice. That test guard was repaired to require presence, not uniqueness. r3 is now history/evidence because canonical advanced.
- No raw source mutation. No production promotion.

## FULLY_VERIFIED_HISTORY

Unchanged from canonical `STATE.md`. This Ch6 Q1–Q7 batch is not FULLY_VERIFIED until reconciled into the sole canonical trunk and exact-current-head Engineering plus full Android/PWA/browser/APK/package/reproducibility/preview certification pass.

## Exact next action

Open the canonical-r4 PR only if live canonical still matches the recorded base; run exact-head Engineering and full build. If both pass, reconcile into `feature/marrow-canonical-full-current`, update authoritative canonical project memory, then certify the resulting exact canonical head before releasing the Anatomy explanation lane. Do not start Ch6 Q8+ in the same run.
