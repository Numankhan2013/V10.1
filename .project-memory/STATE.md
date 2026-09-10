# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`; `main` remains the authoritative merged V11/Marrow line.
- Anatomy topic-index v2 merged through PR #29 at `424d7b2`.
- Biochemistry topic-index v2 merged through PR #30 at `3b0d9dc`.
- Physiology topic-index v2 merged through PR #31 at `fcf0476`.
- Current source-ingest branch: `feature/marrow-automation-ingest-anatomy`; it is based on the verified Physiology Ch34–43 source expansion.
- Resolve live branch tip from Git; never hardcode a self-staling HEAD.
- Accepted device-tested rollback baseline remains **V11.6 Content Quality** at `125d68b`.
- Accepted product commit: `125d68b`
- Production promotion remains explicit and guarded.

## Current feature Marrow bank

Shared architecture remains `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`; Practice/CBT/Review/FSRS/sync/modules/analytics remain shared.

Current feature source scope:
- Anatomy: **898 questions / 52 imported topics** — source Ch1–48 plus Ch60–63.
- Biochemistry: **543 / 26** — Ch27/28 source artifact still not located.
- Physiology: **1,014 / 43** — Ch34–43 expansion included.
- Combined: **2,455 globally unique questions / 121 imported source topics**.

Raw imported Marrow source is authoritative and immutable. Source-ingest adapters normalize storage-field names only; stems/options/answers/explanation text/tables/figures/provenance are not rewritten merely for integration.

## Automation handoff discovery — 2026-09-10

Canonical committed automation handoff is on `feature/marrow-bank-pilot` under `data/marrow/automation_ingest/`.

Physiology Ch34–43:
- 261 questions total; now packaged as `data/marrow/physiology_ch001_043.zlib.b64.part*`.
- Full feature build run `34450005298` passed browser, APK, PWA and raw-schema leakage checks.
- Stable preview used for verification: `https://feature-marrow-automation-in.nk-qbank.pages.dev`.
- Immutable preview: `https://6426c541.nk-qbank.pages.dev`.

Anatomy automation payload actually reachable in Git:
- Ch60 **Bones, Joints and Cartilage** — 30 Q.
- Ch61 **Muscles and Tendons** — 16 Q.
- Ch62 **Cardiovascular, Lymphatic and Nervous Systems** — 20 Q.
- Ch63 **Skin, Connective Tissue and Ligaments** — 13 Q.
- New Anatomy total: **79 questions / 4 source topics**.
- Ch49–59 are not present in the committed handoff, current branch tips, or searched reachable history. Treat this as an explicit source-artifact gap; do not fabricate continuity.

Biochemistry Ch27/28 were reported as automation-produced but no matching committed payload was located in the intended handoff, branch tips, or searched reachable history. Do not fabricate them from planned taxonomy labels; integrate only when the user supplies or identifies the real JSON/JSONL artifact.

## Anatomy Ch60–63 implementation

- Deterministic adapter: `tools/integrate_anatomy_automation_ch060_063.py`.
- Runtime bundle: `data/marrow/anatomy_ch001_048_plus_060_063.zlib.b64.part*` with manifest and SHA-verified compressed/raw payload.
- Existing 819 Ch1–48 records remain unchanged and are a strict subset of the 898-question bundle.
- Ch60 → `General anatomy` planned slot **Bones, joints, and cartilage**.
- Ch61 → planned **Muscles and tendon**.
- Ch62 → planned **Cardiovascular, lymphatic, and nervous systems**.
- Ch63 → planned **Skin** + **Connective tissue and ligaments** without splitting or duplicating its source questions.
- Learner-visible Anatomy topics are now source IDs `1–48, 60–63`, displayed contiguously as learner numbers **1–52**.
- Lower limb and Back still have no imported source topics and therefore remain hidden planned sections; General anatomy now renders because Ch60–63 exist.

## Topic-index contract

All revised subjects use `data/marrow/topic_index_taxonomy.json` with `catalogVersion: 2`, full `plannedIndex`, current imported `topics`, `plannedSlots`, and `displayNumbering: visible-contiguous`.

- Store the full intended syllabus even when source topics are not imported.
- Render only imported source topics; no disabled/blank placeholders.
- Hide a planned major index with zero imported source coverage.
- Combined/split source chapters remain source-faithful; `plannedSlots` supplies learner metadata without duplicating questions.
- Learner numbering follows arranged visible order; backend source chapter IDs never change.

Current plans/imports:
- Anatomy: **71 planned slots / 52 imported source topics / 898 Q**.
- Biochemistry: **32 planned / 26 imported / 543 Q**.
- Physiology: **42 planned / 43 imported source topics / 1,014 Q**; multiple source chapters may map to one planned slot.

## Explanation and image phases

- Explanation quality work is explicitly separate from this source ingest.
- Approved/enhanced inventory remains **184 questions**.
- Current inventory is **184 enhanced / 2,271 pending** across 2,455 questions.
- All 79 new Anatomy questions entered as pending; no explanation enhancement, reconstruction rewrite, or medical-content polish was performed in this ingest.
- Existing image registry/release status remains separate. New source figure metadata is preserved with assets still governed by the image pipeline.

## Verification status

- Anatomy primary source/data gates passed after integration:
  - `MARROW_DATA_OK anatomy=898/52 biochemistry=543/26 physiology=1014/43 total=2455`
  - taxonomy: **121 current source topics**, Anatomy 52 visible, contiguous numbering, no placeholders.
  - explanation inventory: **2,455 total / 184 enhanced / 2,271 pending**.
  - image-consumer and Biochemistry rollout count-dependent tests passed.
- The source/data transformation is **build-verified at its deterministic prechecks**; the full browser/APK/PWA build remains the final feature verification gate.
- Browser wrapper includes a new Ch60 learner-view check that fails on raw keys such as `question_id`, `chapter_number`, `correct_option`, `schema_version`, `review_status`, or `source_fidelity`, plus serialized JSON fragments.
- Current operational source consumers and docs have been aligned to the new Anatomy and Physiology bundles.
- Full feature browser/APK/PWA CI for Anatomy Ch60–63 passed in run `34451249088`; preview deployment succeeded.
- Regression incident found after device preview: automation-adapted Physiology Ch34–43 and Anatomy Ch60–63 emitted lowercase option labels, while the session renderer expected uppercase A–D. This could show the chosen wrong option red without highlighting the actual correct option green. The repair normalizes runtime labels to uppercase, hardens the renderer case handling, adds fail-closed A–D validation, and adds browser red+green checks including the Wrong Questions flow.
- New Anatomy content is **not yet device-verified**. CI success alone does not change the accepted baseline or promote production.

## Known problems / cautions

- Ch49–59 Anatomy source files are missing from the reachable automation handoff; integrate them later only from real canonical artifacts.
- Biochemistry Ch27/28 source files are still pending user location/supply.
- Do not improve remaining explanations during source integration.
- Do not expose raw JSONL/schema objects in learner-facing question/explanation views.
- Do not rewrite source records for taxonomy placement.
- Preserve approved Topics visuals, FSRS dock, PDF renderers, Practice/CBT/Review, sync, modules, persistence and navigation.

## Next step

1. Treat option-state regression verification as the blocking gate; do not resume source expansion until red+green browser checks pass on the repaired bundles.
2. Have the user device-check the repaired preview, especially a deliberately wrong new Physiology/Anatomy question and the Wrong Questions flow.
3. Only after that, resume missing Anatomy source integration; then integrate real Biochemistry Ch27/28 when supplied.
4. Keep explanation/image fine-tuning on their separate governed pipelines.
5. Merge source expansion only after the relevant verification gate; keep production unpromoted unless explicitly requested.

Canonical Marrow integration procedure: `docs/MARROW_BANK_INTEGRATION.md`.
