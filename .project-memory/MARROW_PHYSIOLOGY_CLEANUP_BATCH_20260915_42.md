# Physiology learner-visible cleanup — Batch 42 — 2026-09-15

Status: CLEANED

## Lineage and coordination

- Cleanup lane before proposal: `33aed66e95e93447fa02c05b7ce6e1dbaf976300`.
- Canonical checked before mutation and remained `94edb3af43eb38a1ef762b08c1bdb152c15b3359`; no intersecting canonical advance was present.
- Proposal commit: `7e2f786dd7b97d389a43dd291e54994c71db8594`.
- Promotion workflow: `34913704497`, job `104206605945`, success.
- Verified promotion commit: `1f00e722847474bb842845f92765f867a757cc2d`.
- No merge to canonical or main.

## Source-order review and deferrals

The effective audit at run start contained 77 explanation candidates globally: Anatomy 1, Biochemistry 6, Physiology 70, with zero question/option candidates.

Earlier unresolved Physiology detector hits were reviewed in deterministic source order before advancing:

- Ch3 Q4: detector false-positive only; legitimate Fick-law equations/scientific notation. No rewrite.
- Ch4 Q1/Q3/Q4: detector false-positives only; legitimate +/- notation and ion equations. No rewrite.
- Ch5: 20 explanation candidates remain genuine/possible cleanup work, but all Ch5 stable IDs are owned by accepted v1 question/options overrides. Current governing v2 validator and promotion architecture prohibit any v2 overlap with v1 IDs, so explanation cleanup is deferred rather than weakening validators or mutating the accepted v1 path.
- Ch7: same v1-overlap architecture constraint as Ch5; deferred.
- Ch8 Q14: rendered ED8 p171 contains a missing-glyph block inside medically meaningful source wording (`multiple ■ber summations`). Exact source-faithful wording cannot be established without inference; REVIEW_REQUIRED.
- Ch9 Q7: detector false-positive only (`~75%`).
- Ch11 Q4: detector false-positive only (`~1 mm`).
- Ch14 Q2: rendered ED8 p268 contains missing-glyph blocks in medically meaningful classification wording; REVIEW_REQUIRED.
- Ch14 Q15: rendered ED8 p277 contains missing-glyph blocks in the α/γ coactivation wording; REVIEW_REQUIRED rather than infer.

## Cleaned item

- `marrow__PHYS_CH14_Q010` — Motor Physiology - 1.
- Question page 259; answer-key pages 267–268; authoritative rendered explanation page 274.
- Restored only the readable source prose for the inverse stretch reflex and removed OCR fragments/diagram spillover. Preserved the source sequence: Golgi tendon organ receptor; series arrangement; greater stimulation by contraction; Ib afferent → inhibitory interneuron → glycine → α-motor-neuron inhibition → relaxation.
- Proposal path: `data/marrow/content_hygiene_proposals/physiology/chapter_014_batch42_q010.json`.
- Active override path: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_014.json`.
- Raw imported source, stable ID, question/options, correctOption, correctAnswerText mapping, figures, provenance and chapter ownership were not changed.

## Validation

Promotion workflow `34913704497` passed all steps: exact source-fingerprint promotion; syntax check; global v2 override validator; full effective 2,711-question rebuild; learner-visible debris scan; corpus and raw/effective answer-index invariants; zero question/option candidates.

Post-promotion residual explanation candidates: 76 globally — Anatomy 1, Biochemistry 6, Physiology 69. `marrow__PHYS_CH14_Q010` is absent from the regenerated explanation queue.

## Next unresolved Physiology item

Exact first residual in source order remains `marrow__PHYS_CH03_Q004`, but it is a documented detector false-positive caused by legitimate scientific equations and should not be rewritten. The first large genuine unresolved block is Physiology Ch5, currently deferred by the accepted-v1/v2-overlap architecture. Do not weaken the validator to process it. Continue source-order review only after preserving these deferrals.
