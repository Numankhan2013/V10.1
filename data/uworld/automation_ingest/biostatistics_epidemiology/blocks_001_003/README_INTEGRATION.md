# UWorld 2024 - Biostatistics & Epidemiology (3 blocks)

Canonical OCR reconstruction for NK QBank ingestion.

## Canonical dataset
- Source PDF: `UW 2024 - Biostatistics & Epidemiology - 3 blocks - OCR.pdf`
- Source pages: 548
- Canonical blocks: 3
- Canonical questions: 120 (40 + 40 + 40)
- Validation: 120/120 PASS
- Educational objectives recovered: 120/120
- Figure/exhibit provenance references: 110
- Table provenance references: 4

Use `qbank_blocks_001_003_biostatistics_epidemiology.jsonl` as the canonical three-block source.

## OCR Question-ID repairs
The embedded OCR truncated six Question IDs. The rendered UWorld headers were inspected and are authoritative:
- page 4: OCR `193` -> rendered `19308`
- page 46: OCR `12` -> rendered `1277`
- page 306: OCR `123` -> rendered `1230`
- page 361: OCR `1` -> rendered `1303`
- page 372: OCR `193` -> rendered `19309`
- page 464: OCR `194` -> rendered `19406`

## Source tail after block 3
The PDF does not end cleanly at the third 40-question block.

- Pages 544-547: `Item 1 of 2`, QID **19197** - complete biostatistics regression-analysis question. Preserved in `supplemental_complete_biostatistics_items.jsonl`; intentionally excluded from the canonical 120.
- Page 548: `Item 2 of 2`, QID **20932** - unrelated transplant/infectious-disease stem. The PDF ends before its answer/explanation. It is documented in `source_exclusions.json` and is **not** fabricated into a canonical record.

## Source fidelity
Question boundaries use rendered Item/Question-ID headers. OCR text supplies reconstruction, while rendered pages are authoritative where OCR conflicts. Figure/exhibit assets are deferred, but page provenance is retained for later image integration.

Two canonical questions (10672, 1191) have no recoverable time-spent value because the answer-summary region is cropped/absent in the source capture. No value was invented.