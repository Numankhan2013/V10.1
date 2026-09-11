# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/commit and CI from Git before writing. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- **Sole Marrow integration trunk:** `feature/marrow-canonical-full-current`.
- Product/UI base: user-approved V3/correct-index lineage.
- **Accepted baseline:** V11.6 Content Quality.
- Accepted product commit: `125d68b`.
- **build-verified:** current canonical product/content state is green through Engineering Gate run **34650259296** and full Android/PWA/browser/APK/package/reproducibility/preview run **34650259281**; production promotion was skipped.
- **device-verified:** the user verified the structured-table repair at `c829599050173d24408b72e8dc564ba501a156b4`; Anatomy Ch5 Q10 tables render populated cells correctly.
- Canonical was fast-forwarded to that exact table-fixed tree, then Anatomy Ch5 Q20–Q24 was transplanted by stable question ID only. Historical divergent explanation branch history was not merged.
- Canonical content lineage includes transplant commit `66628b753513963232f3c5ee18e6602a41c400d8`, deterministic inventory refresh commit `5ae636612e8e476dbd651bcda15b502aced9af45`, and subsequent handoff-only memory commits.
- `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` is mandatory for image and explanation workers.
- New batch branches must start from the exact current canonical HEAD and verified results must return to canonical before a lane is released.
- Production promotion remains explicit and guarded. `main`/production must not change without user approval.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.
- Raw imported source remains immutable.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · FSRS · Tests · Insights · More**.
- Study hierarchy: **My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test**.
- FSRS remains review-only; genuinely unseen questions are not introduced by FSRS.
- Old Wrong Questions dashboard/tab remains retired/replaced by Spaced FSRS.
- Preserve approved V3 Home/Topics/question/Review/FSRS/module/timing behavior; do not restore rank/membership UI.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order.
- `[object Object]` in learner-visible output is a hard failure.
- Table-bearing browser regressions must verify actual expected cell content, not container existence.
- The user device-verified the Q10 table fix on the immutable preview from `c829599`.

## Current image state

- assets **163**; bindings **206**; released questions **165**;
- Anatomy **64**, Biochemistry **62**, Physiology **39** released image questions.
- Image source-reference coverage remains incomplete; future image work must start from the exact current canonical head.

## Current explanation state

Deterministic inventory after the Anatomy Q20–Q24 transplant:
- total **2,711**;
- enhanced-reference **581**;
- pending **2,130**;
- inventory fingerprint `eab956894794373d0d29a5ac1ee1087ec85ae5697eef7ff82d9d70cd04629cbe`.

### FULLY_VERIFIED_HISTORY

Verified canonical explanation work includes:
- Anatomy Ch5 Q1–9;
- Anatomy Ch5 Q10–19;
- **Anatomy Ch5 Q20–Q24** — stable-ID transplant onto the canonical table-fixed lineage, deterministic inventory refreshed, Engineering Gate **34650259296** passed, full Android/PWA/browser/APK/package/reproducibility/preview run **34650259281** passed; production promotion skipped;
- Biochemistry canonical verified Ch1–11/gold work;
- Physiology Ch5, Ch6, Ch7, Ch8, Ch9, Ch10 Q1–13 and Q14–18.

### CURRENT_UNVERIFIED explanation batch

- **None. The serialized explanation lane is released.**
- The stale historical Anatomy Q20–Q24 branch is donor evidence/history only and must never be merged wholesale.
- Old open rollout branches/PRs do not constitute locks unless current canonical memory plus live Git prove an unfinished canonical-based batch.

## Anti-fragmentation automation contract

- Explanation and image work build on `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Resolve the **current canonical HEAD at each run**; never carry a hard-coded old SHA forward.
- Before mutation, re-read canonical `STATE.md`, exact commit, inventory/registry fingerprints and current ownership.
- A stale branch/PR is not a lock; blockers require current memory plus matching live Git evidence.
- Short-lived batch branches are allowed only for CI safety. Never accumulate long-lived subject lineages.
- A verified batch must be reconciled back into canonical before another explanation batch begins.
- Historical divergent branches may donate only stable-ID-scoped verified/authored content after ownership/duplicate checks; never wholesale-merge stale history.

## Verification state

- Table renderer repair `c829599`: full build passed and user device verification confirmed the learner-facing table defect is fixed.
- Anatomy Q20–Q24 transplant `66628b7`: initial candidate correctly failed only because the deterministic inventory was stale.
- Inventory workflow regenerated and validated the canonical inventory at `5ae6366`, yielding **581 enhanced / 2,130 pending**.
- Canonical handoff candidate then passed Engineering Gate **34650259296** and full Android/PWA/browser/APK/package/reproducibility/preview run **34650259281**.
- Populated Marrow structured-table browser verification passed in the full run.
- APK/package/reproducibility checks passed.
- Cloudflare preview deployment passed.
- Production promotion was skipped.

## Known problems / cautions

- Image source-reference coverage remains incomplete.
- Historical unfinished explanation branches remain historical unless explicitly transplanted by stable ID onto canonical and reverified.
- Production remains untouched until explicit user approval.
- Never invent missing source text, table cells, or medical-image detail.

## Next step

1. Explanation workers may resume from this single canonical lineage.
2. Anatomy next work must start at the exact next incomplete source-order question after Ch5 Q24; do not resume from the stale historical Q20–Q24 branch.
3. Physiology/Biochemistry workers likewise resolve the live canonical head and current inventory before authoring.
4. Each verified future batch returns to canonical before the explanation lane is released.
5. Do not promote `main` or production without explicit user approval.

Canonical source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
Canonical automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
