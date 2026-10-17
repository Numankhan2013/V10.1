# FSRS audit — 2026-10-16

Scope: the complete FSRS system (scheduler module, host integration, durable
persistence, cross-device sync, and the user-facing review surfaces). Method
requested by the owner: find and fix every bug or issue across the app;
"most robust, best ever".

## Method

1. **Adversarial Node battery** driving the real `fsrs_scheduler.js` with a
   fake `Date` class (exact boundaries, rating chains replayed against the
   pinned ts-fsrs 5.4.2 engine as an oracle, undo, fuzz replay, migration,
   determinism).
2. **Browser time-travel audit** (Playwright `page.clock`): seeded cap/rollover
   state; answer → pending → commit; lapse; relearning step; graduation; undo;
   crossing midnight for whole-day due and overdue, all on the generated
   app; plus a real-clock probe of the rating dock.
3. **Performance probe** of `nkFsrsQueue`/counts/forecast with a heavy due
   backlog, since the queue is rebuilt on every Home/Revision/FSRS render.
4. **Cross-device sync review** of merge/rebuild/eligibility/revision paths.

## Findings

### F1 — `nkFsrsQueue` rebuilt a scheduling engine per comparison (fixed)

The review-retrievability sort comparator called `nkFsrsRetrievability()`,
which constructed a fresh ts-fsrs engine on every comparison. With a 2,984-card
due backlog the queue build took **346 ms** on a desktop-class Node process
(worse on Android WebView), and the queue runs on every Home/Revision/FSRS-page
render.

Fix: one engine per queue call, one retrievability value per card computed
before sorting (`retrOf` map), and the "seen today" scan narrowed to due cards
(only due cards can be filtered by it). Measured: **346 ms → ~70 ms** for the
same backlog (~5×). Ordering is bit-identical — the battery's ordering, cap,
and determinism scenarios all stay green.

**Correction (2026-10-17):** narrowing the "seen today" scan to due cards was
wrong. A card reviewed today usually leaves `due`, but it has still spent the
daily cap. With the narrowed scan, a cap of 20 let 19 more cards in straight
after 20 reviews. S4 missed this because its "seen" cards were kept due
artificially. The scan now walks every question that has attempts; the engine
and `retrOf` gains are unchanged. New scenario S4c makes 20 real reviews and
then requires an empty queue.

### F2 — whole-object preference sync could lose a concurrent setting edit (fixed)

`cross_device_sync.js` merged remote `fsrsPreferences` as
`{...local, ...remote}`: last writer wins the whole block. Scenario: device A
raises retention while device B (offline) raises the daily cap; whichever
envelope is newest overwrites the *other* field with the other device's stale
snapshot — a silent, unrecoverable setting loss.

Fix: every user change now stamps `state.fsrsPreferencesAt[field]=Date.now()`
and the stamp map syncs inside the preferences envelope (only when non-empty,
so legacy payloads stay byte-identical). Merging is per field: newer stamp
wins; untouched fields keep the previous whole-block behaviour, so old clients
and old payloads are unchanged. Locked by a new case in
`tools/test_cross_device_sync_v1.py` covering local-newer-wins, remote
field-adoption with stamp, untouched fields, and the legacy fallback.

### F3 — a missing derived cache scheduled from an empty card (fixed)

`nkFsrsRecordAttempt` extended `state.reviews[qid]`; if that cache was ever
missing while attempts existed (interrupted write, damaged import), the next
rating scheduled from `createEmptyCard` and silently diverged from the true
chain until the next full rebuild. Now the function heals by replaying the
stored attempts first. Covered by the new audit test (S16).

### F4 — dead legacy review paths (reported, not removed)

`dueQuestions()` / `startLibrary('review')` and `streakMarkup()` are
unreachable (the `#review` route resolves to `nkFsrsReviewPage`, and the
streak markup reads a field no writer sets). No live behaviour is affected;
removing them is deferred to keep this change narrow.

### F5 — audit-flow artifacts around dock visibility (not product bugs)

Two harness effects can make the rating dock look "hidden" without a product
defect. First, in flow tests that walk a session to its end with `Next`, the
final-review overlay stays open; its stylesheet deliberately hides every
session footer while it is open
(`body:has(#nk-session-review.nk-practice-final-review) .nk-session-footer`),
so a later session started programmatically renders with a hidden footer until
the overlay is closed the way a learner would. Every real entry point into a
session closes it first. Second, transition-driven nodes (toast) can look
hidden to tooling mid-animation; the CI browser contexts already pass
`reduced_motion='reduce'`. The audit closes the overlay after `Next` and then
asserts the visible, clickable dock on a real (unmocked) clock for both a
review card and a post-lapse relearning card. No app change required.

## Verified with no defects found

Whole-day due / learn-ahead exactness (±1 ms), queue ordering
(learning → retrievability ascending → skipped), daily-cap arithmetic with
learning-repeat exemption and rollover count, rating revision chains equal to
independent engine replays, undo of revisions/attempts/whole cards, pending
recovery idempotence, preview == record under fuzz for every grade including
relearning, per-attempt preference snapshots, legacy due preservation through
migration and later replays, eligibility priority and unanswerable exclusion,
exam binary grading, source mapping, mistake classification, three cold
rebuilds byte-identical, and the browser flows (cap/rollover toast + page
notice, learning repeat, lapse → relearning, graduation, undo, next-day
overdue, visible rating dock).

## Verification

- `python3 tools/test_fsrs_audit_v1.py` — 52 adversarial scenarios, new.
- `python3 tools/test_fsrs_v1.py`, `python3 tools/test_cross_device_sync_v1.py`
  (with the new per-field case), `python3 tools/test_study_module_fsrs_v1.py`.
- Browser time-travel audit against the rebuilt local PWA build: cap/rollover
  context, answer → pending → commit → lapse → relearning step → graduation →
  undo → next-day overdue context, plus real-clock dock probes (review card
  and relearning card).
- Queue performance probe (before/after above).
