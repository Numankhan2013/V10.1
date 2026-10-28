#!/usr/bin/env python3
"""Corrections to the banks where the source itself is wrong.

The sources are followed as they are, except where following them would teach
a learner something wrong: an explanation that calls an option by the wrong
letter, an answer key the explanation and the science both contradict, or a
statement that is objectively false. Each such fix is one reviewed entry in
data/source_corrections.json:

  {"id": "<question id>", "reason": "<why>",
   "edits": [{"find": "<exact text>", "replace": "<corrected text>"}],
   "stemEdits": [the same, for the question text],
   "optionText": {"<1-based option>": "<corrected option text>"},
   "correctOption": <1-based key, only when the key itself is wrong>}

build_app_data.py applies the ledger to every record it ships. An entry whose
question or text is no longer in the banks fails the build, so a re-import can
never silently drop a correction.

The same pass mends bold that the exports open inside a word ("p**ale waxy
disc**" reads "**pale waxy disc**"): only an opening marker after one to six
letters, followed by lowercase letters, moves to the word start.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/source_corrections.json"
BOLD_SPLIT = re.compile(r"(?<![A-Za-z0-9*])([A-Za-z]{1,6})\*\*(?=[a-z])")


class CorrectionError(RuntimeError):
    pass


def mend_bold(text: str) -> str:
    out, last, markers = [], 0, 0
    for m in BOLD_SPLIT.finditer(text):
        markers += text.count("**", last, m.start())
        close = text.find("**", m.end())
        # An opening marker whose bold runs on past the word: the bold starts mid-word.
        if markers % 2 == 0 and close - m.end() >= 3:
            out += [text[last:m.start()], "**", m.group(1)]
        else:
            out.append(text[last:m.end()])
        markers += 1
        last = m.end()
    return "".join(out) + text[last:] if out else text


def _fields(q: dict):
    """(container, key, shown) of every explanation string; shown marks the structured parts the app
    renders, beside the flat copies kept for search."""
    if isinstance(q.get("explanation"), str):
        yield q, "explanation", False
    se = q.get("structuredExplanation")
    if not isinstance(se, dict):
        return
    if isinstance(se.get("text"), str):
        yield se, "text", False

    def items(node: dict):
        for item in node.get("items") or []:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    yield item, "text", True
                yield from items(item)

    for block in se.get("blocks") or []:
        if isinstance(block, dict):
            if isinstance(block.get("text"), str):
                yield block, "text", True
            yield from items(block)
    for table in se.get("tables") or []:
        if isinstance(table, dict):
            if isinstance(table.get("title"), str):
                yield table, "title", True
            for row in table.get("rows") or []:
                for i, cell in enumerate(row if isinstance(row, list) else []):
                    if isinstance(cell, str):
                        yield row, i, True


def load_ledger() -> list[dict]:
    entries = json.loads(LEDGER.read_text(encoding="utf-8"))
    seen = set()
    for e in entries:
        if not e.get("id") or not e.get("reason") or not (e.get("edits") or e.get("stemEdits") or e.get("optionText") or "correctOption" in e):
            raise CorrectionError(f"incomplete correction entry: {e}")
        if e["id"] in seen:
            raise CorrectionError(f"two correction entries for {e['id']}")
        seen.add(e["id"])
    return entries


def correct_question(q: dict, entry: dict) -> None:
    for edit in entry.get("edits") or []:
        find, replace, hits = edit["find"], edit["replace"], 0
        for node, key, shown in _fields(q):
            if find in node[key]:
                node[key] = node[key].replace(find, replace)
                hits += shown
        if not hits:
            raise CorrectionError(f"{q['id']}: correction text not found: {find[:80]!r}")
    for edit in entry.get("stemEdits") or []:
        if edit["find"] not in str(q.get("question") or ""):
            raise CorrectionError(f"{q['id']}: question text not found: {edit['find'][:80]!r}")
        q["question"] = q["question"].replace(edit["find"], edit["replace"])
    for number, text in (entry.get("optionText") or {}).items():
        options = q.get("options") or []
        if not 1 <= int(number) <= len(options) or not isinstance(options[int(number) - 1], dict):
            raise CorrectionError(f"{q['id']}: no option {number} to correct")
        options[int(number) - 1]["text"] = text
        if int(number) == int(q.get("correctOption") or 0) and "correctAnswerText" in q:
            q["correctAnswerText"] = text
    if "correctOption" in entry:
        key, options = int(entry["correctOption"]), q.get("options") or []
        if not 1 <= key <= len(options):
            raise CorrectionError(f"{q['id']}: corrected key {key} is not an option")
        q["correctOption"] = key
        if "correctAnswerText" in q:
            option = options[key - 1]
            q["correctAnswerText"] = option.get("text", "") if isinstance(option, dict) else str(option)


def apply_corrections(records: list[dict], ledger: list[dict] | None = None) -> dict:
    """Mend split bold and apply the ledger in place; every entry must land exactly once."""
    entries = {e["id"]: e for e in (load_ledger() if ledger is None else ledger)}
    applied, mended = set(), 0
    for record in records:
        for q in record.get("questions") or []:
            # Ledger text is quoted from the source as it is, so it applies before the bold mend.
            entry = entries.get(str(q.get("id")))
            if entry:
                if entry["id"] in applied:
                    raise CorrectionError(f"{entry['id']}: question appears twice in the banks")
                correct_question(q, entry)
                applied.add(entry["id"])
            for node, key, _shown in _fields(q):
                fixed = mend_bold(node[key])
                if fixed != node[key]:
                    node[key], mended = fixed, mended + 1
    missing = sorted(set(entries) - applied)
    if missing:
        raise CorrectionError(f"corrections for questions not in the banks: {missing[:5]}")
    return {"corrected": len(applied), "boldMended": mended}
