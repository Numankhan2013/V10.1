# Interaction quality pass — 2026-10-02

The user authorized recovering the previously excluded tap-latency candidate
and implementing restrained native-like interaction polish without changing
the app's layout, palette, navigation or study behavior.

## Audit and recovered work

The September 30 promotion explicitly excluded `b143242` and follow-ups.
The recovered performance changes index immutable bank questions by topic,
remove a redundant state clone/checkpoint normalization during durable saves,
and update timed-test answer selection after persistence without rebuilding
the question. Recovery preserves current source-answerability guards, rating
amendments, saved mocks, checkpoint recovery and failed-save rollback.

The phone/tablet baseline rebuilt the question for every CBT answer. Twelve
rapid changes measured about 12.4–12.5 ms median in local Chromium. The first
refined runs measured 3.6–4.2 ms across 320/390/820/1194px. These are local
browser measurements, not physical-device latency claims.

## Interaction system

- Immediate pointer-down press states for buttons, cards, links, answer options,
  navigation and disclosure controls. Pointer cancellation or a scrolling
  gesture releases the press; actions still use their existing click handlers.
- Immediate press tint and immediate release/selection state. The initial
  release/color transitions and content/sheet movement were removed after
  the user reported slower feel; reduced motion remains respected.
- Bookmark, CBT answer, FSRS grade and exam-review-mark edits update in place
  only after a successful durable commit. Question/source DOM, scroll position
  and rating controls remain mounted. A failed commit publishes neither the
  changed state nor success haptics.
- Same-question renders retain open explanations and scrolling; a different
  question starts at the top. Remove the duplicate legacy hash-route render.
- Sheets contain background scrolling and keyboard focus; closing restores
  the opener when it still exists. Existing Pause/Submit/dismissal behavior
  remains authoritative.
- Intentional feedback for committed answer outcomes, CBT selections, recall
  ratings, bookmarks/marks, Pause and completion. Ordinary navigation is silent;
  Practice emits one outcome rather than selection plus outcome vibrations.
- Android uses a deterministic bridge installed after Activity regeneration,
  honoring the user's touch feedback setting. Browser vibration is optional;
  unsupported platforms retain the visual states. No sound is added.

Owners: `question_interaction_core.js`, `apply_interaction_polish_v1.py`,
`interaction_polish_core.js`, `interaction_polish.css`, and
`apply_android_haptics_v1.py`. The final interaction owner follows result
analysis, before final syntax/package checks.

## Verification and remaining certification

The first actual-use pass and second refinement covered press cancellation,
correct answer → editable FSRS → next, bookmark/mark state, modal focus/scroll,
rapid CBT selections, reduced motion, failed writes and reload. Generated
browser regressions cover multi-chapter Pause/Home Continue, correction/rating
replay, study journey, results, named mocks and original-result preservation.

Local source tests and disposable-preview checks do not certify the APK.
Full exact-candidate Ubuntu generation/browser/PWA/package and Android phone/
tablet CI remain mandatory before main/production promotion. Physical haptic
feel and installation/data-preservation acceptance remain separate.

## Exact-candidate certification and main promotion

Product `a68e9c2d6e2b8f121b747c2aba53d9cc5ffeec75` passed full run
[36956370295](https://github.com/Numankhan2013/V10.1/actions/runs/36956370295)
on the first attempt, both Engineering gates and 87 local checks. Fresh hosted
phone/tablet checks passed at https://f1295420.nk-qbank.pages.dev. Actual module
topic taps and count/name typing also retained focus on phone/tablet.

Main was fast-forwarded to that exact product; PR83 includes merged PR82.
Main full run36957980864 is running for the official Android identity. Canonical
deployment remains pending and must use that successful verified main artifact.
Keep main fixed during the deployment workflow's artifact/current-main guard.

## User-reported responsiveness regression and correction

The user found the initial polish slower throughout the app, then asked for
subtler answer haptics. Canonical release was held. A frame-level A/B audit
found that a committed CBT selection still showed the old background/border
on its first frame, while the shared 110 ms transition animated seven CSS
properties. After correction, the committed, first-frame and settled colors
match immediately and no control transition remains. Press tint is immediate,
release is immediate, and the added question/page/sheet movement is removed.
The faster save/indexing and in-place updates remain intact.

Practice outcomes now use one brief7 ms correct /9 ms wrong browser pulse;
native answer outcomes use CLOCK_TICK, removing CONFIRM/REJECT/LONG_PRESS from
the repeated solving loop. Completion retains its separate feedback. The
native owner also updates an existing bridge idempotently. Verification now
checks actual first-frame appearance, press/release styles and gentle pulses,
rather than relying only on fast synchronous handler measurements.

All87 source/behavior/syntax checks pass. Generated first-frame/press/release/
rollback checks passed at320/390/820/1194px and reduced motion. Practice/CBT/
Review, genuine multi-chapter Pause/Home Continue and FSRS rating amendment/
sync/reload regressions passed. Full correction certification and canonical
deployment are pending.

The first correction's full build exposed an old submission timer: cleanup at
0/80/250 ms could close a newly opened Review navigator. Reproduced locally;
cleanup now checks the submitted exam's identity and leaves Review, Practice
and a later exam alone. Legacy sheet entrance motion is removed too. The
source regression checks all three session boundaries; the generated PYQ
journey checks the Review navigator survives the full250 ms timer window.
Local PYQ/mixed/history/Review/follow-up journeys pass phone/tablet. This is a
new candidate requiring fresh full certification, not a rerun of failedb918.

## 2026-10-18 press language v2 — no movement on press

The user reported that most buttons across the app (subject buttons, QBank
banks inside subjects, topic rows, the Home Prof expanders) "pushed back" when
tapped and asked for the fragility to be fixed app-wide without breaking any
animation or UI component.

Root cause: the tactile press layer. An `:active`/`.nk-pressed` transform
(scale .92–.995, spread across ~25 rule families plus the shared .98 polish
scale and a .94 nav shrink) moved every control on touch-down, and one Home
hover lift stuck after a tap on touch screens (a lingering `translateY(-1px)`
on subject cards and the UWorld card).

The fix removes every movement-based press state in
`app/src/main/assets/app.css`:

- the shared polish scale, the nav icon shrink, the answer-option scales, the
  Bookmark icon shrink, and every family scale (builder, session, insights,
  tests shelf, auth, notes, toast, chapter actions, topic map, …);
- the prof-band press scale (its comment now documents that the row answers
  with its expand animation only);
- the `.topic-session-btn:active` translate and the Home focus
  `translateY(0)` helper.

Kept, deliberately: the immediate `.nk-pressed` commit (class + haptics),
existing color-only press fills where the design already used them (builder
toggles and module topics keep the #f2f2f2 fill exactly as before — the
pattern the user liked on the bank-collapse control), the option press ring,
keyframes and reveal/expand animations. Nine ungated `:hover` lifts on Home,
Topics, Insights and the tests shelf are now wrapped in
`@media (hover: hover) and (pointer: fine)`, so touch taps never inherit a
stuck lift; desktop hover keeps its lift (verified via forced pseudo-state).

Contract tests updated: `tools/test_interaction_polish_v1.py` now asserts the
polish section has no transform transition and no non-`none` transform on
`:active`; `tools/verify_interaction_polish_browser.py` now asserts press
styles are `transform: none` in normal and reduced motion.

Verification (local Chromium against `build/web`): frame-by-frame real-touch
taps on subject card / Prof band / UWorld card / topic row / bank card are
pixel-identical from touch-down through release and 650 ms after (0 changed
pixels; previously the subject card and UWorld card kept a stuck 2901-pixel
shift). Computed-style press audit: no transform, rect, background, shadow or
border change and no residue for 14 controls. The interaction-polish browser
contract passes at 320/390/820/1194 + reduced motion; visual refinement passes
at 4 widths; `verify_local.py` reports 99 checks green. Physical-device feel
remains user-verified, not CI-proven.
