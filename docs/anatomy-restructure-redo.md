# Anatomy explanations the agents left unchanged but that still read as one run of text

Written 2026-10-25 after the 55 Anatomy restructure batches were checked. All 55 result files pass
`tools/explanation_restructure.py check`, and 990 of 1,097 questions are restructured. The agents
returned `unchanged` for 107; 75 of those are over 700 characters (53 of them carry two or more
`(Option X)` rulings). Some are flattened tables whose cell boundaries are not recoverable without the
figure, so `unchanged` follows the rule "a plain paragraph is fine; a wrong table is not". The rest
look splittable (option rulings, enumerations, topic changes) and are worth another pass.

To redo: copy the question out of its result file (`{"id": ..., "unchanged": true}`) and replace it
with `blocks`, then run `tools/explanation_restructure.py import` and rebuild the bank.

| Batch | Questions (characters / option rulings) |
|---|---|
| anatomy-001 | `anatomy-2-2` (936/3), `anatomy-2-16` (1023/3), `anatomy-1-3` (944/0) |
| anatomy-002 | `anatomy-1-12` (766/0) |
| anatomy-003 | `anatomy-4-1` (1045/3), `anatomy-4-6` (900/3), `anatomy-4-11` (1209/3) |
| anatomy-004 | `anatomy-4-21` (1374/3) |
| anatomy-007 | `anatomy-q857934` (1132/3) |
| anatomy-010 | `anatomy-9-6` (1021/3), `anatomy-9-11` (714/3) |
| anatomy-013 | `anatomy-12-13` (805/0) |
| anatomy-015 | `anatomy-14-11` (1123/3), `anatomy-21-64` (976/3) |
| anatomy-016 | `anatomy-q865306` (787/3), `anatomy-15-67` (1469/3) |
| anatomy-017 | `anatomy-15-13` (831/3), `anatomy-15-15` (757/3) |
| anatomy-018 | `anatomy-15-42` (733/3) |
| anatomy-021 | `anatomy-18-12` (997/3) |
| anatomy-024 | `anatomy-21-39` (1074/3) |
| anatomy-026 | `anatomy-22-2` (1076/3) |
| anatomy-033 | `anatomy-27-24` (1190/3) |
| anatomy-034 | `anatomy-28-3` (2090/3) |
| anatomy-035 | `anatomy-29-2` (766/0) |
| anatomy-038 | `anatomy-31-3` (1272/3), `anatomy-31-6` (1464/2), `anatomy-31-12` (1812/0), `anatomy-32-1` (1958/3), `anatomy-32-2` (1173/0), `anatomy-32-3` (1068/0), `anatomy-32-5` (1234/0), `anatomy-32-6` (1138/0) |
| anatomy-039 | `anatomy-32-11` (1001/3) |
| anatomy-040 | `anatomy-33-10` (1900/3), `anatomy-34-4` (840/3), `anatomy-35-1` (2212/3) |
| anatomy-041 | `anatomy-35-8` (1203/3) |
| anatomy-042 | `anatomy-50-1` (1341/3) |
| anatomy-044 | `anatomy-38-7` (1191/0), `anatomy-38-8` (829/3), `anatomy-39-5` (2111/0), `anatomy-39-6` (1784/0), `anatomy-39-7` (1599/0) |
| anatomy-045 | `anatomy-40-8` (2236/0) |
| anatomy-047 | `anatomy-43-6` (1541/3) |
| anatomy-048 | `anatomy-44-1` (2280/3), `anatomy-44-3` (771/4), `anatomy-44-4` (1677/4), `anatomy-44-10` (973/3), `anatomy-44-17` (895/1), `anatomy-44-18` (1230/3) |
| anatomy-049 | `anatomy-44-19` (2068/3), `anatomy-44-21` (1891/4), `anatomy-45-27` (1129/0), `anatomy-45-26` (1311/0), `anatomy-45-25` (1811/3) |
| anatomy-051 | `anatomy-46-1` (729/2), `anatomy-46-2` (746/0), `anatomy-46-3` (1567/4), `anatomy-46-4` (1159/4), `anatomy-46-5` (1512/3), `anatomy-46-11` (1510/0), `anatomy-46-12` (913/0), `anatomy-46-13` (1364/3), `anatomy-46-14` (2285/3), `anatomy-46-15` (1661/3), `anatomy-46-16` (1049/1) |
| anatomy-052 | `anatomy-47-16` (1721/3) |
| anatomy-053 | `anatomy-48-19` (1055/3), `anatomy-48-14` (1326/3) |
| anatomy-054 | `anatomy-q860263` (1445/3), `anatomy-q859522` (933/3), `anatomy-49-1` (1424/3), `anatomy-49-4` (1549/0) |
