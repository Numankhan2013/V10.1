# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Accepted product commit: `125d68b`.
- Accepted baseline remains V11.6 Content Quality; later candidates are not accepted production unless the user explicitly promotes them.
- Current Marrow image integration lineage is `feature/marrow-image-rollout-current`; resolve live HEAD from Git.
- Repair work for the image-coverage defect is on `automation/marrow-image-coverage-repair-20260911`; this branch is not production and must not merge to `main` automatically.
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

Canonical procedure: `docs/MARROW_EXPLANATION_FINE_TUNING.md` + `docs/MARROW_BANK_INTEGRATION.md`.

Current deterministic inventory remains:
- 429 enhanced / 1,686 pending.
- Anatomy approved reference: 62.
- Biochemistry enhanced: 259; Chapters 1–11 complete on its explanation lineage.
- Physiology enhanced: 108 through Chapter 5.

Image integration remains separate from explanation refinement.

## Marrow image coverage incident — authoritative current status

Physical learner review on 2026-09-11 proved the previous Biochemistry image-completeness claim was wrong.

Root cause:
- the image registry only counts assets/bindings already staged for review;
- `stage_marrow_image_review.py` preferentially stages exactly-one-candidate native JPEG cases and skips complex/vector/multi-candidate/zero-native-candidate references;
- therefore “60 approved Biochemistry assets / 60 released questions” described only the reviewed subset and was never evidence of full source coverage.

Authoritative CI audit on repair PR #38 / Engineering Gate run `34617043711` measured:
- **Biochemistry:** 95 source-recorded visual references across 89 questions; **65 released**, **5 tracked but unreleased**, **25 untracked**; plus **31 additional text-cue review items**.
- **Physiology:** 218 source-recorded visual references across 172 questions; **42 released**, **22 tracked but unreleased**, **154 untracked**; plus **27 additional text-cue review items**.

Repeated figures may reuse one asset, so reference counts are not unique-asset counts. The key trust metric is learner-facing source-reference coverage, not number of approved registry assets.

Confirmed learner omissions include source-recorded visuals in Chapters 18–22. Examples independently confirmed from the digitized source records:
- Ch18 Q3/Q5/Q6: explanation flowchart for enzyme non-protein components;
- Ch19 Q2: question-critical reversible-reaction schematic;
- Ch19 Q11: both a question-time enzyme-kinetics graph and an explanation-time inhibition graph.

These are not low-quality-source excuses; they expose a discovery/coverage gap.

## Image coverage repair

New repair components on `automation/marrow-image-coverage-repair-20260911`:
- `tools/marrow_image_coverage.py` — source-reference coverage auditor. It uses the source-derived audit as denominator and reports RELEASED, UNRELEASED_TRACKED, and UNTRACKED_SOURCE_VISUAL per reference plus text-cue review backlog.
- `tools/test_marrow_image_coverage.py` — regression coverage including one-to-one matching so one registry binding cannot satisfy multiple source references.
- `docs/MARROW_IMAGE_COVERAGE_GATE.md` — durable rule: bounded batch completion is not subject completion.
- Engineering Gate runs the regression and computes authoritative Biochemistry/Physiology source coverage after `marrow_images.py audit`.
- Repair PR #38 Engineering Gate `34617043711` passed all steps, including project-memory validation, existing image-registry tests, new coverage regression, authoritative PDF audit, explanation/taxonomy tests and build-pipeline verification.

A subject must never be called learner-image complete unless:
1. every source-recorded visual reference has a released PASS/SOURCE_LIMITED binding;
2. question-time and explanation-time roles are separately covered;
3. the text-cue backlog is cleared;
4. `python3 tools/marrow_image_coverage.py --subject SUBJECT --require-complete --check` passes;
5. normal image QA, browser/PWA/APK gates and memory handoff pass.

Current old registry totals remain useful only as subset state: 162 assets / 204 bindings / 163 released questions globally; Biochemistry 60 approved assets / 62 total assets / 60 released questions. **Do not interpret those numbers as Biochemistry coverage completion.**

The CRISPR Ch25 Q26 asset remains REVIEW_REQUIRED and unreleased because its small labels cannot yet be verified faithfully. Historical Biochemistry candidate branches do not own the shared writer lane.

## Automation state

- Physiology image automation is intentionally paused so the same discovery/coverage defect is not propagated further.
- Biochemistry becomes the recovery subject once the verified coverage guard is incorporated into `feature/marrow-image-rollout-current`.
- Recovery must proceed from the source-coverage backlog in deterministic source order, not by skipping difficult vector/multi-candidate references in favor of easier JPEGs.
- A bounded batch may be COMPLETE while the Biochemistry subject remains INCOMPLETE; always report both statuses.

## Known problems / verification cautions

- Biochemistry currently has **30 source-recorded references not learner-facing** (25 untracked + 5 tracked/unreleased), plus 31 text-cue review items requiring adjudication.
- Physiology currently has **176 source-recorded references not learner-facing** (154 untracked + 22 tracked/unreleased), plus 27 text-cue review items.
- Complex/vector/page-content figures need precise region rendering or source-faithful reconstruction under existing medical-image rules; they must not disappear from the queue.
- Question-time and explanation-time visuals can both exist for one question and both must be represented with correct timing.
- Rejected wrong candidates do not prove the legitimate source visual is resolved.
- Never use approved registry asset count as a completeness denominator again.
- Do not alter raw Marrow bundles/source PDFs or unrelated UI while repairing coverage.

## Next step

1. Incorporate the green coverage repair into `feature/marrow-image-rollout-current` without touching `main` or production.
2. Resume Biochemistry in bounded coverage-first recovery batches from the earliest unreleased source reference, explicitly covering the user-reported Chapters 18–22 examples.
3. Keep Physiology paused until Biochemistry recovery and the corrected selector/coverage workflow are proven trustworthy.
4. After every recovery batch update both batch status and subject coverage status; never claim subject COMPLETE until the coverage gate passes.
