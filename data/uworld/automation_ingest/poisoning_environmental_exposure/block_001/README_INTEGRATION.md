# UWorld Poisoning & Environmental Exposure - Block 01

Production ingest package for the 33-question UWorld block in `UW_2024_Poisoning_&_Environmental_Exposure_1_block_OCR.pdf`.

## Files

- `qbank_block_001_poisoning_environmental_exposure.jsonl` - canonical one-question-per-line JSONL.
- `manifest.json` - source checksum, page-to-question map, special structures, and intentional nulls.
- `qa_report.json` - validation results and fidelity notes.

## Integration contract

- Treat `question_id` (`UWORLD_<Question ID>`) as the stable canonical identifier.
- Rendered PDF pages are authoritative. The source page arrays on every record are intended for audit and later visual extraction.
- `asset: null` on explanation/question visuals means **pending source-PDF crop/extraction**, not missing source data.
- Questions 19 and 20 form a linked sequential set and share the vignette stored in `question_set.shared_vignette`.
- Question 32 requires graph assets; do not replace its graph options with text-only placeholders in the production UI.
- Per-option UWorld percentages are stored on each option and under `uworld_stats`. For question 32, D/E percentages are not visible in the captured review pages and are deliberately `null`.
- `classification_hint` is explicitly marked as either source metadata or content inference. Do not treat inferred discipline as an original UWorld metadata field.

## QA result

**PASS** - 33/33 records; 166/166 PDF pages mapped; 33/33 correct answers resolved; no duplicate IDs; no source UI/footer leakage in canonical stems/explanations.
