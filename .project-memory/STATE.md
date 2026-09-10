# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`; `main` is the authoritative unified V11/Marrow line.
- Anatomy topic-index v2 merged through PR #29 at `424d7b2`.
- Biochemistry topic-index v2 merged through PR #30 at `3b0d9dc`.
- Physiology topic-index v2 merged through PR #31 at `fcf0476`.
- Current source-ingest work branch: `feature/marrow-automation-ingest-physio-biochem`.
- Resolve live HEAD from Git; never hardcode a self-staling HEAD.
- Accepted baseline: **V11.6 Content Quality** at `125d68b`.
- Accepted product commit: `125d68b`
- Production promotion remains explicit and guarded.

## Current Marrow bank

Shared architecture: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`; Practice/CBT/Review/FSRS/sync/modules/analytics remain shared.

Merged `main` source scope before the current ingest:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 source topics**.

Current feature-ingest target after adding confirmed Physiology Ch34–43:
- Anatomy: **819 / 48** unchanged.
- Biochemistry: **543 / 26** unchanged until Ch27/28 source is located.
- Physiology: **1,014 / 43** (**+261 questions / +10 source topics**).
- Feature total: **2,376 questions / 117 source topics**.

Raw imported Marrow source is authoritative and immutable. Source-ingest adapters may normalize storage-field names only; stems/options/answers/explanation text/source provenance are not rewritten merely for integration.

## Automation handoff discovery — 2026-09-10

The canonical committed automation handoff is on `feature/marrow-bank-pilot` under `data/marrow/automation_ingest/`.

Confirmed Physiology JSONL source files Ch34–43:
- Ch34 GFR / renal blood flow / renal clearance — 35 Q.
- Ch35 renal tubular functions / concentration / dilution — 32 Q.
- Ch36 acid-base balance / renal hormones / micturition reflex — 25 Q.
- Ch37 pituitary and thyroid — 24 Q.
- Ch38 pancreas — 25 Q.
- Ch39 adrenals — 21 Q.
- Ch40 calcium homeostasis — 25 Q.
- Ch41 male reproductive physiology — 28 Q.
- Ch42 female reproductive physiology — 30 Q.
- Ch43 exercise physiology — 16 Q.
- Total new Physiology questions: **261**.

Biochemistry Ch27/28 were reported as automation-produced, but no matching committed payload is reachable as of this handoff: checked the intended automation-ingest folder, every current branch tip, and full reachable history across all branches. Do not fabricate or reconstruct these two chapters from taxonomy labels; locate their actual source artifact before integration.

## Shared topic-index contract

Revised subjects use `data/marrow/topic_index_taxonomy.json` with `catalogVersion: 2`, full `plannedIndex`, current imported `topics`, `plannedSlots`, and `displayNumbering: visible-contiguous`.

- Store the full intended syllabus even when source topics are not imported.
- Render only imported source topics; never show blank/disabled placeholders or fake chapters.
- Hide a planned major index when it has zero imported topics.
- Combined/split source chapters remain source-faithful; `plannedSlots` maps them to finer learner slots without duplicating questions.
- Learner numbers follow configured arranged order; backend source chapter IDs are never renumbered.

## Anatomy topic index v2

Order: **Embryology → Histology → Neuroanatomy → Head, neck, and face → Upper limb → Thorax → Abdomen and pelvis → Lower limb → Back → General anatomy**.
- Intended: **71 slots**; current: **48 source topics / 819 questions**.
- Learner numbering is **1–48 contiguous**.
- Full feature CI `34443190210` passed; merged PR #29. New arrangement awaits device verification.

## Biochemistry topic index v2

Order: **Carbohydrates → Amino acids and proteins → Lipids → Enzymes and phenylketonuria → Clinical biochemistry and nutrition → Genetics**.
- Intended: **32 slots**; current: **26 source topics / 543 questions**.
- Current placement: Ch1–6 Carbohydrates; 7–11 amino acids/proteins; 12–16 Lipids; 17–19 enzymes/phenylketonuria; 20–23 clinical/nutrition; 24–26 Genetics.
- Learner numbering is **1–26 contiguous**.
- Full feature CI `34444405972` passed; merged PR #30.
- Planned Genetics slots for Regulation of gene expression and Molecular genetics/recombinant DNA/genomic technology remain available for Ch27/28 when their real source payload is found.

## Physiology topic index v2 + Ch34–43 ingest

Authoritative order: **General physiology → Nerve and muscle physiology → Gastrointestinal system → Cardiovascular system → Respiratory system → Renal physiology → Endocrine physiology → Reproductive physiology → Central nervous system → Integrated physiology**.

- Intended syllabus remains **42 planned slots**.
- After Ch34–43 ingest, all 10 major indexes have imported source coverage and the source bank is **43 topics / 1,014 questions**.
- Learner-order source IDs become `1–9, 31–33, 26–30, 19–25, 34–36, 37–40, 41–42, 10–18, 43`; learner display is **1–43 contiguous**.
- Ch34 → renal slot 1; Ch35 → renal slot 2; Ch36 → renal slots 2+3; Ch37–40 → endocrine slots 1–4; Ch41–42 → reproductive slots 1–2; Ch43 → integrated slot 1.
- `tools/integrate_physio_automation_ch034_043.py` performs deterministic JSONL→Marrow runtime adaptation and emits the hash-verified `physiology_ch001_043` shard bundle without committing raw automation JSONL into the learner app branch.
- New source explanations remain unenhanced/pending; no explanation-polish pass is part of this ingest.

## Explanation and image phases

- Gold explanation grammar remains Key Takeaway → structured detail/native tables → three concise wrong-option rationales.
- Current approved/enhanced inventory remains **184** questions.
- With the Physiology source expansion, explanation inventory becomes **184 enhanced / 2,192 pending**; the 261 new questions enter as pending without content rewriting.
- Image Batch 01 remains **28 approved assets / 34 bindings**; production not promoted.

## Verification / release status

- Anatomy, Biochemistry, and Physiology taxonomy v2 are build-verified and merged to `main`.
- User already approved the Physiology v2 taxonomy preview; the new Ch34–43 source ingest is not yet device-verified.
- `device-verified` status is intentionally withheld until the user checks the resulting build on-device.
- Source-data/taxonomy/inventory prechecks for the Ch34–43 transformation reached **1,014/43 Physiology, 2,376/117 total, 184 enhanced / 2,192 pending** before the handoff-linter wording fix.
- CI success alone does not change the accepted baseline or promote production.

## Known problems / cautions

- Remaining Marrow explanations still need later approved polish; do not improve them during source integration.
- Do not expose raw JSONL/schema objects in learner-facing question/explanation views.
- Do not rewrite raw source for UI taxonomy.
- Do not alter approved Topics visuals, FSRS dock, PDF renderers, Practice/CBT/Review, sync, modules, persistence or navigation during source ingestion.

## Next step

1. Complete/commit the Physiology Ch34–43 source bundle, taxonomy mapping, inventory update and all count-dependent regression updates.
2. Run full feature CI/browser/APK/PWA verification, including a learner-view raw-JSON leakage check, before merge.
3. Merge the verified Physiology source ingest; keep production unpromoted unless explicitly requested.
4. Locate the actual Biochemistry Ch27/28 source artifact before integrating those planned Genetics topics.
5. Anatomy automation-ingest expansion is a separate later task.

Canonical Marrow integration procedure: `docs/MARROW_BANK_INTEGRATION.md`.
