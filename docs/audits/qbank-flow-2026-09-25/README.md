# QBank flow clutter audit — 2026-09-25

Source: fresh generated-app browser captures from workflow run `36042991236`
at product commit `a6f8055`. Phone viewport: 390 × 844. The workflow also
captured small phone, enlarged text, and tablet variants. The screenshots below
show the **before** state. The findings also use the click handlers in the
build scripts to distinguish destinations that only look similar.

| Step | Screen | Health | Finding | Change |
| --- | --- | --- | --- | --- |
| 1 | [Home](01-home-before.png) | Needs work | FSRS, module creation, session history, and progress each recur in multiple Home sections. On a fresh account, “Continue Practice” opens subject selection. Empty performance sections make the page long before there is any study data. | Show a continuation card only when there is something to continue. Keep saved modules, subjects, and one progress summary; use the dedicated tabs for FSRS, Tests, and Insights. |
| 2 | [Module builder](02-module-builder-before.png) | Good | The selected banks, topics, question type, PYQ source and count are explicit before creation. “Change banks/topics” has a clear purpose. | Preserve the builder and its filters. Home has one module-creation entry in the empty state. |
| 3 | [Tests](03-tests-before.png) | Needs work | “Full Question Bank” and “Custom Module” reach the same timed builder. The Practice tab sends Custom Module to the study-module builder. The count on Tests is repeated in the timed builder. | Make Tests a timed-test destination. Use one subject/topic builder, with wrong/bookmarked quick tests as distinct history-based sources. Put completed tests here. |
| 4 | [Timed builder](04-test-builder-before.png) | Good | Subjects, topics, count and the Start action are visible in one place. | Keep it as the canonical subject/topic setup for timed tests. |
| 5 | [More](05-more-before.png) | Needs work | Create module, Timed CBT, Insights, Topics and Due review repeat Home or the primary tabs. | Keep saved-question lists and app controls; remove repeat launchers. FSRS remains its own tab. |
| 6 | [Insights](06-insights-before.png) | Mixed | The complete topic list pushes recent sessions far down the page, even when all topics have no attempts. The Tests link duplicates the primary tab. | Show six topic rows first, with an explicit control to reveal all rows. Keep recent practice and test history here. |
| 7 | [Chapter](07-chapter-before.png) | Good | Practice and Timed test have different feedback and timing behavior within the selected chapter. | Keep both actions. |
| 8 | [FSRS](08-fsrs-before.png) | Good | Subject selection and due-review information form a dedicated task. | Keep the dedicated tab; remove Home and More copies of its entry point. |
| 9 | [Results](09-result-before.png) | Mixed | Review Solutions appears near the top and again beside “Every answer”; both open the same review. | Keep the primary Review Solutions action and remove the duplicate. |

## Accessibility and evidence limits

- Several old Home and Insights captions render at about 8–10 px in phone
  captures. The flow cleanup reduces how much of that text must be scanned;
  contrast and text scaling still need a physical-device review.
- Screenshots show layout and visible hierarchy. They do not establish screen
  reader order, keyboard behavior, cloud sync, or physical Android acceptance.
- The capture used a fresh state. The saved-module card and long test histories
  require separate stateful review after this cleanup build.
