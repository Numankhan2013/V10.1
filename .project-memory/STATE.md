# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- Accepted product commit: `125d68b`.
- Accepted baseline: V11.6 remains the rollback product baseline; the Continue Practice contract below is separately user/device accepted.
- **Sole Marrow/product integration trunk:** `feature/marrow-canonical-full-current`.
- Production / `main` remains explicit and guarded; do not promote without user approval.
- Resolve the live canonical HEAD at run start; never hardcode a supposed current HEAD into automation logic.
- Latest accepted Practice behavior was verified from checkpoint `74abb670c3ae088e06653681e85c347212222455`; full run `34695680534` succeeded and the user physically confirmed the Continue Practice flow. This behavior is build-verified, device-verified, and user-accepted.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.
- Raw imported source remains immutable.
- Source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Mandatory automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · FSRS · Tests · Insights · More**.
- Study hierarchy: **My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test**.
- FSRS schedules every answered question. Pause commits answered work only; final submission adds remaining unanswered session IDs as skipped. Questions outside a submitted session remain unseen and excluded.
- Old Wrong Questions dashboard/tab remains retired/replaced by Spaced FSRS.
- Preserve approved V3 Home/Topics/question/Review/FSRS/module/timing behavior; do not restore rank/membership UI.

## Accepted Practice / Continue Practice contract — user/device verified

- Normal Practice footer = **Previous + Next only**.
- Header grid icon and end-of-session boundary open the **same final review grid**.
- Final review action area = **Pause + Submit only**.
- Do not restore the redundant intermediate Question Navigator, `Back to question`, or `Review unanswered` actions.
- Pause preserves the same active session, full original ordered `sessionQuestionIds`, saved/current index, answers, submitted state, timing and progress.
- Pause does not mark the current unanswered question skipped merely because the learner exits.
- Home Continue Practice resumes the same session ID, restores the complete original ordered test/question list, and returns to the saved position with answered progress intact.
- If an older buggy client reduced `questionIds` to one current question, rebuild the visible session from `sessionQuestionIds`; a multi-question session must never collapse to `1 / 1`.
- Special modes (CBT, Review, Wrong/Bookmarks, FSRS, Custom Study Modules) remain outside this override unless explicitly redesigned.
- Postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`; implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Status: **accepted / user-device verified**. Do not describe this flow as pending.

## Mandatory Practice regression sequence

Any change touching Home, Practice, session persistence, sync, question navigation, final review, FSRS injection or build transforms must exercise the generated learner path: start a genuine multi-question Practice session; answer several questions while leaving at least one unanswered; open the final review grid and Pause; confirm Home/paused lifecycle; use the rendered Home Continue Practice control; verify same session ID, complete ordered IDs, saved/current index and preserved progress; verify no `1 / 1` collapse and no Pause-as-Skip mutation.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order; `[object Object]` is a hard failure.
- Browser regressions must verify meaningful expected cell content, not container existence.
- User physically verified the structured-table repair at `c829599050173d24408b72e8dc564ba501a156b4`.

## Reliability candidate — FSRS lifecycle + shared question presentation

- Substantive candidate commit: `cb37f577bd4cbe59e4005018d24dc7ba0f0bad18` (`Harden FSRS lifecycle and question presentation`).
- Corpus audit found eight PrepLadder records where table/explanation fragments were mixed into answer choices; four more records have no reliable answer contract.
- `question_presentation_core.js` separates coherent A–D/A–E choices from extraction-owned support fragments, renders matching/list material semantically in Practice/CBT/Review, and fails incomplete records closed. Source datasets remain unchanged.
- FSRS eligibility now includes correct-only attempts. Pause commits answered attempts/reviews without adding untouched questions; final Submit marks all remaining unanswered session IDs skipped.
- Deterministic helper/corpus tests pass locally. Generated-browser coverage exercises a broken PrepLadder matching record, incomplete-record fail-closed behavior, and answer→Pause→FSRS / Submit→skipped lifecycle boundaries.
- First exact-head Engineering Gate `34833580760` and full build `34833580864` both stopped at `verify_project_memory.py` before product tests because `STATE.md` exceeded 150 lines. This was a memory-placement failure, not evidence of a product-code failure.
- This checkpoint condenses `STATE.md` while preserving the already-updated `ARCHITECTURE.md`, `DECISIONS.md`, `PRODUCT.md`, and `SESSION_LOG.md` handoff material.
- Status: **CI_RETRY_REQUIRED**. Do not call the reliability candidate build-verified or accepted until current canonical Engineering Gate and full Android/PWA/browser/APK/package verification both pass. Physical-device review is still required for acceptance.

## Learner-content hygiene

- Whole-corpus serialized JSON/code sanitizer candidate `45f6539fff535fadc6aaa6970894f9ff123422fa` passed Engineering `34738522874` and full run `34738530102` over **2,711 questions / 27,898 learner-facing fields**; raw ED8 source is unchanged.
- User preview review found residual OCR debris in Physiology Ch5/Ch7; verified follow-up `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3` added source-fingerprinted stable-ID display overrides for those two chapters. Engineering `34740460617` and full run `34740465004` passed; preview `https://c4744474.nk-qbank.pages.dev`; production skipped.
- Do not generalize Ch5/Ch7 cleanliness to unreviewed chapters; use the same source-fingerprinted override workflow for future OCR cleanup.

## Explanation lane

- FULLY_VERIFIED history: Anatomy Ch6 Q1–Q7 is canonical at certified checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1`; Physiology Ch11 Q1–Q6 is reconciled history at `e01cc0b9a8e62885d29b0c2e7ac6417ce8c96f05`.
- CURRENT_UNVERIFIED owner: Anatomy batch `anatomy-20260913-ch6-q8-q18-r2`, scope `marrow__ANAT_CH06_Q008..Q018`, 11 questions, workload 16.5; no Q19+ work started.
- Fresh transplant branch was based on exact canonical `e01cc0b9a8e62885d29b0c2e7ac6417ce8c96f05`; candidate `9b625f6a881482e43429d97f817128ec917bbfe2` passed Engineering `34744191423` and full run `34744283759`; canonical merge is `420928ae4e1314cb3a23c8687801be5c7b1f0a8c`.
- Inventory: **605 enhanced / 2,106 pending / 2,711 total**, fingerprint `995717a6ac450e2b6a530e0521d58a43e67d4e980401989c69b544c38de98300`; raw source hashes unchanged.
- Keep the explanation lane owned until the current canonical head is dual-green; then move Q8–Q18 to FULLY_VERIFIED_HISTORY, release the lane, and stop without starting Q19+ in the same run.
- Production promotion prohibited.

## Image lane

- Automated Biochemistry image integration is paused. Ch4 Q11 remains `REVIEW_REQUIRED`; two recovery attempts failed before shared registry/progress mutation because embedded PDF text was corrupted. No verified Q11 learner-facing result exists.
- Verified manual Physiology Batch 01 product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` is canonical; Engineering `34699015727` and full run `34699016754` passed; production skipped.
- Batch 02 on historical branch `manual/marrow-physiology-fastlane-20260912-b02` is unverified evidence only: 40 refs audited, 14 metadata-invalid, 12 new assets, 14 specialist deferrals; targeted run `34704088880` failed canonical wiring and was never reconciled.
- Canonical Physiology coverage remains 294 raw / 290 effective / 44 released / 4 invalid metadata / 48 resolved / 21 tracked-unreleased / 225 untracked / 28 text-cue. Next canonical reference: `marrow__PHYS_CH03_Q007:figure:1`.

## Anti-fragmentation rules

- Explanation and image work build from `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Re-read canonical `STATE.md`, live commit, inventory/registry fingerprints and current ownership before editing.
- A stale PR/branch is historical evidence, not a lock or merge target; transplant only stable-ID/content-scoped work after ownership and duplicate checks.
- Reconcile verified work into canonical before starting another conflicting batch in the same lane.
- Accepted product/UI fixes are protected canonical behavior for subsequent content/image/explanation work.

## Known problems / cautions

- Reliability candidate is not build-verified yet because both first exact-head workflows stopped at the memory-length gate before product tests.
- Anatomy Ch6 Q8–Q18 is reconciled but remains CURRENT_UNVERIFIED until current-head canonical Engineering + full build are green.
- Physiology image coverage remains incomplete; Biochemistry Q11 remains unresolved/paused.
- Four PrepLadder source records remain intentionally non-answerable rather than recording corrupt attempts: `anatomy-22-4`, `physiology-23-38`, `physiology-24-6`, `physiology-33-33`.
- Production promotion remains prohibited unless explicitly requested.

## Current priorities / Next step

1. **Reliability candidate:** rerun current canonical Engineering Gate and full Android/PWA/browser/APK/package pipeline after this memory-size repair. If a later stage fails, fix that actual product/test failure and rerun exact-head verification.
2. **Explanation lane:** after current canonical is dual-green, mark Anatomy Q8–Q18 FULLY_VERIFIED and release the lane; do not start Q19+ in the same verification run.
3. **Physical review:** inspect the generated matching-table/question presentation on device before accepting the reliability candidate.
4. **Image lane:** resume from live canonical after fresh ownership/fingerprint checks; keep automated Biochemistry paused at Q11.
5. Production promotion remains prohibited unless the user explicitly asks for it.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- Chronological work/CI history: `.project-memory/SESSION_LOG.md`.
- Accepted Practice handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
