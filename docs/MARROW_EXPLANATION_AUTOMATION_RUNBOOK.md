# MARROW EXPLANATION AUTOMATION RUNBOOK

> Purpose: authoritative operating manual for unattended ChatGPT Scheduled
> Tasks / Work agents that fine-tune Marrow ED8 explanations for Anatomy,
> Biochemistry, or Physiology.
>
> This is **not** a generic writing guide. It is a regulated implementation
> protocol designed to preserve medical accuracy, source ownership, branch
> integrity, regression safety, and resumability under bounded ChatGPT task/tool
> execution.
>
> Read this file completely before every run. Do not rely on a summary from a
> previous run.

---

## 0. Core objective

Improve learner-facing Marrow explanations to the approved NK QBank gold
standard while:

- keeping raw imported Marrow ED8 source immutable;
- preserving source question IDs, options, answer keys, tables, figures and
  provenance;
- correcting/reconstructing learner-facing content when PDF/JSON transcription
  is incomplete, garbled or medically misleading;
- keeping reconstruction auditable;
- producing exactly three useful wrong-option rationales for a four-option SBA;
- protecting the shared Practice / CBT / Review / FSRS / sync / module /
  analytics / navigation engines;
- ensuring one bad run cannot silently compound into later runs;
- leaving an exact, machine-readable handoff for the next scheduled run.

Quality has priority over quantity. Efficiency comes from bounded parallelism,
pre-audit, deterministic validation and checkpointing — never from lowering the
medical or regression standard.

---

## 1. Authority order — what every automation must read

Before any write, read the following from the **current repository state**.

### Mandatory repository documents

1. `AGENTS.md`
2. this file:
   `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md`
3. `docs/MARROW_EXPLANATION_FINE_TUNING.md`
4. `docs/MARROW_BANK_INTEGRATION.md`
5. `.project-memory/STATE.md`
6. `.project-memory/ROADMAP.md`
7. `.project-memory/DECISIONS.md`
8. `.project-memory/ARCHITECTURE.md`
9. `.project-memory/PRODUCT.md`
10. newest relevant section of `.project-memory/SESSION_LOG.md`

Do not use a stale chat summary in place of these files.

### Mandatory implementation files

Read enough of these to understand the current executable contract before
changing it:

- `tools/inventory_marrow_explanations.py`
- `tools/test_marrow_physio_explanation_rollout.py` when Physiology exists on
  the current lineage;
- the current Biochemistry rollout validator;
- any Anatomy explanation validator present on the current lineage;
- `tools/verify_marrow_bank_browser.py`
- `tools/apply_marrow_bank_pilot.py`
- `.github/workflows/engineering-gate.yml`
- `.github/workflows/build-apk.yml`

If a file named above has been renamed, discover the replacement from Git before
proceeding. Never assume old paths are still authoritative.

### Gold/reference augmentation files

Use existing verified augmentation as the style/contract reference:

- Anatomy:
  `data/marrow/explanation_gold_pilot.json`
- Physiology:
  `data/marrow/explanation_physio_pilot.zlib.b64.part*` plus verified
  `explanation_physio_ch*_v1.json` files
- Biochemistry:
  `data/marrow/explanation_biochem_gold_sample_v1.json` plus verified
  `explanation_biochem_ch*_v1.json` files

Do not copy phrases mechanically. Copy the **grammar and quality standard**.

---

## 2. Current source bundles

The current full Marrow ED8 source is stored as immutable sharded bundles:

- Anatomy:
  `data/marrow/anatomy_phase_a.zlib.b64.part*`
- Biochemistry:
  `data/marrow/biochemistry_phase_a.zlib.b64.part*`
- Physiology:
  `data/marrow/physiology_ch001_033.zlib.b64.part*`

Corresponding manifests must remain valid.

Current total imported scope:

- Anatomy: 819 questions / 48 topics
- Biochemistry: 543 / 26
- Physiology: 753 / 33
- Total: 2,115 questions

Never rewrite these bundles to improve learner-facing wording.

---

## 3. Platform constraint: ChatGPT Scheduled Tasks are bounded

As of 2026-09-09, OpenAI publicly documents plan/model/usage and active-task
limits for Scheduled Tasks, but does **not** publish a guaranteed wall-clock
runtime for one scheduled execution.

Therefore:

- do not design a run that requires "about one hour";
- do not rely on an assumed hidden timeout;
- do not spend the entire run polling GitHub Actions;
- do not attempt multiple independent content batches in one scheduled run;
- use the bounded workload rules below;
- checkpoint after every meaningful phase;
- allow the next recurrence to resume verification instead of forcing one run to
  finish everything.

The runbook's safe limits are deliberately based on **workload**, not minutes.

---

## 4. Per-automation inputs

Each scheduled automation should be configured with:

- `SUBJECT`: exactly one of
  - `Anatomy`
  - `Biochemistry`
  - `Physiology`
- `TARGET_WORKLOAD_SCORE`: default **16**
- `MAX_WORKLOAD_SCORE`: **20**
- `MAX_QUESTIONS_PER_NEW_BATCH`: **18**
- `BATCH_ID`: generated per new batch:
  `<subject>-<YYYYMMDD>-ch<chapter>-q<start>-<end>`

The automation must dynamically resolve:

- current latest verified explanation lineage;
- current unverified batch, if any;
- exact next source-order start for its subject;
- current inventory counts/fingerprint;
- current branch/PR/CI status.

Do not hardcode a chapter number permanently in the task prompt.

---

## 5. Global coordination rule for three subject automations

The three subject automations share global files such as:

- explanation inventory;
- browser regression script;
- project memory;
- stacked explanation lineage.

Therefore **new integration work must be serialized**, even if medical pre-audit
can be done independently.

### Before every write

1. Read `.project-memory/STATE.md`.
2. Determine whether it declares an unfinished/unverified explanation batch.
3. Resolve current Git branch/PR state.
4. Re-read current inventory fingerprint.
5. Immediately before the first mutation, check again that none of these changed.

### If another subject owns the current unfinished batch

Do **not** start a new batch.

Allowed actions:

- inspect/report the blocking state;
- if useful, pre-audit the next source chapter for the configured subject
  **without writing shared integration files**;
- stop cleanly.

### If this automation's subject owns the unfinished batch

Resume its stabilization from the exact recorded checkpoint.

Do not start another batch.

### If no unfinished batch exists

The configured subject may start its next source-order batch.

### Why this matters

Parallel subject writes can conflict in the global inventory, browser regression
script, project memory and stacked branch lineage. A successful medical content
file is not enough if shared state is based on an older fingerprint.

Schedules should still be staggered, but **staggering is not a lock**. Every run
must assume two tasks could overlap and perform the double-check above.

---

## 6. Gold-standard explanation grammar

Each normal four-option SBA should contain:

### A. Key Takeaway

- one meaningful high-yield discriminator;
- usually one compact sentence;
- medically useful;
- never merely "Option B is correct";
- never a vacuous "All of the above".

### B. Detailed learner-facing explanation

- medically correct;
- source-faithful in scope;
- clear causal/mechanistic sequence;
- normal prose unless the content is genuinely list-like;
- preserve equations, relationships, timelines and distinctions;
- preserve source tables as tables rather than flattening them;
- source-native figures remain source-owned;
- no flashy or verbose textbook rewrite.

### C. Selective emphasis

- 1–4 exam-relevant phrases;
- every emphasis phrase must occur **verbatim and case-sensitively** in
  `displayText`;
- emphasize discriminators, enzymes, receptors, timing, key relationships,
  equations, derivatives or defining contrasts;
- do not bold whole paragraphs.

### D. Why the other options are wrong

For a four-option single-best-answer question:

- exactly three rationales;
- keys must exactly match the three non-keyed source option letters;
- one concise exam discriminator per option;
- explain why the option is wrong or why it is not the best answer;
- if the source item itself is defective, say so explicitly in the relevant
  rationale rather than inventing a false distinction.

---

## 7. Reconstruction policy — learner correctness over known transcription damage

Raw Marrow source stays immutable.

Learner-facing augmentation should **not knowingly preserve an OCR defect,
missing text, corrupted symbol, wrong scale, misleading absolute statement or
internally inconsistent explanation** when the intended medical-school content
can be recovered with high confidence.

### Permitted reconstruction evidence

Use one or more of:

1. intact stem/options/source key;
2. source explanation/context;
3. verified source PDF page, table or figure when available;
4. standard, established MBBS / USMLE / NEET-PG / INI-CET level medical
   literature.

This is normal medical-school material. High-confidence standard reconstruction
is allowed and expected.

### Required reconstruction metadata

Any reconstructed augmentation must contain:

- `status`
- `sourceProblem`
- `reconstructedContent`
- `evidenceBasis`
- `reviewNote`

Allowed statuses:

- `resolved_reconstruction`
- `needs_manual_review`

### When to use `resolved_reconstruction`

Use only when the educational defect is actually recoverable with high
confidence.

Examples:

- OCR-corrupted Greek receptor symbols;
- corrupted Na-channel inactivation terminology;
- imprecise sarcomere scale/wording;
- standard receptor/tissue dependency replacing an over-broad source sentence.

### When to use `needs_manual_review`

Use when correct medical teaching can be provided but the original item remains
not fully recoverable.

Examples:

- missing numbered statement text;
- two physiologically false choices in an "except" question;
- a stored option that may itself be OCR-corrupted and creates a second correct
  or incorrect answer;
- missing image labels not recoverable with confidence.

### Critical rule

Correct physiology does **not** mean the original item is fully resolved.

Do not mark a damaged question `resolved_reconstruction` merely because the
learner-facing paragraph is good.

---

## 8. Subject-specific quality rules

### Anatomy

Protect:

- spatial relationships;
- origin/insertion/action/innervation ownership;
- arterial/venous/lymphatic drainage;
- embryologic derivatives and timing;
- foramina/contents;
- surface vs deep relations;
- histology structures;
- laterality;
- image/table labels.

Suggested unattended batch size:

- usually **8–12 questions**;
- up to **14** only if source is clean and low-risk.

Anatomy figure/spatial errors are easy to compound. Reduce batch size when
multiple image-dependent or reconstruction-heavy questions appear.

### Biochemistry

Protect:

- enzyme ↔ substrate ↔ product ownership;
- cofactors/vitamins;
- irreversible/regulatory steps;
- cellular compartment;
- pathway direction;
- fed/fasting state;
- deficiency/toxicity relationships;
- inheritance;
- metabolite patterns;
- molecular/clinical distinctions;
- table column ownership.

Suggested unattended batch size:

- usually **10–16 questions**;
- up to **18** only when clean.

### Physiology

Protect:

- causal mechanism order;
- graph axes and direction;
- equations and units;
- membrane currents/channel direction;
- receptor subtype;
- tissue-specific effects;
- feedback/feedforward logic;
- normal vs abnormal physiology;
- time relationships;
- "best available answer" vs literal biologic truth.

Suggested unattended batch size:

- usually **10–16 questions**;
- up to **18** only when clean.

---

## 9. Workload scoring — how to select a safe chunk

Do not select a chunk by question count alone.

For each candidate question, calculate:

### Base cost

- every ordinary clean SBA: **1 point**

### Add modifiers

- source table/equation/source review note: **+0.5**
- figure/image/graph dependent: **+1**
- obvious OCR/garbling: **+1**
- reconstruction candidate: **+2**
- matching/numbered-statement item with missing defining material: **+2**
- external standard-literature verification materially required: **+1**

A single question may have multiple modifiers.

### Target

- target workload score: **16**
- hard maximum workload score: **20**
- hard maximum questions in one new batch: **18**

### Chunk selection algorithm

1. Start at the exact next incomplete source-order question.
2. Keep questions contiguous.
3. Prefer finishing the current chapter if:
   - total questions <= 18; and
   - workload score <= 20.
4. Otherwise choose the largest contiguous block whose score is near 16 without
   exceeding 20.
5. Never skip difficult questions to cherry-pick easy ones.
6. Never cross into a second chapter merely to fill a quota.
7. If a single high-risk cluster already approaches the workload limit, process
   fewer questions.
8. If the remaining chapter tail is small, process the tail even if it is below
   the normal target.

Quality overrides the target count.

---

## 10. One-run state machine

Every scheduled run follows this order.

### PHASE 0 — Preflight

Read mandatory docs and live Git state.

Resolve:

- subject;
- latest verified checkpoint;
- unfinished batch if any;
- next source-order start;
- inventory fingerprint;
- branch/PR/CI state.

If state is internally contradictory, stop and report.

### PHASE 1 — Stabilize existing unfinished work first

If any unfinished explanation batch exists:

- do not author a new batch;
- resume its exact next validation/CI/memory phase;
- if another subject owns it, skip new integration.

### PHASE 2 — Select one bounded new batch

Only if the integration lane is clear.

Calculate workload score and choose one contiguous batch using Section 9.

### PHASE 3 — Source audit before authoring

For every question in the selected batch, determine:

- exact source ID;
- chapter;
- question number;
- stem/options;
- exact correct option;
- source explanation;
- source table/figure metadata;
- source review flags/notes;
- whether reconstruction is needed.

Do not draft rationales before knowing the actual source key.

### PHASE 4 — Author augmentation

Write only the subject/chapter augmentation file.

Do not mutate raw source bundles.

### PHASE 5 — Pre-commit validation

Before commit, validate:

- expected batch count;
- IDs exist in source;
- IDs belong to intended chapter;
- no duplicate/overlap with approved augmentation;
- takeaway non-empty;
- display text non-empty;
- emphasis count 1–4;
- each emphasis phrase occurs verbatim;
- exactly three rationales;
- rationale keys exactly equal non-keyed source option letters;
- reconstruction schema complete where used.

If this fails, fix only the relevant defect and rerun the check.

### PHASE 6 — Deterministic inventory

Regenerate the full 2,115-ID explanation inventory.

Verify:

- previous verified enhanced IDs remain enhanced;
- new batch count is exact;
- pending count decreases by the exact number of new unique IDs;
- raw source hashes remain unchanged;
- review-flag counts do not drift unexpectedly;
- fingerprint is deterministic.

Never hand-edit only the summary count without reproducing the fingerprint logic.

### PHASE 7 — Browser regression

Add **one representative regression per batch/chapter**.

Prefer:

- the most reconstruction-sensitive question;
- a graph/equation question when graph semantics matter;
- an OCR/source-defect question;
- a high-value mechanism question.

The browser test must verify:

- correct bank + subject + stable chapter identity;
- expected chapter question count;
- correct representative question opens;
- Key Takeaway;
- Detailed explanation;
- Structured text;
- Why the other options are wrong;
- key medical discriminator(s);
- exactly three `.nk-gold-wrong-row` rows.

Use stable IDs/attributes where possible.

### PHASE 8 — Bounded PR

Open one PR for the batch/chapter.

PR body must include:

- subject/chapter/range;
- exact question count;
- reconstruction list/statuses;
- new inventory counts/fingerprint;
- browser target;
- statement that raw source is unchanged;
- statement that production promotion is prohibited.

### PHASE 9 — Exact-head certification

Resolve PR current head SHA.

Only accept:

- Engineering Gate run for that exact SHA;
- full Android/PWA run for that exact SHA.

Required full-run gates include, where present:

- source product contract;
- explanation inventory validator;
- subject rollout validator;
- final JS syntax;
- generated product contract;
- CBT regression guardrails;
- offline PWA/FSRS assets;
- live Marrow browser regression;
- APK build;
- packaged APK/product contract;
- packaged image bytes;
- reproducibility manifest;
- preview deployment;
- production promotion skipped.

### PHASE 10 — Memory/handoff

Update project memory after meaningful progress.

See Section 17.

---

## 11. Do not burn a run polling CI

A scheduled ChatGPT task has bounded execution resources.

After launching CI:

- poll only enough to identify run IDs and obvious early failure;
- if CI is still running and the run is otherwise checkpointed, record:
  - exact head SHA;
  - Engineering run ID;
  - full-run ID;
  - current phase;
- stop cleanly;
- next recurrence resumes PHASE 1 and certifies/fixes the existing batch.

Do not sit in a long polling loop merely to finish within one invocation.

---

## 12. Failure containment — prevent compounding

### If source audit fails

Stop. Do not author.

### If augmentation validation fails

Fix only the detected batch issue.

Do not broaden scope.

### If deterministic inventory does not reproduce expected state

Stop.

Do not open the PR.

### If browser regression fails because of a selector/test bug

Diagnose whether product or test is wrong.

Fix the **smallest** test defect if the product is correct.

Do not change medical content to satisfy a brittle selector.

### If CI fails

Inspect the exact failed step/log.

Classify:

1. batch medical/content defect;
2. validator defect;
3. browser-test defect;
4. unrelated infrastructure failure;
5. project-memory contract failure.

Fix only the classified cause.

### Automatic repair limit

For the same exact failure class:

- maximum **2 bounded repair attempts** in one scheduled run.

If the same class fails again:

- stop;
- mark batch blocked;
- record the exact failure/run/log clue in memory;
- do not start another batch.

### Never "fix forward" by stacking more chapters

An unverified parent batch blocks later integration.

---

## 13. Exact-head rule — a major learned failure

Multiple Git mutations can create workflow runs on neighboring SHAs.

A green run on SHA A does not certify current PR head SHA B.

Always:

1. fetch PR;
2. read `head.sha`;
3. query runs for that SHA;
4. accept only matching Engineering + full build;
5. ignore/supersede earlier content-only or neighboring runs.

This rule is mandatory.

---

## 14. Browser-selector rule — another learned failure

Do not rely on fuzzy topic text when a stable identifier exists.

Observed failure:

- `Muscle Physiology I` also matched `Muscle Physiology II`;
- trying to append display count text still timed out because accessible-name
  composition was not guaranteed to equal contiguous DOM text.

Preferred pattern:

`button.nk-topic-row[onclick="window.QB.openChapter('7')"]`

Use actual stable chapter IDs/attributes from current markup.

Do not invent selectors without inspecting the current DOM-generating code.

---

## 15. Medical/source mistakes learned from the rollout

### Do not blindly preserve a source simplification

Examples encountered:

- EPP is a graded **depolarization**; a stored "except" item had two false
  choices.
- Wallerian degeneration begins with distal axonal degeneration even when
  "myelin degeneration" is the earliest offered answer.
- sympathetic smooth-muscle effects are receptor/tissue dependent, not
  universally excitatory or inhibitory.
- 2 μm is sarcomere-scale, not whole muscle-fiber length.
- corrupted Greek receptor/fiber symbols should be restored when standard
  mapping is clear.
- `DOPA` vs `dopamine` can create a second classification problem and should
  remain reviewable until the original option is confirmed.

### Do not pretend a damaged item is resolved

Good learner-facing physiology is not proof that missing source wording was
recovered.

### Do not invent numbered statements

If numbered statements are absent:

- reconstruct only the educational meaning supported by source explanation and
  standard literature;
- keep exact missing wording unclaimed;
- use `needs_manual_review` where appropriate.

### Do not change raw source keys

Raw source remains auditable.

Explain the correct medical distinction in augmentation/provenance.

---

## 16. Gold-standard efficiency lessons

### Safe parallelism

While chapter/batch N is in CI:

- pre-audit N+1;
- map source count;
- identify figure/reconstruction candidates;
- estimate workload score.

Do not commit N+1 until N is fully green.

### Reuse generic infrastructure

Do not create a new loader/renderer/validator for every chapter.

Extend subject-generic discovery and validators.

### One representative browser case is enough per bounded batch

Choose the hardest/highest-risk representative.

Do not add dozens of redundant end-to-end browser cases that make every run too
slow.

### Keep chapter/range ownership obvious

One augmentation file per bounded chapter/range is easier to audit, revert and
resume than a monolithic subject rewrite.

---

## 17. Mandatory memory updates

After any run that changes state, update the handoff so another scheduled task
can resume with no chat context.

### Always update

- `.project-memory/STATE.md`

Record:

- latest verified checkpoint;
- current unverified checkpoint;
- exact batch;
- exact commit/head;
- inventory state;
- PR/run IDs if known;
- reconstruction review items;
- exact next action.

### Update when roadmap state changes

- `.project-memory/ROADMAP.md`

### Append substantive runs

- `.project-memory/SESSION_LOG.md`

### Add only durable new principles

- `.project-memory/DECISIONS.md`

Do not add duplicate decisions every run.

### Runbook updates

If a new failure reveals a reusable lesson, update this automation runbook.

### Preserve project-memory verifier concepts

Do not casually rename/remove required handoff concepts.

The current memory verifier has historically required concepts including:

- build-verified;
- device-verified;
- accepted baseline;
- Known problems;
- Next step;
- Accepted product commit.

Before committing memory, inspect the current verifier and preserve its actual
requirements.

Use `[skip ci]` for documentation-only handoff commits when appropriate, but
record separately that the latest product-verified SHA may precede the doc-only
head.

---

## 18. Branch / PR conventions

Recommended new-batch branch:

`feature/marrow-explanation-rollout-<subject>-ch<NN>-current`

For a split chapter:

`feature/marrow-explanation-rollout-<subject>-ch<NN>-q<start>-<end>-current`

Recommended PR title:

`Refine Marrow <Subject> Chapter <N> explanations`

or, for split batches:

`Refine Marrow <Subject> Chapter <N> Q<start>–Q<end> explanations`

Base the new branch on the **latest verified current explanation lineage plus
required handoff/docs commits**, never an older main branch merely because it is
named `main`.

Resolve the actual current state from `STATE.md` + Git.

---

## 19. Production / merge safety

Default unattended automation behavior:

- do not promote Cloudflare production;
- do not redefine the accepted baseline;
- do not merge to production/main unless a separate explicit release instruction
  authorizes it;
- preview deployment is allowed;
- PR creation/update is allowed;
- stacked explanation branches are allowed;
- build/browser/APK success does not equal user device acceptance.

---

## 20. What not to touch during explanation automation

Do not change, unless necessary to fix a proven explanation regression:

- Practice engine;
- CBT engine;
- Review engine;
- FSRS scheduling semantics;
- sync;
- custom modules;
- analytics;
- navigation;
- Topics taxonomy;
- image-integration pipeline ownership;
- raw Marrow source bundles;
- PrepLadder source-PDF behavior;
- production promotion settings.

Do not redesign UI during explanation fine-tuning.

---

## 21. Regression checklist before a batch can be called verified

### Source ownership

- [ ] raw source hashes unchanged
- [ ] every new ID exists in source
- [ ] correct subject/chapter ownership
- [ ] source answer key preserved
- [ ] native tables/figures preserved

### Augmentation

- [ ] exact expected question count
- [ ] no duplicate IDs
- [ ] meaningful takeaway
- [ ] medically correct display text
- [ ] 1–4 valid verbatim emphasis anchors
- [ ] exactly three wrong-option rationales
- [ ] rationale letters exactly equal non-keyed options
- [ ] reconstruction provenance complete
- [ ] unresolved defects marked `needs_manual_review`

### Global inventory

- [ ] previous verified enhanced set preserved
- [ ] enhanced count increments exactly
- [ ] pending decrements exactly
- [ ] deterministic fingerprint reproduced
- [ ] no unexplained flag/hash drift

### Browser

- [ ] stable bank/subject/chapter navigation
- [ ] chapter count correct
- [ ] representative question correct
- [ ] Key Takeaway visible
- [ ] Detailed explanation visible
- [ ] Structured text visible
- [ ] wrong-options section visible
- [ ] exactly three wrong rows
- [ ] reconstruction discriminator visible where applicable
- [ ] source figures still render separately where applicable

### Full product

- [ ] Engineering Gate exact-head success
- [ ] full Android/PWA exact-head success
- [ ] generated product checks pass
- [ ] CBT regression guardrails pass
- [ ] offline assets pass
- [ ] APK/package checks pass
- [ ] reproducibility passes
- [ ] preview deployment passes
- [ ] production promotion skipped

---

## 22. Per-run reporting contract

At the end of every scheduled run, report compactly:

1. `SUBJECT`
2. `BATCH_ID`
3. what phase was found at startup
4. what was completed
5. exact question range/count
6. reconstruction statuses
7. inventory before/after if regenerated
8. branch/commit/PR
9. exact-head Engineering/full run IDs + status
10. whether production was skipped
11. exact next action
12. whether another subject automation is blocked by this unfinished batch

Never say "complete" if only content authoring is complete.

Use precise states:

- `PREAUDITED`
- `CONTENT_AUTHORED`
- `STATIC_VALIDATED`
- `PR_OPEN_CI_PENDING`
- `CI_FAILED_BLOCKED`
- `FULLY_VERIFIED`

---

## 23. Safe unattended batch examples

### Example A — clean 14-question Physiology chapter

If score <= 20:

- process all 14;
- source-key audit;
- inventory;
- browser;
- PR/CI;
- stop after CI launch if needed.

### Example B — 35-question figure-heavy Physiology chapter

Do not automatically take all 35 unattended.

Instead:

- choose contiguous 10–16-question block based on workload score;
- preserve chapter continuity;
- finish remaining chapter in later runs.

### Example C — Anatomy chapter with 10 questions, 5 figure-dependent

Figure modifiers may push score near/over 16.

Process fewer if needed.

### Example D — 18-question Biochemistry chapter with 2 OCR reconstructions

If score <= 20, whole chapter may be safe.

If reconstruction requires repeated literature/source-page investigation, split
before the high-risk cluster or end the batch at the workload ceiling.

---

## 24. Resume-first examples

### Existing content-authored batch, inventory not regenerated

Next run does **not** author more.

It starts at deterministic inventory + browser + PR.

### PR open, CI running

Next run checks exact head and CI.

It does not author more.

### CI failed on browser selector

Fix selector only if product content is correct.

Do not rewrite explanation text to satisfy a selector.

### Another subject has an unfinished batch

Skip new integration.

Report blocker and optionally pre-audit only.

---

## 25. Completion definition

A bounded explanation batch is **FULLY_VERIFIED** only when:

- source audit is complete;
- augmentation is committed;
- rationale/emphasis/reconstruction validation passes;
- deterministic global inventory is regenerated;
- representative live browser regression passes;
- Engineering Gate passes on exact current head;
- full Android/PWA workflow passes on the same exact head;
- APK/package/reproducibility/preview gates pass;
- production promotion is skipped;
- project memory records the final checkpoint and exact next start.

Anything less must be recorded as an intermediate state.

---

## 26. Final automation principle

The automation is not rewarded for maximizing the number of questions touched.

It is successful when each run leaves the repository in one of two states:

1. **strictly better and fully auditable**, with the current batch verified; or
2. **safely checkpointed**, with an exact next action and no ambiguous partial
   integration.

Never trade traceability for throughput.

