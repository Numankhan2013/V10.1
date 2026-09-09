# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Current image branch: `feature/marrow-image-rollout-current`, based on the verified Physiology Chapter 5 explanation lineage.
- Resolve live branch/HEAD from Git; do not hardcode self-staling HEAD values.
- Current verified explanation lineage reaches
  `feature/marrow-explanation-rollout-physio-ch05-current` / PR #24.
- Exact verified Chapter 5 candidate: `f170eb8517998cdaf4229240d2c2a273c6d98cf8`.
- Engineering Gate 259 and full Android/PWA run 539 both passed.
- Latest immutable verified preview: `https://3cce6bfb.nk-qbank.pages.dev`.
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
- Current rollout contains **147 approved assets / 166 released bindings / 152 released questions**. By subject: Anatomy 58, Biochemistry 55, Physiology 39 questions.
- Batches 05–07 reviewed 90 candidate bindings and released 72: Batch 05 23/30, Batch 06 23/30 with one quality hold, Batch 07 26/30. Seventeen false ownership/reuse mappings were rejected.
- Authentic ultrasound, radiology, clinical, specimen, histology and microscopy assets preserve native bytes. Educational diagrams use native PDF streams only where they meet the approved readability floor.
- The Golgi-tendon-organ sequence remains REVIEW_REQUIRED because its native labels are below the approved baseline; it must be faithfully reconstructed before release.
- Every staged binding carries independent page/xref/region provenance and QA status. Rejected or unreviewed bindings never enter runtime metadata.
- Batches 05–07 passed full Android/PWA CI (`34367383565`, `34367985338`, `34368514110`). Latest immutable preview: `https://4d588745.nk-qbank.pages.dev`; production promotion was skipped.

## Known problems / verification cautions

- Build-verified ≠ device-verified ≠ accepted production baseline.
- User has independently checked the current preview; do not spend agent usage
  repeating routine visual verification unless needed for a code-quality issue.
- Do not rewrite raw Marrow JSON/JSONL/shards for learner-facing cleanup.
- Do not fork Practice/CBT/Review/FSRS/sync/modules/navigation by subject.
- Do not alter Topics taxonomy during explanation or image work.
- Keep production promotion deliberate.

## Next step / ownership split

- **Primary/image automations:** follow
  `docs/MARROW_IMAGE_AUTOMATION_RUNBOOK.md` completely. Use one subject and a
  default six-candidate batch, with one shared-registry writer at a time. Subject
  automations must run sequentially from the latest image base; concurrent work
  is proposal-only. Stop processing by the conservative runbook budget, reserve
  time for validation/memory/commit, and never release uncertainty.
- The runbook is the canonical compact-prompt target for ChatGPT web
  automations. It preserves the native-first, medical-authenticity,
  reconstruction, independent-binding-QA, regression, and timeout-safe
  checkpoint lessons through Batch 07.
- **Explanation refinement agent:** when resumed, continue from
  **Physiology Chapter 6 — Physiology of Nerve**, source order, without touching
  the image-integration ownership.
