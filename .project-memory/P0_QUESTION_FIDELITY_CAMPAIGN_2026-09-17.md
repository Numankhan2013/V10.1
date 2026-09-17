# P0 Question Fidelity Repair Campaign — 2026-09-17

## Purpose

This is the active stabilization directive for NK QBank. It exists because user physical review exposed two learner-facing fidelity defects that must be resolved before unrelated cleanup, explanation tuning, image integration, percentage/community-statistics work, or new features resume.

This is **not a speed task**. Correctness and source fidelity matter more than throughput.

Work through the phases below **strictly one at a time**. For each phase: inspect, reproduce/understand, make the smallest safe change, run focused verification, document the result, mark the phase complete, update project memory if applicable, then move forward. Do not skip ahead because the cause appears obvious. Do not bundle unrelated changes.

## Primary defects

### A. Scientific notation / OCR placeholder corruption

Simple medical/scientific notation can still render incorrectly in learner-facing UI, including dark/black square placeholders where superscripts, subscripts, or ionic charges should appear. Representative forms include:

- Na⁺, K⁺, H⁺, Cl⁻
- Ca²⁺, Mg²⁺, Fe²⁺ / Fe³⁺, Cu²⁺, Zn²⁺, Mn²⁺
- NH₄⁺, HCO₃⁻, H₂PO₄⁻, HPO₄²⁻, PO₄³⁻, SO₄²⁻
- CO₂, O₂, pCO₂, pO₂, PaCO₂, PaO₂
- explicit exponents such as 10⁻⁶

Shared infrastructure already exists around `nkNormalizeScientificDisplayText` and `nkScientificMarkup`. Build on that architecture. Do not replace it casually and do not globally delete OCR placeholders.

### B. Matching / structured-table information loss

A user-reviewed PrepLadder Physiology question exposed a serious defect.

Authoritative source contains:

- `1. Aα` → `a. Preganglionic autonomic`
- `2. Aβ` → `b. Touch`
- `3. Aδ` → `c. Temperature`
- `4. B` → `d. Proprioception`

The app currently displays an incomplete fourth row with a missing counterpart / dash. The learner-facing app must never silently turn incomplete extraction into a plausible-looking incomplete source table.

## Non-negotiable principles

1. **Never manufacture completeness.** If a paired source table should contain four entries on each side but only four on one side and three usable entries on the other are safely recovered, do not render a fake fourth row with `—`. Resolve it from authoritative source or fail closed.
2. **Never guess scientific notation.** Repair only notation that is unambiguous from source/context. Ambiguous source loss must remain flagged for source-backed repair.
3. **Preserve the canonical answer contract.** Presentation repair must not casually alter canonical option text, option order, `correctOption`, stable question identity, history/FSRS mappings, or source records.
4. **Source fidelity beats visual prettiness.** An unavailable question is preferable to a clean-looking incorrect question.
5. **No unrelated work during this campaign.** Do not resume percentage/community statistics, unrelated UI work, image integration, explanation fine-tuning, or broad content cleanup until this fidelity gate is complete.
6. **Do not promote to production without explicit user approval.**

---

# Phase 0 — Orient yourself

Before changing code:

- Resolve the live canonical HEAD of `feature/marrow-canonical-full-current`.
- Read `.project-memory/STATE.md`.
- Read `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Inspect `tools/question_presentation_core.js`.
- Inspect `tools/verify_question_presentation_browser.py`.
- Inspect relevant generated PrepLadder question data and existing stable-ID/source-fingerprinted presentation overrides.
- Reconcile project memory against live Git/CI before trusting stale status text.

Do not edit yet.

Checkpoint required:

`PHASE 0 COMPLETE`

Report exact branch, exact starting commit, relevant architecture, likely files involved, and any uncertainties.

Only then continue.

---

# Phase 1 — Reproduce the reported matching question

Find the exact stable ID using distinctive text such as:

- `Preganglionic autonomic`
- `Aα`
- `Aβ`
- `Aδ`
- `Proprioception`

Inspect:

- raw canonical record
- source page metadata
- extracted question/options/supporting blocks
- normalized learner presentation
- authoritative source page if needed

Determine exactly where `4. B` and/or `d. Proprioception` is lost.

Classify the defect as one or more of:

- extraction/data loss
- presentation normalization loss
- matching parser loss
- duplicate-table trimming bug
- option-run selection bug
- another specifically demonstrated cause

Do not fix until the actual failure point is understood.

Checkpoint required:

`PHASE 1 COMPLETE`

Report stable ID, source page, raw structure, exact failure point, and repair category.

---

# Phase 2 — Fix the matching architecture safely

Repair the architecture rather than only patching the visible example.

Current behavior can permit structured matching tables with unequal list lengths and can later render missing cells as a dash. This is unsafe for genuine paired matching questions.

Introduce a scoped structural-integrity rule for genuine paired matching tables:

- corresponding groups must have compatible cardinality;
- expected label sequences must be coherent;
- meaningful cells must not silently disappear;
- duplicate/repeated source-table extraction must still be trimmed safely;
- incomplete reconstruction must fail closed instead of looking complete.

Do **not** blindly require equal group sizes for every structured-question architecture. The rule must be scoped to genuinely paired structures. If generic parsing cannot faithfully reconstruct a source record, use the existing stable-ID + source-fingerprint override architecture rather than weakening the parser.

For the reported nerve-fibre question, restore source-faithful presentation containing all four rows and both sides:

- `1 | Aα | a | Preganglionic autonomic`
- `2 | Aβ | b | Touch`
- `3 | Aδ | c | Temperature`
- `4 | B  | d | Proprioception`

Preserve all four canonical MCQ choices and the original `correctOption`.

Add a permanent regression for this exact question asserting:

- exact stable question ID opens;
- semantic table exists;
- both lists contain all four source-backed entries;
- `B` is present;
- `Proprioception` is present;
- no fabricated `—` cell exists;
- exactly four canonical answer choices remain;
- option order is unchanged;
- canonical `correctOption` still governs correctness.

Run focused unit/browser checks. Stop and inspect before proceeding.

Checkpoint required:

`PHASE 2 COMPLETE`

Report files changed, invariant added, exact question repair, regressions added, and focused test results.

Do not continue if this phase is not genuinely green.

---

# Phase 3 — Corpus-wide structured-question audit

Do not assume the reported question is unique.

Audit the learner corpus for structured-question families including:

- `match` / `matching`
- List I / List II
- Column A / Column B
- letter ↔ number mappings
- letter ↔ roman mappings
- row-selection tables
- structured combination-list questions
- stable-ID/source-backed overrides
- structured questions whose wording does not literally contain `match`

For every candidate classify:

- complete generic reconstruction
- source-backed override
- incomplete / unsafe
- false-positive ordinary prose

Detect at least:

- unequal paired-list cardinality
- empty cells
- placeholder `—` cells where source data should exist
- duplicate source tables
- truncated final rows
- missing answer choices
- option runs accidentally consumed as source-table data
- source-table cells accidentally exposed as clickable answer options

Fail closed when source structure is incomplete. Do not infer uncertain medical content merely to make a table render.

If repository audit/report conventions exist, produce machine-readable and human-readable output. Add representative regressions for every newly discovered failure class.

Checkpoint required:

`PHASE 3 COMPLETE`

Report counts for total structured candidates, generic-complete, override-backed, fail-closed, newly repaired, and unresolved/source-review-required. List unresolved stable IDs.

---

# Phase 4 — Scientific notation forensic audit

Audit before editing.

Search learner-visible content for suspicious notation including:

- `■`
- replacement-character glyphs
- malformed caret notation
- malformed ionic charge notation
- malformed subscript notation
- OCR-loss patterns adjacent to chemical symbols/formulae

Audit all relevant surfaces:

- stems
- options
- matching/structured-table cells
- native explanations
- key takeaways
- incorrect-option rationales
- review surfaces using alternate rendering paths

Classify occurrences as:

A. deterministically repairable
B. already safe/intentionally visible
C. ambiguous and must not be guessed

Pay special attention to Na⁺, K⁺, H⁺, Cl⁻, Ca²⁺, Mg²⁺, Fe²⁺/Fe³⁺, Cu²⁺, Zn²⁺, Mn²⁺, NH₄⁺, HCO₃⁻, H₂PO₄⁻, HPO₄²⁻, PO₄³⁻, SO₄²⁻, CO₂, O₂, pCO₂, pO₂, PaCO₂, PaO₂, and powers such as `10^-6` / `10^{-6}`.

Do not change code until the occurrence inventory and escaping gap are understood.

Checkpoint required:

`PHASE 4 COMPLETE`

Report suspicious occurrence counts, categories, representative examples, renderer paths involved, and the exact gap in current normalization/markup behavior.

---

# Phase 5 — Repair scientific notation safely

Extend the shared notation architecture conservatively.

Prefer semantic HTML `<sup>` / `<sub>` where appropriate. Preserve source semantics. Do not introduce a broad unconstrained regex that mutates ordinary prose or identifiers.

Every new normalization rule must be bounded and have positive/negative tests.

Ensure the renderer works in:

- question stems
- options
- table cells
- native explanations
- review rendering

Permanent regression coverage must include at minimum:

- Na⁺
- K⁺
- Cl⁻
- Ca²⁺
- Mg²⁺
- HCO₃⁻
- PO₄³⁻ or another multi-charge molecular ion
- pCO₂ / pO₂
- one explicit exponent such as `10^-6` / `10^{-6}`
- one negative regression proving ordinary text/numbers are not accidentally converted

No dark/block placeholder may remain in a deterministically repairable case. Ambiguous source loss must remain source-review-required instead of being guessed.

Checkpoint required:

`PHASE 5 COMPLETE`

Report normalization changes, rendering changes, regression fixtures, focused test output, and intentionally unresolved ambiguous cases.

---

# Phase 6 — Cross-surface learner regression

Verify the fixes through actual learner workflows at phone/mobile width comparable to the reported Android PWA screenshot.

Exercise where applicable:

- Practice
- Timed CBT
- Review Test / Review Solutions
- bookmark/wrong-question revisit if it uses a distinct renderer
- native Marrow enhanced explanations
- PrepLadder source-page/explanation path

Verify:

- matching tables remain complete;
- answer choices remain clickable and correct;
- table cells never become answer options;
- duplicated source-table text does not return;
- notation renders as semantic superscript/subscript;
- no dark-block placeholders remain in known-safe cases;
- long scientific notation does not break layout;
- ordinary prose questions remain unaffected.

Capture screenshots/artifacts for a compact representative set containing at least:

1. the reported nerve-fibre matching question;
2. the existing equilibrium-potential matching regression;
3. a structured row-selection question;
4. a question containing Mg²⁺ or Ca²⁺;
5. an acid-base question containing pCO₂/HCO₃⁻.

Checkpoint required:

`PHASE 6 COMPLETE`

Report screenshot/artifact paths and results.

---

# Phase 7 — Full product verification

Only after all focused phases pass, run the complete canonical verification required by current project memory/runbooks on the **exact final head**.

Include the relevant complete pipeline, including:

- Engineering Gate
- Android build
- PWA build
- browser regressions
- APK/package verification
- reproducibility/integrity checks
- existing Marrow/PrepLadder asset/data gates that are part of canonical CI

If anything fails: stop, diagnose, fix only the relevant issue, and rerun the required gate. Do not call the campaign complete with failed or stale CI.

Checkpoint required:

`PHASE 7 COMPLETE`

Report final commit SHA, workflow/run IDs, PASS/FAIL status of each, and preview deployment URL if generated.

---

# Phase 8 — Physical-review handoff

Do **not** declare `USER_ACCEPTED` yourself.

Final engineering status should remain something like:

`BUILD_VERIFIED / USER_REVIEW_PENDING`

Prepare a concise physical-review checklist with direct IDs/targets for:

- the originally broken nerve-fibre matching question;
- at least two other matching-table architectures;
- at least three notation examples.

The user makes final learner-facing acceptance.

Checkpoint required:

`PHASE 8 COMPLETE — BUILD_VERIFIED / USER_REVIEW_PENDING`

---

# Working method

Treat this as a checklist, not a race.

For every phase use:

**inspect → reproduce → form hypothesis → smallest architecture-safe fix → focused test → inspect result → document → continue**

Do not use:

**change many things → launch CI repeatedly → see what happens**

If a phase exposes a deeper problem, remain in that phase until the mechanism is understood. Do not answer complexity with broad refactoring.

There is no deadline pressure. Take enough time to understand each defect before moving to the next one.

# Definition of done

This P0 campaign is complete only when all of the following are true:

- the reported nerve-fibre table preserves all four source-backed rows;
- generic paired matching tables cannot silently display missing source cells;
- unsafe structured questions fail closed;
- corpus-wide structured-question audit is complete;
- deterministically recoverable scientific-notation placeholders are eliminated;
- scientific superscripts/subscripts render semantically;
- ambiguous OCR loss is not guessed;
- all relevant learner surfaces are tested;
- permanent regressions cover the reported defect classes;
- full canonical CI passes on the exact final head;
- project memory/handoff is updated;
- a preview is ready for physical user review;
- production remains unpromoted unless explicitly authorized.

## Immediate priority lock

Until this file is completed through Phase 8, do **not** resume:

- percentage/community-statistics work;
- new features;
- unrelated UI redesign;
- image integration;
- explanation fine-tuning;
- broad cleanup work unrelated to these P0 fidelity defects.

After Phase 8, stop and report back. Do not automatically begin the next project lane.