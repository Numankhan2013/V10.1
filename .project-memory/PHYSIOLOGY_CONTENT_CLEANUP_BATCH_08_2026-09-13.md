# Physiology learner-visible content cleanup — Batch 08

## Scope and lineage

- Cleanup lane: `fix/marrow-full-content-cleanup-20260913`.
- Pre-mutation cleanup head: `5abd4c253a583a91a3de4a52502172b7b9a2b283`.
- Canonical head checked before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`.
- Cleanup and canonical are diverged; this run made no merge to canonical/main and no intersecting canonical Physiology cleanup mutation was identified.
- Raw Marrow bundles remained immutable.

## Source review

- Verified source: Marrow ED8 Physiology `physiologyed8.pdf`.
- Question/options reviewed against rendered source pages 160–164.
- Explanations reviewed against rendered source pages 165–170.
- This bounded run cleaned Chapter 8 Q1–Q10 only.

## Cleaned stable IDs

- `marrow__PHYS_CH08_Q001`
- `marrow__PHYS_CH08_Q002`
- `marrow__PHYS_CH08_Q003`
- `marrow__PHYS_CH08_Q004`
- `marrow__PHYS_CH08_Q005`
- `marrow__PHYS_CH08_Q006`
- `marrow__PHYS_CH08_Q007`
- `marrow__PHYS_CH08_Q008`
- `marrow__PHYS_CH08_Q009`
- `marrow__PHYS_CH08_Q010`

Cleanup removed OCR, diagram, footer, punctuation, and symbol spillover only while preserving source-readable teaching content. No Key Takeaway authoring, rationale expansion, or explanation fine-tuning was performed.

A latent learner-visible Q5 option defect was discovered even though the high-precision q/option detector reported zero candidates. The options were source-repaired to: `All or none phenomenon`, `Length-tension relationship`, `Tetanization`, `Plateau potential`. The correct option index was not changed.

## Proposal and fail-closed repair

- Reviewed proposal added at commit `c32d9b98917dc6657be0426b03642b3ad3a1e682`: `data/marrow/content_hygiene_proposals/physiology/chapter_008_cleanup_batch_20260913_08.json`.
- First promotion workflow run `34763043756` failed closed at the promoter because the old inert Chapter 8 proposal contained duplicate stable IDs. No validator was weakened and no active override was written by that failed run.
- The already-promoted, superseded inert proposal `data/marrow/content_hygiene_proposals/physiology/chapter_008.json` was removed at commit `f44f66f495aa337a981cbaf303a06e1026614177`. The active v2 Chapter 8 override was not deleted or bypassed.
- Retry workflow run `34763081358` completed successfully.
- Successful promotion/audit branch head: `2ebdc3954056b2286aa79472cdd839c8b17d2e7a`.

## Validation

The successful workflow completed all required fail-closed gates:

- promoted reviewed proposals through source-fingerprinted v2 overrides;
- validated every active v2 override;
- rebuilt and rescanned the complete 2,711-question effective learner-visible bank;
- verified raw/effective answer-index identity for all 2,711 questions;
- required `questionOptionCandidateQuestions == 0`.

Post-promotion effective audit:

- Question/option candidates: `0` globally.
- Explanation candidates: `406` globally.
- Anatomy explanation candidates: `31`.
- Biochemistry explanation candidates: `59`.
- Physiology explanation candidates: `316`.

Chapter 8 now has only three explanation candidates: `marrow__PHYS_CH08_Q011`, `marrow__PHYS_CH08_Q012`, and `marrow__PHYS_CH08_Q014`. Q1–Q10 are absent from the regenerated Chapter 8 explanation review packet.

## Deferrals and exact next action

- Chapter 5 remains `REVIEW_REQUIRED` because accepted v1 ownership prevents safe v2 explanation promotion until a v1→v2 ownership migration is implemented.
- Chapter 7 remains `REVIEW_REQUIRED` for the same reason.
- Do not weaken v1/v2 overlap protection or write around the reviewed proposal promoter.
- Exact next ordinary source-order target: `marrow__PHYS_CH08_Q011`, explanation page 170. Then Q12, then Q14 (pages 171–172 for Q14).
