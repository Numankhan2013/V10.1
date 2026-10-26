# Anatomy explanations still left as one run of text

Written 2026-10-25. All 55 Anatomy restructure batches pass `tools/explanation_restructure.py check`;
1,034 of 1,097 questions are restructured. The first agent pass returned `unchanged` for 107, of which 75
were over 700 characters and still read as one run of text. A second pass (8 Haiku agents) restructured 43
of those 75; the 31 below are still unchanged. Some are flattened tables whose cell boundaries are not
recoverable without the figure, so `unchanged` follows the rule "a plain paragraph is fine; a wrong table is not".

A third pass (3 Haiku agents, 2026-10-25) restructured the 25 explanations that still held a paragraph
over 100 words (24 restructured ones plus `anatomy-q860263`); none of the 31 below has a paragraph over
100 words, so each reads as short paragraphs or option rulings.

To redo: replace the question's `{"id": ..., "unchanged": true}` in its result file with `blocks`, then run
`tools/explanation_restructure.py import --bank anatomy` and rebuild the bank.

| Batch | Questions (characters / option rulings) |
|---|---|
| anatomy-001 | `anatomy-2-2` (936/3) |
| anatomy-003 | `anatomy-4-6` (900/3), `anatomy-4-11` (1209/3) |
| anatomy-007 | `anatomy-q857934` (1132/3) |
| anatomy-010 | `anatomy-9-11` (714/3) |
| anatomy-015 | `anatomy-21-64` (976/3) |
| anatomy-016 | `anatomy-q865306` (787/3) |
| anatomy-017 | `anatomy-15-13` (831/3), `anatomy-15-15` (757/3) |
| anatomy-018 | `anatomy-15-42` (733/3) |
| anatomy-021 | `anatomy-18-12` (997/3) |
| anatomy-024 | `anatomy-21-39` (1074/3) |
| anatomy-026 | `anatomy-22-2` (1076/3) |
| anatomy-033 | `anatomy-27-24` (1190/3) |
| anatomy-034 | `anatomy-28-3` (2090/3) |
| anatomy-038 | `anatomy-31-3` (1272/3) |
| anatomy-039 | `anatomy-32-11` (1001/3) |
| anatomy-040 | `anatomy-34-4` (840/3) |
| anatomy-041 | `anatomy-35-8` (1203/3) |
| anatomy-042 | `anatomy-50-1` (1341/3) |
| anatomy-044 | `anatomy-38-7` (1191/0), `anatomy-38-8` (829/3) |
| anatomy-047 | `anatomy-43-6` (1541/3) |
| anatomy-048 | `anatomy-44-3` (771/4), `anatomy-44-10` (973/3) |
| anatomy-049 | `anatomy-44-21` (1891/4) |
| anatomy-051 | `anatomy-46-1` (729/2) |
| anatomy-053 | `anatomy-48-19` (1055/3), `anatomy-48-14` (1326/3) |
| anatomy-054 | `anatomy-q859522` (933/3), `anatomy-49-4` (1549/0) |
