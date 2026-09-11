# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/HEAD and CI from Git before writing. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- **Sole Marrow integration trunk:** `feature/marrow-canonical-full-current`.
- Product/UI base: user-approved V3/correct-index lineage.
- `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` is mandatory for image and explanation workers.
- Historical rollout branches/PRs are donor evidence/history only. New candidate branches must start from the exact canonical head and verified results must return to canonical before a lane is released.
- Production promotion remains explicit and guarded. This lineage is preview-only until user approval.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.

Anatomy Ch49–59 were restored from validated canonical JSONL and now fill the existing Abdomen/Pelvis, Lower Limb and Back taxonomy slots. Learner numbering is contiguous while backend source chapter/question IDs remain source-faithful. Raw imported source remains immutable.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · FSRS · Tests · Insights · More**.
- Study hierarchy: **My Subjects → subject → Topics journey → topic → Practice/Topic Test**.
- FSRS is review-only: incorrect or encountered-and-skipped questions may enter; genuinely unseen questions must not be introduced by FSRS.
- Preserve V3 Home, corrected subject→Topics routing, Topics journey visuals, question experience, Review Solutions, FSRS dock, custom modules and accepted timing semantics.
- Do not restore rejected rank/membership UI or unrelated redesigns.

## Verified image layer carried into canonical

The later verified image rollout was grafted by image-owned files/content hashes only; its stale source/UI/history was not merged.

Current canonical image state:
- assets: **163** total;
- bindings: **206** total;
- released questions: **165**;
- Anatomy released questions: **64**;
- Biochemistry released questions: **62**;
- Physiology released questions: **39**.

Current image graft head `0313f34d85470502a6bf725a7e7bf5efa7cc87f3` passed:
- Engineering Gate run **34637182951**;
- full Android/PWA/browser/APK/package/reproducibility/preview run **34637182841**;
- production promotion skipped.

Image coverage is **not complete merely because the reviewed registry is valid**. Future workers must measure against authoritative source visual references using `docs/MARROW_IMAGE_COVERAGE_GATE.md`; unresolved/untracked source references remain work.

## Verified explanation layer carried into canonical

Only previously `FULLY_VERIFIED` batches were grafted by stable question ID:
- Anatomy Ch5 Q1–9;
- Anatomy Ch5 Q10–19;
- Physiology Ch6;
- Physiology Ch7;
- Physiology Ch8;
- Physiology Ch9;
- Physiology Ch10 Q1–13;
- Physiology Ch10 Q14–18.

Existing canonical verified Biochemistry Ch1–11/gold work and Physiology Ch5 were preserved.

Explicitly **not** promoted as verified:
- Anatomy Ch5 Q20–24 unfinished historical work;
- Biochemistry Ch12 Q1–9/Q1–10 unfinished historical work.

Deterministic inventory on complete corpus after graft:
- total **2,711**;
- enhanced-reference **576**;
- pending **2,135**.

The inventory refresh workflow now triggers automatically when `data/marrow/explanation_*.json` changes, preventing future verified batches from leaving a stale global snapshot.

## Anti-fragmentation automation contract

- Explanation and image scheduled-task prompts are repointed to `feature/marrow-canonical-full-current` and the complete 2,711-question denominator.
- Scheduler enable/disable state is external; repository policy, not historical task text, defines lineage authority.
- Before every mutation, workers must re-read canonical `STATE.md`, exact head, shared inventory/registry fingerprints and current unfinished ownership.
- A stale open branch/PR is not a lock. A genuine blocker requires current authoritative memory plus matching live Git/head evidence.
- Short-lived batch branches are allowed for CI safety, but a batch is not considered integrated until reconciled back to canonical.

## Current verification state

- Complete source consolidation: verified.
- V3 product/browser baseline: full run **34636787305** passed.
- Verified image graft: Engineering + full build passed as recorded above.
- Verified explanation donor batches: historically exact-head verified before graft; canonical inventory regeneration succeeded on bot head `b41e4743ddfa5d45a1987dc049adb5660ab3fa35`.
- **Final requirement:** certify the current documentation/handoff head (which includes source + V3 + verified images + verified explanations) through exact-head Engineering Gate and full Android/PWA/browser/APK/package/reproducibility/preview. Live GitHub CI is authoritative over this static note.
- Device verification by user is still required before production promotion.

## Next action

1. Run/observe exact-head Engineering Gate and full Android/PWA pipeline for the current canonical head.
2. Repair only concrete failures; never weaken medical/source/coverage/product regressions merely to obtain green CI.
3. When exact-head green, re-enable the three explanation workers and the previously-active Biochemistry image worker; keep Anatomy/Physiology image workers in their prior disabled state unless user explicitly changes them.
4. All future verified batches must start from and reconcile into canonical.
5. Present canonical preview for user/device verification when desired.
6. Promote production only after explicit user approval.

Canonical source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
Canonical automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
