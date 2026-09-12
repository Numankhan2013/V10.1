#!/usr/bin/env python3
"""Validate the current bounded Anatomy explanation rollout against canonical source."""
from __future__ import annotations

import json

from inventory_marrow_explanations import DATA, load_sharded

BATCH = "explanation_anatomy_ch06_q001_q007_v1.json"
EXPECTED_IDS = {f"marrow__ANAT_CH06_Q{i:03d}" for i in range(1, 8)}
EXPECTED_CANONICAL_SHA = "f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387"
EXPECTED_BATCH_BASE_SHA = "700cde07869068a7d3aadf77dc89d7bd85726530"


def main() -> None:
    batch = json.loads((DATA / BATCH).read_text(encoding="utf-8"))
    canonical, canonical_sha = load_sharded("anatomy_ch001_063")
    legacy, _ = load_sharded("anatomy_phase_a")

    assert canonical_sha == EXPECTED_CANONICAL_SHA
    assert len(canonical["questions"]) == 1115
    assert batch["scope"]["subject"] == "Anatomy"
    assert batch["scope"]["chapterId"] == "6"
    assert batch["scope"]["questionStart"] == 1
    assert batch["scope"]["questionEnd"] == 7
    assert batch["scope"]["questions"] == 7
    assert batch["scope"]["canonicalBaseSha"] == EXPECTED_BATCH_BASE_SHA
    questions = batch["questions"]
    assert set(questions) == EXPECTED_IDS

    canonical_by_id = {q["id"]: q for q in canonical["questions"]}
    legacy_by_id = {q["id"]: q for q in legacy["questions"]}
    for qid in EXPECTED_IDS:
        assert qid in canonical_by_id and qid in legacy_by_id
        source = canonical_by_id[qid]
        assert source == legacy_by_id[qid]
        assert str(source["chapterId"]) == "6"
        assert int(source["questionNumber"]) == int(qid.rsplit("Q", 1)[1])
        cfg = questions[qid]
        assert str(cfg.get("takeaway", "")).strip()
        display = str(cfg.get("displayText", "")).strip()
        assert display
        emphasis = cfg.get("emphasis", [])
        assert 1 <= len(emphasis) <= 4
        assert all(str(anchor) in display for anchor in emphasis)
        correct = int(source["correctOption"])
        wrong = {
            str(option.get("letter") or chr(64 + index)).lower()
            for index, option in enumerate(source["options"], 1)
            if index != correct
        }
        assert len(cfg.get("rationales", {})) == 3
        assert set(cfg["rationales"]) == wrong
        assert all(str(reason).strip() for reason in cfg["rationales"].values())

    q2 = questions["marrow__ANAT_CH06_Q002"]
    reconstruction = q2.get("reconstruction", {})
    assert reconstruction.get("status") == "needs_manual_review"
    for key in ("sourceProblem", "reconstructedContent", "evidenceBasis", "reviewNote"):
        assert reconstruction.get(key)
    assert canonical_by_id["marrow__ANAT_CH06_Q002"].get("reviewStatus") == "needs_manual_review"

    print("MARROW_ANATOMY_EXPLANATION_ROLLOUT_TEST_OK chapter=6 range=1-7 count=7 canonical_source=pinned legacy_equivalence=pinned q2=needs_manual_review")


if __name__ == "__main__":
    main()
