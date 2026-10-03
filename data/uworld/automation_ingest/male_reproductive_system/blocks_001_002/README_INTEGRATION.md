# UWorld Male Reproductive System — Blocks 001–002

Canonical OCR reconstruction for downstream NK QBank ingestion.

- Source: `UW 2024 - Male Reproductive System - 2 blocks - OCR.pdf`
- Source SHA-256: `1b06296226be118da84743cd9cf8abed7c3e669dd260543734dbf27cefcf6c24`
- Source pages: 281
- Canonical records: 52
- Block 1: 39 records
- Block 2: 13 records
- Validation: 52/52 PASS
- Educational objectives recovered: 52/52
- Questions requiring source visual handling: 5
- Questions with source answer percentages: 48/52

## Important source anomaly

The first source block labels its items as `of 40`, but the PDF proceeds from **Item 39 of 40 directly to Item 1 of 13** for the second block. No Item 40 is present in this PDF. No synthetic question was created.

## Hard cases resolved

- QID 1737 and QID 839 use image-labeled answer choices and retain source-visual requirements.
- QID 1902 uses a hormone-level answer table reconstructed from the rendered source page.
- QID 1449 uses an internal-genital-duct/external-genitalia answer table reconstructed from the rendered source page.
- Split/dropped percentage labels were repaired only where supported by the rendered/result pages.
- Percentages are left null when the source does not provide a usable value rather than being guessed.

## Integration

Use `qbank_blocks_001_002_male_reproductive_system.jsonl` as the canonical question source. Question boundaries are anchored to UWorld Question IDs rather than PDF page adjacency. Every record retains exact source-page provenance; records needing diagrams/exhibits are explicitly marked for later source-image integration.
