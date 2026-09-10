# STATE.md — Current Project State and Handoff

> Concise operational handoff. History belongs in `SESSION_LOG.md`; durable
> reasoning in `DECISIONS.md`; future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`.
- `main` is the authoritative unified V11/Marrow product line.
- Anatomy topic-index v2 merged through PR #29 at `424d7b2`.
- Biochemistry topic-index v2 is on `feature/marrow-biochemistry-topic-index-v2` at `fe8067e`, pending full feature CI/PR.
- Resolve live branch/HEAD from Git; never hardcode a self-staling HEAD value.
- Accepted baseline: **V11.6 Content Quality** at `125d68b`, run `34050921180`.
- Accepted product commit: `125d68b`.
- Production promotion remains explicit and guarded.

## Current Marrow bank

Shared architecture: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` →
`BANKS_BY_SUBJECT`; Practice/CBT/Review/FSRS/sync/modules/analytics remain shared.

Current supplied ED8 scope:
- Anatomy: **819 questions / 48 topics**.
- Biochemistry: **543 / 26**.
- Physiology: **753 / 33**.
- Total: **2,115 globally unique questions / 107 topics**.

Raw imported Marrow source is authoritative and immutable. Expanded bundles are
manifest/hash validated. The original 62 Anatomy + 80 Physiology enhanced
questions remain regression references; resolved Anatomy reconstructions retain
provenance.

## Anatomy topic index v2 — 2026-09-10

User-authoritative major-index order:
**Embryology → Histology → Neuroanatomy → Head, neck, and face → Upper limb →
Thorax → Abdomen and pelvis → Lower limb → Back → General anatomy**.

Implementation contract:
- `data/marrow/topic_index_taxonomy.json` contains a **71-topic intended Anatomy
  catalog** in `plannedIndex` plus the **48 currently imported source topics**.
- Current source placement: Ch 1–10 Embryology; 11–16 Histology; 17–27
  Neuroanatomy; 28–34 Head, neck, and face; 35–40 Upper limb; 41–46 Thorax;
  47–48 Abdomen and pelvis.
- Source IDs, exact source titles, question linkage, history and FSRS identity are
  never rewritten for presentation ordering.
- Combined current source chapters stay combined; `plannedSlots` records their
  relationship to finer intended syllabus slots.
- Missing planned topics never render as rows/placeholders/gaps. Entire empty
  planned indexes are hidden. Lower limb, Back and General anatomy are currently
  metadata-only because the current Anatomy import stops at Ch 48.
- Learner numbering is `visible-contiguous`; the current arranged view shows
  1–48 while source IDs remain backend truth.
- Updated: `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`,
  `tools/test_marrow_topic_taxonomy.py`, and
  `tools/verify_marrow_bank_browser.py`.
- Physiology taxonomy remains unchanged; Biochemistry now has its own v2 contract below.
- Feature CI run `34443190210` passed end-to-end, including the explicit taxonomy
  contract, real-browser Anatomy grouping/1–48 numbering, APK packaging and
  packaged-product checks. Feature preview deployment passed; production was skipped.
- Merged to `main` through PR #29 at `424d7b2`; device verification of the new
  Anatomy arrangement is still pending.

## Biochemistry topic index v2 — 2026-09-10

User-authoritative major-index order: **Carbohydrates → Amino acids and proteins →
Lipids → Enzymes and phenylketonuria → Clinical biochemistry and nutrition → Genetics**.

- `plannedIndex` stores all **32 supplied learner slots** while current source remains **26 topics / 543 questions**.
- Current placement: Ch 1–6 Carbohydrates; 7–11 Amino acids/proteins; 12–16 Lipids; 17–19 Enzymes/phenylketonuria; 20–23 Clinical biochemistry/nutrition; 24–26 Genetics.
- Combined source chapters stay combined; `plannedSlots` maps Ch 1, 4, 20 and 24 to multiple finer learner slots.
- Missing future topics never render as placeholders; learner numbering is visible-contiguous 1–26; source IDs/titles/question linkage/FSRS remain untouched.
- Static taxonomy + project-memory validation passed before commit; full Android/PWA/browser feature CI is the remaining gate before merge.
- Physiology taxonomy is still pending the user's revised arrangement.

## User/device verification

- On 2026-09-08 the user physically verified the expanded Marrow PWA and approved
  the recovered Topics journey/fixed Continue Learning tray and FSRS controls.
- The visual journey remains approved; only the older Anatomy grouping taxonomy
  is superseded by the 2026-09-10 Anatomy v2 contract above.
- Build-verified ≠ device-verified ≠ accepted baseline.

## Explanation-quality phase

- Existing 142 Anatomy+Physiology enhanced questions define the original gold
  grammar: Key Takeaway → structured detail/native tables → three concise
  wrong-option rationales.
- The user approved the 20-question Biochemistry gold sample on 2026-09-09;
  approved reference is therefore **162 questions**.
- Biochemistry Chapter 1 is fully enhanced; inventory is **184 enhanced / 1,931
  pending**.
- Keep raw source immutable and preserve explicit ambiguity instead of inventing
  missing lab values, lists, figures, labels or facts.

## Image phase

- User-approved image pilot and Batch 01 are merged; production was not promoted.
- Batch 01: **28 approved assets / 34 released bindings** across Anatomy,
  Biochemistry and Physiology.
- Full Android/PWA run `34334231275` passed at product commit `44990c0`.
- Preserve exact medical/photo pixels; reconstruction is restricted to faithful
  educational diagrams and annotation layers.

## Verification / release status

- Expanded Marrow integration and Anatomy topic-index v2 are build-verified.
- Anatomy v2 is merged to `main` but not yet device-verified as a new arrangement.
- Biochemistry v2 has passed static taxonomy/memory validation; full feature build/browser verification is pending.
- Main/production release requires explicit guarded promotion; CI success alone
  must never promote production.
- Accepted rollback checkpoint remains V11.6 `125d68b` until explicit user
  promotion.

## Known problems / cautions

- Remaining Marrow explanations still need approved polish.
- Do not rewrite raw JSONL/sharded source for UI taxonomy.
- Do not alter approved Topics visuals, FSRS dock, PDF renderers, Practice/CBT/
  Review, sync, modules, persistence or navigation during taxonomy work.
- Future Anatomy and Biochemistry imports must use `plannedIndex` / `plannedSlots`, not infer learner placement from source chapter number alone.
- Never show unavailable planned topics or empty sections to the learner.

## Next step

1. Complete Biochemistry v2 full feature CI/browser verification and merge only after green.
2. Apply the user's revised Physiology taxonomy when supplied.
3. Continue image and explanation rollout separately from taxonomy changes.

Canonical Marrow procedure: `docs/MARROW_BANK_INTEGRATION.md`.
