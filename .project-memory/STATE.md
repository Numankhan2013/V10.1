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

- **Anatomy owns the serialized explanation lane.**
- State: **CONTENT_AUTHORED** — not yet static-validated, inventoried, PR-opened, or CI-certified.
- Branch: `feature/marrow-explanation-rollout-anatomy-ch05-q020-q024-current`.
- Exact content-authoring commit: `d5ec74c2a354dc57341569571cee11f4ed5358ea` (later memory-only commits may advance branch HEAD without changing authored product content).
- Scope: Chapter 5 **Pharyngeal arches, Skeletal & Muscular Systems**, contiguous Q20–Q24 chapter tail; **5 questions**, workload score **8.0**. Chapter 6 was not entered merely to fill target workload.
- Augmentation: `data/marrow/explanation_anatomy_ch05_q020_q024_v1.json`.
- Reconstruction status: Q22 = `resolved_reconstruction`; Q20/Q21/Q23/Q24 have no reconstruction metadata.
- Q22 preserves source key **D / Splanchnic mesoderm** while correcting a medically misleading source exception: iris sphincter/dilator are optic-cup neuroectoderm derivatives and sweat-gland myoepithelial cells are ectodermal; arrector pili must not be taught as ectoderm-derived.
- Source-owned figures/provenance remain in the immutable source layer; Q20/Q21 retain source explanation figures and Q23 is image-dependent.
- Raw Marrow source/key: unchanged.
- Deterministic inventory/fingerprint: **not regenerated yet**. Last verified baseline remains **576 enhanced / 1,539 pending**, fingerprint `09f7720c9fe9775f5e2ebc980035e5c78257664f5941a91b952b1b9263ad36ae`; do not treat that baseline fingerprint as the current batch fingerprint.
- PR: **not opened yet**.
- Exact-head Engineering Gate: **not run yet**.
- Exact-head Android/PWA workflow: **not run yet**.
- Blocker: the current automation execution environment cannot run the repository tooling locally, so deterministic inventory regeneration and static/browser validation were not claimable. This is an execution-capability checkpoint, not a medical/source blocker.

## Known problems / cautions

- The old sibling branch `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current` is stale and diverged from the verified lineage; do not use it.
- Never accept a neighboring green workflow run; certify only a PR's exact current product head SHA.
- Documentation-only handoff commits after a certified product SHA do not invalidate that exact product certification and must not be mistaken for new product candidates.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.

## Next step

1. **Resume this exact CURRENT_UNVERIFIED Anatomy Q20–Q24 batch first; no other subject may acquire the explanation lane.**
2. In a repository-capable environment, regenerate `data/marrow/explanation_inventory_v1.json` deterministically and run the runbook static/source-ownership checks, including `tools/test_marrow_explanation_inventory.py`, Anatomy rollout validation through the shared installer/inventory contract, immutable raw-source comparison, and emphasis/reconstruction schema checks.
3. Add/update stable-ID browser regression for this batch, with Q22 reconstruction-sensitive coverage and Q23 image-dependent coverage, then run shared Practice/CBT/Review/FSRS regressions.
4. Only after STATIC_VALIDATED, open/refresh the PR, certify the PR's exact current head with Engineering Gate and the full Android/PWA workflow, verify APK/package/reproducibility/preview, skip production promotion, and then move this batch to FULLY_VERIFIED_HISTORY.
5. Do not start Chapter 6 in the same run that finalizes this Chapter 5 tail.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
