# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Resolve live branch/HEAD from Git; do not hardcode a self-staling HEAD value.
- Current explanation lineage is `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current`.
- Latest **fully verified** explanation product candidate remains Anatomy Chapter 5 Q1–Q9: `1921d758b19d0804438f434aaca950fa32d419ea`.
- Exact-candidate verification: Engineering Gate **333** / `34567801778` and full Android/PWA run **712** / `34567798753` both passed on that same SHA.
- Full-run artifact `V11.7-android-pwa`: ID `10186705331`, digest `sha256:cc332a829500e1cc4fa72ae48a846f5d6f9af518999d27905ce3710df4114bcb`.
- Browser/screenshot artifact: ID `10186689132`, digest `sha256:653be4144f19d4911d9f87948ee693d08e8f4f91cd56a2e7f6898ecc8298365b`.
- Production promotion was skipped.
- Accepted baseline / rollback baseline remains **V11.6 Content Quality** until the user explicitly promotes a later product baseline.
- Accepted product commit: `125d68b`
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
For unattended Scheduled Tasks, `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md` is the mandatory execution/safety protocol.

Every refined four-option SBA should have one meaningful Key Takeaway; medically correct structured display text; 1–4 verbatim emphasis anchors; exactly three wrong-option rationales keyed to the three incorrect source options; source-owned figures/tables/provenance; and reconstruction metadata when source defects are recovered under the runbook contract.

## FULLY_VERIFIED_HISTORY

- Biochemistry enhanced: **259**; Chapters **1–11** verified on the stacked lineage.
- Physiology Chapters 1–9 are fully verified; Chapter 9 exact verified product SHA `7974b8eee842f668e9fb4fac95783ac64893e98d`, Gate 327, full run 701.
- Anatomy Chapter 5 Q1–Q9 is **FULLY_VERIFIED**.
  - PR: **#34**.
  - Product SHA: `1921d758b19d0804438f434aaca950fa32d419ea`.
  - Scope: Chapter 5 **Pharyngeal arches, Skeletal & Muscular Systems**, Q1–Q9 only.
  - Count/workload: **9 questions**, workload score **16.5**.
  - Augmentation: `data/marrow/explanation_anatomy_ch05_q001_q009_v1.json`.
  - Reconstruction statuses: **none** in Q1–Q9.
  - Raw Marrow source stayed unchanged.
  - Deterministic inventory: **548 enhanced / 1,567 pending**.
  - Inventory fingerprint: `3ac131bdd442b649b7778260565f43156e3bf1c04ef4717c3a6c8b82bf30c4fc`.
  - Engineering Gate **333** / `34567801778`: success on exact product SHA.
  - Full Android/PWA **712** / `34567798753`: success on the same exact SHA.
  - Production promotion skipped.

## CURRENT_UNVERIFIED

- Owner: **Anatomy**.
- Batch ID: `anatomy-20260911-ch05-q10-q19`.
- Branch: `feature/marrow-explanation-rollout-anatomy-ch05-q10-q19-current`.
- Chapter 5: **Pharyngeal arches, Skeletal & Muscular Systems**.
- Exact source-order range: **Q10–Q19** / IDs `ANAT_CH05_Q010` through `ANAT_CH05_Q019`.
- Count/workload: **10 questions**, workload score **17.0**.
- Augmentation: `data/marrow/explanation_anatomy_ch05_q010_q019_v1.json`.
- Content checkpoint commit: `248e3540fd35b8e5b18e6356a9ec9b401f2d40d7`.
- Source audit: Q10 and Q13 preserve source tables; Q14–Q19 preserve source-owned figures; Q16 and Q18 are image-dependent and were audited against the generated exact-head source payload/labels.
- Reconstruction statuses: **none required** for Q10–Q19 after source audit. Q14 learner-facing text explicitly avoids teaching thyroid hypoplasia as the defining DiGeorge pouch abnormality while preserving the source-keyed answer.
- Raw Marrow source stayed unchanged.
- Pre-batch deterministic inventory remains **548 enhanced / 1,567 pending**, fingerprint `3ac131bdd442b649b7778260565f43156e3bf1c04ef4717c3a6c8b82bf30c4fc`; inventory regeneration has **not yet** been performed for Q10–Q19.
- Pre-commit in-memory checks completed: 10/10 expected IDs; 1–4 emphasis anchors all occur verbatim; exactly three rationale keys per item; rationale keys equal the three non-source-keyed options.
- PR: not yet opened.
- Exact-head Engineering Gate: not yet run.
- Exact-head Android/PWA: not yet run.
- State: **CONTENT_AUTHORED / CURRENT_UNVERIFIED**.
- Other subject workers must not start a new integration batch while this section remains current.

## Known problems / cautions

- Never accept a neighboring green workflow run; certify only a PR's exact product head SHA.
- Documentation-only `[skip ci]` handoff commits may follow a verified product SHA; do not pretend the later documentation head itself was APK/package certified.
- Prefer stable chapter/question IDs over fuzzy display-text selectors.
- Keep image integration separate. Do not rewrite raw Marrow shards, fork study engines, alter Topics taxonomy, redesign UI, merge, or promote production.
- Historical PR #34 may remain open; it is non-blocking because Q1–Q9 is recorded above as FULLY_VERIFIED_HISTORY.

## Next step

1. Resume this exact Anatomy Q10–Q19 batch; do **not** author Q20+.
2. Run repository-native source-ID/chapter/count, source-key/distractor, emphasis, duplicate-ID, reconstruction-schema and raw-source immutability validation for `explanation_anatomy_ch05_q010_q019_v1.json`.
3. Regenerate the deterministic 2,115-ID explanation inventory and verify enhanced increases by exactly 10 with unchanged raw-source hashes.
4. Add/update one stable-ID Chapter 5 browser regression representative of this batch, preferably image-dependent Q18 or histology Q16, without altering shared Practice/CBT/Review/FSRS behavior.
5. Run shared static/local regressions, then open the bounded PR and require exact-head Engineering Gate plus full Android/PWA/APK/package/reproducibility/preview certification.
6. Keep production promotion skipped. After exact-head certification succeeds, move this section to FULLY_VERIFIED_HISTORY and release the serialized lane.

Efficiency rule: pre-audit future content while CI runs, but never commit another batch on an unverified lineage.
