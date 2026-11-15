# "Not studied yet" flag

Owner request, 2026-11-12; hardened 2026-11-13; bug-report fixes 2026-11-14
(branch `fix/not-studied-flag-bugs`, see "Fixes 2026-11-14" below). Module
`app/src/main/modules/not_studied_flags.js` (`NK_NOT_STUDIED_V1`), styles
`/* ── nk-not-studied-v1 ── */` in `app.css`, just before the visual refinement
layer (which must stay last).

## What the learner sees

- **Session header** (Practice, custom/topic practice, FSRS/revision practice,
  timed CBT/mocks/topic tests): a flag button beside the bookmark. Off = outline
  flag; on = amber filled flag on a pale amber tile. A toast confirms each tap.
  Review Solutions has no flag. The fixed footer stays Previous + Next. While a
  question is flagged its Rate recall dock is hidden and takes no rating.
- **Session review sheet / question navigator** (Practice and timed tests):
  a flagged cell loses its answered / correct / wrong / skipped look, becomes a
  neutral cell with the amber corner flag and the label "Not studied"; the
  legend gains a flag chip "Not studied" (Practice drops a Correct/Wrong/Skipped
  legend entry that only flagged cells had).
- **After submitting** (practice result, CBT/mock/topic-test analysis): the
  "Question by question" grid keeps every question in its place; a flagged one
  is a neutral cell with the flag glyph (`is-ns`, "Not studied, not scored"),
  never the amber-outline omitted/skipped cell, with a line "N not studied ·
  left out of the score". "Every answer" lists it as **Not studied**. Review
  Solutions includes it in order (explanation available, no answer) and its
  navigator marks it with the corner flag and a "Not studied" legend entry.
- **Topics list**: a topic with flagged questions shows an amber flag badge with
  the count on its second line.
- **Topic page**: the question grid adds the corner flag to flagged cells;
  tapping a cell still opens that one question (`practiceOne`). The legend
  counts "N not studied" and the options gain **Practice flagged (N)**.

## The rules

**R1 — Outside every measure.** While a question is flagged, no answer to it
from the flagging session counts: no FSRS card is created or changed, no due
review, no pending rating commits into a visible card, no accuracy, test or
topic stats, Insights, coverage, weak areas, streak day, attempt count or
Today plan entry. Every one of these reads `nkFsrsActiveAttempts`; the module
wraps it so a flag set in session S hides S's attempts (the flag stores
`session: S`). A flagged question is never submitted-as-skipped, and a flagged
question is not eligible for Today's Review, its counts or forecast, even if an
earlier session left a skip mark or earlier answers (R4; the mark and the
answers are kept, so unflagging restores them).

**R2 — Flag/unflag in the same session is a no-op.** Unflagging in the
session that set the flag gives back exactly what was there: the same
attempt events (same ids, times, ratings, rating revisions), the same card
byte for byte, the same pending recall rating. Nothing is deleted while
flagged: answers are hidden, not undone, and the visible card is the card
without them (the full card is kept aside in local `state.notStudiedHeld`,
never synced). Toggling any number of times leaves the state of the final
flag position, with no accumulated events. Answering, rating and moving on
while flagged record exactly what they would have unflagged, hidden; moving
on commits the default Good like any unrated answer.

**R3 — Flags from elsewhere clear on answering.** A flag set outside the
current session (an earlier session, another device's session, or a legacy
flag without a session that predates this session's start) clears the moment
the question is answered (Practice: submit; timed test: at submission only,
because timed answers are provisional until then). The answers that flag withheld are withdrawn for good with
FSRS undo events (`isUndo`, `reason:'not-studied'`) — the visible card does
not change — and the new answer counts once, normally. Unflagging such a flag
by hand does the same.

**R4 — A flag takes the question out of FSRS entirely (rewritten 2026-11-15,
`feature/review-learning-queue`).** While a question is flagged it is not
review-eligible (`nkFsrsEligibility` returns `''`) whatever its earlier
history: it leaves Today's Review and the due queue, FSRS counts, the forecast,
memory stages and a due review's learning queue (all of them filter on
eligibility; the topic page's due count skips flagged questions too). This
applies whether it was flagged in a due review or any Practice session.
Nothing is deleted while it is flagged: earlier attempts, the card and any skip
mark stay, so **unflagging without answering restores the card exactly as
before** (the flagging session's own answers follow R2/R3 as before). When a
flagged question is **answered again** and its flag clears (R3), the question
starts **fresh** from that answer: every earlier answer, not only the ones the
flag withheld, is withdrawn with the existing undo events (`isUndo`,
`reason:'not-studied'`, synced like any attempt), the card is rebuilt, and the
new answer is the first on an empty card, so a guessed history no longer shapes
scheduling. A refused submit puts the attempts, flag and card back. Unflagging
by hand is not an answer and withdraws only what the flag withheld.
**Saved results are not rewritten**: past practice/test results keep their
scores and accuracy (R6's 10-minute window still applies to the ending
session only); FSRS-derived views, and attempt-based statistics that read
`nkFsrsActiveAttempts` (Insights, coverage, mistakes), no longer count the
withdrawn earlier answers once the question is answered fresh.

**R5 — Ending a session settles it.** When a Practice session is submitted
(and the submission actually saved), discarded from Paused Practice, or
abandoned (a Practice that cannot be paused, such as Today's Review, replaced by
a new session), answers still hidden by its flags get undo events (so app
versions that predate the flag never count them either) and what was kept aside
is dropped. Kept-aside entries whose session is neither live nor paused are
pruned. Timed tests never record a flagged question's answer at all.

**R6 — Results.** A result saved now drops the flagged questions from
`questionIds`, `answers`, `questionTimes`, `markedForReview`, `expired` and
recomputes correct/incorrect/attempted/unattempted/total (and practice time),
so score, accuracy, test stats, CBT/topic analysis and mock insights skip them.
It keeps `notStudiedIds` (also the "already handled" marker),
`allQuestionIds` (full order, for the grids and Review Solutions) and a newer
`updatedAt` so the cleaned copy wins sync. Cleaning happens when the result is
created (the first save of the submitting/finishing session), so no unclean
copy is ever saved or queued for sync; opening a result still cleans one saved
by another path. A question is left out when its flag belongs to this session,
or when it is flagged elsewhere and this session has no counted answer to it, or
when this session's answer was later withdrawn (undo `reason:'not-studied'`).
Results older than 10 minutes or already marked are never rewritten. A session
whose every question is flagged keeps no result: the record becomes a hidden
shell (`noResult:true`, `questionIds:[]`, zero counts, `notStudiedIds`,
`allQuestionIds`, newer `updatedAt`, plus `scheduledMockId`/`makeupFor`) that is
never deleted, so no older copy can come back through sync and a scheduled mock
or make-up still reads as taken; the Tests list, Insights and the mock ticket
skip it, and opening it returns to its origin page. A timed result with flagged
questions also shows "N% counting them" beside "left out of the score".

**R8 — Time is up.** In a timed test a question whose per-question time is
spent, or any question once the test clock has run out, cannot be flagged
(unflagging is still allowed).

**R7 — Pause/resume.** Flags, hidden answers and what was kept aside survive
Pause, reload and Continue Practice; the resume checkpoint is the normal one.
The flag still belongs to that session after resuming.

Unflagged skipped questions behave exactly as before (they enter FSRS as
skipped under the existing rule).

## Storage and sync

`state.notStudied[qid] = {on:true, at, updatedAt, session?}`; clearing keeps a
tombstone `{on:false, updatedAt}`. `cross_device_sync.js` syncs kind
`notStudied`, one document per question per device
(`users/{uid}/notStudied/{device}--{qid}`, owner-only rule), merged per
question: newest `updatedAt` wins, a tie resolves to cleared, an unsafe
session id is dropped. A tombstone that has synced (its payload hash recorded,
nothing in the outbox) moves out of `state.notStudied` into the local-only
`state.notStudiedCleared[qid] = updatedAt`, which the merge and new flags still
honour, so sync capture no longer walks it. A flag arriving from another device hides that
session's answers there too, and an unflag shows them again (the card is
replayed when the hiding changes). `state.notStudiedHeld` stays local.
Account reset tombstones the kind like every other synced kind.

## Scenarios (each is a case in `tools/test_not_studied_flags_v1.py`)

Byte-identical cases compare a run with the flag toggles against the same run
without them: FSRS cards, raw attempt events, rating revisions, skip marks,
due queue and admitted cards, FSRS counts, per-question stats (eligibility,
attempts, correct, open mistake, study days), saved results, session state,
resume checkpoints and the sync payloads of attempts, flags and results.

1. Flag→unflag before answering, then skip = plain skip (byte-identical).
2. Flag→unflag before answering, then answer wrong / correct+Hard = normal.
3. Wrong answer, flag (card gone, no stats, not due, no undo written), unflag = byte-identical.
4. Correct answer waiting for its rating, flag (dock hidden, rating refused), move on (default Good hidden), unflag, rate Hard = the unflagged run; flag/unflag while waiting, then Hard = direct Hard.
5. Correct answer rated Hard, flag, unflag = baseline.
6. Rating revised Good→Easy, flag, unflag = baseline.
7. 26 toggles ending unflagged = never flagged.
8. 25 toggles ending flagged = one flag (one settling undo event).
9. 10 toggles on a pending correct answer = one rating.
10. Flag, answer while flagged (hidden), unflag = baseline.
11. Flag, correct answer while flagged, unflag, move on = baseline.
12. Flag, answer, finish: withheld, settled with an undo, result/checkpoint clean.
13. Earlier FSRS card, answered and flagged now: the card is kept byte for byte, but the question is out of FSRS (not eligible, never due) while flagged, also after the session; flag/unflag = baseline.
14–15. Flag from an earlier session (finished or abandoned), answered later: flag clears (tombstone syncs), earlier answer withdrawn once, card = a single later answer.
16. Re-flagged in that later practice: stays flagged, both answers excluded.
17. Unflag an earlier session's flag during a later session, then answer: counts normally, old answer stays out.
18. "Practice flagged (N)" (and all-flagged session saves no result).
19. Answer, flag, pause, reload, resume, unflag, rate = baseline.
20. Flag before pause, answer after resume while flagged, unflag = baseline.
21. Flag kept through pause: excluded from the result.
22. Due-review session: flag takes the question out of the due queue and FSRS counts (card kept); unflag in the session puts it back; flag/unflag = baseline.
23. Timed test: flag answered + unanswered, submit: nothing recorded, no skip card, counts recomputed.
24. Timed test: flag→unflag = never flagged.
25. Timed test: change answer after flagging: excluded.
26. Timed test: earlier flag clears at submission; changed answer counts once.
27. Timed test: earlier card untouched by a flagged answer.
28. Timed test: all flagged saves no result.
29. Result grid / Every answer / Review Solutions show flagged questions in place as Not studied.
30. Older results never rewritten; cleaned result is newer.
31. Topic list badge, topic grid, Practice flagged, header button rules.
R4 2026-11-15 (one case each): earlier guessed answer, flagged later without
answering, unflagged by hand = card, due queue, counts and statistics exactly
as never flagged, nothing withdrawn; flagged question answered later starts
fresh (earlier answers withdrawn once with `reason:'not-studied'`, card = the
new answer alone, the past saved result unchanged); a refused submit puts the
card back too; a skip-marked flagged question with earlier answers also leaves
the due queue.
Fixes 2026-11-14 (one case each): all-flagged result is a shell from its
first save (timed and Practice, mock/make-up link kept) and a partly flagged
result is clean at its first save; a failed finish does not settle; flagged
skip-marked question leaves Today's Review; no flag after time is up, raw
score line; a remotely synced flag keeps this session's counted answer; a
resumed session leaves out an answer a later session withdrew; discard and
abandon settle, stale kept-aside entries pruned; timed option choice keeps an
earlier flag until submit; a refused submit restores undo events, kept-aside
card and flag; unflag rebuilds a missing card cache. Sync: synced tombstones
pruned to `notStudiedCleared` with merge unchanged; the shell beats a stale copy.
Sync: one envelope per question, session travels, nothing kept aside is
uploaded, tombstone payload, merge order and ties, unsafe ids, remote flag
hides/unhides that session's answers on another device, 20 cross-device
toggles converge on the newest, no repeated uploads.

`tools/verify_not_studied_browser.py` (390 px and desktop, light and dark):
header placement and target, footer untouched, analysis grid flagged cell
distinct from omitted, Review Solutions navigator and Practice review sheet
flag cells and legends, topic grid corner flag, list badge, Practice flagged.

Not device-verified.
