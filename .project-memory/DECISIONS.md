# DECISIONS.md — Durable Technical / Product Decisions

Record the decision + why. Date/branch/commit where useful.

## 1. Keep the WebView monolith; no rewrite, no second shell (standing)

Rejected the V11 clean-foundation shell (duplicate nav, excess chrome,
replacement shell, lost question-first hierarchy). No wholesale native Compose
rewrite. Evolve component-by-component only. Basis: `memory.md` §3, Run 170
lesson (transformation restored old Home; fixed by restoring exact accepted
composition).

## 2. Candidate states are distinct (standing)

Implemented ≠ build-verified ≠ device-verified ≠ accepted baseline.
Only explicit user physical-device approval promotes a baseline. CI + static
checks are never sufficient. Basis: `docs/ENGINEERING_BASELINE.md`, Run 220
(`73c0428`, run `34011265432`).

## 3. Source visuals are frozen infrastructure (standing)

Native raster figures at native resolution, tight crops, lossless PNG display
cache (~420: Anatomy 297 / Physiology 62 / Biochemistry 51); original PDFs stay
authoritative; exact normalized stem matching; subject-specific PDFs only; no
fuzzy cross-subject assignment; no `Question N has image` heuristics; aspect
preserved; fullscreen zoom/pan protected. Do not alter during unrelated UI work.

## 4. Subject renderer isolation (standing)

Biochemistry known-good renderer stays isolated (no global replacement).
Physiology uses source-PDF tables/diagrams/graphs; never heuristically rebuild
flattened explanations into fake tables/bullets. Anatomy changes must come from
source inspection, not heuristics.

## 5. Session / Review protection (standing)

Final question → session-review navigator (answered/unanswered + jumping +
Submit/Finish); no persistent end-of-session toast; singleton transient toasts.
Review Solutions keeps one live engine: Previous/Next fixed footer (isolated
styling), grid/navigator, jump, End Review → originating analysis, source-PDF
explanations. Generic CSS must not clip the footer; no second navigator.

## 6. Home composition and streak ownership (V11 accepted)

One cohesive Home surface (not card stacks); Today’s Focus as command area;
Home-only streak below greeting (rectangular/chiseled, Home-axis aligned,
subtle motion OK); legacy global streak injector removed
(`v102-streak-layer*` must stay absent). Canonical `currentStreak()`/state
functions reused; no duplicate persistence. Header logo removal is Home-only.

## 7. Today’s Focus: permanent Practice-20 + conditional Review-Due (2026-09-06,
   `v11.4`, `9e6abc7`)

Kept `startAllSubjectPractice()` always visible (user direction) **and**
restored `${due? startLibrary('review') : ''}` (`Review N Due`) when due>0.
Rationale: prior toggle hid Practice-20 when due>0; the “always Practice”
follow-up hid the Review action the focus title promised and broke
`test_whole_app_vision_v1.py` (runs `34034905290`/`34034904068`/`34034791899`).
Fix preserves both markers, keeps 3-button layout when no due, switches to a
4-column `:has(>button:nth-child(4))` grid only when the 4th button exists;
older WebViews degrade to wrapped layout without breakage. Verified by run
`34043059869` (`WHOLE_APP_VISION_OK`) and user device confirmation.

## 8. Deterministic pipeline + syntax last (standing)

One owner script per transform; `verify_build_pipeline.py` enforces order and
single ownership; `fix_boot_syntax.py` + `node --check` run after **all**
transforms and again on packaged `assets/index.html`; packaged APK greps +
`verify_product_contract --stage packaged` + `verify_cbt_invariants` gate
release. Lesson from WebView syntax failures (transforms after the check) and
review-footer clipping.

## 9. Accurate progress semantics (V11.2, standing)

Subject stats use `SUBJECTS.flatMap` over all records; attempt history is
`state.attempts` (`qAttempts`), not `state.answers`; Topics completion is
attempted/total (all-wrong still counts as attempted); counts use numeric-safe
formatting (no `NaN Questions/Topics`); `BY_ID` unified across subjects.
Covered by `test_study_metrics.py`, `test_whole_app_vision_v1.py`.

## 10. Custom Study Modules reuse the Practice engine (V11.5, `f13d12f`)

Modules persist in `qbank_state_v1.studyModules` (filters, frozen IDs, answers,
timing, position, lifecycle, optional result ID); IDs frozen at creation and
never rebuilt by status changes; seeded shuffle (Mixed weighted
Wrong-heavy); cap at eligible count; dedupe by canonical ID; missing IDs
skipped. Sessions are normal Practice with `studyModuleId`; every save syncs
back; finish creates normal Practice Analysis; leave saves and returns Home;
restart clears progress but preserves frozen set + global history. Owned by
`apply_custom_study_modules_v1.py` before syntax validation; tested by
`test_custom_study_modules_v1.py`. See `docs/CUSTOM_STUDY_MODULES.md`.

## 11. Harness-agnostic memory (2026-09-06, this change)

`AGENTS.md` is the universal entry; `.project-memory/` holds operational truth
(`STATE` current, `ROADMAP` future, `DECISIONS` durable, `ARCHITECTURE` +
`PRODUCT` implementation/product, `SESSION_LOG` history). Harness files are
thin pointers only; no duplicated knowledge. Repo is source of truth; fix
memory on drift. `memory.md` + `docs/` preserved as background, not forked.
