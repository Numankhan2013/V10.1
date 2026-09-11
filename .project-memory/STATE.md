# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-anatomy-ch05-q01-q09-current`.
- Latest **fully verified** explanation product candidate before the current batch is Physiology Chapter 9:
  `7974b8eee842f668e9fb4fac95783ac64893e98d`.
- Physiology Chapter 9 exact-candidate verification: Engineering Gate **327** / `34534383189` and
  full Android/PWA run **701** / `34534378465` both passed on that same SHA.
- Latest immutable verified preview: `https://5dc3071d.nk-qbank.pages.dev`.
- Production promotion was skipped.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** until the user explicitly promotes a later product baseline.
- Accepted product commit: `125d68b`
- build-verified, device-verified, and accepted are separate states; the current Anatomy batch
  is not yet build-verified or device-verified.

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

## Fully verified explanation history

- Anatomy approved reference: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** verified on the stacked lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapters 5–9 are fully verified; Chapter 9 exact verified product SHA
  `7974b8eee842f668e9fb4fac95783ac64893e98d`, Gate 327, full run 701.
- Latest **fully verified deterministic inventory** before the current Anatomy batch:
  **539 enhanced / 1,576 pending**.
- Verified pre-batch inventory fingerprint:
  `06882fcd885436ebd15e38c2ff950de267d164434dc4050ca60d0841ca5dd131`.

## CURRENT_UNVERIFIED — Anatomy Chapter 5 Q1–Q9

- Owner: **Anatomy**.
- Branch: `feature/marrow-explanation-rollout-anatomy-ch05-q01-q09-current`.
- Scope: Chapter 5 **Pharyngeal arches, Skeletal & Muscular Systems**, Q1–Q9 only.
- Augmentation file: `data/marrow/explanation_anatomy_ch05_q001_q009_v1.json`.
- Scope metadata records workload score **16.5** and 9 contiguous source-order questions.
- Learner-facing content is **CONTENT_AUTHORED** and a dedicated stable-ID browser regression is committed.
- Raw Marrow source remains unchanged; Q1–Q9 contain no reconstruction-marked item.
- Deterministic inventory has now been regenerated for this batch: **548 enhanced / 1,567 pending**.
- Current inventory fingerprint: `3ac131bdd442b649b7778260565f43156e3bf1c04ef4717c3a6c8b82bf30c4fc`.
- Source hashes and review-flag counts are unchanged from the pre-batch inventory.
- PR **#34** is open for this exact bounded batch.
- Earlier exact-head runs 707/708 and Gates 329/330 failed only on project-memory vocabulary requirements; those requirements are now repaired.
- Engineering Gate **331** / `34563798787` on head `304ef3bf88f9ba37d09395bc206abf534b6d2d4d` passed project-memory, verification preflight, Python compile, study metrics, Custom Study Modules, cross-device/PWA, FSRS, Marrow source, image registry and Topics taxonomy, then failed exactly at `Validate Marrow explanation inventory` because the committed manifest was still the pre-batch 539/1,576 version.
- Gate 331 itself printed the deterministic expected manifest: **548 / 1,567**, fingerprint `3ac131bd...`; that exact generated manifest is now committed.
- Production promotion remains prohibited/skipped.

## Current integration-lane status

- **Anatomy Chapter 5 Q1–Q9 is the sole CURRENT_UNVERIFIED explanation batch.**
- Other subject workers must not start a new integration batch while this state is current.
- Historical/open fully verified PRs do not block the lane; this Anatomy batch does because live Git state and this authoritative handoff agree on the unfinished scope.
- If an Anatomy worker resumes, continue this exact Q1–Q9 batch; do not append Q10+ or start another chapter until this batch reaches FULLY_VERIFIED.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only the PR's exact current head SHA.
- Inventory drift from the newly added nine augmentation IDs has been repaired; fresh exact-head CI is still required.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines,
  alter Topics taxonomy, redesign UI, merge, or promote production.

## Exact next action / Next step

1. Re-resolve PR #34 head after this memory/inventory checkpoint.
2. Confirm deterministic inventory validation now passes and complete the remaining source-answer/distractor, emphasis, duplicate-ID, raw-source immutability and augmentation-schema checks for Q1–Q9.
3. Run/confirm stable-ID browser regression and shared Practice/CBT/Review/FSRS regressions.
4. Require fresh exact-head Engineering Gate and full Android/PWA workflow on the PR's exact current head.
5. Certify APK/package/reproducibility and preview only from that exact head; production promotion stays skipped.
6. If all gates pass, record the exact verified product SHA/run IDs/preview, move this batch to FULLY_VERIFIED_HISTORY, release the lane, and end without starting Q10+.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
