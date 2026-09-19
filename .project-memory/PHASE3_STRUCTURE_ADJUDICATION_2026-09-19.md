# Phase 3 structural adjudication — 2026-09-19

Input HEAD: `f5daabef70939069310655a5eba6582576b2091a` (`feature/marrow-canonical-full-current`).
Verified CI: Engineering `35228932515`, full `35228932475` (both success).
Audit: `python3 tools/audit_question_structure.py` re-run at this HEAD; `--check` deterministic pass.
Reports (ignored `build/`): `build/question-fidelity/structure-audit.json`, `structure-audit.md`.

Status: **triage adjudicated; no product code changed; audit script remains OPEN by design.**
No demonstrated rendered-cell/label defect still answerable (0 PrepLadder, 0 Marrow).

## Counts at this HEAD

- Scanned: 5,397 (PrepLadder 2,686; Marrow 2,711).
- PrepLadder candidates 444: 36 complete-generic, 22 source-backed-override, 272 false-positive-ordinary-prose, 114 incomplete-unsafe, 8 fail-closed.
- Marrow candidates 273: 173 false-positive, 100 incomplete-unsafe, 0 fail-closed.
- Source-review-required 219; unsafe-still-answerable 206 (all suspected/unadjudicated, none demonstrated).

## Fail-closed 8 (all correctly answering-disabled, not rendered corrupt)

Known intentionally non-answerable (per STATE): `anatomy-22-4` (p888, empty options + answer-text leak),
`physiology-23-38` (p649) / `physiology-33-33` (p944) (duplicate tactile-discrimination, non-standard 5-option contract),
`physiology-24-6` (p690, compliance-curve image, empty options).

Image/source-dependent, correctly fail-closed pending source-page review (not parser fixes):
`anatomy-9-1` (p306, haemorrhage match, truncated `Locatio` + empty source marker),
`anatomy-14-5` (p528, nasal-septum labelled parts, duplicated source block),
`anatomy-40-10` (p1593, uterine-artery branches explicitly `based on the image given`),
`anatomy-47-2` (p1811, 5-item match with empty counterparts, duplicated block).

## True match-family residuals without semantic tables (no demonstrated cell loss)

- PrepLadder `7-53` (p173): `not correctly matched` combination question (options `1 only` / `1 and 2` / …). Combination-type, not a matching-table defect.
- Marrow image-owned matchings (stems carry only the prompt; list content is image-owned, no text table expected):
  `marrow__ANAT_CH13_Q005` (p232), `marrow__ANAT_CH14_Q004` (p247), `marrow__ANAT_CH16_Q001` (p286),
  `marrow__ANAT_CH28_Q023` (p480), `marrow__ANAT_CH31_Q005` (p557), `marrow__ANAT_CH43_Q005` (p793).
- Marrow row-selection / figure-point: `marrow__ANAT_CH48_Q007`, `marrow__PHYS_CH06_Q010`, `marrow__PHYSIO_CH24_Q007`.
- These belong to the image lane / manual source comparison when that lane resumes, not to the generic text parser.

## Bulk incomplete-unsafe (not proven defects)

- PrepLadder: structured-combination 68, row-selection 35, enumerated-list 31, row-table-wording 23.
- Marrow: row-selection 54, structured-combination 41.
- These are combination/ordering/plain-enumeration adjudication items. Lack of a semantic table alone does not prove information loss. None shows empty/dash rendered cells still answerable.

## Stem-override audit artifact (not table defects)

`4-3` and `5-10` appear in `unresolvedIds` because the audit records `before.question` (post-hygiene, pre-`nkQuestionStemOverride`)
as `normalizedQuestion`. Both are build-verified stem repairs at this HEAD (`4-3` page-82 Q3 prompt; `5-10` α-1,4 linkage).
Their table-null status is correct: neither is a matching-table question.

## New failure classes requiring regression

None demonstrated in this re-run. Existing regressions already cover: nerve-fibre `physiology-9-6`,
ion `physiology-9-17`, row-selection `physiology-9-22`, complete-source overrides (10 records),
stem overrides `4-3`/`5-10`, paired structural integrity, native-explanation selectors.

## Next per campaign

Phase 3 machine/human reports exist; adjudication above narrows residuals to image-owned/source-review
and combination false-positive classes. Next is Phase 4 scientific-notation forensic audit
(remaining ambiguous `■`: `5-14`, `14-9`, `physiology-9-18`, `physiology-20-7`, `physiology-23-11`,
`physiology-26-20`, `marrow__BIOCHEM_CH14_Q013`, `marrow__BIOCHEM_CH17_Q008`, plus 55 PrepLadder + 1 Marrow
explanation residuals). No commits/pushes in this adjudication step; production untouched.
