# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Authoritative image lineage is carried by `feature/marrow-image-rollout-current`; resolve its live HEAD from Git rather than hardcoding a self-staling pointer.
- Image-coverage infrastructure repair is currently on `fix/marrow-image-source-coverage`, based directly on the authoritative image lineage. It changes discovery/coverage tooling and docs only; it does not mutate the image registry or learner runtime.
- Production promotion remains explicit and guarded.
- Accepted product baseline remains V11.6 Content Quality `125d68b` until the user explicitly promotes a later product baseline.

## Current Marrow bank

Shared architecture:
`MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
There is one shared Practice/CBT/Review/FSRS/sync/module/analytics/navigation engine.

Supplied Marrow ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 topics**.

Raw imported Marrow source is authoritative and immutable. Source bundles remain
manifest/hash validated and ingestion fails closed on corruption/count/ID/option/
topic-link drift.

## Explanation-quality phase

Canonical procedure: `docs/MARROW_EXPLANATION_FINE_TUNING.md` +
`docs/MARROW_BANK_INTEGRATION.md`.

Approved learner-facing contract:
- one meaningful Key Takeaway;
- source-faithful structured detailed explanation;
- 1–4 selective emphasis anchors that exist verbatim in display text;
- exactly three concise wrong-option rationales mapped to the three incorrect
  source options for four-option SBA;
- ID-keyed augmentation separate from raw source;
- source tables/figures/provenance remain source-owned and separate;
- missing/ambiguous source content remains explicit; never invent it;
- FSRS/session behavior is untouched.

The explanation workstream is separate from the image-coverage repair. Do not
change explanation content while fixing image discovery.

## Image registry progress — not a coverage denominator

Current deterministic registry/runtime state remains:
- **162 assets / 204 bindings / 163 released questions** globally.
- Anatomy: **63 approved assets / 63 total assets / 64 released questions**.
- Biochemistry: **60 approved assets / 62 total assets / 60 released questions**.
- Physiology: **35 approved assets / 37 total assets / 39 released questions**.

These numbers remain valid registry progress metrics but are **not evidence that
a subject's source images are complete**.

Historical bounded Biochemistry batch `NKQ_BIOCHEMISTRY_20260911` is
**BATCH_COMPLETE / VERIFIED_HISTORY**. It released 5 of its 6 candidates. The
held CRISPR asset `biochemistry-e10cc8a9721a17da` for
`marrow__BIOCHEM_CH25_Q026` remains `REVIEW_REQUIRED` and unreleased because its
small labels cannot be reconstructed faithfully from the available source.
This historical batch does not own the writer lane.

## Source-PDF image coverage — authoritative current status

A learner review on 2026-09-11 exposed a major completeness defect: many crisp,
source-owned Biochemistry question/solution images were missing despite prior
reports that the subject was finished. Root cause was systemic:

1. the legacy audit primarily followed `structuredExplanation.figures` and a
   narrow text cue rather than treating the source PDF as the completeness
   denominator;
2. bounded staging silently skipped zero/multi-candidate cases;
3. normalized bank records can drop visual-specific metadata even while retaining
   authoritative question/explanation page provenance.

The old statement that **Biochemistry image integration was complete is invalid**.
Only its bounded batches were complete.

New fail-closed source coverage run `34617334236` on
`fix/marrow-image-source-coverage` passed discovery regressions and measured:

- **Biochemistry:** 201 source image placements / 178 unique source image streams;
  62 released placements, 1 `REVIEW_REQUIRED`, 3 rejected, **135 UNACCOUNTED**.
  `IMAGE_COVERAGE_INCOMPLETE`.
- **Physiology:** 388 source image placements / 355 unique streams; 38 released,
  2 rejected, **348 UNACCOUNTED**. `IMAGE_COVERAGE_INCOMPLETE`.
- **Anatomy:** 915 source image placements / 793 unique streams; 69 released,
  **846 UNACCOUNTED**. `IMAGE_COVERAGE_INCOMPLETE`.

A placement count is not automatically a learner figure count: repeated assets,
shared pages, and non-instructional placements can be rejected or mapped after
source inspection. The key guarantee is that each placement must now be
**explicitly released, held, or rejected**; it may no longer disappear silently.

Permanent regression coverage now includes the learner-reported Biochemistry
omissions across Chapters 18–22. Verified examples include:
- Ch18 Q3/Q5/Q6 explanation figures;
- Ch19 Q2 question-time schematic;
- Ch19 Q11 and Q12 question/explanation figures;
- Ch19 Q19 question/explanation figures;
- Ch20 Q6/Q11/Q14/Q17 explanation figures;
- Ch21 Q8 explanation, Q9/Q10/Q12 question-page figures;
- Ch22 Q2 explanation figure.

The regression passes from PDF image placement + canonical page provenance even
where normalized visual metadata is absent.

## Image coverage repair implementation

Repair branch `fix/marrow-image-source-coverage` adds:
- `tools/marrow_visual_inventory.py`: discovers both surviving visual metadata and
  every non-background PDF image placement on canonical question/explanation pages;
- `tools/marrow_image_coverage.py`: classifies source placements as `RELEASED`,
  `REVIEW_REQUIRED`, `REJECTED`, or `UNACCOUNTED` and fails completion claims when
  unaccounted placements remain;
- `tools/test_marrow_image_source_coverage.py`: permanent real-question regressions
  for the reported omissions;
- updated `tools/stage_marrow_image_review.py`: does not silently discard
  source-recorded visuals and can stage unambiguous PDF-placement discoveries;
- `.github/workflows/marrow-image-coverage.yml`: builds the PDF audit, runs the
  coverage regressions/reports, and standard registry/progress/build-pipeline
  source checks;
- updated `docs/MARROW_IMAGE_AUTOMATION_RUNBOOK.md`: separates `BATCH_COMPLETE`
  from `SUBJECT IMAGE_COMPLETE`. A subject may be called complete only when
  `python3 tools/marrow_image_coverage.py --subject SUBJECT --check-complete`
  passes with zero unaccounted placements.

## Current ownership / automation state

- The source-coverage repair branch is an infrastructure fix; it does not own an
  unfinished shared-registry mutation.
- **Physiology image automation is intentionally disabled** while this systemic
  discovery defect is being repaired, so it cannot repeat the same incomplete
  coverage pattern.
- Anatomy and Biochemistry image automations remain disabled at this checkpoint.
- Explanation automations are separate and must not touch image ownership.

## Known verification cautions

- Build-verified ≠ device-verified ≠ accepted production baseline.
- `BATCH_COMPLETE` ≠ `SUBJECT IMAGE_COMPLETE`.
- Registry asset counts ≠ source coverage.
- Figure-metadata counts ≠ source coverage.
- A PDF placement on a shared page can have multiple possible question owners;
  that ambiguity requires source review, not silent omission.
- Do not rewrite raw Marrow JSON/JSONL/shards or source PDFs for this repair.
- Do not alter Topics taxonomy, Practice/CBT/Review/FSRS/sync/modules/navigation,
  or unrelated UI.
- Keep production promotion deliberate.

## Exact next step

1. Finish CI/regression validation of `fix/marrow-image-source-coverage`.
2. If clean and still a fast-forward descendant, advance
   `feature/marrow-image-rollout-current` to the verified repair handoff without
   force-push or main/production promotion.
3. Resume **Biochemistry first**, because its previous subject-complete claim was
   invalidated and it has 135 currently unaccounted source placements. Work in
   bounded batches from the ordered coverage queue until each placement is
   released, held, or rejected with evidence.
4. Only when Biochemistry `--check-complete` passes may it be called
   `IMAGE_COMPLETE`; then hand the lane to Physiology and apply the same coverage
   standard.
