# Anatomy Explanation Ch6 Q1–Q7 Handoff

## CURRENT_UNVERIFIED

- Owner: Anatomy
- BATCH_ID: `anatomy-20260912-ch6-q1-q7`
- Range: Anatomy Ch6 Q1–Q7, 7 contiguous questions, workload score 16.5
- Sole integration trunk: `feature/marrow-canonical-full-current`
- Exact canonical base for this reconciliation: `700cde07869068a7d3aadf77dc89d7bd85726530`
- Active batch branch: `feature/marrow-explanation-rollout-anatomy-ch06-q001-q007-canonical-r5`
- Stable-ID transplant/content commit: `a86967b5950db9533f2bb37aedb55eb4abd4a423`
- Inventory commit: `4b6a7dd7971002dfeeac989a4cf409a11261032d`
- State: `STATIC_VALIDATED`; fresh exact-head CI has not yet certified this r5 reconciliation.
- Reconstruction: `marrow__ANAT_CH06_Q002` remains `needs_manual_review`; source-rendered numbered 1–4 legend is missing. Teach only the recoverable named cranial→caudal order and preserve source key D; do not invent the number mapping.
- Canonical Anatomy source bundle SHA: `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`
- Deterministic inventory after this batch: 2,711 total / 588 enhanced / 2,123 pending; fingerprint `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- r5 was created directly from live canonical after the verified Physiology image batch and its memory checkpoint, preserving accepted Continue Practice and image state.
- No raw source mutation. No production promotion.

## FULLY_VERIFIED_HISTORY

Unchanged from canonical `STATE.md`. Ch6 Q1–Q7 is not FULLY_VERIFIED until the permanent Anatomy validator/browser regression and shared gates are present on this r5 candidate, exact-current-head Engineering plus full Android/PWA/browser/APK/package/reproducibility/preview certification pass, and the verified result is reconciled into the sole canonical trunk.

## Exact next action

Transplant/reconcile the r4 Anatomy validator, stable-ID browser regression, and only the minimal shared gate hooks required for this stable-ID scope onto r5 without overwriting newer canonical Practice/image changes. Re-read canonical STATE/head/inventory before those writes. Run exact-head Engineering Gate and the full Android/PWA/browser/APK/package/reproducibility/preview workflow. If green and canonical remains compatible, reconcile into `feature/marrow-canonical-full-current`, update canonical memory, certify the resulting exact canonical head, and release the Anatomy lane. Do not start Ch6 Q8+ in the same run.
