# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`; `main` remains the authoritative merged V11/Marrow line.
- Anatomy topic-index v2 merged through PR #29; Biochemistry topic-index v2 through PR #30; Physiology topic-index v2 through PR #31.
- Current source-ingest branch: `feature/marrow-biochem-ch27-28-integration`.
- Accepted device-tested rollback baseline remains **V11.6 Content Quality** at `125d68b`.
- Accepted product commit: `125d68b`.
- Production promotion remains explicit and guarded.

## Current feature Marrow bank

Shared architecture remains `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`; Practice/CBT/Review/FSRS/sync/modules/analytics remain shared.

Current feature source scope after deterministic Ch27–28 integration:
- Anatomy: **898 questions / 52 imported topics** — source Ch1–48 plus Ch60–63.
- Biochemistry: **582 / 28** — Ch1–28 complete for the supplied Biochemistry set.
- Physiology: **1,014 / 43** — Ch1–43 complete for the supplied Physiology set.
- Combined: **2,494 globally unique questions / 123 imported source topics**.

Raw imported Marrow source is authoritative and immutable. Source-ingest adapters normalize storage/runtime field names and option-label casing only; stems/options/answers/explanation text/tables/figures/provenance are not rewritten merely for integration.

## Biochemistry Ch27–28 integration — 2026-09-10

User supplied the canonical JSONL artifacts directly:
- Ch27 `Regulation of gene expression`: **12 questions**, source SHA-256 `d4d4b5e6b89bd97050d907818603aa2f3099428cfd2eae71d3a98596cfb7c349`.
- Ch28 `Molecular genetics, recombinant DNA & genomic technologies`: **27 questions**, source SHA-256 `f7f1d24434cb072bb3e849d960fda3f654aae66a148475c5b0f322cd08c74027`.
- Total added: **39 questions / 2 source topics**.
- Deterministic adapter: `tools/integrate_biochem_user_ch027_028.py`.
- Runtime bundle: `data/marrow/biochemistry_ch001_028.zlib.b64.part*` plus SHA-verified manifest.
- Ch27 maps to `Genetics` planned slot `genetics:05`; Ch28 maps to `genetics:06`.
- Learner-visible Biochemistry numbering remains contiguous **1–28**; backend source IDs remain 27 and 28.
- Source/data/taxonomy/inventory prechecks passed on bot commit `229867ebbc1dc1fa6d618a1f7160c52ed66e3652`.
- The 39 new explanations remain source-as-is and **pending**; no explanation enhancement was performed.

## Existing Anatomy / Physiology expansion

Physiology Ch34–43 added 261 questions and is packaged as `data/marrow/physiology_ch001_043.zlib.b64.part*`.

Anatomy Ch60–63 added 79 questions:
- Ch60 Bones, Joints and Cartilage — 30 Q.
- Ch61 Muscles and Tendons — 16 Q.
- Ch62 Cardiovascular, Lymphatic and Nervous Systems — 20 Q.
- Ch63 Skin, Connective Tissue and Ligaments — 13 Q.
- Ch49–59 are still not present in the committed handoff/reachable searched history; never fabricate them.

## Topic-index contract

All revised subjects use `data/marrow/topic_index_taxonomy.json` with `catalogVersion: 2`, full `plannedIndex`, current imported `topics`, `plannedSlots`, and `displayNumbering: visible-contiguous`.

- Store the full intended syllabus even when source topics are not imported.
- Render only imported source topics; no disabled/blank placeholders.
- Hide a planned major index with zero imported source coverage.
- Combined/split source chapters remain source-faithful; `plannedSlots` supplies learner metadata without duplicating questions.
- Learner numbering follows arranged visible order; backend source chapter IDs never change.

Current plans/imports:
- Anatomy: **71 planned slots / 52 imported source topics / 898 Q**.
- Biochemistry: **32 planned slots / 28 imported source topics / 582 Q**.
- Physiology: **42 planned slots / 43 imported source topics / 1,014 Q**; multiple source chapters may map to one planned slot.

## Explanation and image phases

- Explanation quality work is explicitly separate from source ingest.
- Approved/enhanced inventory remains **184 questions**.
- Current deterministic inventory is **184 enhanced / 2,310 pending** across 2,494 questions.
- All 39 new Biochemistry questions entered as pending.
- No explanation enhancement, reconstruction rewrite, or medical-content polish was performed for Ch27–28.
- Image registry/release status remains a separate governed pipeline; source figure metadata is preserved.

## Verification status

- The option-state regression repair is **build-verified** and **device-verified** by the user.
- User confirmed the repaired preview works well after the wrong-answer incident.
- Regression root cause: newer automation source used lowercase `a/b/c/d`; the legacy session renderer historically assumed uppercase A–D. Generated runtime banks are now normalized to uppercase A–D and the shared renderer is case-tolerant; canonical source JSONL remains unchanged.
- Browser regression requires exactly one red selected-wrong option plus one green true-correct option and asserts computed CSS values. It covers an old Marrow question, newly ingested Physiology, newly ingested Anatomy, and the dashboard → Wrong Questions → Practice path.
- Full repaired feature run `34458523873` passed browser, APK and PWA gates; production remained unpromoted.
- Biochemistry Ch27–28 source/data integration passed its deterministic checks at `229867ebbc1dc1fa6d618a1f7160c52ed66e3652`: **582/28 Biochemistry, 2,494/123 overall, 184 enhanced unchanged**.
- Ch27/28 browser coverage now checks both new topics, raw-schema leakage, contiguous 1–28 numbering, and the red+green answer-state contract.
- **Biochemistry Ch27–28 is not yet final-build-verified or device-verified.** The exact-head browser/APK/PWA build from this finalized branch is the blocking gate before merge or production promotion.

## Known problems / cautions

- Anatomy Ch49–59 source files remain missing from the reachable automation handoff; integrate them only from real canonical artifacts.
- Do not improve pending explanations during source integration.
- Do not expose raw JSONL/schema objects in learner-facing question/explanation views.
- Preserve approved Topics visuals, FSRS dock, PDF renderers, Practice/CBT/Review, Wrong Questions, sync, modules, persistence and navigation.
- Do not merge or promote a source expansion when the full exact-head regression suite is red.

## Next step

1. Run the final exact-head browser/APK/PWA build for `feature/marrow-biochem-ch27-28-integration`.
2. Require Biochemistry 582/28, overall 2,494/123, raw-JSON leakage clean, and all red+green answer-state regressions green.
3. Deploy a feature preview only after all gates pass and have the user device-check Ch27/28.
4. After user acceptance, merge the verified source expansion; production promotion remains explicit.
5. Resume Anatomy Ch49–59 only when canonical source artifacts are supplied/found.

Canonical Marrow integration procedure: `docs/MARROW_BANK_INTEGRATION.md`.
