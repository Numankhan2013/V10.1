# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-physio-ch10-q014-q018-current`.
- Latest **fully verified** explanation product candidate is Physiology Chapter 10 Q14–Q18:
  `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`.
- Exact-candidate verification: Engineering Gate **338** / `34591048655` and
  full Android/PWA run **724** / `34591045176` both passed on that exact SHA.
- Full-run artifact `V11.7-android-pwa`: ID `10195721333`, digest
  `sha256:4982c285174125aecb7434afe133d6772d1db6f7cc266dba499c622c2972f536`.
- Browser/screenshot artifact: ID `10195700442`, digest
  `sha256:099ab9602bd3cec93396b9604fd6a20b24b308fc0a61ed2e275f3904f2842911`.
- Immutable verified preview: `https://ea6c7b4b.nk-qbank.pages.dev`.
- Production promotion was skipped.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** until the user explicitly promotes a later product baseline.
- Accepted product commit: `125d68b`
- build-verified, device-verified, and accepted are separate states.

## Current Marrow bank

Shared architecture: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
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
- Anatomy Chapter 5 Q1–Q9 is **FULLY_VERIFIED** on PR #34, product SHA
  `1921d758b19d0804438f434aaca950fa32d419ea`, Gate 333 / `34567801778`,
  full run 712 / `34567798753`; inventory then **548 / 1,567**.
- Physiology Chapter 10 Q1–Q13 is **FULLY_VERIFIED** on PR #35, product SHA
  `45cda2196c40d30eaf9283b031cba3942ed2e132`, Gate 336 / `34580097242`,
  full run 719 / `34580093798`; Q13 is `resolved_reconstruction`.
- Physiology Chapter 10 Q14–Q18 is **FULLY_VERIFIED**.
  - PR: **#36**.
  - Product SHA: `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`.
  - Scope: Chapter 10 **Neurotransmitters**, Q14–Q18 contiguous source-order chapter tail.
  - Count/workload: **5 questions**, workload score **10.0**; Chapter 11 was not entered merely to fill target workload.
  - Augmentation: `data/marrow/explanation_physio_ch10_q014_q018_v1.json`.
  - Q15 reconstruction status: `resolved_reconstruction`; source-keyed answer is preserved while learner-facing text teaches receptor-dependent serotonin physiology rather than the false universal claim that serotonin is inhibitory.
  - Q14/Q16/Q17/Q18 have no reconstruction metadata.
  - Q18 QA repair changed only one non-verbatim emphasis anchor; medical prose/source data stayed unchanged.
  - Raw Marrow source/key stayed unchanged.
  - Deterministic inventory: **566 enhanced / 1,549 pending**.
  - Inventory fingerprint: `991a2c84500ee94e52a3d09f0f47ed7b77b3057ff2ff7d9a1842594ec387cf78`.
  - Physiology enhanced count: **236**.
  - Stable-ID browser regression verified Physiology → Marrow → Chapter 10 → Q15, receptor-dependent serotonin reconstruction, and exactly three wrong-option rationales; existing Q13 coverage also passed.
  - Engineering Gate **338** / `34591048655`: success on exact product SHA.
  - Full Android/PWA **724** / `34591045176`: success on the same exact SHA.
  - Generated product, deterministic inventory, Physiology/Biochemistry rollout validators, Practice/CBT/Review/FSRS/shared regressions, browser verification, APK build, packaged APK/product checks, reproducibility manifest, artifact upload and Cloudflare preview deployment all passed.
  - Full-run artifact `V11.7-android-pwa`: ID `10195721333`, digest `sha256:4982c285174125aecb7434afe133d6772d1db6f7cc266dba499c622c2972f536`.
  - Browser/screenshot artifact: ID `10195700442`, digest `sha256:099ab9602bd3cec93396b9604fd6a20b24b308fc0a61ed2e275f3904f2842911`.
  - Immutable preview: `https://ea6c7b4b.nk-qbank.pages.dev`.
  - Production promotion skipped.

## CURRENT_UNVERIFIED explanation batch

- **None.** The serialized explanation lane is released.
- Historical/stacked open PRs and branches whose exact candidates are already FULLY_VERIFIED are non-blocking.

## Current integration-lane status

- No authoritative CURRENT_UNVERIFIED explanation batch exists after Physiology Chapter 10 Q14–Q18 certification.
- Every worker must re-resolve newest authoritative `STATE.md` plus live Git/PR/head state before claiming the lane.
- Stale sibling branches and historical open PRs must never be resurrected as blockers solely because they remain open.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only a PR's exact product head SHA.
- Documentation-only `[skip ci]` handoff commits may follow a verified product SHA; do not pretend the later documentation head itself was APK/package certified.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Browser lesson from this batch: for Q15, serotonin appears in the option list rather than the stem; stable source-order navigation plus option-content assertion is the correct regression check.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.
- ROADMAP/FINE_TUNING historical prose may lag the newest verified checkpoint; `STATE.md` + live Git/CI are authoritative for immediate lane ownership.

## Next step

1. End the current run; do **not** start Chapter 11 in the same run that finalized Chapter 10 Q14–Q18.
2. On a later worker run, re-resolve live lane ownership from authoritative `STATE.md` plus live Git/PR/head state.
3. If Physiology reacquires a free lane, exact next Physiology source-order start is **Chapter 11 Q1**; dynamically workload-score the contiguous batch under the runbook before authoring.
4. Preserve raw Marrow source, shared study engines, image-integration ownership, and production baseline constraints.

Efficiency rule: pre-audit future content while CI runs, but never commit another
batch on an unverified lineage.
