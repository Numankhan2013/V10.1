# Matching Table Architecture Handoff — 2026-09-14

## Why this work was reopened

User physical preview review showed that the shared matching/list renderer was only fixing a subset of PrepLadder matching questions. `physiology-9-6` rendered as a semantic List I / List II table, but `physiology-9-17` (“Match the ion with its equilibrium potential…”) still exposed duplicated/interleaved source-table text in the learner stem.

This was not a one-question manual patch. The existing shared runtime architecture in `tools/question_presentation_core.js` was real, but its matching-intent detector was brittle: it only admitted `match` prompts followed by a hard-coded vocabulary such as `following`, `column`, `pairs`, `types`, etc. Valid variants such as `Match the ion…`, `Match each…`, and other source wording never reached the structural table parser.

## Corpus audit

Audit of the generated PrepLadder artifact found 63 questions containing `match` / `matching`. The prior build rendered 39 semantic matching/list tables. Several missed questions already had enough structure for the existing parser; the detector alone blocked them. The audit also found parser limitations around duplicated extracted table blocks, A–F source labels, `Column A / Column B` prose references, bare `a…d ↔ i…iv` notation, and label-only source groups.

The generalized architecture increased semantic table renderings from 39 to 53 while preserving structural gating so ordinary prose such as “injured during a soccer match” is not converted into a table.

## Generic architecture repair

Canonical implementation lineage:

- `d9dd3271d8375bab3d1f6c4c1fa77e67d8d988ab` — generalized shared matching-table architecture.
- `c87ea82fd60b7fa5c181f3c58449b54968bc1111` — expanded corpus/unit regressions.
- `54e0f97318abd3eb4d3d2a83f4b2587a8226ac53` — browser regression for alternate matching prompts, including the user-reported equilibrium-potential question.
- `f0471f5b494c50e36bf7e3952be90a33ba45dea1` — source-stable final regression contract.

The shared renderer now accepts general `match` / `matching` wording but renders only when structural evidence is present; trims repeated source-table blocks; supports A–H and roman i–viii labels; ignores Column/List prose headers as row labels; supports bare letter↔roman notation; and preserves source fidelity rather than fabricating missing cells.

## Exact ion regression

`physiology-9-17` is explicitly exercised in the generated PWA browser regression. It must show List I / List II with Sodium, Chloride, Potassium, Calcium and -70, +63, +132, -90; expose exactly four canonical answer choices; and show the duplicated `Ion Equilibrium Potential (mV)` source block only once.

The generic repair was verified at `f0471f5b494c50e36bf7e3952be90a33ba45dea1`: Engineering `34837009703` PASS and full Android/PWA/browser/APK/package run `34837009688` PASS. Production promotion was skipped.

## Source-backed residual matching repairs

Some genuine matching questions do not contain enough text structure for a safe generic parser because one side is image-owned or extraction-flattened. They must not be left as raw prose and must not be guessed. Commit `d111b7c6a4efcbdc09c15354072973b78fee35b2` added source-fingerprinted presentation overrides for the previously listed residuals:

- `26-13`
- `physiology-10-10`
- `physiology-36-7`
- `anatomy-3-12`
- `anatomy-14-3`
- `anatomy-29-16`
- `anatomy-29-33`
- `anatomy-30-4`

These are no longer “unrepaired residuals.” They use explicit source-backed presentation data while leaving the canonical question/options/correct-answer records unchanged. Future structurally incomplete matching questions should follow the same rule: generic parser first, then source-backed targeted reform if needed.

Ordinary non-table uses of the word “match” such as `physiology-32-23`, `anatomy-22-20`, and `anatomy-29-24` must remain ordinary MCQs/prose.

## Structured row-selection family

User review then exposed a separate family that is not phrased as a matching question at all: `physiology-9-22`, an axonal-transport question whose source contains a four-column table and whose choices are only `1 / 2 / 3 / 4`. Extraction had flattened and duplicated the source table into the stem.

Commit `5352eb415e96834f3514139951a17ef7da3f368a` adds a reusable multi-column override-grid path and a source-fingerprinted reform for `physiology-9-22`. Learner presentation is now:

- prompt: “Which of the following statements accurately describes the type, direction and mediators of axonal transport?”
- columns: **Statement / Type / Direction / Mediator**;
- rows preserved from source:
  - 1 | Anterograde | Cell body to axon terminal | Dynein
  - 2 | Anterograde | Axon terminal to cell body | Kinesin
  - 3 | Retrograde | Axon terminal to cell body | Dynein
  - 4 | Retrograde | Cell body to axon terminal | Kinesin
- answer choices remain exactly `1 / 2 / 3 / 4`;
- canonical `correctOption` remains `3`;
- raw duplicated source rows do not appear in the learner stem.

The browser regression now explicitly opens `physiology-9-22`, verifies all four headers and source cells, asserts no duplicated row block, confirms the four canonical row-number choices, and confirms option 3 remains the correct answer.

## Current verification

Exact product checkpoint `5352eb415e96834f3514139951a17ef7da3f368a`:

- Engineering Gate `34855852205`: **PASS**.
- Full Android/PWA/browser/APK/package run `34855852211`: **PASS**.
- PrepLadder question-presentation browser regression: **PASS**, covering the normal matching table, the equilibrium-potential alternate wording, the new axonal-transport row-selection table, the combination-list case, and fail-closed incomplete choices.
- Continue Practice browser regression: **PASS**.
- APK build/package/reproducibility/Marrow asset checks: **PASS**.
- PWA preview deployment: **PASS**.
- Production promotion: **SKIPPED**.

Status is **BUILD_VERIFIED / USER_REVIEW_PENDING**. The ion question has been physically confirmed by the user. The new axonal-transport row-table and the source-backed residual matching overrides still need user preview review before being called accepted.

## Rule for future malformed structured questions

Do not limit this cleanup to literal “Match…” wording. If a learner-facing stem clearly contains a duplicated or flattened source table/list and the question asks the learner to select a row, combination, label mapping, or structured statement, first attempt a safe structural parser. If that cannot reconstruct the source faithfully, inspect the authoritative source and add a stable-ID/source-fingerprinted presentation override. Never rewrite the canonical answer contract merely to make the UI prettier, and never leave a clearly recoverable table as unreadable flattened prose.
