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

## Latest image recovery batch — CURRENT_UNVERIFIED

Classification: **CURRENT_UNVERIFIED / source-validated bounded coverage-recovery batch**. This branch owns the writer lane until exact-head canonical CI finishes or the batch is safely retired.

- Subject: Biochemistry.
- Batch: `NKQ_BIOCHEM_COVERAGE_Q4_20260911`.
- Candidate branch: `automation/marrow-images-biochemistry-NKQ_BIOCHEM_COVERAGE_Q4_20260911`.
- Exact integration base: `3bc5229c573e304f1216c054457697eff6a78121`.
- Released reference: `marrow__BIOCHEM_CH01_Q004:figure:1`, explanation role, Marrow ED8 Biochemistry page 12 / xref 25 / region `[162,433,450,649]`.
- Production is the source-faithful 300-DPI exact-region render, SHA-256 `400546eaace6e3f0a2ec793f528c94722a8d2c2896f304e08cbd652277fdb03f`, 1200×901.
- Source inspection verified both Fischer projections and all stereochemical H/OH placements against the authoritative full page; no reconstruction or medical-image processing was used.
- Post-batch candidate coverage: **95 raw / 94 effective / 67 released / 1 invalid metadata / 68 resolved / 4 tracked-unreleased / 23 untracked / 31 text-cue items**. Subject remains **INCOMPLETE**.
- Exact-head Engineering Gate and full Android/PWA/package verification are pending on this clean candidate. Production promotion remains forbidden.

Exact next deterministic unresolved source reference after this candidate: `marrow__BIOCHEM_CH02_Q006:figure:1` (explanation, source pages [31], status UNTRACKED_SOURCE_VISUAL).

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
- `NKQ_BIOCHEM_COVERAGE_Q4_20260911` is CURRENT_UNVERIFIED and owns the writer lane until exact-head CI completes or it is safely retired.
- The next deterministic unresolved source reference after this candidate is `marrow__BIOCHEM_CH02_Q006:figure:1` (explanation, source pages [31], status UNTRACKED_SOURCE_VISUAL).

## Known problems / verification cautions

- Biochemistry still has 28 legitimate source references not learner-facing (4 tracked-unreleased + 24 untracked), plus 31 text-cue items requiring adjudication.
- User-confirmed missing visuals in Chapters 18–22 remain outstanding and are not exhausted by the listed examples.
- Complex/vector/page-content figures may require native vector extraction, precise region rendering, or source-faithful reconstruction; medical pixels must remain authentic.
- Question-time and explanation-time visuals can both exist for one question and both must be represented with correct timing.
- Ch25 Q26 CRISPR remains REVIEW_REQUIRED because tiny labels cannot yet be verified faithfully.

## Next step

1. Finish exact-head Engineering Gate and full Android/PWA/package verification for `NKQ_BIOCHEM_COVERAGE_Q4_20260911`.
2. If both pass, record the exact verified candidate/run IDs, retire this batch to VERIFIED_HISTORY, and fast-forward only `feature/marrow-image-rollout-current`; never `main` or production.
3. The following bounded recovery batch must start at `marrow__BIOCHEM_CH02_Q006:figure:1` (explanation, source pages [31], status UNTRACKED_SOURCE_VISUAL).
