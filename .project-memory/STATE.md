# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation work is on
  `feature/marrow-explanation-rollout-physio-ch09-current` / PR #33.
- Latest **fully verified** explanation lineage remains Physiology Chapter 8 on PR #27:
  candidate `0a1f31f9dd1689ef6be73948a3e77262ec5b2ff2`.
- Chapter 8 verification: Engineering Gate **266** and full Android/PWA run
  **561** (`34367467186`) both passed.
- Latest immutable verified preview: `https://afdceb7d.nk-qbank.pages.dev`.
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

## Fully verified explanation history

- Anatomy approved reference: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** complete on the stacked lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapter 5 — Body Fluids: **28/28**, verified Gate 259 / full run 539.
- Physiology Chapter 6 — Physiology of Nerve: **34/34**, verified Gate 262 / full run 549.
- Physiology Chapter 7 — Muscle Physiology I: **35/35**, verified Gate 265 / full run 556.
- Physiology Chapter 8 — Muscle Physiology II: **14/14**, verified Gate 266 / full run 561.
- Latest **fully verified deterministic inventory** after Chapter 8:
  **512 enhanced / 1,603 pending**.
- Verified Chapter 8 inventory fingerprint:
  `8d35e1f870a1c414c1546327858d464055717fd0edf2eac683daa7e277ae10bf`.

## CURRENT_UNVERIFIED — exact resume point

Physiology Chapter 9 — **Synapse and Junctional Transmission** is the sole current
unfinished explanation batch and continues to own the serialized integration lane.

Content/source status:
- **27/27 learner-facing augmentation records** exist in
  `data/marrow/explanation_physio_ch09_v1.json`.
- Original content checkpoint: `9c7cf3f73320673f59ad0328cb9374085fd2e28a`.
- Canonical Chapter 9 source JSONL was re-audited against its visually reviewed
  printed answer-key mappings; augmentation rationale keys match the three
  non-source-keyed options.
- Reconstruction-marked items remain:
  - Q1: `needs_manual_review` — numbered statements absent from imported block;
  - Q5: `needs_manual_review` — stored option `DOPA` creates a second classification
    problem and may be OCR/truncation of dopamine; raw source key A remains unchanged;
  - Q24: `resolved_reconstruction` — corrupted opioid receptor symbols restored to
    standard δ/κ/μ terminology with raw source/key unchanged.

Deterministic/static validation progress:
- Added a fail-informative inventory-drift diagnostic at commit
  `4080279cb998250a43b29d84338a3df5417a8bd7`.
- Regenerated `data/marrow/explanation_inventory_v1.json` at commit
  `440c41b3c1b00e1cc260d6738e95a70429899166`.
- Current Chapter 9 candidate inventory is **539 enhanced / 1,576 pending** with
  fingerprint `06882fcd885436ebd15e38c2ff950de267d164434dc4050ca60d0841ca5dd131`.
- Raw source hashes and global triage-flag counts are unchanged.
- Previous PR head `c45a0b793d07624f33606ae30ef36b930ee521ad` passed exact-head
  Engineering Gate 324 / `34517248792` and full Android/PWA run 698 /
  `34517243286`. Those runs establish the pre-browser-regression baseline only;
  they do not certify the changed current head.
- The missing Chapter 9-specific generated-app browser proof was added at commit
  `19d5c567124689570ed8ed37e3c735f6e39c6bef` in
  `tools/verify_recall_dock_browser.py`. It selects Physiology Chapter 9 using
  canonical `window.QB.openChapter('9')` identity, opens Q24, verifies the
  learner-facing δ/κ/μ opioid-receptor reconstruction plus exactly three wrong-option
  rationales, and captures `physiology-ch09-q24-opioid-reconstruction.png`.

**Do not call Chapter 9 FULLY_VERIFIED yet.** This memory checkpoint changes the PR
head after the browser-regression commit. Freeze the resulting exact head and require
BOTH Engineering Gate and the full Android/PWA workflow to pass that final head,
including the new Q24 browser assertion, APK/package/reproducibility checks and preview
deployment. Then append the final verification record to `SESSION_LOG.md` and refresh
this state with exact final head/run IDs/preview before releasing the lane.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only the PR's **exact
  current head SHA**.
- Browser topic selectors based on substring text are unsafe. Prefer stable chapter
  identity such as `button.nk-topic-row[onclick="window.QB.openChapter('9')"]`.
- Pre-commit emphasis validation is case-sensitive; fix the anchor, not medical content.
- A source key may be the best available answer while its explanation is medically
  imprecise. Preserve the raw key and teach the correct distinction in augmentation.
- Missing numbered statements should be reconstructed only to the level actually
  recoverable. Do not fabricate verbatim text.
- Keep image integration as a separate workstream.
- Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, or
  promote production during explanation refinement.

## Next step

Resume **Chapter 9 verification**, not Chapter 10:
1. freeze the current PR #33 exact head after this checkpoint;
2. require exact-head Engineering Gate + full Android/PWA browser/APK/package/
   reproducibility/deploy success;
3. confirm the full run executes the new Chapter 9 Q24 browser regression successfully;
4. append `SESSION_LOG.md` with the completed Chapter 9 verification session and
   refresh this state with exact final head/run IDs/preview;
5. only after all of the above may Chapter 9 be labeled **FULLY_VERIFIED** and the
   serialized lane released for another subject/new batch.

Efficiency rule: pre-audit the next chapter while CI runs, but **never commit the
next chapter onto an unverified lineage**.
