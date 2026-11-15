# Submit attempted (normal Practice)

Owner request 2026-11-15, branch `feature/review-quiet-finish`. Module
`app/src/main/modules/practice_submit_attempted.js`, styles `nk-submit-attempted-v1`.

- **Where:** the Practice session sheet (header grid icon) shows **Submit attempted**
  under Pause / Submit, with "Questions 1–N · K skipped · M left for later". It shows
  only in normal topic Practice (`nkPracticeResumeEligible`), when at least one
  question is answered and at least one comes after the last answer.
- **The cut:** the result covers questions 1..last answered (answered = checked:
  `answers` and `submitted`). A blank question before that point is **Skipped**:
  scored as today (not wrong), and FSRS treats it by the existing skip rule
  (`nkMarkSkippedFromSession`). A not-studied flag keeps its own rules.
- **Left out:** the questions after the last answer are not in the result, not
  marked skipped (even after 15 s on screen), not in FSRS, and their time is not
  counted. A choice picked but never checked counts as not answered.
- **Mechanics:** the live session is trimmed to the cut (`questionIds`,
  `sessionQuestionIds`, answers/submitted/times/pending ratings) and ends through the
  normal `finishPracticeSession` chain, so not-studied settling, the submitted
  checkpoint and integrity guards run as before. The test record gets
  `partial:true`, `sessionTotal`, `skipped`, and `practiceContext.remainingIds`
  (`completed:false`). A refused finish restores the whole session.
- **Result page:** a note "Questions 1–N of T · M left for later · not counted";
  blank questions read "Skipped" instead of "Omitted / Not answered".
- **Topic page:** when the topic's latest Practice result is partial with questions
  left (and no paused session), "Continue where you left off · From question N of T ·
  M left" starts those questions; the main button reads "Practice entire topic".
  Every other topic option (timed test, redo mistakes, only unanswered, saved) is
  unchanged.
- **Grid language** (session sheet, topic map, result strip): correct = solid green,
  wrong = solid red, skipped = hollow yellow outline, not attempted = hollow neutral
  outline; the not-studied flag mark is unchanged.

Tests: `tools/verify_submit_attempted_browser.py` (390/1280, light/dark).
