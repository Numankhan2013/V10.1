# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- Accepted product commit: `125d68b`.
- Accepted baseline: V11.6 remains the rollback product baseline; the canonical Continue Practice contract below is separately user/device accepted.
- **Sole Marrow/product integration trunk:** `feature/marrow-canonical-full-current`.
- Production / `main` remains explicit and guarded; do not promote without user approval.
- Resolve live canonical HEAD at run start; do not hardcode it into automation logic.
- Latest accepted Practice behavior was verified from canonical checkpoint `74abb670c3ae088e06653681e85c347212222455`; full Android/PWA/browser/APK/package/preview run `34695680534` succeeded and the user physically confirmed the resulting Continue Practice flow works. This is build-verified, device-verified, and user-accepted.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.
- Raw imported source remains immutable.
- Canonical source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Mandatory automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · FSRS · Tests · Insights · More**.
- Study hierarchy: **My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test**.
- FSRS remains review-only; genuinely unseen questions are not introduced by FSRS.
- Old Wrong Questions dashboard/tab remains retired/replaced by Spaced FSRS.
- Preserve approved V3 Home/Topics/question/Review/FSRS/module/timing behavior; do not restore rank/membership UI.

## Accepted Practice / Continue Practice contract — user/device verified

- Normal Practice question footer = **Previous + Next only**.
- Header grid icon and end-of-session boundary open the **same final review grid**.
- Final review action area = **Pause + Submit only**.
- Do not restore the redundant intermediate Question Navigator, `Back to question`, or `Review unanswered` actions.
- Pause preserves the **same active session**, complete original ordered `sessionQuestionIds`, saved/current index, answers, submitted state, timing and progress.
- Pause does **not** mark the current unanswered question skipped merely because the learner exits.
- Home Continue Practice resumes the **same session ID**, restores the **complete original test/question list**, and returns to the saved position with answered progress intact.
- If an older buggy client reduced `questionIds` to one current question, rebuild the visible session from `sessionQuestionIds`.
- A resumed multi-question session must never collapse to `1 / 1`.
- Special modes (CBT, Review, Wrong/Bookmarks, FSRS, Custom Study Modules) remain outside this override unless explicitly redesigned.
- Postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`; implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Status: **accepted / user-device verified**. Do not describe this flow as pending.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order.
- `[object Object]` in learner-visible output is a hard failure.
- Table-bearing browser regressions must verify actual expected cell content, not container existence.
- User physically verified the structured-table repair at canonical commit `c829599050173d24408b72e8dc564ba501a156b4`.

## Explanation lane

### FULLY_VERIFIED_HISTORY

- Anatomy Ch6 Q1–Q7 (`marrow__ANAT_CH06_Q001..Q007`) is reconciled into canonical and exact-head verified at canonical checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1`.
- Inventory at that verified checkpoint: **588 enhanced / 2,123 pending / 2,711 total**, fingerprint `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- Q2 remains `needs_manual_review` because the defining numbered 1–4 legend is absent; do not invent it.

### CURRENT_UNVERIFIED — Anatomy owns the lane

- Batch ID: `anatomy-20260913-ch6-q8-q18`.
- Scope: `marrow__ANAT_CH06_Q008..Q018`, **11 contiguous questions**, workload score **16.5**.
- Branch: `automation/marrow-explanations-anatomy-20260913-ch06-q008-q018`; PR **#56**; exact canonical base `58bb99d5c1fc96a98b4f922a963dba16105487d1`.
- Live canonical was rechecked unchanged immediately before the latest bounded repair. Raw source remains unchanged; Anatomy source SHA remains `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`.
- Q12/Q16/Q17/Q18 are figure-dependent. Q18 also owns a structured table and has a stable-ID browser regression that verifies meaningful table cells, rejects `[object Object]`, requires exactly three distractor rows and preserves the shared FSRS dock.
- Initial Engineering Gate `34721151621` failed only because the persisted deterministic explanation inventory still represented the preceding 588-enhanced checkpoint; all earlier shared checks passed.
- A bounded diagnostic run `34726572358` produced the exact deterministic manifest: **599 enhanced / 2,112 pending / 2,711 total**, fingerprint `549af134d84553c1227a9994de67c35bcdae216ad30d7c8be2bcfb844754c902`; raw source hashes and inventory flag counts did not drift.
- The exact manifest is now stored in `data/marrow/explanation_inventory_v1.json`. The temporary diagnostic was removed again. Content/inventory/validator head before the memory checkpoints was `43b2e4963fcd15aa0a4caae0a68fb7a827b305bd`.
- Dedicated handoff: `.project-memory/ANATOMY_EXPLANATION_HANDOFF_2026-09-13.md`.
- This batch is **PR_OPEN_CI_PENDING**, not FULLY_VERIFIED. Only CI attached to the final current PR head may certify it. No Q19+ content has been started.

## Image lane

- Automated Biochemistry image integration is paused. Ch4 Q11 remains the exact unresolved Biochemistry reference and is preserved as `REVIEW_REQUIRED`; two recovery attempts failed before shared registry/progress mutation because embedded PDF text was corrupted.
- Manual Physiology Batch 01 was completed on `automation/marrow-images-physiology-manual-20260912-b01`, based on canonical SHA `4f716c3a8eb2c6bc8030bb638a766580f5ddeca3`, and verified product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` was reconciled into canonical.
- Product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` passed Engineering Gate `34699015727` and full Android/PWA/browser/image-comparison/APK/package run `34699016754`; production promotion skipped.
- Current Physiology image coverage remains incomplete; next deterministic reference is `marrow__PHYS_CH03_Q007:figure:1` only after fresh ownership checks.

## Anti-fragmentation rules

- Explanation and image work build from `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Re-read canonical `STATE.md`, live commit, inventory/registry fingerprints and current ownership before editing.
- A stale PR/branch is historical evidence, not a lock and not a merge target.
- Donate old work only by stable-ID/content-scoped transplant after ownership and duplicate checks.
- Reconcile verified work into canonical before starting another conflicting batch in the same lane.
- Product/UI fixes that become accepted are protected canonical behavior for subsequent content/image/explanation work.

## Known problems / cautions

- Anatomy Ch6 Q8–Q18 is still CURRENT_UNVERIFIED and blocks other explanation writers until exact-head candidate and canonical certification finish.
- Physiology image coverage remains incomplete, and Biochemistry Q11 remains unresolved/paused.
- Production promotion remains prohibited unless explicitly requested by the user.

## Current priorities / Next step

1. **Explanation lane:** resolve the final PR #56 head after the memory checkpoints and require fresh Engineering Gate on that exact SHA. If green, require the full Android/PWA/browser/APK/package/reproducibility/preview workflow on the same candidate SHA. Then reconcile to canonical only if canonical is still the recorded base, and require exact-current-canonical-head Engineering + full certification before moving Q8–Q18 to FULLY_VERIFIED_HISTORY and releasing the lane. Stop after FULLY_VERIFIED; do not start Q19+ in that same run.
2. **Main product work:** preserve the accepted Practice/Continue Practice contract above.
3. **Image lane:** begin no new conflicting batch without fresh ownership/live-canonical checks; keep Biochemistry Q11 unresolved rather than inventing source recovery.
4. Production promotion remains prohibited unless the user explicitly asks for it.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- Accepted Practice implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice failure/postmortem/lessons: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
