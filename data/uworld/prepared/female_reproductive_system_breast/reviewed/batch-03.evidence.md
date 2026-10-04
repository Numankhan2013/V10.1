# Female Reproductive System & Breast — batch 03 source audit

Audit target: `batch-03.json` (21 records), against the original source PDF at `/workspace/scratch/uworld-female-reproductive/source.pdf`, SHA-256 `ab85991bc3089c7f3936dfe40e7b7d3f31440d3023b83df54b19ec761b75423b` (595 pages). Read-only companions used: `source-ocr.txt`, `source-bboxes.html`, and `page_to_question_manifest.json`. The source page images for every owned page, 322–457, were rendered from the PDF with `pdftoppm -cropbox`; each page was visually inspected in contact sheets, with pages 340, 351, and 389 enlarged for the question exhibits.

## Source coverage

| ID | PDF pages |
|---|---:|
| UWORLD_15589 | 322–325 |
| UWORLD_879 | 326–331 |
| UWORLD_11890 | 332–339 |
| UWORLD_1986 | 340–345 |
| UWORLD_12298 | 346–349 |
| UWORLD_15546 | 350–359 |
| UWORLD_207 | 360–365 |
| UWORLD_8390 | 366–375 |
| UWORLD_20285 | 376–382 |
| UWORLD_577 | 383–388 |
| UWORLD_19189 | 389–395 |
| UWORLD_11888 | 396–402 |
| UWORLD_256 | 403–408 |
| UWORLD_1899 | 409–414 |
| UWORLD_21791 | 415–420 |
| UWORLD_888 | 421–425 |
| UWORLD_1056 | 426–431 |
| UWORLD_11920 | 432–437 |
| UWORLD_1830 | 438–444 |
| UWORLD_11802 | 445–451 |
| UWORLD_578 | 452–457 |

## Confirmed corrections

- `UWORLD_1986`: restored the omitted question-side LH/progesterone-versus-time graph as a figure sourced from page 340. The crop targets the graph itself; the trailing OCR fragment `LH` was removed from the stem. The source answer is D; the PDF’s answer-rate display shows 82%, matching the record.
- `UWORLD_19189`: restored the question-side answer matrix from page 389 as a native table: choices A–E across endogenous GnRH, FSH, and estrogen. The matrix matches the existing answer choices and correct key E; the PDF’s answer-rate display shows 72%, matching the record.
- `UWORLD_15546`: page 351 contains the question’s wet-mount exhibit; the existing question figure reference is correctly assigned to the question. Other figures on pages 353, 356, 358, and 359 are explanation exhibits.
- `UWORLD_15589`: removed a trailing OCR/statistics fragment (`6`) from option D’s text; its selection percentage remains in the separate source-matched statistics field. `UWORLD_11802`: removed the trailing UI fragment `V6` from option E.
- `UWORLD_1830`: the source has six options; upstream OCR had merged E (69,XXX; 9%) and F (69,XXY; 20%) and misread C. Restored the separate E/F options and source percentages, corrected C to 47,XXX, and retained key A / 41% answered correctly. Also corrected the stem OCR `[-hCG` to `β-hCG`.
- Corrected BMI units to `kg/m²` where OCR had reduced the superscript to `kg/m.` and corrected `BMl` to `BMI`.
- The remaining keys and displayed answer percentages checked against the source agree with the prepared records. No confirmed key or statistic changes were made.

## Completion and source limits

All 21 records are now source-reviewed and marked `verified`; `reviewed_pages` enumerates each owned page in the manifest (136 page records total). Explanation text was reconciled against the readable PDF text and page images, including merged sentences crossing viewport pages, removed repeated viewport prose and UI/OCR insertions, restored complete `(Choice X)` discussions and objectives, and preserved scientific wording. No essential source material is missing from the original PDF; no records are blocked.

The batch contains eight native tables: the question-side hormone matrix for `UWORLD_19189`, plus source tables for contraceptive mechanisms (`UWORLD_879`), vaginitis comparisons (`UWORLD_15546`, `UWORLD_11802`), contraceptive contraindications (`UWORLD_577`), cell junctions (`UWORLD_11888`), PCOS (`UWORLD_21791`), and ovarian cancer risk/protective factors (`UWORLD_578`). Source diagrams and histology remain figure references; the question-side graph for `UWORLD_1986` and wet-mount exhibit for `UWORLD_15546` are assigned to the question. There are 51 source figure references across question and explanation content.

The source answer keys and displayed answer rates agree with all 21 records. The only distribution correction was splitting the source-confirmed 9% and 20% E/F responses for `UWORLD_1830`; no answer key or answered-correctly rate changed. Source PDF, OCR companions, normalized records, and original JSONL were not modified.

Root follow-up: Female1830 has a PDF-confirmed six-choice normalization repair
in the separate pinned source_repairs.json ledger. Original archived JSONL is
unchanged; only the normalized adapter row/display was corrected, with refreshed
manifest/row hashes. Reported source percentages remain unchanged.
