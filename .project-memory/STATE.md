# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`.
- Git `main` is the authoritative unified V11/Marrow product line after PRs #6–#8.
- Current explanation-quality branch:
  `feature/marrow-explanation-rollout-biochem-ch01`.
- Resolve live branch/HEAD from Git; never hardcode a self-staling HEAD value.
- Accepted product baseline remains **V11.6 Content Quality** at `125d68b`,
  canonical APK run `34050921180`.
- Accepted product commit: `125d68b`.
- Production promotion remains explicit and guarded.

## Current Marrow bank

The shared subject-indexed architecture remains:
`MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
There is no duplicate Practice/CBT/Review/FSRS/sync/module/analytics engine.

Current supplied Marrow ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 topics**.

Expanded source bundles are deterministic zlib/base64 shards with manifest
counts, byte lengths and SHA-256 validation. Runtime ingestion fails closed on
corruption, count drift, duplicate IDs, bad option shape or topic-link mismatch.
Raw imported Marrow source remains authoritative and immutable.

The original 62-question Anatomy and 80-question Physiology enhanced subsets
remain regression/augmentation references. Three resolved Anatomy
reconstructions retain provenance: `ANAT_CH02_Q010`, `ANAT_CH03_Q004`,
`ANAT_CH04_Q013`.

## User/device verification — 2026-09-08

- The user physically verified the newly deployed Marrow PWA.
- The user confirmed the questions/current integration are correct and declared
  the integration/taxonomy verification phase complete.
- The recovered Topics journey, fixed Continue Learning tray and dedicated FSRS
  controls are also user-approved.
- The explicit source-aligned 107-topic taxonomy is therefore **device-verified**
  for the current deployed experience. Four cross-system Anatomy placements
  remain internally reviewable but do not block explanation work.
- This does not mean every one of the 2,115 raw explanations was individually
  reviewed, and it is not an explicit production-baseline promotion.

## Explanation-quality phase

- The user explicitly designated the existing **142 enhanced questions**
  (62 Anatomy + 80 Physiology) as the gold-standard explanation reference.
- Those 142 contain 426 stored distractor rationales and define the approved
  presentation grammar:
  Key Takeaway → structured detailed explanation with selective emphasis and
  native tables → exactly three concise wrong-option rationales.
- FSRS remains protected in the fixed/floating session footer above Previous/Next.
- The deterministic inventory originally accounted for all 2,115 IDs as
  142 references + 1,973 pending. After approval of the 20-question sample and
  completion of the remaining 22 questions in Biochemistry Chapter 1,
  **184 are enhanced and 1,931 remain to roll out**.
- The approved cross-chapter **20-question Biochemistry gold reference** is stored
  at `data/marrow/explanation_biochem_gold_sample_v1.json`.
- Biochemistry Chapter 1 rollout is complete: the remaining **22 questions** are
  stored in `data/marrow/explanation_biochem_ch01_v1.json`; together with gold
  sample Q23, all 23 Chapter 1 questions now use the approved grammar.
- On 2026-09-09 the user physically reviewed the 20-question Biochemistry sample
  and explicitly approved it: “They are good. We need that kind of explanation everywhere.”
  The approved explanation reference is therefore now **162 questions**
  (62 Anatomy + 80 Physiology + 20 Biochemistry).
- Source ambiguities remain explicit rather than invented. In particular:
  - the PCT question refers to a lab panel absent from the rendered question page;
  - the vitamin-B12 combination question omits the defining numbered enzyme list.
- Contract test:
  `tools/test_marrow_biochem_explanation_sample.py` validates the exact 20 IDs,
  source SHA, nonempty display content and exactly three rationales mapped to the
  three incorrect options.

## Verification / release status

- Expanded Marrow bank integration is **build-verified** by prior successful
  Engineering/full Android+PWA runs, including run 405 and authoritative-main
  run 409.
- The approved 20-question sample passed Engineering/full Android+PWA/browser
  verification before merge. The Chapter 1 rollout branch still requires its own
  final CI/browser/package pass before merge.
- Build-verified ≠ device-verified ≠ accepted baseline.
- V11.6 `125d68b` remains the **accepted baseline** / rollback checkpoint until
  the user explicitly promotes a later candidate.
- Main/production release guard requires explicit workflow dispatch plus exact
  full release SHA; CI success alone must never promote production.

## Known problems / cautions

- The remaining non-reference Marrow explanations still need the approved polish.
- Preserve source tables, figure metadata and uncertainty/reconstruction notes.
  Actual missing image binaries remain a later pass.
- Do not invent missing list items, lab values, graph labels or image-dependent facts.
- Do not rewrite raw JSONL/sharded source to make the UI prettier.
- Do not alter the approved Topics journey, FSRS dock, source-PDF renderers,
  Practice/CBT/Review, sync, modules, persistence or navigation during explanation work.
- Large connector/Git writes should remain bounded, deterministic and validated.

## Image phase — active

- Branch: `feature/marrow-image-pipeline`; initial commit `07ee53d` passed full
  APK/PWA CI `34311877059`. Expanded 18-asset checkpoint: `1925eec`.
- Audit covers 2,484 PDF pages: 1,082 explicit references across 821 questions,
  plus 58 text-cue candidates. Native candidates are not final asset counts.
- Pilot: 15 PASS, one SOURCE_LIMITED microscopy image, two REVIEW_REQUIRED
  redraws. Sixteen assets release by stable question ID; two reviewed SVGs.
- Local registry tests pass. Expanded batch still needs local gate, CI/browser/
  package checks, user review, and full-bank classification.
- Audit and workflow: `docs/MARROW_IMAGE_PIPELINE.md`. Preserve raw sources and
  `tools/__pycache__/`; no production promotion. UI upgrade remains deferred.

## Next step

1. Verify and publish the expanded pilot branch, then inspect CI evidence.
2. Present pilot for user review before wider asset rollout.
3. Reconstruct the held notochord and compressed-glycolysis figures.
4. Continue bounded classification and asset batches across all subjects.
5. Resume explanation rollout separately after the image priority phase.

Canonical Marrow procedure: `docs/MARROW_BANK_INTEGRATION.md`.
