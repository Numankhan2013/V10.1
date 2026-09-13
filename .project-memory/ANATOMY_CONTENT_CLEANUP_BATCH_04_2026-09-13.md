# Anatomy learner-visible content cleanup — Batch 04 — 2026-09-13

Status: **CLEANED / FULLY VALIDATED**

## Lineage and coordination

- Repository: `Numankhan2013/V10.1`
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`
- Canonical trunk inspected before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`.
- Cleanup and canonical were diverged. The live canonical-only delta did not intersect Anatomy Chapter 14 raw source, Chapter 14 hygiene proposals/overrides, or this cleanup batch, so this run used stable-ID/source-fingerprint reconciliation and did not merge or overwrite canonical.
- Raw Marrow source remained immutable. Main/production untouched.

## Source reviewed

Authoritative source: exact verified `marrow ed 8 qbank_compressed.pdf`.
Rendered PDF pages were used because indexed/embedded text was corrupted.

- Answer key: p251.
- `marrow__ANAT_CH14_Q001`: explanation pp251–252 (metadata extends through p253).
- `marrow__ANAT_CH14_Q002`: explanation p253 (metadata pp253–254); this was an older active-override defect discovered during post-gate inspection even though the current detector did not queue it.
- `marrow__ANAT_CH14_Q003`: explanation pp254–255.
- `marrow__ANAT_CH14_Q004`: explanation p255.
- `marrow__ANAT_CH14_Q006`: explanation p257; source boundary inspection proved the long learner-visible Q7–Q11 continuation was OCR/page bleed and not part of Q6.
- `marrow__ANAT_CH14_Q011`: explanation p261, with p260 inspected to confirm the Q11 boundary.

## Cleanup completed

Reviewed source-faithful explanation cleanup was completed for these stable IDs:

- `marrow__ANAT_CH14_Q001`
- `marrow__ANAT_CH14_Q002` (latent older active-override repair)
- `marrow__ANAT_CH14_Q003`
- `marrow__ANAT_CH14_Q004`
- `marrow__ANAT_CH14_Q006`
- `marrow__ANAT_CH14_Q011`

No gold-standard tuning, Key Takeaway authoring, new teaching content, medical correction, question rewrite, option rewrite, answer-index change, or raw-source mutation was performed. Diagram/table OCR debris and cross-question page bleed were removed while readable source prose was preserved.

Reviewed proposal path: `data/marrow/content_hygiene_proposals/anatomy/chapter_014.json`.
Initial five-question proposal commit: `f3aedf1e941ddaab2f897c1df57dd868cedf9859`.
Latent Q2 active-override source repair commit: `36cb8df0c052cff0f91442433a1aa199899f14a2`.
Proposal handoff including Q2: `de947cb2cb310896b7209b7823cedad0ed3b7719`.

## Validation

Promotion workflow for the initial reviewed batch: GitHub Actions run `34753297496` — **SUCCESS**.

Post-gate inspection exposed the older dirty Q2 override. It was source-repaired and then revalidated through the same promotion path. Final validation run: GitHub Actions run `34753481912` — **SUCCESS**.

Final validated cleanup-branch product/audit head after promotion: `42091ee58ee5569c9ee625656ffcdb1afd8f6ba6`.

The promotion workflow validated all active v2 overrides, rebuilt the complete effective bank, asserted the full **2,711-question** corpus, asserted raw/effective `correctOption` identity, regenerated the learner-visible debris audit, and required `questionOptionCandidateQuestions == 0`.

Current verified residual summary:

- learner-visible question/option candidates: **0** globally.
- explanation candidates: **482** globally.
- Anatomy: **39**.
- Biochemistry: **94**.
- Physiology: **349**.

`marrow__ANAT_CH14_Q003` remains listed by the heuristic detector only because the clean source-faithful text table uses `|` separators and the detector classifies `|` as `hard_noise_char`. The four table lines were visually reconciled against rendered source pp254–255. This is a documented detector false-positive, not unresolved OCR/code leakage. Do not weaken the detector merely to remove this flag.

## Deferred / review-required

- No semantic source uncertainty was deferred in this batch.
- Q3 detector residue is a documented formatting false-positive as described above.

## Exact next Anatomy cleanup target

The next real unresolved source-order Anatomy explanation candidate is:

- `marrow__ANAT_CH24_Q001` — Brainstem
- question page: 404
- answer-key page: 409
- explanation pages: 409–410
- current `correctOption`: 1

Chapter 24 currently contains 8 explanation candidates. Resume from Q1 in deterministic source order. Do not revisit Chapter 14 Q3 solely to satisfy the `|` heuristic unless a learner-visible defect is independently demonstrated.
