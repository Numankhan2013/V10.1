# FSRS smart review

NK QBank includes a functional offline FSRS v6 review system in both the Android APK and the responsive website/PWA. Both targets use the same generated HTML and the same pinned scheduler assets, so review behavior stays consistent across platforms.

## Runtime behavior

- `ts-fsrs` 5.4.2 is vendored under `app/src/main/assets/vendor/ts-fsrs/` with its MIT license; the app never depends on a runtime CDN.
- The scheduler uses FSRS v6 with ts-fsrs fuzz enabled (its seed is the review time, repetition count and difficulty×stability, so every device replays identical intervals while review load spreads across days), 90% desired retention, a 365-day maximum interval, and 10-minute learning and relearning steps.
- Existing `state.reviews` entries migrate to schema v2. A local migration backup is created, and each legacy due date is preserved until that card receives its first new FSRS rating.
- Immutable attempts are the replay and synchronization truth. Schema-v2 review cards are derived from sorted attempts, with audit snapshots on rated attempts.
- Practice ratings support Again, Hard, Good, and Easy. CBT answers map to binary Again/Good outcomes, and a pending Good rating can be recovered if a session closes between answer submission and navigation.
- Every answered question enters the FSRS pool, regardless of correctness. Pausing commits answered questions (including a pending default-Good rating) but never adds untouched questions. Finalizing a session (Practice Submit, timed-test Submit, Finish a revision pass, Finish a study module) applies one **skip rule**: an unanswered question counts as skipped, and enters FSRS, if it comes *before your last answered question* (you moved past it) **or** you spent real time on it (15 s or more of recorded dwell time, so a hard question at the very end of a module that you tried and could not answer still counts). Questions you never opened, or only glanced at, after your last answer stay unseen; a session with no answers marks only questions you genuinely worked on. Example: in a 20-question session where you answer 1, 3, 4 and 5, question 2 enters FSRS as skipped and 6–20 do not, unless you worked on one of them for 15 s or more. Pause and Save & exit never mark anything. Questions that already have answer history are untouched by the rule.
- Availability follows Anki: a review card is due for its whole local calendar day; learning/relearning steps may be studied up to 20 minutes early (`nkFsrsIsDue`, shared by Home, Revision, the FSRS page and Insights).
- The all-subject Today queue orders learning/relearning steps first (by due time), then reviews from least to most retrievable, then submitted-as-skipped questions that were never answered; applies the 150-distinct-card daily cap; supports subject/topic filters; shows counts and estimates; and provides a seven-day forecast plus lapse attention flags.
- Questions that accept no answer (incomplete-source gates) are never review-eligible, never marked skipped and never listed as Unseen or as remaining Continue Practice work.
- The recall dock shows each grade's next interval on the button (for example Hard 15m · Good 2d · Easy 7d).
- Settings change future ratings without rewriting past attempt history. Undo records a reversible event rather than deleting synchronized history.
- Settings synchronize per field: each edit stamps `state.fsrsPreferencesAt[field]`, cross-device merge keeps the newest value for each field independently, and payloads without stamps keep the whole-block merge so older clients are unaffected.

## Build and verification

The deterministic pipeline installs FSRS after cross-device integration and verifies the generated source, web artifact, and packaged APK assets. `tools/test_fsrs_v1.py` covers migration, replay, all-attempt eligibility, ratings, queue caps and filters, preferences, undo, pending-rating recovery, and the offline vendor assets. `tools/test_fsrs_audit_v1.py` adds the adversarial audit battery: due/learn-ahead boundaries, cap arithmetic, revision chains against engine replays, undo, fuzz, cold-rebuild determinism, damaged-cache healing, preference stamps and a queue performance canary. The generated-browser Continue Practice regression owns the Pause-versus-Submit boundary.

FSRS acceptance status as of 2026-09-07: the new APK was installed and confirmed working, and the website/PWA was opened and confirmed functional. The separate Firebase cross-device synchronization acceptance remains tracked in the project memory and deployment handoff.


## Recall dock

After a correct answer is submitted, the Hard / Good / Easy recall dock appears
inside the fixed practice footer, immediately above Previous / Next. It uses the
approved brain medallion, Rate recall / Default: Good label, text-only pills,
purple Good default, and a static lilac glow. It is absent before answering and
in CBT/review modes. Incorrect answers retain automatic Again; Next still commits
an unanswered recall prompt as Good. Scheduler semantics are unchanged.

## Learning cards in a due review (2026-11-15, `feature/review-learning-queue`)

Module `app/src/main/modules/review_learning_queue.js` (`NK_REVIEW_LEARNING_QUEUE_V1`),
styles `/* ── nk-review-learning-queue-v1 ── */` in `app.css`. **Due-review sessions
only** (`revisionQueueKind:'due'`, started by Revision → Review due): normal
Practice, Today's Review (`spaced-review`), mistakes, bookmarks, modules and
timed tests are unchanged.

**In-session learning queue (Anki style).** A rating that leaves the card in
learning or relearning (FSRS state 1/3: Again from a wrong answer, or Hard on a
card still in a step) puts the question in `session.learningQueue[qid] =
{due, round}` with the card's FSRS due time. The queue entry follows the card:
revising Hard→Good on a revisit (graduated) removes it; a pending rating does
not enter until it commits. The card is never duplicated: `questionIds` and
`sessionQuestionIds` keep their membership, so the checkpoint `membershipHash`,
the abandon/Back guard and sync stay stable. It reopens **in its own row as a
new round**: the previous round's answer, submitted flag, time, outcome, rating
and attempt id move to `session.roundHistory[qid]`, the live answer clears, and
the header and the session grid show "Round N". `nkFsrsSessionRating` only sees
the live round's attempt (attempts at or after the round's `reopenedAt`).

- **Show when due** (default): on every Next (and after an auto-advance) a
  queued card that is due now comes before the rest of the set; Next from it
  continues after the card it interrupted (`learningReturnIndex`).
- **Show at the end**: queued cards wait until the set is done.
- **Off**: one pass, exactly as before (no queue, no rounds).
- At the end of the set (both modes) a card due within the 20-minute
  learn-ahead (`NK_FSRS_LEARN_AHEAD`) shows at once; if only later ones remain,
  a dialog says "1 learning card due in 14 min" with **Study now** (opens it
  now) and **Finish** (the existing end-of-session sheet, which also repeats
  the line with Study now).
- Every round records a normal FSRS attempt (`source:'fsrs-review'`; round 2+
  also carries `learningRound:N`), so the scheduling history is the full Anki
  log. The daily cap keeps exempting same-day learning repeats (`repeatIds` in
  `nkFsrsQueue`).
- **Results count each question once, by its latest answered round.** A round
  reopened but left unanswered gives way to the round before it; the result's
  time for the question is the sum of its rounds. Insights
  (`nkLearningCollect`) skip `learningRound` attempts, so a relearning repeat is
  not a second answered question; FSRS history and memory views keep every round.
- Persistence: `learningQueue`, `roundHistory` and `learningReturnIndex` ride in
  the practice checkpoint (`nkCheckpointFromSession`, `nkNormalizeCheckpoint`
  keeps only entries inside the session's membership), durable persistence and
  the sync merge (`nkMergePracticeCheckpoint`: per question, the copy with more
  rounds owns the live answer, its time and the queue entry; equal rounds keep
  the old rule). A reopened round adds the round count to that question's
  update signature (older signatures are unchanged). Payloads without these
  fields load and merge as before; Pause/resume restores them.
- A not-studied-flagged question never enters or stays in the queue (flagging
  removes it; unflagging in the session puts it back if the card is still learning).

**Advance after rating** (default on). In a due review, the first Hard/Good/Easy
on an answer (committing its pending rating) saves it, keeps the pressed state
for ~250 ms (`.nk-fsrs-rating.is-advancing`), then runs Next: a due learning
card first, the end-of-session sheet after the last card. Wrong answers never
advance (the explanation waits for Next). Changing an already saved rating only
saves. A tap while the advance waits is ignored; the timer fires only if the
same session, question and round are current, the session is not paused, the
question is not flagged and no sheet or dialog is open; Next/Previous/grid
jumps, flag toggles, Pause and Abandon cancel it.

**Settings** (FSRS customization → 04 Review sessions): "Learning cards in a
review session" (Show when due / Show at the end / Off) and "Advance after
rating" (switch). Stored in `state.fsrsPreferences.learningInSession` /
`advanceAfterRating`, stamped per field in `fsrsPreferencesAt` and merged per
field by sync like the scheduling values; older clients that drop the fields
leave them alone. Attempts record only the three scheduling values as
`schedulerPreferences`.

Tests: `tools/test_review_learning_queue_v1.py` (requeue timing, Hard/Good,
learn-ahead and the wait line, all three modes, result counted once, pause /
reload / resume, older and damaged checkpoints, auto-advance on first rating
only / not on wrong / no jump on revision / stale timers / end sheet, flags,
untouched other sessions, daily cap, checkpoint sync merge, preference merge);
`tools/verify_review_learning_queue_browser.py` (real app, 390 px and 820 px:
Again → Round 2 returns in the session → Good auto-advances → end sheet →
counted once). Not device-verified.
