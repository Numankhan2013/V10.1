# Marrow Physiology learner-content cleanup — Batch 09 — 2026-09-13

## Status

CLEANED with one source-grounded deferral.

## Lineage and coordination

- Repository: `Numankhan2013/V10.1`
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`
- Cleanup head at run start: `5c8478b40b385e97bc27ed4a37b900cfa2e591e6`
- Canonical head checked at run start: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`
- Canonical/main were not mutated.
- Source corpus contract remained Anatomy 1,115 / Biochemistry 582 / Physiology 1,014 = 2,711 questions.

## Source review

Verified source: Marrow ED8 Physiology `physiologyed8.pdf` / Library copy `physiologyed8(3).pdf`.
Rendered pages were treated as authoritative because the embedded text layer is corrupted.

Reviewed Chapter 8 `Muscle Physiology II` residuals:

- `marrow__PHYS_CH08_Q011` — explanation page 170 — source-resolved and cleaned.
- `marrow__PHYS_CH08_Q012` — explanation page 170 — source-resolved and cleaned.
- `marrow__PHYS_CH08_Q014` — explanation pages 171–172 — `REVIEW_REQUIRED`. The rendered source contains an unresolved glyph inside medically meaningful prose in the tetanization/summation explanation. The same glyph remained unresolved with independent PDF rendering, so no wording was inferred from memory or outside knowledge.

## Reviewed proposal and promotion

- Proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_008_cleanup_batch_20260913_09.json`
- Proposal commit: `98c70f637f378655d6fe9534baac6f107b54a2ee`
- Scope: explanation-only cleanup for Q11 and Q12; no question/option/correctOption mutation.
- Promotion workflow: GitHub Actions run `34765902757` — SUCCESS.
- Verified promotion commit: `cf6602b6044b4c99820ae2114194c63f8e2bd794`

## Validation

Promotion workflow passed all required gates:

- `MARROW_CONTENT_OVERRIDES_V2_TEST_OK`
- effective learner-visible audit rebuilt for all 2,711 questions
- raw/effective `correctOption` maps identical for all 2,711 questions
- `questionOptionCandidateQuestions == 0`
- no source/footer/serialized marker accepted through the active v2 validator
- current active v2 state after promotion: 27 files / 272 questions / 208 explanation overrides

Post-promotion debris audit:

- Global explanation candidate questions: **399**
- Anatomy: **26**
- Biochemistry: **59**
- Physiology: **314**
- Question/option candidates: **0 globally**
- Chapter 8 explanation candidates: **1**, only `marrow__PHYS_CH08_Q014`

Physiology therefore decreased **316 → 314** in this bounded run.

## Existing deferrals carried forward

- Physiology Chapters 5 and 7 remain `REVIEW_REQUIRED` for explanation cleanup because their stable IDs are owned by the accepted v1 display override and the v2 promoter correctly refuses overlap. Do not weaken that guard.
- Chapter 8 Q14 is additionally `REVIEW_REQUIRED` for source ambiguity as documented above.

## Exact next action

- Exact next unresolved source-order Physiology item: `marrow__PHYS_CH08_Q014`, explanation pages 171–172, `REVIEW_REQUIRED` pending a source-faithful resolution of the unreadable glyph.
- With that explicit deferral preserved, the next ordinary actionable cleanup target is `marrow__PHYS_CH09_Q001` (`Synapse and Junctional Transmission`), question page 173, answer-key pages 180–181, explanation pages 181–182.
- Continue one bounded batch at a time and re-run the full v2/effective-bank validation after every promotion.
