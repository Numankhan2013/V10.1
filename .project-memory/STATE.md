# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation work is on
  `feature/marrow-explanation-rollout-physio-ch09-current`.
- Latest **fully verified** explanation lineage is Physiology Chapter 8 on PR #27:
  candidate `0a1f31f9dd1689ef6be73948a3e77262ec5b2ff2`.
- Chapter 8 verification: Engineering Gate **266** and full Android/PWA run
  **561** (`34367467186`) both passed.
- Latest immutable verified preview:
  `https://afdceb7d.nk-qbank.pages.dev`.
- Production promotion was skipped.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** at
  `125d68b` until the user explicitly promotes a later product baseline.
- Accepted product commit: `125d68b`.
- Build-verified, device-verified and accepted baseline are separate states.

## Current Marrow bank

Shared architecture:
`MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
There is one shared Practice/CBT/Review/FSRS/sync/module/analytics/navigation
engine; explanation work must not fork it by subject.

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

Every refined four-option SBA should have:
- one meaningful Key Takeaway;
- source-faithful, medically correct structured display text;
- 1–4 selective emphasis anchors that occur verbatim in display text;
- exactly three concise rationales keyed to the three incorrect source options;
- source tables/figures/provenance kept source-owned and separate;
- reconstruction metadata when source text is garbled, incomplete or medically
  inconsistent but can be recovered from source evidence and/or standard
  MBBS/USMLE/NEET-PG/INI-CET-level literature.

Reconstruction metadata must include:
`status`, `sourceProblem`, `reconstructedContent`, `evidenceBasis`,
and `reviewNote`. Use `resolved_reconstruction` only when the defect is
actually resolved; otherwise keep `needs_manual_review`.

## Verified explanation progress

- Anatomy approved reference: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** complete on the stacked
  explanation lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapter 5 — Body Fluids: **28/28**, verified Gate 259 / run 539.
- Physiology Chapter 6 — Physiology of Nerve: **34/34**, verified Gate 262 /
  run 549. Reconstruction provenance introduced and browser-tested on Q23.
- Physiology Chapter 7 — Muscle Physiology I: **35/35**, verified Gate 265 /
  run 556. Q10/Q20/Q23/Q34 resolved reconstructions; Q35 remains
  `needs_manual_review` because missing numbered statement wording was not
  invented.
- Physiology Chapter 8 — Muscle Physiology II: **14/14**, verified Gate 266 /
  run 561. Q13 resolved reconstruction teaches receptor/tissue-dependent
  autonomic smooth-muscle effects.
- Latest **verified deterministic inventory** after Chapter 8:
  **512 enhanced / 1,603 pending**.
- Verified Chapter 8 inventory fingerprint:
  `8d35e1f870a1c414c1546327858d464055717fd0edf2eac683daa7e277ae10bf`.

## Current unverified work — exact resume point

Physiology Chapter 9 — **Synapse and Junctional Transmission**:
- **27/27 learner-facing augmentation records authored and committed** in
  `data/marrow/explanation_physio_ch09_v1.json`.
- Content checkpoint commit: `9c7cf3f73320673f59ad0328cb9374085fd2e28a`.
- Reconstruction-marked items:
  - Q1: `needs_manual_review` — numbered statements absent from imported block;
  - Q5: `needs_manual_review` — stored option `DOPA` creates a second
    classification problem and may be OCR/truncation of dopamine;
  - Q24: `resolved_reconstruction` — corrupted opioid receptor symbols restored
    to standard δ/κ/μ terminology.
- **Do not call Chapter 9 verified yet.** No Chapter 9 inventory update, browser
  regression, PR, Engineering Gate or full Android/PWA certification has been
  completed after the content commit.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only the PR's **exact
  current head SHA**.
- Browser topic selectors based on substring text are unsafe:
  `Muscle Physiology I` also matched `Muscle Physiology II`.
  Prefer stable chapter identity such as
  `button.nk-topic-row[onclick="window.QB.openChapter('7')"]`.
- Pre-commit emphasis validation is case-sensitive. Several batches caught only
  exact-string capitalization/phrase mismatches; fix the anchor, not the medical
  content.
- A source key may be the best available answer while its explanation is
  medically imprecise. Preserve the raw key, but teach the correct distinction
  in augmentation and provenance.
- Missing numbered statements should be reconstructed only to the level actually
  recoverable. Do not fabricate verbatim text.
- Keep image integration as a separate workstream owned by the primary agent.
- Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, or
  promote production during explanation refinement.

## Next step

Resume **Chapter 9 validation**, not Chapter 10:
1. audit all 27 Q9 records against actual source correct-option letters;
2. confirm exactly three non-keyed rationales and all emphasis anchors;
3. validate the three reconstruction records and statuses;
4. recompute deterministic 2,115-ID inventory and fingerprint;
5. add one stable-ID live browser regression, preferably a reconstruction case;
6. open the bounded Chapter 9 PR stacked on verified Chapter 8;
7. freeze to the PR exact head and require Engineering Gate + full Android/PWA
   browser/APK/package/reproducibility/deploy success;
8. only then begin Physiology Chapter 10.

Efficiency rule: pre-audit the next chapter while CI runs, but **never commit the
next chapter onto an unverified lineage**.
