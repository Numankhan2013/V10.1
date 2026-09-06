# ROADMAP.md — Planned Work and Priorities

Source: `memory.md` refinement phases R1–R9 + V11.5 docs + current handoff.
Check off only when build-verified **and** device-verified where UI is involved.
`STATE.md` holds the immediate next step.

## Immediate (next 1–2 sessions)

- [ ] Physical-device test of V11.5 APK from runs `34049523411` / `34049637559`
      (Home, Topics, Modules create/resume/finish/restart, Practice/CBT/Review,
      Insights, source visuals, safe-area). Promote to accepted baseline only on
      explicit user approval; record run ID + commit in `STATE.md` + log.
- [ ] Adopt this memory system across harnesses: verify a fresh Codex/OpenCode/
      Claude session can reconstruct context from `AGENTS.md` + `STATE.md` +
      `git`; fix drift immediately.

## R1 — Gold-standard Question Screen (highest priority per `memory.md`)

Refine typography rhythm, stem density, option spacing, selected/correct/wrong
states, bookmark/grid affordances, explanation hierarchy, source-visual
placement, long-explanation behavior, image/text relationship, sticky
Previous/Next, mobile readability, noise reduction. Preserve wording and source
renderers; use before/after screenshots; narrow scope per change.

## R2 — Home polish

Three-action + Review-Due hierarchy, streak geometry, spacing rhythm, section
alignment, subject rows, progress indicators, empty states, responsive +
reduced-motion behavior. Keep current Home architecture.

## R3 — Review consistency

Unify Practice/CBT/Test Review: header hierarchy, grid language, navigation,
state indicators, explanation surface; no duplicate implementations.

## R4 — Daily Study Loop

`Home → Continue/Practice → Review → Return Home` frictionless; Continue
Practice, unfinished recovery, Wrong/Due/Bookmarks, post-session next action.
No over-automation or Home clutter.

## R5 — Study Intelligence

Robust Wrong, persistent Bookmarks, restrained spaced-review foundation,
actionable weak-topic signals. Prioritization over gamification. V11.5 modules
are the reusable-set primitive — build on them, do not fork a second system.

## R6 — Insights / Analytics

Answer: weak at? study next? how much done? accuracy improving? time wasted?
Actionable summaries over decorative graphs; keep no-evidence vs poor
performance distinct.

## R7 — Test System refinement

Builder clarity, topic selection, counts, timing, history, results, unanswered
review, analysis — after Review stability.

## R8 — Engineering hardening

Golden/screenshot checks (Home, Topics, question, image-Q, long explanation,
Practice, CBT, Review, grid, Insights), state/data separation increments,
backup/restore + schema validation (after inspecting persistence), contract
coverage without calling static markers regression-proof.

## R9 — Final visual system

Spacing/typography tokens, icon consistency, border/radius discipline, shadow
discipline, transitions, accessibility, adaptive/tablet — only after behavior
is stable.

## Explicitly deferred

- Native Compose rewrite; second navigation/shell; global renderer rewrites.
- Heuristic Physiology explanation reconstruction.
- Re-cropping medically meaningful source content.
- Copying competitor medical content (reference links are workflow-only).
