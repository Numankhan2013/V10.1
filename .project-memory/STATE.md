# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`; `main` is the authoritative unified V11/Marrow line.
- Anatomy topic-index v2 merged through PR #29 at `424d7b2`.
- Biochemistry topic-index v2 merged through PR #30 at `3b0d9dc`.
- Physiology topic-index v2 is on `feature/marrow-physiology-topic-index-v2`; full feature CI/preview is the merge gate.
- Resolve live HEAD from Git; never hardcode a self-staling HEAD.
- Accepted baseline: **V11.6 Content Quality** at `125d68b`.
- Accepted product commit: `125d68b`.
- Production promotion remains explicit and guarded.

## Current Marrow bank

Shared architecture: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`; Practice/CBT/Review/FSRS/sync/modules/analytics remain shared.

Current supplied ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 source topics**.

Raw imported Marrow source is authoritative and immutable. Taxonomy changes learner navigation metadata only; source IDs/titles, question linkage, history, provenance and FSRS identity stay stable.

## Shared topic-index contract

Revised subjects use `data/marrow/topic_index_taxonomy.json` with `catalogVersion: 2`, full `plannedIndex`, current imported `topics`, `plannedSlots`, and `displayNumbering: visible-contiguous`.

- Store the full intended syllabus even when source topics are not imported.
- Render only imported source topics; never show blank/disabled placeholders or fake chapters.
- Hide a planned major index when it has zero imported topics.
- Combined/split source chapters remain source-faithful; `plannedSlots` maps them to finer learner slots without duplicating questions.
- Learner numbers follow configured arranged order; backend source chapter IDs are never renumbered.
- Future imports use `plannedIndex` / `plannedSlots`, not source chapter number inference.

## Anatomy topic index v2

Order: **Embryology → Histology → Neuroanatomy → Head, neck, and face → Upper limb → Thorax → Abdomen and pelvis → Lower limb → Back → General anatomy**.

- Intended: **71 slots**; current: **48 source topics / 819 questions**.
- Current placement: Ch 1–10 Embryology; 11–16 Histology; 17–27 Neuroanatomy; 28–34 Head/neck/face; 35–40 Upper limb; 41–46 Thorax; 47–48 Abdomen/pelvis.
- Lower limb, Back, General anatomy are metadata-only and hidden at the current boundary.
- Learner numbering is **1–48 contiguous**.
- Full feature CI `34443190210` passed; merged PR #29. New arrangement awaits device verification.

## Biochemistry topic index v2

Order: **Carbohydrates → Amino acids and proteins → Lipids → Enzymes and phenylketonuria → Clinical biochemistry and nutrition → Genetics**.

- Intended: **32 slots**; current: **26 source topics / 543 questions**.
- Current placement: Ch 1–6 Carbohydrates; 7–11 amino acids/proteins; 12–16 Lipids; 17–19 enzymes/phenylketonuria; 20–23 clinical/nutrition; 24–26 Genetics.
- Ch 1, 4, 20 and 24 map to multiple planned slots while remaining single source topics.
- Learner numbering is **1–26 contiguous**.
- Full feature CI `34444405972` passed; merged PR #30. New arrangement awaits device verification.
- User reports digitized Biochemistry Ch 27/28 JSONs may also exist on GitHub; do not integrate them during Physiology taxonomy work. Exact branch/path still needs later verification.

## Physiology topic index v2 — 2026-09-10

Authoritative order: **General physiology → Nerve and muscle physiology → Gastrointestinal system → Cardiovascular system → Respiratory system → Renal physiology → Endocrine physiology → Reproductive physiology → Central nervous system → Integrated physiology**.

- Intended: **42 slots**; current source stays **33 topics / 753 questions**.
- Current learner-order placement: General Ch 1–5; Nerve/muscle Ch 6–9; GI Ch 31–33; Cardiovascular Ch 26–30; Respiratory Ch 19–25; CNS Ch 10–18.
- Arranged source-ID sequence: `1–9, 31–33, 26–30, 19–25, 10–18`; learner display must be **1–33 contiguous**.
- Renal, Endocrine, Reproductive and Integrated physiology have no topics in the current Ch 1–33 import, so they remain metadata-only and invisible.
- Source split/combo mappings: Muscle I/II → Muscle physiology; Motor 1/2 → Motor physiology; Ch16 → Basal ganglia + Cerebellum; Ch17 → Hypothalamus + Limbic system; Vascular I/II → one vascular slot; Ch22/23 → supplied combined gas-transport/lung-volume slot; Ch31 → GI secretion + hormones.
- `tools/apply_marrow_topic_numbering_v1.py` provides Marrow-only arranged learner serials after the whole-app Topics renderer; the existing content-hygiene transformation invokes it, avoiding a second workflow/UI owner.
- `tools/test_marrow_topic_taxonomy.py` validates all 10 indexes, 42 planned slots, 33 source IDs/titles, slot mapping and arranged ID order.
- The deep existing browser suite is preserved byte-for-byte as `tools/verify_marrow_bank_browser_core.py`; its wrapper updates only Physiology taxonomy/1–33 assertions.
- Full feature CI/browser/APK/preview verification is pending before merge.

## Explanation and image phases

- Gold explanation grammar: Key Takeaway → structured detail/native tables → three concise wrong-option rationales.
- Approved reference = 142 Anatomy+Physiology + 20 Biochemistry sample = **162 questions**.
- Current enhanced inventory: **184 enhanced / 1,931 pending**; raw source remains immutable.
- Image Batch 01: **28 approved assets / 34 bindings** across all three subjects; production not promoted.
- Preserve exact medical/photo pixels; reconstruction only for faithful educational diagrams/annotation layers.

## Verification / release status

- Anatomy and Biochemistry taxonomy v2 are build-verified and merged; both await device verification of the new arrangements.
- Physiology v2 is not yet build-verified or device-verified; full feature CI is its gate.
- CI success alone does not change the accepted baseline or promote production.

## Known problems / cautions

- Remaining Marrow explanations still need approved polish.
- Do not rewrite raw JSONL/sharded source for UI taxonomy.
- Do not alter approved Topics visuals, FSRS dock, PDF renderers, Practice/CBT/Review, sync, modules, persistence or navigation during taxonomy work.
- Never show unavailable planned topics or empty planned indexes.

## Next step

1. Run/inspect full Physiology v2 feature CI and browser 10-index/1–33 contract; fix any regression before merge.
2. After green CI, merge Physiology v2 and record its exact Cloudflare preview alias/immutable URL; keep production unpromoted.
3. Later locate/verify reported Biochemistry Ch 27/28 outputs and integrate them against the planned taxonomy.
4. Continue explanation/image rollouts separately.

Canonical Marrow integration procedure: `docs/MARROW_BANK_INTEGRATION.md`.
