# Matching Table Architecture Handoff — 2026-09-14

## Why this work was reopened

User physical preview review showed that the shared matching/list renderer was only fixing a subset of PrepLadder matching questions. `physiology-9-6` rendered as a semantic List I / List II table, but `physiology-9-17` (“Match the ion with its equilibrium potential…”) still exposed duplicated/interleaved source-table text in the learner stem.

This was not a one-question manual patch. The existing shared runtime architecture in `tools/question_presentation_core.js` was real, but its matching-intent detector was brittle: it only admitted `match` prompts followed by a hard-coded vocabulary such as `following`, `column`, `pairs`, `types`, etc. Valid variants such as `Match the ion…`, `Match each…`, and other source wording never reached the structural table parser.

## Corpus audit

Audit of the generated PrepLadder artifact found 63 questions containing `match` / `matching`. The prior build rendered 39 semantic matching/list tables. Several missed questions already had enough structure for the existing parser; the detector alone blocked them. The audit also found parser limitations around duplicated extracted table blocks, A–F source labels, `Column A / Column B` prose references, bare `a…d ↔ i…iv` notation, and label-only source groups.

The generalized architecture increases semantic table renderings in the built artifact from 39 to 53 while preserving structural gating so ordinary prose such as “injured during a soccer match” is not converted into a table.

## Architecture repair

Canonical implementation lineage:

- `d9dd3271d8375bab3d1f6c4c1fa77e67d8d988ab` — generalized shared matching-table architecture.
- `c87ea82fd60b7fa5c181f3c58449b54968bc1111` — expanded corpus/unit regressions.
- `54e0f97318abd3eb4d3d2a83f4b2587a8226ac53` — browser regression for alternate matching prompts, including the user-reported equilibrium-potential question.
- `f0471f5b494c50e36bf7e3952be90a33ba45dea1` — source-stable final regression contract after removing transformed-content assumptions from source-stage unit tests.

The shared renderer now:

- accepts general `match` / `matching` wording but renders a table only when structural evidence is present;
- trims repeated source-table blocks/headings rather than leaking the duplicate into the last cell;
- supports source labels through A–H and roman i–viii, including legitimate A–F / 1–6 tables;
- ignores `Column A`, `Column B`, `List A`, etc. when those are prose/header references rather than row labels;
- supports bare `a…h ↔ i…viii` source notation;
- can preserve label-only source groups when another group contains meaningful source values, without inventing missing text;
- leaves source-incomplete/image-dependent records un-reconstructed rather than fabricating content.

## Exact user-reported regression

`physiology-9-17` is now explicitly exercised in the generated PWA browser regression. The test requires:

- a visible semantic List I / List II table;
- Sodium, Chloride, Potassium, Calcium;
- -70, +63, +132, -90;
- exactly four canonical answer choices;
- the duplicated `Ion Equilibrium Potential (mV)` source block to appear only once in the learner-visible question.

The earlier “good” example `physiology-9-6` also benefits from repeated-prelude cleanup; the architecture no longer intentionally relies on its accidental trailing header text.

## Verification

Exact-head canonical checkpoint `f0471f5b494c50e36bf7e3952be90a33ba45dea1`:

- Engineering Gate `34837009703`: **PASS**.
- Full Android/PWA/browser/APK/package run `34837009688`: **PASS**.
- Generated PrepLadder matching-question browser regression: **PASS**, including `physiology-9-17`.
- Continue Practice browser regression: **PASS**.
- APK build/package/reproducibility/Marrow asset checks: **PASS**.
- PWA preview deployment: **PASS**.
- Production promotion: **SKIPPED** as required.

Status is **BUILD_VERIFIED**, not yet user-accepted. User should physically re-review the new preview across several matching questions before acceptance.

## Remaining matching records

After the generalized built-artifact audit, the following genuine match-like records still do not have enough safely parseable text structure for generic reconstruction and may require source-image inspection or targeted/manual repair:

- `26-13`
- `physiology-10-10`
- `physiology-36-7`
- `anatomy-3-12`
- `anatomy-14-3`
- `anatomy-29-16`
- `anatomy-29-33`
- `anatomy-30-4`

Do not force these through generic parsing if one side of the match is absent or image-dependent. Preserve source fidelity and repair them only with sufficient source evidence.

Ordinary non-table uses of the word “match” such as `physiology-32-23`, `anatomy-22-20`, and `anatomy-29-24` must remain ordinary MCQs/prose.

## Next action

Have the user physically inspect the newly deployed preview, especially `physiology-9-17` and a spread of matching questions across subjects/chapters. If residual failures are among the structurally incomplete/image-dependent IDs above, handle them as targeted source-fidelity repairs rather than broadening the generic parser until it guesses.
