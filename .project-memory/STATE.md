# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Git `main` is the authoritative unified V11/Marrow product line.
- Current explanation candidate: `feature/marrow-explanation-rollout-biochem-ch02-current`,
  stacked on `feature/marrow-explanations-next-chapter` (Chapter 4 / PR #14).
- Resolve live branch/HEAD from Git; never hardcode a self-staling HEAD value.
- Accepted product baseline remains **V11.6 Content Quality** at `125d68b`,
  canonical APK run `34050921180`.
- Accepted product commit: `125d68b`.
- Production promotion remains explicit and guarded.

## Current Marrow bank

Shared architecture:
`MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
There is no duplicate Practice/CBT/Review/FSRS/sync/module/analytics engine.

Supplied Marrow ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 topics**.

Raw imported Marrow source is authoritative and immutable. Source bundles are
manifest/hash validated and runtime ingestion fails closed on corruption,
count/ID/option/topic-link drift. The user device-verified the expanded Marrow
integration/taxonomy and approved Topics/Continue Learning/FSRS behavior.

## Explanation-quality phase — active priority

Canonical procedure: `docs/MARROW_EXPLANATION_FINE_TUNING.md` +
`docs/MARROW_BANK_INTEGRATION.md`.

Gold-standard contract:
- approved reference = 62 Anatomy + 80 Physiology + user-approved 20-question
  Biochemistry sample = **162 questions**;
- one meaningful Key Takeaway;
- source-faithful structured detailed explanation with 1–4 selective emphasis
  anchors and native source tables preserved;
- exactly three concise wrong-option rationales mapped to the three incorrect options;
- augmentation is ID-keyed and separate from raw source;
- missing/ambiguous lists, values, figures or mechanisms remain explicit rather
  than being invented;
- FSRS stays in the fixed session footer.

Current deterministic inventory after completed augmentation layers:
- **223 enhanced / 1,892 pending**.
- Chapter 1: **23/23** (22 rollout + approved sample Q23).
- Chapter 2: **30/30** (29 rollout + approved sample Q9), on current candidate.
- Chapter 4: **11/11** (10 rollout + approved sample Q5).
- Chapter 4 full Android/PWA run 475 passed generated-app, browser, APK and
  packaged-contract verification.
- Chapter 2 was recovered from stale PR #11 onto the current Chapter 4 lineage.
  Its metadata, emphasis anchors, generalized chapter contracts, browser coverage
  and regenerated inventory are now aligned with the current architecture.

Source ambiguities remain reviewable, including the PCT question with an absent
lab panel and the vitamin-B12 combination question with a missing numbered enzyme list.

## Verification / release status

- Expanded Marrow bank integration is **build-verified** by prior successful
  Engineering/full Android+PWA runs.
- Build-verified ≠ device-verified ≠ accepted baseline.
- Chapter 4 candidate is build/browser/package verified; PR #14 remains unmerged.
- Chapter 2 candidate PR #15 is not yet build-verified until its current full CI
  run passes all source, explanation, browser, PWA, APK and package gates.
- V11.6 `125d68b` remains the **accepted baseline** until explicit user promotion.
- CI success alone must never promote production.

## Known problems / cautions

- Remaining non-reference Marrow explanations still need approved refinement.
- Preserve source tables, figure metadata and uncertainty/reconstruction notes.
- Do not rewrite raw JSONL/sharded source to improve display.
- Do not invent missing list items, lab values, graph labels or image-dependent facts.
- Do not alter Topics, source-PDF renderers, Practice/CBT/Review, FSRS, sync,
  modules, persistence or navigation during explanation work.
- Keep connector/Git writes bounded, deterministic and validated.
- Image rollout is paused after build-verified Batch 01. Batch 02 has six
  REVIEW_REQUIRED candidates checkpointed separately and none is learner-facing.

## Next step

1. Make PR #15 / Chapter 2 pass the complete current CI/browser/PWA/APK/package gate.
2. Once stable, exact next fresh content start is **Biochemistry Chapter 3 —
   Glycogen metabolism and glycogen storage disorders**.
3. Implement Chapter 3 only as another bounded ID-keyed augmentation batch,
   preserving raw source, native tables/figures, ambiguity and the approved grammar.
4. Keep production promotion deliberate and protect Practice/CBT/Review/FSRS/navigation.
