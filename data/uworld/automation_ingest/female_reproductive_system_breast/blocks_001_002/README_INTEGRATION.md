# UWorld Female Reproductive System & Breast — Blocks 001–002

Canonical OCR reconstruction for downstream NK QBank ingestion.

- Source: `UW_2024_Female_Reproductive_System_&_Breast_2_blocks_OCR.pdf`
- Source pages: 595
- Canonical records: 81
- Block 1: 41 records (pages 1–312)
- Block 2: 40 records (pages 313–595)
- Validation: 81/81 PASS
- Educational objectives recovered: 81/81
- Questions with figure/exhibit provenance: 73
- Figure/exhibit provenance references: 232

## Important source anomaly

The source contains **two distinct Question IDs both labeled Item 40 of 40 in block 1**:
- QID 18714
- QID 127

Both records are intentionally preserved. Do not collapse the dataset to 80 records.

## Integration

Use `qbank_blocks_001_002_female_reproductive_system_breast.jsonl` as the canonical question source. Question boundaries are anchored to UWorld Question IDs, not PDF page adjacency. Figure/exhibit references retain source-page provenance so image integration can be performed later against the original PDF.
