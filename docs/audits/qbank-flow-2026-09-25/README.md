# QBank flow clutter audit — 2026-09-25

Source: fresh generated-app browser captures from workflow run `36042991236`
at product commit `a6f8055`. Phone viewport: 390 × 844. The workflow also
captured small phone, enlarged text, and tablet variants. The screenshots below
show the **before** state. The findings also use the click handlers in the
build scripts to distinguish destinations that only look similar.

| Step | Screen | Health | Finding | Change |
| --- | --- | --- | --- | --- |
| 1 | [Home](01-home-before.png) | Needs work | FSRS, module creation, session history, and progress each recur in multiple Home sections. On a fresh account, “Continue Practice” opens subject selection. Empty performance sections make the page long before there is any study data. | Keep the top streak and Today’s Focus; make the focus action honest for each study state. Remove only duplicate secondary launchers and empty sections. |
| 2 | [Module builder](02-module-builder-before.png) | Good | The selected banks, topics, question type, PYQ source and count are explicit before creation. “Change banks/topics” has a clear purpose. | Preserve the builder and its filters. Home has one module-creation entry in the empty state. |
| 3 | [Tests](03-tests-before.png) | Needs work | “Full Question Bank” and “Custom Module” reach the same timed builder. The Practice tab sends Custom Module to the study-module builder. The count on Tests is repeated in the timed builder. | Make Tests a timed-test destination. Use one subject/topic builder, with wrong/bookmarked quick tests as distinct history-based sources. Put completed tests here. |
| 4 | [Timed builder](04-test-builder-before.png) | Good | Subjects, topics, count and the Start action are visible in one place. | Keep it as the canonical subject/topic setup for timed tests. |
| 5 | [More](05-more-before.png) | Needs work | Create module, Timed CBT, Insights, Topics and Due review repeat Home or the primary tabs. | Keep saved-question lists and app controls; remove repeat launchers. FSRS remains its own tab. |
| 6 | [Insights](06-insights-before.png) | Mixed | The complete topic list pushes recent sessions far down the page, even when all topics have no attempts. The Tests link duplicates the primary tab. | Show six topic rows first, with an explicit control to reveal all rows. Keep recent practice and test history here. |
| 7 | [Chapter](07-chapter-before.png) | Good | Practice and Timed test have different feedback and timing behavior within the selected chapter. | Keep both actions. |
| 8 | [FSRS](08-fsrs-before.png) | Good | Subject selection and due-review information form a dedicated task. | Keep the dedicated tab; remove Home and More copies of its entry point. |
| 9 | [Results](09-result-before.png) | Mixed | Review Solutions appears near the top and again beside “Every answer”; both open the same review. | Keep the primary Review Solutions action and remove the duplicate. |

## First cleanup candidate — Home rejected

The generated app at `c863f1f` passed Engineering run `36051479141` and the
full browser, PWA, APK, and Android WebView run `36051447529`. The fresh-state
captures show [Home](10-home-after.png), [Home at 320px](11-small-phone-after.png),
and [Tests](12-tests-after.png). Home now puts one module action and the subject
list ahead of the streak display. The 320px Create module action is at least
44px high and clears the bottom navigation. Tests shows one subject/topic
builder plus separate wrong/bookmarked quick tests; it no longer offers two
buttons for the same builder. The full capture artifact on the build run also
includes More, Insights, FSRS, module steps, and question and result screens.

The user rejected this Home layout: moving the streak down and hiding Today’s
Focus stripped out the sense of a personal study dashboard. They accepted the
other flow changes. The next candidate restores the streak and focus hierarchy
while keeping the deduplicated navigation.

Reference check: [Marrow’s QBank guide](https://www.marrow.com/how-to-use-qbank-document)
emphasizes a consistent solving and revision habit, and its [QBank overview](https://www.marrow.com/)
shows visible progress and subject structure. [PrepLadder’s app guide](https://www.prepladder.com/help-center/prepladder-modules/how-to-create-test-or-qbank-practise-module)
keeps module creation inside a deliberate QBank flow; its [Medical PG dashboard example](https://www.prepladder.com/courses/medical-pg/offerings)
gives the streak its own prominent space. Our design inference is to keep one
clear daily study anchor above the library, then show the module and subject
choices without extra copies of their actions.

## Revised Home after the user's feedback

The new [fresh Home](13-home-focus-restored.png), [320px Home](14-small-phone-focus-restored.png),
and [saved-module Home](15-saved-module-focus.png) show the streak immediately
under the greeting and a persistent Today’s Focus card beneath it. A fresh
state says “Choose a subject” and scrolls to the visible subject list. A saved
unfinished module gets the Focus Continue action; its study-set card keeps
progress and management without a second Continue button. The browser capture
checks this hierarchy and the 320px button position. Engineering run
`36078896597` and full browser/PWA/APK/Android run `36078893896` passed on
product commit `8339764`; preview: https://eaa6041b.nk-qbank.pages.dev.

## Accessibility and evidence limits

- Several old Home and Insights captions render at about 8–10 px in phone
  captures. The flow cleanup reduces how much of that text must be scanned;
  contrast and text scaling still need a physical-device review.
- Screenshots show layout and visible hierarchy. They do not establish screen
  reader order, keyboard behavior, cloud sync, or physical Android acceptance.
- The capture used a fresh state. The saved-module card and long test histories
  require separate stateful review after this cleanup build.
