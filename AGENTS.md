# AGENTS.md — Universal Agent Entry Point (NK QBank)

This file is the **single entry point for all coding agents and harnesses**
(Codex, OpenCode, Claude Code, Cursor, Copilot, plain CLI, etc.).
Harness-specific files, if they exist, must be **thin adapters that point here**.
Do not duplicate project knowledge in harness-specific files.

## Canonical memory

- Operational handoff: `.project-memory/STATE.md` (read first, keep current)
- Product goals: `.project-memory/PRODUCT.md`
- Architecture: `.project-memory/ARCHITECTURE.md`
- Decisions: `.project-memory/DECISIONS.md`
- Roadmap: `.project-memory/ROADMAP.md`
- History: `.project-memory/SESSION_LOG.md`

Preserved legacy references (do not delete, do not fork knowledge from them):

- `memory.md` — long-form continuity note; accepted Run 220 baseline and
  refinement phases. `STATE.md` is the current handoff; `memory.md` remains
  background until explicitly migrated.
- `docs/ENGINEERING_BASELINE.md`, `docs/STUDY_CLARITY.md`,
  `docs/V11_SOURCE_VISUALS.md`, `docs/CUSTOM_STUDY_MODULES.md`
- `design-qa.md` — V11.4 visual QA scope (physical-device checks blocked in CI)
- `README.md` — build and baseline summary

If `.project-memory/` disagrees with the repository, **the repository wins**.
Fix the memory file in the same change when you notice drift.

## Session start (required before substantial changes)

1. Read `AGENTS.md` (this file) and `.project-memory/STATE.md`.
2. Read `PRODUCT.md` + `ARCHITECTURE.md` for the area you will touch;
   consult `ROADMAP.md` / `DECISIONS.md` / `SESSION_LOG.md` as needed.
3. Inspect actual repo state — do not rely on memory alone:
   `git status --short --branch`, `git log --oneline -10`,
   `git branch --show-current`, relevant files under `app/`, `tools/`,
   `.github/workflows/`, `docs/`.
4. Reconstruct context (active branch, last CI result, what is
   build-verified vs device-verified vs accepted baseline) before editing.

## Session end (required after substantial work)

1. Update `.project-memory/STATE.md` so a new agent with zero history can
   continue: what changed, what currently works, known problems,
   unfinished work, logical next step. Keep it concise and current.
2. Append history to `.project-memory/SESSION_LOG.md`; move durable
   reasoning to `DECISIONS.md` and future work to `ROADMAP.md`.
3. Update `ARCHITECTURE.md` / `PRODUCT.md` only if the implementation
   actually changed.
4. Never turn `STATE.md` into an ever-growing log.

## Working rules (NK QBank)

- Motto: **we do not break anything while we build something**.
- Core study flows are complete; work is refinement, polish, and hardening.
- One narrow, deterministic change per milestone; one owner script per
  build-time transformation.
- Protected: Practice, Timed CBT, session review + navigator, Review
  Solutions + grid + Previous/Next + End Review, persistence, Home/Topics/
  Tests/Insights/More + subject switching, source-faithful renderers,
  source visuals + fullscreen zoom/pan, offline WebView operation.
- Do not revive the rejected duplicate-navigation V11 shell; do not do a
  wholesale native Compose rewrite; do not touch source visuals casually;
  keep Biochemistry isolated; keep Physiology source-PDF authoritative.
- Build order matters: `tools/verify_build_pipeline.py` enforces it;
  `tools/fix_boot_syntax.py` + inline-JS `node --check` must run after all
  transforms; packaged `assets/index.html` must also be checked.
- Labels are not interchangeable: **build-verified** (CI+packaged checks pass)
  ≠ **device-verified** (installed on physical Android) ≠ **accepted baseline**
  (explicit user approval). Never claim physical testing the user did not confirm.
- Prefer building over narrating; verify by execution (`python3`, `node --check`,
  `gh run view`, artifact inspection) where possible.

## File map (verified 2026-09-06, branch `v11.5-custom-study-modules`)

- `app/src/main/assets/index.html` — monolithic WebView app (source ~6 MB on
  V11 branches; 1.9 MB on stale `main`)
- `app/src/main/assets/*.pdf` — Anatomy / Biochemistry / Physiology sources
- `app/src/main/assets/source_visuals/` — ~420 lossless PNG display cache
- `app/src/main/assets/source_visual_metadata.js`,
  `source_visual_renderer.js`, `subjects_qbank_data.js`
- `tools/` — 55 deterministic transform/test/verify scripts; order enforced by
  `tools/verify_build_pipeline.py`; contracts by
  `tools/verify_product_contract.py` and `tools/verify_cbt_invariants.py`
- `.github/workflows/build-apk.yml` — deterministic APK pipeline
  (GitHub display name `Build V10.1 APK`); `engineering-gate.yml` — fast contract gate
- `data/subjects_qbank_lzma.b64.part*` — bundled subject data parts

## Harness adapters (thin only)

If you add `CLAUDE.md`, `.cursorrules`, `.opencode/*`, Codex config, etc.,
each file must contain only a pointer such as:

> Read `AGENTS.md` and `.project-memory/STATE.md` first; canonical memory lives
> in `.project-memory/`; the repository is the source of truth.

Do not copy product/architecture/roadmap content into adapters.
