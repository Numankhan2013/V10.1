# Female Reproductive System & Breast — batch 04 source audit

- Source PDF: `/workspace/scratch/uworld-female-reproductive/source.pdf`
- Source SHA-256: `ab85991bc3089c7f3936dfe40e7b7d3f31440d3023b83df54b19ec761b75423b`
- Scope: batch 04, items 23–40, question IDs 20237, 1015, 7489, 831, 18654, 20169, 15869, 1096, 1932, 2056, 18233, 1929, 333, 20084, 18919, 19970, 19641, and 11781.
- Pages reviewed: PDF pages 458–595 inclusive (138 pages). Every page was reviewed visually in rendered contact sheets; crowded exhibits and table pages were enlarged for transcription. Pages 458–459 for UWORLD_20237 were subsequently checked individually: p. 458 contains the stem and gross specimen, and p. 459 shows the complete enlarged specimen; the exhibit crop now uses the full specimen on p. 459. OCR and the source bounding-box export were used as navigation aids; the PDF page images were authoritative.
- Result: 18/18 records verified; 138/138 source pages recorded in each record’s `reviewed_pages`. All existing answer keys, option order, and reported statistics were checked against the source and retained. The missing statistics for UWORLD_1015 remain null as shown in the source.

## Repairs and source handling

- Restored the missing question exhibit for UWORLD_20237 from the full gross specimen on page 459 and UWORLD_19641 from page 578, with crops that retain the full gross specimens/arrow and omit screen controls.
- Removed OCR insertion noise from question and explanation text, including UI strings, repeated fragments, split words, and the missing-picture placeholder in UWORLD_20237. Restored the cleaned specimen prompt for UWORLD_19970 and the source’s BMI unit for UWORLD_19641.
- Recovered source explanation passages lost or mixed with OCR table text in UWORLD_831, UWORLD_1096, UWORLD_20169, UWORLD_2056, and UWORLD_18233. Retained the full source explanation and the source choice discussions, including inline answer-choice references.
- Represented legible source text tables as native table blocks for UWORLD_831 (page 488), UWORLD_20169 (501), UWORLD_1096 (508), UWORLD_2056 (521), UWORLD_18233 (533), and UWORLD_333 (548). Added a complete textual table for the illustrated vaginitis differential on page 518 while retaining that source figure, whose medical illustrations are part of the source exhibit.
- Retained explanation figures as figures, including histology, cytology, gross pathology, anatomy, and illustrated educational charts. Existing candidate crops were visually checked for role, scientific labels, and screen chrome; the two added question crops are source-specific.

No essential source omissions remain in this batch. The `normalized.jsonl`, source originals, manifests, shared tools, and PDF were not edited.
