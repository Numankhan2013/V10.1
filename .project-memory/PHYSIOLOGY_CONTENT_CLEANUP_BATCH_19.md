# Physiology learner-visible content cleanup — Batch 19

## 2026-09-14 — Chapter 14 Motor Physiology - 1 partial cleanup

- Cleanup lane: `fix/marrow-full-content-cleanup-20260913`.
- Cleanup head immediately before proposal mutation: `58119a45c72c85f46f07e7e83e291d9f9a5232cf`.
- Canonical head immediately before proposal mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no intersecting canonical Chapter 14 cleanup change was present.
- Re-read the current cleanup audit/detector/splitter, v2 validator, reviewed proposal promoter, safe explanation review/preview/promoter, both promotion workflows, current `STATE.md`, `SESSION_LOG.md`, and the existing Physiology cleanup handoff before mutation.
- Start-of-run effective Chapter 14 packet: 13 explanation candidates, 0 question/option candidates. Global start snapshot from the prior verified handoff was 245 explanation candidates: Anatomy 1, Biochemistry 6, Physiology 238.
- Source of truth: rendered Marrow ED8 Physiology pages 268–277 for this bounded source-order review. Embedded PDF text was visibly corrupted and was not used to infer unreadable medical wording.

### CLEANED in this bounded batch

Reviewed and source-faithfully cleaned these five Chapter 14 explanations:

- `marrow__PHYS_CH14_Q004` — rendered explanation pages 270–271.
- `marrow__PHYS_CH14_Q005` — rendered explanation page 271. The OCR-flattened comparison table was omitted from the prose override rather than guessed/reformatted; readable explanatory prose was preserved.
- `marrow__PHYS_CH14_Q007` — rendered explanation page 272.
- `marrow__PHYS_CH14_Q009` — rendered explanation page 273.
- `marrow__PHYS_CH14_Q013` — rendered explanation pages 276–277. Reciprocal-inhibition figure spillover was omitted while readable source prose before and after the figure was preserved.

No stem/options, stable IDs, correctOption indexes, answer mapping, provenance, chapter ownership, figures, or immutable raw bundles were changed.

### REVIEW_REQUIRED source-order deferrals

The following earlier Chapter 14 items were reviewed but not mutated because medically meaningful source glyphs remain unreadable/ambiguous in the rendered source. They were not reconstructed from memory or context:

- `marrow__PHYS_CH14_Q002` — rendered pages 268–269 contain unresolved glyphs in the Erlanger/Gasser fiber-group and small-motor-efferent wording.
- `marrow__PHYS_CH14_Q010` — rendered page 274 contains an unresolved motor-neuron glyph in the inverse-stretch-reflex mechanism prose.
- `marrow__PHYS_CH14_Q015` — rendered page 277 contains unresolved glyphs in the α/γ coactivation prose.

These deferrals justify continuing past them without silently calling them clean.

### Promotion and validation

- Reviewed proposal path: `data/marrow/content_hygiene_proposals/physiology/chapter_014.json`.
- Reviewed proposal commit: `d526747034c741d216507ce34a69c9d3c346c515`.
- Promotion workflow: `34796575990` — SUCCESS.
- Verified promotion commit: `dd112cec98a968f5d020cd6ac8f02fe91a7ba5b2`.
- Active Chapter 14 v2 source fingerprint: `34bf51a98002500fa826545abece8210edd1675004b60ca530c7a29f98c5c970`.
- Existing Chapter 14 Q31/Q35 active explanation fields were preserved additively.
- Global v2 validator passed: 32 files, 396 v2 questions, 880 changed fields, 372 explanations.
- Full effective audit rebuilt successfully at 2,711 questions; raw/effective `correctOption` maps were identical.
- Learner-visible debris scan after promotion: `questionOptionCandidateQuestions=0`; explanation candidates global **240**, Anatomy **1**, Biochemistry **6**, Physiology **233**.
- Chapter 14 reduced from 13 to 8 explanation candidates. All five cleaned IDs are absent from the regenerated Chapter 14 queue.
- No runtime/product output path changed, so browser/build regression was not required for this data-only batch.
- No validator was weakened and no merge to canonical or `main` was performed.

### Exact continuation point

- Earliest unresolved Physiology item remains `marrow__PHYS_CH14_Q002`, but it is explicitly `REVIEW_REQUIRED` pending exact source-glyph resolution.
- `marrow__PHYS_CH14_Q010` and `marrow__PHYS_CH14_Q015` are likewise `REVIEW_REQUIRED` source deferrals.
- The next ordinary actionable source-order cleanup target is `marrow__PHYS_CH14_Q019`, question pages 261–262, rendered explanation pages 278–279.
- After Q19, continue the current Chapter 14 queue in deterministic source order (`Q024`, `Q033`, `Q034`, `Q037`) unless new source-grounded defects or ownership changes appear.
