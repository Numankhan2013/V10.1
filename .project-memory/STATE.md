# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Latest **fully verified** explanation product candidate is Anatomy Chapter 5 Q10–Q19: `e045226f3a942da34102ca339fa394a930738c36` on PR #37.
- That exact product SHA passed Engineering Gate 352 / `34607517171` and full Android/PWA 739 / `34607512312`.
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

- **Biochemistry Chapter 12 Q1–Q10** currently owns the serialized explanation lane on branch `feature/marrow-explanation-rollout-biochem-ch12-q001-q010-current`.
- Source-order range: `marrow__BIOCHEM_CH12_Q001` through `marrow__BIOCHEM_CH12_Q010`; 10 newly enhanced questions; workload score **16.0**. Chapter 12 Q11 is already an approved gold-sample question and is not duplicated.
- Raw Biochemistry source SHA remains expected at `d9d89966b2733f86b6c5a413e61b0af5559becff3bc580802262deb2f3b9c1ae`.
- Q7 is `needs_manual_review`: the printed item retains numeric-combination options but the numbered statement list is absent. Learner-facing augmentation teaches only the source-supported semantic answer (linoleic acid + α-linolenic acid), preserves source key C (1,3), and does not invent the missing mapping.
- Q5 preserves the source PUFA comparison table and arachidonic-acid figure; Q9 preserves the source trans-fat configuration figure. Explanation automation does not mutate image bindings/assets.
- Content file: `data/marrow/explanation_biochem_ch12_q001_q010_v1.json`.
- Biochemistry validator was updated to permit workload-bounded contiguous chapter slices while enforcing a gap-free source-order prefix when approved gold-sample IDs are included.
- Inventory before this batch is **576 enhanced / 1,539 pending**, fingerprint `09f7720c9fe9775f5e2ebc980035e5c78257664f5941a91b952b1b9263ad36ae`; expected count after this batch is **586 / 1,529**. Deterministic regenerated fingerprint is still pending validation.
- PR/exact-head Engineering Gate/full Android-PWA verification: **pending**. This batch is not FULLY_VERIFIED yet and blocks later explanation integration until resolved.

## Known problems / cautions

- The old sibling branch `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current` is stale and diverged from the verified lineage; do not use it.
- Never accept a neighboring green workflow run; certify only the current PR product head SHA.
- Documentation-only handoff commits after a certified product SHA do not invalidate that exact product certification and must not be mistaken for new product candidates.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.

## Next step

1. Complete static/inventory validation for the current Biochemistry Chapter 12 Q1–Q10 batch; regenerate the deterministic inventory without touching raw source.
2. Add/execute a stable-ID browser regression for one current-batch question, with Q7 preferred because it exercises the source-omission reconstruction contract.
3. Open/refresh the PR and require exact-head Engineering Gate plus exact-head Android/PWA success, APK/package/reproducibility checks, preview deployment, and production promotion skipped.
4. On FULLY_VERIFIED, move this batch into `FULLY_VERIFIED_HISTORY`, release the lane, and set the next Biochemistry source-order start to Chapter 12 Q12 (Q11 is already approved in the gold sample).

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
