# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-rebased-current`.
- Latest **fully verified** explanation product candidate remains Physiology Chapter 10 Q14–Q18: `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`.
- Exact-candidate verification: Engineering Gate **338** / `34591048655` and full Android/PWA **724** / `34591045176` both passed on that exact SHA.
- Full-run artifact `V11.7-android-pwa`: ID `10195721333`, digest `sha256:4982c285174125aecb7434afe133d6772d1db6f7cc266dba499c622c2972f536`.
- Browser/screenshot artifact: ID `10195700442`, digest `sha256:099ab9602bd3cec93396b9604fd6a20b24b308fc0a61ed2e275f3904f2842911`.
- Immutable verified preview: `https://ea6c7b4b.nk-qbank.pages.dev`.
- Production promotion was skipped.
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

Every refined four-option SBA should have one meaningful Key Takeaway; medically correct structured display text; 1–4 verbatim emphasis anchors; exactly three wrong-option rationales keyed to the three incorrect source options; source-owned figures/tables/provenance; and reconstruction metadata when source defects are recovered.

## FULLY_VERIFIED_HISTORY

- Anatomy approved reference before Chapter 5 rollout: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** verified on the stacked lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapters 5–9 are fully verified; Chapter 9 exact verified product SHA `7974b8eee842f668e9fb4fac95783ac64893e98d`, Gate 327, full run 701.
- Anatomy Chapter 5 Q1–Q9 is **FULLY_VERIFIED** on PR #34, product SHA `1921d758b19d0804438f434aaca950fa32d419ea`, Gate 333 / `34567801778`, full run 712 / `34567798753`; inventory then **548 / 1,567**.
- Physiology Chapter 10 Q1–Q13 is **FULLY_VERIFIED** on PR #35, product SHA `45cda2196c40d30eaf9283b031cba3942ed2e132`, Gate 336 / `34580097242`, full run 719 / `34580093798`; Q13 is `resolved_reconstruction`.
- Physiology Chapter 10 Q14–Q18 is **FULLY_VERIFIED** on PR #36.
  - Product SHA: `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`.
  - Q15: `resolved_reconstruction`; Q14/Q16/Q17/Q18: no reconstruction metadata.
  - Deterministic inventory: **566 enhanced / 1,549 pending**.
  - Inventory fingerprint: `991a2c84500ee94e52a3d09f0f47ed7b77b3057ff2ff7d9a1842594ec387cf78`.
  - Engineering Gate **338** / `34591048655`: success.
  - Full Android/PWA **724** / `34591045176`: success.
  - APK/package/reproducibility/preview passed; production promotion skipped.

## CURRENT_UNVERIFIED explanation batch

- Owner: **Anatomy**.
- Batch ID: `anatomy-20260911-ch05-q10-q19`.
- Branch: `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-rebased-current`.
- Base lineage: latest verified Physiology Chapter 10 Q14–Q18 handoff (`1ff957f5f244f1ab649d6e38fbb21db61b21c308`; product certification remains anchored to `e12a36f3eda07cea7b89920a75e7c9e259d3c2fd`).
- Chapter 5: **Pharyngeal arches, Skeletal & Muscular Systems**.
- Exact source-order range: **Q10–Q19** / IDs `ANAT_CH05_Q010` through `ANAT_CH05_Q019`.
- Count/workload: **10 questions**, workload score **17.0**.
- Augmentation: `data/marrow/explanation_anatomy_ch05_q010_q019_v1.json`.
- Rebased content checkpoint: `16f8852e5ea8757d6cbf9494237c7eb74808bb8e`.
- Transplant note: medical learner-facing text is unchanged from the previously authored Q10–Q19 batch; only rollout metadata was advanced to the latest verified lineage (`approvedBeforeBatch=566`, Physiology enhanced reference `236`, scope status `approved-rollout`).
- Source audit carried forward: Q10 and Q13 preserve source tables; Q14–Q19 preserve source-owned figures; Q16 and Q18 are image-dependent and were previously audited against exact source payload/labels.
- Reconstruction statuses: **none required** for Q10–Q19. Q14 learner-facing text avoids teaching thyroid hypoplasia as the defining DiGeorge pouch abnormality while preserving the source-keyed answer.
- Raw Marrow source stayed unchanged.
- Pre-batch deterministic inventory is **566 enhanced / 1,549 pending**, fingerprint `991a2c84500ee94e52a3d09f0f47ed7b77b3057ff2ff7d9a1842594ec387cf78`.
- Expected inventory after successful deterministic regeneration: **576 enhanced / 1,539 pending** if all 10 IDs validate uniquely; fingerprint not yet generated.
- Pre-commit content checks from the authored batch: 10/10 expected IDs; 1–4 emphasis anchors occur verbatim; exactly three rationale keys per item; rationale keys equal the three non-source-keyed options.
- PR: not yet opened.
- Exact-head Engineering Gate: not yet run.
- Exact-head Android/PWA: not yet run.
- State: **CONTENT_AUTHORED / CURRENT_UNVERIFIED**.
- Other subject workers must not start a new integration batch while this section remains current.

## Known problems / cautions

- The old sibling branch `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current` is stale and diverged from the verified Physiology lineage; do not use its handoff/inventory as current authority.
- Never accept a neighboring green workflow run; certify only a PR's exact product head SHA.
- Documentation-only `[skip ci]` handoff commits may follow a verified product SHA; do not pretend the later documentation head itself was APK/package certified.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.
- ROADMAP/FINE_TUNING historical prose may lag the newest verified checkpoint; `STATE.md` + live Git/CI are authoritative for immediate lane ownership.

## Next step

1. Resume this exact Anatomy Q10–Q19 batch; do **not** author Q20+.
2. Run repository-native source-ID/chapter/count, source-key/distractor, emphasis, duplicate-ID, reconstruction-schema and raw-source immutability validation on the rebased lineage.
3. Regenerate the deterministic 2,115-ID explanation inventory and require exactly **576 enhanced / 1,539 pending** with unchanged raw-source hashes; record the new fingerprint.
4. Add/update one stable-ID Chapter 5 browser regression representative of this batch, preferably image-dependent Q18 or histology Q16, without altering shared Practice/CBT/Review/FSRS behavior.
5. Run shared static/local regressions, then open the bounded PR and require exact-head Engineering Gate plus full Android/PWA/APK/package/reproducibility/preview certification.
6. Keep production promotion skipped. After exact-head certification succeeds, move this section to FULLY_VERIFIED_HISTORY and release the serialized lane.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
