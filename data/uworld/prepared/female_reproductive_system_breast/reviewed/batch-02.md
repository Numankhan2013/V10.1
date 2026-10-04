# UWorld Female Reproductive System & Breast — batch 02 source audit

Source: `/workspace/scratch/uworld-female-reproductive/source.pdf` (SHA-256 `ab85991bc3089c7f3936dfe40e7b7d3f31440d3023b83df54b19ec761b75423b`; source span pp. 145–321). Each mapped source page for all 21 records was reviewed in rendered form and against `source-ocr.txt`. The scientific exhibit pages were separately enlarged to read figure titles, labels, and table cells and to assess the candidate crop against interface chrome. Source order, answer labels, and answer-selection percentages were retained; unknown percentages remain null.

## Essential question exhibits restored

- `UWORLD_1109`: biopsy histology, p. 163.
- `UWORLD_1057`: labeled breast anatomy diagram, p. 200.
- `UWORLD_11652`: unannotated ovarian histology in the complete Exhibit Display popup, p. 191; crop `[358,115,965,571]` isolates the image canvas.
- `UWORLD_20083`: complete gross ovarian specimen in the Exhibit Display popup, p. 275; crop `[447,110,876,576]` isolates the full specimen photograph, including its source watermark, and excludes question text/options and popup controls. The question views on pp. 274 and 276 show truncated top/bottom portions at the viewport boundaries and are not used as image crops.
- `UWORLD_1831`: hysterosalpingogram popup exhibit, p. 314.

## Source text tables restored

- `UWORLD_1809`, p. 156: Müllerian agenesis vs androgen insensitivity syndrome; five feature rows.
- `UWORLD_1549`, p. 178: painful/painless infectious genital ulcer comparison; four disease rows.
- `UWORLD_1837`, pp. 252–253: malignant ovarian neoplasms; epithelial, germ-cell, and sex-cord stromal rows.
- `UWORLD_1917`, p. 293: prolactinoma clinical features, workup, and treatment.

OCR that had joined figure/table labels and interface text to prose was removed from affected main explanation paragraphs. Duplicate continuation-page excerpts were removed. Question-stem OCR repairs include BMI/squared-unit typography, the complete diagnosis prompt for `UWORLD_1809`, and removal of UI debris; trailing `6` option artifacts were removed from affected options. No key or percentage discrepancy was found. All 21 records are marked verified and carry their exact source-page lists in the JSON.

**Loader contract repair (2026-10-04):** UWORLD_1809's source table on PDF page 156 now uses the reviewed-document table contract (`caption`, `columns`, and complete rectangular `rows`). The source table compares Müllerian agenesis with androgen insensitivity syndrome and includes its Müllerian-duct footnote. Its reviewed page ownership and all learner/source content remain intact.

**Targeted source-page table repairs (2026-10-04):** Reopened only the cited table pages for the loader-rejected records: `UWORLD_1549` p. 178, `UWORLD_1837` pp. 252–253, and `UWORLD_1917` p. 293. Rebuilt them in the loader's `caption`/`columns`/rectangular `rows` format from the rendered pages. The infectious-ulcer comparison retains all four diseases and their findings; the ovarian-neoplasm chart retains all six tumor rows and the AFP/LDH footnote; the prolactinoma chart retains clinical features, laboratory/imaging, and treatment. This was a targeted repair of those source-page tables, not a new full-batch review.


**Popup crop correction (2026-10-04):** Replaced the viewport crops for `UWORLD_11652` and `UWORLD_20083` with image-canvas-only crops from the complete source popups on pp. 191 and 275, respectively. Page 191 shows the full ovarian histology exhibit; page 275 shows the entire gross specimen, including the hair and lower specimen edge. The source placements on pp. 274 and 276 repeat partial views interrupted by the interface and are excluded from the question image nodes. No question prose, options, key, or statistics were changed in this correction.
