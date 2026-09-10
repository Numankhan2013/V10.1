# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`.
- Git `main` is the authoritative unified V11/Marrow product line; the user-approved image pilot merged through PR #12.
- Anatomy topic-index v2 work is prepared on `feature/anatomy-topic-index-v2`; use a `feature/marrow-*` integration branch for full push CI before merge.
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

## Anatomy topic index v2 — 2026-09-10

- The user replaced the older Anatomy major-index taxonomy with this exact order:
  **Embryology → Histology → Neuroanatomy → Head, neck, and face → Upper limb →
  Thorax → Abdomen and pelvis → Lower limb → Back → General anatomy**.
- `data/marrow/topic_index_taxonomy.json` now distinguishes the **71-topic intended
  Anatomy catalog** (`plannedIndex`) from the **48 currently imported source
  topics** (`topics`). Stable source IDs/titles/question linkage stay untouched.
- Current source placement is: Ch 1–10 Embryology; 11–16 Histology; 17–27
  Neuroanatomy; 28–34 Head, neck, and face; 35–40 Upper limb; 41–46 Thorax;
  47–48 Abdomen and pelvis.
- Current combined source chapters are not fabricated into multiple learner
  chapters. `plannedSlots` records which finer future catalog entries each
  combined source topic represents (for example Placenta + Fetal membranes and
  twinning).
- Planned topics not yet imported must remain invisible: no blank rows,
  placeholders, artificial gaps or empty index sections. Lower limb, Back and
  General anatomy therefore remain metadata-only at the current Ch 1–48 import.
- Learner-facing numbering is defined as `visible-contiguous`; backend/source IDs
  remain authoritative. The current rendered arrangement must show 1–48 without
  exposing source-order jumps caused by grouping.
- `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`, the taxonomy contract test and browser
  verification were updated for this behavior. Physiology and Biochemistry
  taxonomy were deliberately left unchanged until the user supplies their exact
  arrangements.
- This Anatomy v2 candidate is not yet device-verified or merged into `main` at
  this handoff point.

## User/device verification — 2026-09-08

- The user physically verified the newly deployed Marrow PWA.
- The user confirmed the questions/current integration are correct and declared
  the integration verification phase complete.
- The recovered Topics journey, fixed Continue Learning tray and dedicated FSRS
  controls are also user-approved.
- The visual Topics journey remains approved; the older Marrow Anatomy grouping
  taxonomy is superseded by the 2026-09-10 Anatomy topic-index v2 specification
  above.
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
- The approved 20-question sample and completed Biochemistry Chapter 1 rollout
  are merged into `main`; their dedicated content and browser contracts remain.
- Anatomy topic-index v2 is a separate candidate and must pass full CI before it
  is described as build-verified.
- Build-verified ≠ device-verified ≠ accepted baseline.
- V11.6 `125d68b` remains the **accepted baseline** / rollback checkpoint until
  the user explicitly promotes a later candidate.
- Main/production release guard requires explicit workflow dispatch plus exact
  full release SHA; CI success alone must never promote production.

## Known problems / cautions

- The remaining non-reference Marrow explanations still need the approved polish.
- Preserve source tables, figure metadata and uncertainty/reconstruction notes.
  The image pass is active; ambiguous, composite, masked and vector-only figures
  remain withheld until their source ownership and completeness are reviewed.
- Do not invent missing list items, lab values, graph labels or image-dependent facts.
- Do not rewrite raw JSONL/sharded source to make the UI prettier.
- Do not alter the approved Topics journey, FSRS dock, source-PDF renderers,
  Practice/CBT/Review, sync, modules, persistence or navigation during taxonomy
  or explanation work.
- Anatomy future topic integration must use `plannedIndex` / `plannedSlots`; do
  not infer placement from source chapter number alone and do not expose missing
  planned topics as placeholders.
- Large connector/Git writes should remain bounded, deterministic and validated.

## Image phase — active

- The approved pilot merged into `main` through PR #12 at merge commit `4faf0e5`.
  Production was not promoted.
- Audit covers 2,484 PDF pages: 1,082 explicit references across 821 questions,
  plus 58 text-cue candidates. Native candidates are not final asset counts.
- On 2026-09-09 the user reviewed all sixteen released pilot figures in the PWA
  and approved them as the minimum quality threshold for wider rollout. Future
  releases may improve on this baseline but must not fall below it.
- Merged Batch 01 has **28 approved assets / 34 released question bindings**:
  Anatomy 12, Biochemistry 11, Physiology 11. It adds ten inspected
  native assets, six approved repeated-asset bindings, and the two formerly held
  SVG reconstructions. Two false reuse matches were explicitly REJECTED.
- Authentic Pompe/McArdle muscle imagery retains exact native JPEG bytes. The
  Pompe stem image uses question-time placement and neutral alt text. Diagrams
  remain explanation-only unless their source explicitly makes them part of the stem.
- Registry now gates repeated-image ownership separately from asset quality and
  records source page/xref/region per reuse binding. Unsafe binding statuses are
  excluded from web/APK manifests. `data/marrow/images/progress.json` records
  deterministic rollout totals.
- Batch 01 is build-verified by full Android/PWA run `34334231275` at product
  commit `44990c0`: registry/progress, browser role timing, zoom viewer, offline
  hashes, APK build/package and exact packaged bytes all passed. Generated
  glycolysis and question-biopsy screenshots were inspected. Artifact
  `V11.7-android-pwa` ID `10097131223`; immutable preview
  `https://88a0ce10.nk-qbank.pages.dev`; production promotion was skipped.
- Audit and workflow: `docs/MARROW_IMAGE_PIPELINE.md`. Preserve raw sources and
  `tools/__pycache__/`; UI upgrade remains deferred.

## Next step

1. Finish/verify Anatomy topic-index v2 on a CI-triggering `feature/marrow-*`
   branch, then merge only after green taxonomy/browser/product checks.
2. Keep Physiology and Biochemistry taxonomy unchanged until the user supplies
   their intended index arrangements.
3. Continue image Batch 02 separately from current `main`, prioritizing unresolved
   question-critical and multi-candidate figures; never substitute an explanation
   image for a missing stem image.
4. Resume explanation rollout separately after the image priority phase.

Canonical Marrow procedure: `docs/MARROW_BANK_INTEGRATION.md`.
