#!/usr/bin/env python3
"""Validate the bounded Marrow Biochemistry explanation candidate against source."""
from __future__ import annotations

import json

from inventory_marrow_explanations import DATA, load_sharded


def main() -> None:
    candidate = json.loads((DATA / "explanation_biochem_gold_sample_v1.json").read_text(encoding="utf-8"))
    inventory = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    bank, source_sha = load_sharded("biochemistry_phase_a")

    assert candidate["scope"] == {
        "subject": "Biochemistry",
        "bank": "Marrow",
        "questions": 20,
        "status": "candidate-human-review",
    }
    assert candidate["referenceGrammar"] == {
        "approvedQuestions": 142,
        "anatomy": 62,
        "physiology": 80,
    }

    sample_ids = {row["id"] for row in inventory["biochemistryGoldSample"]}
    questions = candidate["questions"]
    assert len(questions) == 20
    assert set(questions) == sample_ids

    source_questions = {q["id"]: q for q in bank["questions"]}
    assert set(questions) <= set(source_questions)
    assert source_sha == inventory["sourceRawSha256"]["Biochemistry"]

    for qid, cfg in questions.items():
        source = source_questions[qid]
        assert str(cfg.get("takeaway", "")).strip()
        assert str(cfg.get("displayText", "")).strip()
        assert cfg.get("emphasis")
        assert "sourceText" not in cfg
        options = source["options"]
        correct = int(source["correctOption"])
        wrong_letters = {
            str(option.get("letter") or chr(64 + index)).lower()
            for index, option in enumerate(options, 1)
            if index != correct
        }
        assert len(cfg["rationales"]) == 3
        assert set(cfg["rationales"]) == wrong_letters
        assert all(str(reason).strip() for reason in cfg["rationales"].values())

    # The approved 142 remain the reference set until the user reviews this sample.
    anatomy = json.loads((DATA / "explanation_gold_pilot.json").read_text(encoding="utf-8"))["questions"]
    physiology, _ = load_sharded("explanation_physio_pilot")
    approved_ids = set(anatomy) | set(physiology["questions"])
    assert len(approved_ids) == 142
    assert not (approved_ids & set(questions))

    print(
        "MARROW_BIOCHEM_EXPLANATION_SAMPLE_TEST_OK "
        "candidate=20 approved_reference=142 rationales=60 raw_source=unchanged"
    )


if __name__ == "__main__":
    main()
