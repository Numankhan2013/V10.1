# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Latest **fully verified** explanation product candidate is Biochemistry Chapter 12 Q1–Q10: `dae7b048c0997bb70737b2d0ab5b0fec91fb79a0` on PR #40.
- Exact product SHA passed Engineering Gate 384 / `34633177553` and full Android/PWA 790 / `34633172786`.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** until explicitly promoted.
- Accepted product commit: `125d68b`.
- build-verified, device-verified, and accepted baseline are separate states.

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

Canonical procedure: `docs/MARROW_EXPLANATION_FINE_TUNING.md`; unattended execution protocol: `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md`.
Each refined four-option SBA requires a meaningful Key Takeaway, medically correct structured display text, 1–4 verbatim emphasis anchors, exactly three wrong-option rationales keyed to incorrect source options, preserved source figures/tables/provenance, and reconstruction metadata when source defects are recovered.

## FULLY_VERIFIED_HISTORY

- Anatomy approved reference before Chapter 5 rollout: **62**.
- Biochemistry Chapters **1–11** verified before the current batch; historical enhanced count **259**.
- Physiology approved pilot: **80** across Chapters 1–4; Chapters 5–9 fully verified.
- Anatomy Chapter 5 Q1–Q9: PR #34, product SHA `1921d758b19d0804438f434aaca950fa32d419ea`, Gate 333 / `34567801778`, full 712 / `34567798753`.
- Physiology Chapter 10 Q1–Q13: PR #35, product SHA `45cda2196c40d30eaf9283b031cba3942ed2e132`, Gate 336 / `34580097242`, full 719 / `34580093798`; Q13 `resolved_reconstruction`.
- Physiology Chapter 10 Q14–Q18: PR #36, product SHA `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`; Q15 `resolved_reconstruction`; inventory **566 / 1,549**, fingerprint `991a2c84500ee94e52a3d09f0f47ed7b77b3057ff2ff7d9a1842594ec387cf78`; Gate 338 and full 724 passed; production skipped.
- Anatomy Chapter 5 Q10–Q19: PR #37, product SHA `e045226f3a942da34102ca339fa394a930738c36`; 10 questions, workload **17.0**; inventory **576 / 1,539**, fingerprint `09f7720c9fe9775f5e2ebc980035e5c78257664f5941a91b952b1b9263ad36ae`; stable-ID browser Q18; Gate 352 / `34607517171` and full 739 / `34607512312` passed; production skipped.
- **Biochemistry Chapter 12 Q1–Q10: FULLY_VERIFIED on PR #40**, product SHA `dae7b048c0997bb70737b2d0ab5b0fec91fb79a0`; 10 questions, workload **16.0**. Q5 preserves the source PUFA comparison table and arachidonic-acid figure; Q9 preserves the trans-fat figure. Q7 is `needs_manual_review`: the printed item omits the numbered statement list, so augmentation teaches only the source-supported semantic answer (linoleic acid + α-linolenic acid), preserves source key C `(1,3)`, and does not invent the missing mapping. Deterministic inventory **586 enhanced / 1,529 pending**, fingerprint `57a6ce84d7f64de83229c07b7dbdac9b17eb3f4b26db14fd848e490ba6c532eb`; Biochemistry raw SHA remained `d9d89966b2733f86b6c5a413e61b0af5559becff3bc580802262deb2f3b9c1ae`. Stable-ID browser regression covers Chapter 12 Q7 and its omission/reconstruction contract. Exact-head Gate **384 / 34633177553** and full Android/PWA **790 / 34633172786** passed. Screenshot artifact `10276867533`; Android/PWA artifact `10277781316`. Preview: `https://f768d0bf.nk-qbank.pages.dev` (alias `https://feature-marrow-explanation-r-o067.nk-qbank.pages.dev`). APK/package/reproducibility checks passed and production promotion was skipped.

## CURRENT_UNVERIFIED explanation batch

- **None.** The serialized explanation lane is released.
- Open historical/stacked PRs already recorded above as FULLY_VERIFIED do not block a later subject worker.
- A documentation-only handoff commit after the certified product SHA is not a new product candidate and does not replace the exact-head certification above.

## Known problems / cautions

- The old sibling branch `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current` is stale and diverged from the verified lineage; do not use it.
- Never certify a neighboring green workflow run; only the recorded product SHA's exact-head runs count.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.

## Next step

- Next incomplete **Biochemistry** source-order item is **Chapter 12 Q12**; Q11 is already an approved gold-sample question and must not be duplicated.
- A later explanation worker must first re-resolve the newest authoritative lineage and lane ownership, then may start one bounded batch if no CURRENT_UNVERIFIED owner exists.
- Production remains untouched unless the user explicitly authorizes promotion.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
