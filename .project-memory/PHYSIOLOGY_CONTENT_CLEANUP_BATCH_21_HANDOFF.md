# Physiology learner-visible content cleanup — Batch 21 handoff

Date: 2026-09-14

## Scope
- Subject: Physiology
- Cleanup integration lane: `fix/marrow-full-content-cleanup-20260913`
- Canonical comparison head before proposal write: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`
- Cleanup head before proposal write: `686c810023070df9129f66564e2e1ca1cf8d04e3`
- Canonical remained unchanged through final handoff preparation.
- Cleanup-only campaign: no fine-tuning, teaching expansion, Key Takeaways, stylistic rewrite, raw-source mutation, answer-index change, figure mutation, or canonical/main merge.

## Reviewed batch
Chapter 15 — Motor Physiology - 2

Stable IDs cleaned:
- `marrow__PHYS_CH15_Q004`
- `marrow__PHYS_CH15_Q006`
- `marrow__PHYS_CH15_Q008`
- `marrow__PHYS_CH15_Q009`
- `marrow__PHYS_CH15_Q010`
- `marrow__PHYS_CH15_Q012`
- `marrow__PHYS_CH15_Q015`
- `marrow__PHYS_CH15_Q017`

Rendered ED8 explanation pages reviewed: 298–304. Rendered PDF pages were authoritative; corrupted embedded text was not used to infer wording. Diagram-only/OCR-flattened debris was omitted where it did not carry necessary prose. Q12's readable afferent-tract table content was reconstructed as plain learner-readable text from the rendered source.

Reviewed proposal:
- `data/marrow/content_hygiene_proposals/physiology/chapter_015_cleanup_batch_20260914_21.json`
- proposal commit: `80b678e055e1fbadffcccf1141ce74228edefc40`

## Promotion and validation
Promotion workflow: `34802997786` — SUCCESS.
Verified promotion commit: `323181fd093f2d2e8f97ad5b001a2b1dffd7f01b`.

Passed gates:
- global v2 override validator
- full effective learner-visible audit rebuild: 2,711 questions
- raw/effective `correctOption` maps identical for all 2,711 questions
- learner-visible debris detector and review-packet rebuild
- `questionOptionCandidateQuestions == 0`
- no Chapter 15 explanation packet remains after promotion
- all eight targeted Chapter 15 explanation candidates cleared the regenerated queue

Post-promotion residual explanation counts:
- Global: 227
- Anatomy: 1
- Biochemistry: 6
- Physiology: 220
- Question/option candidates: 0 globally and 0 in every subject

Active Chapter 15 v2 source fingerprint after promotion:
`d4efb67760234902a23559b07bb4ea6920111c09e409911315803fa5d2ed9db5`

Deferred items in this batch: none.

## Exact next Physiology target
`marrow__PHYS_CH16_Q001` — Chapter 16, Basal Ganglia and Cerebellum.
- question page: 307
- answer-key pages: 312–313
- explanation page: 313
- Chapter 16 currently has 8 explanation candidates and 0 question/option candidates.

Continue in deterministic source order from Q1, after fresh cleanup/canonical head comparison and current ownership checks. Do not merge cleanup work to canonical or `main` automatically.
