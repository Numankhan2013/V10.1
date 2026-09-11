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

Coverage repair is incorporated into the image lineage. The current verified post-adjudication Biochemistry coverage is:
- raw source visual references: **95**;
- effective learner visual references: **94**;
- released source visual references: **65**;
- exact invalid-source-metadata references: **1**;
- resolved source visual references: **66**;
- tracked but unreleased: **4**;
- untracked: **25**;
- text-cue review items: **31**.

Physiology remains paused at 218 raw references / 42 released / 22 tracked-unreleased / 154 untracked / 27 text-cue items.

The source-derived audit plus `tools/marrow_image_coverage.py` is the completion gate. A bounded batch may be COMPLETE while a subject remains INCOMPLETE.

## Latest image recovery batch — VERIFIED_HISTORY

Classification: **VERIFIED_HISTORY / COMPLETE specialist source-metadata adjudication**. It no longer owns the shared writer lane.

- Subject: Biochemistry.
- Batch: `NKQ_BIOCHEM_SOURCE_ADJ_20260911`.
- Historical branch: `automation/marrow-images-biochemistry-NKQ_BIOCHEM_SOURCE_ADJ_20260911`.
- Exact integration base: `e8504ee1310df67eb88c5f65051ab8bddb67ebef`.
- Exact build-verified candidate: `2f075f190142476a8b0f40813c7b298c84982114`.
- PR: #39, targeting only the image integration branch; never `main` or production.
- Specialist target: `marrow__BIOCHEM_CH02_Q010:figure:1`.

Authoritative finding:
- Canonical metadata declares an explanation `glycolysis_pathway` on Marrow ED8 Biochemistry page 33.
- Authoritative `biochemistryed8.pdf` verified at 7,958,177 bytes, SHA-256 `463cb586aa18b702243d2467b4ad1f7fb24537d7ae73388607421516660643eb`.
- Full rendered page 33 contains the Q10 explanation text but **no figure**.
- Neighboring pages 31, 32 and 35 do contain glycolysis pathway figures, so attaching one to Q10 would be a false ownership substitution.
- Existing registry history already rejected the page-33 hexokinase/glucokinase graph for Q10 as the wrong figure.

Implemented and verified:
- `data/marrow/images/source_reference_adjudications.json` records this exact reference as `SOURCE_METADATA_INVALID`; raw Marrow source remains unchanged.
- `tools/marrow_image_coverage.py` keeps invalid metadata visible in the raw denominator, reports it separately, never calls it released, and excludes it only from the effective learner-image requirement.
- Matching fails closed on stable reference ID, question, subject, role and exact source page set; orphaned/mismatched adjudications fail.
- Regression coverage passes for one-to-one binding matching and wrong-page adjudication rejection.
- Engineering Gate `34618396121` passed on exact candidate `2f075f190142476a8b0f40813c7b298c84982114`, including authoritative PDF coverage recomputation.
- Full Android/PWA/package run `34618398667` passed on the exact candidate, including generated browser checks, image/offline byte verification, APK/package contracts, reproducibility manifest and preview deployment. Production promotion was skipped.

No learner image was released for Q10 because the authoritative referenced page contains none. No registry asset/binding, raw source bundle, UI, `main`, or production deployment was changed by this specialist adjudication.

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
- The next deterministic unresolved source reference is `marrow__BIOCHEM_CH02_Q013:figure:1`, explanation role, source page 35 (`Glycolysis pathway diagrams`). The authoritative page does contain the pathway figure and the current registry has no binding for Q13.
- After one bounded batch completes, stop that run and leave Biochemistry recurring recovery enabled while subject coverage remains incomplete.

## Known problems / verification cautions

- Biochemistry still has 29 legitimate source references not learner-facing (4 tracked-unreleased + 25 untracked), plus 31 text-cue items requiring adjudication.
- User-confirmed missing visuals in Chapters 18–22 remain outstanding and are not exhausted by the listed examples.
- Complex/vector/page-content figures may require native vector extraction, precise region rendering, or source-faithful reconstruction; medical pixels must remain authentic.
- Question-time and explanation-time visuals can both exist for one question and both must be represented with correct timing.
- Ch25 Q26 CRISPR remains REVIEW_REQUIRED because tiny labels cannot yet be verified faithfully.

## Next step

1. Acquire the free shared writer lane from live `feature/marrow-image-rollout-current` only if no newer current writer exists.
2. Start the next bounded Biochemistry recovery batch at `marrow__BIOCHEM_CH02_Q013:figure:1` (explanation, page 35) and continue only within the runbook workload budget.
3. Keep Physiology paused and never claim Biochemistry COMPLETE until the full coverage gate passes.
