# Anatomy Explanation Ch6 Q1–Q7 Handoff

## CURRENT_UNVERIFIED

- Owner: Anatomy
- BATCH_ID: `anatomy-20260912-ch6-q1-q7`
- Range: Anatomy Ch6 Q1–Q7, 7 contiguous questions, workload score 16.5
- Sole integration trunk: `feature/marrow-canonical-full-current`
- Exact canonical base for this reconciliation: `a3a4dbe80504c9214f8ffb8c7ac9479cb2798be1`
- Active batch branch: `feature/marrow-explanation-rollout-anatomy-ch06-q001-q007-canonical-r4`
- Stable-ID transplant/content commit before this handoff update: `844447cce638fcc5827e41a20d1d70ffec3ee70b`
- Active PR: #52 targeting `feature/marrow-canonical-full-current`.
- State: `PR_OPEN_CI_PENDING`; this handoff update intentionally triggers exact-head CI for the repaired r4 candidate.
- Reconstruction: `marrow__ANAT_CH06_Q002` remains `needs_manual_review`; source-rendered numbered 1–4 legend is missing. Teach only the recoverable named cranial→caudal order and preserve source key D; do not invent the number mapping.
- Canonical Anatomy source bundle SHA: `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`
- Deterministic inventory after this batch: 2,711 total / 588 enhanced / 2,123 pending; fingerprint `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- Durable browser regression: `tools/verify_marrow_anatomy_ch06_q002_browser.py`, routed through the shared Marrow browser gate. It requires the stable ID in generated PWA bytes, navigates Anatomy → Marrow → Ch6 → Q2, verifies the safe learner-facing reconstruction, exactly three distractor rationales, and shared FSRS recall dock.
- Previous r3 exact-head Engineering Gate `34695148863` passed. Previous r3 full run `34695122510` reached the new browser regression and failed only because its first version incorrectly required the stable ID to occur exactly once in generated PWA bytes; the generated runtime correctly contained it twice. The repaired guard now requires presence, not uniqueness. r3 is history/evidence because canonical advanced.
- No raw source mutation. No production promotion.

## FULLY_VERIFIED_HISTORY

Unchanged from canonical `STATE.md`. This Ch6 Q1–Q7 batch is not FULLY_VERIFIED until reconciled into the sole canonical trunk and exact-current-head Engineering plus full Android/PWA/browser/APK/package/reproducibility/preview certification pass.

## Exact next action

Require Engineering Gate and full Android/PWA/browser/APK/package/reproducibility/preview to pass on the exact current r4 head. Then re-read canonical head/ownership. If canonical is unchanged from the recorded base, reconcile PR #52 into `feature/marrow-canonical-full-current`; otherwise transplant this stable-ID scope again onto the newer exact canonical head. After reconciliation, update authoritative canonical project memory and certify the resulting exact canonical head before releasing the Anatomy explanation lane. Do not start Ch6 Q8+ in the same run.
