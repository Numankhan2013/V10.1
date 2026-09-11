# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/HEAD from Git. Historical detail belongs in `SESSION_LOG.md` and dedicated handoff documents.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Current consolidation branch: `feature/marrow-canonical-full-current`.
- Product/UI base: the user-approved V3/correct-index lineage from `feature/home-topic-content-integration-current`.
- Accepted baseline remains **V11.6 Content Quality**.
- Accepted product commit: `125d68b`.
- The consolidation branch is preview-only. Production promotion remains explicit and guarded.
- **build-verified:** pending exact-head full Android/PWA completion for the consolidated corpus.
- **device-verified:** not yet for this consolidated corpus candidate.
- CI/browser success, device verification, user acceptance, and production promotion are distinct states.

## Canonical Marrow ED8 source scope

The complete digitized source is now consolidated on one product lineage:

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
- Anatomy now fills all 10 planned major sections through Ch63.
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

## Explanation and image layers

- Deterministic explanation inventory after source consolidation: **2,711 total**.
- Current detected enhanced layer on this lineage: **401 enhanced-reference / 2,310 pending**.
- Explanation fine-tuning remains a separate controlled layer keyed by stable question IDs.
- The V3 image registry/layer was preserved while source bundles were consolidated; image integration remains separately controlled.
- Do not take source consolidation as proof that every latest image/explanation rollout branch has already been transplanted. Reconcile those verified layers by stable question ID only after the source candidate is green.

## Consolidation verification

The one-shot canonical corpus job completed successfully and verified:

- Anatomy 1,115 / 63.
- Biochemistry 582 / 28.
- Physiology 1,014 / 43.
- Global 2,711 / 134.
- deterministic source bundle hashes;
- source ID/question-count ownership;
- uppercase runtime option contract;
- explicit topic taxonomy;
- deterministic explanation inventory regeneration.

The first Android/PWA attempt on the generated candidate stopped at project-memory length validation before product transformation. That was a handoff-format failure, not a medical/source-data failure. This STATE file is the bounded repair.

## Protected UI/product decisions

- Keep the V3 Home composition and corrected subject → Topics routing.
- Keep the approved Topics journey/state visuals and fixed Continue Learning tray.
- Keep question experience, Review Solutions, FSRS dock, custom modules and timing semantics intact.
- Topic Timed Test: strict 60 seconds per question.
- Tests/custom timed modules: global budget = question count × 60 seconds.
- Practice: no limiting countdown; timing analytics still recorded.
- Do not restore rejected rank/membership UI or unrelated redesigns during corpus work.

## Known problems / cautions

- This complete-corpus candidate is not yet build-verified until the exact-head Android/PWA/browser/package pipeline passes.
- It is not yet device-verified by the user.
- Production must remain untouched until explicit user approval.
- Latest verified image and explanation rollout branches may be ahead of the layers currently present on this consolidation lineage; reconcile them only after source/product verification.
- Do not infer an unfinished automation lock from stale open PRs/branches whose exact candidates are already FULLY_VERIFIED.
- Preserve source-review flags; never invent missing numbered labels/statements from source omissions.

## Next step

1. Run exact-head Android/PWA/browser/package/preview verification on the consolidated 2,711-question candidate.
2. Repair only concrete verification failures; do not weaken regression coverage or alter accepted UI to satisfy stale assertions.
3. Once source/product verification is green, reconcile latest FULLY_VERIFIED image and explanation layers by stable question IDs.
4. Present the resulting feature preview for user/device verification.
5. Promote production only after explicit user approval.

Canonical source-consolidation handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
