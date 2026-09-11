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

Coverage repair is incorporated into the image lineage. Authoritative CI measured:
- **Biochemistry:** 95 source-recorded visual references across 89 questions; 65 released, 5 tracked but unreleased, 25 untracked; plus 31 text-cue review items.
- **Physiology:** 218 source-recorded visual references across 172 questions; 42 released, 22 tracked but unreleased, 154 untracked; plus 27 text-cue review items.

The source-derived audit plus `tools/marrow_image_coverage.py` is now the completion gate. A bounded batch may be COMPLETE while a subject remains INCOMPLETE.

## Current image recovery batch

Classification: **CURRENT_UNVERIFIED / specialist source-metadata adjudication**.

- Subject: Biochemistry.
- Batch: `NKQ_BIOCHEM_SOURCE_ADJ_20260911`.
- Branch: `automation/marrow-images-biochemistry-NKQ_BIOCHEM_SOURCE_ADJ_20260911`.
- Exact base: `e8504ee1310df67eb88c5f65051ab8bddb67ebef` from `feature/marrow-image-rollout-current`.
- PR: #39, targeting only the image integration branch; never `main` or production.
- Specialist target: `marrow__BIOCHEM_CH02_Q010:figure:1`.

Authoritative finding:
- Canonical metadata declares an explanation `glycolysis_pathway` on Marrow ED8 Biochemistry page 33.
- Authoritative source `/Marrow digitization Biochem/biochemistryed8.pdf` verified at 7,958,177 bytes, SHA-256 `463cb586aa18b702243d2467b4ad1f7fb24537d7ae73388607421516660643eb`.
- Full rendered page 33 was inspected and contains Q10 explanation text only, with **no figure**.
- Neighboring pages 31, 32 and 35 do contain glycolysis pathway figures; attaching one to Q10 would be a false ownership substitution.

Implementation on the current candidate:
- `data/marrow/images/source_reference_adjudications.json` records this exact reference as `SOURCE_METADATA_INVALID` with source hash and inspection evidence; raw Marrow data remains unchanged.
- `tools/marrow_image_coverage.py` keeps invalid metadata visible in the raw source-reference denominator, reports it separately, never calls it released, and removes it only from the effective learner-image requirement.
- Adjudication matching is fail-closed on stable reference ID, question, subject, role and exact source page set; orphaned/mismatched adjudications fail validation.
- `tools/test_marrow_image_coverage.py` covers exact adjudication, one-to-one binding coverage, and wrong-page fail-closed behavior.
- `docs/MARROW_IMAGE_COVERAGE_GATE.md` documents the immutable-source-safe adjudication policy.

No image registry asset/binding, learner runtime, raw Marrow bundle, UI, `main`, or production deployment is changed by this specialist batch.

Exact-head CI and recomputed coverage are pending for the latest candidate; do not classify this batch VERIFIED_HISTORY until the final current head passes required gates.

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

- Biochemistry is the active coverage-recovery subject.
- Physiology image automation remains paused so the old discovery defect is not propagated.
- Recovery proceeds in deterministic source-reference order; complex/vector/zero-native references cannot be skipped for easier JPEGs.
- After one bounded batch completes, stop that run and leave Biochemistry recurring recovery enabled while subject coverage remains incomplete.

## Known problems / verification cautions

- Biochemistry remains substantially incomplete even after this single metadata adjudication; exact post-adjudication counts must come from final CI, not arithmetic assumptions.
- User-confirmed missing visuals in Chapters 18–22 remain outstanding and are not exhausted by the listed examples.
- Complex/vector/page-content figures may require native vector extraction, precise region rendering, or source-faithful reconstruction; medical pixels must remain authentic.
- Question-time and explanation-time visuals can both exist for one question and both must be represented with correct timing.
- Ch25 Q26 CRISPR remains REVIEW_REQUIRED because tiny labels cannot yet be verified faithfully.

## Next step

1. Finish exact-head verification of PR #39 and inspect recomputed Biochemistry coverage.
2. If green, incorporate only this specialist adjudication batch into `feature/marrow-image-rollout-current`, mark it VERIFIED_HISTORY, and release the writer lane.
3. Next run resumes from the next unresolved source reference in deterministic coverage order; do not jump to the user-reported later chapters merely because they are easier to identify.
4. Keep Physiology paused and never claim Biochemistry COMPLETE until the full coverage gate passes.
