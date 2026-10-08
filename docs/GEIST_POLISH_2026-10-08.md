# Geist polish pass (2026-10-08)

Status: preview candidate on `feature/home-geist-polish-20261008`, stacked on the
Geist redesign preview (`feature/home-geist-redesign`, c92548dc). Presentation
only. Not accepted, not for main/production until the user approves it.

## Goal

Keep the approved Geist / Linear / shadcn direction and make it one coherent
production-quality system: audit → fix layout/hierarchy/state problems →
refine the system → integrate the approved prototype interactions
(`preview/easyui-ui-concepts`, `qbank-ui-preview.html`) in the QBank idiom.

## Files

- `redesign/nk-polish.css` — system layer after `nk-redesign.css`: type scale,
  page frame, card language, controls, neutral surfaces, dark-mode focus card,
  question screen, plus styles for the interaction layer.
- `redesign/nk-feel.js` — interaction layer, called by `nk-redesign.js` after
  every app render (`NKFeel.render(app, page, session)`). Idempotent; drives the
  app's own selects/buttons, never study logic or storage.
- `redesign/vendor/motion-12.23.12.min.js` — Motion (motion.dev, MIT): springs,
  keyframes, number tweens, `inView`. Entrance animations clear their inline
  styles when done (no lingering transforms that would trap fixed docks).
- Haptics: native Android bridge (`QBankHaptics`, existing kinds only) →
  Vibration API → the ios-haptics switch technique (tijn.dev, MIT) for iPad/iOS
  Safari. Licence copies are in `redesign/vendor/`.
- `index.html` gains three asset tags; `sw.js` precaches the three new files.

## Approved concepts → implementation

| # | Concept | In the app |
|---|---------|-----------|
| 01 | Home progress seg + stats | Range select becomes Today/Week/Month/Year seg with a sliding pill (FLIP across re-renders); figures count between values; delta chips vs the same point of the previous period, shown only when the recomputation matches the figure the app displays. |
| 02 | Insights controls | One bar: ghost chevrons, Week/Month/Year seg, range label, subject/bank dropdowns (listbox, keyboard, UWorld grouped). Year selector uses the same dropdown. |
| 03 | Questions chart + trend | Bars grow in on view/period change; tap readout styled. Trend redrawn from the app's own data as an ink spline + area, dashed previous series, peak label, scrub/hover tooltip (inverse card) with tick haptics, keyboard arrows, draw-in. |
| 05 | Topic tabs | Seg track with sliding pill; hairline rows; 4px ink accuracy bars; rows crossfade on tab change. |
| 06 | Donut | Semantic ring sweeps in on view (registered `--nkg-sweep` mask), centre counts up, legend staggers. |
| 07 | Count picker | 10/20/50/100 as one mono seg with sliding pill; availability figure ticks. |
| 10 | Quick-test source cards | Selected card takes the ink border + inverse check disc; others show an empty ring; press scale; selection haptic. |

## Reworked (not approved as drawn)

- **08 Period comparison.** Each row: label, `previous → current` (muted mono →
  bold mono), semantic delta chip, and a dumbbell track on one scale: hollow
  ○ previous, filled ● current, segment coloured by direction. Answer to the
  "what if this week regressed?" problem: weight encodes *recency* (the
  period under review is always the emphasised value), never goodness.
  Direction is carried by a separate channel — the red/green segment, which
  physically points left for a regression, and the chip. On reveal the ●
  slides from the previous value to the current one, so the change itself is
  what moves.
- **09 Forecast.** Insights, Revision and FSRS share one chart: today is the
  inverse column contained inside the chart box (it can no longer bleed over
  the title), any day is selectable by tap, drag-scrub (tick haptic per day)
  or arrow keys, with a live readout. Zero days are hairlines.
- **11 Streak.** Compact by default (one ~60px row: flame, count, week dots).
  Tapping expands current/longest/active days, progress to the next milestone
  (3/7/14/30/60/100/180/365) and the rule. The flame flickers slowly while a
  streak is alive; tier (1/3/7/14/30) deepens the tile; the day the streak
  grows plays one ignite + success haptic. No Rive: a .riv runtime and asset
  would add weight and motion beyond the restrained direction.
- **12 Heatmap.** Kept the relative-band ink scale; dense square cells that
  fill the card on wide screens (container-query sizing) and scroll to "now"
  on phones with an edge fade; floating date tooltip; one entrance wave per
  session for visible weeks; selection uses the focus ring.

Reference only (not integrated as designs): 04 bottom-nav variant; Cult/Origin
UI/shadcn/EasyUI/Dashboardcn components (React/Tailwind) — their interaction
ideas were re-expressed on the existing DOM.

## System audit fixes

- Page title owned by the page; the top bar shows the wordmark and reveals the
  page title only after it scrolls away; translucent bar on scroll.
- One type scale (title 28/30, section 17, body 15, meta 13/12); headings
  balance, long text uses `pretty` (question stems no longer break raggedly).
- One page frame: 16/24px gutters, 720px reading column (Insights 1080px).
- Neutral icon tiles everywhere (no tinted red/green/orange chips); colour only
  for meaning (mistakes, deltas, answer states, streak).
- Hero figures (22px+) in Geist Sans tabular; Geist Mono for small data
  (chips, axes, counts, pickers, comparisons).
- Dark mode: Today's focus is an elevated surface, not a light slab.
- Nav due badge sits on the icon; Revision actions are secondary buttons;
  answer options keep a fixed letter column across states; sync card inputs
  and kickers follow the system; secondary pages get quiet back links and
  sentence-case badges; empty subject rows collapse to one line.

## Verification (local, against the deployed Geist preview with local assets)

- 320/390/820/1280px, light and dark: Home, Insights, Revision, FSRS, Tests,
  More, Profile, My UWorld, bank chooser, Practice question. No horizontal
  overflow at 320px.
- Interaction script: Home seg, Insights seg + dropdown (keyboard), trend
  tooltip, forecast keyboard selection, heatmap tooltip, count picker, Practice
  answer; normal and reduced-motion; zero page errors/warnings.
- `python3 tools/verify_local.py`: 108 checks pass.
- Not done: full CI on this SHA, hosted preview review, physical Android/iPad
  check (native haptics feel, iOS switch haptic, WebView performance).
