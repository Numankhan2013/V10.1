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

## Learner-content hygiene

- User-reported serialized JSON/code leakage in Marrow question, option and explanation surfaces is fixed on verified candidate `45f6539fff535fadc6aaa6970894f9ff123422fa`, based on canonical `58bb99d5c1fc96a98b4f922a963dba16105487d1`. The prior memory-only handoff was `0efdd434`; its substantive but unverified implementation checkpoint was `a3f0e3da`.
- The durable fix sanitizes learner-facing Marrow strings/structured values at registration and again after all 2,711 canonical records are injected; raw ED8 source is unchanged. It covers stems, options, option rationales, answers, explanations, takeaways and structured-explanation text while preserving tables/figures and ordinary medical notation.
- Full-corpus regression passed **2,711 questions / 27,898 learner-facing fields**. Physiology Ch5 and Ch7 have a 390x844 real-browser regression covering question, options, answer-time study support, tuned explanation and three distractor rationales.
- Root cause of the old sanitizer branch browser failure was a hidden unrelated topic-numbering side effect in the former hygiene installer. Topic numbering is now an explicit protected build stage; sanitation remains logically independent.
- Exact candidate Engineering Gate `34738522874` and full Android/PWA/browser/APK/package/preview run `34738530102` passed. Preview `https://8d6d9366.nk-qbank.pages.dev`; production promotion skipped.

- Correction after user preview review: the first sanitizer gate caught serialized JSON but missed OCR/code-like debris already embedded in source-transcribed question and option strings. Verified follow-up `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3` adds stable-ID, source-fingerprinted learner-display overrides for every Physiology Ch5 and Ch7 question: **63 questions, 252 options, and matching correct-answer display text**. Raw source and answer indexes are unchanged. The browser gate now compares all 315 rendered question/option values exactly and opens Ch5 Q1 plus Ch7 Q1, Q2 and Q35 through the learner UI. Engineering `34740460617` and full Android/PWA/browser/APK/package run `34740465004` passed; preview `https://c4744474.nk-qbank.pages.dev`; production skipped. Do not claim other chapters are visually clean without equivalent reviewed overrides/browser evidence.

## Explanation lane

### FULLY_VERIFIED_HISTORY

- Anatomy Ch6 Q1–Q7 is canonical history, not current ownership. Its certified checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1` is an ancestor of the Physiology batch base; exact-head Engineering Gate `34715415821` and full Android/PWA/APK/package run `34715415818` passed there. Historical PR #52 remains evidence only and is non-blocking.
- Canonical pre-batch inventory at Physiology acquisition was **588 enhanced / 2,123 pending / 2,711 total**, Physiology raw SHA `f3cd6b9dccb2092743fa86de4b0bef682d61c83762e9f00fa3b04d0a355d89d6`.

### CURRENT_UNVERIFIED

- Owner: **Physiology Chapter 11 Q1–Q6** (`marrow__PHYS_CH11_Q001..Q006`), one bounded source-order batch, workload score **16.0**.
- Branch: `feature/marrow-explanation-physiology-ch11-q001-q006-20260913`; exact canonical base SHA `4f943af34bb4bd49f644f2655e23459fc1534031`.
- Authored content commit: `bd3e2f814f0fd2a2cf901b5b2a1bee1f132da0ec`; bounded-prefix validator commit: `9e34d44aef7de7a92e6ad17afe9d3f8b7681a195`.
- Q1/Q2/Q5 preserve source figure metadata through the immutable canonical source record. Q6 uses `resolved_reconstruction` to preserve source-keyed option A while explicitly correcting the overbroad claim that mechanoreceptor and exteroceptor are universally synonymous.
- Deterministic candidate inventory: **594 enhanced / 2,117 pending / 2,711 total**; question-record fingerprint `f860fc38da57af2d20be05efa33a5594b08425008a2cbcb2f3dff0bfdd27b974`; raw source unchanged.
- State: **STATIC_VALIDATED**. Inventory, Physiology rollout, Anatomy rollout, and Biochemistry rollout validators passed before this memory checkpoint was committed.
- Still required before `FULLY_VERIFIED`: stable-ID real-browser regression for this batch; shared Practice/CBT/Review/FSRS regressions; PR/exact-head Engineering Gate; full Android/PWA/APK/package/reproducibility/preview verification; reconciliation back into `feature/marrow-canonical-full-current` followed by canonical exact-head certification if canonical moved.
- Production promotion remains prohibited.
## Image lane

- Automated Biochemistry image integration is paused. Ch4 Q11 remains the exact unresolved Biochemistry reference and is preserved as `REVIEW_REQUIRED`; two recovery attempts failed before shared registry/progress mutation because embedded PDF text was corrupted. No verified Q11 learner-facing result exists on a side branch, and no Biochemistry work was skipped or newly started.
- Manual Physiology Batch 01 was completed on `automation/marrow-images-physiology-manual-20260912-b01`, based exactly on canonical SHA `4f716c3a8eb2c6bc8030bb638a766580f5ddeca3`, and its verified product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` was fast-forwarded into the sole canonical trunk.
- The bounded source-order scope is six references: `marrow__PHYS_CH01_Q009:figure:1`, `marrow__PHYS_CH01_Q018:figure:1`, `marrow__PHYS_CH01_Q021:figure:1`, `marrow__PHYS_CH01_Q021:figure:2`, `marrow__PHYS_CH02_Q020:figure:1`, and `marrow__PHYS_CH03_Q005:figure:2`.
- Source review workflow `34698354509` confirmed the first four are table-only metadata already represented by structured tables, Q20 is a question-critical four-tile clinical photograph requiring a precise authentic region render, and Q5 figure 2 is the repeated page-44 diffusion plot. The first four references were adjudicated `SOURCE_METADATA_INVALID`; Q20 gained PASS question binding `physiology-f675135b3bc1c381`; Q5 gained a second PASS explanation binding to existing asset `physiology-95389f30f8277be3`.
- Product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` passed Engineering Gate `34699015727` and full Android/PWA/browser/image-comparison/APK/package run `34699016754`; source/production and emitted Q20/Q5 screenshots were inspected and passed. Preview `https://72286d5a.nk-qbank.pages.dev`; production promotion skipped.
- Physiology Batch 02 exists only on historical side branch `manual/marrow-physiology-fastlane-20260912-b02`: 40 references audited, 14 metadata-invalid, 12 new assets, 14 specialist deferrals, image-data commit `aedfe3164`. Its latest targeted run `34704088880` failed canonical wiring at head `7505a7c`; it was never reconciled. Canonical coverage therefore remains 294 raw / 290 effective / 44 released / 4 invalid metadata / 48 resolved / 21 tracked-unreleased / 225 untracked / 28 text-cue. The image writer is released; next canonical reference remains `marrow__PHYS_CH03_Q007:figure:1`.

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
2. **Explanation lane:** Physiology Ch11 Q1–Q6 is `CURRENT_UNVERIFIED` on the exact canonical base recorded above. Finish stable-ID browser/full exact-head certification and reconcile it into live canonical before releasing the lane.
3. **Image lane:** Batch 02 is unverified and unreconciled historical evidence only; do not treat its 12 assets as canonical. Resume from live canonical at `marrow__PHYS_CH03_Q007:figure:1` after fresh ownership/fingerprint checks. Keep automated Biochemistry paused with Q11 preserved unresolved.
4. Production promotion remains prohibited unless the user explicitly asks for it.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- Accepted Practice implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice failure/postmortem/lessons: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
