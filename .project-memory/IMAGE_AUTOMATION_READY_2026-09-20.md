# Image automation start handoff — 2026-09-20

## Authority and scope

The user assigns Marrow image integration to automations, not the primary agent. The user has lifted the P0 campaign's temporary image-work priority lock only; P0 findings and all source-fidelity, review and product-protection gates still apply. Do not start percentage-correct, unrelated UI or explanation work under this handoff.

The only integration trunk is `feature/marrow-canonical-full-current`. Resolve its **live** head when starting; `356cce4` is the last product checkpoint verified before this handoff, not a reusable base SHA. Engineering `35453226391` and full Android/PWA/browser/APK/package run `35453226292` passed on that checkpoint. Any handoff commit or later batch needs its own exact-head CI before being called build-verified. Production remains unpromoted.

## Read-only start checks

1. Read `AGENTS.md`, `.project-memory/STATE.md`, `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`, `docs/MARROW_IMAGE_COVERAGE_GATE.md`, and `docs/MARROW_IMAGE_PIPELINE.md`. The older 2,455-question and 95-reference figures near the top of the pipeline document are historical; use live 2,711-question source coverage.
2. Resolve `git rev-parse origin/feature/marrow-canonical-full-current` and compare it with the checked-out base. Do not use historical image, percentage-correct or pilot branches as a base. Check current image-lane ownership and registry/progress fingerprints before any shared-state write.
3. Run `python3 tools/marrow_images.py validate`, `python3 tools/marrow_image_progress.py --check`, and `python3 tools/marrow_image_coverage.py --check`. These passed on the 2026-09-20 canonical checkout. Re-run against the live base; a passing ledger check does not mean image coverage is complete.

## First bounded lane

Biochemistry is next. Live checked coverage: 110 raw references, 109 effective, 71 released, 1 source-metadata-invalid, 4 tracked but unreleased, 34 untracked, and 31 text-cue review items. The next source-order reference is `marrow__BIOCHEM_CH04_Q011:figure:1` (explanation, source page 69). It is `REVIEW_REQUIRED`: two text-based attempts encountered corrupted embedded PDF text and made no verified learner-facing change. Inspect the authoritative **rendered** page/region and question ownership. If it cannot be verified, leave it flagged; report the blocker explicitly and do not attach a neighboring or inferred visual.

Physiology image automation remains paused while Biochemistry coverage recovery is open, per `docs/MARROW_IMAGE_COVERAGE_GATE.md`. Anatomy is also incomplete (69/1,028 effective released); it is not the first batch under this handoff. PrepLadder source visuals are a separate lane: 422 technical audit items still await manual source comparison.

## Reconciliation contract

Use one bounded automation batch from the live canonical base. Preserve raw source, stable question IDs and immutable originals. Only reviewed source-backed assets and bindings enter runtime metadata. Verify registry, progress and source-reference coverage, then run exact-head Engineering and full Android/PWA/browser/APK/package CI. Reconcile the verified result into canonical before another image batch starts. Report released **and** remaining coverage; do not equate a passed batch with subject completeness or user/device acceptance.
