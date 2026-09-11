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
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** at `125d68b`
  until the user explicitly promotes a later product baseline.
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
- Learner-facing content is **CONTENT_AUTHORED** and a dedicated stable-ID browser
  regression is committed.
- Raw Marrow source remains unchanged.
- Current augmentation contains no reconstruction-marked item in Q1–Q9.
- The committed deterministic inventory file is still the pre-batch verified manifest
  (**539 / 1,576**, fingerprint `06882f...`) and therefore has **not yet been regenerated
  for this batch**. Do not treat the current batch as STATIC_VALIDATED until inventory
  regeneration/fingerprint and the remaining static checks pass.
- PR **#34** is open for this exact bounded batch.
- Exact-head full Android/PWA run **707** / `34557657242` on head
  `64b45f91bfd4596c2e3a7745e0c19c7861819eac` failed only at the project-memory
  vocabulary gate before product checks: `STATE.md` lacked the literal `build-verified`
  concept. The subsequent exact-head Gate 329 / `34557786879` and full run 708 /
  `34557784243` on head `c180bf2bbd812308e6828359e609d470cf49db8a` also stopped at project-memory
  verification because the required literal `Next step` handoff concept was absent.
  This commit is bounded repair attempt #2 for the same project-memory vocabulary failure class.
- Engineering Gate **328** / `34557680199` was started on the superseded pre-repair
  head and cannot certify the repaired candidate.
- Production promotion remains prohibited/skipped.

## Current integration-lane status

- **Anatomy Chapter 5 Q1–Q9 is the sole CURRENT_UNVERIFIED explanation batch.**
- Other subject workers must not start a new integration batch while this state is current.
- Historical/open fully verified PRs do not block the lane; this Anatomy batch does because
  live Git state and this authoritative handoff agree on the exact unfinished scope.
- If an Anatomy worker resumes, continue this exact Q1–Q9 batch; do not append Q10+ or start
  another chapter until this batch reaches FULLY_VERIFIED.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only the PR's exact product SHA.
- The current batch was partially committed before project memory was updated. The handoff
  now records explicit CURRENT_UNVERIFIED ownership so later workers cannot mistake the lane as free.
- The inventory manifest must be regenerated deterministically from the unchanged raw source
  plus the Anatomy Q1–Q9 augmentation before certification.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines,
  alter Topics taxonomy, redesign UI, merge, or promote production.

## Exact next action / Next step

1. Resume `feature/marrow-explanation-rollout-anatomy-ch05-q01-q09-current` and PR #34.
2. Require fresh exact-head Engineering Gate and full Android/PWA runs after this repair.
3. Complete source-answer/distractor, emphasis, duplicate-ID, raw-source immutability and
   augmentation-schema checks for Q1–Q9.
4. Regenerate `data/marrow/explanation_inventory_v1.json` deterministically and record the
   new enhanced/pending totals plus fingerprint.
5. Run/confirm stable-ID browser regression and shared Practice/CBT/Review/FSRS regressions.
6. Certify only the PR's exact current head, including APK/package/reproducibility and preview.
7. If all gates pass, record the exact verified product SHA/run IDs/preview, move this batch to
   FULLY_VERIFIED_HISTORY, release the lane, and end the run without starting Q10+.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an
unverified lineage.
