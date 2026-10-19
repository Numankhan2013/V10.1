# UWorld auto-extraction pipeline (2026-10-09)

Importing a UWorld collection used to mean a model read every question and every
screenshot and hand-built a "reviewed" overlay. That was expensive and slow. Most of
the work is mechanical, so it is now a deterministic program: `tools/uworld_auto/`.

## What the PDFs are

Each source PDF is a run of 1416×757 screenshots of the UWorld viewer with an OCR text
layer. Per question: an unanswered view, an answered view (choice percentages, the
correct-answer tick, statistics), scrolled explanation views and "Exhibit Display"
popups that show each figure at full size. Some PDFs store a question's screenshots
newest-first.

## How the extractor works

1. **Page model.** Poppler gives OCR lines with coordinates and the page raster. The
   blue toolbar and footer bound the content area; the question ID and "Item N of M"
   come from the header.
2. **One canvas per question.** Answered and scrolled views of a question are one
   scrolling document. They are aligned on shared OCR lines (pixel matching when no
   line is shared), so every line is read once, from the view where it is not clipped.
   This removes scroll duplication.
3. **No OCR leakage.** Tables (bordered boxes) and pictures (ink blobs that are not
   prose) are found on every view. Any OCR text inside them, on any view, is dropped
   from the prose. Tables ship as source crops; figures ship from their full-size popup.
4. **Answer key.** The correct choice is read three ways: the green tick, the choice
   whose percentage equals "% answered correctly", and the OCR letter. Disagreement
   flags the question.
5. **Clean-up.** Split words are rejoined using the PDF's own vocabulary ("intern a" →
   "interna"), OCR glyph errors are repaired (`°/o` → `%`, `<:!` → `≥`, accents), and
   the subject/system/topic footer is cut from the objective.
6. **Automatic QA.** A question ships as `verified` only if all checks pass:
   - 4–9 choices in order
   - the correct answer is read
   - the percentages are present and sum to about 100
   - the stem, explanation and objective are non-empty
   - no suspicious OCR characters
   - the existing screenshot-chrome and overlap hygiene gate passes

   Anything else ships `source-blocked`, the existing safe state, and is listed in
   `qa_report.json`.

## Accuracy

Measured against the 81 hand-reviewed Female Reproductive questions (`compare.py`):

| Measure | Result |
|---|---|
| Questions extracted | 80 / 81 |
| Stems | 78 / 80 |
| Correct answer | 79 / 80 |
| Choice percentages | 79 / 80 |
| Objectives | 74 / 80 |
| Explanation prose similarity | mean 98.7% |
| Passed every check automatically | 54 / 80 |

Several remaining "mismatches" are errors in the hand review (stray "6" or "V6" left in
choice text, explanation paragraphs it dropped). Figures come from the same popups the
reviewers used. The extractor also keeps legitimate exhibits the reviewers skipped.

## Running it

```sh
git lfs fetch origin <branch> --include="data/uworld/Source_pdfs/<dir>/*"
python3 tools/uworld_auto/package.py <slug> "<Collection>" "data/uworld/Source_pdfs/<dir>/<file>.pdf"
# then add `import uworld_<slug>` to tools/uworld_collections.py
python3 tools/test_uworld_auto.py
```

About 6 minutes per 600 pages on one CPU and no model tokens. Flagged questions can
be fixed later. `review_packet.py <slug>` exports just those questions (JSON plus
page images) for a person or a small model. Fixes go in `reviewed/fixes.json` and
survive re-runs.

Figure crops are committed under `prepared/<slug>/figures/`. CI copies them, so CI
no longer downloads the multi-GB PDFs for these collections.

## First collection: General Pharmacology

- 40 of 47 questions extracted: 26 verified and 14 flagged (shipped `source-blocked`).
- 7 questions could not be extracted. Their 26 pages are listed in `manifest.json`
  under `unowned_pages`.
- This PDF is an older, lower-resolution capture with reversed page order. Block
  labels are approximate, because "Item N of M" OCR is unreliable there.

## Header question IDs (2026-10-19)

The OCR layer misreads the small header, so the extractor reads the "Question Id" digits
from the screenshot (`header_id.py`: the digits after "Id:" are equal-width cells matched
to templates in `header_digits.npz`, cut from cleanly OCR-read headers; confidence at
least 0.85 or the OCR value is kept). Image-read IDs are trusted in `group_pages`. Run
`fix_leaks.py` then `sanitize.py` after every re-extraction; delete `reviewed/fixes.json`
first when a re-extraction changes question IDs, because fixes are keyed by ID.

## Review and rescue by outside agents

`review_packet.py <slug>` (flagged) and `rescue.py <slug> packets <dir>` (unassembled)
build packets; convert the page PNGs to JPEG and publish them as batches on a branch
that holds only review material (`uworld-review`, files under `data/uworld/review/`).
Agents follow `review/INSTRUCTIONS.md` (+ `INSTRUCTIONS_RESCUE.md`), write
`answers/<batch>/UWORLD_<id>.json` and run `review/check_review.py <batch>`. Their
branches must not be named `uworld-review/...` (a branch cannot sit under another
branch's name). Apply with `apply_reviews.py <slug> <dir> --careful` and
`rescue.py <slug> adopt <packets> <answers>`. Result for the five 2026-10 collections:
148 answers, 134 verified at review, all applied; agents held back packets with no
answered screenshot instead of guessing.
