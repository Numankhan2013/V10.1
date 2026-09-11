#!/usr/bin/env python3
"""Validate all approved Marrow Physiology explanation rollouts on canonical corpus."""
from __future__ import annotations

import json
from collections import defaultdict

from inventory_marrow_explanations import DATA, enhanced_ids, load_sharded


def main() -> None:
    pilot, _ = load_sharded("explanation_physio_pilot")
    inventory = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    bank, source_sha = load_sharded("physiology_ch001_043")
    source_questions = {q["id"]: q for q in bank["questions"]}
    pilot_ids = set(pilot["questions"])
    assert len(pilot_ids) == 80
    assert source_sha == inventory["sourceRawSha256"]["Physiology"]
    assert len(source_questions) == 1014

    batch_paths = sorted(DATA.glob("explanation_physio_ch*_v1.json"))
    assert batch_paths
    batch_ids: set[str] = set()
    chapter_batch_ids: dict[str, set[str]] = defaultdict(set)

    for path in batch_paths:
        batch = json.loads(path.read_text(encoding="utf-8"))
        scope = batch["scope"]
        assert scope["subject"] == "Physiology"
        assert scope["bank"] == "Marrow"
        assert scope["status"] == "approved-rollout"
        chapter = str(scope["chapterId"])
        questions = batch["questions"]
        question_ids = set(questions)
        assert len(questions) == int(scope["questions"])
        assert questions
        assert not (question_ids & pilot_ids)
        assert not (question_ids & batch_ids)
        assert all(qid in source_questions for qid in questions)
        assert all(str(source_questions[qid]["chapterId"]) == chapter for qid in questions)

        for qid, cfg in questions.items():
            source = source_questions[qid]
            assert str(cfg.get("takeaway", "")).strip()
            assert str(cfg.get("displayText", "")).strip()
            assert 1 <= len(cfg.get("emphasis", [])) <= 4
            assert all(str(phrase) in str(cfg["displayText"]) for phrase in cfg.get("emphasis", []))
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

        batch_ids.update(question_ids)
        chapter_batch_ids[chapter].update(question_ids)

    # A chapter may be represented by multiple approved files (for example
    # Chapter 10 Q1–13 + Q14–18). Validate completeness on the chapter union,
    # not on each individual file.
    for chapter, approved_ids in chapter_batch_ids.items():
        source_chapter = {
            qid for qid, question in source_questions.items()
            if str(question["chapterId"]) == chapter
        }
        approved_pilot_in_chapter = source_chapter & pilot_ids
        assert source_chapter == approved_ids | approved_pilot_in_chapter

    enhanced = enhanced_ids()
    assert pilot_ids | batch_ids <= enhanced
    total = int(inventory["summary"]["questions"])
    assert total == 2711
    assert inventory["summary"]["enhancementStatus"] == {
        "enhanced-reference": len(enhanced),
        "pending": total - len(enhanced),
    }

    covered = sorted(chapter_batch_ids, key=int)
    print(
        "MARROW_PHYSIO_EXPLANATION_ROLLOUT_TEST_OK "
        f"chapters={','.join(covered)} batch_questions={len(batch_ids)} "
        f"physiology_enhanced={len(pilot_ids | batch_ids)} "
        f"approved_total={len(enhanced)} pending={total-len(enhanced)} "
        "corpus=2711 raw_source=unchanged"
    )


if __name__ == "__main__":
    main()
