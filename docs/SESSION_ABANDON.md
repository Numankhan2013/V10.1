# Abandon session

Owner request, 2026-11-13 (Hark). Module `app/src/main/modules/session_abandon.js`
(`NK_SESSION_ABANDON_V1`, installed after `not_studied_flags.js`), styles
`/* ── nk-session-abandon-v1 ── */` in `app.css` (before the visual refinement
layer, which must stay last), native dialog `NATIVE_CONFIRM_ACTION_V1` in
`MainActivity.java`. It supersedes the timed-only grid action
(`timed_abandon_grid.js`, removed): same place for timed tests, now for every
session type, with a real confirmation and a history entry.

## What the learner sees

- **Where:** a quiet destructive row, "Abandon session" (timed tests: "Abandon
  test"), at the foot of the sheet that already ends a session: the review sheet
  (header Back; in Practice also the grid icon) and the question navigator (grid
  icon in timed tests and the other modes). It sits under a hairline, below
  Pause / Submit (which stay the only two actions, as the accepted Practice
  contract requires), never on the question screen, header or footer.
- **Confirm:** "Abandon this session?" / "Abandon this test?" — "Your answers
  won't be saved or counted. Nothing from this session reaches your reviews,
  mistakes or stats." plus "N of M answered", with Cancel (focused first) and
  Abandon (solid red). Escape, Cancel or a tap outside cancels.
  - Android shell (newer APKs): a native AlertDialog in the app theme with a red
    Abandon button, through `QBankShell.confirmAction(requestId, title, message,
    confirm, cancel)`; the answer returns via `window.QB.nkAbandonAnswer`.
  - PWA / browsers / older shells: the in-app alert dialog (`role=alertdialog`,
    focus trapped, reduced-motion aware). Never `window.confirm()`.
  - Haptics: `NKFeel.haptics('toggle')` when the dialog opens,
    `NKFeel.haptics('impact')` on Abandon (native bridge → vibration → iOS switch).
- **After:** the session ends (timed tests → Tests; Practice → where it started;
  revision → Revision; study module → Home) with the toast "Session abandoned.
  Nothing from it was saved." The Tests "Recent" list (timed tests) and Insights
  "Study sessions" show the session as a row with an **Abandoned** badge and
  "N of M answered · date". The row opens nothing.

- **System Back (owner request, 2026-11-14):** during a live Practice session
  or timed test, Android's system Back opens the same "Abandon this session?" /
  "Abandon this test?" confirmation (Back first closes an open sheet or viewer;
  Back while the dialog is open cancels it).
  - Web app / PWA (mobile browser or installed from Chrome): a guard history
    entry (same URL, `history.state.nkSessionGuard = <session id>`) is pushed on
    render while a session is live. Back pops it; the page pushes it back and
    opens the in-app dialog. Cancel keeps the session; Abandon runs the flow
    above. Any navigation off the session (Submit → Results, Pause, Abandon,
    in-app links) is held by the page's `navigate()` (`nkBackGuardHold`) until
    the guard is popped, then replayed through the page's own navigate
    (`nkNavigateBase`), so history is identical to a run without the guard.
    A guard left by a session that ended without leaving its page (e.g.
    abandoned on another device) is popped quietly.
  - Android shell: no guard. `MainActivity.onBackPressed` asks
    `window.QB.nkSessionBack()` (`NATIVE_BACK_ABANDON_V1`); `handled` means the
    page closed a sheet or opened the native abandon dialog (`confirmAction`).
  - Scheduled mocks (cannot be abandoned) and paused sessions get no guard and
    keep the existing "Do you want to exit?" warning (browser `confirm()` /
    native Stay/Exit). Leaving a session without abandoning it is done from the
    app (review sheet Pause, or the app's own navigation), not system Back.

Covered: Practice (topic, mixed, all-subject, not-studied practice, correction),
Revision queues (wrong / bookmarks / due), Today's Review / FSRS review, study
modules, timed CBT, topic timed tests (per-question timer), quick tests, CBT
retakes. Not offered: Review Solutions (nothing to abandon) and scheduled mocks
(existing rule: a scheduled mock is submitted, never abandoned).

## The rules

**A1 — One trace.** An abandoned session leaves only its entry in
`state.abandonedSessions` (`{sessionId,title,mode,kind,subject,total,answered,
startedAt,abandonedAt,updatedAt}`, newest 200 kept).

**A2 — Answers recorded at once are withdrawn.** Practice records every answer
when it is made (FSRS attempt with the session id). Abandon writes an FSRS undo
event (`isUndo`, `reason:'abandoned'`) for each of the session's attempts —
answered right, wrong, rated, revised — and replays those cards, so each card is
what it was before the session (an old-scheduler due date is given back). A
correct answer still waiting for its recall rating is dropped, never committed.
Undo events are the existing mechanism every app version honours.

**A3 — The session id is excluded everywhere.** `nkFsrsActiveAttempts` drops
any attempt whose `sessionId` is abandoned. FSRS cards and the due queue,
mistakes (`wrongQuestions` / practice mistakes), accuracy and topic stats,
Insights (questions, time, heatmap, streak), coverage, Today, the Home
"continue" topic and the topic grid all read through it, so an answer that
arrives later from another device (still in the session, or an old outbox)
never counts either, with or without an undo event.

**A4 — Nothing else is written.** No skip marks (`fsrsReviewEligible`), no
result in `state.tests` (so no score, CBT/mock analysis, mock insights,
scheduled-mock record), no study-module completion. Timed tests record nothing
before Submit, so their session is simply dropped.

**A5 — It cannot come back.** A normal/revision Practice checkpoint becomes a
terminal `discarded` tombstone (`abandonedAt`); terminal wins every checkpoint
merge. Continue Practice, the paused-sessions sheet and resume-by-id refuse
abandoned ids even from a stale paused copy. The synced special session
(`sessions/active`) is deleted, and an incoming copy of an abandoned session is
dropped on apply.

**A6 — Side effects of answering are undone.** A not-studied flag from an
earlier session that answering in this session cleared is put back (newer
`updatedAt`, so it wins sync). A flag set in the session, or a flag removed by
hand, stays: those are the learner's choices, not answers. A study module gets
the progress it had when the session began (kept on the session as
`abandonBase`; for sessions started before this version, this session's
answered questions are removed), under a new `syncEpoch` so the union merge
cannot resurrect them.

**A7 — Sync.** Kind `abandoned`, one document per session
(`users/{uid}/abandoned/...`, existing owner-only rule), never deleted. On
arrival: the entry is added (newer copy wins), a session still open on that
device ends, its checkpoint becomes terminal; the post-pull FSRS rebuild drops
the session's answers. Account reset tombstones the kind like every other kind.

**A8 — "Timed test in progress".** Choosing *Abandon test* in that dialog (when
starting another session) records the test the same way, without a second
confirmation.

## Not covered by design

Bookmarks, notes, highlights and voice clips made during the session stay:
they are the learner's content, not attempts. The learning-analytics worker
(`nk-jev`) is not called by the app today; if it is wired in, it must read
attempts through `nkFsrsActiveAttempts` (or skip abandoned session ids).
Discarding a *paused* session from the Paused Practice sheet is unchanged: it
ends the session but keeps the answers already counted.

## Tests

`tools/test_session_abandon_v1.py` (Node, real FSRS / Continue Practice /
not-studied modules, driven clock): abandoned run = run without the session for
cards, active attempts, rating revisions, skip marks, due queue, counts, stats,
results, resumable list and Home continue topic; earlier card byte-identical;
cancel; pause → reload → resume → abandon; timed test; scheduled mock; timed
conflict dialog; late answer from another device; not-studied restore rules;
study module restore + epoch; history rows; entry cleaning/cap; sync envelope,
remote entry ends the session there, a synced session copy cannot reopen it.

`tools/verify_session_abandon_browser.py` (built app, 390 px and 1280 px, light
and dark): placement inside the sheet under Pause/Submit (still exactly two),
44 px target, alert dialog fits, Cancel focused, Escape cancels, state after
abandon, Insights row badge, timed navigator/sheet rows clear of Submit, Tests
"Recent" row. Screenshots: `build/ui-checks/session-abandon/`.

`tools/test_session_back_guard_v1.py` (Node, the page's real `navigate()` and the
module over a fake history): guard pushed once; Back opens the dialog; Cancel,
Back-to-cancel, Abandon; Submit → Results, Pause, in-app navigation and abandon
leave history identical to an unguarded run (no guard left, no doubled Back);
overlays close first; scheduled mock and paused sessions unguarded; stale guard
dropped; Android `nkSessionBack` opens the native dialog. Source contracts on
`navigate()`, `window.QB.nkSessionBack` and `MainActivity`.
`verify_session_abandon_browser.py` also drives `history.back()` in Chromium.

`tools/verify_android_question_interaction.js` (emulator job, dispatch with
`build_apk=true`): taps the native dialog's Abandon; KEYCODE_BACK opens it and
Cancel keeps the session (not run for this change).

Not device-verified.
