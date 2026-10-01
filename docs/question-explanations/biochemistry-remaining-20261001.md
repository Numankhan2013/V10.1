# Biochemistry remaining explanations audit — 2026-10-01

**Scope:** canonical Biochemistry source SHA-256 `919f0709b2eb833e302c6f7524b6dd2bd13bfaed638009375b5062135d3795b1`; authored against base `d4abce86068b4221e61e541c34dd29258de61cca` on `work/luna-biochem-remaining`. This checkpoint covers 226 of the 263 actionable pending IDs. The authored-and-validated count is separate from deployment; no runtime wiring or preview build is included in this worktree. Eight source-gated IDs remain excluded and untouched: CH13 Q020, CH14 Q012/Q018, CH15 Q003, CH16 Q014, CH17 Q012, CH27 Q012, CH28 Q009.

## Batches

| File | Count | Source question IDs |
|---|---:|---|
| `explanation_biochem_ch15_q001_q012_v1.json` | 11 | Q001, Q002, Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q011, Q012 |
| `explanation_biochem_ch15_q013_q024_v1.json` | 12 | Q013, Q014, Q015, Q016, Q017, Q018, Q019, Q020, Q021, Q022, Q023, Q024 |
| `explanation_biochem_ch16_q001_q012_v1.json` | 12 | Q001, Q002, Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q011, Q012 |
| `explanation_biochem_ch16_q015_q021_v1.json` | 7 | Q015, Q016, Q017, Q018, Q019, Q020, Q021 |
| `explanation_biochem_ch17_q001_q010_v1.json` | 10 | Q001, Q002, Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010 |
| `explanation_biochem_ch17_q013_q024_v1.json` | 12 | Q013, Q014, Q015, Q016, Q017, Q018, Q019, Q020, Q021, Q022, Q023, Q024 |
| `explanation_biochem_ch18_q001_q019_v1.json` | 18 | Q001–Q008, Q010–Q019 |
| `explanation_biochem_ch19_q001_q010_v1.json` | 10 | Q001–Q010 |
| `explanation_biochem_ch19_q011_q020_v1.json` | 9 | Q011–Q018, Q020 |
| `explanation_biochem_ch20_q001_q017_v1.json` | 16 | Q001–Q005, Q007–Q017 |
| `explanation_biochem_ch21_q001_q011_v1.json` | 11 | Q001–Q011 |
| `explanation_biochem_ch21_q013_q020_v1.json` | 8 | Q013–Q020 |
| `explanation_biochem_ch22_q001_q013_v1.json` | 12 | Q001–Q005, Q007–Q013 |
| `explanation_biochem_ch23_q001_q014_v1.json` | 13 | Q001–Q004, Q006–Q014 |
| `explanation_biochem_ch24_q001_q017_v1.json` | 16 | Q001–Q015, Q017 |
| `explanation_biochem_ch25_q001_q018_v1.json` | 18 | Q001–Q018 |
| `explanation_biochem_ch25_q019_q028_v1.json` | 10 | Q019–Q028 |
| `explanation_biochem_ch26_q001_q019_v1.json` | 18 | Q001–Q013, Q015–Q019 |
| `explanation_biochem_ch26_q020_q022_v1.json` | 3 | Q020–Q022 |

## Source review and flags

All learner explanations preserve the original question stem, options, answer index, source tables, figure metadata, and provenance in the immutable canonical shard. The authored JSON files add takeaways, display text, selective emphasis, and one rationale for each of the three source-keyed incorrect options. The source-order batches include only pending/actionable IDs; no approved explanation was overwritten.

- Chapters 15–16 explanations use the source explanation as the detailed-display foundation, with concise individualized takeaways and distractor reasoning. Ch15 Q013 repairs a broken sentence from its explicit PIP2/PLC/IP3/DAG context. Ch16 Q004 corrects the source claim that vitamin C is a direct CYP7A1 cofactor; the display retains the first intermediate, NADPH/oxygen chemistry and FXR feedback.
- Chapter 17 source explanations contain OCR/diagram debris and cross-question solutions. Displays isolate only the relevant item details. Reconstruction evidence is recorded per affected question. Q17 Q007 had no imported explanation; the lead/ALA-dehydratase explanation is reconstructed from the stem, source key, and established heme-pathway toxicology.
- Ch15 Q011 qualifies the source word “only” for cardiolipin distribution while retaining mitochondrial enrichment, function and Barth-syndrome details. Ch15 Q021 clarifies that Fabry is X-linked and female heterozygotes can manifest. Ch17 Q010 preserves the source exam contrast while noting FECH inheritance complexity.
- Ch17 Q022 is authored with `needs_manual_review`: its stem refers to laboratory values absent from the canonical question record. MRP2 remains supported by the reported black-liver finding and source explanation; no missing laboratory data were invented.
- Source-limited questions remain excluded: Ch15 Q003 lacks the numbered organ mapping; Ch16 Q014 lacks the numbered lipoprotein list; Ch17 Q012 remains blocked under the completeness ledger. No question key, option, or source gate was changed.

## Per-question source references

Page references below are from immutable `provenance.questionPages` / `provenance.explanationPages`; reconstruction notes in each augmentation record identify OCR damage, omitted neighboring solutions, and source-local evidence.

### `explanation_biochem_ch15_q001_q012_v1.json`

- `marrow__BIOCHEM_CH15_Q001` — key A; question p. 229, explanation p. 237.
- `marrow__BIOCHEM_CH15_Q002` — key B; question p. 229, explanation p. 237,238.
- `marrow__BIOCHEM_CH15_Q004` — key C; question p. 229,230, explanation p. 238.
- `marrow__BIOCHEM_CH15_Q005` — key C; question p. 230, explanation p. 238,239.
- `marrow__BIOCHEM_CH15_Q006` — key B; question p. 230, explanation p. 239.
- `marrow__BIOCHEM_CH15_Q007` — key B; question p. 230,231, explanation p. 240.
- `marrow__BIOCHEM_CH15_Q008` — key A; question p. 231, explanation p. 240.
- `marrow__BIOCHEM_CH15_Q009` — key B; question p. 231, explanation p. 240.
- `marrow__BIOCHEM_CH15_Q010` — key A; question p. 231, explanation p. 241.
- `marrow__BIOCHEM_CH15_Q011` — key B; question p. 231,232, explanation p. 241; reconstruction review.
- `marrow__BIOCHEM_CH15_Q012` — key B; question p. 232, explanation p. 241.

### `explanation_biochem_ch15_q013_q024_v1.json`

- `marrow__BIOCHEM_CH15_Q013` — key B; question p. 232, explanation p. 241,242; reconstruction review.
- `marrow__BIOCHEM_CH15_Q014` — key C; question p. 232, explanation p. 242.
- `marrow__BIOCHEM_CH15_Q015` — key B; question p. 233, explanation p. 242.
- `marrow__BIOCHEM_CH15_Q016` — key B; question p. 233, explanation p. 242,243.
- `marrow__BIOCHEM_CH15_Q017` — key B; question p. 233, explanation p. 243.
- `marrow__BIOCHEM_CH15_Q018` — key D; question p. 233, explanation p. 243.
- `marrow__BIOCHEM_CH15_Q019` — key A; question p. 233,234, explanation p. 244.
- `marrow__BIOCHEM_CH15_Q020` — key A; question p. 234,235, explanation p. 244.
- `marrow__BIOCHEM_CH15_Q021` — key B; question p. 235, explanation p. 244; reconstruction review.
- `marrow__BIOCHEM_CH15_Q022` — key C; question p. 235,236, explanation p. 245,246.
- `marrow__BIOCHEM_CH15_Q023` — key B; question p. 236, explanation p. 246.
- `marrow__BIOCHEM_CH15_Q024` — key B; question p. 236, explanation p. 246.

### `explanation_biochem_ch16_q001_q012_v1.json`

- `marrow__BIOCHEM_CH16_Q001` — key A; question p. 247, explanation p. 253.
- `marrow__BIOCHEM_CH16_Q002` — key C; question p. 247, explanation p. 254.
- `marrow__BIOCHEM_CH16_Q003` — key D; question p. 247, explanation p. 254.
- `marrow__BIOCHEM_CH16_Q004` — key B; question p. 247,248, explanation p. 254; reconstruction review.
- `marrow__BIOCHEM_CH16_Q005` — key B; question p. 248, explanation p. 255.
- `marrow__BIOCHEM_CH16_Q006` — key C; question p. 248, explanation p. 255.
- `marrow__BIOCHEM_CH16_Q007` — key A; question p. 248, explanation p. 256.
- `marrow__BIOCHEM_CH16_Q008` — key B; question p. 248,249, explanation p. 256.
- `marrow__BIOCHEM_CH16_Q009` — key A; question p. 249, explanation p. 256.
- `marrow__BIOCHEM_CH16_Q010` — key A; question p. 249, explanation p. 256.
- `marrow__BIOCHEM_CH16_Q011` — key D; question p. 249, explanation p. 256.
- `marrow__BIOCHEM_CH16_Q012` — key D; question p. 249,250, explanation p. 257.

### `explanation_biochem_ch16_q015_q021_v1.json`

- `marrow__BIOCHEM_CH16_Q015` — key B; question p. 251, explanation p. 258,259.
- `marrow__BIOCHEM_CH16_Q016` — key A; question p. 251, explanation p. 259.
- `marrow__BIOCHEM_CH16_Q017` — key D; question p. 251, explanation p. 259,260.
- `marrow__BIOCHEM_CH16_Q018` — key D; question p. 251, explanation p. 260.
- `marrow__BIOCHEM_CH16_Q019` — key A; question p. 252, explanation p. 260.
- `marrow__BIOCHEM_CH16_Q020` — key A; question p. 252, explanation p. 260.
- `marrow__BIOCHEM_CH16_Q021` — key B; question p. 252, explanation p. 261.

### `explanation_biochem_ch17_q001_q010_v1.json`

- `marrow__BIOCHEM_CH17_Q001` — key A; question p. 262, explanation p. 270; reconstruction review.
- `marrow__BIOCHEM_CH17_Q002` — key D; question p. 262, explanation p. 270; reconstruction review.
- `marrow__BIOCHEM_CH17_Q003` — key C; question p. 262, explanation p. 270; reconstruction review.
- `marrow__BIOCHEM_CH17_Q004` — key A; question p. 262, explanation p. 271; reconstruction review.
- `marrow__BIOCHEM_CH17_Q005` — key A; question p. 263, explanation p. 272; reconstruction review.
- `marrow__BIOCHEM_CH17_Q006` — key B; question p. 263, explanation p. 273; reconstruction review.
- `marrow__BIOCHEM_CH17_Q007` — key B; question p. 263, explanation p. 273; reconstruction review.
  - Flag: no imported explanation; mechanism reconstructed from the lead-ingestion stem and keyed ALA-dehydratase option.
- `marrow__BIOCHEM_CH17_Q008` — key B; question p. 264, explanation p. 274; reconstruction review.
- `marrow__BIOCHEM_CH17_Q009` — key C; question p. 264, explanation p. 275; reconstruction review.
- `marrow__BIOCHEM_CH17_Q010` — key A; question p. 264, explanation p. 275; reconstruction review.

### `explanation_biochem_ch17_q013_q024_v1.json`

- `marrow__BIOCHEM_CH17_Q013` — key D; question p. 265, explanation p. 277; reconstruction review.
- `marrow__BIOCHEM_CH17_Q014` — key A; question p. 265, explanation p. 277; reconstruction review.
- `marrow__BIOCHEM_CH17_Q015` — key C; question p. 266, explanation p. 277; reconstruction review.
- `marrow__BIOCHEM_CH17_Q016` — key B; question p. 266, explanation p. 278; reconstruction review.
- `marrow__BIOCHEM_CH17_Q017` — key B; question p. 267, explanation p. 278; reconstruction review.
- `marrow__BIOCHEM_CH17_Q018` — key B; question p. 267, explanation p. 278; reconstruction review.
- `marrow__BIOCHEM_CH17_Q019` — key D; question p. 267, explanation p. 279; reconstruction review.
- `marrow__BIOCHEM_CH17_Q020` — key B; question p. 267, explanation p. 280; reconstruction review.
- `marrow__BIOCHEM_CH17_Q021` — key A; question p. 268, explanation p. 280; reconstruction review.
- `marrow__BIOCHEM_CH17_Q022` — key D; question p. 268, explanation p. 281; reconstruction review.
  - Flag: missing lab values referenced in stem; display uses biopsy finding and source explanation only.
- `marrow__BIOCHEM_CH17_Q023` — key C; question p. 268, explanation p. 281; reconstruction review.
- `marrow__BIOCHEM_CH17_Q024` — key B; question p. 269, explanation p. 282; reconstruction review.

## Additional question references — checkpoint 101 of 263


### `explanation_biochem_ch18_q001_q019_v1.json`

- `marrow__BIOCHEM_CH18_Q001` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q002` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q003` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q004` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q005` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q006` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q007` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q008` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q010` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q011` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q012` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q013` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q014` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q015` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q016` — key C; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q017` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q018` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH18_Q019` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.


### `explanation_biochem_ch19_q001_q010_v1.json`

- `marrow__BIOCHEM_CH19_Q001` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q002` — key C; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q003` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q004` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q005` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q006` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q007` — key C; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q008` — key C; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q009` — key C; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q010` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.


### `explanation_biochem_ch19_q011_q020_v1.json`

- `marrow__BIOCHEM_CH19_Q011` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q012` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q013` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q014` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q015` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q016` — key A; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q017` — key D; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q018` — key B; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

- `marrow__BIOCHEM_CH19_Q020` — key C; question and explanation source pages are recorded in `provenance` and `sourceNotes`.

### Additional question references — checkpoint 136 of 263

- Chapter 20, Q001–Q005 and Q007–Q017 (16 items); chapter 21, Q001–Q011 and Q013–Q020 (19 items). Source-page citations and source-key rationale mappings are included in the corresponding augmentation records.

### Additional question references — checkpoint 177 of 263

- Chapter 22, Q001–Q005 and Q007–Q013 (12 items); chapter 23, Q001–Q004 and Q006–Q014 (13 items); chapter 24, Q001–Q015 and Q017 (16 items). Source-page citations and question-key rationales are included per item in the augmentation records.

### Additional question references — checkpoint 226 of 263

- Chapter 25, Q001–Q028 (28 items); chapter 26, Q001–Q013, Q015–Q022 (21 items). Source-page citations and keyed rationales are included per item. Chapter 26 Q015 is flagged `needs_manual_review`: its source key selects alanine tRNA, while U6 snRNA also has a specialized 5′ end rather than conventional m7G capping; the printed key and source record remain unchanged.
