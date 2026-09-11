# MARROW CANONICAL AUTOMATION POLICY

This file is the authoritative anti-fragmentation overlay for all Marrow explanation and image automations.

## Canonical integration trunk

The sole current integration trunk is:

`feature/marrow-canonical-full-current`

Historical rollout branches remain evidence/history only. They must never become the base for a new batch merely because they are open, recent, or subject-specific.

Short-lived batch branches are allowed for safe CI, but every such branch MUST:

1. start from the exact current head of `feature/marrow-canonical-full-current`;
2. record that base SHA in project memory;
3. preserve stable question IDs and shared product architecture;
4. reconcile/fast-forward the verified batch back into `feature/marrow-canonical-full-current` before the lane is released;
5. never release the lane while a verified result exists only on a side branch.

Every new image or explanation batch must resolve the **current canonical HEAD at run start**. Do not carry forward a hard-coded historical canonical SHA.

If this policy conflicts with an older branch/base instruction in another runbook, this policy wins for lineage/base selection. Medical/source-quality rules in the subject runbooks remain fully authoritative.

## Complete canonical Marrow ED8 corpus

The current canonical source scope is:

- Anatomy: Chapters 1–63, 1,115 questions, 63 visible source topics.
- Biochemistry: Chapters 1–28, 582 questions, 28 visible source topics.
- Physiology: Chapters 1–43, 1,014 questions, 43 visible source topics.
- Global: 2,711 questions, 134 visible source topics.

Do not use the historical 2,115-question Phase-A denominator or the intermediate 2,455-question denominator for completeness, inventory, coverage, or next-source-order decisions.

Raw imported source remains immutable. The complete-corpus runtime bundles and canonical JSONL handoffs are source-faithful integration artifacts, not permission to rewrite medical source content.

## Explanation work

- Read `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md`, then this policy.
- Read project memory and implementation state from the canonical integration trunk or an exact current batch branch based on it.
- Resolve next incomplete source-order work against the 2,711-question corpus.
- Use stable question IDs for all augmentation/inventory reconciliation.
- `FULLY_VERIFIED` history from old branches may be transplanted only after stable-ID/source ownership checks and canonical exact-head regressions.
- Unfinished historical branches are not silently adopted. Either resume/transplant them explicitly onto the canonical head or leave them historical.

## Structured explanation table contract

Structured tables are part of the **explanation pipeline**, not deferred image work, unless the source explicitly requires a raster/image table asset.

Canonical ED8 structured tables may use object-keyed schema such as:

- columns: `{key, label}` objects;
- rows: objects keyed by the column `key`.

The learner renderer must preserve the source table as a real populated table. Merely preserving a table object in JSON is not sufficient.

Hard failures:

- `[object Object]` appears in a learner-visible table;
- a non-empty source table renders empty headers or empty cells;
- source column ownership/order is lost;
- a table is flattened into prose when structured source table data exists;
- browser QA checks only for the existence of a table container without checking meaningful content.

The deterministic compatibility layer is `tools/apply_marrow_structured_table_renderer_v1.py`. It adapts canonical object-keyed table data to the accepted shared table renderer without mutating source data or changing table styling.

`tools/verify_marrow_structured_table_browser.py` is the learner-visible regression. It must verify actual header/cell content and reject object-string leakage. Anatomy Chapter 5 Question 10 is the fixed sentinel because its source table is known, populated, and was the user-reported regression.

Future explanation batches containing tables must validate both source table integrity and rendered table content. A broken table blocks `FULLY_VERIFIED` even when takeaway, prose and distractor rationales are otherwise correct.

## Image work

- Read the Marrow image automation runbook plus this policy.
- `INTEGRATION_BASE_BRANCH` is `feature/marrow-canonical-full-current`.
- The shared image registry/progress state on the canonical trunk is authoritative after reconciliation.
- Existing verified image assets/bindings from historical image branches may be transplanted by content hash + stable question ID + provenance; never wholesale-merge an old incomplete source lineage.
- Coverage completeness is measured against the complete canonical corpus/source references, not the old reviewed-registry denominator.
- Image automation owns source-native visual assets (figures, diagrams, microscopy, radiology, image-only tables). It does **not** repair text/structured explanation tables that already exist as table data.

## Shared-writer / lane rule

Explanation and image workflows have separate shared-state lanes, but within each workstream only one writer may mutate its shared registry/inventory at a time.

A blocker requires current authoritative memory plus live Git/head evidence. A stale open PR/branch that is already verified or superseded is non-blocking.

Before every write, re-read canonical `STATE.md`, exact branch/head, shared fingerprint/registry state, and current ownership. If those changed, stop and rebase/reconcile rather than choosing one side.

## Product protection

The V3/correct-index product lineage and accepted shared Practice/CBT/Review/FSRS/sync/modules/navigation architecture are preserved. Do not redesign UI, fork engines by subject, merge/promote production, or weaken regressions as part of content/image automation.

Production remains explicit and user-approved only.
