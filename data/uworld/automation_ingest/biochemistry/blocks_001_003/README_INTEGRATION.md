# UWorld 2024 — Biochemistry — 3 Blocks

Canonical OCR reconstruction for NK QBank ingestion.

## Canonical files

- `qbank_blocks_001_003_biochemistry.jsonl` — **120 questions**, exactly 40 per nominal block.
- `supplemental_biochemistry_questions.jsonl` — **12 additional complete Biochemistry questions** present in the source outside the three nominal 40-question blocks.
- `question_index.csv` / `supplemental_index.csv` — page/QID audit maps.
- `manifest.json` — source structure, hashes, rendered-header corrections, and source limitations.
- `qa_report.json` — validation results.
- `source_anomalies.json` — unusual source layout and clipping notes.

## Source structure

The 729-page PDF is not simply 3 consecutive blocks. It contains:

1. Block 1 — pages 1–225 — 40 questions.
2. Block 2 — pages 226–440 — 40 questions.
3. Complete orphan QID 1434 — pages 441–444.
4. Separate 11-question mini-block — pages 445–504, captured in descending item order.
5. Block 3 — pages 505–729 — 40 questions, captured in descending item order with reverse screenshot progression.

The main JSONL therefore remains 120 questions. The extra 12 complete questions are preserved separately rather than dropped or mixed into the three-block dataset.

## Render-authoritative repairs

Rendered UWorld headers were used when OCR header text was corrupt:

- Block 2 item 2: `103-0` → QID **1030**
- Block 2 item 32: `14TT` → QID **1477**
- Block 3 item 11: `213()7` → QID **21307**

Headerless reverse-capture pages were also reassigned by their visible content:

- pages 545–546 belong to **QID 1866**, not QID 1727
- page 621 belongs to **QID 1790**, not QID 2038

Diagram/table answers for QIDs **1032**, **107590**, and **11914** were linearized from rendered pages rather than OCR guesses.

## Source limitations intentionally not fabricated

- **QID 1486:** the `Educational objective:` heading is visible, but its text is below the captured viewport / obscured by exhibit overlays. The objective is left null and documented.
- Some answered-correctly percentages are absent because the source itself shows `Collecting Statistics`; they remain null.
- **QID 11914 option A percentage:** the answered screenshot exposes B=3%, C=4%, D=3%, E=84%, while A is above the captured viewport; A remains null.

## Validation

- 120/120 nominal-block records structurally pass.
- 12/12 supplemental records structurally pass.
- 132 unique Question IDs.
- Question text, correct answer, and explanation present for all 132 records.
- 131/132 educational objectives recovered exactly; the sole exception is the source-clipped QID 1486 objective.
- All 729 PDF pages are assigned exactly once across canonical + supplemental records.
- No duplicate QIDs, no invalid option-label sequences, no correct-answer/percentage mismatches, and no detected UWorld UI-chrome leakage in question/explanation/objective text.
- 284 figure/exhibit provenance references across 112 questions; image asset extraction remains deferred for the later image-integration pass.