# PDF-only Ophthalmology extraction

This is the immutable source snapshot for the original 30-question, 204-page
Ophthalmology block. `manifest.json` pins the original PDF and JSONL bytes;
`page_to_question_manifest.json` accounts for every source page. Rows preserve
per-page OCR alongside reviewed question text, choices, answer keys and prose.
The source PDF is tracked by its unchanged Git LFS pointer.

The three display documents under `data/uworld/reviewed/ophthalmology` supply
source ordering, native tables and complete focused figures. They pin each
complete source row. OCR screenshot transcripts remain archival and are not
repeated inside the shipped runtime. `qa_report.json` records source review,
independent answer-key checks and crop reconciliation; it is not clinical
certification. See `docs/UWORLD_OPHTHALMOLOGY_COLLECTION.md` for build status.
