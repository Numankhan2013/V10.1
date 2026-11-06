#!/usr/bin/env python3
"""The corrections ledger is well formed, and the correction pass changes exactly what it should.

The full ledger is applied to the real banks by build_app_data.py, which fails on any entry
whose question or text is gone; this test covers the mechanics on small synthetic questions.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_corrections import CorrectionError, apply_corrections, load_ledger, mend_bold  # noqa: E402


def question(qid: str = "q1") -> dict:
    text = "Correct option B - Anterior fossa\n\nMiddl**e fossa (Option A):** Battle's sign"
    return {
        "id": qid, "question": "Raccoon eyes come from which fossa? serum pH 6.5",
        "options": [{"letter": "A", "text": "Anterior"}, {"letter": "B", "text": "D) Middle"}],
        "correctOption": 2, "correctAnswerText": "D) Middle", "explanation": text,
        "structuredExplanation": {"text": text, "blocks": [
            {"type": "heading", "text": "Correct option B - Anterior fossa"},
            {"type": "paragraph", "text": "Middl**e fossa (Option A):** Battle's sign"},
            {"type": "bullets", "items": [{"text": "a p**ale waxy disc** here"}, "plain string item"]}],
            "tables": [{"title": "", "rows": [["I**mmediate cause:** rupture", "x"]]}, {"rows": None}]},
    }


def main() -> None:
    cases = {
        "a p**ale waxy disc** due": "a **pale waxy disc** due",
        "I**mmediate Cause:** R": "**Immediate Cause:** R",
        "into the formu**la:**": "into the **formula:**",
        "plain **bold** text": "plain **bold** text",
        "is**s**ue": "is**s**ue",
        "X**2** and H**2**O": "X**2** and H**2**O",
        "**open** b**old**": "**open** **bold**",
    }
    for raw, want in cases.items():
        assert mend_bold(raw) == want, (raw, mend_bold(raw), want)

    ledger = load_ledger()
    assert len(ledger) >= 150, len(ledger)
    for entry in ledger:
        for edit in entry.get("edits", []) + entry.get("stemEdits", []):
            assert edit["find"] and edit["find"] != edit["replace"], entry["id"]

    entry = {"id": "q1", "reason": "test",
             "edits": [{"find": "Correct option B - Anterior", "replace": "Correct option A - Anterior"},
                       {"find": "Middl**e fossa (Option A):**", "replace": "**Middle fossa (Option B):**"}],
             "stemEdits": [{"find": "serum pH 6.5", "replace": "urine pH 6.5"}],
             "optionText": {"2": "Middle"}, "correctOption": 1}
    record = {"questions": [question()]}
    stats = apply_corrections([record], [entry])
    q = record["questions"][0]
    assert stats["corrected"] == 1 and stats["boldMended"] >= 2, stats
    blocks = q["structuredExplanation"]["blocks"]
    assert blocks[0]["text"] == "Correct option A - Anterior fossa"
    assert blocks[1]["text"] == "**Middle fossa (Option B):** Battle's sign"
    assert blocks[2]["items"][0]["text"] == "a **pale waxy disc** here"
    assert q["structuredExplanation"]["tables"][0]["rows"][0][0] == "**Immediate cause:** rupture"
    assert "Correct option A" in q["explanation"] and "Correct option A" in q["structuredExplanation"]["text"]
    assert q["question"].endswith("urine pH 6.5")
    assert q["options"][1]["text"] == "Middle" and q["correctOption"] == 1 and q["correctAnswerText"] == "Anterior"

    def fails(records: list[dict], ledger_: list[dict], why: str) -> None:
        try:
            apply_corrections(records, ledger_)
        except CorrectionError:
            return
        raise AssertionError(why)

    table = [{"columns": ["Statements"], "rows": [["1. One"], ["2. Two"]]}]
    tabled = {"questions": [question()]}
    apply_corrections([tabled], [{"id": "q1", "reason": "statements", "stemTables": table}])
    assert tabled["questions"][0]["stemTables"] == table
    fails([{"questions": [question()]}], [{"id": "q1", "reason": "x", "stemTables": [{"rows": []}]}],
          "a statement table without rows must fail")
    fails([{"questions": [question()]}], [{**entry, "id": "gone"}], "an entry for a missing question must fail")
    fails([{"questions": [question()]}], [{**entry, "edits": [{"find": "not there", "replace": "x"}]}],
          "text that is not in the question must fail")
    flat_only = copy.deepcopy(entry)
    flat_only["edits"] = [{"find": "Correct option B - Anterior fossa\n\nMiddl", "replace": "x"}]
    fails([{"questions": [question()]}], [flat_only], "text found only in the flat copy must fail")
    fails([{"questions": [question()]}, {"questions": [question()]}], [entry], "a question twice must fail")
    fails([{"questions": [question()]}], [{**entry, "correctOption": 5}], "a key outside the options must fail")
    print(f"SOURCE_CORRECTIONS_TEST_OK entries={len(ledger)}")


if __name__ == "__main__":
    main()
