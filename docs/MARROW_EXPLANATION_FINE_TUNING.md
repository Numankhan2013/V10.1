# Marrow explanation fine-tuning runbook

> Status: active content-quality workflow under the canonical Marrow automation policy.
> Before every unattended explanation run, read the complete
> `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md` and
> `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`, then resolve the exact current
> head of `feature/marrow-canonical-full-current`.
> Read with `docs/MARROW_BANK_INTEGRATION.md` and the approved explanation
> augmentation already in the repository.

## Goal

Fine-tune learner-facing explanations for the full Marrow bank while keeping the imported ED8 source transcription auditable and unchanged.

Current canonical scope:
- Anatomy: 1,115 questions / 63 topics.
- Biochemistry: 582 / 28.
- Physiology: 1,014 / 43.
- Total: 2,711 questions / 134 topics.

Do not use the historical 2,455-question intermediate denominator or older topic counts for completeness or next-work decisions.

The verified Anatomy/Physiology reference set plus approved later subject batches establishes the desired hierarchy, selective bolding, source-table handling, and concise **Why the other options are wrong** section. Copy the grammar and quality standard, not wording mechanically.

## Non-negotiable source rules

- Imported Marrow source text remains immutable and auditable.
- Never silently paraphrase away unique medical meaning.
- Never invent a missing list, table, diagram label, mechanism or fact.
- Existing source tables stay tables.
- Figure/image metadata stays preserved even if binaries are deferred.
- Source omissions/uncertain reconstructions stay flagged until source evidence resolves them.
- Resolved reconstructions keep internal provenance.
- PrepLadder source-PDF renderers are unrelated and must not be changed here.
- Every batch starts from the exact current canonical head; historical rollout branches are donors/history only unless explicitly transplanted and reverified.

## Approved learner-facing grammar

### 1. Key Takeaway
- one high-yield discriminator, usually one compact sentence;
- source-derived/reviewed;
- never use a vacuous answer such as “All of the above” when a meaningful source explanation exists.

### 2. Detailed Explanation — Structured text
- readable paragraphs with semantic hierarchy;
- selective bolding of exam-relevant discriminators, timing, pathways, derivatives, definitions and contrasts;
- structured lists only when the source is genuinely list-like;
- real populated HTML tables when structured table data exists;
- no forced bulletization of normal prose.

### 3. Why the other options are wrong
- exactly three rationales for a four-option single-best-answer question;
- one concise exam discriminator per incorrect option;
- explain what makes that option wrong, not a mini textbook;
- rationales remain separate generated augmentation, never original Marrow text.

### 4. FSRS recall dock
- remains fixed/floating in the session footer above Previous/Next;
- explanation work must not move it into document flow or alter scheduler semantics.

## Structured table contract

Structured explanation tables are owned by the **explanation/runtime integration path**, not the image pipeline, unless the original source explicitly requires a raster/image table asset.

Canonical ED8 table data may contain object columns (`{key,label}`) and object rows keyed by those column keys. That source representation is valid and must not be string-coerced directly into the UI.

A table is considered preserved only when the learner sees meaningful headers and meaningful cells in the correct order. These are hard failures:

- `[object Object]` appears anywhere in the table;
- source rows are populated but learner-visible rows/cells are blank;
- a structured source table is flattened into prose;
- column ownership/order changes;
- validation checks only that `.nk-marrow-table` exists without checking its content.

The shared compatibility renderer is `tools/apply_marrow_structured_table_renderer_v1.py`. The browser sentinel is `tools/verify_marrow_structured_table_browser.py`, currently anchored to Anatomy Ch5 Q10 because that question exposed the regression.

For any batch containing a table, pre-commit and browser QA must verify table content, not merely table presence. A broken table blocks `FULLY_VERIFIED` even if the prose, takeaway, and rationales are otherwise good.

## Display-only micro-concision

The approved implementation may:
- suppress a short opening paragraph when it substantially duplicates the already-visible Key Takeaway;
- suppress dead “image/figure/flowchart below” boilerplate when no asset is rendered;
- suppress legacy source `Option A/B/C/D:` rationale paragraphs when the standardized distractor section replaces them.

It must **not** delete unique mechanism, timing, derivative, relationship, clinical nuance, table content, equations, or figure ownership.

## OCR and reconstruction policy

### Safe cleanup
A separate display layer may correct obvious extraction artifacts when the intended wording is directly recoverable from stored source context, table structure, options, answer key, or verified page evidence.

Safe examples:
- broken line joins;
- repeated OCR characters;
- obvious spacing/punctuation corruption;
- duplicated headers/footers;
- source option-label debris represented elsewhere.

### Reconstruction
Reconstruct missing educational content only when source evidence makes the result high confidence. Store:
- original raw fragment;
- reconstructed display content;
- evidence/provenance used;
- reconstruction status.

If defining list items, table cells, labels, or image-dependent facts are absent and cannot be recovered from source evidence, do **not** invent them. Keep a review flag and render the source-faithful remainder.

## Fine-tuning workflow

Current canonical deterministic inventory:
- `data/marrow/explanation_inventory_v1.json` accounts for all 2,711 IDs;
- `tools/inventory_marrow_explanations.py` regenerates it from canonical source bundles and verified augmentation;
- current canonical checkpoint: 576 enhanced-reference questions and 2,135 pending, subject to live regeneration after each verified batch.

1. **Inventory first**
   - enumerate all 2,711 IDs and review statuses;
   - separate clean source, OCR-cleanup candidates, source omissions, image-dependent items, tables, and reconstruction cases.

2. **Preserve raw; build augmentation**
   - keep imported bundles untouched;
   - create/extend versioned explanation augmentation keyed by stable Marrow ID;
   - store takeaway, optional displayText/structured blocks, selective emphasis, distractor rationales and provenance separately.

3. **Work in bounded chapter batches**
   - deterministic source order;
   - no all-bank monolithic rewrite;
   - each batch records IDs/counts/hashes and unresolved review items.

4. **Subject-aware quality**
   - Anatomy: preserve spatial/derivative/timing precision, table contents and labels.
   - Physiology: repair OCR without flattening mechanisms, graphs, equations or tables; preserve causal chains and normal-vs-abnormal contrasts.
   - Biochemistry: preserve pathways, enzyme/substrate/product ownership, molecular/clinical distinctions, cycles and table columns.

5. **Generate distractor rationales**
   - keys match exactly the three incorrect option letters;
   - concise and source/standard-fact consistent;
   - no rationale for the correct option in the wrong-options section;
   - no unsupported extra medical claims.

6. **Validation**
   - augmentation IDs map to existing Marrow IDs only;
   - no duplicates;
   - exactly three wrong-option rationales when applicable;
   - selective emphasis, not blanket bolding;
   - source tables preserved with valid headers/rows;
   - raw source unchanged;
   - unresolved omissions remain reviewable.

7. **Browser QA**
   - sample short/long explanations, tables, OCR-heavy questions, reconstructed questions and image-metadata questions;
   - verify Key Takeaway + Detailed explanation + Structured text + wrong-option section;
   - when a table exists, verify actual expected header/cell text and fail on `[object Object]` or blank populated-source rows;
   - verify fixed FSRS dock and Previous/Next remain intact;
   - compare mobile and tablet widths where presentation changed.

8. **Canonical reconciliation**
   - exact-head CI must pass on the short-lived batch branch;
   - verified work must be reconciled into `feature/marrow-canonical-full-current` before the explanation lane is released;
   - production remains untouched until explicit user approval.

## What not to do

- Do not rewrite raw JSONL/bundle source to make the UI prettier.
- Do not use generic summaries in place of source explanations.
- Do not shorten away source nuance.
- Do not convert every paragraph to bullets.
- Do not infer a diagram/table that is not recoverable.
- Do not defer a broken structured text table to image automation.
- Do not change Topics taxonomy while doing explanation rendering.
- Do not base new work on an old subject rollout branch.
- Do not promote production merely because CI/browser tests pass.

## Completion definition

A chapter/batch is explanation-fine-tuned only when:
- every intended question ID is accounted for;
- source text remains intact;
- display augmentation passes schema/ID/count checks;
- structured tables with source data render populated and correctly ordered;
- unresolved omissions/reconstruction items are listed explicitly;
- representative browser output is verified;
- no Practice/CBT/Review/FSRS/navigation regression is introduced;
- exact-head verification is green and the verified result is reconciled into canonical.
