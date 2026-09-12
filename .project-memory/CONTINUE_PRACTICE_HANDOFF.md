# Continue Practice Handoff — Accepted 2026-09-12

This file is the authoritative product handoff for the accepted Practice pause/resume flow. It supersedes the older 16-of-20 / remaining-only resume model and any earlier one-question fallback description.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- Sole Marrow/product integration trunk: `feature/marrow-canonical-full-current`.
- Accepted Practice implementation is on canonical after PRs #47, #48, #51 and #53.
- Canonical checkpoint that received the real generated-Home verification: `74abb670c3ae088e06653681e85c347212222455`.
- Full Android/PWA/browser/APK/package/preview workflow `34695680534` completed successfully on that checkpoint.
- The user then physically tested the resulting build and confirmed that Continue Practice works.
- Production / `main` remains guarded and must not be promoted without explicit user approval.

## Accepted UI contract

Normal Practice question screen:

- Footer contains only **Previous** and **Next**.
- Do not add Pause or Submit to the question footer.
- The explanation/FSRS area must remain unobstructed.

Question-grid / end-of-session flow:

- The header grid icon opens the single final review grid directly.
- Reaching the end of the session converges on the same final review grid.
- Do not restore the redundant intermediate Question Navigator.
- The final review grid retains its close control and tappable question cells.
- Its action area contains exactly **Pause** and **Submit**.
- Do not restore **Back to question** or **Review unanswered** buttons there.

## Accepted Pause semantics

Pause means suspend the current Practice session without changing what has been completed.

When Pause is pressed:

- preserve the same `activeSession` identity;
- preserve the complete original ordered question set in `sessionQuestionIds`;
- preserve the current/saved index;
- preserve answers, submitted state, timing and progress;
- set the session lifecycle to paused;
- return to Home/dashboard;
- do **not** mark the current unanswered question as skipped merely because the learner paused;
- do **not** shrink `questionIds` to only unanswered/skipped questions;
- do **not** create a new session.

Pause is not Submit, Skip, completion, or a new-test boundary.

## Accepted Continue Practice semantics

The Home **Continue Practice** control must resume the same paused Practice session.

On resume:

- keep the same session ID;
- restore the complete original test/question list from canonical `sessionQuestionIds`;
- restore the saved question position;
- preserve questions already answered and their submitted/progress state;
- unanswered questions remain unanswered and available in normal navigation;
- if a buggy older persisted client reduced `questionIds` to one current question while `sessionQuestionIds` survived, rebuild the full visible session from `sessionQuestionIds`;
- never collapse the resumed session to `1 / 1`;
- never call a legacy one-question `startSession([q.id], ...)` fallback when a paused session exists.

The visible resumed session is therefore the original complete test, not a filtered remaining-only test.

## Critical regression history

The sequence matters because future agents must not repeat it.

1. PR #45 added visible Pause/Submit controls to the question footer and used a remaining-only resume model. This conflicted with the desired UI and session architecture.
2. PR #47 restored the accepted UI: Previous/Next-only question footer, one final review grid, Pause/Submit-only actions.
3. PR #48 fixed the core state model so resume restores the full original session, saved index and progress, and Pause no longer marks the current item skipped.
4. The first verification still missed the real Home lifecycle and the user observed a `1 / 1` resumed session on-device.
5. PR #51 traced that failure to the Home continuation path and added a real multi-question Pause → Home → Continue regression.
6. PR #53 corrected the browser verifier again so it exercises the actual generated Home Continue Practice control rather than a superseded selector/path.
7. Full CI passed and the user physically confirmed the feature now works.

Detailed failure analysis, wrong assumptions, lessons and permanent do/don't rules are in `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.

## What was done wrong

- Treating Pause as equivalent to Skip.
- Filtering the active visible session down to only remaining questions on resume.
- Adding Pause/Submit controls to the normal question footer and stealing explanation/FSRS space.
- Leaving a redundant intermediate navigator in front of the final review grid.
- Verifying an internal helper instead of the exact visible Home control.
- Simulating session data in tests without first exercising a genuine multi-question Practice session.
- Assuming a selector/handler was the current generated learner path without inspecting the generated app.
- Declaring the bug fixed before physical verification even though the visible `1 / 1` symptom remained.

## Permanent lessons / do-not-regress rules

- Test the complete learner path: start genuine multi-question Practice → answer some questions → open final review grid → Pause → Home → click the actual rendered Continue Practice control → verify same session ID, full original IDs, same saved index/current question and preserved submitted progress.
- Browser tests must interact with the actual generated UI element the learner sees, not only exported helpers.
- `sessionQuestionIds` is the durable canonical identity/order of the paused Practice test.
- `questionIds` must be repaired from `sessionQuestionIds` if an older bad state collapsed it.
- Pause must never mutate answer correctness or FSRS eligibility merely because the learner exits temporarily.
- UI and state behavior must be verified independently: a correct-looking final grid does not prove correct resume behavior.
- CI/browser success is not the same as user/device acceptance. Use explicit status labels.
- No Marrow-only or subject-specific Practice engine may be introduced; this remains shared Practice/session architecture.
- Do not restore legacy one-question continuation behavior.
- Do not promote production without explicit user approval.

## Required regression contract

A future change touching Home, Practice, session persistence, sync, question navigation, final review, FSRS injection or build transforms must preserve all of the following:

- normal question footer = Previous + Next only;
- final review action area = Pause + Submit only;
- grid icon/end boundary = same final review grid;
- Pause preserves same full session and saved position;
- Home Continue restores same session ID and complete original question set;
- submitted answers remain submitted;
- current unanswered question is not auto-skipped by Pause;
- previously collapsed one-question persisted state is repaired from `sessionQuestionIds`;
- special modes (CBT, Review, Wrong/Bookmarks, FSRS, Custom Study Modules) remain outside this override unless explicitly redesigned.

## Current status

**Accepted / user-device verified.** Do not describe this flow as pending. Future work may build on it, but must preserve the contract above and the postmortem lessons.
