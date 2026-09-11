#!/usr/bin/env python3
"""Validate deterministic Marrow Biochemistry explanation rollout."""
from __future__ import annotations

import json

from inventory_marrow_explanations import DATA, enhanced_ids, load_sharded


RECONSTRUCTION_STATUSES = {"resolved_reconstruction", "needs_manual_review"}


def _validate_reconstruction(qid: str, cfg: dict) -> None:
    reconstruction = cfg.get("reconstruction")
    if reconstruction is None:
        return
    assert reconstruction.get("status") in RECONSTRUCTION_STATUSES, qid
    for field in ("sourceProblem", "reconstructedContent", "reviewNote"):
        assert str(reconstruction.get(field, "")).strip(), (qid, field)
    evidence = reconstruction.get("evidenceBasis")
    assert isinstance(evidence, list) and evidence, qid
    assert all(str(item).strip() for item in evidence), qid


def main() -> None:
    sample = json.loads((DATA / "explanation_biochem_gold_sample_v1.json").read_text(encoding="utf-8"))
    inventory = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    bank, source_sha = load_sharded("biochemistry_phase_a")
    source_questions = {q["id"]: q for q in bank["questions"]}
    sample_ids = set(sample["questions"])
    assert source_sha == inventory["sourceRawSha256"]["Biochemistry"]

    batch_paths = sorted(DATA.glob("explanation_biochem_ch*_v1.json"))
    assert batch_paths
    batch_ids = set()
    covered_chapters: dict[str, set[str]] = {}

    for path in batch_paths:
        batch = json.loads(path.read_text(encoding="utf-8"))
        scope = batch["scope"]
        assert scope["subject"] == "Biochemistry"
        assert scope["bank"] == "Marrow"
        assert scope["status"] == "approved-rollout"
        chapter = str(scope["chapterId"])
        questions = batch["questions"]
        assert len(questions) == int(scope["questions"])
        assert questions
        assert not (set(questions) & sample_ids)
        assert not (set(questions) & batch_ids)
        assert all(qid in source_questions for qid in questions)
        assert all(str(source_questions[qid]["chapterId"]) == chapter for qid in questions)

        source_order = []
        for qid, cfg in questions.items():
            source = source_questions[qid]
            source_order.append(int(source.get("questionNumber") or 0))
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
            _validate_reconstruction(qid, cfg)

        # Legacy whole-chapter rollout files intentionally omit their already-
        # approved gold-sample question, so their own question numbers can contain
        # one hole. New workload-bounded files declare explicit source bounds;
        # validate those bounds against every non-sample source item in the range.
        if "questionStart" in scope or "questionEnd" in scope:
            assert "questionStart" in scope and "questionEnd" in scope, path.name
            start = int(scope["questionStart"])
            end = int(scope["questionEnd"])
            assert start <= end, path.name
            expected_ids = {
                qid for qid, question in source_questions.items()
                if str(question["chapterId"]) == chapter
                and start <= int(question.get("questionNumber") or 0) <= end
                and qid not in sample_ids
            }
            assert set(questions) == expected_ids, path.name
            assert min(source_order) >= start and max(source_order) <= end, path.name

        batch_ids.update(questions)
        covered_chapters.setdefault(chapter, set()).update(questions)

    # A chapter may be intentionally split into workload-bounded files. For every
    # chapter with rollout work, the union of rollout + approved sample questions
    # must be a gap-free source-order prefix. Historical completed chapters remain
    # full prefixes; the current partial chapter may stop only at a clean boundary.
    for chapter, rollout_ids in covered_chapters.items():
        source_chapter = {
            qid for qid, question in source_questions.items()
            if str(question["chapterId"]) == chapter
        }
        approved_in_chapter = (rollout_ids | sample_ids) & source_chapter
        numbers = sorted(int(source_questions[qid].get("questionNumber") or 0) for qid in approved_in_chapter)
        assert numbers
        assert numbers == list(range(1, max(numbers) + 1)), (chapter, numbers)

    enhanced = enhanced_ids()
    biochemistry_enhanced = len(sample_ids) + len(batch_ids)
    assert sample_ids | batch_ids <= enhanced
    assert len(enhanced) >= 142 + biochemistry_enhanced
    assert inventory["summary"]["enhancementStatus"] == {
        "enhanced-reference": len(enhanced),
        "pending": 2115 - len(enhanced),
    }

    print(
        "MARROW_BIOCHEM_EXPLANATION_ROLLOUT_TEST_OK "
        f"chapters={','.join(sorted(covered_chapters, key=int))} "
        f"batch_questions={len(batch_ids)} biochemistry_enhanced={biochemistry_enhanced} "
        f"approved_total={len(enhanced)} pending={2115-len(enhanced)} raw_source=unchanged"
    )


if __name__ == "__main__":
    main()
