# Physiology learner-visible content cleanup — Batch 18 handoff

Status: **CLEANED**

## Lineage and coordination

- Repository: `Numankhan2013/V10.1`
- Cleanup lane before proposal mutation: `fix/marrow-full-content-cleanup-20260913` at `b8be49fe7a8a031677a58de13f6845d25c9d162b`.
- Canonical comparison lane: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; canonical did not advance during this run and did not intersect this batch.
- Existing Chapter 13 reviewed proposal was updated additively; existing reviewed question/options fields were preserved exactly.
- Raw Marrow source bundles were not mutated. No merge to canonical or `main` was performed.

## Source review

Verified Marrow ED8 Physiology PDF `physiologyed8.pdf` was used. Embedded text on these pages was visibly corrupted, so rendered pages were authoritative.

Cleaned stable IDs and rendered source pages:

- `marrow__PHYS_CH13_Q018`: question page 245, answer-key page 246, explanation page 254.
- `marrow__PHYS_CH13_Q020`: question page 245, answer-key page 246, explanation page 255.
- `marrow__PHYS_CH13_Q021`: question page 246, answer-key page 246, explanation pages 255–256.

Cleanup was limited to restoring readable source prose and removing OCR/diagram/footer/serialization debris. No Key Takeaways, rationale expansion, teaching additions, medical corrections, or stylistic rewrites were added. Q18's non-prose olfactory diagram labels were omitted because the diagram relationship was not required for the readable explanation. Q20's rods/cones diagram labels were omitted; the readable source prose was retained. Q21's watermark/diagram-like OCR debris was omitted while the source's homonymous hemianopia continuation on page 256 was retained.

## Proposal and promotion

- Reviewed proposal: `data/marrow/content_hygiene_proposals/physiology/chapter_013.json`
- Proposal commit: `bb4032304fbe5e8141ffe501d535c0ceba36aa7a`
- Promotion workflow: `34793305321` — **success**
- Verified promotion commit: `0588c970d1d6d304962956763045ea50dfa5536a`
- Active Chapter 13 v2 override source fingerprint: `e9d3238fba2224fe9e82735ca4a4ae341661e4294816f40d11738618cc435dd9`

## Validation

Promotion workflow passed:

1. source-fingerprinted reviewed proposal promotion;
2. global v2 override validation;
3. full effective learner-visible bank rebuild for all 2,711 questions;
4. learner-visible debris rescan;
5. raw/effective `correctOption` equality across all 2,711 questions;
6. `questionOptionCandidateQuestions == 0`.

Post-promotion review packet summary:

- Question/option candidates: **0 globally**.
- Explanation candidates: **245 globally**.
- Anatomy: **1** explanation candidate.
- Biochemistry: **6** explanation candidates.
- Physiology: **238** explanation candidates.
- Chapters with explanation candidates: **27**.

The regenerated `physiology/chapter_013.json` review packet is absent, confirming Chapter 13 has no remaining detector candidates after this promotion.

## Next Physiology target

Continue in deterministic source order at:

- `marrow__PHYS_CH14_Q002` — Motor Physiology - 1.
- Question page 257.
- Answer-key pages 267–268.
- Explanation pages 268–269.

Chapter 14 currently has 13 explanation candidates and 0 question/option candidates. Rebuild the live audit and re-check both branch heads/ownership before the next mutation.
