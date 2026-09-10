# Marrow explanation fine-tuning runbook

> Status: **next content-quality phase; do not execute until explicitly asked**.
> For unattended explanation automations, first read the complete shared
> `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md` from authoritative `main`.
> Read with `docs/MARROW_BANK_INTEGRATION.md` and the approved 142-question
> explanation augmentation already in the repository.

## Goal

Fine-tune the learner-facing explanations for the full Marrow bank while keeping
the imported ED8 source transcription auditable and unchanged.

Current imported scope:
- Anatomy: 898 questions / 48 topics.
- Biochemistry: 543 / 26.
- Physiology: 1,014 / 33.
- Total: 2,455 questions.

The current 142-question enhanced subset (62 Anatomy + 80 Physiology) is the
reference grammar. It already establishes the desired hierarchy, selective
bolding, source-table handling and concise **Why the other options are wrong**
section.

The user's physical review confirms the question integration works. The
Biochemistry screenshot also shows the next-quality problem clearly:
source-faithful structured text may still contain raw OCR/typing debris and poor
sentence flow. Clean that at the **display/augmentation layer**, not by
overwriting the imported source record.

## Non-negotiable source rules

- Imported Marrow source text remains immutable and auditable.
- Never silently paraphrase away unique medical meaning.
- Never invent a missing list, table, diagram label, mechanism or fact.
- Existing source tables stay tables.
- Figure/image metadata stays preserved even if binaries are deferred.
- Source omissions/uncertain reconstructions stay flagged until source evidence
  resolves them.
- Resolved reconstructions keep internal provenance.
- PrepLadder source-PDF renderers are unrelated and must not be changed here.

## Approved learner-facing grammar

### 1. Key Takeaway
- one high-yield discriminator, usually one compact sentence;
- source-derived/reviewed;
- never use a vacuous answer such as “All of the above” when a meaningful source
  explanation exists.

### 2. Detailed Explanation — Structured text
- readable paragraphs with semantic hierarchy;
- selective bolding of exam-relevant discriminators, timing, pathways,
  derivatives, definitions and contrasts;
- structured lists only when the source is genuinely list-like;
- real HTML tables when table data exists;
- no forced bulletization of normal prose.

### 3. Why the other options are wrong
- exactly three rationales for a four-option single-best-answer question;
- one concise exam discriminator per incorrect option;
- explain what makes that option wrong, not a mini textbook;
- rationales remain separate generated augmentation, never original Marrow text.

### 4. FSRS recall dock
- remains fixed/floating in the session footer above Previous/Next;
- explanation work must not move it into document flow or alter scheduler semantics.

## Display-only micro-concision

The approved Anatomy implementation may:
- suppress a short opening paragraph when it substantially duplicates the
  already-visible Key Takeaway;
- suppress dead “image/figure/flowchart below” boilerplate when no asset is
  rendered;
- suppress legacy source `Option A/B/C/D:` rationale paragraphs when the
  standardized distractor section replaces them.

It must **not** delete unique mechanism, timing, derivative, relationship or
clinical nuance.

## OCR and reconstruction policy

### Safe cleanup
A separate display layer may correct obvious extraction artifacts when the
intended wording is directly recoverable from stored source context, table
structure, options, answer key, or verified page evidence.

Safe examples:
- broken line joins;
- repeated OCR characters;
- obvious spacing/punctuation corruption;
- duplicated headers/footers;
- source option-label debris represented elsewhere.

### Reconstruction
Reconstruct missing educational content only when source evidence makes the
result high confidence. Store:
- original raw fragment;
- reconstructed display content;
- evidence/provenance used;
- reconstruction status.

The existing resolved Anatomy cases are the pattern:
`ANAT_CH02_Q010`, `ANAT_CH03_Q004`, `ANAT_CH04_Q013`.

If defining list items, table cells, labels, or image-dependent facts are absent
and cannot be recovered from source evidence, do **not** invent them. Keep a
review flag and render the source-faithful remainder.

## Fine-tuning workflow

Current deterministic inventory:
- `data/marrow/explanation_inventory_v1.json` accounts for all 2,455 IDs without
  copying source explanation text into the inventory;
- `tools/inventory_marrow_explanations.py` regenerates it from hash-verified
  source bundles and the approved augmentation subsets;
- the inventory records 142 enhanced references and 1,973 pending questions and
  identifies the 20-question Biochemistry gold-sample review set.

1. **Inventory first**
   - enumerate all 2,455 IDs and review statuses;
   - separate clean source, OCR-cleanup candidates, source omissions,
     image-dependent items, tables, and reconstruction cases.

2. **Preserve raw; build augmentation**
   - keep imported bundles untouched;
   - create/extend versioned explanation augmentation keyed by stable Marrow ID;
   - store takeaway, optional displayText/structured blocks, selective emphasis,
     distractor rationales and provenance separately.

3. **Work in bounded chapter batches**
   - deterministic chapter order;
   - no all-bank monolithic rewrite;
   - each batch records IDs/counts/hashes and unresolved review items.

4. **Subject-aware quality**
   - Anatomy: preserve spatial/derivative/timing precision and tables.
   - Physiology: repair OCR without flattening mechanisms, graphs or equations;
     preserve causal chains and normal-vs-abnormal contrasts.
   - Biochemistry: preserve pathways, enzyme/substrate/product ownership,
     molecular/clinical distinctions, cycles and table columns. The raw-text
     garbling seen in the PWA is a priority cleanup class.

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
   - source tables preserved;
   - raw source unchanged;
   - unresolved omissions remain reviewable.

7. **Browser QA**
   - sample short/long explanations, tables, OCR-heavy questions,
     reconstructed questions and image-metadata questions;
   - verify Key Takeaway + Detailed explanation + Structured text +
     wrong-option section;
   - verify fixed FSRS dock and Previous/Next remain intact;
   - compare mobile and tablet widths.

8. **User visual approval before broad presentation rollout**
   - existing Anatomy/Physiology enhanced subset is the reference;
   - for Biochemistry, review a representative small gold sample before applying
     a new OCR/display grammar across hundreds of questions.

## What not to do

- Do not rewrite raw JSONL bundles to make the UI prettier.
- Do not use generic summaries in place of source explanations.
- Do not shorten away source nuance.
- Do not convert every paragraph to bullets.
- Do not infer a diagram/table that is not recoverable.
- Do not change Topics taxonomy while doing explanation rendering.
- Do not promote production merely because CI/browser tests pass.

## Completion definition

A chapter is explanation-fine-tuned only when:
- every question ID in the chapter is accounted for;
- source text remains intact;
- display augmentation passes schema/ID/count checks;
- unresolved omissions/reconstruction items are listed explicitly;
- representative browser output is reviewed;
- no Practice/CBT/Review/FSRS/navigation regression is introduced.
