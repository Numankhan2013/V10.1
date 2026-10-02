# Interaction quality pass — 2026-10-02

The user authorized recovering the previously excluded tap-latency candidate
and implementing restrained native-like interaction polish without changing
the app's layout, palette, navigation or study behavior.

## Audit and recovered work

The September 30 promotion explicitly excluded `b143242` and follow-ups.
The recovered performance changes index immutable bank questions by topic,
remove a redundant state clone/checkpoint normalization during durable saves,
and update timed-test answer selection after persistence without rebuilding
the question. Recovery preserves current source-answerability guards, rating
amendments, saved mocks, checkpoint recovery and failed-save rollback.

The phone/tablet baseline rebuilt the question for every CBT answer. Twelve
rapid changes measured about 12.4–12.5 ms median in local Chromium. The first
refined runs measured 3.6–4.2 ms across 320/390/820/1194px. These are local
browser measurements, not physical-device latency claims.

## Interaction system

- Immediate pointer-down press states for buttons, cards, links, answer options,
  navigation and disclosure controls. Pointer cancellation or a scrolling
  gesture releases the press; actions still use their existing click handlers.
- Short release transitions and 120–140 ms content/sheet movement. No animation
  gates navigation or saving. Reduced-motion users receive static feedback.
- Bookmark, CBT answer, FSRS grade and exam-review-mark edits update in place
  only after a successful durable commit. Question/source DOM, scroll position
  and rating controls remain mounted. A failed commit publishes neither the
  changed state nor success haptics.
- Same-question renders retain open explanations and scrolling; a different
  question starts at the top. Remove the duplicate legacy hash-route render.
- Sheets contain background scrolling and keyboard focus; closing restores
  the opener when it still exists. Existing Pause/Submit/dismissal behavior
  remains authoritative.
- Intentional feedback for committed answer outcomes, CBT selections, recall
  ratings, bookmarks/marks, Pause and completion. Ordinary navigation is silent;
  Practice emits one outcome rather than selection plus outcome vibrations.
- Android uses a deterministic bridge installed after Activity regeneration,
  honoring the user's touch feedback setting. Browser vibration is optional;
  unsupported platforms retain the visual states. No sound is added.

Owners: `question_interaction_core.js`, `apply_interaction_polish_v1.py`,
`interaction_polish_core.js`, `interaction_polish.css`, and
`apply_android_haptics_v1.py`. The final interaction owner follows result
analysis, before final syntax/package checks.

## Verification and remaining certification

The first actual-use pass and second refinement covered press cancellation,
correct answer → editable FSRS → next, bookmark/mark state, modal focus/scroll,
rapid CBT selections, reduced motion, failed writes and reload. Generated
browser regressions cover multi-chapter Pause/Home Continue, correction/rating
replay, study journey, results, named mocks and original-result preservation.

Local source tests and disposable-preview checks do not certify the APK.
Full exact-candidate Ubuntu generation/browser/PWA/package and Android phone/
tablet CI remain mandatory before main/production promotion. Physical haptic
feel and installation/data-preservation acceptance remain separate.
