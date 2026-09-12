# Practice flow postmortem — 2026-09-12

Status: **device/user-verified and accepted** on the canonical integration lineage.

This document records the complete Practice-flow incident, the accepted behavior, what went wrong during implementation and verification, the lessons that must survive future agent handoffs, and the regression contract that must not be weakened.

## Canonical result

Canonical branch: `feature/marrow-canonical-full-current`.

Accepted lineage at the time of user verification:

- PR #45 — `Fix durable Continue Practice pause and resume`.
- PR #47 — `Fix Practice flow: one final review grid, no footer Pause/Submit`.
- PR #48 — `Fix Continue Practice restoring only one question`.
- PR #51 — `Fix Home Continue Practice to resume full paused session`.
- PR #53 — `Verify the real Home Continue Practice path`.
- Canonical commit after PR #53: `74abb670c3ae088e06653681e85c347212222455`.
- Full Android/PWA build run `34695680534` completed successfully on that exact canonical SHA.
- After that build, the user physically exercised the flow and reported: **“Peak! It works.”** This is the acceptance signal for the behavior below. CI alone did not establish device acceptance.

## Final accepted learner behavior

Normal Practice question screen:

- Footer contains exactly `Previous` and `Next`.
- There is no Pause button on the question screen.
- There is no Submit button on the question screen.
- The FSRS/explanation area must not lose space to redundant session controls.

Session review entry:

- The header grid icon goes directly to the existing final review grid.
- Reaching the end of the Practice session uses that same final review grid.
- The old intermediate `Question Navigator` / `Review or Finish Session` layer must not appear for normal Practice.

Final Practice review grid:

- Keep the close `X`.
- Keep tappable question cells so the learner can jump back to any question.
- Bottom action area contains exactly two actions: `Pause` and `Submit`.
- Do not show `Back to question`.
- Do not show `Review unanswered`.

Pause semantics:

- Pause preserves the existing active Practice session rather than creating a new session.
- Preserve the canonical full ordered question list in `sessionQuestionIds`.
- Preserve the full visible `questionIds` list when resuming.
- Preserve answered/submitted progress, timing state, the saved position, and the same session identity.
- Pausing while an unanswered question is open is **not** the same as skipping that question; do not mark it skipped merely because the learner paused.

Continue Practice semantics:

- Resuming a paused Practice session restores the complete original session, not only unanswered/unseen questions.
- Already answered questions remain in the session and remain visibly answered; they are not removed from the test denominator.
- Restore the saved/current question index inside the full original session.
- If an older buggy client persisted `questionIds` as only one current question but still preserved the canonical full `sessionQuestionIds`, rebuild the visible session from `sessionQuestionIds` and restore the saved position.
- A genuine finished topic can still route to the next canonical topic through the existing continuation logic.

Scope exclusions:

- Wrong Questions, Bookmarks, FSRS review, Review/Test review, CBT, and Custom Study Modules remain outside this normal-Practice override unless a later explicitly approved design changes that contract.

## What went wrong

### 1. The first implementation solved the wrong UX

PR #45 added direct Pause and Submit controls to the question footer. That technically exposed session actions but violated the intended interaction model and stole vertical space from the explanation/FSRS area. The user explicitly rejected that layout.

Lesson: a technically functional control is still wrong if its placement breaks the approved screen hierarchy. Preserve the user-approved information architecture, not merely feature availability.

### 2. A redundant review layer was left in the path

The existing grid icon could still lead through an intermediate `Question Navigator` / `Review or Finish Session` surface before the real final grid. The user wanted one review surface, not two.

PR #47 corrected this by making normal Practice converge on the single existing final review grid and moving Pause/Submit there.

Lesson: do not create or preserve extra confirmation/navigation layers when the product already has a suitable canonical surface. One learner action should map to one obvious surface.

### 3. Resume semantics incorrectly treated “continue” as “show only remaining questions”

The initial durable-resume logic rebuilt `questionIds` from skipped/unseen/unsubmitted items. After four answers in a twenty-question session it could reopen as sixteen questions; near the end it could reopen as `1 / 1`. That changed the identity of the test and caused the exact user-visible regression.

PR #48 fixed the real state bug:

- `sessionQuestionIds` is the canonical original ordered session.
- resume restores the full canonical session into `questionIds`;
- the saved/current item is mapped back to its index in that full session;
- answered/submitted state stays attached rather than being removed from the visible test;
- persisted one-question state can be repaired from `sessionQuestionIds`.

Lesson: **Pause means suspend the same test; it does not mean generate a new test from the remainder.** The denominator and navigation history are part of session identity.

### 4. Pause incorrectly marked the open question as skipped

The earlier implementation called the skip-marking path while pausing. That conflated a session lifecycle action with an answer/review event and could contaminate FSRS/review eligibility.

PR #48 removed that behavior.

Lesson: lifecycle transitions must not invent learning events. A learner who pauses on a question has not answered or skipped it.

### 5. Verification was initially too synthetic

The first regression coverage directly manipulated functions/state and even constructed a fake twenty-question list after starting a one-question Practice surface. That could prove internal helpers behaved under a manufactured state while still missing the actual rendered learner path.

Lesson: state/unit tests are necessary but not sufficient for UI lifecycle bugs. Browser tests must start a genuine multi-question Practice session and exercise the same visible controls the learner uses.

### 6. We declared the fix too early

After PR #47, CI was green and the UI contract looked correct, but the user’s real screenshot still showed `1 / 1`. Calling the issue fixed before reproducing the complete Pause → Home → Continue lifecycle was premature.

Lesson: do not equate “CI green” with “the reported behavior is fixed.” For a user-reported runtime/UI bug, verification must cover the exact reported sequence and device acceptance must remain a separate status.

### 7. We made an incorrect assumption about the active Home handler

PR #51 was based on the assumption that the current visible Home Continue control called legacy `continuePractice()`. A legacy path did exist and was defensively routed through the durable continuation logic, but the approved Home command-center actually renders `.nk-home-focus-action` and calls `window.QB.nkContinueRecentPractice()`.

PR #53 corrected the browser test to click the actual rendered current control and assert its handler before testing the lifecycle.

Lesson: never infer the live UI entry point from an old function name, stale design layer, or superseded selector. Inspect the final generated DOM/runtime after all transforms and click the real element.

### 8. The test itself briefly encoded the wrong selector

The first “real Home button” Playwright revision targeted `.nk-home-v4-action-continue`, a superseded layer. This exposed a second-order verification mistake: a browser test can still be wrong if it targets a historical UI element rather than the post-transform product.

Lesson: regression tests must verify both the selector and the expected current handler. If the app has layered transforms, test the generated artifact after all transforms, not an earlier source-layer mental model.

## Durable technical rules

1. `sessionQuestionIds` is the authoritative original ordered Practice-session membership for normal Practice pause/resume.
2. `questionIds` on resume should be restored to that canonical full sequence, not filtered down to remaining questions.
3. `pausedIndex` plus current-ID mapping restores position. Prefer current-ID mapping when valid; use the saved index as repair fallback.
4. `submitted`/answers/timing stay attached to the same session object.
5. Pause changes lifecycle to `paused`; Continue changes it back to `active`; Submit/finish owns completion/history.
6. Pause itself does not call skip/FSRS eligibility mutation.
7. If all questions are already submitted when a paused session resumes, return to the Practice route and open the final review sheet rather than silently creating another test.
8. Normal Practice overrides must not leak into Wrong/Bookmarks, FSRS, Review, CBT, or Custom Study Modules.
9. The final review grid owns Pause/Submit. The question footer owns Previous/Next.
10. The normal-Practice grid icon must bypass the redundant legacy navigator and open the final review sheet directly.

## Required regression path

Future changes touching Practice navigation, Home, session persistence, FSRS, final review, build transforms, or `window.QB` exports must preserve this exact end-to-end scenario:

1. Start a genuine multi-question Practice session using the product path (the current automated regression uses `startAllPractice()`).
2. Confirm the session has more than one real question.
3. Move to a later question and mark earlier questions submitted.
4. Open the final Practice review grid.
5. Confirm its action area is exactly `Pause`, `Submit`; no `Back to question`; no `Review unanswered`; question cells remain available.
6. Pause through the rendered review-grid button.
7. Confirm the same active-session ID remains, lifecycle becomes `paused`, full `questionIds` and `sessionQuestionIds` are preserved, and the saved index is preserved.
8. From Home, click the actual current rendered Continue Practice control (`button.nk-home-focus-action` at the time of this incident) and verify its current handler is the durable continuation path.
9. Confirm the same session ID resumes, the full original question list is restored, the current question/index is restored, and previously submitted answers remain submitted.
10. Repeat after intentionally simulating legacy corruption where `questionIds` contains only the current item while `sessionQuestionIds` still contains the full session; Continue must repair the session.
11. Run this against the generated PWA artifact at mobile widths, not only against isolated helper functions.

If the Home UI is redesigned later, update the selector only after inspecting the generated DOM; preserve the behavioral assertions.

## Things not to do

- Do not put Pause/Submit back on the normal Practice question footer.
- Do not reintroduce the intermediate normal-Practice Question Navigator.
- Do not reduce a paused session to unanswered/unseen questions.
- Do not treat Pause as Skip.
- Do not create a new session when resuming an existing paused one.
- Do not use a one-question `practiceOne()` fixture as proof that a multi-question Pause/Continue lifecycle works.
- Do not mutate a fake question list in browser tests and call that end-to-end verification.
- Do not rely on stale selectors or old Home layers.
- Do not claim device/user verification from CI, screenshots generated in CI, or source inspection.
- Do not promote production merely because the canonical preview/build is green; production promotion still requires explicit approval.
- Do not let unrelated explanation/image automation rewrite this Practice lifecycle unless its exact-head branch contains the canonical fixes and the regression suite stays green.

## What to do next

There is no open functional bug in this Practice flow after the user’s physical acceptance. Treat it as protected behavior.

For future work:

- Keep `tools/test_continue_practice_resume_v1.py` and `tools/verify_continue_practice_browser.py` as regression owners.
- Keep `tools/practice_single_review_grid_core.js` as the normal-Practice UI convergence layer unless intentionally refactored with equivalent tests.
- When Home is redesigned, update the browser test to the new real rendered control and assert the handler before clicking it.
- Before merging any change touching session lifecycle or Home continuation, run exact-head Engineering Gate plus the full generated Android/PWA/browser/package workflow.
- Use the canonical branch as the integration base for image/explanation automations; stale donor branches are evidence only.
- Preserve the distinction between `build-verified`, `browser-verified`, `device-verified`, and `accepted` in memory.
- Production remains a separate explicit-release decision.

## Acceptance statement

As of 2026-09-12, the user physically confirmed the corrected Practice flow works. The accepted contract is therefore the combination of the canonical code through commit `74abb670c3ae088e06653681e85c347212222455`, successful full build run `34695680534`, and the user’s subsequent device verification. Any future behavior that returns to `1 / 1`, moves Pause/Submit back onto the question screen, reintroduces the redundant navigator, or loses the full paused session is a regression.
