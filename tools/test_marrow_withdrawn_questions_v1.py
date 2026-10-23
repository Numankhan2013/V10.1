#!/usr/bin/env python3
"""Withdrawn Marrow questions: recorded, absent from the app, source intact.

The canonical shards keep every extracted question. A question is withheld only
when its stem refers to a picture the bank cannot release, and the withdrawal
ledger must say why and what would restore it. This test fails if a withdrawn
question leaks back into the app records, if its topic counts stop matching, or
if the source record disappears.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_microbiology_marrow_bank as builder  # noqa: E402
from marrow_bank_data import (  # noqa: E402
    app_marrow_records, expanded_marrow_records, microbiology_record, withdrawn_questions,
)

LEDGER = ROOT / "data/marrow/withdrawn_questions_v1.json"

# The 13 questions once listed as pending used "shown by" verbally ("Tumbling
# motility is shown by ___"), not as an image reference. They must keep shipping.
FALSE_POSITIVE_IDS = {
    "marrow__MICRO_CH05_Q004", "marrow__MICRO_CH05_Q005", "marrow__MICRO_CH06_Q022",
    "marrow__MICRO_CH07_Q005", "marrow__MICRO_CH07_Q033", "marrow__MICRO_CH09_Q035",
    "marrow__MICRO_CH10_Q002", "marrow__MICRO_CH10_Q017", "marrow__MICRO_CH10_Q022",
    "marrow__MICRO_CH10_Q038", "marrow__MICRO_CH12_Q004", "marrow__MICRO_CH22_Q021",
    "marrow__MICRO_CH24_Q011",
}


def main() -> None:
    payload = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert payload["schemaVersion"] == 1
    entries = {entry["id"]: entry for entry in payload["questions"]}
    assert set(entries) == {
        "marrow__ANAT_CH45_Q004", "marrow__BIOCHEM_CH17_Q014", "marrow__MICRO_CH18_Q013",
    }, sorted(entries)
    assert withdrawn_questions() == entries

    source = {}
    for record in expanded_marrow_records() + [microbiology_record()]:
        for question in record["questions"]:
            source[question["id"]] = question
    for qid, entry in entries.items():
        question = source[qid]
        assert entry["status"] == "withdrawn"
        for field in ("subject", "chapterId", "questionNumber"):
            assert entry[field] == question[field], f"{qid}: ledger {field} drifted"
        assert entry["reason"].strip() and entry["evidence"].strip() and entry["restoreWhen"].strip()
        assert "figure" in entry["reason"].lower() or "image" in entry["reason"].lower(), qid

    app_records = app_marrow_records()
    app_ids = {question["id"] for record in app_records for question in record["questions"]}
    assert not (set(entries) & app_ids), "a withdrawn question is still shipped"
    assert len(source) - len(app_ids) == len(entries), "withdrawal removed questions it did not record"
    assert len(app_ids) == 3434, len(app_ids)

    for record in app_records:
        counts = Counter(str(question["chapterId"]) for question in record["questions"])
        assert sum(topic["questionCount"] for topic in record["topics"]) == len(record["questions"]), record["subject"]
        for topic in record["topics"]:
            assert topic["questionCount"] == counts.get(str(topic["id"]), 0), (
                f"{record['subject']} topic {topic['id']} count drifted"
            )

    # The 13 verbal "shown by" questions were a cue false positive, not debt.
    assert FALSE_POSITIVE_IDS <= set(app_ids)
    assert not (FALSE_POSITIVE_IDS & set(entries))
    unbound = [
        f"MICRO_CH{int(q['module_index']):02d}_Q{int(q['question_number']):03d}"
        for q in builder.load_source()[0]
        if builder.QUESTION_FIGURE_CUE.search(str(q.get("question_stem") or ""))
        and not any(image.get("location") == "question_stem" for image in (q.get("images") or []))
    ]
    assert unbound == ["MICRO_CH18_Q013"], unbound
    assert set(unbound) <= builder.WITHDRAWN_QUESTION_FIGURES

    # A released figure was mis-bound as explanation; it must now mount before
    # the answer for the physiology question whose stem says "the picture shows".
    metadata = (ROOT / "app/src/main/assets/marrow_visual_metadata.js").read_text(encoding="utf-8")
    visuals = json.loads(metadata.removeprefix("window.MARROW_VISUALS=").removesuffix(";\n"))
    physiology = visuals["marrow__PHYSIO_CH35_Q020"]
    assert any(figure["role"] == "question" for figure in physiology), physiology

    print(
        "MARROW_WITHDRAWN_QUESTIONS_TEST_OK "
        f"withdrawn={len(entries)} shipped={len(app_ids)} source={len(source)} cue_false_positives={len(FALSE_POSITIVE_IDS)}"
    )


if __name__ == "__main__":
    main()
