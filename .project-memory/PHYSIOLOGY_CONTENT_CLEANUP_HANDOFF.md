# Physiology learner-visible content cleanup handoff

## 2026-09-13 — Batch 06 (Chapter 5 deferral + Chapter 6 bounded cleanup)

- Cleanup lane: `fix/marrow-full-content-cleanup-20260913`.
- Canonical head checked before mutation: `feature/marrow-canonical-full-current` at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no intersecting Physiology cleanup mutation was identified.
- Current cleanup validation architecture was re-read before mutation, including effective audit, debris detector/splitter, v2 override validator, reviewed proposal promoter, safe explanation review/preview tools, promotion workflow, and current project memory.
- Source of truth reviewed: rendered Marrow ED8 Physiology pages 93–98 and 104–115 in `physiologyed8.pdf`.

### Source-order deferral

- Chapter 5 is the earliest unresolved explanation chapter, but every Chapter 5 stable ID is already owned by the accepted v1 question/option override. The current v2 promoter and v2 validator explicitly reject v1/v2 stable-ID overlap. Therefore Chapter 5 explanation cleanup cannot be safely promoted through the required source-fingerprinted v2 path without first migrating the accepted v1 ownership contract.
- Chapter 5 was therefore deferred as `REVIEW_REQUIRED` for architecture migration. No validator was weakened, no raw source was mutated, and no direct/unsafe override was written.

### Verified Chapter 6 cleanup

- Cleaned stable IDs in this bounded run: `marrow__PHYS_CH06_Q001`, `Q003`, `Q004`, `Q006`, `Q007`, `Q008`, `Q009`, `Q011`, `Q013`, `Q018`, `Q019` (11 questions total).
- Explanation cleanup removed only source-OCR/diagram spillover and preserved readable source teaching text.
- High-priority latent learner-visible stem/option defects missed by the high-precision q/option detector were also source-repaired where encountered: Q3 OCR prefix removed; Q4 `Nat` restored to source `Na+`; Q9 option tails removed; Q11 stem prefix removed; Q18 stem/options repaired to rendered source.
- Existing reviewed Chapter 6 question/option cleanup outside this batch was preserved exactly.
- Proposal commits: `7f0ccd6b68f3a64c62fac881c07265b600d0264a` and `9a3965d4f8db17fa18f141bb530cf711e5e79296`.
- Promotion commits after the fail-closed workflow: `77ff85602388bf0d60212da229ab6429026676d1` and `a510d3d3c0fd8feda2e54a6a4feebb175669f4df`.
- Active override: `data/marrow/content_hygiene_overrides_v2/physiology/chapter_006.json` with source fingerprint `d5081aa08a9baa3a620765341694f07fc6e9246368d383f3bcd31ae2451d8b0d`.
- Promotion workflow completed its v2 validation, full effective-bank rebuild, answer-index identity assertion, and debris audit before each bot promotion commit. Raw source remained immutable.
- Effective audit after the final promotion: 2,711 questions; `questionOptionCandidateQuestions=0`; explanation candidates global `441`, Anatomy `36`, Biochemistry `72`, Physiology `333`.
- Chapter 6 explanation candidates reduced from 21 before this run to 10 after this run.
- Exact next unresolved source-order Chapter 6 candidate is `marrow__PHYS_CH06_Q022`, source question page 99, explanation pages 115–116. Continue from Q22 unless Chapter 5 v1→v2 ownership migration has been safely implemented first.

### Handoff rule

- Do not call Chapter 5 clean. It remains deferred solely because of the current v1/v2 ownership contract, not because source text is unavailable.
- Do not bypass the reviewed proposal promoter or weaken v1/v2 overlap protection. A later architecture migration must preserve the already accepted Ch5/Ch7 question/options byte-for-byte while adding source-fingerprinted explanations.
- Continue Chapter 6 in deterministic source order from Q22 for ordinary cleanup work.
