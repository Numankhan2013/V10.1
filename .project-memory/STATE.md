# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/HEAD from Git. Historical detail belongs in `SESSION_LOG.md` and dedicated handoff documents.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- **Sole current integration trunk:** `feature/marrow-canonical-full-current`.
- Product/UI base: the user-approved V3/correct-index lineage from `feature/home-topic-content-integration-current`.
- Accepted baseline remains **V11.6 Content Quality**.
- Accepted product commit remains historical reference `125d68b`; the canonical consolidation candidate is newer and preview-only.
- Production promotion remains explicit and guarded.
- **build-verified:** pending exact-head full Android/PWA/browser/package completion after inventory regeneration and canonical-policy sync.
- **device-verified:** not yet for this consolidated corpus candidate.
- CI/browser success, device verification, user acceptance, and production promotion are distinct states.

## Canonical anti-fragmentation rule

`docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` is mandatory for Marrow explanation and image workers.

Historical rollout branches are evidence/history only. New batches may use short-lived candidate branches for safe CI, but they must start from the exact current canonical head and verified results must be reconciled back into `feature/marrow-canonical-full-current` before the lane is released.

Do not let a stale open PR/branch become authoritative merely because it is open, recent, or subject-specific. A real blocker requires current authoritative memory plus matching live Git/head evidence.

## Canonical Marrow ED8 source scope

The complete digitized source is consolidated on one product lineage:

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.

Anatomy Ch49–59 were restored from the validated canonical JSONL handoff and fill the pre-existing Abdomen/Pelvis, Lower Limb and Back taxonomy slots. No learner taxonomy redesign or backend source-ID renumbering was required.

Generated Anatomy bundle: `data/marrow/anatomy_ch001_063*`.
The generated manifest is hash-verified, reports `scope: complete_ch001_063`, and has no known source gap.

Raw imported Marrow source remains immutable. Runtime adaptation may normalize storage shape only; stems, options, source answer mapping, explanations, figures/tables and provenance are not rewritten merely for integration.

## Topic/index contract

- Preserve V3 Topics journey visuals and navigation behavior.
- Learner display numbering is visible-contiguous.
- Backend source chapter/question IDs remain source-faithful.
- Anatomy fills all planned source chapters through Ch63.
- Biochemistry includes Ch27 Regulation of gene expression and Ch28 Molecular genetics/recombinant DNA/genomic technologies.
- Physiology includes Ch34–43 through Exercise Physiology.
- Never show blank planned placeholders or fabricate unavailable source topics.

## Product architecture to preserve

Shared bank architecture remains:
`MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.

Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence or analytics by bank/subject.

Primary navigation remains **Home · FSRS · Tests · Insights · More**.
Study hierarchy remains **My Subjects → subject → Topics journey → topic → Practice/Topic Test**.

FSRS remains review-only: only incorrect or encountered-and-skipped questions may enter the learner-facing FSRS pool; genuinely unseen questions must not be introduced by FSRS.

## Explanation layer

- Deterministic explanation inventory denominator: **2,711 total**.
- Current regenerated canonical inventory: **429 enhanced / 2,282 pending**.
- Explanation fine-tuning remains keyed by stable question ID.
- Existing `FULLY_VERIFIED` explanation history from old branches may be transplanted only after source-ID ownership checks and exact-head canonical regressions.
- Unfinished historical batches are not silently treated as verified; explicitly transplant/resume them on the canonical head or leave them historical.

## Image layer

- The canonical source candidate currently validates the preserved image layer and installer.
- A later verified image-line registry exists and must be reconciled onto canonical by content hash + stable question ID + provenance, not by wholesale-merging the stale source lineage.
- Image integration workers must use `feature/marrow-canonical-full-current` as their integration base.
- Coverage completeness must be measured against complete canonical source references, not the old reviewed-registry denominator.

## Consolidation verification already proven

The canonical corpus job completed successfully and verified:

- Anatomy 1,115 / 63.
- Biochemistry 582 / 28.
- Physiology 1,014 / 43.
- Global 2,711 / 134.
- deterministic source bundle hashes;
- source ID/question-count ownership;
- uppercase runtime option contract;
- explicit topic taxonomy;
- image registry/install on the preserved canonical image layer;
- FSRS/shared bank architecture;
- deterministic explanation inventory regeneration.

The previous full Android/PWA attempt on pre-regeneration SHA `92a727d542e13ec7f223177fc24ede3e7d7d8c74` reached the Marrow explanation-inventory gate and failed only because the committed snapshot had not yet been regenerated after Physiology rollout coverage was added. The regeneration workflow then succeeded and produced canonical inventory commit `9ad3bc26ce650fc21e37387f81979fefd710923c` with 429 enhanced / 2,282 pending. A fresh exact-head full pipeline is required after this handoff/policy commit.

## Protected UI/product decisions

- Keep the V3 Home composition and corrected subject → Topics routing.
- Keep the approved Topics journey/state visuals and fixed Continue Learning tray.
- Keep question experience, Review Solutions, FSRS dock, custom modules and timing semantics intact.
- Topic Timed Test: strict 60 seconds per question.
- Tests/custom timed modules: global budget = question count × 60 seconds.
- Practice: no limiting countdown; timing analytics still recorded.
- Do not restore rejected rank/membership UI or unrelated redesigns during corpus work.

## Known problems / cautions

- This complete-corpus candidate is not yet build-verified until the new exact-head Android/PWA/browser/package pipeline passes.
- It is not yet device-verified by the user.
- Production must remain untouched until explicit user approval.
- Latest verified image and explanation rollout work may still be ahead of canonical; reconcile only verified work by stable IDs/content hashes/provenance.
- Do not infer an unfinished automation lock from stale open PRs/branches whose exact candidates are already FULLY_VERIFIED or superseded.
- Preserve source-review flags; never invent missing numbered labels/statements from source omissions.

## Next step

1. Run exact-head Android/PWA/browser/package/preview verification on the current canonical 2,711-question head.
2. Repair only concrete verification failures; do not weaken regression coverage or alter accepted UI to satisfy stale assertions.
3. Reconcile latest FULLY_VERIFIED image work onto canonical by content hash + stable question ID + provenance and re-run gates.
4. Reconcile latest FULLY_VERIFIED explanation work onto canonical by stable question ID and re-run inventory/browser/Engineering/full gates.
5. Keep all explanation/image scheduled workers pointed at canonical so future batches cannot fork the source/product lineage again.
6. Present the resulting canonical feature preview for user/device verification.
7. Promote production only after explicit user approval.

Canonical source-consolidation handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
Canonical automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
