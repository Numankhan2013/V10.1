# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-rebased-current` / PR #37.
- Latest **fully verified** explanation product candidate remains Physiology Chapter 10 Q14–Q18: `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`.
- That candidate passed Engineering Gate 338 / `34591048655` and full Android/PWA 724 / `34591045176` on the exact product SHA.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** until explicitly promoted.
- Accepted product commit: `125d68b`.
- build-verified, device-verified, and accepted are separate states.

## Current Marrow bank

Shared architecture: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
There is one shared Practice/CBT/Review/FSRS/sync/module/analytics/navigation engine; explanation work must not fork it by subject.

Supplied Marrow ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 topics**.

Raw imported Marrow source is immutable/auditable. Learner-facing correction and reconstruction belong only in ID-keyed augmentation.

## Explanation-quality contract

Canonical procedure: `docs/MARROW_EXPLANATION_FINE_TUNING.md`.
For unattended runs, `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md` is the mandatory execution/safety protocol.
Every refined four-option SBA requires a meaningful Key Takeaway, medically correct structured display text, 1–4 verbatim emphasis anchors, exactly three wrong-option rationales keyed to the three incorrect source options, source-owned figures/tables/provenance, and reconstruction metadata when source defects are recovered.

## FULLY_VERIFIED_HISTORY

- Anatomy approved reference before Chapter 5 rollout: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** verified.
- Physiology approved pilot: **80** across Chapters 1–4; Chapters 5–9 fully verified.
- Anatomy Chapter 5 Q1–Q9 is **FULLY_VERIFIED** on PR #34, product SHA `1921d758b19d0804438f434aaca950fa32d419ea`, Gate 333 / `34567801778`, full run 712 / `34567798753`; inventory then **548 / 1,567**.
- Physiology Chapter 10 Q1–Q13 is **FULLY_VERIFIED** on PR #35, product SHA `45cda2196c40d30eaf9283b031cba3942ed2e132`, Gate 336 / `34580097242`, full run 719 / `34580093798`; Q13 is `resolved_reconstruction`.
- Physiology Chapter 10 Q14–Q18 is **FULLY_VERIFIED** on PR #36, product SHA `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`; Q15 is `resolved_reconstruction`; deterministic inventory **566 / 1,549**, fingerprint `991a2c84500ee94e52a3d09f0f47ed7b77b3057ff2ff7d9a1842594ec387cf78`; Gate 338 and full run 724 passed; production promotion skipped.

## CURRENT_UNVERIFIED explanation batch

- Owner: **Anatomy**.
- Batch ID: `anatomy-20260911-ch05-q10-q19`.
- Branch: `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-rebased-current`.
- PR: **#37** (`Refine Marrow Anatomy Chapter 5 Q10–Q19 explanations`).
- Base lineage: latest verified Physiology Chapter 10 Q14–Q18 handoff (`1ff957f5f244f1ab649d6e38fbb21db61b21c308`; product certification anchored to `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`).
- Chapter 5: **Pharyngeal arches, Skeletal & Muscular Systems**.
- Exact source-order range: **Q10–Q19** / IDs `ANAT_CH05_Q010` through `ANAT_CH05_Q019`.
- Count/workload: **10 questions**, workload score **17.0**.
- Augmentation: `data/marrow/explanation_anatomy_ch05_q010_q019_v1.json`.
- Authored content checkpoint: `16f8852e5ea8757d6cbf9494237c7eb74808bb8e`.
- Reconstruction statuses: **none required** for Q10–Q19. Q14 learner-facing text avoids teaching thyroid hypoplasia as the defining DiGeorge pouch abnormality while preserving the source-keyed answer.
- Source audit carried forward: Q10 and Q13 preserve source tables; Q14–Q19 preserve source-owned figures; Q16 and Q18 are image-dependent and were audited against source payload/labels.
- Raw Marrow source remains unchanged.
- Deterministic inventory is regenerated and CI-validated: **576 enhanced / 1,539 pending**, fingerprint `09f7720c9fe9775f5e2ebc980035e5c78257664f5941a91b952b1b9263ad36ae`.
- Inventory repair commit: `7217c574640d324b88ef61b0d50f7be165af1195`.
- Engineering Gate **349** / `34607064801`: **success** on inventory-repair head `7217c574640d324b88ef61b0d50f7be165af1195`; inventory, Biochemistry/Physiology rollout validators, project memory, shared study/FSRS/sync/source/pipeline contracts passed.
- Added the required current-batch stable-ID browser regression at commit `b8127887bcc839843ffeca7bc282f42e838f8059`: Anatomy → Marrow → Chapter 5 → source-order Q18, asserting Key Takeaway, Detailed explanation, Structured text, DiGeorge syndrome, 3rd/4th pouch relationship, `label 3`, thymic region, and exactly three distractor rows. Prior Q9 and Physiology regressions remain intact.
- Engineering Gate **351** / `34607416145` started on browser-regression head `b8127887bcc839843ffeca7bc282f42e838f8059` and was in progress at checkpoint time.
- Full Android/PWA certification must be matched to the final PR head after this handoff; neighboring run 736 / `34607068608` belongs to the earlier inventory-repair head and cannot certify the final candidate.
- State: **PR_OPEN_CI_PENDING / CURRENT_UNVERIFIED**.
- Other subject workers must not start a new integration batch while this section remains current.

## Known problems / cautions

- Initial PR #37 Engineering run 340 / `34600802732` failed only because `explanation_inventory_v1.json` still described the previous 566/1,549 inventory. Its log printed the deterministic replacement manifest; commit `7217c574...` applied that exact manifest and Gate 349 then passed.
- The old sibling branch `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current` is stale and diverged from the verified Physiology lineage; do not use it.
- Never accept a neighboring green workflow run; certify only a PR's exact current product head SHA.
- Documentation-only handoff commits are not product certification. Resolve the final live PR head and require exact-head Engineering + full Android/PWA before declaring FULLY_VERIFIED.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.

## Next step

1. Resume this exact Anatomy Q10–Q19 batch; do **not** author Q20+.
2. Resolve the live PR #37 head after this checkpoint and inspect the exact-head Engineering and full Android/PWA runs.
3. Require the Q18 stable-ID browser regression plus generated product, CBT/FSRS/offline, APK/package, reproducibility, artifact and preview gates to pass on that exact candidate; production promotion remains skipped.
4. If a failure appears, make at most two bounded repairs for that exact failure class and re-certify the resulting exact head.
5. After exact-head certification succeeds, move this section to `FULLY_VERIFIED_HISTORY`, append the substantive run to `SESSION_LOG.md`, record exact artifacts/preview, release the lane, and stop without starting Q20+ in the same run.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
