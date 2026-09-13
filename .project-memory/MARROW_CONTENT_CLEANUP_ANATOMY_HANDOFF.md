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
