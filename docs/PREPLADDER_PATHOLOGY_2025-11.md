# PrepLadder Pathology — November 2025 edition (2026-10-17)

Pathology is a new Second Prof subject with one bank, PrepLadder. Source: the
PrepLadder Pathology QBank generated on 18 November 2025 (nine PDFs,
`pathoprep11-1-300.pdf` … `pathoprep11-2401-2889.pdf`, 2,889 pages), extracted
by an external agent into a master JSONL, a manifest and 48 figure archives.

- Build: `tools/build_prepladder_pathology_bank.py import <master.jsonl> <images-dir>`.
- Text and block rules are Microbiology's (`tools/build_prepladder_microbiology_bank.py`).
- Data: `data/Prepladder/pathology/`.

## Result

| | |
|---|---:|
| Questions | 1,459 |
| Lessons (topics) | 90, in 4 sections |
| PYQ lessons | 27 (615 questions), join the PYQ journey |
| Figures | 1,676 (373 in stems, 1,303 in explanations) |

- **Sections.** General Pathology, Systemic Pathology, Hematology, and Blood
  Banking and Clinical Pathology.
- **IDs.** `pathology-<lesson>-<n>`, lessons in source order; each question
  also carries its PrepLadder QID.
- **Home.** Pathology joins Microbiology under Second Prof, with the
  microscope icon and its own accent dot (orange).

## What was checked

- **Counts.** Every lesson's question count matches the manifest; every
  question has four options and one key, flagged correct in the source.
- **Figures.** All 1,676 figures arrived, and each matches the manifest's pixel
  size. Original bytes are kept; `tools/figure_trim.py` removed thin
  extraction borders from 1,127.
- **Text.** No ■ placeholder, leaked image markup or "Correct answer" lead
  reaches the learner (the bank test fails otherwise).
- **Against the PDF.** The combined `pathoprep11.pdf` was parsed separately
  and matched by QID. All 1,450 printed "Correct Answer" lines agree with the
  bank's key, letter and text; the 9 blank ones are the 9 `needs_review`
  questions. Explanations match the PDF apart from removed debris (data-hash
  leaks, `{{caption_text}}`, glyph runs). Options match apart from 2 Unicode
  subscripts (O₂•⁻), 1 restored CBC and the 8 image-only option sets, which
  the PDF does not print as text.
- **Browser.** `tools/verify_prepladder_pathology_browser.py` walks Home →
  bank → lessons → a stem figure → an explanation → a PYQ lesson.

## Fixes made in the build

- **Lesson titles.** The extraction title-cased every word ("Cml And Cll",
  "Hodgkin'S"). Acronyms (ER, RHD, GIT, IBD, CNS, CML, CLL, WBC, ALL, AML),
  Roman numerals and "Hodgkin's" are restored and joining words lowercased;
  nothing else changes.
- **Reference URLs.** The extraction turned `&source=` into `&source;=`; the
  stray `;` is removed.
- **Long URLs on phones.** An unbroken reference URL widened the explanation
  past the screen. The explanation column is now held to the container and
  long strings wrap (applies to every structured explanation).

## Known gaps

- **17 explanations missing in the source.** The PDF prints only the tail of
  a sentence ("Explanation: of the correct answer.", "for Assertion."), so
  there is nothing to recover. The fragment is replaced by "The source PDF
  prints no explanation for this question." and a review note; any figure and
  references stay.
- **9 image-only option sets.** The PDF printed the options as images and left
  the answer line blank; the extraction rebuilt the options and key from the
  explanation. These stay `needs_review`.
- **Flat explanations.** As with Microbiology's November 2025 edition, the PDF
  prints explanations as running text, so they show as paragraphs; option
  analyses get a bold label.
- No physical-device review.
