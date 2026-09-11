# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-physio-ch10-q001-q013-current`.
- Latest **fully verified** explanation product candidate is Physiology Chapter 10 Q1–Q13:
  `45cda2196c40d30eaf9283b031cba3942ed2e132`.
- Exact-candidate verification: Engineering Gate **336** / `34580097242` and
  full Android/PWA run **719** / `34580093798` both passed on that same SHA.
- Full-run artifact `V11.7-android-pwa`: ID `10191339526`, digest
  `sha256:79355c9c23135053f457092d5256b923ccfa4eb787bbc0e79265ab411e46c42b`.
- Browser/screenshot artifact: ID `10191308077`, digest
  `sha256:999c4a92fb9dc80fa07d7f5702ccd1fecd0f24f1811669e24c9c5155a69f2d5f`.
- Immutable verified preview: `https://ff02ca04.nk-qbank.pages.dev`.
- Production promotion was skipped.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** until the user explicitly promotes a later product baseline.
- Accepted product commit: `125d68b`
- build-verified, device-verified, and accepted are separate states.

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

- Anatomy approved reference before Chapter 5 rollout: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** verified on the stacked lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapters 5–9 are fully verified; Chapter 9 exact verified product SHA
  `7974b8eee842f668e9fb4fac95783ac64893e98d`, Gate 327, full run 701.
- Anatomy Chapter 5 Q1–Q9 is **FULLY_VERIFIED**.
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
- Physiology Chapter 10 Q1–Q13 is **FULLY_VERIFIED**.
  - PR: **#35**.
  - Product SHA: `45cda2196c40d30eaf9283b031cba3942ed2e132`.
  - Scope: Chapter 10 **Neurotransmitters**, Q1–Q13 contiguous source order.
  - Count/workload: **13 questions**, workload score **18.5**.
  - Augmentation: `data/marrow/explanation_physio_ch10_q001_q013_v1.json`.
  - Q13 reconstruction status: `resolved_reconstruction`; learner-facing content
    preserves the standard eccrine sweat-gland sympathetic postganglionic
    cholinergic exception without teaching outdated nonessential extensions.
  - Raw Marrow source stayed unchanged.
  - Deterministic inventory: **561 enhanced / 1,554 pending**.
  - Inventory fingerprint:
    `773c057042d6b6ab17dec12817f4a174c30e989036b4e5d43af5ef3e9061dfa0`.
  - Stable-ID browser regression verified Physiology → Marrow → Chapter 10 → Q13,
    learner-facing reconstruction, and exactly three wrong-option rationales.
  - Engineering Gate **336** / `34580097242`: success on exact product SHA.
  - Full Android/PWA **719** / `34580093798`: success on the same exact SHA.
  - Generated product, Practice/CBT/Review/FSRS/shared regressions, browser,
    APK/package, reproducibility, artifact upload and preview deployment passed.
  - Full-run artifact `V11.7-android-pwa`: ID `10191339526`, digest
    `sha256:79355c9c23135053f457092d5256b923ccfa4eb787bbc0e79265ab411e46c42b`.
  - Browser/screenshot artifact: ID `10191308077`, digest
    `sha256:999c4a92fb9dc80fa07d7f5702ccd1fecd0f24f1811669e24c9c5155a69f2d5f`.
  - Immutable preview: `https://ff02ca04.nk-qbank.pages.dev`.
  - Production promotion skipped.

## CURRENT_UNVERIFIED explanation batch

- **None.**
- Physiology Chapter 10 Q1–Q13 has moved to `FULLY_VERIFIED_HISTORY`.
- No Q14–Q18 content was authored or committed in the finalization run.

## Current integration-lane status

- The serialized explanation lane is **released**.
- Historical open PRs/branches, including PR #34 and any already-certified PR,
  are non-blocking even if GitHub still reports them open.
- Every worker must re-resolve newest authoritative `STATE.md` plus live Git/PR/head
  state before claiming the lane.
- An earlier empty branch named `feature/marrow-explanation-rollout-physio-ch10-q001-q014-current`
  remains **STALE_HISTORY / non-authoritative** and must not be treated as lane ownership.

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

1. Re-resolve live explanation-lane ownership before doing any new content work.
2. If Physiology next acquires the free lane, dynamically workload-score the exact
   next source-order incomplete range beginning at **Physiology Chapter 10 Q14**;
   do not assume a hardcoded batch boundary beyond the runbook limits.
3. Start at most one bounded new batch, preserve raw source immutability, and follow
   the full source-audit → augmentation → deterministic inventory → static/shared
   validation → stable-ID browser → exact-head Engineering + Android/PWA sequence.
4. Keep production promotion skipped and preserve the accepted V11.6 baseline unless
   the user explicitly changes it.

Efficiency rule: pre-audit future content while CI runs, but never commit another
batch on an unverified lineage.
