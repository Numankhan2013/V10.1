# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-anatomy-ch05-q01-q09-current`.
- Latest **fully verified** explanation product candidate is Anatomy Chapter 5 Q1–Q9:
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
- build-verified, device-verified, and accepted are separate states. This Anatomy
  batch is build-verified; it is not thereby device-verified or an accepted baseline.

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

- Anatomy approved reference before this batch: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** verified on the stacked lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapters 5–9 are fully verified; Chapter 9 exact verified product SHA
  `7974b8eee842f668e9fb4fac95783ac64893e98d`, Gate 327, full run 701.
- Anatomy Chapter 5 Q1–Q9 is now **FULLY_VERIFIED**.
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

## Current integration-lane status

- There is **no CURRENT_UNVERIFIED explanation batch** after the Anatomy Q1–Q9 verification.
- PR #34 may remain open historically; its mere open state does **not** block the lane.
- The serialized explanation lane is released for the next subject worker.
- The next Anatomy source-order start is Chapter 5 **Q10**, subject to dynamic
  source/workload re-audit before any new batch is created.

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

1. Re-resolve live explanation lineage, open PRs and `STATE.md` before any write.
2. If no other subject has acquired a new CURRENT_UNVERIFIED batch, the configured
   subject may select its exact next incomplete source-order questions using the
   runbook workload algorithm.
3. For Anatomy specifically, begin from Chapter 5 Q10 only after dynamic source audit;
   do not hardcode a later range or skip difficult questions.
4. Keep production promotion skipped and preserve the accepted V11.6 baseline unless
   the user explicitly changes it.

Efficiency rule: pre-audit future content while CI runs, but never commit another
batch on an unverified lineage.
