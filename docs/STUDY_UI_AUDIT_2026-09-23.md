# Study UI audit — 2026-09-23

## Evidence and scope

The generated learner app was captured at 320×640, 390×844, 390×844 with a
150% browser text-size simulation, and 820×1180. Each screenshot is a current
run artifact, not a mockup. Baseline: [run 35821738540](https://github.com/Numankhan2013/V10.1/actions/runs/35821738540), artifact `study-ui-audit`. The first corrected capture is [run 35822409845](https://github.com/Numankhan2013/V10.1/actions/runs/35822409845). Each report includes screenshot names, viewport, horizontal overflow, selected control bounds, and JavaScript errors. A later capture adds the Marrow Q23 microscopy image, fullscreen viewer and post-answer explanation; resolve its exact run from the current canonical SHA.

The baseline had zero page errors and zero document-level horizontal overflow in
all 68 screenshots. Those measurements did not rule out clipping inside a
component. The screenshots exposed the defects below.

## Walkthrough

Health refers to the corrected browser capture. The same numbered screenshot
names are emitted for each viewport in the `study-ui-audit` artifact.

| Step | Screen or action | Health and finding |
| --- | --- | --- |
| 01 | Home | Working; primary study actions and bottom navigation visible. |
| 01b | Subject card destination | Working; current Home card opens the preferred bank's Topics directly. |
| 02 | Topics | Working; list, filters and continuation tray visible. |
| 03 | Chapter library | Working; question list and entry visible. |
| 04 | Unanswered Practice question | The subject and chapter context bar has been removed; question content starts higher on the screen. |
| 05 | Answer feedback | Working; chosen wrong and correct choices have distinct text/color states. |
| 06 | Long explanation | Working; structured explanation scrolls beneath the fixed footer. |
| 07 | Explanation bottom | Working; final explanation content remains reachable. |
| 08 | Final Practice grid | Working; Pause and Submit are visible for the one-question fixture. |
| 09 | Practice Analysis | Fixed: date, title and Review Solutions have separate space on phones. |
| 10 | Review Solutions | Working; saved answer and correct answer visible. |
| 11 | Review grid | Working; End Review visible, no blocking stale sheet. |
| 12 | FSRS | Working; subject choices and due-state copy visible. |
| 13 | Tests | Working; setup route visible. |
| 14 | Timed CBT question | Working; timer and options visible. |
| 15 | CBT selection | Working; selection remains distinct from final scoring. |
| 16 | CBT final grid | Fixed: cells now show session positions 1–20; four columns keep status labels within cells at 320px. |
| 17 | CBT Analysis | Working; Submit Test reaches Analysis with one attempted and 19 unanswered. |
| 18 | Marrow image question | Capture added; inspect exact final artifact for image pixels and layout. |
| 19 | Fullscreen image viewer | Capture added; inspect exact final artifact for viewer and close control. |
| 20 | Image explanation | Capture added; inspect exact final artifact for explanation figure and scrolling. |

## Defects fixed in the first batch

| Finding | Baseline evidence | Change | Corrected evidence |
| --- | --- | --- | --- |
| The CBT grid showed source question numbers in random order even though its cells navigate by session position. | `small-phone-16-cbt-grid.png`, `tablet-16-cbt-grid.png` | Display and announce `i+1`; use four columns below 361px and slightly larger status text. | Same names in the corrected artifact; 1–20 in order, status inside each cell. |
| A long chapter title occupied space above the question and added no study value. | `small-phone-04-question.png`, `large-text-phone-04-question.png` | Remove the subject/chapter context bar from shared Practice, CBT and Review question cards. | The updated capture asserts no context bar is rendered and shows the question higher on screen. |
| The Analysis date and heading were squeezed beside Review Solutions on phones. | `phone-09-analysis.png`, `large-text-phone-09-analysis.png` | Stack header text and action below 481px. | Same names in corrected artifact; date and heading fit. |

The capture regression asserts session-position numbering, status-label bounds,
absence of the subject/chapter context bar, and successful CBT submission from the grid. The
existing Continue Practice, CBT, Review, FSRS, browser, packaged APK and Android
emulator checks remain required on the exact final SHA.

## Evidence limits

The larger-text viewport is a browser CSS simulation, not Android's system font
setting. Screenshots cannot establish screen-reader announcements, keyboard
focus order or measured color contrast. The user's brief preview check covered
the visible study flows but did not establish a prolonged stress test. This
Termux session could not inject Android input or capture a physical device
screen. An in-place installation of the canonical APK, old-data preservation,
force-close/reopen and cross-device sync still require a real-device check;
preview review alone does not establish those results.
