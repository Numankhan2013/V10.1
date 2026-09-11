# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-physio-ch09-current` / PR #33.
- Latest **fully verified** explanation product candidate is Physiology Chapter 9:
  `7974b8eee842f668e9fb4fac95783ac64893e98d`.
- Exact-candidate verification: Engineering Gate **327** / `34534383189` and
  full Android/PWA run **701** / `34534378465` both passed on that same SHA.
- Run 701 also passed the dedicated Chapter 9 Q24 browser regression,
  APK/package checks, reproducibility manifest, artifact upload, and Cloudflare
  preview deployment.
- Latest immutable verified preview: `https://5dc3071d.nk-qbank.pages.dev`.
- Production promotion was skipped.
- The docs-only handoff commit after the verified product SHA does not redefine
  the certified product candidate; verification remains anchored to `7974b8e`.
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

Use `resolved_reconstruction` only when the defect is actually resolved;
otherwise keep `needs_manual_review`.

## Fully verified explanation history

- Anatomy approved reference: **62**.
- Biochemistry enhanced: **259**; Chapters **1–11** complete on the stacked lineage.
- Physiology approved pilot: **80** across Chapters 1–4.
- Physiology Chapter 5 — Body Fluids: **28/28**, verified Gate 259 / full run 539.
- Physiology Chapter 6 — Physiology of Nerve: **34/34**, verified Gate 262 / full run 549.
- Physiology Chapter 7 — Muscle Physiology I: **35/35**, verified Gate 265 / full run 556.
- Physiology Chapter 8 — Muscle Physiology II: **14/14**, verified Gate 266 / full run 561.
- Physiology Chapter 9 — Synapse and Junctional Transmission: **27/27**,
  verified Gate 327 / full run 701 on exact product SHA `7974b8eee842f668e9fb4fac95783ac64893e98d`.
- Chapter 9 reconstruction statuses:
  - Q1: `needs_manual_review` — defining numbered statements remain absent;
  - Q5: `needs_manual_review` — stored `DOPA` option remains source-ambiguous;
  - Q24: `resolved_reconstruction` — δ/κ/μ opioid-receptor terminology restored.
- Dedicated stable-ID browser coverage verifies Chapter 9 Q24 learner-facing
  reconstruction and exactly three wrong-option rationales.
- Latest **fully verified deterministic inventory**:
  **539 enhanced / 1,576 pending**.
- Verified inventory fingerprint:
  `06882fcd885436ebd15e38c2ff950de267d164434dc4050ca60d0841ca5dd131`.

## Current integration-lane status

- There is **no CURRENT_UNVERIFIED explanation batch** after Chapter 9.
- Chapter 9 is `FULLY_VERIFIED_HISTORY`; PR #33 being open is historical and does
  not itself hold the serialized integration lane.
- The lane is released for the next scheduled subject worker to acquire under the
  runbook's live ownership/double-check rules.
- No Chapter 10 content was authored or committed during the Chapter 9 finalization run.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only the PR's exact
  product-candidate SHA.
- A docs-only `[skip ci]` handoff commit may follow a verified product SHA; record
  the certified product SHA explicitly rather than pretending docs-only HEAD was
  package-certified.
- Browser topic selectors based on substring text are unsafe. Prefer stable chapter identity.
- Pre-commit emphasis validation is case-sensitive; fix the anchor, not medical content.
- A source key may be the best available answer while its explanation is medically
  imprecise. Preserve the raw key and teach the correct distinction in augmentation.
- Missing numbered statements should be reconstructed only to the level actually
  recoverable. Do not fabricate verbatim text.
- Keep image integration as a separate workstream.
- Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, or
  promote production during explanation refinement.

## Next step

- On the next explanation run, re-resolve the current explanation lineage and
  unfinished-batch ownership from live Git plus this handoff before writing.
- If no other subject has acquired the lane and Physiology is selected, resolve
  the exact next incomplete Physiology source-order item dynamically (Chapter 10
  is next after the fully verified Chapter 9 lineage) and select one bounded batch
  with the runbook workload algorithm.
- Do not hardcode a Chapter 10 title or batch range in automation prompts; derive
  them from the immutable source and current inventory at run time.

Efficiency rule: pre-audit while CI runs, but never commit a new batch onto an
unverified lineage.
