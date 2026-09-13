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
- Correction after user preview review: verified follow-up `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3` adds stable-ID, source-fingerprinted learner-display overrides for Physiology Ch5 and Ch7. Engineering `34740460617` and full Android/PWA/browser/APK/package run `34740465004` passed; preview `https://c4744474.nk-qbank.pages.dev`; production skipped. Do not claim other chapters are visually clean without equivalent reviewed overrides/browser evidence.

## Explanation lane

### FULLY_VERIFIED_HISTORY

- Anatomy Ch6 Q1–Q7 (`marrow__ANAT_CH06_Q001..Q007`) is canonical history. Certified checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1`; exact-head Engineering Gate `34715415821` and full Android/PWA/APK/package run `34715415818` passed. Historical PR #52 is evidence only and non-blocking.
- Physiology Ch11 Q1–Q6 (`marrow__PHYS_CH11_Q001..Q006`) is reconciled canonical history at merge commit `e01cc0b9a8e62885d29b0c2e7ac6417ce8c96f05`; older CURRENT_UNVERIFIED memory is stale evidence only.

### CURRENT_UNVERIFIED — Anatomy owns the lane

- Batch ID: `anatomy-20260913-ch6-q8-q18-r2`.
- Scope: `marrow__ANAT_CH06_Q008..Q018`, **11 contiguous questions**, workload score **16.5**. No Q19+ work has started.
- Stale donor PR #56 / branch `automation/marrow-explanations-anatomy-20260913-ch06-q008-q018` remains history only and must never be merged.
- Fresh transplant branch `automation/marrow-explanations-anatomy-20260913-ch06-q008-q018-r2` was created from exact canonical base `e01cc0b9a8e62885d29b0c2e7ac6417ce8c96f05`. Candidate PR #58 was merged only after exact candidate certification; canonical merge commit is `420928ae4e1314cb3a23c8687801be5c7b1f0a8c`.
- Candidate exact SHA `9b625f6a881482e43429d97f817128ec917bbfe2` passed Engineering Gate `34744191423` and full Android/PWA/browser/APK/package/reproducibility/preview run `34744283759` on the same SHA. The full build passed generated Marrow browser checks, structured-table rendering, Continue Practice regression, APK/package checks, reproducibility manifest, and preview deployment; production promotion was skipped.
- Stable-ID content lineage: augmentation `ef4475b24927a28e2ce233793789dd1096b1a390`; Anatomy validator `3c8463a64b683312ef84d2024e95bddcd5cfe972`; Q18 stable-ID browser regression `9816dc73cfd03d39a0c8983975efd2f0a0b5ef3e`; shared browser wrapper reconciliation `4013cdc7b42c6d4dc91df3021a0231615fd1591d` preserves the Physiology Ch11 regression.
- Q12/Q16/Q17/Q18 remain figure-dependent through immutable source metadata. Q18 also owns a structured embryological-remnants table; the stable-ID browser test verifies meaningful cells, rejects `[object Object]`, requires exactly three distractor rows, and preserves the FSRS recall dock.
- Deterministic canonical inventory is now **605 enhanced / 2,106 pending / 2,711 total**, fingerprint `995717a6ac450e2b6a530e0521d58a43e67d4e980401989c69b544c38de98300`. Raw source hashes remain Anatomy `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`, Biochemistry `919f0709b2eb833e302c6f7524b6dd2bd13bfaed638009375b5062135d3795b1`, Physiology `f3cd6b9dccb2092743fa86de4b0bef682d61c83762e9f00fa3b04d0a355d89d6`; flag counts are unchanged.
- Raw imported source is unchanged. The canonical inventory workflow produced formatting-only tip `c4a5e24074a6a4da25efce7e669ceb6ed6678ff8` after the merge.
- State: **PR_OPEN_CI_PENDING** only because the exact current canonical head created by this memory checkpoint must itself pass Engineering Gate and the full Android/PWA/browser/APK/package/reproducibility/preview workflow. Candidate-level content certification is already green and the batch is reconciled into canonical.
- Exact next action: require both canonical workflows to pass on the exact same post-memory canonical SHA. If they pass and canonical has not advanced, move this batch to `FULLY_VERIFIED_HISTORY`, release the explanation lane, and stop without starting Q19+ in the same run. If canonical moves again, do not release the lane until the new exact head is certified.
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

- Anatomy Ch6 Q8–Q18 is reconciled into canonical but remains CURRENT_UNVERIFIED until exact-current-head canonical Engineering + full build complete.
- Physiology image coverage remains incomplete after the verified bounded batch, and Biochemistry Q11 remains unresolved/paused.
- Production promotion remains prohibited unless explicitly requested.

## Current priorities / Next step

1. **Explanation lane:** certify the exact post-memory canonical head with Engineering Gate and full Android/PWA/browser/APK/package/reproducibility/preview. On dual success without a newer canonical commit, mark Anatomy Q8–Q18 FULLY_VERIFIED, release the lane, and stop; do not start Q19+ in this run.
2. **Main product work may proceed from live canonical.** Preserve the accepted Practice contract above.
3. **Image lane:** Batch 02 is unverified historical evidence only; resume from live canonical after fresh ownership/fingerprint checks. Keep automated Biochemistry paused with Q11 unresolved.
4. Production promotion remains prohibited unless the user explicitly asks for it.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- Accepted Practice implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice failure/postmortem/lessons: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
