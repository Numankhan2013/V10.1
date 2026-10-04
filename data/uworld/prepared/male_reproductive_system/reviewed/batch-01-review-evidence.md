# UWorld Male Reproductive System, batch 01 review evidence

Reviewed 26 records in `batch-01.json` against the pinned source PDF, SHA-256 `1b06296226be118da84743cd9cf8abed7c3e669dd260543734dbf27cefcf6c24`. Source ownership is anchored by the immutable `normalized.jsonl`; reviewed page sets now match each owned record's `source_pages` exactly.

## Pages examined and method

Every source page owned by this batch, PDF pages **1–138**, was examined. I read the supplied OCR text page by page and visually inspected a complete set of `pdftoppm -r 72 -cropbox` page renders (contact sheets plus enlarged page views for tables, figures, and unclear OCR). No PyMuPDF was installed or used. The supplied OCR file has a form feed between pages. The images were used to resolve text, labels, and source exhibit/table boundaries; they were not treated as replacements for source wording.

Record page ownership:

| Record | Pages | Record | Pages |
|---|---:|---|---:|
| UWORLD_1737 | 1–8 | UWORLD_8351 | 9–11 |
| UWORLD_11658 | 12–17 | UWORLD_19030 | 18–24 |
| UWORLD_15804 | 25–29 | UWORLD_107790 | 30–34 |
| UWORLD_1902 | 35–39 | UWORLD_8930 | 40–43 |
| UWORLD_807 | 44–48 | UWORLD_580 | 49–52 |
| UWORLD_19697 | 53–58 | UWORLD_343 | 59–67 |
| UWORLD_19029 | 68–70 | UWORLD_419 | 71–78 |
| UWORLD_8468 | 79–82 | UWORLD_16005 | 83–85 |
| UWORLD_19020 | 86–89 | UWORLD_1055 | 90–96 |
| UWORLD_15538 | 97–101 | UWORLD_19012 | 102–106 |
| UWORLD_8326 | 107–111 | UWORLD_19031 | 112–115 |
| UWORLD_1870 | 116–120 | UWORLD_687 | 121–126 |
| UWORLD_20231 | 127–135 | UWORLD_7606 | 136–138 |

## Corrections and reconstructed exhibits

- Replaced OCR-damaged prose with the visible source wording where overlapping screenshot text had produced duplicated or truncated content: UWORLD_1737, _15804, _19030, _8930, _1055, _19012, _20231, _687, _19029, _419, _8468, and _16005. Corrected isolated OCR splits in objectives and explanation prose where the page image resolved the intended printed word.
- Restored the opening sentence of the UWORLD_19012 explanation from page 104, which the OCR draft had reduced to the trailing word “intercourse.”
- Reconstructed native tables from the source pages: UWORLD_19030 (p20), _15804 (p27), _8930 (p42), _807 (p46), _580 (p51), _19020 (p88), _1055 (p92–93), _15538 (p99), _19012 (p104), _687 (p123), and _20231 (p129). The UWORLD_1902 question matrix is a native table with a Choice column and the Testosterone, Inhibin, FSH, and LH columns, preserving rows A–E from pp35–36.
- Tightened the UWORLD_1737 question figure on p2 to the CT exhibit itself (`[359,189,967,543]`), preserving its complete A–F labels while excluding popup chrome. Other owned source figure nodes were retained after page-image checks confirmed that their current exhibit crops include the scientific content and exclude popup header/footer controls.
- Preserved source answer keys, option order, option wording except for the OCR-only question-matrix header cleanup, and all percentages.

## Source limitations recorded

- UWORLD_1902: the explanation says the Sertoli-cell-failure hormone pattern is “Choice D” on pp38–39, while the question matrix/result on pp35–36 marks row C correct. The explanation reference remains verbatim and the conflict is recorded in the record's `issues`.
- UWORLD_19020: the explanation calls the decreased prostate-volume effect “Choice E” on p89, while the result on pp86–87 marks B correct. The explanation reference remains verbatim and the conflict is recorded in `issues`.
- UWORLD_15804: the source calls the marker “beta human chorionic growth hormone” on pp27–28. This source wording remains verbatim and is recorded in `issues` rather than silently substituting a clinical term.

All 26 documents are marked `verified` after inspection of their exact source page sets. No unresolved omitted essential exhibit or unanswerable record was found in this batch.
