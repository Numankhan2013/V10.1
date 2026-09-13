# Marrow Anatomy learner-visible content cleanup handoff

## 2026-09-14 — Anatomy Chapter 51 completion

- Subject: Anatomy.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical comparison at final write: cleanup HEAD before this handoff `fd60f8addba83de080acbf565f2bedd4b4dc4b94`; canonical `feature/marrow-canonical-full-current` HEAD `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`. Canonical did not advance into or intersect this Chapter 51 cleanup scope.
- Bounded reviewed batch: Chapter 51 `KUB & Adrenal Gland`: `marrow__ANAT_CH51_Q012`, `marrow__ANAT_CH51_Q014`, `marrow__ANAT_CH51_Q017`, `marrow__ANAT_CH51_Q018`, `marrow__ANAT_CH51_Q025`.
- Authoritative source: exact Marrow ED8 Anatomy PDF with provenance `marrow ed 8 qbank_compressed.pdf`. Rendered source pages reviewed: 960–965 and 970–971. Question pages were 945–949 as applicable; answer key page 950. Embedded/indexed PDF text was corrupted and was not treated as authoritative.
- Cleanup standard applied: preserved readable medical prose; removed OCR/diagram-label spillover, source branding/footer debris, punctuation/symbol garbage, and non-prose diagram text. No Key Takeaways, new rationale sections, teaching expansion, or stylistic enhancement was added.
- Proposal changed: `data/marrow/content_hygiene_proposals/anatomy/chapter_051.json`, explanation-only additions. Reviewed proposal commit: `20ba3d72a0cfaa948df78206d3a86ff00ce1fdb4`.
- Active override changed only through the source-fingerprinted v2 promotion path: `data/marrow/content_hygiene_overrides_v2/anatomy/chapter_051.json`. Verified promotion commit: `3e03b965642f038bfc44e14241b5a9cb9e617597`.
- Raw Marrow bundles, stable IDs, chapter ownership, provenance, figures, stems, options, `correctOption`, option count, and answer mapping were not mutated by this batch.
- Validation: the promotion workflow completed its fail-closed v2 validation, full effective 2,711-question rebuild/debris scan, raw/effective answer-index invariant, and zero question/option candidate gate before writing the promotion commit. Post-promotion effective audit reports `questionOptionCandidateQuestions = 0` and 334 explanation candidates globally: Anatomy 6, Biochemistry 46, Physiology 282. Chapter 51 is absent from the residual explanation index.
- Deferred/documented item: Anatomy Ch14 retains the previously reviewed detector false-positive caused by legitimate source table separators; do not distort source content solely to eliminate that heuristic hit.
- Exact next real unresolved Anatomy target: `marrow__ANAT_CH52_Q002` — Chapter 52 `Internal and external genitalia`, question page 972, answer-key page 979, explanation page 980. Chapter 52 has five current explanation candidates (Q2, Q7, Q13, Q15, Q20) and zero question/option candidates.
- Status: CLEANED for this bounded Chapter 51 batch. Do not merge the cleanup campaign to canonical or main automatically.

## 2026-09-14 — Anatomy Chapter 52 completion / genuine queue complete

- Subject: Anatomy.
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`.
- Live heads immediately before the final memory write: cleanup `8b75765236ee81376942391601592914b9222ef0`; canonical `feature/marrow-canonical-full-current` `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`. Canonical did not advance during this batch and did not intersect the Chapter 52 stable-ID scope.
- Start-of-run effective audit at the then-current cleanup lineage: 2,711 questions; `questionOptionCandidateQuestions = 0`; explanation candidates global 324: Anatomy 6, Biochemistry 43, Physiology 275.
- Bounded reviewed batch: Chapter 52 `Internal and external genitalia`: `marrow__ANAT_CH52_Q002`, `marrow__ANAT_CH52_Q007`, `marrow__ANAT_CH52_Q013`, `marrow__ANAT_CH52_Q015`, `marrow__ANAT_CH52_Q020`.
- Authoritative source: exact Marrow ED8 Anatomy PDF corresponding to provenance `marrow ed 8 qbank_compressed.pdf`. Rendered source pages reviewed: 980, 984–985, 989–991, and 993–994. Source prose for the five target explanations was reconciled from rendered pages 980, 984, 989, 991, and 994; adjacent diagram/continuation pages were inspected and non-prose diagram OCR was omitted. Embedded/indexed PDF text was corrupted and was not used as wording authority.
- Cleanup standard applied: source-faithful readable explanation prose only. Removed OCR garbage, diagram-label spillover, footer/branding text, malformed separators, and meaningless symbol fragments. No Key Takeaways, new rationale sections, teaching expansion, medical embellishment, or stylistic beautification was added.
- Proposal changed: `data/marrow/content_hygiene_proposals/anatomy/chapter_052.json`, explanation-only additions for the five stable IDs above. Reviewed proposal commit: `f3b84bb468297e7173be28f0b35d8ef76586b148`.
- Existing active Chapter 52 reviewed content was preserved additively: the pre-existing Q17 explanation override remained in `data/marrow/content_hygiene_overrides_v2/anatomy/chapter_052.json`; the promotion recomputed the source fingerprint across the merged stable-ID set rather than replacing the file.
- Promotion workflow `34779124298` passed every fail-closed step: source-fingerprinted proposal promotion, syntax checks, global v2 validator, full 2,711-question effective-bank rebuild, learner-visible debris rescan, raw/effective `correctOption` identity, and `questionOptionCandidateQuestions == 0`. Verified promotion commit: `8b75765236ee81376942391601592914b9222ef0`.
- Final active Chapter 52 v2 source fingerprint: `677ec1fc050cf51678898190e58d423253168847566fd34643451fa0ee5ca754`.
- Raw Marrow bundles, stable IDs, chapter ownership, provenance, figures, stems, options, option order/count, `correctOption`, and `correctAnswerText` mapping were not mutated by this batch. No runtime/product output path was changed, so no browser/build regression was required.
- Post-promotion effective audit: 2,711 questions; `questionOptionCandidateQuestions = 0`; explanation candidates global 319: Anatomy 1, Biochemistry 43, Physiology 275. Chapter 52 is absent from the residual explanation queue.
- The only remaining Anatomy detector entry is `marrow__ANAT_CH14_Q003`. It is already source-reviewed and is a detector false-positive caused solely by legitimate `|` separators in the source-faithful elastic-vs-muscular-artery table. Do not rewrite or flatten this valid table merely to force the heuristic count to zero.
- Exact next genuine unresolved Anatomy cleanup target: none. Anatomy has no remaining source-grounded learner-visible cleanup item in the current effective queue; the sole residual is the documented Ch14 Q3 false-positive.
- Status: CLEANED for Chapter 52 and the genuine Anatomy learner-visible content cleanup queue is complete on this cleanup lane. Do not merge the cleanup campaign to canonical or main automatically.
