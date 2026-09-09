#!/usr/bin/env python3
"""Validate deterministic Marrow Biochemistry chapter explanation rollouts."""
from __future__ import annotations

import json

from inventory_marrow_explanations import DATA, enhanced_ids, load_sharded


def main() -> None:
    chapter_1 = json.loads((DATA / "explanation_biochem_ch01_v1.json").read_text(encoding="utf-8"))
    chapter_4 = json.loads((DATA / "explanation_biochem_ch04_v1.json").read_text(encoding="utf-8"))
    sample = json.loads((DATA / "explanation_biochem_gold_sample_v1.json").read_text(encoding="utf-8"))
    inventory = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    bank, source_sha = load_sharded("biochemistry_phase_a")

    assert chapter_1["scope"] == {
        "subject": "Biochemistry",
        "bank": "Marrow",
        "chapterId": "1",
        "chapterTitle": "Chemistry of Carbohydrates, Amino sugars and Mucopolysaccharides",
        "questions": 22,
        "status": "approved-rollout",
    }
    assert chapter_4["scope"] == {
        "subject": "Biochemistry",
        "bank": "Marrow",
        "chapterId": "4",
        "chapterTitle": "HMP shunt pathway, Fructose , Galactose metabolism",
        "questions": 10,
        "status": "approved-rollout",
    }
    chapter_1_questions = chapter_1["questions"]
    chapter_4_questions = chapter_4["questions"]
    expected_chapter_1 = {f"marrow__BIOCHEM_CH01_Q{i:03d}" for i in range(1, 23)}
    expected_chapter_4 = {
        f"marrow__BIOCHEM_CH04_Q{i:03d}" for i in range(1, 12) if i != 5
    }
    assert set(chapter_1_questions) == expected_chapter_1
    assert set(chapter_4_questions) == expected_chapter_4
    questions = {**chapter_1_questions, **chapter_4_questions}
    assert len(questions) == len(chapter_1_questions) + len(chapter_4_questions)
    assert not (set(questions) & set(sample["questions"]))
    assert all(
        all(str(phrase) in str(cfg["displayText"]) for phrase in cfg["emphasis"])
        for cfg in chapter_4_questions.values()
    )

    source_questions = {q["id"]: q for q in bank["questions"]}
    chapter_1_source = {q["id"] for q in bank["questions"] if str(q["chapterId"]) == "1"}
    chapter_4_source = {q["id"] for q in bank["questions"] if str(q["chapterId"]) == "4"}
    assert source_sha == inventory["sourceRawSha256"]["Biochemistry"]
    assert set(chapter_1_questions) <= chapter_1_source
    assert set(chapter_4_questions) <= chapter_4_source
    assert chapter_1_source == set(chapter_1_questions) | {"marrow__BIOCHEM_CH01_Q023"}
    assert chapter_4_source == set(chapter_4_questions) | {"marrow__BIOCHEM_CH04_Q005"}

    for qid, cfg in questions.items():
        source = source_questions[qid]
        assert str(cfg.get("takeaway", "")).strip()
        assert str(cfg.get("displayText", "")).strip()
        assert 1 <= len(cfg.get("emphasis", [])) <= 4
        assert "sourceText" not in cfg
        correct = int(source["correctOption"])
        wrong_letters = {
            str(option.get("letter") or chr(64 + index)).lower()
            for index, option in enumerate(source["options"], 1)
            if index != correct
        }
        assert len(cfg.get("rationales", {})) == 3
        assert set(cfg["rationales"]) == wrong_letters
        assert all(str(reason).strip() for reason in cfg["rationales"].values())

    enhanced = enhanced_ids()
    assert len(enhanced) == 194
    assert chapter_1_source <= enhanced
    assert chapter_4_source <= enhanced
    assert inventory["summary"]["enhancementStatus"] == {
        "enhanced-reference": 194,
        "pending": 1921,
    }

    print(
        "MARROW_BIOCHEM_EXPLANATION_ROLLOUT_TEST_OK "
        "chapters=1,4 batch=32 chapter_totals=23,11 approved_total=194 pending=1921 raw_source=unchanged"
    )


if __name__ == "__main__":
    main()
