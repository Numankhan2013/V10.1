# Marrow learner-visible content cleanup — Biochemistry Batch 10

Status: CLEANED
Date: 2026-09-14
Subject: Biochemistry
Chapter: 25 — DNA organization, replication and repair

## Lineage reconciliation

- Cleanup lane before proposal: `4b11b72922560299eda8bfb1ae8d635609597e5c`.
- Live canonical checked before mutation: `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`.
- The branches had diverged from merge base `4f943af34bb4bd49f644f2655e23459fc1534031`; the 21 canonical-side commits were inspected and affected project memory, Anatomy/Physiology explanation rollout/inventory/browser tooling, not Biochemistry Ch25 learner-content cleanup files or stable IDs Q13-Q15. No intersecting canonical Biochemistry Ch25 mutation was found.
- Re-read before project-memory write: cleanup `ed11f26529bdecadd0d4d9b1f7ba04d2a34e6fd8`, canonical `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no conflicting Biochemistry cleanup ownership was present.

## Bounded cleanup batch

Cleaned source-order stable IDs:

- `marrow__BIOCHEM_CH25_Q013` — Klenow fragment; question p384; explanation pp395-396.
- `marrow__BIOCHEM_CH25_Q014` — DNA synthesis/cell-cycle phase; question p384; explanation p396.
- `marrow__BIOCHEM_CH25_Q015` — features of DNA replication; question pp384-385; explanation pp396-397.

The exact verified Marrow ED8 source `/Marrow digitization Biochem/biochemistryed8.pdf` was materialized and rendered for source review because the embedded text layer was corrupted. The rendered pages were authoritative.

Cleanup was explanation-only. Removed PDF page markers, OCR symbol/punctuation garbage, and flattened non-prose diagram debris. Source-faithful readable prose was retained. The cell-cycle and replication diagrams were not reconstructed into speculative prose; redundant/unreadable flattened diagram debris was omitted. Source footer/branding (`Sold by @itachibot`) was not copied into learner-visible content.

No stable ID, question, option, `correctOption`, correct-answer mapping, chapter ownership, provenance, or figures were changed. Raw imported source remained immutable.

## Proposal and promotion

- Proposal: `data/marrow/content_hygiene_proposals/biochemistry/chapter_025_reviewed_20260914_batch10.json`
- Proposal commit: `7e00564399f159f167efba10994bb9f14bd35e33`
- Active override: `data/marrow/content_hygiene_overrides_v2/biochemistry/chapter_025.json`
- Promotion workflow: `34777821722` — SUCCESS.
- Verified promotion commit: `ed11f26529bdecadd0d4d9b1f7ba04d2a34e6fd8`.

## Validation

Promotion workflow passed all required stages:

1. source-fingerprinted proposal promotion;
2. syntax check;
3. global v2 override validation;
4. full effective learner-visible bank rebuild and debris scan;
5. 2,711-question corpus assertion;
6. byte/index-equivalent raw-vs-effective `correctOption` map assertion;
7. `questionOptionCandidateQuestions == 0`;
8. commit of active overrides and refreshed effective audit.

Post-promotion readback confirmed Q13, Q14, and Q15 are absent from the Chapter 25 explanation debris packet and their active v2 entries contain explanation fields only. Four-option structures and answer mappings therefore remain source-owned and unchanged.

Post-promotion effective residuals:

- Anatomy: 6 explanation candidates.
- Biochemistry: 43 explanation candidates.
- Physiology: 282 explanation candidates.
- Global: 331 explanation candidates.
- Question/option candidates: 0 globally.

Chapter 25 now has 14 detector candidates. Q3 and Q11 remain previously documented source-faithful detector false positives and were intentionally not distorted. The next real unresolved Biochemistry item is `marrow__BIOCHEM_CH25_Q016`, question p385, explanation pp397-398.

## Batch boundary / next action

Stopped after three questions because Q15 crossed into a diagram-heavy rendered page and the governing policy explicitly permits a smaller batch when source complexity is high. This preserves deterministic source order; no later real candidate was cherry-picked past Q16.

Next run: rebuild/reconcile the live effective audit and start with `marrow__BIOCHEM_CH25_Q016` unless a newer source-grounded ownership or lineage conflict requires deferral.
