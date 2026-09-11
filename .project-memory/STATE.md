# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Accepted product commit: `125d68b`.
- Accepted baseline remains V11.6 Content Quality; later candidates are not accepted production unless the user explicitly promotes them.
- Current Marrow image integration lineage is `feature/marrow-image-rollout-current`; resolve live HEAD from Git.
- Build-verified ≠ device-verified ≠ accepted baseline.

## Current Marrow bank

Shared architecture remains `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`, using one Practice/CBT/Review/FSRS/sync/module/analytics/navigation engine.

Supplied ED8 scope:
- Anatomy: 819 questions / 48 topics.
- Biochemistry: 543 / 26.
- Physiology: 753 / 33.
- Total: 2,115 questions / 107 topics.

Raw imported source is authoritative and immutable. Source bundles remain manifest/hash validated.

## Explanation-quality phase

Current deterministic inventory remains 429 enhanced / 1,686 pending: Anatomy 62 approved reference, Biochemistry 259 through Chapters 1–11, Physiology 108 through Chapter 5. Image integration remains a separate workstream.

## Marrow image coverage — authoritative status

Physical learner review on 2026-09-11 proved the earlier Biochemistry image-completeness claim wrong. Registry asset counts describe only reviewed/staged work and are never a subject-completeness denominator.

Coverage repair is incorporated into the image lineage. The current candidate Biochemistry coverage is:
- raw source visual references: **95**;
- effective learner visual references: **94**;
- released source visual references: **66**;
- exact invalid-source-metadata references: **1**;
- resolved source visual references: **67**;
- tracked but unreleased: **4**;
- untracked: **24**;
- text-cue review items: **31**.

Physiology remains paused at 218 raw references / 42 released / 22 tracked-unreleased / 154 untracked / 27 text-cue items.

The source-derived audit plus `tools/marrow_image_coverage.py` is the completion gate. A bounded batch may be COMPLETE while a subject remains INCOMPLETE.

## Latest image recovery batch — VERIFIED_HISTORY

Classification: **VERIFIED_HISTORY / COMPLETE bounded coverage-recovery batch**. This batch no longer owns the shared writer lane.

- Subject: Biochemistry.
- Batch: `NKQ_BIOCHEM_COVERAGE_Q13_20260911`.
- Candidate branch: `automation/marrow-images-biochemistry-NKQ_BIOCHEM_COVERAGE_Q13_20260911`.
- Exact integration base: `c9b5930b7ffdbc9af7a1edcc5acc829ad96e79c3`.
- Released reference candidate: `marrow__BIOCHEM_CH02_Q013:figure:1`, explanation role, Marrow ED8 Biochemistry page 35 / xref 1126 / region `[162,453,450,669]`.
- The authoritative page places this glycolysis pathway immediately after the Q13 solution and before Solution to Question 14.
- Reused the already source-compared PASS glycolysis reconstruction `biochemistry-aa11f9fa6a08baea` / production SHA-256 `e6b4d76fa9ff07dbf62b5094b8fdcd46a744837bb802aa55945ac7021f6fa8e2`; no new medical or diagram content was invented.
- Source/reference validation, release regeneration, progress check, coverage check, image tests, coverage tests, pipeline verification, project-memory verification and `git diff --check` passed in bounded recovery run `34623825459`.
- Temporary generated coverage output and Python bytecode were removed; `.gitignore` now excludes `__pycache__/` and `*.pyc`.
- Post-batch candidate coverage: **95 raw / 94 effective / 66 released / 1 invalid metadata / 67 resolved / 4 tracked-unreleased / 24 untracked / 31 text-cue items**. Subject remains **INCOMPLETE**.
- Exact certified product candidate: `363084ba5c7f302774617863f383652706a22b89`.
- Exact-head Engineering Gate `34624402159` **SUCCESS**.
- Exact-head full Android/PWA/package run `34624404224` **SUCCESS**.
- Production promotion was skipped; `main` was not changed.

Exact next deterministic unresolved source reference after this candidate: `marrow__BIOCHEM_CH01_Q004:figure:1 (explanation, source pages [12], status UNTRACKED_SOURCE_VISUAL)`.

## Coverage and trust rules

A subject may be called learner-image complete only when:
1. every legitimate source visual has a released PASS/SOURCE_LIMITED binding;
2. every invalid source reference has exact evidence-backed adjudication rather than substitution;
3. question/explanation roles and multi-figure order are separately covered;
4. the text-cue backlog is cleared;
5. `marrow_image_coverage.py --subject SUBJECT --require-complete --check` passes;
6. normal image QA/browser/PWA/APK gates and memory handoff pass.

Rejected wrong candidates do not resolve legitimate visuals. Never use approved asset count as a completeness denominator.

## Automation state

- Biochemistry remains the active coverage-recovery subject and is **INCOMPLETE**.
- Physiology image automation remains paused so the old discovery defect is not propagated.
- Recovery proceeds in deterministic source-reference order; complex/vector/zero-native references cannot be skipped for easier JPEGs.
- No image batch currently owns the writer lane after the verified Q13 handoff is incorporated.
- The next deterministic unresolved source reference is `marrow__BIOCHEM_CH01_Q004:figure:1 (explanation, source pages [12], status UNTRACKED_SOURCE_VISUAL)`.

## Known problems / verification cautions

- Biochemistry still has 28 legitimate source references not learner-facing (4 tracked-unreleased + 24 untracked), plus 31 text-cue items requiring adjudication.
- User-confirmed missing visuals in Chapters 18–22 remain outstanding and are not exhausted by the listed examples.
- Complex/vector/page-content figures may require native vector extraction, precise region rendering, or source-faithful reconstruction; medical pixels must remain authentic.
- Question-time and explanation-time visuals can both exist for one question and both must be represented with correct timing.
- Ch25 Q26 CRISPR remains REVIEW_REQUIRED because tiny labels cannot yet be verified faithfully.

## Next step

1. Fast-forward only `feature/marrow-image-rollout-current` to this verified handoff if its live head still equals exact base `c9b5930b7ffdbc9af7a1edcc5acc829ad96e79c3`; never force, merge `main`, or promote production.
2. Start the next bounded Biochemistry recovery batch at `marrow__BIOCHEM_CH01_Q004:figure:1 (explanation, source pages [12], status UNTRACKED_SOURCE_VISUAL)`.
3. Keep Biochemistry subject status INCOMPLETE until the full coverage gate passes.
