# Study-flow refinement — 2026-10-03

The user accepted the subtle visual and icon direction from PR90 and requested another Impeccable UX/UI pass focused on interruptions. Preserve that direction and the existing study architecture.

## Audit and direction

Used the installed official Impeccable audit, harden and craft-floor guidance. Inspected the actual certified PR90 artifact on phone (390×844) and tablet (820×1180), including Practice, notes, question search and custom module setup. Existing immediate answer locking, feedback, FSRS controls, native filter continuity and haptics remain unchanged.

Reproduced three interruptions: unsaved recall notes disappeared on Next/Previous; explicitly opening the note editor left its actions behind the fixed study footer; search pagination rebuilt earlier rows and dropped keyboard focus. Module count selection also replaced the focused control. Editing fields used 14–15px text.

The refinement keeps the established warm paper, violet actions and two-tone icons. It adds continuity rather than animation: session-only draft retention, deliberate editor reveal, progressive result append and stable module-setting focus. Editor/select text is 16px; Save uses the established violet action color.

## Behavior and boundaries

Drafts live only in memory and are fenced by session and account. Save remains the only durable write; Cancel discards the draft. Restoring a draft does not steal focus or scroll the question. Saved note escaping, storage rollback, deletion tombstones and question identity remain under the existing notes owner. Reloading ends temporary draft retention.

Search uses the existing matching and ranking functions and appends the next 30 results, retaining all previous nodes and the result summary. Keyboard pagination focuses the first newly added Practice action without changing scroll position. Filters retain their existing in-place behavior.

Module setting rerenders restore the same action only while the builder step title stays unchanged. Advancing steps retains the existing navigation behavior. No scoring, FSRS, history, module eligibility, source data or navigation semantics change.

## Validation

`verify_study_flow_browser.py` exercises note visibility above the footer, mixed RTL/escaped text, draft navigation and non-persistence, explicit Save/Cancel, retained search nodes and keyboard focus, module focus and 16px editing on phone/tablet. It runs in full CI. Note source tests additionally verify account/session fencing and existing persistence rollback.

Local source checks: 93 passed. Actual phone/tablet browser checks passed. Full generated/PDF/APK/Android and hosted checks remain pending until CI completes. Browser/emulator evidence does not establish physical keyboard or haptic quality.
