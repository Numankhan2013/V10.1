# UWorld Biochemistry OCR pilot

The pilot imports only Biochemistry from `uworld-poisoning-env-block-01-20261003` at `2cc0ea8f9ab4d2e3ac18d32b94b58b36a0f3700d`. The original canonical JSONLs, QA material and Git LFS PDF are unchanged. No other UWorld subject is integrated.

The supplied corpus contains 120 nominal questions in three blocks and 12 supplemental questions: 132 unique canonical IDs and 729 uniquely assigned source PDF pages. The source PDF is pinned to SHA-256 `806d95d6f09dde57d34e0d0b5fda69298a7789041bb570ce4fa6dd1c95d4fae9` and retained for the later source-validation pass. The current build uses JSONL/OCR text only, following the user's revised scope. It does not extract or package UWorld PDF screenshots.

## Shared architecture

`tools/uworld_biochemistry.py` checks source hashes, counts, stable IDs, question/answer consistency, consecutive A–H choices and source-page ownership, then adapts the corpus into one additional `BANKS_BY_SUBJECT.Biochemistry` record. Each question retains its complete immutable original under `uworldSource`, plus a separate auditable OCR display transcript. Canonical IDs, including the supplemental namespace, are preserved.

The three source blocks and Supplemental source questions are four navigation topics. Forty-seven records lack reliable topic metadata, so the adapter does not invent a medical taxonomy. Existing Practice, CBT, Review Solutions, bookmarks, notes, custom modules, FSRS, history, sync and checkpoints remain the product's shared engines. The UWorld-only presentation branch accepts four through eight choices and bypasses incumbent extraction repair. Other banks retain their existing presentation rules.

`uworld_biochemistry_core.js` renders UWorld explanation text directly, rather than routing it through Marrow takeaway or generated distractor sections. Original choice discussions, numbered stages and the supplied Educational objective remain recognizable. Impeccable's Operate/Read and typeset guidance informs the retained NK palette, 17px body, 1.72 line-height, 70ch maximum measure, paragraph spacing and source-label emphasis. Phone users can scroll vertically; iPad and desktop use the same readable document instead of compressed screenshot panels. There is no animation or source-asset wait before answering.

`uworld_source_text.py` removes only explicit screenshot labels, narrowly identifiable leading statistics, and exact repeated runs of at least 40 words. Display paragraph breaks change whitespace only. Removals retain hashes and counts; raw OCR remains available behind a disclosure. No medical wording, option reasoning, tables or missing content is generated.

## OCR boundary and deferred validation

The native OCR display replaces an earlier rejected screenshot-panel prototype. That prototype is not the shipped design or a certified result.

There are currently **105 structurally usable questions** and **27 conservatively held diagram-dependent references**. The latter are listed in `MISSING_VISUAL_IDS`. They remain discoverable individually, open a read-only text view, and do not create answers, scores or FSRS records. New CBT, module and Revision pools exclude them before sampling; the session-start guard also excludes them. Known pedigree and arrow choices keep neutral labels rather than presenting imported interpretations as source choices.

This is not a completed medical-content audit. Scanning errors, partial overlaps and flattened laboratory/comparison tables remain possible, including in the 105 practice questions. Some diagrams may eventually be shown unnecessary, and additional missing exhibits may be found. The next pass should use the user-requested **Luna subagents to validate every question against the PDF**, then recover focused scientific exhibits and structured tables with explicit source evidence. That work is deliberately deferred; no question-by-question certification is claimed now.

QID1486's Educational objective is clipped in the supplied source and remains null. Twelve aggregate correct percentages and QID11914's option-A percentage remain unavailable. Missing text or statistics are never invented.

Before scaling, complete that Luna pass, review each gated record, verify figure roles prevent answer leakage, verify table relationships and scientific symbols, and budget offline media sizes. Other subjects must supply their own source evidence; do not reuse Biochemistry screenshot coordinates or assume its metadata is universal.

## Revision sessions

Mistakes and Bookmarks launch full eligible frozen queues. Due Review uses the complete queue admitted by existing FSRS priority and daily limits. Labels are Practice mistakes, Practice bookmarks and Review due, without an arbitrary 20-question cap. Unseen retains its separate existing random-20 action.

The grid and final-question action open the same Revision sheet with **Pause** and **Finish session**. Pause preserves exact ordered membership, position, answers, timing and pending ratings in shared durable checkpoints and returns to Revision. Resume restores the same session. Finish saves answered work only; untouched questions remain eligible without fabricated skipped attempts. Finishing with no answers creates no result. Storage-failure rollback and retry remain shared.

## Search-engine exclusion

[Search engine exclusion](SEARCH_ENGINE_EXCLUSION.md) documents HTML robots metadata, `robots.txt`, static response headers and source-worker response coverage. These discourage cooperative indexing. They do not restrict direct downloads or hide a public GitHub repository and its history. Actual access restrictions require private source storage and server-side authentication; obfuscation does not supply that protection.

## Validation status

Source adapter/runtime/OCR checks pass. The running generated diagnostic app passes UWorld Practice, immediate committed feedback, shared FSRS/bookmarks, deferred CBT feedback, Review Solutions, custom modules, read-only references and incumbent-bank switching at 390, 820, 1194 and 1440px. Body computes to 17px/29.24px with a 70ch maximum measure. Continuous Revision has phone/tablet completion, pause/reload, save-failure retry, answered-only finish and daily-cap checks.

Product **c7b505370b00f696b50ec2d81ea719283b8acced** passes both Engineering gates (`37128060474`, `37128062400`) and full ordered build `37128060483`, including packaged APK/PWA and Android phone/tablet emulators. Two earlier candidates failed the 320px Revision geometry check; concise dashboard hints preserve the existing type sizes, 44px controls and unchanged all-four-cards-visible assertion. Session eligibility uses one question index before filtering, avoiding repeated corpus scans.

The actual hosted [pilot preview](https://690495d5.nk-qbank.pages.dev) passes the same UWorld scenarios at 390/820/1194/1440px and full Revision scenarios at 390/820px. Hosted static/worker/PDF, HEAD and Range responses carry crawler exclusion; the PDF range remains byte-correct. HTML SHA-256: `d833fdd0781061fe671c6689b344f1f53ef1748933f391134a5d725d9b066dec`. [PR93](https://github.com/Numankhan2013/V10.1/pull/93) stacks on PR92 and preserves the preceding refinements.

Production remains unchanged and its previous HTML hash was independently rechecked. No physical-device acceptance or OCR medical certification is claimed. This certification handoff is documentation only and keeps the tested product branch/artifact immutable.
