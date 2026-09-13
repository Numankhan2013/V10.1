# Anatomy learner-content cleanup — Batch 09 — 2026-09-13

## Lineage and coordination

- Subject: Anatomy.
- Cleanup lane immediately before reviewed proposal: `fix/marrow-full-content-cleanup-20260913` at `08fe572e0587a1648210b1a45c4474c69b71e465`.
- Canonical comparison head: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`.
- The branches were diverged, but the canonical-only changes were explanation/inventory/test work and did not intersect Anatomy Chapter 26 raw source, cleanup proposals, or cleanup overrides. Reconciliation therefore remained stable-ID/provenance scoped; no merge to canonical/main was performed.

## Source reviewed

Authoritative source: `marrow ed 8 qbank_compressed.pdf` (Marrow ED8 Anatomy). Rendered pages were treated as authoritative because the embedded text layer is corrupted.

Reviewed and cleaned stable IDs:

- `marrow__ANAT_CH26_Q004` — question p435, answer key p443, explanation pp445–446.
- `marrow__ANAT_CH26_Q008` — question p437, answer key p443, explanation p448.
- `marrow__ANAT_CH26_Q009` — question p437, answer key p443, explanation p449.
- `marrow__ANAT_CH26_Q010` — question p437, answer key p443, explanation pp449–450.
- `marrow__ANAT_CH26_Q011` — question p438, answer key p443, explanation pp450–451.
- `marrow__ANAT_CH26_Q012` — question p439, answer key p443, explanation p451.
- `marrow__ANAT_CH26_Q014` — question p440, answer key p443, explanation pp452–453.

Cleanup was explanation-only. Readable source prose was preserved; OCR-flattened diagram labels/noise were omitted. No stem, options, `correctOption`, answer mapping, stable ID, provenance, chapter ownership, figure ownership, or immutable raw source was intentionally changed.

## Proposal and promotion

- Proposal: `data/marrow/content_hygiene_proposals/anatomy/chapter_026.json`.
- Reviewed proposal commit: `b7f4e7c572bc84fef88da7e5f068c6c624e722f4`.
- Promotion workflow: `34767133271` — SUCCESS.
- Verified active promotion commit: `6e89ef36056c0a146ff71d7f32958e6ca718ef11`.
- Active override: `data/marrow/content_hygiene_overrides_v2/anatomy/chapter_026.json`.

## Validation

All required promotion gates passed on the promoted branch head:

- `MARROW_CONTENT_OVERRIDES_V2_TEST_OK`: 28 v2 files, 279 override questions, 674 changed learner fields, 215 explanation overrides.
- Effective learner bank rebuilt successfully: exactly 2,711 questions, 342 display-override questions, 63 v1 questions, 28 v2 files, 215 v2 explanation questions.
- Raw/effective `correctOption` maps were exactly equal for all 2,711 questions.
- `questionOptionCandidateQuestions == 0` globally.
- All seven Batch 09 IDs disappeared from the post-promotion Chapter 26 explanation review packet.
- No build/runtime path was changed by this batch, so no separate product/browser build regression was required beyond the content promotion gates.

## Residual cleanup state after verification

Post-promotion unique explanation candidates: **392 globally**:

- Anatomy: **19**
- Biochemistry: **59**
- Physiology: **314**

Anatomy Chapter 26 now has exactly three unresolved explanation questions:

1. `marrow__ANAT_CH26_Q015` — question p441, key p443, explanation pp453–454.
2. `marrow__ANAT_CH26_Q016` — question p441, key p443, explanation pp454–455.
3. `marrow__ANAT_CH26_Q017` — question p442, key p443, explanation pp455–456.

The previously reviewed Anatomy Chapter 14 legitimate-table detector false-positive remains intentionally documented and must not be source-distorted just to clear the heuristic.

## Exact next action

Continue Anatomy in deterministic source order at **`marrow__ANAT_CH26_Q015`**, using rendered Marrow ED8 pp453–454. Do not skip Q15 merely because later questions may be easier. If source-faithful cleanup cannot be established, mark it `REVIEW_REQUIRED` and record the deferral before moving on.
