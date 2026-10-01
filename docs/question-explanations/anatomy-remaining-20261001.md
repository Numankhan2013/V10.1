# Anatomy remaining explanation refinement — 2026-10-01

**Owner:** Anatomy remaining worktree `work/luna-anatomy-remaining`, based on `d4abce86068b4221e61e541c34dd29258de61cca`.

**Source:** immutable Anatomy ED8 source bundle SHA-256 `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`. The complete source and assignment were supplied read-only in `/tmp/explanation-remaining-20261001/`. The earlier source audit `.project-memory/source-audits/anatomy-ch09-q001-q018.json` is retained unchanged.

## Checkpoint 1

Authored 129 of the 914 pending actionable Anatomy IDs in fifteen new augmentation files (initial checkpoint; subsequent checkpoints are appended below):

- Ch9 Q15–18 (`explanation_anatomy_ch09_q015_q018_v1.json`)
- Ch10 Q19 (`explanation_anatomy_ch10_q019_q019_v1.json`)
- Ch11 Q11–24 (`explanation_anatomy_ch11_q011_q024_v1.json`)
- Ch11 Q25–26 (`explanation_anatomy_ch11_q025_q026_v1.json`)
- Ch12 Q1–14 (`explanation_anatomy_ch12_q001_q014_v1.json`)
- Ch12 Q15 (`explanation_anatomy_ch12_q015_q015_v1.json`)
- Ch13 Q1–12 (`explanation_anatomy_ch13_q001_q012_v1.json`)
- Ch14 Q1–11 (`explanation_anatomy_ch14_q001_q011_v1.json`)
- Ch15 Q1–15 excluding gated Q14 (`explanation_anatomy_ch15_q001_q015_v1.json`)
- Ch15 Q16–22 (`explanation_anatomy_ch15_q016_q022_v1.json`)
- Ch16 Q1–14 (`explanation_anatomy_ch16_q001_q014_v1.json`)
- Ch16 Q15–17 (`explanation_anatomy_ch16_q015_q017_v1.json`)
- Ch17 Q1–14 (`explanation_anatomy_ch17_q001_q014_v1.json`)
- Ch17 Q15–21 (`explanation_anatomy_ch17_q015_q021_v1.json`)
- Ch18 Q1–11 (`explanation_anatomy_ch18_q001_q011_v1.json`)

Each file is bounded to one chapter and 14 or fewer questions, uses the exact `approved-rollout` scope and canonical base SHA, and adds new IDs only. Every four-option SBA has exactly the three source-key-matching distractor rationales and one to four case-sensitive emphasis anchors. Display text retains source details; native table and figure data remains in the untouched source record. Ch12–14 OCR cleanup is annotated as resolved reconstruction with the raw fragment, clean reconstruction, PDF pages and question-specific review note. Ch9 Ch12 work does not change the answer key or completeness ledger.

## Validation and status

The shared batch validator passed: `python3 /root/V10.1/tools/validate_marrow_explanation_batch.py --root /root/luna_anatomy_remaining --base-sha d4abce86068b4221e61e541c34dd29258de61cca` → `MARROW_WORKER_BATCHES_OK files=15 questions=129 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`.

This checkpoint is authoring/source-review validation only. It is not a combined preview, browser, CI, APK or release certification. The original assignment has since been rebalanced: this worktree owns the remaining actionable Anatomy IDs through Chapter 50 (662 IDs total in that range); Chapters 51–63 (252 actionable IDs) are assigned to the freed Biochemistry worker. The 13 completeness-gated IDs remain untouched.


## Checkpoint 2

Added 24 more actionable IDs across Chapters 19–20 in three bounded files:

- Ch19 Q1–14 (`explanation_anatomy_ch19_q001_q014_v1.json`)
- Ch19 Q15–17 (`explanation_anatomy_ch19_q015_q017_v1.json`)
- Ch20 Q1–7 (`explanation_anatomy_ch20_q001_q007_v1.json`)

The Chapter 19 Q17 classification ambiguity and Chapter 20 Q1 collateral/calcarine sulcus ambiguity remain explicitly flagged for subject review, with source wording and evidence preserved. Chapter 20 Q4/Q7 figure/table interpretation was checked against the source PDF. Validator passed: `MARROW_WORKER_BATCHES_OK files=18 questions=153 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Current authored total is 153 of the 662 actionable IDs owned through Chapter 50; 509 remain in my range. Chapters 51–63 are handed off under the balancing assignment to another worker, so they are outside this author's remaining count.

## Checkpoint 3

Added 22 IDs in three bounded files:

- Ch21 Q1–14 (`explanation_anatomy_ch21_q001_q014_v1.json`)
- Ch21 Q15–16 (`explanation_anatomy_ch21_q015_q016_v1.json`)
- Ch22 Q1–6 (`explanation_anatomy_ch22_q001_q006_v1.json`)

The rationales preserve distinctions among association, projection, and commissural fibers, internal capsule subdivisions, and basal ganglia pathway/nomenclature details. The source explanation's classification of arcuate fasciculus and fornix is retained as written. Validator passed: `MARROW_WORKER_BATCHES_OK files=21 questions=175 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored: 175/662 in my owned range; 487 remain through Chapter 50.

## Checkpoint 4

Added 26 IDs in three bounded files: Chapter 23 Q1–12, Chapter 24 Q1–7, and Chapter 24 Q8–14. Chapter 24 OCR-corrupted sections were reconstructed from the source pages with source-specific tracts, levels, syndrome signs and cross-sections retained; intact source explanations were copied. Figure and native table metadata remain in the unmodified source records. Validator passed: `MARROW_WORKER_BATCHES_OK files=24 questions=201 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`.

Also completed the source-level review of two flagged items. Ch19 Q17 keeps key C but now distinguishes the conventional brain CVO list from broader pituitary classification and corrects the erroneous implication that adenohypophysis has a conventional BBB; primary histology and NCBI evidence are recorded. Ch20 Q1 keeps key B but records that the unqualified calcarine option also includes a complete anterior part; editorial qualification is recommended. Neither source key nor gate changed. Total authored is 201/662 through Chapter 50; 461 remain in my range.

## Checkpoint 5

Added Chapter 25 Q1–14 in `explanation_anatomy_ch25_q001_q014_v1.json`. The chapter distinguishes cerebellar lobes, deep nuclei, cortical cell types, afferent/efferent pathways and vascular territory; OCR-damaged sections carry question-specific readable reconstructions and evidence notes. The source figure/table metadata remains intact. Validator passed: `MARROW_WORKER_BATCHES_OK files=25 questions=215 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. This checkpoint also normalizes reconstruction status/provenance fields to the rollout validator's accepted vocabulary. Total authored is 215/662 through Chapter 50; 447 remain.

## Checkpoint 6

Added Chapter 26 Q1–20 in two bounded files (14 and 6 IDs). The vascular explanations preserve carotid segments and branch origins, cerebral arterial territories, circle-of-Willis composition, stroke localizations, and superficial/deep cerebral venous drainage. Corrupted OCR/figure text was reconstructed with source fragments and evidence pages recorded; source diagrams and structured metadata remain unchanged. Validator passed: `MARROW_WORKER_BATCHES_OK files=27 questions=235 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored is 235/662 through Chapter 50; 427 remain.

## Checkpoint 7

Added Chapter 27 Q1–15 in two bounded files (Q1–14 and Q15). Explanations retain spinal-level landmarks, rami and arterial supply, pathway crossings, Brown–Séquard findings, and conus-versus-cauda equina distinctions. Validator passed: `MARROW_WORKER_BATCHES_OK files=29 questions=250 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored is 250/662 through Chapter 50; 412 remain.

## Checkpoint 8

Added 26 IDs in three bounded Chapter 28 files: Q1–14, Q15–22 and Q24–27. The source-gated Q23 match item remains intentionally untouched because its numbered muscle list/action list is missing from the rendered question page. Other explanations preserve skull joints, sutures, foramina, cranial nerves, orbital/skull-base anatomy, scalp layers and facial innervation. Validator passed: `MARROW_WORKER_BATCHES_OK files=32 questions=276 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored is 276/662 through Chapter 50; 386 remain.

## Checkpoint 9

Added Chapter 29 Q1–15 in two files. Chapter 29 Q2 received visual source review (PDF p. 508): the printed key selects suprascapular nerve, and the source explicitly calls it a lower posterior-triangle content while noting it is not part of the roof. The stem's “neither roof nor content” wording conflicts with that explanation; key C is retained and the augmentation states the nerve is a content rather than teaching it is absent. Remaining explanations retain triangle boundaries/contents, fascial layers, ansa cervicalis, spinal accessory and cervical sympathetic relationships. Validator passed: `MARROW_WORKER_BATCHES_OK files=34 questions=291 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored is 291/662 through Chapter 50; 371 remain.

## Checkpoint 10

Added Chapter 30 Q1–24 in two files. The explanations cover mastication and TMJ mechanics, trigeminal branches, extraocular/facial muscle innervation, carotid branches and landmarks, pterygoid canal, venous pathways, facial danger zone and cervical node levels. Rationales distinguish neighboring nerve/artery routes and compartment anatomy. Validator passed: `MARROW_WORKER_BATCHES_OK files=36 questions=315 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored is 315/662 through Chapter 50; 347 remain.

## Checkpoint 11

Added 23 Chapter 31 IDs in two files, skipping gated Q5 (the matching question with missing source lists). These records cover parotid/otic/pterygopalatine and submandibular anatomy, thyroid levels/arteries/veins, recurrent laryngeal risk, parathyroid supply and thyroid fixation. Q24's tubarial-gland terminology is qualified with current anatomical evidence while preserving the keyed torus tubarius location. Validator passed: `MARROW_WORKER_BATCHES_OK files=38 questions=338 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored is 338/662 through Chapter 50; 324 remain.

## Checkpoint 12

Added Chapter 32 Q1–12 and Chapter 33 Q1–9 (21 IDs). This covers tongue papillae/muscles, sensory and taste routes, tongue lymph drainage, palate supply, pharyngeal regions and constrictors, and clinical diverticula. Ch32 Q11 distinguishes V2 palatine peripheral carriage from CN VII greater-petrosal central taste afferents while preserving the keyed trigeminal answer. Validator passed: `MARROW_WORKER_BATCHES_OK files=40 questions=359 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`. Total authored is 359/662 through Chapter 50; 303 remain.
