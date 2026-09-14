# Physiology learner-visible content cleanup — Batch 22 handoff

## Status

CLEANED and promotion-verified on `fix/marrow-full-content-cleanup-20260913`.

## Coordination / lineage

- Cleanup branch before proposal write: `77510440aed6430e54c29ae2579f6f49a008accc`.
- Canonical branch checked before mutation and again after promotion: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`.
- Canonical did not advance or intersect this Chapter 16 batch.
- No merge to canonical or `main` was performed.
- No pre-existing Chapter 16 v2 override existed before this batch.

## Scope

Subject: Physiology
Chapter: 16 — Basal Ganglia and Cerebellum

Cleaned explanation IDs in deterministic source order:

- `marrow__PHYS_CH16_Q001`
- `marrow__PHYS_CH16_Q002`
- `marrow__PHYS_CH16_Q003`
- `marrow__PHYS_CH16_Q004`
- `marrow__PHYS_CH16_Q005`
- `marrow__PHYS_CH16_Q006`
- `marrow__PHYS_CH16_Q010`
- `marrow__PHYS_CH16_Q011`

The pre-run effective packet had 8 explanation candidates and 0 question/option candidates. All 8 Chapter 16 explanation candidates were handled in this bounded run.

## Source review

Authoritative source: verified Marrow ED8 Physiology PDF.
Rendered PDF pages reviewed: 313, 314, 315, 316, 317, 318.

Cleanup was source-faithful only. OCR-flattened basal-ganglia/cerebellar diagrams and other non-prose debris were omitted where they did not add independently necessary readable explanation content. Readable source prose and readable table relationships were retained. No Key Takeaway, new teaching rationale, stylistic rewrite, or source-medicine correction was introduced.

## Proposal and active override

Reviewed proposal:
`data/marrow/content_hygiene_proposals/physiology/chapter_016_cleanup_batch_20260914_22.json`

Proposal commit:
`9ed7de0898059b7787ef80cf4dde26e648ccc97e`

Promotion workflow:
`34806607056` — `Promote Marrow content cleanup proposals` — SUCCESS.

Verified promotion commit:
`9f2b5f9ae0a0d425de1b3ccab5c2bb834ba59a34`

Active override:
`data/marrow/content_hygiene_overrides_v2/physiology/chapter_016.json`

Active Chapter 16 source fingerprint:
`d0275f00f7487c8a8f8b81d1ecb984afff14dddf8033333e278775e17a56c922`

The Chapter 16 override changes explanation fields only.

## Validation

Promotion workflow passed:

- exact source-fingerprint promotion;
- global v2 override validator;
- full effective 2,711-question audit rebuild;
- learner-visible debris scan;
- raw/effective `correctOption` equality for all 2,711 questions;
- `questionOptionCandidateQuestions == 0`;
- four-option / answer-index invariants remained intact.

No runtime output path was modified, so a product/browser rebuild was not required for this content-only override batch.

Post-promotion effective residuals:

- Global explanation candidates: 219
- Anatomy: 1
- Biochemistry: 6
- Physiology: 212
- Question/option candidates: 0 globally

Chapter 16 is absent from the regenerated explanation queue after promotion.

## Deferred / pre-existing residuals

No new Chapter 16 deferrals were created. Earlier documented detector false-positives / REVIEW_REQUIRED items in prior Physiology chapters remain unchanged and must not be rewritten merely to satisfy detector heuristics.

## Exact next ordinary actionable Physiology target

`marrow__PHYS_CH18_Q002` — Chapter 18, Higher Mental Functions.

- question page: 330
- answer-key pages: 337–338
- explanation page: 339
- Chapter 18 currently has 20 explanation candidates and 0 question/option candidates.

Continue from this target in deterministic source order after fresh head/ownership/audit checks.
