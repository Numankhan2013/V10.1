#!/usr/bin/env python3
"""Validate deterministic Marrow Biochemistry chapter explanation rollout."""
from __future__ import annotations

import json

from inventory_marrow_explanations import DATA, enhanced_ids, load_sharded


def main() -> None:
    batch = json.loads((DATA / "explanation_biochem_ch01_v1.json").read_text(encoding="utf-8"))
    sample = json.loads((DATA / "explanation_biochem_gold_sample_v1.json").read_text(encoding="utf-8"))
    inventory = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    bank, source_sha = load_sharded("biochemistry_phase_a")
    expanded_bank, expanded_sha = load_sharded("biochemistry_ch001_028")
    legacy_manifest = json.loads((DATA / "biochemistry_phase_a_manifest.json").read_text(encoding="utf-8"))

    assert batch["scope"] == {
        "subject": "Biochemistry",
        "bank": "Marrow",
        "chapterId": "1",
        "chapterTitle": "Chemistry of Carbohydrates, Amino sugars and Mucopolysaccharides",
        "questions": 22,
        "status": "approved-rollout",
    }
    questions = batch["questions"]
    expected = {f"marrow__BIOCHEM_CH01_Q{i:03d}" for i in range(1, 23)}
    assert set(questions) == expected
    assert not (set(questions) & set(sample["questions"]))

    source_questions = {q["id"]: q for q in bank["questions"]}
    expanded_questions = {q["id"]: q for q in expanded_bank["questions"]}
    chapter_source = {q["id"] for q in bank["questions"] if str(q["chapterId"]) == "1"}
    assert source_sha == legacy_manifest["raw_sha256"]
    assert expanded_sha == inventory["sourceRawSha256"]["Biochemistry"]
    assert set(questions) <= chapter_source
    assert chapter_source == set(questions) | {"marrow__BIOCHEM_CH01_Q023"}
    assert all(expanded_questions[qid] == source_questions[qid] for qid in chapter_source)

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
    assert len(enhanced) == 184
    assert chapter_source <= enhanced
    assert inventory["summary"]["enhancementStatus"] == {
        "enhanced-reference": 184,
        "pending": 2310,
    }

    print(
        "MARROW_BIOCHEM_EXPLANATION_ROLLOUT_TEST_OK "
        "chapter=1 batch=22 chapter_total=23 approved_total=184 pending=2310 legacy_source=pinned expanded_source=pinned raw_source=unchanged"
    )


if __name__ == "__main__":
    main()
