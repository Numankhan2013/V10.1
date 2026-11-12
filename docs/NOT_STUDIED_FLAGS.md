# "Not studied yet" flag

Owner request, 2026-11-12. Module `app/src/main/modules/not_studied_flags.js`
(`NK_NOT_STUDIED_V1`), styles `/* ── nk-not-studied-v1 ── */` at the end of
`app.css`.

## What the learner sees

- **Session header** (Practice, custom/topic practice, FSRS/revision practice,
  timed CBT/mocks/topic tests): a flag button beside the bookmark. Off = outline
  flag; on = amber filled flag on a pale amber tile. A toast confirms each tap.
  Review Solutions has no flag. The fixed footer stays Previous + Next.
- **Session review sheet / question navigator**: flagged cells get a small amber
  corner flag and "Not studied" label; the legend gains "Not studied".
- **Topics list**: a topic with flagged questions shows an amber flag badge with
  the count on its second line.
- **Topic page**: the question grid (colours from earlier answers, amber
  skipped, blank unattempted) adds a corner flag to flagged cells; tapping a cell
  still opens that one question (`practiceOne`). The legend counts "N not
  studied" and the options list gains **Practice flagged (N)**, which starts a
  Practice session of every flagged question in the topic.

## What a flag does

A flagged question is outside everything that measures learning:

- no attempt is recorded (`nkFsrsRecordAttempt`/`recordAttempt` refuse it), so
  no FSRS card is created or updated, and accuracy, Insights, coverage, weak
  areas and study-time-from-attempts never see it;
- it is never submitted-as-skipped (`nkMarkSkippedFromSession` leaves it out);
- when a session or test is saved, its result drops the flagged questions
  (`questionIds`, `answers`, `questionTimes`, `markedForReview`, `expired`) and
  recomputes correct/incorrect/attempted/unattempted/total (and practice time),
  so score, test stats, CBT/topic analysis and mock insights skip them. The
  result keeps `notStudiedIds` (also the "already handled" marker; results
  older than 10 minutes or already marked are never rewritten). A test whose
  every question is flagged saves no result and returns to its origin page.

Unflagged skipped questions behave exactly as before (they enter FSRS as
skipped under the existing rule).

## When a flag clears

One rule for Practice and timed tests:

- A flag set **before** the current session started clears the moment the
  question is answered (Practice: on submit of the answer; timed test: on
  choosing an option, and at submission as a backstop). That answer then enters
  FSRS and stats normally.
- A flag set **during** the session stays even if the question is answered, and
  that answer is withheld. In Practice (answers are recorded immediately)
  flagging an answered question withdraws this session's attempts with the
  existing FSRS undo events (`isUndo`, `reason:'not-studied'`) and replays the
  card; an uncommitted recall rating is dropped. Unflagging in the same session
  gives the answer back (a miss is recorded, a correct answer waits for its
  recall rating).

## Storage and sync

`state.notStudied[qid] = {on:true, at, updatedAt}`; clearing keeps a tombstone
`{on:false, updatedAt}`. `cross_device_sync.js` syncs kind `notStudied`, one
document per question per device (`users/{uid}/notStudied/{device}--{qid}`,
covered by the existing owner-only rule), merged per question: newest
`updatedAt` wins, a tie resolves to cleared. Account reset tombstones the kind
like every other synced kind.

## Tests

- `tools/test_not_studied_flags_v1.py`: real FSRS module + the page's own
  submit/skip functions; flag/withdraw/restore, lifecycle rule, result
  sanitizing, all-flagged test, merge rules, two-device sync, topic markup.
- `tools/verify_not_studied_browser.py`: app stylesheet at 390 px and desktop,
  light/dark: header placement and target size, footer untouched, corner flag
  inside cells, badge inside rows, Practice flagged action.

Not device-verified.
