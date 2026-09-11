# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Current image lineage is carried by `feature/marrow-image-rollout-current`; resolve its live HEAD from Git rather than hardcoding a self-staling pointer.
- This image lineage contains explanations through Physiology Chapter 5. Separately,
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
- Batch 08 contains **153 approved assets / 172 released bindings / 158 released questions**. By subject: Anatomy 64, Biochemistry 55, Physiology 39 questions. Exact product commit `0c1af90` passed full Android/PWA run `34438683420`; generated visual QA passed.
- Batch 08 immutable preview: `https://af73057f.nk-qbank.pages.dev`; artifact ID `10137184212`. Production promotion was skipped.
- Subsequent completed Biochemistry batch `NKQ_BIOCHEMISTRY_20260911` advanced deterministic totals to **162 assets / 204 bindings / 163 released questions**; Biochemistry now has **60 approved assets / 62 total assets / 60 released questions**.
- Authentic ultrasound, radiology, clinical, specimen, histology and microscopy assets preserve native bytes. Educational diagrams use native PDF streams only where they meet the approved readability floor.
- The Golgi-tendon-organ sequence remains REVIEW_REQUIRED because its native labels are below the approved baseline; it must be faithfully reconstructed before release.
- Every staged binding carries independent page/xref/region provenance and QA status. Rejected or unreviewed bindings never enter runtime metadata.

## Current image automation checkpoint

- Classification: **VERIFIED_HISTORY / COMPLETE (retired without learner-facing release)** for specialist batch `NKQ_BIOCHEMISTRY_CRISPR_20260911`. It **does not own the shared image-writer lane**.
- Historical branch: `automation/marrow-images-biochemistry-NKQ_BIOCHEMISTRY_CRISPR_20260911`; exact base SHA `532c6c8b9dcaf651ef203660cdc4581a985d1424`. Resolve the final handoff HEAD from Git rather than hardcoding a self-staling value.
- The specialist batch contained exactly one target: `marrow__BIOCHEM_CH25_Q026` / asset `biochemistry-e10cc8a9721a17da`.
- Final asset/binding status remains **REVIEW_REQUIRED** and unreleased. Source ownership is confirmed to Marrow ED8 Biochemistry page 402 / xref 961. The authoritative native object is a 600×451 JPEG with SHA-256 `e10cc8a9721a17daea04f60fb422e85611a233b31c0075ca5095e9df09aa4844`.
- Fresh full-page and 300-DPI inspection on 2026-09-11 reconfirmed that several small CRISPR/Cas9 repair-pathway labels/arrow annotations remain too soft to transcribe with enough certainty for a label-for-label, arrow-for-arrow faithful reconstruction. No wording, arrow, branch or relationship was guessed; no SVG was authored.
- Source recovery reverified the exact authoritative PDF: `biochemistryed8.pdf`, 7,958,177 bytes, SHA-256 `463cb586aa18b702243d2467b4ad1f7fb24537d7ae73388607421516660643eb`; no PrepLadder or alternate source was used.
- Registry/progress/runtime state remains unchanged from the completed prior batch: registry SHA-256 `1927cb19959c931503c396a2cf58d0fd37f26531df23f3c542a7f6770d38de38`; progress SHA-256 `77c32ec0be4ef75a9941b8a2e44040a00720e354b5463a0e245b79caebc790b8`; totals 162 assets / 204 bindings / 163 released questions, Biochemistry 60 approved assets / 62 total assets / 60 released questions.
- Exact pre-retirement branch HEAD `c70af7fcfea727cb3e8451cafe578686c246f0b6` passed the image CI bridge `34606554239`, Engineering Gate `34606564335`, and full Android/PWA/package run `34606567130`; production promotion was skipped.
- This specialist backlog must **not** block later image batches. Revisit Q26 only if a genuinely higher-fidelity authoritative or vector-equivalent source makes every small label/arrow verifiable; otherwise preserve REVIEW_REQUIRED indefinitely.

## Known problems / verification cautions

- Build-verified ≠ device-verified ≠ accepted production baseline.
- User has independently checked the current preview; do not spend agent usage
  repeating routine visual verification unless needed for a code-quality issue.
- Do not rewrite raw Marrow JSON/JSONL/shards for learner-facing cleanup.
- Do not fork Practice/CBT/Review/FSRS/sync/modules/navigation by subject.
- Do not alter Topics taxonomy during explanation or image work.
- Keep production promotion deliberate.

## Next step / ownership split

- **Primary/image work:** the shared image-writer lane is free. A later image worker must first resolve live `feature/marrow-image-rollout-current`, reconcile memory/registry/progress, and then acquire the lane with one new bounded subject batch. Historical Biochemistry CRISPR work is VERIFIED_HISTORY, not a lock.
- Q26 CRISPR is an isolated REVIEW_REQUIRED backlog item; revisit only with higher-fidelity authoritative/vector-equivalent evidence sufficient to verify every label and arrow.
- For later batches follow `docs/MARROW_IMAGE_AUTOMATION_RUNBOOK.md` completely, serialize registry writers and never release uncertainty.
- **Explanation refinement agent:** keep explanation work separate and do not touch image-integration ownership.
