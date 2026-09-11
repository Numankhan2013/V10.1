# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-physio-ch10-q001-q013-current`.
- Latest **fully verified** explanation product candidate remains Anatomy Chapter 5 Q1–Q9:
  `1921d758b19d0804438f434aaca950fa32d419ea`.
- Exact-candidate verification: Engineering Gate **333** / `34567801778` and
  full Android/PWA run **712** / `34567798753` both passed on that same SHA.
- Full-run artifact `V11.7-android-pwa`: ID `10186705331`, digest
  `sha256:cc332a829500e1cc4fa72ae48a846f5d6f9af518999d27905ce3710df4114bcb`.
- Browser/screenshot artifact: ID `10186689132`, digest
  `sha256:653be4144f19d4911d9f87948ee693d08e8f4f91cd56a2e7f6898ecc8298365b`.
- Production promotion was skipped.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** until the user explicitly promotes a later product baseline.
- Accepted product commit: `125d68b`
- build-verified, device-verified, and accepted are separate states.

## Current Marrow bank

Shared architecture:
`MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
There is one shared Practice/CBT/Review/FSRS/sync/module/analytics/navigation engine;
explanation work must not fork it by subject.

Supplied Marrow ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 topics**.

Raw imported Marrow source is immutable/auditable. Learner-facing correction and
reconstruction belong only in ID-keyed augmentation.

## Explanation-quality contract

Canonical procedure: `docs/MARROW_EXPLANATION_FINE_TUNING.md`.
For unattended Scheduled Tasks, `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md`
is the mandatory execution/safety protocol.

Every refined four-option SBA should have one meaningful Key Takeaway; medically
correct structured display text; 1–4 verbatim emphasis anchors; exactly three
wrong-option rationales keyed to the three incorrect source options; source-owned
figures/tables/provenance; and reconstruction metadata when source defects are
recovered under the runbook contract.

## FULLY_VERIFIED_HISTORY

- Anatomy approved reference before Chapter 5 rollout: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** verified on the stacked lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapters 5–9 are fully verified; Chapter 9 exact verified product SHA
  `7974b8eee842f668e9fb4fac95783ac64893e98d`, Gate 327, full run 701.
- Anatomy Chapter 5 Q1–Q9 is **FULLY_VERIFIED**.
  - PR: **#34**.
  - Product SHA: `1921d758b19d0804438f434aaca950fa32d419ea`.
  - Scope: Chapter 5 **Pharyngeal arches, Skeletal & Muscular Systems**, Q1–Q9 only.
  - Count/workload: **9 questions**, workload score **16.5**.
  - Augmentation: `data/marrow/explanation_anatomy_ch05_q001_q009_v1.json`.
  - Reconstruction statuses: **none** in Q1–Q9.
  - Raw Marrow source stayed unchanged.
  - Deterministic inventory: **548 enhanced / 1,567 pending**.
  - Inventory fingerprint:
    `3ac131bdd442b649b7778260565f43156e3bf1c04ef4717c3a6c8b82bf30c4fc`.
  - Engineering Gate **333** / `34567801778`: success on exact product SHA.
  - Full Android/PWA **712** / `34567798753`: success on the same exact SHA.
  - Required generated-product, browser, APK/package, reproducibility, artifact
    and preview-deployment stages are certified by the successful full workflow.
  - Production promotion skipped.

## CURRENT_UNVERIFIED explanation batch

- Owner: **Physiology**.
- Branch: `feature/marrow-explanation-rollout-physio-ch10-q001-q013-current`.
- Chapter: **10 — Neurotransmitters**.
- Scope: **Q1–Q13**, contiguous source order; no Chapter 11 work started.
- Workload score: **18.5** (target 16, maximum 20, 13 questions ≤ maximum 18).
- Source audit used rendered Marrow ED8 pages **198–209**; the embedded text layer is corrupted and was not treated as authoritative.
- Source answer keys for Q1–Q13 were visually verified from the rendered answer table.
- Augmentation file: `data/marrow/explanation_physio_ch10_q001_q013_v1.json`.
- Content checkpoint commit: `3d44fed367b7c1a5251b270e7b11f7843c9e9f6a`.
- Validator-support checkpoint: `d2e7ab57eea157c589788082f079fa6227c0d967`.
- `tools/test_marrow_physio_explanation_rollout.py` was generalized narrowly so one chapter may be refined in bounded contiguous slices while still enforcing Q1-starting, gap-free aggregate coverage, no duplicate IDs, source chapter ownership, exact rationale keys, emphasis and reconstruction schema.
- Q13 carries `resolved_reconstruction`: the raw source correctly keys sweat-gland sympathetic adrenergic innervation as wrong, but its explanatory extension to additional cholinergic exceptions is not retained as a modern general rule. Raw source remains unchanged.
- Local structure audit of the new augmentation passed: 13 records, 1–4 emphasis anchors all present verbatim, and rationale keys exactly match the three source-incorrect options for every question.
- Deterministic inventory has **not yet been regenerated** on this branch. Expected count after regeneration is **561 enhanced / 1,554 pending**, but do not treat that expected count as certified until `tools/inventory_marrow_explanations.py --write` and validators pass.
- No Engineering Gate or Android/PWA exact-head certification exists for this batch yet.
- Status: **CONTENT_AUTHORED / CURRENT_UNVERIFIED**.

## Current integration-lane status

- Physiology Chapter 10 Q1–Q13 is the sole **CURRENT_UNVERIFIED** explanation batch and owns the serialized lane.
- Historical open PRs/branches, including PR #34, are non-blocking.
- Other subject workers may pre-audit only; they must not start another integration batch until this batch is FULLY_VERIFIED or safely retired.
- An earlier empty branch named `feature/marrow-explanation-rollout-physio-ch10-q001-q014-current` was created before the workload re-score narrowed the batch. It contains no batch mutations and is **STALE_HISTORY / non-authoritative**; it must not be treated as lane ownership.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only a PR's exact product head SHA.
- Documentation-only `[skip ci]` handoff commits may follow a verified product SHA;
  do not pretend the later documentation head itself was APK/package certified.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines,
  alter Topics taxonomy, redesign UI, merge, or promote production.
- ROADMAP/FINE_TUNING historical prose may lag the newest verified checkpoint;
  `STATE.md` + live Git/CI are authoritative for immediate lane ownership.

## Next step

1. Resume this exact Physiology Chapter 10 Q1–Q13 batch; do **not** author Q14–Q18 yet.
2. Regenerate `data/marrow/explanation_inventory_v1.json` deterministically with
   `python3 tools/inventory_marrow_explanations.py --write`; confirm **561 enhanced / 1,554 pending** and record the new fingerprint.
3. Run the Physiology rollout validator and the runbook-required static/shared regressions. Fix at most two bounded failures of the same class.
4. Add/update a stable-ID Chapter 10 browser regression for this batch, then open/update the PR and require exact-head Engineering Gate plus exact-head Android/PWA workflow, APK/package/reproducibility and preview deployment.
5. Only after exact-head certification and final memory handoff move this batch to `FULLY_VERIFIED_HISTORY` and release the lane.
6. Keep production promotion skipped and preserve the accepted V11.6 baseline unless the user explicitly changes it.

Efficiency rule: pre-audit future content while CI runs, but never commit another
batch on an unverified lineage.
