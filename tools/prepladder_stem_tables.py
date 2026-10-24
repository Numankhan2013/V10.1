"""Hand-checked display fixes for PrepLadder stems and choices the source PDF flattened.

`data/Prepladder/<bank>/stem_tables.json` maps an app question ID to
{"stem": the question sentence without its lists, "columns": [...], "rows": [[...], ...]}.
Each list keeps its printed order (row k = item k of every list), so the table never
gives the answer away. The app renders `stemTables` as a real table under the stem.
"""
import json
import re
from pathlib import Path

LABEL = re.compile(r"^\(?([A-Za-z]|\d{1,2}|[ivx]{1,4})[.)]\s", re.I)


def apply(record: dict, path: Path, fail) -> int:
    if not path.exists():
        return 0
    tables = json.loads(path.read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in record["questions"]}
    for qid, t in tables.items():
        q = by_id.get(qid)
        if q is None:
            fail(f"{path.name}: unknown question {qid}")
        cols, rows, stem = t.get("columns") or [], t.get("rows") or [], (t.get("stem") or "").strip()
        if not stem or not 1 <= len(cols) <= 6 or not all(str(c).strip() for c in cols):
            fail(f"{path.name}: {qid} needs a stem and 1-6 column headers")
        if len(rows) < 2 or any(len(r) != len(cols) for r in rows) or any(not str(r[0]).strip() for r in rows[:2]):
            fail(f"{path.name}: {qid} rows must match the columns")
        # A printed table may replace only an extracted one that came out empty
        # (its lists landed in the headers with no rows).
        if any(t.get("rows") for t in q.get("stemTables") or []):
            fail(f"{path.name}: {qid} already has a stem table")
        # Every label the key pairs ("1-iii", "A-4") must head a cell of the table.
        labels = {m.group(1).lower() for r in rows for c in r if (m := LABEL.match(str(c)))}
        if len(cols) > 1:
            for pair in re.findall(r"\b([A-Za-z]|\d{1,2}|[ivx]{1,4})\s*[-–]\s*([A-Za-z]|\d{1,2}|[ivx]{1,4})\b", q["correctAnswerText"], re.I):
                missing = [p for p in pair if p.lower() not in labels]
                if missing:
                    fail(f"{path.name}: {qid} key label {missing} heads no cell")
        q["question"] = stem
        q["stemTables"] = [{"columns": cols, "rows": rows}]
    return len(tables)


def apply_options(record: dict, path: Path, fail) -> int:
    """`option_text.json`: {question ID: [choice text A, B, …]} for choices the source
    printed as pictures (filled with descriptions that gave the answer away) or glued
    to a neighbouring statement. Letters and the key never change."""
    if not path.exists():
        return 0
    fixes = json.loads(path.read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in record["questions"]}
    for qid, texts in fixes.items():
        q = by_id.get(qid)
        if q is None or len(texts) != len(q["options"]) or not all(str(t).strip() for t in texts):
            fail(f"{path.name}: {qid} must give one non-empty text per choice")
        for option, text in zip(q["options"], texts):
            option["text"] = text
        q["correctAnswerText"] = q["options"][q["correctOption"] - 1]["text"]
    return len(fixes)
