# V11.4 Whole-App Vision Design QA

## Visual target

The user-selected PrepLadder-inspired dashboard, topics, and analysis references, harmonized with the accepted V11.3.1 Calm Study Canvas question experience. The app should feel compact, medically serious, source-faithful, and phone-native, with one obvious next learning action on each screen.

## Implemented scope

- Shared compact white header and five-tab bottom navigation.
- Home command center with streak, focus actions, accurate subject counts/progress, learning metrics, revision shortcuts, strongest chapters, and recent sessions.
- Subject and Topic navigation with medically recognizable subject icons, search, supported progress filters, accurate completion, and direct chapter entry.
- Chapter overview with Practice/CBT actions, coverage metrics, source-order question library, and attempt states.
- Timed CBT landing page, focused builder modal, scope/topic selection, question count, and test history.
- Practice and CBT result analysis with score, answer distribution, timing, completion, and canonical Review Solutions entry.
- Insights with accuracy, timing, completion, spaced review, chapter coverage, and recent sessions.
- Revision libraries and More reorganized into compact, descriptive lists and reliable empty states.

## Protected behavior

V11.3.1 Practice, CBT question answering, Review Solutions, the anytime navigator, bookmarks, exact source-PDF renderer, source-image handling, offline persistence, test history, and subject-specific datasets are not replaced by this visual layer.

## Automated checks

- Every non-question route has one canonical V11.4 renderer.
- Primary actions retain their existing window.QB behavior.
- Review Solutions retains its canonical entry attributes.
- The V11.3.1 session UI, Review grid contract, and 4x source PDF markers remain present.
- JavaScript syntax, product contracts, CBT invariants, deterministic build ordering, Gradle, packaged APK, and reproducibility checks run in GitHub Actions.

## Blocking visual checks

The Android WebView cannot be visually captured in this environment. Physical-device verification is required at 576px-class phone width for Home, all three subjects, Topics filters/search, a long chapter name, chapter question states, Test builder scrolling, empty and populated histories, Insights, More, Practice analysis, CBT analysis, and bottom safe-area behavior.

Final result: blocked
