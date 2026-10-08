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

## Build and verification

The deterministic pipeline installs FSRS after cross-device integration and verifies the generated source, web artifact, and packaged APK assets. `tools/test_fsrs_v1.py` covers migration, replay, all-attempt eligibility, ratings, queue caps and filters, preferences, undo, pending-rating recovery, and the offline vendor assets. The generated-browser Continue Practice regression owns the Pause-versus-Submit boundary.

FSRS acceptance status as of 2026-09-07: the new APK was installed and confirmed working, and the website/PWA was opened and confirmed functional. The separate Firebase cross-device synchronization acceptance remains tracked in the project memory and deployment handoff.


## Recall dock

After a correct answer is submitted, the Hard / Good / Easy recall dock appears
inside the fixed practice footer, immediately above Previous / Next. It uses the
approved brain medallion, Rate recall / Default: Good label, text-only pills,
purple Good default, and a static lilac glow. It is absent before answering and
in CBT/review modes. Incorrect answers retain automatic Again; Next still commits
an unanswered recall prompt as Good. Scheduler semantics are unchanged.
