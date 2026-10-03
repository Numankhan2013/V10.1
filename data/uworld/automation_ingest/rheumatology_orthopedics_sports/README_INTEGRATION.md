# UWorld Rheumatology / Orthopedics & Sports — 5 Blocks

Production ingest package reconstructed from `UW_2024_Rheumatology_Orthopedics_&_Sports_5_blocks_OCR.pdf`.

## Contents

- `qbank_rheumatology_orthopedics_sports_all_172.jsonl` — canonical master dataset.
- `qbank_block_001_rheumatology_orthopedics_sports.jsonl` — 40 questions.
- `qbank_block_002_rheumatology_orthopedics_sports.jsonl` — 40 questions.
- `qbank_block_003_rheumatology_orthopedics_sports.jsonl` — 40 questions.
- `qbank_block_004_rheumatology_orthopedics_sports.jsonl` — 40 questions.
- `qbank_block_005_rheumatology_orthopedics_sports.jsonl` — 12 questions.
- `page_to_question_manifest.json` — source-page / question / visual-reference mapping.
- `manifest.json` — package metadata and hashes from reconstruction.
- `qa_report.json` — validation report.

## Integration contract

- There are **172 unique questions**, distributed 40 + 40 + 40 + 40 + 12.
- Treat the UWorld `question_id` and canonical record `id` as stable identifiers.
- Source question/explanation pages are carried on each record. Page order was not blindly assumed when source screenshots were interleaved.
- Visuals are intentionally represented as source-PDF page references with deferred image-crop status. Do not treat these as missing image data.
- Answer-choice percentages are preserved when visible. Seven source questions display "Collecting Statistics"; their unavailable percentages are intentionally null rather than inferred.
- Do not replace source-derived question wording or explanation content with external medical text during ingest.

## Source PDF note

The source PDF is approximately 235 MB, above GitHub's normal 100 MB single-file repository limit. It is therefore **not represented here as a normal Git blob**. Use the original source file supplied with this ingest when performing the later visual-crop/image-integration stage.

## QA

The reconstruction package was validated for 172/172 unique question records, block/item continuity, valid option labels and correct-answer mappings, populated stems/explanations/objectives, and source-page visual references.
