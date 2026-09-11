# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Latest **fully verified** explanation product candidate remains Anatomy Chapter 5 Q10–Q19: `e045226f3a942da34102ca339fa394a930738c36` on PR #37.
- That exact Anatomy product SHA passed Engineering Gate 352 / `34607517171` and full Android/PWA 739 / `34607512312`.
- Current explanation integration lineage is the unfinished Biochemistry Chapter 12 Q1–Q9 branch `feature/marrow-explanation-rollout-biochem-ch12-q01-q09-current`.
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
- Anatomy Chapter 5 Q10–Q19 is **FULLY_VERIFIED** on PR #37, product SHA `e045226f3a942da34102ca339fa394a930738c36`; 10 questions, workload **17.0**, no reconstruction statuses required. Q10/Q13 preserve source tables; Q14–Q19 preserve source-owned figures; Q16/Q18 are image-dependent and were audited against source payload/labels. Deterministic inventory **576 enhanced / 1,539 pending**, fingerprint `09f7720c9fe9775f5e2ebc980035e5c78257664f5941a91b952b1b9263ad36ae`. Stable-ID browser regression covers Anatomy Chapter 5 Q18. Exact-head Engineering Gate **352 / 34607517171** and full Android/PWA **739 / 34607512312** both succeeded. Raw source remained unchanged and production promotion was skipped.

## CURRENT_UNVERIFIED explanation batch

- **Owner: Biochemistry. State: CONTENT_AUTHORED.**
- Batch: Chapter **12 — Lipids: Basics**, source-order **Q1–Q9**, 9 questions, workload score **16.0**.
- Augmentation file: `data/marrow/explanation_biochem_ch12_q01_q09_v1.json`.
- Content commit: `adcc3a31846cd347bfb993d09a5454f8deba5994`.
- Biochemistry rollout validator was updated to permit bounded contiguous chapter slices while retaining source-order, no-gap, source-key, distractor, emphasis and reconstruction checks; validator commit `53a8701067ac1486bdbb3e44dcf3f2c6bebcf5b6`.
- Q5 preserves the source table and molecular-structure figure through immutable source ownership. Q9 preserves the source trans-fat figure through immutable source ownership.
- Q7 is `needs_manual_review`: the rendered question omits the defining 1–4 fatty-acid mapping. The source key C (1,3) and source-supported teaching point (linoleic + alpha-linolenic acid are essential) are preserved, but the missing numeral mapping was not invented.
- Raw Biochemistry source remains unchanged at SHA-256 `d9d89966b2733f86b6c5a413e61b0af5559becff3bc580802262deb2f3b9c1ae`.
- Last certified inventory remains **576 enhanced / 1,539 pending**, fingerprint `09f7720c9fe9775f5e2ebc980035e5c78257664f5941a91b952b1b9263ad36ae`; it has **not yet been regenerated** for this batch. Expected post-regeneration count is **585 enhanced / 1,530 pending**.
- No PR or exact-head Engineering Gate / Android-PWA certification exists yet for this batch.
- Other subject workers must yield the serialized explanation lane until this exact batch becomes FULLY_VERIFIED or is explicitly abandoned/reverted.

## Known problems / cautions

- The old sibling branch `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current` is stale and diverged from the verified lineage; do not use it.
- Do not treat historical open PR #37 as a blocker; its exact product candidate is in `FULLY_VERIFIED_HISTORY`.
- Never accept a neighboring green workflow run; certify only a PR's exact current product head SHA.
- Documentation-only handoff commits after a certified product SHA do not invalidate that exact product certification and must not be mistaken for new product candidates.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.

## Next step

1. Resume **this exact Biochemistry Chapter 12 Q1–Q9 batch**; do not start Q10+ yet.
2. Regenerate the deterministic 2,115-ID inventory and verify **585 enhanced / 1,530 pending**, unchanged raw-source hashes, and the new fingerprint.
3. Run the Biochemistry rollout/source-key/emphasis/distractor/reconstruction checks and the shared static regressions.
4. Add a stable-ID browser regression for the reconstruction-sensitive Chapter 12 Q7 (or another representative current-batch question if the runbook evidence requires it), then run shared Practice/CBT/Review/FSRS browser regressions.
5. Only after static validation, open/refresh the PR and certify the PR's exact current head through Engineering Gate and full Android/PWA/APK/package/reproducibility/preview checks. Production promotion remains skipped.
6. After FULLY_VERIFIED, release the lane. Biochemistry's next source-order start will then be **Chapter 12 Q10**.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
