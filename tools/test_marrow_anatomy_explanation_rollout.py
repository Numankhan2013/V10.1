#!/usr/bin/env python3
"""Validate approved bounded Anatomy explanation rollouts against canonical source."""
from __future__ import annotations

import json

from inventory_marrow_explanations import DATA, load_sharded

EXPECTED_CANONICAL_SHA = "f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387"
BATCHES = (
    ("explanation_anatomy_ch06_q001_q007_v1.json", 6, 1, 7, "700cde07869068a7d3aadf77dc89d7bd85726530"),
    ("explanation_anatomy_ch06_q008_q018_v1.json", 6, 8, 18, "e01cc0b9a8e62885d29b0c2e7ac6417ce8c96f05"),
    ("explanation_anatomy_ch06_q019_q025_v1.json", 6, 19, 25, "0c57fd4deb0a0ffb6ea57865bef56ac00b52c1e0"),
    ("explanation_anatomy_ch07_q001_q010_v1.json", 7, 1, 10, "105cf02e358d8f869d745e698fc4faa32d777c92"),
    ("explanation_anatomy_ch07_q011_q021_v1.json", 7, 11, 21, "cb3f44b95aca5030b8b72afc9654a1b135ff96de"),
)


def validate_batch(canonical_by_id: dict, legacy_by_id: dict, filename: str, chapter: int, start: int, end: int, base_sha: str) -> None:
    batch = json.loads((DATA / filename).read_text(encoding="utf-8"))
    expected_ids = {f"marrow__ANAT_CH{chapter:02d}_Q{i:03d}" for i in range(start, end + 1)}
    scope = batch["scope"]
    assert scope["subject"] == "Anatomy" and scope["bank"] == "Marrow"
    assert scope["chapterId"] == str(chapter)
    assert scope["questionStart"] == start and scope["questionEnd"] == end
    assert scope["questions"] == end - start + 1
    assert scope["status"] == "approved-rollout"
    assert scope["canonicalBaseSha"] == base_sha
    questions = batch["questions"]
    assert set(questions) == expected_ids
    for qid in expected_ids:
        assert qid in canonical_by_id and qid in legacy_by_id
        source = canonical_by_id[qid]
        assert source == legacy_by_id[qid]
        assert str(source["chapterId"]) == str(chapter)
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


def validate_reconstruction(questions: dict, canonical_by_id: dict, qid: str) -> None:
    reconstruction = questions[qid].get("reconstruction", {})
    assert reconstruction.get("status") == "needs_manual_review"
    for key in ("sourceProblem", "reconstructedContent", "evidenceBasis", "reviewNote"):
        assert str(reconstruction.get(key, "")).strip()
    assert canonical_by_id[qid].get("reviewStatus") == "needs_manual_review"


def main() -> None:
    canonical, canonical_sha = load_sharded("anatomy_ch001_063")
    legacy, _ = load_sharded("anatomy_phase_a")
    assert canonical_sha == EXPECTED_CANONICAL_SHA
    assert len(canonical["questions"]) == 1115
    canonical_by_id = {q["id"]: q for q in canonical["questions"]}
    legacy_by_id = {q["id"]: q for q in legacy["questions"]}
    for args in BATCHES:
        validate_batch(canonical_by_id, legacy_by_id, *args)

    q1_7 = json.loads((DATA / BATCHES[0][0]).read_text(encoding="utf-8"))["questions"]
    q19_25 = json.loads((DATA / BATCHES[2][0]).read_text(encoding="utf-8"))["questions"]
    validate_reconstruction(q1_7, canonical_by_id, "marrow__ANAT_CH06_Q002")
    validate_reconstruction(q19_25, canonical_by_id, "marrow__ANAT_CH06_Q024")

    print(
        "MARROW_ANATOMY_EXPLANATION_ROLLOUT_TEST_OK "
        "chapter6=1-25 chapter7=1-21 count=46 canonical_source=pinned "
        "legacy_equivalence=pinned q2=needs_manual_review q24=needs_manual_review"
    )


if __name__ == "__main__":
    main()
