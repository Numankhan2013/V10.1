# PrepLadder QBank web export (Version XI)

The owner's export holds three HTML files per run: the regular **QBank**, the **Elite QBank** and the **PYQ** collection. `tools/prepladder_qbank_import.py` reads all three; `tools/prepladder_qbank_bank.py` builds the app banks; `tools/test_prepladder_qbank_bank.py` and `tools/verify_prepladder_qbank_browser.py` check them.

## What the three files contain

- **Elite** is the main, revised bank: most questions, newest wording.
- **QBank** overlaps Elite heavily; its unique questions are kept, repeats are dropped.
- **PYQ** questions mostly already sit in Elite/QBank; only PYQ-only questions are added.

## Merge rules

1. Questions are matched on normalised stem + options. Elite wins a match; a QBank stem that Elite revised counts as the same question (`eliteRevisedStem`).
2. PYQ-only and QBank-only questions are added to the lesson the source puts them in.
3. For the six subjects already in the app (Anatomy, Physiology, Biochemistry, Microbiology, Pathology, Pharmacology), only questions not already in the PDF bank are added (`merged_record`), into the matching existing lesson.
4. Lessons follow the official app's index (`data/Prepladder/qbank/indexes.json`), in its order, with its British spellings.

## Counts

| | Questions |
|---|---|
| 13 new subjects (Third and Final Prof) | 15,159 |
| Added to the six existing banks | 2,114 (Anatomy 286, Physiology 288, Biochemistry 200, Microbiology 356, Pathology 480, Pharmacology 504) |
| Held out: blank option text in the export | 26 (`held_blank_options.json`) |

Per-subject numbers are pinned in `data/Prepladder/qbank/expected.json`.

## Figures

- 13,682 figures, loaded **at original quality from `image.prepladder.com`**; nothing is recompressed.
- Every figure is probed once (type, width, height, bytes; `figures.json`) so the app reserves its space and nothing jumps.
- Figures over 8 MB (large animated GIFs) show a "Tap to load · N MB" card instead of downloading on their own.
- Ten URLs the server answers empty (HTTP 416) are dropped; SVG URLs are PrepLadder interface icons and are skipped.
- Planned: move figures to Cloudflare R2 as lossless WebP (pixel-identical, about 57% of the size) once the owner sets up a bucket and token.

## Known source gaps

- Anaesthesia Emergency Medicine: 1 unique PYQ after dedup (6 shown in the official app).
- Medicine Miscellaneous Topics: 22 vs 23.
- Forensic Medicine: Torture Types and Entomology have no QBank tests in the export.
- O&G: "RIS" has no topic in the index.
