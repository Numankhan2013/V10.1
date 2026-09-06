# V11.3 Question Experience Design QA

## Target

The user-approved revised Calm Study Canvas mobile question screen: compact session progress, subject/topic tag, accessible answer states, quiet timing metadata, Key Takeaway, canonical source-PDF explanation, and fixed Previous/Next actions.

## Automated checks

- Approved layout markers are present exactly once in generated HTML.
- Practice still uses the canonical `selectPractice`, `prevQ`, `nextQ`, bookmark, and question-navigator functions.
- Timing is read from the existing per-question `questionTimes` state.
- Duplicate Correct/Incorrect success-panel copy is absent from the rebuilt Practice renderer.
- Source explanations still use `renderExplanationText` and the exact PDF solution mappings.
- Source-PDF scale is raised only to the native renderer's existing 4x safety ceiling.
- Generated JavaScript, protected product contracts, CBT invariants, Gradle build, and packaged APK verification pass in GitHub Actions.

## Blocking visual checks

The final Android WebView could not be captured in this environment. Physical-device verification is required at the same interaction state as the approved target, including correct and incorrect answers, a long question, a long option, a multi-page explanation, safe-area behavior, PDF sharpness, and pinch zoom.

Final result: blocked
