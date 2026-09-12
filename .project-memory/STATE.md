# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- Accepted product commit: `125d68b`.
- Accepted baseline: V11.6 remains the rollback product baseline; the canonical Continue Practice contract below is separately user/device accepted.
- **Sole Marrow/product integration trunk:** `feature/marrow-canonical-full-current`.
- Product/UI base remains the user-approved V3/correct-index lineage.
- Production / `main` remains explicit and guarded; do not promote without user approval.
- Resolve the live canonical HEAD at run start. Do not hardcode a supposed current HEAD into automation logic.
- Latest accepted Practice behavior was verified from canonical checkpoint `74abb670c3ae088e06653681e85c347212222455`; full Android/PWA/browser/APK/package/preview run `34695680534` succeeded and the user physically confirmed the resulting Continue Practice flow works. This is build-verified, device-verified, and user-accepted.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 visible source topics**.
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

This section supersedes all earlier remaining-only or 16-of-20 resume descriptions.

- Normal Practice question footer = **Previous + Next only**.
- Header grid icon and end-of-session boundary open the **same final review grid**.
- Final review action area = **Pause + Submit only**.
- Do not restore the redundant intermediate Question Navigator, `Back to question`, or `Review unanswered` actions.
- Pause preserves the **same active session**, full original ordered `sessionQuestionIds`, saved/current index, answers, submitted state, timing and progress.
- Pause does **not** mark the current unanswered question skipped merely because the learner exits.
- Home Continue Practice resumes the **same session ID**, restores the **complete original test/question list**, and returns to the saved position with answered progress intact.
- If an older buggy client reduced `questionIds` to one current question, rebuild the visible session from `sessionQuestionIds`.
- A resumed multi-question session must never collapse to `1 / 1`.
- Special modes (CBT, Review, Wrong/Bookmarks, FSRS, Custom Study Modules) remain outside this override unless explicitly redesigned.
- The exact failure history, mistakes, lessons, do/don't rules and regression sequence are in `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Status: **accepted / user-device verified**. Do not describe this flow as pending.

## Practice regression sequence required for future changes

Any change touching Home, Practice, session persistence, sync, question navigation, final review, FSRS injection or build transforms must exercise the actual generated learner path:

1. Start a genuine multi-question Practice session.
2. Answer several questions and leave at least one unanswered.
3. Open the final review grid and press Pause.
4. Confirm Home/dashboard and paused lifecycle.
5. Click the actual rendered Home Continue Practice control.
6. Verify same session ID, complete original ordered IDs, saved/current index and preserved submitted progress.
7. Verify no `1 / 1` collapse and no Pause-as-Skip mutation.

Do not certify this behavior by calling only an internal helper or by using a superseded selector.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order.
- `[object Object]` in learner-visible output is a hard failure.
- Table-bearing browser regressions must verify actual expected cell content, not container existence.
- The user physically verified the structured-table repair at canonical commit `c829599050173d24408b72e8dc564ba501a156b4`.

## Explanation lane

- Canonical explanation inventory before Anatomy Ch6 Q1–Q7: **581 enhanced / 2,130 pending / 2,711 total**.
- Anatomy Ch6 Q1–Q7 has been repeatedly rebased/reconciled as canonical advanced. Historical PRs #43/#49/#50 are not merge targets.
- Current newest open reconciliation is **PR #52**, branch `feature/marrow-explanation-rollout-anatomy-ch06-q001-q007-canonical-r4`, based on canonical checkpoint `a3a4dbe80504c9214f8ffb8c7ac9479cb2798be1`, head `7bee1f4118e084fa7e5e8934fedf26e8f131f73b`.
- Scope is stable-ID limited to `marrow__ANAT_CH06_Q001..Q007`; raw source unchanged.
- Deterministic inventory on that reconciliation is **588 enhanced / 2,123 pending / 2,711 total** with fingerprint `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- Q2 remains `needs_manual_review` because the rendered source omits the defining numbered 1–4 legend; do not invent the missing mapping.
- Because canonical has advanced again with accepted Practice memory updates, the explanation worker must resolve live canonical before merging or mutating and must rebase/reconcile if required. Do not wholesale-merge stale branch history.

## Image lane

- Automated Biochemistry image integration remains paused. Ch4 Q11 is still the exact unresolved Biochemistry reference and remains `REVIEW_REQUIRED`; do not silently bypass it.
- **Physiology Fast-Lane Batch 02** reviewed the next 40 source references from canonical base `700cde07869068a7d3aadf77dc89d7bd85726530` on `manual/marrow-physiology-fastlane-20260912-b02`. Source-review run `34700776495` produced 14 exact `SOURCE_METADATA_INVALID` adjudications, 0 safe reuse bindings, 12 clean new assets/bindings, and 14 specialist `REVIEW_REQUIRED` deferrals.
- The 12 clean assets are bound to `PHYS_CH03_Q007`, `PHYS_CH03_Q018`, `PHYS_CH03_Q022`, `PHYS_CH04_Q003`, `PHYS_CH04_Q012`, `PHYS_CH05_Q024`, `PHYS_CH06_Q008`, `PHYS_CH07_Q011` figures 3/4, `PHYS_CH07_Q012` figure 2, `PHYS_CH07_Q015`, and `PHYS_CH07_Q020`. Native source pixels/regions were preserved; no generative medical processing was used.
- Apply workflow run `34703103259` passed canonical/shared-state locks, materialization, registry/progress/coverage checks, image tests, build-pipeline/product-contract checks, strict mutation scope, post-commit exact-head validation, and push. Image-data commit is `aedfe3164da35e875db347483d8db3283169f8c0`.
- Physiology coverage after Batch 02 is **294 raw / 276 effective / 56 released / 18 invalid metadata / 74 resolved / 14 tracked-unreleased / 206 untracked / 28 text-cue**. Global released-question count is 179; Physiology has 48 approved assets / 50 tracked assets / 49 released questions.
- The 14 D decisions are not skipped or resolved; they remain specialist-lane work. The next deterministic unresolved Physiology reference is `marrow__PHYS_CH03_Q013:figure:2` (multiple plausible page-47 candidates; exact Na+/K+-ATPase ownership/crop requires specialist review).
- Targeted learner/browser QA is **triggered for this clean exact-head checkpoint and pending**; it must pass before canonical reconciliation. Full Android/PWA/APK checkpoint is intentionally amortized because Batch 02 changes image data only; production promotion remains prohibited.

## Anti-fragmentation rules

- Explanation and image work build from `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Re-read canonical `STATE.md`, live commit, inventory/registry fingerprints and current ownership before editing.
- A stale PR/branch is historical evidence, not a lock and not a merge target.
- Donate old work only by stable-ID/content-scoped transplant after ownership and duplicate checks.
- Reconcile verified work into canonical before starting another conflicting batch in the same lane.
- Product/UI fixes that become accepted must be treated as protected canonical behavior by subsequent content/image/explanation work.

## Known problems / cautions

- Physiology image coverage remains incomplete after Fast-Lane Batch 02; 14 reviewed specialist deferrals remain unresolved, beginning with `marrow__PHYS_CH03_Q013:figure:2`. Biochemistry Q11 remains unresolved/paused.
- Former canonical tip `4f716c3` had a memory-validator wording failure only; the reconciled batch restores the required status vocabulary without changing accepted product behavior.

## Current priorities / Next step

1. **Main product work may proceed from live canonical.** Preserve the accepted Practice contract above.
2. **Explanation lane:** reconcile Anatomy Ch6 Q1–Q7 from the newest valid stable-ID scope onto the then-live canonical head, re-run exact-head deterministic/browser/full gates, then release the lane only after canonical integration.
3. **Image lane:** Batch 02 image data is committed on the fast-lane branch and deterministic source gates are green. Run/inspect the targeted changed-question learner QA, then reconcile the verified branch into canonical. After reconciliation, continue the specialist lane from `marrow__PHYS_CH03_Q013:figure:2`. Keep automated Biochemistry paused with Q11 preserved unresolved.
4. Production promotion remains prohibited unless the user explicitly asks for it.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- Accepted Practice implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice failure/postmortem/lessons: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
