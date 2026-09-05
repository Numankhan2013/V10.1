# NK QBank — Project Memory / Continuity

**Updated:** 2026-09-05  
**Baseline:** V11 / Run 184 (physically tested and accepted)  
**Repository:** `Numankhan2013/V10.1`  
**Active branch:** `v11-source-visuals`

## 1. Project goal

NK QBank is a personal Android medical QBank intended to become a dependable daily study tool. The priority is not version-number churn; the priority is making every existing study interaction better while preserving working behavior.

**Motto:** **We do not break anything while we build something.**

Engineering loop:

> Inspect → implement → build → verify → fix → rebuild → verify again.

Physical Android-device behavior is the final authority. Never hand over an APK merely because source checks pass; the packaged APK must pass verification first.

## 2. Trusted baseline — Run 184

Run 184 is the current accepted behavioral/UI baseline.

Confirmed working on device:
- Practice sessions.
- Timed CBT sessions.
- Last-question boundary behavior: pressing Next on the final question opens the session-review grid instead of showing a persistent “End of session reached.” message.
- Session-review grid with answered/unanswered state and question jumping.
- Finish/Submit flow for practice and timed CBT.
- Test Review / review-solutions flow.
- Previous/Next navigation in review solutions.
- Home V8 / V4 cohesive dashboard.
- Topics V2.
- Tests page.
- Insights page.
- More page.
- Subject navigation and scroll reset.
- Persistence/state behavior already present in the baseline.
- Source-visual rendering with high-quality cropped native raster assets.

Run 184 was physically tested and accepted for both Practice and Timed CBT.

## 3. Source Visual Renderer — frozen foundation

This is effectively complete and must not be casually altered.

Original subject PDFs remain source of truth. Embedded raster figures are extracted at native resolution, tightly cropped to meaningful figure content, and stored as lossless PNG display assets. The app renders these assets without adding lossy intermediate processing. Source-PDF rendering remains available as fallback.

Current coverage:
- Anatomy: 297 mapped questions.
- Physiology: 62 mapped questions.
- Biochemistry: 51 mapped questions.
- 420 source-visual PNGs are retained in the packaged APK.

Important rules:
- Exact normalized question-stem matching; no fuzzy cross-subject image assignment.
- Subject-specific PDFs only.
- No heuristic “Question N has image” logic.
- Preserve aspect ratio and medically meaningful content.
- Full-screen image viewer with zoom/pan remains working.
- Do not redesign or replace this pipeline while working on unrelated UI.

## 4. Home / navigation foundation

Home V8 is accepted.

Home principles:
- Cohesive application surface rather than a pile of floating cards.
- Compact identity/header.
- Today’s Focus command area.
- Subjects as central study-library rows.
- Progress snapshot.
- Quick access.
- Performance/recent sections.

Topics V2 is accepted:
- Compact subject switcher.
- Search/filter controls.
- Topic counts/progress.
- Direct chapter opening.
- Unified subject navigation.

Legacy global streak injector is removed. Streak belongs on Home only.

Do not revert to the rejected V11 shell/Figma redesign that introduced duplicate navigation and excessive chrome.

## 5. CBT / review architecture

The current system has a reusable question navigator/session-review grid used during active sessions.

Current session-review behavior:
- Final question → review grid.
- Grid shows answered/unanswered state.
- User can jump to any question.
- User can review unanswered questions.
- User can Finish Session / Submit Test.

Current review-solutions behavior:
- Completed test opens a review session.
- Previous/Next are fixed and functional.
- Review footer is hardened against the earlier WebView/CSS positioning bug.
- The review renderer must remain isolated from generic footer CSS.

### Immediate next addition

**Add the question grid to Review Solutions itself.**

Desired behavior:
- While viewing a completed test’s review solution, a clear grid/navigator control is present in the review header.
- Tapping it opens the existing question navigator.
- User can jump directly to any reviewed question.
- Reuse the existing navigator rather than creating a second grid implementation.
- Preserve Previous/Next and all current review behavior.

A build-time patch has been added as `tools/add_review_solution_grid.py` and the workflow now runs it after the review-footer hardening step.

## 6. Current workflow hardening

`.github/workflows/build-apk.yml` now performs, in order:
1. Existing source/CBT/UI transformations.
2. Home V4/V5 transformations.
3. Legacy streak removal.
4. CBT end-of-session review/toast fix.
5. CBT review footer hardening.
6. Review Solutions question-grid patch.
7. WebView boot-syntax repair after all transformations.
8. Final inline-JavaScript syntax validation.
9. CBT regression guardrails.
10. Final generated-app checks.
11. Gradle APK build.
12. Packaged APK verification.
13. Artifact upload.

Packaged verification must include:
- Home V8/V4 markers.
- Topics V2 markers.
- Subject navigation/scroll reset.
- No legacy streak injector.
- CBT session-review and fixed review-footer markers.
- Review Solutions grid markers.
- Valid packaged inline JavaScript.
- At least 400 source-visual PNGs (expected current total: 420).
- APK ZIP integrity.

## 7. Known historical failures — do not repeat

### Failed V11 shell
A clean V11 foundation build was rejected because it replaced the compact V10.3.x question-first architecture with duplicate navigation/excessive chrome. Do not revive that approach.

### Run 170 regression
A later build reverted to the old Home UI. The recovery was to restore the exact accepted Home V8 baseline rather than recreate it approximately.

### WebView boot failures
Home V8 transformations once introduced malformed inline JavaScript after an earlier syntax check. Therefore syntax repair/check must happen after every transformation, and the packaged APK must be checked too.

### Review footer regression
Generic CSS caused Previous/Next in Test Review to appear clipped/misaligned. The fix isolated the review footer and anchored it correctly. Run 184 confirmed Practice and Timed CBT review navigation works.

### Persistent toast regression
“End of session reached.” once stacked and persisted. The boundary logic now opens the review grid and uses a singleton transient toast system.

## 8. Next roadmap

### Phase 1 — Review Experience
1. Review Solutions question grid — **current task**.
2. Make review navigation consistent across Practice Review, CBT Review, and Test Review.
3. Improve review-state indicators without overloading the grid.

### Phase 2 — Gold-standard Question Screen
Polish typography, spacing, option states, explanation hierarchy, source solution placement, long explanations, image/text relationships, and sticky navigation without changing the question engine unnecessarily.

### Phase 3 — Daily Study Loop
Make Home → study → review → continue feel intelligent and actionable. Improve Continue, Wrong Questions, Due Review, Bookmarks, and unfinished-session recovery incrementally.

### Phase 4 — Study Intelligence
Build robust Wrong Questions, persistent Bookmarks, then a restrained Spaced Review foundation.

### Phase 5 — Analytics
Turn Insights into decisions: weak chapters, accuracy trends, question volume, study time, and prioritized next actions.

### Phase 6 — Test System
Expand test configuration and history only after Practice/Review are stable: topic selection, question count, timing, results, unanswered review, and detailed analysis.

### Phase 7 — Engineering Hardening
Add golden/screenshot regression coverage for Home, Topics, question screen, image questions, long explanations, Practice, CBT, Review, Review Grid, Insights, etc. Gradually improve state/data separation using principles learned from Now in Android without wholesale architectural replacement.

### Phase 8 — Final Visual Refinement
Only after functionality is stable: spacing rhythm, typography, icon consistency, borders, radii, shadows, transitions, empty states, accessibility, and adaptive layouts.

## 9. Architectural direction

Do not perform a wholesale rewrite.

Use principles incrementally:
- single source of truth for study state;
- unidirectional data/state flow where practical;
- small reusable UI components;
- isolated feature responsibilities;
- shared core utilities;
- screenshot/golden regression testing;
- adaptive layouts.

Potential long-term organization:

```text
app
├── core
│   ├── question-engine
│   ├── source-visuals
│   ├── persistence
│   ├── analytics
│   └── ui
└── features
    ├── home
    ├── practice
    ├── timed-test
    ├── review
    ├── analysis
    ├── bookmarks
    └── spaced-repetition
```

This is a direction, not an instruction to modularize immediately.

## 10. User preference / working style

The user wants **more building and less narrating**. Prefer executing the next safe step over lengthy discussion. When a build is requested, inspect the source, implement narrowly, build, verify, and report the concrete result.

Do not give an APK until the packaged artifact has passed the established verification gates.

## 11. Golden rule for future changes

> **Build forward from what already works; never make the user pay for a new feature with a regression in an old one.**

Every new feature should be:
- narrowly scoped;
- deterministic;
- build-time owned by one script where appropriate;
- guarded by regression checks;
- physically tested before becoming the new baseline.
