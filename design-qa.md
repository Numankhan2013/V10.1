# V11.3.1 Shared Session Experience Design QA

## Target

The approved Calm Study Canvas question screen across Guided Practice, timed CBT, and Review Solutions: compact progress, a medically recognizable subject/topic tag, unambiguous answer states, a viewport-docked footer, a working question grid, useful source-grounded takeaways, and the canonical source-PDF explanation.

## Implemented corrections

- Removed all option-side circles and detached correctness icons; the option border, fill, and letter badge carry state.
- Docked Previous/Next to the bottom viewport edge with explicit safe-area and content clearance.
- Replaced Biochemistry's network-like symbol with a DNA double helix; retained the approved Physiology heart and Anatomy body icon.
- Strengthened the answer-time treatment in blue without adding a duplicate Correct/Incorrect panel.
- Removed the correct-option-only takeaway fallback. A takeaway appears only when reviewed content exists or a meaningful sentence can be extracted from the source explanation.
- Removed the legacy inline navigator that caused the four-dot overlay to be deleted in Practice.
- Applied the shared shell to Practice, CBT, and Review while preserving CBT answer privacy and changeability.
- Preserved the exact source-PDF renderer at its existing 4x ceiling.
- Added conservative source-image canvas trimming and post-crop Lanczos interpolation; it never generates or reconstructs medical content.

## Automated checks

- All three session renderers use the shared shell and fixed navigation footer.
- CBT contains no correctness, takeaway, or source-explanation reveal before submission.
- Practice and Review preserve timing, bookmarking, source explanation, question jumps, and terminal-session behavior.
- Legacy option-hole and inline-navigator markup is absent.
- Navigator status semantics are mode-specific.
- Transformation ordering, generated JavaScript syntax, product contracts, CBT invariants, Gradle build, and packaged APK checks run in GitHub Actions.

## Blocking visual checks

The final Android WebView cannot be captured in this environment. Physical-device verification remains required for correct and incorrect Practice answers, unanswered and answered CBT states, Review Solutions, an anytime grid jump, long options, a multi-page PDF explanation, bottom safe-area behavior, a cropped dark-canvas figure, and pinch zoom.

Final result: blocked
