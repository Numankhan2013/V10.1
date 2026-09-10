# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`; `main` is the authoritative unified V11/Marrow line.
- Anatomy topic-index v2 merged through PR #29 at `424d7b2`.
- Biochemistry topic-index v2 merged through PR #30 at `3b0d9dc`.
- Physiology topic-index v2 is on `feature/marrow-physiology-topic-index-v2`; full feature CI/preview is the merge gate.
- Resolve live HEAD from Git; never hardcode a self-staling commit.
- Accepted rollback baseline remains **V11.6 Content Quality** `125d68b` until explicit production promotion.
- Production promotion is explicit and guarded; ordinary feature/main CI must not promote it.

## Current Marrow bank

Shared architecture: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`; Practice/CBT/Review/FSRS/sync/modules/analytics remain shared.

Current supplied ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 source topics**.

Raw imported Marrow source is authoritative and immutable. Topic-index work changes learner navigation metadata only; source IDs/titles, question linkage, history, provenance and FSRS identity stay stable.

## Topic-index contract

All revised subjects use `data/marrow/topic_index_taxonomy.json` with `catalogVersion: 2`, a complete `plannedIndex`, current imported `topics`, `plannedSlots`, and `displayNumbering: visible-contiguous`.

Rules:
- Store the full intended syllabus even when source topics are not imported yet.
- Render only currently imported source topics; never show blank/disabled placeholders or fake chapters.
- Hide an entire planned index when it currently has zero imported topics.
- Combined/split source chapters stay source-faithful; `plannedSlots` records their relationship to finer learner slots without duplicating questions.
- Learner numbers follow configured arranged order; backend source chapter IDs are never renumbered.
- Future imports must use `plannedIndex` / `plannedSlots`, not infer placement from source chapter numbers.

## Anatomy topic index v2

Order: **Embryology → Histology → Neuroanatomy → Head, neck, and face → Upper limb → Thorax → Abdomen and pelvis → Lower limb → Back → General anatomy**.

- Intended catalog: **71 slots**; current: **48 source topics / 819 questions**.
- Current placement: Ch 1–10 Embryology; 11–16 Histology; 17–27 Neuroanatomy; 28–34 Head/neck/face; 35–40 Upper limb; 41–46 Thorax; 47–48 Abdomen/pelvis.
- Lower limb, Back, General anatomy currently metadata-only and hidden.
- Current learner numbering: **1–48 contiguous**.
- Full feature CI `34443190210` passed; merged PR #29. New arrangement still awaits device verification.

## Biochemistry topic index v2

Order: **Carbohydrates → Amino acids and proteins → Lipids → Enzymes and phenylketonuria → Clinical biochemistry and nutrition → Genetics**.

- Intended catalog: **32 slots**; current: **26 source topics / 543 questions**.
- Current placement: Ch 1–6 Carbohydrates; 7–11 amino acids/proteins; 12–16 Lipids; 17–19 enzymes/phenylketonuria; 20–23 clinical/nutrition; 24–26 Genetics.
- Ch 1, 4, 20 and 24 map to multiple finer planned slots; current source records remain combined.
- Current learner numbering: **1–26 contiguous**.
- Full feature CI `34444405972` passed; merged PR #30. New arrangement still awaits device verification.
- User reports additional digitized Biochemistry Ch 27/28 JSONs may be committed somewhere in GitHub; do not integrate them during Physiology taxonomy work. Their exact branch/path still needs later verification.

## Physiology topic index v2 — 2026-09-10

User-authoritative order: **General physiology → Nerve and muscle physiology → Gastrointestinal system → Cardiovascular system → Respiratory system → Renal physiology → Endocrine physiology → Reproductive physiology → Central nervous system → Integrated physiology**.

- Intended catalog: **42 slots**; current source remains **33 topics / 753 questions**.
- Current populated placement in learner order:
  - General physiology: source Ch 1–5
  - Nerve and muscle physiology: Ch 6–9
  - Gastrointestinal system: Ch 31–33
  - Cardiovascular system: Ch 26–30
  - Respiratory system: Ch 19–25
  - Central nervous system: Ch 10–18
- Current arranged source-ID sequence: `1–9, 31–33, 26–30, 19–25, 10–18`; learner display must be **1–33 contiguous**.
- Renal, Endocrine, Reproductive and Integrated physiology are currently metadata-only because no matching topics exist in the imported Ch 1–33 source bundle; they must not render empty.
- Source split/combo mappings: Muscle I/II → one Muscle slot; Motor 1/2 → one Motor slot; Ch16 → Basal ganglia + Cerebellum; Ch17 → Hypothalamus + Limbic; Vascular I/II → one vascular slot; Ch22/23 → supplied combined gas-transport/lung-volume slot; Ch31 → GI secretion + hormones.
- `tools/apply_marrow_topic_numbering_v1.py` adds Marrow-only arranged learner serials after the whole-app Topics renderer; it is invoked by the existing content-hygiene transformation owner, so no second workflow/UI owner is introduced.
- `tools/test_marrow_topic_taxonomy.py` now validates the exact 10 indexes, 42 planned slots, all 33 immutable source IDs/titles, slot mapping, hidden-empty behavior, and arranged ID order.
- The existing deep browser suite is preserved byte-for-byte as `tools/verify_marrow_bank_browser_core.py`; the wrapper updates only current Physiology taxonomy/1–33 assertions.
- Full feature CI, browser verification, APK packaging and preview deployment are pending before merge.

## Explanation-quality phase

- Existing 142 Anatomy+Physiology enhanced questions define the original gold grammar: Key Takeaway → structured detail/native tables → three concise wrong-option rationales.
- User approved the 20-question Biochemistry gold sample on 2026-09-09; approved reference = **162 questions**.
- Biochemistry Chapter 1 is fully enhanced; inventory currently **184 enhanced / 1,931 pending**.
- Keep raw source immutable and preserve explicit ambiguity instead of inventing missing values, labels, figures or facts.

## Image phase

- User-approved image pilot + Batch 01 merged; production not promoted.
- Batch 01: **28 approved assets / 34 released bindings** across all three subjects.
- Full Android/PWA run `34334231275` passed at product commit `44990c0`.
- Preserve exact medical/photo pixels; reconstruction is restricted to faithful educational diagrams/annotation layers.

## Verification / cautions

- Build-verified ≠ device-verified ≠ accepted production baseline.
- Do not rewrite raw JSONL/sharded source for UI taxonomy.
- Do not alter approved Topics visuals, FSRS dock, PDF renderers, Practice/CBT/Review, sync, modules, persistence or navigation during taxonomy work.
- Never show unavailable planned topics or empty planned indexes.

## Next step

1. Run/inspect full Physiology v2 feature CI and real-browser 10-index/1–33 contract; fix any regression before merge.
2. After green CI, merge Physiology v2 and record the immutable feature preview URL/alias; keep production unpromoted.
3. Later locate/verify the reported Biochemistry Ch 27/28 digitization outputs and integrate them against the planned taxonomy.
4. Continue explanation/image rollouts separately from taxonomy changes.

Canonical Marrow integration procedure: `docs/MARROW_BANK_INTEGRATION.md`.
