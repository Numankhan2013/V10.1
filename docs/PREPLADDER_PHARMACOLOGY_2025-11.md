# PrepLadder Pharmacology — November 2025 edition (2026-10-17)

Pharmacology is a new Second Prof subject with one bank, PrepLadder. Source:
the PrepLadder Pharmacology QBank of November 2025 (`pharmaprep11.pdf`, 1,817
pages: Part A questions pp 6–610, Part B answers and explanations pp
611–1817), extracted by an external agent into a master JSONL, a manifest and
six figure archives.

- Build: `tools/build_prepladder_pharmacology_bank.py import <master.jsonl> <images-dir>`.
- The pipeline is shared with Pathology (`tools/prepladder_text_bank.py`);
  text and block rules are Microbiology's (`tools/build_prepladder_microbiology_bank.py`).
- Data: `data/Prepladder/pharmacology/`.

## Result

| | |
|---|---:|
| Questions | 1,321 |
| Lessons (topics) | 59, in 13 sections |
| PYQ lessons | 16 (650 questions), join the PYQ journey |
| Figures | 272 (71 in stems, 201 in explanations) |

- **Sections.** General Pharmacology through Anaesthetics and Miscellaneous
  Pharmacology, in source order.
- **IDs.** `pharmacology-<lesson>-<n>`, lessons in source order; each question
  also carries its PrepLadder QID.
- **Options.** 1,317 questions have four options; 4 PYQs (lesson 42 Q2, Q30,
  Q31, Q99) print five (A–E) and keep them.
- **Home.** Pharmacology joins Microbiology and Pathology under Second Prof,
  with a pill icon and its own accent dot (yellow).

## What was checked

- **Counts.** Every lesson's question count matches the manifest; every
  question has one key, flagged correct in the source. The extraction
  report says 17 PYQ lessons; the data and the PDF have 16 lessons titled
  "Previous Year Questions" (650 questions, the report's own total).
- **Against the PDF.** Part B was parsed separately and matched by QID: all
  1,321 printed "Correct Answer" lines agree with the bank's key. Explanation
  words match the PDF apart from the PDF's own broken words ("r heumatoid",
  "iierythromycin"), which the extraction repaired.
- **Figures.** All 272 figures arrived; `tools/figure_trim.py` removed thin
  extraction borders from 227.
- **Text.** No ■ placeholder, leaked image markup, `;=` URL leak or "Correct
  Option D." lead reaches the learner (the bank test fails otherwise). The
  answer-lead rule now also takes "Correct Option. C" (one question); the
  Microbiology and Pathology shards are unchanged by it.

## Fixes that apply to every PrepLadder text bank

- **References-only explanations.** Four questions print nothing after
  "Explanation:" but references. They show "The source PDF prints no
  explanation for this question." and a review note, like a lost fragment.
  The app used to hide that opening note as a repeat of the takeaway when
  only references followed; it now keeps it.
- **Fragments followed by text.** Two explanations open mid-sentence
  ("linical, accidental, or suicidal overdose."). The fragment is left out
  and the rest stays, with a review note. The same rule now applies to three
  Pathology questions whose fragment was followed by a figure: they show the
  figure without the "no explanation" note.
- **Text after the references.** The extraction once split a reference into a
  new paragraph; text after the references now joins them.

## Known gaps

- **6 explanations missing in the source.** Two print only a sentence tail,
  four only references.
- **Option rulings stay inline.** As in Pathology, the PDF prints
  explanations flat; the restructure pack (`docs/EXPLANATION_RESTRUCTURE.md`)
  can be pointed at this bank once Pathology's run is in.
- **Matching questions keep their options.** 34 "match the…" questions across
  the three text banks (Pharmacology 11, Pathology 18, Microbiology 5) had
  complete options but a stem the matching-table parser could not lay out
  (for example "e:" instead of "e."), and the app hid the options. For these
  banks the stem now stays plain text and the question stays answerable; the
  82 tables that already rendered are unchanged. Older OCR banks keep the
  fail-closed rule.

## Cut-off openings and the restructure pack (2026-10-17)

- **112 explanations open mid-word or mid-sentence in the PDF itself**
  ("Explanation: ue to alpha 1a…", "Explanation: : There is no…"). The shared
  builder now repairs what it can. In 74, the first word lost one or two
  letters, and the full word is the only completion found elsewhere in the
  bank ("ue" → "Due", "drenaline" → "Adrenaline", "losetron" → "Alosetron").
  In the other 38 a whole label or sentence is gone ("is a prodrug…"). Those
  openings are written by hand in `data/Prepladder/pharmacology/openings.json`
  (`{"from": exact start, "to": new start}`; empty `from` prepends), worked out
  from the question, its answer and the rest of the explanation. Where the
  surviving text covered only wrong options, the new opening also says why the
  key is right (5-7, 5-43, 42-32). Two (28-7, 31-6) already read complete and
  only get a note. The builder applies openings after any restructure and fails
  if an explanation no longer starts with `from`, so restructure batches and
  their hashes stay on the PDF text. Each carries a review note saying the
  opening was written by hand. Pathology had one such case (25-19,
  "Castleman disease, …"), in `data/Prepladder/pathology/openings.json`.
- **Restructure pack.** `tools/explanation_restructure.py` takes `--bank`, or
  reads the bank from the result file's name or folder. Pharmacology batches:
  `data/Prepladder/pharmacology/restructure/batches/pharmacology-001` … `066`
  (1,315 questions; the 6 with no explanation are left out). Worked examples:
  `restructure/examples/example-result.json`. Instructions and prompts:
  `docs/EXPLANATION_RESTRUCTURE.md`. Only squashed explanations get
  restructured; clean one-paragraph-per-option explanations stay unchanged.

## Restructure run (2026-10-18)

- All 66 batches restructured by in-session agents (the user's own agents
  were rate-limited) and re-checked: 1,155 restructured, 160 unchanged, 0
  rejected; 422 tables. Results in `restructure/results/`, merged into
  `restructure/restructured.json`.
- Reviewed by hand: tables where the PDF's cell boundaries were unclear.
  16-4 (glucocorticoid table, lost merged cells) stays unchanged. Blank
  cells in other tables mark merged cells of the source.
- 3-2 opened with the source's own "Correct answer- C) …" line, hidden by
  bold markup; it is dropped from the overlay, as for every other answer label.
- Two cut-off openings were also hidden by bold markup (27-56, 55-3). They
  get hand-written openings with a lead paragraph explaining the key.
  Openings now also apply when a restructure starts with a table (27-36:
  the opening becomes its own paragraph).
