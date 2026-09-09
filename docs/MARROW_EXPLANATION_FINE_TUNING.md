# Marrow explanation fine-tuning runbook

> Status: **active chapter-by-chapter content-quality phase**.
> Read with `docs/MARROW_BANK_INTEGRATION.md` and the approved 142-question
> explanation augmentation already in the repository.
> For unattended ChatGPT Scheduled Tasks, also read the complete
> `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md` before every run.

## Goal

Fine-tune the learner-facing explanations for the full Marrow bank while keeping
the imported ED8 source transcription auditable and unchanged.

Current imported scope:
- Anatomy: 819 questions / 48 topics.
- Biochemistry: 543 / 26.
- Physiology: 753 / 33.
- Total: 2,115 questions.

The original 142-question enhanced subset (62 Anatomy + 80 Physiology), plus
its user-approved 20-question Biochemistry sample, is the reference grammar. It already establishes the desired hierarchy, selective
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
- Never invent unsupported content. High-confidence reconstruction from verified source evidence and/or standard medical literature is explicitly allowed and should be provenance-marked.
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
Reconstruction is **expected** when the imported PDF/JSON transcription is
incomplete, garbled, internally inconsistent, or has already been flagged for
review and the intended undergraduate medical content can be recovered with
high confidence.

Permitted evidence is broader than the damaged transcription itself:
- intact source stem/options/answer key and nearby source context;
- verified source-PDF page/figure/table when available;
- standard, well-established medical-school literature and consensus physiology,
  anatomy or biochemistry used for MBBS / USMLE / NEET-PG / INI-CET level facts.

Do not leave learner-facing content knowingly wrong merely because the raw
transcription is defective. Correct/reconstruct the **augmentation layer** while
leaving raw imported source immutable.

Every reconstruction must remain auditable. Store, as applicable:
- original raw fragment or precise source problem;
- reconstructed learner-facing content;
- evidence/provenance basis (for example source page, standard-literature
  principle, or both);
- reconstruction status such as `resolved_reconstruction` or
  `needs_manual_review`;
- a concise internal note explaining what changed and why.

The existing resolved Anatomy cases are the pattern:
`ANAT_CH02_Q010`, `ANAT_CH03_Q004`, `ANAT_CH04_Q013`.

If a defining image label, list item, table cell or other fact still cannot be
recovered confidently after source inspection **and** standard-literature
verification, do not guess. Keep the uncertainty explicit and leave it
reviewable.

## Fine-tuning workflow

Current deterministic inventory / resume state:
- `data/marrow/explanation_inventory_v1.json` accounts for all 2,115 IDs without
  copying source explanation text into the inventory;
- `tools/inventory_marrow_explanations.py` regenerates it from hash-verified
  source bundles and all approved augmentation subsets;
- latest **verified** inventory after Physiology Chapter 8:
  **512 enhanced / 1,603 pending**;
- Biochemistry Chapters **1–11** are complete;
- Physiology Chapters **1–4** retain the approved 80-question pilot;
- Physiology Chapters **5–8** are fully explanation-refined and exact-head
  CI/browser/APK/package verified;
- latest verified Physiology checkpoint is Chapter 8 / PR #27,
  Engineering Gate 266 + full Android/PWA run 561;
- Physiology Chapter 9 — **Synapse and Junctional Transmission** has **27/27**
  augmentation records authored at content checkpoint `9c7cf3f`, but remains
  **unverified**;
- exact Chapter 9 resume sequence is source-key/distractor/emphasis/
  reconstruction audit → deterministic inventory regeneration → stable-ID
  browser regression → bounded PR → exact-head Engineering + full Android/PWA
  certification → only then Chapter 10.

1. **Inventory first**
   - enumerate all 2,115 IDs and review statuses;
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


## Operational lessons from the Physiology rollout

These rules came from actual Chapters 5–9 failures and should be treated as part
of the workflow, not optional polish.

### 1. Audit/author/validate before commit
For every chapter:
1. inspect source count and question IDs;
2. identify figure-heavy items, source notes and reconstruction candidates;
3. author learner-facing augmentation;
4. validate 1–4 emphasis anchors **verbatim and case-sensitively**;
5. validate exactly three rationales mapped to the non-keyed options;
6. validate reconstruction metadata/status;
7. commit only after those checks pass.

Several chapters caught only capitalization/phrase mismatches in emphasis. Do not
rewrite medically correct content to fix an emphasis-anchor failure; fix the
anchor.

### 2. Source-key audit is mandatory
Do not rely on remembered or drafted correct-option letters. Compare every
augmentation record with the actual source record and verify that rationales
cover exactly the three non-keyed option letters.

A source key can remain immutable while the learner-facing explanation clarifies
that it is merely the best available option or that the item itself is defective.

### 3. Reconstruction is bounded by recoverability
Use standard established medical literature when the transcription is wrong or
incomplete, but keep provenance.

- `resolved_reconstruction`: the intended educational defect is recoverable
  with high confidence.
- `needs_manual_review`: correct physiology can be taught, but exact missing
  source wording/options or item validity still cannot be fully recovered.

Missing numbered statements should be reconstructed only to the educational
meaning supported by source explanation/standard literature. Never invent their
verbatim wording.

### 4. Regenerate inventory deterministically
After a chapter passes the content audit, regenerate the full 2,115-ID inventory
and fingerprint. Do not hand-wave counts. The inventory is part of the chapter's
certification contract.

### 5. Browser tests should use stable identity
Avoid fuzzy topic substring selectors. Chapter 7 demonstrated that
`Muscle Physiology I` also matches `Muscle Physiology II`, and display-text
workarounds can still be structurally brittle.

Prefer stable chapter identity already present in the DOM, for example:
`button.nk-topic-row[onclick="window.QB.openChapter('7')"]`.

Choose one representative browser regression per chapter, preferably the item
that most strongly exercises reconstruction or explanation-quality behavior.

### 6. Exact-head CI only
Multiple commits can produce neighboring workflow runs. Only certify:
- the PR's exact current head SHA;
- the Engineering Gate run for that SHA;
- the full Android/PWA run for that SHA.

Earlier failed/content-only runs are superseded only when a later exact-head run
passes. A green neighboring SHA is never sufficient.

### 7. Safe parallelism for speed
Quality-first speed-up:
- while chapter N exact-head CI runs, pre-audit chapter N+1;
- map its source count, figure items, ambiguities and likely reconstruction cases;
- do **not** commit N+1 until N is fully green;
- keep one bounded PR per chapter.

This safely allowed Chapters 7 (35 questions) and 8 (14 questions) to be
completed in the same session without weakening browser/APK/package gates.

### 8. Do not confuse generated-app verification with production acceptance
Engineering/browser/APK/package success means build-verified. It is still not
device-verified or an accepted production baseline unless the user explicitly
promotes/accepts it.


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
