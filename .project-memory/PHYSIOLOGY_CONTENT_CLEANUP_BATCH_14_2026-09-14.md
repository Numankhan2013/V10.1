# Physiology learner-visible content cleanup — Batch 14

Date: 2026-09-14
Subject: Physiology
Cleanup lane: `fix/marrow-full-content-cleanup-20260913`

## Lineage and ownership

- Cleanup head immediately before proposal mutation: `c24cf04d62329365cbb4d7e6a4435ac688223112`.
- Canonical head immediately before proposal mutation: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`.
- Canonical is diverged from the cleanup lane and contains newer Physiology Chapter 11 Q1-Q6 explanation augmentation (`data/marrow/explanation_physio_ch11_q001_q006_v1.json`). That canonical work was treated as protected newer provenance.
- This cleanup batch touched only Q11, Q12, Q13, Q14, Q16, Q18, and Q21, so there is no stable-ID overlap with canonical Q1-Q6 augmentation. No canonical or main merge was performed.
- Cleanup head after verified promotion: `d1e07228571d33323d18510d0d06ff2d2ea2ac3f`; canonical remained `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0` before this memory write.

## Source review

- Authoritative source: rendered Marrow ED8 Physiology PDF pages 220-224. Embedded PDF text was corrupted and was not used to infer wording.
- Cleaned explanations, in deterministic source order:
  - `marrow__PHYS_CH11_Q011`
  - `marrow__PHYS_CH11_Q012`
  - `marrow__PHYS_CH11_Q013`
  - `marrow__PHYS_CH11_Q014`
  - `marrow__PHYS_CH11_Q016`
  - `marrow__PHYS_CH11_Q018`
  - `marrow__PHYS_CH11_Q021`
- Cleanup removed only OCR/diagram spillover, source branding/footer material, malformed table flattening, and meaningless symbol debris. Medically meaningful readable source content was preserved.
- Q11 thermal-receptor table and Q16 A-delta/C-fiber comparison were reconstructed only as readable source-faithful text. Q18's non-prose gate-control diagram debris was omitted because the readable source prose already states the verifiable relationship.
- No Key Takeaways, new rationale sections, teaching expansions, source-medicine corrections, or stylistic rewrites were added.
- Existing reviewed Chapter 11 question/options fields were preserved exactly; this batch added explanations only.

## Proposal and promotion

- Reviewed proposal path: `data/marrow/content_hygiene_proposals/physiology/chapter_011.json`.
- Reviewed proposal commit: `cddf8c3ee311b37797e31ebdf490ee3d30dd917d`.
- Promotion workflow: `34781192946` (`Promote Marrow content cleanup proposals`) — SUCCESS.
- Verified promotion commit: `d1e07228571d33323d18510d0d06ff2d2ea2ac3f`.
- Active override: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_011.json`.
- Active Chapter 11 source fingerprint after promotion: `8520c8d16b17d5d36e1a9ee38c60da4084ecda30ea1529a3fcdaddad2325375e`.

## Validation

The promotion workflow passed every required gate:

1. reviewed proposal promotion through exact raw-source fingerprints;
2. syntax checks;
3. global v2 override validator;
4. full effective 2,711-question bank rebuild;
5. learner-visible debris rescan;
6. raw/effective `correctOption` identity assertion;
7. `questionOptionCandidateQuestions == 0`;
8. commit/push of the active override and refreshed effective audit.

Post-promotion effective audit:

- total questions: 2,711;
- question/option candidate questions: 0;
- explanation candidate questions: 307 globally;
- Anatomy: 1;
- Biochemistry: 38;
- Physiology: 268.

All seven explanations cleaned in this batch disappeared from the regenerated explanation debris queue. Chapter 11 now contains exactly one detector entry: `marrow__PHYS_CH11_Q004`, the previously documented source-clean false positive caused by legitimate `~ 1 mm` notation. Do not rewrite that source notation merely to satisfy the heuristic detector.

No runtime/product output path changed, so no additional browser/build regression was required for this data-only batch.

## Deferred/next work

- Earlier documented source-order false positives/architecture deferrals remain unchanged and were not bypassed in this run.
- Chapter 11's genuine debris work is complete; Q4 remains detector-only false positive.
- Exact next ordinary actionable Physiology target is `marrow__PHYS_CH12_Q001` — Somatosensory Pathways, question page 225, explanation page 232. Chapter 12 currently has 15 explanation candidates and zero question/option candidates.
- Continue from Q12 Q1 only after resolving live cleanup/canonical heads and ownership again.
