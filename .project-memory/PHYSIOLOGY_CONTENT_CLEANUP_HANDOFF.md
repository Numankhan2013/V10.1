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

## 2026-09-13 — Batch 07 (Chapter 6 completion)

- Re-checked cleanup head and canonical head before mutation. Canonical remained at `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`; no intersecting canonical Physiology cleanup change was found.
- Re-read the reviewed proposal promoter/workflow and preserved the v1/v2 overlap guard. Chapter 5 remains `REVIEW_REQUIRED`; Chapter 7 is subject to the same accepted-v1 ownership guard and must not be bypassed.
- Rendered source reviewed directly from verified `physiologyed8.pdf`, pages 115–125, covering the remaining Chapter 6 explanation candidates.
- Cleaned the final 10 Chapter 6 explanation candidates: `marrow__PHYS_CH06_Q022`, `Q023`, `Q025`, `Q026`, `Q027`, `Q029`, `Q030`, `Q032`, `Q033`, `Q034`.
- Removed only OCR/diagram/footer spillover and preserved source-readable teaching content. Diagram/table material was converted only where its textual relationship was clearly readable; unreadable non-prose debris was omitted rather than guessed.
- To respect promoter duplicate-ID protection, the old inert Chapter 6 proposal was removed and replaced by `data/marrow/content_hygiene_proposals/physiology/chapter_006_cleanup_batch_20260913_07.json`; active v2 override history was not deleted or rewritten outside the promoter.
- Proposal commits: removal `134b6ac0a7e6c9f062913450f115695152f45727`; reviewed batch `062b65c034679c951a3a0ca1dc525b92e91b84cf`.
- Promotion workflow run `34760526105` completed successfully and produced promotion commit `ea60da9426f94a64b3efb03e04cdb66cf8dc20ee`.
- The workflow passed the v2 validator, rebuilt the full 2,711-question effective bank, verified raw/effective answer-index identity, and re-ran learner-visible debris scanning.
- Post-promotion effective audit: `questionOptionCandidateQuestions=0`; explanation candidates global `427`, Anatomy `33`, Biochemistry `71`, Physiology `323`.
- `data/marrow/content_audit_effective/review_packets/physiology/chapter_006.json` no longer exists after the audit, confirming Chapter 6 has no remaining detector candidates.
- Next ordinary v2-compatible source-order candidate after the v1-owned Chapter 5/7 deferrals is `marrow__PHYS_CH08_Q001`, question page 160, explanation page 165. Chapter 8 currently has 10 explanation candidates and zero question/option candidates.

### Current handoff rule

- Do not call Chapter 5 or Chapter 7 clean; both require safe v1→v2 ownership migration before explanation overrides can be promoted.
- Do not weaken overlap protection or write directly around the reviewed proposal promoter.
- Continue ordinary cleanup from `marrow__PHYS_CH08_Q001` unless the v1→v2 migration is implemented first.

## 2026-09-14 — Batch 12 (Chapter 10 Neurotransmitters completion)

- Resolved the live cleanup lane before mutation. Initial cleanup head was `a812d059b949c528b83f97ac48b714f8e7a63bee`; canonical remained `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`. The live lane already contained a completed Physiology Chapter 9 Batch 12 from another worker, so Chapter 9 was not duplicated. The next current unresolved ordinary Physiology packet was Chapter 10.
- Re-read the complete current cleanup tool/workflow architecture and project memory before editing. The current promoter explicitly supports additive extension of an existing active chapter v2 override while retaining existing fields and hard-failing conflicts.
- Current Chapter 10 audit at start: 11 explanation candidates and zero detector-identified question/option candidates. Source-order batch: `marrow__PHYS_CH10_Q002`, `Q005`, `Q006`, `Q007`, `Q011`, `Q013`, `Q014`, `Q015`, `Q016`, `Q017`, `Q018`.
- Rendered Marrow ED8 Physiology pages **202–209** were reviewed directly. Embedded/OCR text was not trusted where corrupted. Explanations were restored only to readable source-faithful prose; diagram OCR, source watermark/footer text, page markers, and meaningless symbol/code spillover were omitted. No Key Takeaways, new rationale sections, medical corrections, or stylistic teaching expansions were added.
- A high-priority detector false-negative was found in `marrow__PHYS_CH10_Q017`: the effective options contained OCR tails (`Basophil Ss`, `Mast cell x Ca`, `Platelets Ae) Le)`, `Posterior hypothalamus a <“ »`) even though `questionOptionCandidateQuestions` was zero. Rendered question page 202 verifies the exact options as `Basophil`, `Mast cell`, `Platelets`, `Posterior hypothalamus`; these were source-repaired while preserving correctOption index 3 and four-option order.
- Existing reviewed Chapter 10 question/options fields were preserved exactly. The reviewed proposal was extended additively at `data/marrow/content_hygiene_proposals/physiology/chapter_010.json`.
- Reviewed proposal commit: `6d7570234c7db5e23252125d66a273d722e5161d`.
- Promotion workflow run `34776026715` completed successfully. Every required job step passed: reviewed proposal promotion, syntax check, global v2 override validator, full effective-bank rebuild/debris scan, 2,711-question corpus assertion, raw/effective answer-index identity assertion, zero question/option candidate assertion, and commit/push.
- Verified promotion commit: `6370ce1a24fa03713bd8990f86588285e8479146`.
- Active Chapter 10 v2 override fingerprint after promotion: `868dd6d29442f12e5c0acfae863ea08294d37cb7a5abe9978860cef1ef42464f`.
- Post-promotion effective audit at that exact promotion snapshot: 2,711 questions; `questionOptionCandidateQuestions=0`; explanation candidates global **339**, Anatomy **11**, Biochemistry **46**, Physiology **282**.
- The regenerated `review_packets/physiology/chapter_010.json` no longer exists, confirming all 11 Chapter 10 detector candidates are absent from the current explanation debris queue. The Q17 option repair is active in the v2 override and the global q/option detector remains zero.
- No runtime/product output paths were changed, so browser/build regression was not required for this data-only batch.
- Before this memory write, cleanup had independently advanced to `20ba3d72a0cfaa948df78206d3a86ff00ce1fdb4` for non-overlapping Anatomy Chapter 51 proposal work; canonical was rechecked and remained `fcb7c51af1f24d3090a5f7b483bf4c6f2cc003a0`. No same-chapter/shared Physiology ownership conflict was present.
- Exact next ordinary source-order Physiology target is **`marrow__PHYS_CH11_Q001` — Sensory Receptors**, question page **210**, explanation page **217**. Chapter 11 currently has 15 explanation candidates and zero question/option candidates.

### Current handoff rule

- Chapter 10 is verified CLEANED at promotion commit `6370ce1a24fa03713bd8990f86588285e8479146`.
- Continue from `marrow__PHYS_CH11_Q001` after resolving the live cleanup/canonical heads and current ownership again. Do not revisit Chapter 10 unless a later effective audit produces a new source-grounded regression.
- Historical Chapter 5/7 ownership notes above are superseded only if the live promoter/validator architecture has explicitly migrated those accepted fields; never infer migration from old handoff text alone.
