# Biochemistry learner-visible cleanup — Batch 13

Status: CLEANED

- Subject: Biochemistry
- Chapter: 26 — RNA synthesis, processing and modification
- Working lineage: `fix/marrow-full-content-cleanup-20260913`
- Cleanup HEAD immediately before handoff write: `cde5b4a83a416e0d8431be97e8aab4bdf5fef54d`.
- Canonical comparison immediately before handoff write: `feature/marrow-canonical-full-current` = `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; canonical had not advanced into the Chapter 26 cleanup scope and no stable-ID/provenance reconciliation was required.
- Source of truth: rendered `biochemistryed8.pdf` pages 411–419. Embedded PDF text was corrupted and was not used as the authority where it disagreed with the rendered pages.
- Cleaned stable IDs: `marrow__BIOCHEM_CH26_Q003`, `Q008`, `Q010`, `Q011`, `Q013`, `Q015`, `Q016`, `Q017`, `Q018`, `Q020`, `Q021`, `Q022`.
- Proposal: `data/marrow/content_hygiene_proposals/biochemistry/chapter_026_reviewed_20260914_batch13.json`.
- Proposal commit: `075d5e22556ee7c9f4db59a435dd252af79a3d59`.
- Promoted v2 override: `data/marrow/content_hygiene_overrides_v2/biochemistry/chapter_026.json`.
- Verified promotion commit: `cde5b4a83a416e0d8431be97e8aab4bdf5fef54d`.
- Promotion workflow: `34786308946`, conclusion SUCCESS.

## Source pages reviewed

- Q3: p411
- Q8: p412
- Q10: pp412–413
- Q11: p413
- Q13: p414
- Q15: p415
- Q16: pp415–416
- Q17: p416
- Q18: pp416–417
- Q20: p418
- Q21: pp418–419
- Q22: p419

Rendered pages were reviewed directly. Readable prose was retained; non-prose OCR from comparison diagrams, transcription/translation diagrams, alternative-splicing diagrams, apoB diagrams and the eIF initiation diagram was omitted where the relationship was already expressed in readable source prose. Source-visible wording was preserved rather than medically rewritten; for example Q18 retains the rendered source's `binary complex (GTP+eIF)` wording.

## Cleanup performed

Only learner-visible corruption was removed: OCR/symbol garbage, literal backslashes, source footer/page debris, meaningless punctuation runs, malformed OCR separators, duplicated/flattened diagram labels and unreadable non-prose diagram spillover. Readable source medical content was preserved.

No Key Takeaways, new rationale sections, teaching expansions, stylistic beautification, raw-bundle edits, stable-ID changes, chapter ownership changes, figure changes, stem edits, option edits, answer-index changes, or runtime implementation changes were introduced. The proposal and promoted Chapter 26 v2 override are explanation-only.

## Validation

Promotion workflow `34786308946` passed every required gate:
- exact source-fingerprint proposal promotion
- syntax checks
- global v2 override validator: `MARROW_CONTENT_OVERRIDES_V2_TEST_OK files=31 questions=366 changed_fields=809 explanations=336`
- full effective learner-visible audit rebuild: `EFFECTIVE_MARROW_CONTENT_AUDIT_OK questions=2711 override_questions=429 v1=63 v2_files=31 v2_explanations=336`
- learner-visible debris rescan
- complete 2,711-question raw/effective corpus invariant
- byte/index-identical raw/effective `correctOption` map for all 2,711 questions
- `questionOptionCandidateQuestions == 0`

Post-promotion debris audit:
- Anatomy explanation candidates: **1**
- Biochemistry explanation candidates: **19**
- Physiology explanation candidates: **256**
- Global explanation candidates: **276**
- Question/option candidates: **0 globally**

The Chapter 26 review packet was deleted by the successful effective-audit rebuild because none of the 12 cleaned questions remains in the explanation debris queue. The active Chapter 26 override contains no source footer/brand/code markers. Because the active override is explanation-only, all four source options and `correctAnswerText` mapping remain inherited unchanged; the global validator and raw/effective answer-index invariant passed.

No runtime-output path was modified, so the deterministic content-promotion validation was the relevant regression gate; no browser/build product mutation was required for this batch.

## Deferred / false-positive items

No Chapter 26 cleanup item was deferred.

Biochemistry still has 19 detector candidates: the two previously documented Chapter 25 legitimate-notation false positives plus 17 real Chapter 28 explanation candidates. The Chapter 25 false positives remain intentionally unmodified:
- Q3: legitimate source notation `A = T and G = C`
- Q11: legitimate source notation `~16 kbp`

## Exact next Biochemistry target

The next real deterministic source-order unresolved item is `marrow__BIOCHEM_CH28_Q001` — Chapter 28, Molecular genetics, recombinant DNA & genomic technologies; question page **431**, answer-key pages **438–439**, explanation page **439**. Chapter 28 currently has **17** explanation candidates. Continue from Q1 in source order on the next bounded Biochemistry run.
