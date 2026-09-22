# BC4 — Question Interaction Integrity

Base: canonical BC3 `54f7d0fe210683e6236a00a6669f145734ae0335`.
BC3 was fast-forwarded only after Engineering `35738354092` and Android/PWA
`35738352700` passed on that exact SHA. All eight BC3 donor commits were retained;
newer canonical Anatomy Ch7 explanations/browser coverage and the 635/2,076
inventory were preserved. Inventory regeneration was byte-identical. No source
content, explanations, images, inventories, or automation assets change in BC4.

## Defects

| ID | Reproduction | Root cause | Architectural correction | Regression / status |
|---|---|---|---|---|
| QI-01 | Inject a failed save, then answer correct/wrong, Next with a pending rating, or toggle a bookmark. In-memory progress changes despite unchanged durable state. | Individual handlers ignore failed saves; nested FSRS/navigation handlers save and render independently. | One nested transaction collects saves, rendering, route publication and success feedback; persist once, or restore the entire pre-action state. | Real-handler failure tests reproduced before fix and pass afterward; generated-browser quota/restart matrix pending. |
| QI-02 | Navigate to q2, then invoke q1's stale option handler; or pass option 99. | Selection trusts supplied question ID and option without validating current identity or canonical choices. | Validate active mode, question identity and option membership at action boundary; reject stale pointer identity and duplicate browser clicks. | Stale/out-of-range real-handler tests pass; phone/tablet double-click matrix pending. |
| QI-03 | Invoke selection for an expired CBT question, or legacy Retry on Review / submitted Practice. | Visual locking was not enforced by all handlers. | Enforce expired/submitted/read-only state at handler boundary. Existing CBT answer changes remain allowed before submission. | Handler immutability, CBT changeability and duplicate-attempt tests pass. Browser matrix pending. |
| QI-04 | Enter Bookmarks with default normal context, or FSRS using context without originRoute. | Normal-mode classification reads only the first populated field; reliable session creation drops originRoute; FSRS source classification ignores context. | Classify all session identity fields and preserve originRoute at creation; FSRS source has a context fallback. | FSRS-source test reproduced before fix and passes after; full Practice→Wrong→Bookmarks→FSRS→Review→Practice browser transition pending. |
| QI-05 | Browser/Android WebView history Back while recall is pending. | hashchange bypasses the function-navigation FSRS save boundary and may retain modal overlays. | History boundary durably flushes elapsed/pending work, restores the old route on failure, and removes stale navigation overlays after success. | Browser history regression pending; native WebView uses the same history path. Physical Android testing not available in this environment. |
| QI-06 | Restore a legacy selected-but-unsubmitted Practice answer, then submit the session. Analysis counts it but no attempt or FSRS event exists. | Final result classification reads selections while attempt creation runs only in question submission. | Explicit final submission commits every valid pending selection through the shared answer/FSRS path inside the same transaction. Pause still preserves the unsubmitted state. | Failing regression reproduced; fixed handler test and final-submit browser assertion added. |
| QI-07 | Finish FSRS with the session-review sheet open; Analysis appears behind a modal and Review Solutions cannot be tapped. | Special-mode finish bypasses normal Practice overlay cleanup. | The shared committed route transition removes session overlays whenever it leaves a question surface, including special-mode finalization. | Reproduced in browser run `35761765709`: the old sheet intercepted every Review Solutions click. Explicit overlay-survival assertion now covers this path. |

First full candidate `d4c1aed`: Engineering passed (`35752801349`); build
`35752800543` passed the existing browser/lifecycle suites and the BC4 answer,
quota, double-navigation, Pause/reload and Wrong/Bookmarks checks, then failed in
the new test fixture because it assumed `fsrsReviewEligible` was initialized.
The fixture now initializes its skipped-state map explicitly; no product
assertion was removed. Rerun pending.

## Scope and audit contract

- Practice is already tap-to-submit. Changing a choice before submission applies
  to CBT; a legacy selected-but-unsubmitted Practice fixture is tested through Pause.
- Correct/wrong/selected styling, bookmark toggle and persistence, classification,
  Previous/Next, grids, double Submit/Pause/navigation, stale callbacks, restart,
  and mode isolation are exercised without redesigning controls.
- Canonical does not expose option-percentage badges or “X% got it right”. The
  historical percentage pilot is unmerged; these are not added as a BC4 feature.
- Generated runtime phone/tablet coverage is not physical device verification.
- The full build now also installs its exact APK in an Android 35 emulator and
  exercises native WebView phone/tablet layouts, hardware Back, force-stop/reopen,
  Pause/Resume, bookmark/attempt persistence, double navigation/submission and
  read-only Review. This is native emulator verification, not physical acceptance;
  the first run is pending. No app debugging flags or production code were added.
- Final exact-SHA verification and results remain pending.

Local real-handler coverage now includes 20 assertions: stale question and old
session callbacks, invalid options, stale CBT callbacks, correct/wrong save
rollback, pending-rating/navigation rollback, bookmark rollback, expired CBT,
Review/submitted-Practice immutability, current and legacy FSRS origin, duplicate
submission/rating, CBT answer changes, single-commit answer, legacy final answer,
successful/failed history Back, and duplicate/stale pointer input. Shared source
contracts additionally test Bookmarks/Wrong/FSRS checkpoint preservation.
