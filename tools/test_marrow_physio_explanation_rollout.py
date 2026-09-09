#!/usr/bin/env python3
"""Validate deterministic Marrow Physiology chapter explanation rollout."""
from __future__ import annotations

from inventory_marrow_explanations import DATA, enhanced_ids, load_sharded


def main() -> None:
    pilot, _ = load_sharded("explanation_physio_pilot")
    inventory = __import__("json").loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    bank, source_sha = load_sharded("physiology_ch001_033")
    source_questions = {q["id"]: q for q in bank["questions"]}
    pilot_ids = set(pilot["questions"])
    assert len(pilot_ids) == 80
    assert source_sha == inventory["sourceRawSha256"]["Physiology"]

    batch_paths = sorted(DATA.glob("explanation_physio_ch*_v1.json"))
    assert batch_paths
    batch_ids = set()
    covered_chapters = set()

    for path in batch_paths:
        batch = __import__("json").loads(path.read_text(encoding="utf-8"))
        scope = batch["scope"]
        assert scope["subject"] == "Physiology"
        assert scope["bank"] == "Marrow"
        assert scope["status"] == "approved-rollout"
        chapter = str(scope["chapterId"])
        questions = batch["questions"]
        assert len(questions) == int(scope["questions"])
        assert questions
        assert not (set(questions) & pilot_ids)
        assert not (set(questions) & batch_ids)
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
            reconstruction = cfg.get("reconstruction")
            if reconstruction is not None:
                assert reconstruction.get("status") in {"resolved_reconstruction", "needs_manual_review"}
                assert str(reconstruction.get("sourceProblem", "")).strip()
                assert str(reconstruction.get("reconstructedContent", "")).strip()
                evidence = reconstruction.get("evidenceBasis")
                assert isinstance(evidence, list) and evidence and all(str(item).strip() for item in evidence)
                assert str(reconstruction.get("reviewNote", "")).strip()

        source_chapter = {
            qid for qid, question in source_questions.items()
            if str(question["chapterId"]) == chapter
        }
        approved_pilot_in_chapter = source_chapter & pilot_ids
        assert source_chapter == set(questions) | approved_pilot_in_chapter
        batch_ids.update(questions)
        covered_chapters.add(chapter)

    enhanced = enhanced_ids()
    assert pilot_ids | batch_ids <= enhanced
    assert inventory["summary"]["enhancementStatus"] == {
        "enhanced-reference": len(enhanced),
        "pending": 2115 - len(enhanced),
    }

    print(
        "MARROW_PHYSIO_EXPLANATION_ROLLOUT_TEST_OK "
        f"chapters={','.join(sorted(covered_chapters, key=int))} "
        f"batch_questions={len(batch_ids)} physiology_enhanced={len(pilot_ids)+len(batch_ids)} "
        f"approved_total={len(enhanced)} pending={2115-len(enhanced)} raw_source=unchanged"
    )


if __name__ == "__main__":
    main()
