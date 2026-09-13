# Biochemistry learner-visible content cleanup — Batch 14

- Subject: Biochemistry
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`
- Canonical comparison head before mutation: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`
- Cleanup head before proposal mutation: `717bdf2d2075c1c08a43d805de106ddd26528f60`
- Proposal commit: `1be8588322cd61a60e889d0953c2460d01e465f7`
- Verified promotion commit: `b28efce19aaf34b6bf53105fc7f7670b536906a7`
- Promotion workflow: `34789451758` — PASS

## Scope cleaned

Deterministic source-order Chapter 28 explanations:

- `marrow__BIOCHEM_CH28_Q001`
- `marrow__BIOCHEM_CH28_Q002`
- `marrow__BIOCHEM_CH28_Q007`
- `marrow__BIOCHEM_CH28_Q008`
- `marrow__BIOCHEM_CH28_Q009`
- `marrow__BIOCHEM_CH28_Q011`
- `marrow__BIOCHEM_CH28_Q012`
- `marrow__BIOCHEM_CH28_Q013`
- `marrow__BIOCHEM_CH28_Q018`
- `marrow__BIOCHEM_CH28_Q019`
- `marrow__BIOCHEM_CH28_Q020`
- `marrow__BIOCHEM_CH28_Q022`

Rendered authoritative Marrow ED8 explanation pages reviewed: **439–446** from `biochemistryed8.pdf`.

Reviewed proposal: `data/marrow/content_hygiene_proposals/biochemistry/chapter_028_reviewed_20260914_batch14.json`.
Promoted source-fingerprinted v2 override: `data/marrow/content_hygiene_overrides_v2/biochemistry/chapter_028.json`.

Cleanup remained explanation-only. OCR/serialization noise, source watermark/footer spillover, malformed punctuation, and flattened diagram-label debris were removed while preserving readable source medical content. Raw imported source, stable IDs, question text, four options, `correctOption`, `correctAnswerText` mapping, provenance, chapter ownership, and figures were not changed.

## Validation

Promotion workflow `34789451758` passed:

- `MARROW_CONTENT_OVERRIDES_V2_TEST_OK files=32 questions=380 changed_fields=829 explanations=351`
- `EFFECTIVE_MARROW_CONTENT_AUDIT_OK questions=2711 override_questions=443 v1=63 v2_files=32 v2_explanations=351`
- raw/effective `correctOption` maps identical for all **2,711** questions
- `questionOptionCandidateQuestions == 0`
- cleaned Chapter 28 batch questions are absent from the explanation debris queue
- no runtime output paths were changed, so no additional browser/build gate was required for this proposal-only batch

Post-promotion explanation residual counts:

- Anatomy: **1**
- Biochemistry: **7**
- Physiology: **253**
- Global: **261**

Biochemistry residuals consist of the two previously documented Chapter 25 detector false positives plus five real Chapter 28 candidates.

## Deferred / retained detector items

No item in Batch 14 was deferred. The previously documented legitimate Chapter 25 detector false positives remain intentionally unchanged:

- Ch25 Q3: legitimate `A = T and G = C` notation
- Ch25 Q11: legitimate `~16 kbp` notation

## Exact next Biochemistry target

`marrow__BIOCHEM_CH28_Q023` — question page **436**, answer-key pages **438–439**, explanation pages **446–447**.

Remaining real Chapter 28 queue after Batch 14: Q23, Q24, Q25, Q26, Q27. Continue in deterministic source order.
