# Logic and FSRS audit (2026-10-08)

Branch `feature/home-geist-polish-20261008`. Method: read the shipped runtime
(the deployed build's app script, ~620 KB of code) and drove it through a
private in-closure probe with seeded state, plus the scheduler itself
(`ts-fsrs` 5.4.2, the app's exact parameters). Every fix lives in its source
owner (`tools/*_core.js`, `tools/apply_*.py`, source `index.html`, `redesign/`).

## FSRS — is it as good as Anki?

The architecture is sound and close to Anki:

- **FSRS-6 scheduling:** the pinned ts-fsrs implements FSRS-6.
- **History is the source of truth:** immutable attempts are replayed into cards after every sync pull, so devices cannot drift.
- **Answer semantics:** wrong answers record Again; correct ones default to Good, with Hard or Easy available and amendable.
- **Pause/submit eligibility:** pausing commits answered work only; submission marks unanswered questions skipped.
- **Daily cap:** limits distinct review cards per day; learning repeats are exempt.
- **Consistency:** Home, Revision, the FSRS page and Insights all agreed on counts.

Gaps versus Anki, now fixed:

| Problem (verified in runtime) | Fix |
|---|---|
| Never-answered *skipped* questions have retrievability 0, so they sorted ahead of genuinely overdue reviews (a 100-question CBT with 60 skips put 60 blanks first). | Queue order: learning steps (by due) → reviews (lowest retrievability first) → never-answered skips last. |
| Review cards became due at the exact minute (a card due 23:00 was not offered at 16:00). | `nkFsrsIsDue`: review cards are due for their whole local day. One rule shared by every surface. |
| No learn-ahead: a 10-minute relearning step could not be studied for 10 minutes. | 20-minute learn-ahead for learning/relearning cards (Anki default). |
| Fuzz disabled, so cards answered together got identical intervals and reviews piled onto the same days. | Fuzz enabled. ts-fsrs seeds it from review time + reps + D×S, so replay is still identical on every device (tested). |
| A skipped *unanswerable* question (34 incomplete-source records) became "due" forever, with no card, at the top of every review session. | Unanswerable questions are never review-eligible, never marked skipped. |
| Hard/Good/Easy showed intervals only in a hover tooltip (invisible on phones). | Each button shows its interval (e.g. Hard 15m · Good 2d · Easy 7d). |

Kept as deliberate design (changing them touches contracts or sync):

- **No in-session re-queue of lapses.** Durable checkpoints hash their membership. Learn-ahead makes a lapse available again right after the session.
- **No Again for a correct answer.** Rating revisions are limited to Hard/Good/Easy everywhere, sync included. Use Hard for a guess.
- **Ordinary practice counts as review.** "FSRS schedules every answered question."
- **No separate new-card limit.** FSRS stays review-only, as pinned by tests.
- **No per-user parameter optimisation yet.** This is on the roadmap.

## App-wide bugs found and fixed

1. **Continue Practice loop.** When the only unanswered question in a topic was unanswerable, Home kept offering "Practice remaining questions" for it forever and never advanced to the next topic. Remaining work now excludes unanswerable questions.
2. **Topic completion stuck below 100%.** Topics containing gated questions showed 13/14 "in progress" forever. Completion now counts answerable questions only.
3. **Topic accuracy dropped after Undo.** `chapterStats` counted undo events as incorrect answers. It now counts active answers only.
4. **Undo kept streaks alive.** Undo events counted as study days. The streak now uses active answers, matching Insights.
5. **Home progress counted undone answers.** Home progress, the Profile lifetime figures and the Home delta chips now exclude them.
6. **Unseen served unanswerable questions.** These are now excluded from Unseen.
7. **Legacy per-subject lists were still reachable.** The Profile shortcuts and old `#wrong`/`#bookmarks`/`#review` links opened outdated lists. Those lists covered the current subject only, counted resolved misses as still wrong, and used a timestamp due rule. They now open the all-bank Revision views.

8. **Skips seeded FSRS with questions never reached (found on follow-up).** Submitting a Practice session, a timed test or a study module marked *every* unanswered question as skipped, so answering 5 of 20 queued 15 untouched questions, and answering none queued all 20. The module review sheet's *Save & exit* did the same and also left the module un-saved. New shared **skip rule** (`nkMarkSkippedFromSession`, used by Practice Submit, timed-test Submit, Finish revision and Finish module): a question enters FSRS as skipped only if it comes *before your last answered question*. In a 20-question session where you answer 1, 3, 4 and 5, only question 2 enters; 6-20 stay unseen; answering none adds nothing. Also counted as skipped: an unanswered question you spent 15 s or more on (tried, could not answer), even at the end of a module. A quick glance does not count. Pause and *Save & exit* (now correctly keeps an unfinished module open) add nothing. Questions that already have history are untouched. Verified in the real app for Practice, Unseen, Bookmarks, Mistakes, timed tests and modules (`tools/test_study_module_fsrs_v1.py` covers the rule).
9. **Insights bank/subject filters ignored each other.** Choosing the UWorld bank still offered PrepLadder/Marrow subjects, and picking a subject cleared the bank. Each filter now only offers what the other contains (UWorld lists its collections only; Anatomy offers PrepLadder and Marrow only); a selection that becomes invalid is cleared.
10. **Skipped had no consistent colour.** Insights showed skipped questions in neutral grey (and lilac in the legacy theme) while Test analysis used amber. Amber is now the single skipped colour in both.
11. **Answered cells in the answer grid were nearly identical to unanswered ones** (`#fafafa` vs white). Answered cells now have a tinted fill, stronger border and a check badge (review sheet and question navigator, light and dark) while text stays fully legible.

## Verified correct (no change)

- **Sync:** merge and rebuild of reviews from attempts.
- **CBT:** recording (Again/Good, unanswered marked skipped) and global-timer expiry while away (auto-submits, time capped).
- **Practice:** pause, resume and finish keep the session ID, order, answers and skip marking.
- **Correct my misses:** resolves mistakes.
- **Due review sessions:** answers are tagged `fsrs-review` for the daily cap.
- **Study modules:** progress, exit/resume, finish early and restart (history kept).
- **Counts:** consistent across Home, Revision, the FSRS page and Insights.

## Verification

- `tools/test_fsrs_v1.py` covers the new behaviour: whole-day due, a bounded learn-ahead, skipped-last ordering, the unanswerable exclusion and fuzz determinism. All existing assertions still pass.
- `python3 tools/verify_local.py`: 108 checks pass.
- I re-ran the runtime scenarios against the deployed build with the new source blocks spliced in. All passed with zero page errors.
- Full CI on this commit and physical-device review are still pending.
