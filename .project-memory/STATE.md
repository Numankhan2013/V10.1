# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Current image candidate: `feature/marrow-image-rollout-batch-08-small`, based
  on `feature/marrow-image-rollout-current` and the verified Physiology Chapter
  5 explanation lineage.
- Resolve live branch/HEAD from Git; do not hardcode self-staling HEAD values.
- This image base contains explanations through Physiology Chapter 5. Separately,
  the verified explanation lineage reaches Chapter 8 at `0a1f31f`; full run
  `34367467186` passed and previewed at `https://afdceb7d.nk-qbank.pages.dev`.
- Production promotion remains explicit and guarded; run 539 skipped production.
- Accepted baseline remains V11.6 Content Quality `125d68b` until the user explicitly promotes a later product baseline.
- Accepted product commit: `125d68b`.

## Current Marrow bank

Shared architecture:
`MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
There is one shared Practice/CBT/Review/FSRS/sync/module/analytics/navigation engine.

Supplied Marrow ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 topics**.

Raw imported Marrow source is authoritative and immutable. Source bundles remain
manifest/hash validated and ingestion fails closed on corruption/count/ID/option/
topic-link drift.

## Explanation-quality phase

Canonical procedure: `docs/MARROW_EXPLANATION_FINE_TUNING.md` +
`docs/MARROW_BANK_INTEGRATION.md`.

Approved learner-facing contract:
- one meaningful Key Takeaway;
- source-faithful structured detailed explanation;
- 1–4 selective emphasis anchors that exist verbatim in display text;
- exactly three concise wrong-option rationales mapped to the three incorrect
  source options for four-option SBA;
- ID-keyed augmentation separate from raw source;
- source tables/figures/provenance remain source-owned and separate;
- missing/ambiguous source content remains explicit; never invent it;
- FSRS/session behavior is untouched.

Current deterministic inventory:
- **429 enhanced / 1,686 pending**.
- Anatomy approved reference: **62**.
- Physiology approved pilot: **80** across Chapters 1–4.
- Biochemistry enhanced: **259**; Chapters 1–11 are complete on the current
  stacked explanation lineage, including fixed gold-sample overlaps.
- Physiology Chapter 5 **Body Fluids: 28/28 complete**.
- Physiology enhanced total is now **108**.
- Physiology Chapter 5 inventory fingerprint:
  `09989df1e8745f7338abf146fb4eb1337738ecaf4dafb1b69f9c76314e521ea8`.

Physiology rollout infrastructure was generalized on PR #24:
- `data/marrow/explanation_physio_ch*_v1.json` discovery in inventory;
- shared app loader merges Physiology chapter augmentations with the existing
  80-question Physiology pilot;
- `tools/test_marrow_physio_explanation_rollout.py` provides fail-closed
  source-ID/chapter/emphasis/distractor validation;
- both Engineering Gate and full Android/PWA workflow run the Physiology validator;
- Biochemistry rollout validation was generalized so other subjects may add
  enhanced records without invalidating its subject-local guarantees.

Representative Chapter 5 browser regression:
Physiology → Marrow → Body Fluids → Q17 verifies the permeant-urea / tonicity
explanation and exactly three distractor rationales through the real learner UI.

## Image pipeline / ownership

- Explanation refinement and image integration remain separate workstreams.
- The primary agent is taking ownership of **image integration**.
- Preserve source-native figure/image metadata and source fidelity.
- Do not reconstruct medically meaningful figures from prose when source assets
  exist or when the source is ambiguous.
- Historical Batch 01 remains build-verified and user-approved as the minimum quality threshold.
- Current Batch 08 candidate contains **153 approved assets / 172 released
  bindings / 158 released questions**. By subject: Anatomy 64, Biochemistry 55,
  Physiology 39 questions. Exact product commit `0c1af90` passed full Android/PWA
  run `34438683420`; generated visual QA passed.
- Batch 08 immutable preview: `https://af73057f.nk-qbank.pages.dev`; artifact ID
  `10137184212`. Production promotion was skipped.
- Batches 05–07 reviewed 90 candidate bindings and released 72: Batch 05 23/30, Batch 06 23/30 with one quality hold, Batch 07 26/30. Seventeen false ownership/reuse mappings were rejected.
- Authentic ultrasound, radiology, clinical, specimen, histology and microscopy assets preserve native bytes. Educational diagrams use native PDF streams only where they meet the approved readability floor.
- The Golgi-tendon-organ sequence remains REVIEW_REQUIRED because its native labels are below the approved baseline; it must be faithfully reconstructed before release.
- Every staged binding carries independent page/xref/region provenance and QA status. Rejected or unreviewed bindings never enter runtime metadata.
- Batches 05–07 passed full Android/PWA CI (`34367383565`, `34367985338`, `34368514110`). Latest immutable preview: `https://4d588745.nk-qbank.pages.dev`; production promotion was skipped.

## Current image automation checkpoint

- Classification: **VERIFIED_HISTORY**; completed owner **Biochemistry**; batch `NKQ_BIOCHEMISTRY_20260911` is complete and no longer owns the shared writer lane.
- Branch `automation/marrow-images-biochemistry-NKQ_BIOCHEMISTRY_20260911`; working base `1ae61e205804d3d3b2359fcbad218f56e396896b`; exact build-verified candidate `04027242473b46ab5941ea3a41c11046458f2c90`; substantive image QA/release commit `6170c412a98f2147889e9b62845442a44b9dedd0`. Resolve live branch HEAD from Git for the memory-only handoff commit.
- Registry SHA-256 `1927cb19959c931503c396a2cf58d0fd37f26531df23f3c542a7f6770d38de38`; progress SHA-256 `77c32ec0be4ef75a9941b8a2e44040a00720e354b5463a0e245b79caebc790b8`.
- PASS/released in this batch: `marrow__BIOCHEM_CH25_Q024`, `marrow__BIOCHEM_CH26_Q003`, `marrow__BIOCHEM_CH26_Q014`, `marrow__BIOCHEM_CH26_Q021`, `marrow__BIOCHEM_CH26_Q022`.
- Deferred specialist backlog, **REVIEW_REQUIRED** and unreleased: `marrow__BIOCHEM_CH25_Q026` / asset `biochemistry-e10cc8a9721a17da`; ownership is correct but native CRISPR labels remain below the confident phone-width readability threshold. This deferred item is not a current writer lock and must remain unreleased until a dedicated readability/reconstruction batch verifies it.
- Exact-head verification for `04027242473b46ab5941ea3a41c11046458f2c90`: CI bridge `34600790522` PASS; Engineering Gate `34600799528` PASS; full Android/PWA/package run `34600801834` PASS, with production promotion skipped. Browser/image-byte/APK/package/reproducibility gates passed.
- Current deterministic totals: 162 assets, 204 bindings, 163 released questions; Biochemistry 60 approved assets / 62 total assets / 60 released questions.
- Exact next action: the next image writer must resolve the live image pointer and may acquire the lane normally. Treat this batch as VERIFIED_HISTORY. Handle the deferred CRISPR figure only in a future dedicated specialist batch; do not revive this completed mixed batch as CURRENT_UNFINISHED.

## Known problems / verification cautions

- Build-verified ≠ device-verified ≠ accepted production baseline.
- User has independently checked the current preview; do not spend agent usage
  repeating routine visual verification unless needed for a code-quality issue.
- Do not rewrite raw Marrow JSON/JSONL/shards for learner-facing cleanup.
- Do not fork Practice/CBT/Review/FSRS/sync/modules/navigation by subject.
- Do not alter Topics taxonomy during explanation or image work.
- Keep production promotion deliberate.

## Next step / ownership split

- **Primary/image work:** Batch 08 is build-verified and visually inspected; ask
  the user for physical review when convenient. The six released Anatomy Chapter
  9 IDs are Q5, Q8, Q9, Q10, Q12 and Q13; all preserve native bytes, and
  Q9/Q12/Q13 retain neutral question-time alt text.
- For later batches follow `docs/MARROW_IMAGE_AUTOMATION_RUNBOOK.md` completely,
  serialize registry writers and never release uncertainty.
- **Explanation refinement agent:** repair and validate the existing unverified
  Physiology Chapter 9 checkpoint before beginning Chapter 10; do not touch the
  image-integration ownership.
