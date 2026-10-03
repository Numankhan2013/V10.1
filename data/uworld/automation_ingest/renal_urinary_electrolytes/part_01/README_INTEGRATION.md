# UWorld 2024 — Renal, Urinary Systems & Electrolytes — Part 1

Canonical ingestion package for NK QBank. This is **Part 1 of 2** of the source PDF split.

## Source / scope
- Source: `UW_2024_Renal,_Urinary_Systems_&_Electrolytes_6_blocks_OCR-1-720.pdf`
- Pages in this part: **1–720**
- UWorld blocks present in this part: **3 blocks × 40 logical item slots = 120 slots**
- Actual source questions present: **119**
- Complete source questions: **118**
- Part-boundary continuation: **1** (`uworld__RENAL_P1_B03_Q040`, UWorld Question ID `11806`)
- Genuine source-missing slot: **1** (`uworld__RENAL_P1_B02_Q027`)

## Integration rules
1. Treat `uworld_renal_urinary_electrolytes_part_01.jsonl` as the canonical Part-1 corpus. The per-block JSONLs are identical slices for parallel work.
2. **Do not import `uworld__RENAL_P1_B02_Q027` as a user-facing question.** The rendered Part-1 PDF itself jumps from Block 2 Item 26 (QID 8249) to Item 28 (QID 981). The placeholder exists only to preserve source numbering and prevent an off-by-one remap.
3. **Do not finalize or duplicate `uworld__RENAL_P1_B03_Q040` / QID 11806 yet.** Page 720 contains its question stem, options, and CT-source visual only. Correct answer, statistics, explanation, educational objective, and subsequent source pages continue in Part 2. When Part 2 is processed, merge continuation material into this exact canonical ID.
4. `provenance.all_pages`, `question_pages`, `answer_key_pages`, `explanation_pages`, and `visual_source_pages` are source-of-truth pointers for later source verification and image extraction.
5. Visuals are deliberately not embedded in JSONL. `asset: null` + `status: pending_asset_extraction` means the visual was identified and its source page is known; it is **not** a missing-content error.
6. For graph/table/diagram answer choices, use the normalized option text where supplied and retain the listed `visual_source_pages`. Some graphical choices intentionally use labels/placeholders with the source page because the visual itself is the answer choice.
7. `subject` and `topic` are left null when the source screenshot does not expose reliable UWorld footer metadata. Do not infer or fabricate them during ingestion. `system` is fixed to `Renal, Urinary Systems & Electrolytes` because that is the source collection.
8. Sequential linked items retain `linked_set` metadata and shared vignette provenance. Do not break their source relationship even if the app presents them independently.

## Validation gate
- 720/720 pages assigned to source records: **PASS**
- Complete records with resolved correct answer: **118/118 PASS**
- Complete records with educational objective: **118/118 PASS**
- Correct answer exists in its normalized option set: **118/118 PASS**
- Contiguous option labels after visual adjudication: **118/118 PASS**
- Viewer/footer/Telegram leakage in canonical question/options/explanation text: **0 detected**
- Duplicate UWorld source IDs within Part 1: **0**
- Intentional non-pass records only: source-missing B02Q027 and Part-2 continuation B03Q040

## Files
- `uworld_renal_urinary_electrolytes_part_01.jsonl` — canonical combined corpus
- `block_001.jsonl`, `block_002.jsonl`, `block_003.jsonl` — parallelizable slices
- `manifest.json` — source identity, question IDs, and boundary state
- `qa_report.json` — record-by-record extraction QA

Part 2 must be processed against this manifest before integration so the QID 11806 continuation is merged rather than recreated.