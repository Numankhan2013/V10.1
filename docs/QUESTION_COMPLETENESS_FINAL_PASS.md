# Question completeness final pass

## Scope and current evidence

The final pass restores question-essential lists, tables, charts and text without a medical rewrite of the whole bank. On 2026-09-30 the existing structural audit scanned all 5,397 question IDs and returned 220 source-review candidates (101 Marrow, 119 PrepLadder). These are suspected cases, not confirmed defects. Joining all 36 Marrow manual-review/source-omission flags adds six otherwise missed records: the initial queue contains 226 IDs (107 Marrow, 119 PrepLadder). Of these, 36 receive first priority. Previous `pass` status is not sufficient evidence of completeness.

Reproduce the inexpensive inventory:

```sh
python3 tools/audit_question_structure.py
python3 tools/queue_question_completeness.py
```

Reports are in ignored `build/question-fidelity/`; review decisions belong in the versioned `docs/question-completeness/` evidence files. The queue generator never changes learner content. The image coverage ledger accompanies each Marrow record; a released image alone does not establish that all required rows/labels are present.

## Parallel review and repair

1. Split the queue into disjoint stable-ID batches. Review existing manual/source-omission flags first, then combination choices, row-selection choices, matching pairs and flattened or truncated structures. Group source reads by subject and page to avoid repeated PDF work. Reviewers own separate evidence files; one primary writer integrates product changes.
2. Compare source text and page layout against current presentation, including question-owned images and continuation pages. Use rendered pages whenever extraction leaves uncertainty about labels, rows, cells or ownership. Explicitly record whether the evidence is text-only or visually inspected.
3. Use an existing generic parser where it reproduces all source cells. Otherwise add the smallest stable-ID/source-fingerprinted presentation override. If the source table is visible but transcription remains uncertain, a readable source crop is a valid recovery path; retain all headers, labels and rows and keep it with the question before answering.
4. The user explicitly authorized contextual reconstruction on 2026-09-30. Recover unclear characters or cells using the visible source, question constraints, choices, explanation and corroborating same-source material. Record the inferred fields, supporting constraints and plausible alternatives. Confidence must be justified by evidence, not by a model's self-assigned percentage. Preserve original imported data and distinguish reconstruction from exact transcription in the review ledger. If different plausible readings change the answer, escalate that item rather than silently selecting one.
5. When required content is absent from the source, record `SOURCE_OMISSION`. Anatomy `marrow__ANAT_CH62_Q006` is the concrete example: source pages 1188–1189 omit items 1–5. Combination choices cannot uniquely determine the absent list. Find corroborating original material before restoring it. A confirmed unusable question should show an explicit incomplete-source state and should not accept a scored answer; this requires a targeted, evidence-backed product change, not blanket disabling of heuristic candidates.

## Evidence and outcomes

Each reviewed ID needs its source file/page/hash, canonical fingerprint, review method, observed essential content, outcome, and exact repair if applicable. Outcomes: `COMPLETE`, `FALSE_POSITIVE`, `VISUAL_OWNED_COMPLETE`, `EXACT_SOURCE_REPAIR`, `CONTEXTUAL_RECONSTRUCTION`, `SOURCE_OMISSION`, or `UNRESOLVED`. Unresolved items remain visible in the ledger and are not counted as validated. Preserve canonical choices and answer indexes. Two explicit source-key repairs restore a display key where the immutable raw key was null: physiology-23-38 and physiology-33-33 retain all five choices and use source-confirmed option A. This bounded exception is tested by the compiler and runtime scoring contract.

## Prevent recurrence

Add question-essential-content checks alongside the existing answer-choice validity contract: combination choices need their referenced statement labels; row choices need the complete selectable rows; matching choices need the mapped labels on both sides; question-dependent figures need released question-owned visuals. These checks should use reviewed structured metadata where possible. Missing a semantic HTML table is not itself a failure: ordinary lists and complete source images are valid.

Use heuristics only to open review cases. Fail closed only for demonstrated missing required information or an explicit reviewed completeness contract. Include previously uncertain OCR/normalization flags in future inventories, and check explanation tables separately where they carry information essential to interpreting the question. A structural scan cannot detect every unflagged OCR error; a small stratified sample of unflagged records checks that blind spot. Expand review only when that sample exposes a new repeatable failure family.

## Final dispositions and integrated changes — 2026-09-30

The 226 initial candidates plus 28 supplemental IDs have all received evidence-backed dispositions. Of 254 unique source-reviewed questions, 74 require contextual reconstruction and 15 exact source repair: 89 repairs comprising 81 text/table/notation/key changes and eight native question-image integrations. Another 132 are already complete (53 ordinary/false positives and 79 owned-visual cases). The remaining 33 have underdetermined source omissions and are gated against scored answers. This includes Anatomy `marrow__ANAT_CH62_Q006`: its omitted five-item list cannot be uniquely recovered from combination choices.

A final inexpensive screen for explicit question-role visual dependencies caught cases outside the original structural queue. Source-described observations can replace absent visuals when the solution supplies a specific clue without revealing the answer: reddish-brown tooth discoloration and a precisely located chest surface-marking line are examples. These are recorded as contextual textual recoveries; missing original images/markers remain archival evidence. Whole omitted lists with nonunique alternatives remain gated.

Regenerated Marrow image coverage after the final two native owners is 1,502 references: 1,421 released, 79 invalid and two archival holds, with zero unresolved cues; runtime release contains 1,486 bindings across 1,306 assets for 1,128 question owners. Reference coverage, runtime bindings, unique assets and question owners count different units and must not be conflated.

## Pinned integration architecture

`docs/question-completeness/` preserves individual source-review evidence. The accepted ledger `data/question_completeness_reviews_v1.json` pins immutable question fingerprints, source PDF hashes/pages and exact display contracts. `tools/build_question_completeness_reviews.py` verifies those pins and compiles contracts into the shared `tools/question_presentation_core.js`; it does not modify raw imports or generate PDFs. Runtime presentation and interaction use those bounded contracts across banks, including fail-closed behavior on drift and scored-answer gates for demonstrated omissions. The compiled display ledger contains 114 entries. Source images use the existing native-stream registry and ownership architecture. Anatomy45Q23 receives its source-native diagram; Physiology37Q9 receives native JPEG object1775 (720×718) with complete axes and exercise/sleep labels. Its existing explanation PNG remains explanation-owned because it included clipped neighboring prose; it is not reused as the question image.

Ordinary combined builds preserve PDF generation/package checks but skip optional archival source-region review rendering. Manual workflow input `render_review_regions` enables that evidence regeneration when needed, avoiding roughly 1 GB of redundant review sheets during ordinary builds. Source-only review/compiler checks remain available locally; full generated/browser/APK verification belongs to Ubuntu CI.

## Verification and release

Source tests pass for all 81 display repairs and 33 omission gates across four input variants. The final local pass completed all 52 checks; final combined Android/PWA/browser/package CI remains pending. The queue now scans whole-bank structure, glyphs and explicit missing question visuals using actual runtime roles, merges review evidence and supports `--require-reviewed`: CI fails on any new unreviewed candidate and publishes a small report. The current rerun contains 195 remaining heuristic candidates, all reviewed, with zero unreviewed candidates. Prior image checkpoint `7f326e61` passed Engineering run `36695041130`; its full run `36695040994` failed on the ambiguous Muscle Physiology I browser locator, which also matched II. The selector is now fixed to select the chapter exactly. That failed run does not establish final build verification.

The primary writer will certify all repairs together in one combined preview build, checking representative repaired questions on phone and tablet, meaningful table cells, pre-answer visual ownership, unchanged choices, source-confirmed keys, omission gates, image loading and zoom. Production is not promoted. Physical-device verification and user acceptance remain separate from CI.

Completion of this bounded pass means all 254 identified cases have an explicit disposition, accepted repairs are integrated, and source omissions have deliberate handling. It does not mean all 5,397 questions received manual source or scientific validation. Continue inexpensive missing-visual dependency and uncertain-OCR scans; use heuristics to open review cases rather than disabling unreviewed questions. Expand source review when new repeatable failure families appear.
