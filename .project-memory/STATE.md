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

- Automated Biochemistry image integration is paused. Ch4 Q11 remains the exact unresolved Biochemistry reference and is preserved as `REVIEW_REQUIRED`; two recovery attempts failed before shared registry/progress mutation because embedded PDF text was corrupted. No verified Q11 learner-facing result exists on a side branch, and no Biochemistry work was skipped or newly started.
- Manual Physiology Batch 01 was completed on `automation/marrow-images-physiology-manual-20260912-b01`, based exactly on canonical SHA `4f716c3a8eb2c6bc8030bb638a766580f5ddeca3`, and its verified product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` was fast-forwarded into the sole canonical trunk.
- The bounded source-order scope is six references: `marrow__PHYS_CH01_Q009:figure:1`, `marrow__PHYS_CH01_Q018:figure:1`, `marrow__PHYS_CH01_Q021:figure:1`, `marrow__PHYS_CH01_Q021:figure:2`, `marrow__PHYS_CH02_Q020:figure:1`, and `marrow__PHYS_CH03_Q005:figure:2`.
- Source review workflow `34698354509` confirmed the first four are table-only metadata already represented by structured tables, Q20 is a question-critical four-tile clinical photograph requiring a precise authentic region render, and Q5 figure 2 is the repeated page-44 diffusion plot. The first four references were adjudicated `SOURCE_METADATA_INVALID`; Q20 gained PASS question binding `physiology-f675135b3bc1c381`; Q5 gained a second PASS explanation binding to existing asset `physiology-95389f30f8277be3`.
- Product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` passed Engineering Gate `34699015727` and full Android/PWA/browser/image-comparison/APK/package run `34699016754`; source/production and emitted Q20/Q5 screenshots were inspected and passed. Preview `https://72286d5a.nk-qbank.pages.dev`; production promotion skipped.
- Current Physiology coverage is 294 raw / 290 effective / 44 released / 4 invalid metadata / 48 resolved / 21 tracked-unreleased / 225 untracked / 28 text-cue; subject incomplete. The image writer is released and no second batch has begun.

## Anti-fragmentation rules

- Explanation and image work build from `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Re-read canonical `STATE.md`, live commit, inventory/registry fingerprints and current ownership before editing.
- A stale PR/branch is historical evidence, not a lock and not a merge target.
- Donate old work only by stable-ID/content-scoped transplant after ownership and duplicate checks.
- Reconcile verified work into canonical before starting another conflicting batch in the same lane.
- Product/UI fixes that become accepted must be treated as protected canonical behavior by subsequent content/image/explanation work.

## Known problems / cautions

- Physiology image coverage remains incomplete after the verified bounded batch, and Biochemistry Q11 remains unresolved/paused.
- Former canonical tip `4f716c3` had a memory-validator wording failure only; the reconciled batch restores the required status vocabulary without changing accepted product behavior.

## Current priorities / Next step

1. **Main product work may proceed from live canonical.** Preserve the accepted Practice contract above.
2. **Explanation lane:** reconcile Anatomy Ch6 Q1–Q7 from the newest valid stable-ID scope onto the then-live canonical head, re-run exact-head deterministic/browser/full gates, then release the lane only after canonical integration.
3. **Image lane:** Batch 01 is verified, reconciled, and the writer is clean. The next deterministic Physiology reference is `marrow__PHYS_CH03_Q007:figure:1` (explanation, source page 44, two native candidates, `UNTRACKED_SOURCE_VISUAL`). Keep automated Biochemistry paused with Q11 preserved unresolved; begin no new batch without fresh ownership and live-canonical checks.
4. Production promotion remains prohibited unless the user explicitly asks for it.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- Accepted Practice implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice failure/postmortem/lessons: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
