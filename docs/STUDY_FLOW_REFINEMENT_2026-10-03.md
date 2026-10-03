# Study-flow refinement — 2026-10-03

The user accepted the subtle visual and icon direction from PR90 and requested another Impeccable UX/UI pass focused on interruptions. Preserve that direction and the existing study architecture.

## Audit and direction

Used the installed official Impeccable audit, harden and craft-floor guidance. Inspected the actual certified PR90 artifact on phone (390×844) and tablet (820×1180), including Practice, notes, question search and custom module setup. Existing immediate answer locking, feedback, FSRS controls, native filter continuity and haptics remain unchanged.

Reproduced three interruptions: unsaved recall notes disappeared on Next/Previous; explicitly opening the note editor left its actions behind the fixed study footer; search pagination rebuilt earlier rows and dropped keyboard focus. Module count selection also replaced the focused control. A longer round trip exposed Notes-origin practice returning to Topics and losing the Notes search. Module step changes left keyboard focus on BODY, and a custom count of 0 advanced to a one-question review. Editing fields used 14–15px text.

The refinement keeps the established warm paper, violet actions and two-tone icons. It adds continuity rather than animation: session-only draft retention, deliberate editor reveal, progressive result append and stable module-setting focus. Editor/select text is 16px; Save uses the established violet action color.

## Behavior and boundaries

Drafts live only in memory and are fenced by session and account. Save remains the only durable write; Cancel discards the draft. Restoring a draft does not steal focus or scroll the question. Saved note escaping, storage rollback, deletion tombstones and question identity remain under the existing notes owner. Reloading ends temporary draft retention.

Search uses the existing matching and ranking functions and appends the next 30 results, retaining all previous nodes and the result summary. Keyboard pagination focuses the first newly added Practice action without changing scroll position. Filters retain their existing in-place behavior.

Module setting rerenders restore the same action while the builder step title stays unchanged; changing steps focuses the new heading immediately. Invalid custom counts (empty, 0, over 500 or fractional) show an inline correction, mark the input invalid and prevent advancement until corrected. The existing count bounds and question eligibility remain unchanged. Final review uses content height rather than a fixed 300px minimum. Notes-origin practice records its correct return destination; result Back returns to Notes with its existing query reapplied. Queries are memory-only and clear on account changes. Notes/search use the shared search and chevron glyphs; Notes adopts the accepted warm-paper/violet palette and readable editing text. No scoring, FSRS, history, module eligibility or source data changes.

## Validation

`verify_study_flow_browser.py` exercises note visibility above the footer, mixed RTL/escaped text, draft navigation and non-persistence, explicit Save/Cancel, retained search nodes and keyboard focus, module focus and 16px editing on phone/tablet. It runs in full CI. Note source tests additionally verify account/session fencing and existing persistence rollback.

Expanded coverage includes failed note writes retaining text and saved data, a complete Notes → Practice → Analysis → Notes round trip, 180 results without duplicate/rebuilt rows, keyboard step headings, four invalid count cases, recovery to a valid 24-question review and content-height review geometry. Existing notes reload/review/removal and exact-ID/bank/filter/search/exam-guard regressions also passed. Source checks: 93 passed; viewport interaction/visual checks passed at320/390/820/1194px and reduced motion. Impeccable focused detection returned no findings. The smaller initial candidate run37100662997 was cancelled before preview deployment after the user requested a larger consolidated batch. Full generated/PDF/APK/Android and hosted checks remain pending for the expanded candidate. Browser/emulator evidence does not establish physical keyboard or haptic quality.

## Technical audit assessment

Ratings apply only to inspected surfaces, not a whole-product accessibility certification. Accessibility3/4: labeled editors, retained keyboard focus, explicit outcome/error text and measurable contrast; physical assistive-technology checks remain outside browser evidence. Performance3/4: search append retains old nodes and uses no new dependency or animation gate; large-bank indexing remains existing synchronous behavior. Theming2/4: focused refinements use the approved shared palette, while unrelated legacy styles remain intentionally outside scope. Responsiveness3/4: narrow/phone/tablet/wide checks and long-copy/RTL note checks pass; physical keyboards remain untested. Pattern discipline3/4: no new ornamental motion or containers, shared glyphs replace stray search/chevron characters, and the final module review removes artificial blank height.
