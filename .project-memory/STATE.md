# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/commit and CI from Git before writing. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- **Sole Marrow integration trunk:** `feature/marrow-canonical-full-current`.
- Product/UI base: user-approved V3/correct-index lineage.
- Current canonical checkpoint before the structured-table repair: `cc24d396783f4738fe33f432ae521f5da436fee1`.
- That canonical checkpoint passed exact-head Engineering Gate and full Android/PWA/browser/APK/package/preview verification and was subsequently preview-verified by the user for the requested product/UI fixes.
- `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` is mandatory for image and explanation workers.
- Historical rollout branches/PRs are donor evidence/history only. New batch branches must start from the exact **current** canonical HEAD and verified results must return to canonical before a lane is released.
- Production promotion remains explicit and guarded. `main`/production must not be changed without user approval.

## Current blocker — structured explanation table regression

User preview review exposed a real learner-facing defect in Anatomy Ch5 Q10: the table titled **Pharyngeal arch muscle derivatives** rendered `[object Object]` as its column headings and blank cells.

Investigation established:
- the canonical source table is populated and medically intact;
- source columns use object schema such as `{key, label}`;
- source rows are objects keyed by those column keys;
- explanation fine-tuning correctly preserves `structuredExplanation.tables`;
- the shared legacy `nkRenderMarrowTable` presentation contract expected scalar/string columns and positional row arrays;
- direct object string coercion produced `[object Object]`, while numeric row access produced blank cells;
- existing browser QA checked that a `.nk-marrow-table` container existed but did not assert meaningful header/cell contents, so the broken table passed verification.

Ownership: this is an **explanation/runtime renderer integration defect**, not deferred Anatomy image work. Image automation owns source-native visual assets; it does not repair an already-structured text table.

Repair branch:
`feature/marrow-structured-table-renderer-fix-20260912`

Exact repair base:
`cc24d396783f4738fe33f432ae521f5da436fee1`

Repair components:
- `tools/apply_marrow_structured_table_renderer_v1.py`
  - audits canonical table source data;
  - normalizes object-keyed columns/rows to the accepted shared table renderer;
  - preserves source data and existing visual styling;
  - fails closed on empty source rows/headers or object-string leakage;
  - verifies the Anatomy Ch5 Q10 sentinel source content.
- `tools/verify_marrow_structured_table_browser.py`
  - opens Anatomy → Marrow → Ch5 → Q10 through the learner UI;
  - answers the question and verifies the actual populated table;
  - rejects `[object Object]` and blank/under-populated output;
  - checks expected headers and representative cell text.
- `.github/workflows/build-apk.yml`
  - runs the compatibility repair after Marrow bank generation;
  - runs the new learner-visible browser regression;
  - requires the renderer marker in generated and packaged app output.
- `tools/verify_build_pipeline.py`
  - protects transform ordering and requires the new browser regression/renderer marker.

**Current status of the repair branch:** implementation/docs are being exact-head certified. Do not call this fix integrated or `FULLY_VERIFIED` until live CI passes and the verified tree is reconciled into canonical.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.

Do not use old 2,115 or 2,455 denominators for completeness/inventory/coverage decisions. Raw imported source remains immutable.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · FSRS · Tests · Insights · More**.
- Study hierarchy: **My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test**.
- Subject Home cards must expose the PrepLadder/Marrow chooser.
- Marrow enhanced explanations must be learner-visible in runtime.
- FSRS is review-only: incorrect or encountered-and-skipped questions may enter; genuinely unseen questions must not be introduced by FSRS.
- Preserve V3 Home, Topics journey visuals, question experience, Review Solutions, FSRS dock, custom modules and accepted timing semantics.
- Old Wrong Questions dashboard/tab path is intentionally retired/replaced by Spaced FSRS. Do not restore it to satisfy historical tests.
- Do not restore rejected rank/membership UI or unrelated redesigns.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless source material is explicitly an image/raster table.
- Source table object presence alone does not count as successful integration.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells.
- `[object Object]` in any learner-visible table is a hard failure.
- Browser regressions for table-bearing batches must check actual content, not merely table-container count.
- A table regression blocks `FULLY_VERIFIED` even when all surrounding prose/rationales are correct.

## Verified image layer carried into canonical

Current canonical image state at the last recorded checkpoint:
- assets: **163** total;
- bindings: **206** total;
- released questions: **165**;
- Anatomy released questions: **64**;
- Biochemistry released questions: **62**;
- Physiology released questions: **39**.

Image coverage is not complete merely because the reviewed registry is valid. Future workers must measure against authoritative source visual references. New image work starts from the exact current canonical head.

## Verified explanation layer carried into canonical

Verified donor/grafted work includes Anatomy Ch5 Q1–19, established Physiology batches, canonical Biochemistry rollout work, and subsequent verified batches represented by the deterministic inventory.

Explicitly do not infer historical unfinished work as verified merely because an old branch exists.

Deterministic canonical inventory checkpoint:
- total **2,711**;
- enhanced-reference **576**;
- pending **2,135**.

The inventory refresh workflow must continue to prevent new verified batches from leaving a stale global snapshot.

## Anti-fragmentation automation contract

- Explanation and image work build on `feature/marrow-canonical-full-current` and the 2,711-question denominator.
- Workers resolve the **current canonical HEAD at each run**, not a hard-coded SHA.
- Before every mutation, re-read canonical `STATE.md`, exact commit, shared inventory/registry fingerprints and current unfinished ownership.
- A stale open branch/PR is not a lock. A genuine blocker requires current authoritative memory plus matching live Git/commit evidence.
- Short-lived batch branches are allowed for CI safety, but work is not integrated until reconciled back to canonical.
- Explanation and image automations have separate shared-state lanes; within each lane, shared writers remain serialized.

## Verification state

Canonical checkpoint `cc24d396783f4738fe33f432ae521f5da436fee1`:
- Engineering Gate: success.
- Full Android/PWA/browser/APK/package/reproducibility/preview build: success.
- User preview check: accepted requested product features/fixes.
- Production promotion: skipped.

New structured-table repair branch:
- exact base: canonical `cc24d396783f4738fe33f432ae521f5da436fee1`;
- exact-head CI: pending/live Git is authoritative;
- canonical reconciliation: pending until green.

## Known problems / cautions

- The structured-table regression is the active blocker until the repair branch passes exact-head validation and is reconciled into canonical.
- Existing historical browser coverage was insufficient because it checked table existence rather than content; do not weaken the new populated-table gate.
- Image source-reference coverage remains incomplete and must continue coverage-first.
- Historical unfinished explanation branches must not be treated as completed work without stable-ID transplant + exact-head reverification.
- Production must remain untouched until explicit user approval.
- Preserve source-review flags; never invent missing source text, table cells or medical-image detail.

## Next step

1. Exact-head validate `feature/marrow-structured-table-renderer-fix-20260912`.
2. Repair only concrete failures; never weaken the populated-table assertion merely to obtain green CI.
3. Once green, reconcile the exact verified repair tree into `feature/marrow-canonical-full-current` if canonical HEAD has not diverged; otherwise rebase/reconcile and reverify.
4. After canonical is green again, all future explanation/image batches resolve that new current canonical HEAD.
5. Do not promote `main` or production without explicit user approval.

Canonical source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
Canonical automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
