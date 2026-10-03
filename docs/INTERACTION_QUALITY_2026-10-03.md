# Interaction quality — October 3, 2026

## Scope and Impeccable installation

User requested an interaction quality pass on the mature NK QBank, preserving
identity, architecture, question behavior, scoring, FSRS, history, modules,
storage, sync, navigation and good existing interactions. Function never waits
for animation. This work includes the separate analysis/PWA candidate; missed
practice stays in Test Analysis and is absent from Insights.

Official open-source Impeccable **skill-v4.5.0**, released October 2, is installed
from its published `universal.zip` into `.agents/skills/impeccable`. Its source
release is `pbakaus/impeccable` at `508d7e8`. The bundled launcher installs its
required engine separately in the user's cache. Codex project hooks are in
`.codex/hooks.json`, pointing to the single `.agents` installation rather than
keeping duplicate skill copies. `PRODUCT.md` is a symlink to canonical memory;
`DESIGN.md` records this restrained direction without forking product knowledge.

Used the actual `context` command, technical audit guidance, Operate guidance,
motion guidance, craft floor and polish playbook. Ran the deterministic detector
on the final generated HTML and inspected running browser captures. This API
session executes the detector explicitly; it does not claim the Codex UI has
approved automatic hooks. On a future Codex CLI session, use `/hooks` to see the
project hook's trust status. Skills do not become application runtime assets.

## Audit before editing

Browser screenshots and actual interactions covered Home, study library, Topics,
Revision, Tests, Insights, More, bookmarks, modules, module builder, Practice
answer/result and review grid at390px phone and820px tablet. Existing generated
regressions also cover CBT, result analysis, Review Solutions, source rendering,
saved mocks and builders. Captures/reports live under `build/interaction-audit`.

The incumbent system is coherent and product-specific. Fixed Previous/Next,
question-first reading, immediate state colors, correct/wrong differentiation,
durable transaction/rollback, in-place CBT/bookmark/rating edits, restrained press
feedback and silent question navigation are strengths to preserve.

| Audit dimension | Score /4 | Evidence |
| --- | --- | --- |
| Accessibility | 2 | Filter/mode replacements lose focus;365 heatmap day tab stops; several small controls. |
| Performance | 3 | In-place CBT/ratings already avoid rebuilding. Practice still replaces the complete question. |
| Responsive design | 3 | Phone/tablet screens fit; small common targets need improvement. |
| Theming | 3 | Existing coherent violet/semantic palette; legacy generated CSS contains unused styles. |
| Implementation integrity | 3 | Scoped deterministic owners and preserved study contracts; some local update paths replace too much DOM. |
| Total | 14 /20 | Good foundation with meaningful interaction defects. |

Priority findings:

- **P1:** Insights subject/time/scope filters replace their select controls and
  send focus to body. Keep the native pickers mounted and refresh dependent
  content immediately; keep the metrics disclosure and reading position.
- **P2:** Practice answer rendering replaces the question and its loaded figures.
  Retain those nodes and reveal only answer/support/footer changes after the
  existing durable save. Correctness must be visible synchronously.
- **P2:** Outcomes lean on color. Add plain Correct/Incorrect/Unattempted text
  with the correct answer letter, including accessible status feedback.
- **P2:** Topic/time/mode changes replace the focused button. Preserve focus and
  scroll on the corresponding new control without delaying the change.
- **P2:** Dense activity data has hundreds of keyboard stops. Keep its compact
  year overview with one tab stop, spatial arrow navigation and Enter activation.
- **P2:** Module menus/actions, Topic controls and Activity year/period controls
  fall below44px. Enlarge these actual controls without inflating data cells.

Static detector evidence is separate from these verified interaction findings.
It flags an old `.result-stat::before` stripe and a dark colored glow in the
generated archive, plus an advisory decorative stripe. These are not a reason
to restyle approved Home/streak or source material; selectors and live surfaces
take precedence. Dense heatmap cells deliberately remain compact and now gain
keyboard access. No universal minimum-target CSS is applied to chart data.

## Implementation stages

1. Extend the existing late interaction owner and durable question transaction
   paint callback. Keep the Practice question/figure/header/options container
   mounted; replace locked answer rows, append the existing study-support markup,
   mount the existing note editor and replace the existing footer/FSRS dock.
   Keyboard answering proceeds to recall/Next without scrolling. A failed save
   publishes neither the outcome nor its feedback.
2. Refresh Insights report data within its current surface, preserving native
   time/subject/bank pickers, app navigation, metrics disclosure and heatmap
   horizontal position. Local topic/time/year switches restore control focus and
   reading position. Heatmap arrows move focus only; Enter explicitly reads a day.
3. Apply scoped target-size, outcome-text, tabular-numeral and caret refinements
   in the existing CSS owner. No page choreography or new animation is added.

## Validation

Source checks, actual running responsive/touch/keyboard checks, ordered generated
CI, preview and Android phone/tablet certification are tracked in the canonical
handoff and pull request. Local patched rendering is supplementary; it is not a
substitute for a successful full generated/PDF/PWA/APK/Android run. Physical
haptic feel, installed upgrade preservation and user acceptance remain separate.
