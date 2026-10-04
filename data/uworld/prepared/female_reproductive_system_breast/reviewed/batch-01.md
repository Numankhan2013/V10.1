# Female Reproductive System & Breast — batch 01 source audit

**Result:** 21/21 records verified against the original PDF. Source: `/workspace/scratch/uworld-female-reproductive/source.pdf`; SHA-256 `ab85991bc3089c7f3936dfe40e7b7d3f31440d3023b83df54b19ec761b75423b`. The PDF has 595 pages and 90° page rotation. The assigned records cover normalized source pages 1–144; page 145 begins the next item and is outside this batch. `reviewed_pages` now matches each record's complete `source_pages` list in immutable `normalized.jsonl`.

## Page coverage

| Record | Source pages | Record | Source pages | Record | Source pages |
|---|---:|---|---:|---|---:|
| UWORLD_869 | 1–8 | UWORLD_21426 | 9–12 | UWORLD_258 | 13–19 |
| UWORLD_1560 | 20–23 | UWORLD_18918 | 24–31 | UWORLD_299 | 32–39 |
| UWORLD_110 | 40–46 | UWORLD_1027 | 47–52 | UWORLD_1877 | 53–60 |
| UWORLD_1158 | 61–69 | UWORLD_1928 | 70–74 | UWORLD_18747 | 75–83 |
| UWORLD_1810 | 84–90 | UWORLD_19886 | 91–96 | UWORLD_12225 | 97–102 |
| UWORLD_11908 | 103–107 | UWORLD_11885 | 108–115 | UWORLD_1992 | 116–121 |
| UWORLD_1008 | 122–129 | UWORLD_21642 | 130–138 | UWORLD_1632 | 139–144 |

## Review method and decisions

Rendered pages 1–145 from the pinned source with `pdftoppm -cropbox -r 72 -png` and inspected all pages in labeled ten-page contact sheets. OCR page text and bbox evidence were cross-checked against the page images. I enlarged pages 72 and 93 at 144 dpi to resolve table glyphs and the ovarian-mass threshold. The rendered rotated page is approximately 1416 × 757 points. The draft `[64,116,1264,621]` region was treated only as a candidate. Final figure regions use `[96,116,1230,550]` after checking each exhibit page; this retains the complete diagram or specimen and its labels while excluding the popup frame and bottom zoom controls.

Corrected source-visible OCR artifacts in stems and choices, including “last 3 days,” the superscript in BMI units, “theca interna,” and stray selection-marker digits in UWORLD_21426 and UWORLD_1008. Percentages, answer labels, correct answers, and available statistics were compared with the submitted-answer pages; no source discrepancy was found, and no absent statistic was filled in. The source objectives were retained and OCR-damaged objectives were restored from their explanation pages. Explanation display prose was cleaned of repeated page-overlap and screenshot-control text while retaining the source's scientific statements and choice discussions.

Restored text tables as native nodes at their original explanation positions from pages 3 (cervical-cancer risk factors), 42 (vulvovaginal candidiasis), 58 (breast-cancer classification), 63 (granulosa-cell tumor), 72 (malignant ovarian neoplasms), 93 (ovarian torsion), and 124 (acute cervicitis). Their table cells were transcribed from the rendered page images, including all visible rows and footnotes. These text tables are represented natively; raster pathology and anatomy exhibits remain source figures.

The exhibit audit found that UWORLD_1027's full PID illustration is on page 49; it was restored from that page. The draft page-52 PCOS image belongs to adjacent source material and was removed. UWORLD_1008's page-129 estrogen-conversion image was likewise an unrelated carry-over and was removed. The table pages for UWORLD_110 and UWORLD_1877 are represented by their native tables instead of duplicate figure crops. Remaining exhibit pages were retained after page-by-page relevance review.

## Limits

No answer-essential source omission was found in this batch. No record is blocked. No source-page range outside pages 1–144 was claimed as reviewed. The source PDF, OCR originals, normalized records, source hashes, and other reviewed batches were not modified.
