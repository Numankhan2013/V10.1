# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/commit and CI from Git before writing. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- **Sole Marrow integration trunk:** `feature/marrow-canonical-full-current`.
- Product/UI base: user-approved V3/correct-index lineage.
- **Accepted baseline:** V11.6 Content Quality.
- Accepted product commit: `125d68b`.
- **build-verified:** last explanation-certified canonical content state is green through Engineering Gate **34650259296** and full Android/PWA/browser/APK/package/reproducibility/preview run **34650259281**; production promotion was skipped. Later image-only canonical work may advance live HEAD and must be resolved from Git.
- **device-verified:** the user verified the structured-table repair at `c829599050173d24408b72e8dc564ba501a156b4`; Anatomy Ch5 Q10 tables render populated cells correctly.
- `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` is mandatory for image and explanation workers.
- Production promotion remains explicit and guarded. `main`/production must not change without user approval.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.
- Raw imported source remains immutable.
- Anatomy full-bundle raw SHA-256: `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`.

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

## Current explanation state

Deterministic inventory before the current Anatomy batch:
- total **2,711**;
- enhanced-reference **581**;
- pending **2,130**;
- inventory fingerprint `eab956894794373d0d29a5ac1ee1087ec85ae5697eef7ff82d9d70cd04629cbe`.

### FULLY_VERIFIED_HISTORY

Verified canonical explanation work includes:
- Anatomy Ch5 Q1–9;
- Anatomy Ch5 Q10–19;
- Anatomy Ch5 Q20–Q24 — stable-ID transplant onto canonical, inventory refreshed, Engineering Gate **34650259296** and full run **34650259281** passed; production skipped;
- Biochemistry canonical verified Ch1–11/gold work;
- Physiology Ch5, Ch6, Ch7, Ch8, Ch9, Ch10 Q1–13 and Q14–18.

### CURRENT_UNVERIFIED explanation batch

- **Owner:** Anatomy.
- **BATCH_ID:** `anatomy-20260912-ch6-q1-q7`.
- **Range:** Anatomy Ch6 Q1–Q7, 7 contiguous questions, estimated workload **16.5**.
- **Canonical base SHA at branch creation:** `daa48f78ca208846f8be8781c64b8a297b5ab98d`.
- **Batch branch:** `feature/marrow-explanation-rollout-anatomy-ch06-q001-q007-current`.
- **Content commit:** `cf358f951930295ba03aae9b9ec5b7a658d69086`.
- **Current batch head:** `f004133f5e245be7a51b8ebc712c3f2b2c0bab74`.
- **PR:** #43 targeting `feature/marrow-canonical-full-current`.
- **State:** `STATIC_VALIDATED`; exact-head Engineering Gate **34665992491** completed **success** on `f004133f5e245be7a51b8ebc712c3f2b2c0bab74`. Deterministic inventory promotion/browser/full CI remain incomplete.
- **Reconstruction:** `marrow__ANAT_CH06_Q002` = `needs_manual_review` because the source-rendered question omits the numbered 1–4 structure legend; named cranial→caudal order is recoverable, but the missing original mapping was not invented.
- **Source validation contract:** `tools/test_marrow_anatomy_explanation_rollout.py` pins canonical Anatomy SHA `f38dc861…`, requires Ch6 Q1–Q7 stable-ID source records to equal their audited Phase-A records, and validates chapter/question ownership, emphasis anchors, answer/distractor mapping and Q2 reconstruction schema.
- **Inventory:** still 581/2130; no inventory regeneration has occurred yet.
- **CI:** Engineering Gate **34665992491** succeeded for exact batch head `f004133f…`; full Android/PWA run has not yet certified this batch.
- **Lane:** locked to Anatomy until this batch is reconciled FULLY_VERIFIED into canonical or explicitly abandoned.

## Anti-fragmentation automation contract

- Explanation and image work build on `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Resolve the current canonical HEAD at each run; never carry a hard-coded old SHA forward.
- Before mutation, re-read canonical `STATE.md`, exact commit, inventory/registry fingerprints and current ownership.
- A stale branch/PR is not a lock; blockers require current memory plus matching live Git evidence.
- A verified batch must be reconciled back into canonical before another explanation batch begins.
- Historical divergent branches may donate only stable-ID-scoped verified/authored content after ownership/duplicate checks; never wholesale-merge stale history.

## Current image state / cautions

- Image source-reference coverage remains incomplete; image automation has a separate writer lane.
- **Biochemistry image recovery was re-enabled on 2026-09-12.** Its integration base is `feature/marrow-canonical-full-current`, and it must recompute live Biochemistry source-reference coverage each run rather than trusting historical registry completeness.
- The Biochemistry image worker must remain enabled until the authoritative subject coverage `--require-complete --check` genuinely passes. Historical `feature/marrow-image-rollout-current` remains evidence/history only.
- Previously reviewed verified Biochemistry image work checked during the 2026-09-12 audit is already represented in canonical, including Ch1 Q4 D-glucose/D-mannose and Ch2 Q13 glycolysis bindings/assets. No other already-verified stranded batch was identified in that audit.
- Explanation work must not redesign UI or modify image ownership.

## Current product handoff — Continue Practice

- A durable handoff is recorded in `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Root cause found: the current Continue Practice behavior is not a true resume flow; it effectively resolves a globally unattempted question and can start a synthetic one-question Practice session instead of restoring the learner's interrupted topic/session.
- The future fix must use the shared Practice/session persistence architecture; do not create a Marrow-only or subject-specific duplicate engine.
- **Session-level control contract:** expose two clear, reachable actions — **Submit** and **Pause** — with no viewport clipping, hidden buttons, overlap or footer collision.
- **Pause is the resumable exit.** Resume the same topic/session with skipped + unseen questions still attemptable. Questions already answered correctly or incorrectly are finished for that session and must not be served again on resume.
- **Completed/green topic:** there is no paused session to restore. Continue Practice must target the immediately next topic in canonical topic order and take the learner there.
- Example invariant: 20-question topic, 3 correct + 1 wrong + 1 skipped + 15 unseen → Pause → Continue Practice = **16 remaining attemptable questions**; the four answered questions do not return.
- Do not infer completion merely from current index. Pause and completed/green are explicit, distinct lifecycle states.

## Known problems / cautions

- Current Anatomy batch has passed canonical-source/static exact-head Engineering validation but still needs deterministic +7 inventory regeneration, representative stable-ID browser regression, and exact-head full Android/PWA/APK/package/reproducibility/preview verification.
- Continue Practice currently needs the bounded shared-session-state repair described above; the present global-first-unattempted/one-question behavior is not the intended contract.
- Historical unfinished explanation branches remain historical unless explicitly transplanted by stable ID onto canonical and reverified.
- Production remains untouched until explicit user approval.
- Never invent missing source text, table cells, or medical-image detail.

## Next step

1. Resume Anatomy Ch6 Q1–Q7 only; do not start another explanation batch.
2. Promote the source-validated batch to `approved-rollout` and regenerate the deterministic 2,711-ID inventory; expected unique enhancement change is +7 (581→588, pending 2130→2123).
3. Add one representative stable-ID browser regression (prefer Q2 for reconstruction sensitivity or Q3 for structured-table protection).
4. Run exact-head Engineering Gate + full Android/PWA/browser/APK/package/reproducibility/preview workflow.
5. Reconcile verified explanation result back into canonical before releasing the explanation lane. Production promotion is prohibited.
6. In a bounded product patch from the exact current canonical HEAD, replace the broken Continue Practice behavior with the Pause/resume/completed-next-topic contract in `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`, including behavioral and viewport regressions.
7. Let the re-enabled Biochemistry image worker continue canonical coverage recovery independently under the single-writer/image policy until the full Biochemistry coverage gate passes.

Canonical source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
Canonical automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
Continue Practice handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
