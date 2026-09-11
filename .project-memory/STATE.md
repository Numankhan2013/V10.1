# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/commit and CI from Git before writing. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- **Sole Marrow integration trunk:** `feature/marrow-canonical-full-current`.
- Product/UI base: user-approved V3/correct-index lineage.
- **Accepted baseline:** V11.6 Content Quality.
- Accepted product commit: `125d68b`.
- Canonical checkpoint before the structured-table repair: `cc24d396783f4738fe33f432ae521f5da436fee1`.
- **build-verified:** that canonical checkpoint passed exact-head Engineering Gate plus full Android/PWA/browser/APK/package/reproducibility/preview verification.
- **device-verified:** user preview review accepted the requested product/UI fixes at that checkpoint, then exposed the structured-table defect below.
- `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` is mandatory for image and explanation workers.
- New batch branches must start from the exact current canonical HEAD and verified results must return to canonical before a lane is released.
- Production promotion remains explicit and guarded. `main`/production must not change without user approval.

## Current blocker — structured explanation table regression

User preview review exposed a real learner-facing defect in Anatomy Ch5 Q10: **Pharyngeal arch muscle derivatives** rendered `[object Object]` headings and blank cells.

Investigation established:
- canonical source table data is populated and medically intact;
- source columns use object schema such as `{key, label}`;
- source rows are objects keyed by those column keys;
- explanation fine-tuning preserves `structuredExplanation.tables`;
- shared legacy `nkRenderMarrowTable` expected scalar columns + positional row arrays;
- direct object coercion produced `[object Object]`; numeric row access produced blank cells;
- old browser QA checked only that `.nk-marrow-table` existed, so broken content passed.

Ownership: **explanation/runtime renderer integration**, not deferred image work. Image automation owns source-native visual assets, not an already-structured text table.

Repair branch: `feature/marrow-structured-table-renderer-fix-20260912`.
Exact repair base: `cc24d396783f4738fe33f432ae521f5da436fee1`.

Repair components:
- `tools/apply_marrow_structured_table_renderer_v1.py`: audits source table payloads, normalizes object-keyed columns/rows to the shared renderer, preserves styling/source, and fails closed on empty source rows/headers or object-string leakage.
- `tools/verify_marrow_structured_table_browser.py`: opens Anatomy → Marrow → Ch5 → Q10, answers it, asserts actual expected table headers/cells, rejects `[object Object]`/blank output, and captures a screenshot.
- `.github/workflows/build-apk.yml`: installs the compatibility layer after Marrow bank generation, runs the new browser regression, and requires its marker in generated + packaged output.
- `tools/verify_build_pipeline.py`: protects transform ordering and requires the new regression.

Do not call this repair integrated or `FULLY_VERIFIED` until exact-head CI passes and the verified tree is reconciled into canonical.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.
- Never use historical 2,115 or 2,455 denominators for completeness/inventory/coverage decisions.
- Raw imported source remains immutable.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · FSRS · Tests · Insights · More**.
- Study hierarchy: **My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test**.
- Subject Home cards expose PrepLadder + Marrow; enhanced Marrow explanations are learner-visible.
- FSRS remains review-only; genuinely unseen questions are not introduced by FSRS.
- Old Wrong Questions dashboard/tab is intentionally retired/replaced by Spaced FSRS; do not restore it for stale tests.
- Preserve approved V3 Home/Topics/question/Review/FSRS/module/timing behavior; do not restore rank/membership UI.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Source table object presence alone is insufficient.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order.
- `[object Object]` in learner-visible output is a hard failure.
- Table-bearing browser regressions must check actual expected content, not merely container count.
- Any such regression blocks `FULLY_VERIFIED` even if surrounding prose/rationales are correct.

## Current content state

Image checkpoint:
- assets **163**; bindings **206**; released questions **165**;
- Anatomy **64**, Biochemistry **62**, Physiology **39** released image questions.
- Image coverage remains incomplete; new image work starts from the exact current canonical head.

Explanation checkpoint:
- canonical deterministic inventory **2,711 total / 576 enhanced / 2,135 pending**;
- historical unfinished branches are not verified merely because they exist;
- verified/transplanted work remains keyed by stable question ID.

## Anti-fragmentation automation contract

- Explanation and image work build on `feature/marrow-canonical-full-current` and the 2,711-question corpus.
- Resolve the **current canonical HEAD at each run**; never carry a hard-coded old SHA forward.
- Before mutation, re-read canonical `STATE.md`, exact commit, shared inventory/registry fingerprints and current ownership.
- A stale branch/PR is not a lock; blockers require current memory + matching live Git evidence.
- Short-lived batch branches are allowed for CI safety, but work is not integrated until reconciled back to canonical.
- Explanation and image work have separate lanes; shared writers within a lane remain serialized.

## Verification state

Canonical checkpoint `cc24d396783f4738fe33f432ae521f5da436fee1`:
- Engineering Gate: success.
- Full Android/PWA/browser/APK/package/reproducibility/preview: success.
- User preview review: requested product/UI behavior accepted.
- Production promotion: skipped.

Structured-table repair branch:
- exact base: canonical checkpoint above;
- exact-head CI: pending/live Git is authoritative;
- canonical reconciliation: pending until green.

## Known problems / cautions

- Structured-table regression is the active blocker until repair CI is green and reconciled into canonical.
- Historical table QA was too weak; never weaken the new populated-table gate to obtain green CI.
- Image source-reference coverage remains incomplete.
- Historical unfinished explanation work needs stable-ID transplant + exact-head reverification before promotion.
- Production remains untouched until explicit user approval.
- Never invent missing source text, table cells, or medical-image detail.

## Next step

1. Exact-head validate `feature/marrow-structured-table-renderer-fix-20260912`.
2. Repair only concrete failures; keep the populated-table assertion strict.
3. When green, reconcile the exact verified tree into `feature/marrow-canonical-full-current` if canonical has not diverged; otherwise rebase/reverify.
4. Future image/explanation batches then resolve that new current canonical HEAD.
5. Do not promote `main` or production without explicit user approval.

Canonical source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
Canonical automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
