# Continuous Revision workflow

The Revision hub now launches **Practice mistakes**, **Practice bookmarks**, and
**Review due**. Mistakes and Bookmarks snapshot the complete eligible focused
queue, shuffled once. Due snapshots all cards admitted by the existing FSRS
priority order and daily review limit. Unseen retains its existing 20-question
sample. A protected timed test cannot be replaced by a Revision action.

The header grid and last-question Next open the same shared final review sheet.
It offers **Pause** and **Finish session**, with question cells and Close for
returning to study. The old intermediate navigator and Review unanswered / Back
to question action rows are absent for these hub queues.

Pause commits answered work and pending recall ratings, then returns to Revision.
The hub shows saved sets with scope, answered count and saved position. Resume
uses the same session ID, complete original ordered question list, index,
answers, submitted flags, per-question timing and pending ratings. Starting a
different session preserves the existing checkpoint rather than rebuilding its
membership from a changing mistake/due/bookmark list.

Finish closes this pass whenever the learner chooses. Its Practice result
includes only answered questions; untouched questions are never marked skipped,
added to FSRS, or counted as incorrect. Finishing before answering creates no
empty result. Completing all questions creates the normal Practice result.
Mistake resolution, bookmarks and FSRS schedules retain their existing answer
and rating behavior.

## Implementation

`tools/revision_session_core.js` is installed by the existing deterministic
`tools/apply_revision_desk_v1.py` owner, after the shared Practice/persistence/FSRS
owners. It opts in only explicitly tagged hub queues. Chapter Practice, one-off
browse questions, Custom Study Modules, CBT and Review Solutions retain their
existing contracts.

The existing durable checkpoint collection, journal, account isolation, sync
merge and terminal tombstones are reused. Queue kind, original context and focus
are stored in the checkpoint's existing extensible context. There is no new
storage namespace, schema migration, scheduler or parallel question engine.
Restored Due sessions retain `context: fsrs`, so answered questions still count
as FSRS reviews toward the same daily limit. Unknown Revision kinds fail closed
on checkpoint restoration. Queue start, Pause and Finish use the existing atomic
question transaction, including durable-save rollback and committed feedback.

## Validation

- Source and transform tests cover opt-in boundaries, full membership, kind and
  context recovery, answered-only result membership, terminal checkpoints, repeat
  finish guards, ordinary Practice delegation and legacy checkpoints.
- Real generated-app phone 390×844 and tablet 820×1180 checks cover 27-question
  Mistakes/Bookmarks queues, completing all 27 bookmarks beyond the old boundary,
  mid-session Pause, reload/Resume identity and timing, final-question Next,
  failed Pause/Finish followed by the existing Retry save recovery, a one-answer
  Finish leaving 26 mistakes, and a zero-answer Finish producing no result.
- Due checks verify 23 admitted cards in exact priority order, four rollovers
  under a 23-card daily limit, correct FSRS attempt source after answer/Pause, and
  restored Due context. Timed-test replacement is rejected.
- Existing broad Revision and mandatory Continue Practice browser regressions
  pass, including 320/390/820px Practice, multiple paused chapters, saved index,
  full ordered IDs, Pause-as-no-skip, final Submit-as-skip and Analysis/Review.
- Installed Impeccable Operate/clarify/craft-floor guidance informed the scoped
  labels and sheet. Batched phone/tablet screenshots were inspected; detector
  reported no findings. Existing identity, icon system and haptics remain.

The new source/browser tests are called from the existing Revision CI gates.
Generated diagnostic checks above are local browser verification; final artifact
certification still requires the full build/PWA/APK/Android workflow. No physical
device or production acceptance is asserted by this document.
