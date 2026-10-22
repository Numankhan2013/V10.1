#!/usr/bin/env python3
"""Microbiology Marrow bank: source -> shards -> app wiring, without generated artifacts."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from app_page import assemble  # noqa: E402
from marrow_bank_data import (  # noqa: E402
    MICROBIOLOGY_PREFIX, app_marrow_records, load_sharded, microbiology_record, withdrawn_questions,
)
import microbiology_visuals  # noqa: E402


def main() -> None:
    # The committed shards are exactly what the normalizer makes from the raw JSONL.
    subprocess.run([sys.executable, str(ROOT / "tools/build_microbiology_marrow_bank.py"), "--check"], check=True)
    manifest = json.loads((ROOT / f"data/marrow/{MICROBIOLOGY_PREFIX}_manifest.json").read_text(encoding="utf-8"))
    # Every JSONL part, mapped onto the full PDF pages and app modules (PART_LAYOUT).
    from build_microbiology_marrow_bank import (
        load_source, MODULE_OVERRIDES, QUESTION_FIGURE_CUE, PENDING_QUESTION_FIGURES,
        WITHDRAWN_QUESTION_FIGURES, check_question_figure,
    )
    raw_rows = load_source()[0]

    record = microbiology_record()
    questions = record["questions"]
    assert record["subject"] == "Microbiology" and record["bank"] == "Marrow"
    assert len(questions) == len(raw_rows) == manifest["questions"]
    assert [q["mcqId"] for q in questions] == [r["mcq_id"] for r in raw_rows], "source order changed"

    # Every stem, option and answer key equals the raw extraction.
    for q, raw in zip(questions, raw_rows):
        assert q["question"] == raw["question_stem"].strip(), q["id"]
        assert [o["text"] for o in q["options"]] == [o["text"].strip() for o in raw["options"]], q["id"]
        assert "ABCD"[q["correctOption"] - 1] == raw["correct_option"], q["id"]
        assert q["chapterId"] == str(raw["module_index"]) and q["questionNumber"] == raw["question_number"], q["id"]
        assert q["id"] == f"marrow__MICRO_CH{raw['module_index']:02d}_Q{raw['question_number']:03d}"
        blocks = q["structuredExplanation"]["blocks"]
        assert q["structuredExplanation"]["layout"] == "ordered-blocks" and blocks, q["id"]
        tables = {t["table_id"] for t in q["structuredExplanation"]["tables"]}
        source_tables = {t["table_id"] for t in raw.get("tables") or []}
        if raw.get("_schema") == 2:
            source_tables |= {t["table_id"] for p in raw.get("pearls") or [] for t in p.get("tables") or []}
        assert tables == source_tables, q["id"]
        # Source peer statistics travel unchanged; the keyed option's poll is the
        # "got this right" figure (same check as against the PDF).
        stats = q["sourceStats"]
        assert stats["peerAccuracyPercent"] == raw["peer_accuracy_percentage"], q["id"]
        assert stats["optionPollPercent"] == {o["id"]: o["poll_percentage"] for o in raw["options"]}, q["id"]
        assert stats["optionPollPercent"]["ABCD"[q["correctOption"] - 1]] == stats["peerAccuracyPercent"], q["id"]
        assert all(t["columns"] and t["rows"] for t in q["structuredExplanation"]["tables"]), q["id"]

    # Microbiology joins the app's Marrow records after the canonical ED8 three,
    # which ship 2,711 source questions minus the ones recorded as withdrawn.
    records = app_marrow_records()
    assert [r["subject"] for r in records] == ["Anatomy", "Biochemistry", "Physiology", "Microbiology"]
    canonical_withdrawn = {
        qid for qid in withdrawn_questions() if not qid.startswith("marrow__MICRO_")
    }
    assert sum(len(r["questions"]) for r in records[:3]) == 2711 - len(canonical_withdrawn)
    ids = [q["id"] for r in records for q in r["questions"]]
    assert len(ids) == len(set(ids))

    taxonomy = json.loads((ROOT / "data/marrow/topic_index_taxonomy.json").read_text(encoding="utf-8"))["subjects"]
    assert [t["id"] for t in taxonomy["Microbiology"]["topics"]] == [t["id"] for t in record["topics"]]

    for topic in record["topics"]:
        override = MODULE_OVERRIDES.get(int(topic["id"]))
        if override:
            assert topic["title"] == override["title"] and topic["sourceQuestionTotal"] == override["total"]
    visuals = microbiology_visuals.validate()
    bound = {f["questionId"] for f in visuals["figures"]}
    assert bound <= {q["id"] for q in questions}
    assert sum(len(r.get("images") or []) for r in raw_rows) == len(visuals["figures"])

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    # SUBJECTS.push(record) twice: the Marrow-only fallback and the structured
    # PrepLadder Microbiology record that rides along in MARROW_DATA.
    assert page.count("SUBJECTS.push(record);") == 2
    for marker in (
        "function nkRenderMarrowOrdered(q)",
        "function nkSourcePollPercent(q,o,revealed=true)",
        "nkUworldOptionPercentage(q,o,locked):nkSourcePollPercent(q,o,locked)",
        "${time}${nkSourceCohort(q)}",
        "layout==='ordered-blocks'",
        "if(key.includes('microbiology')) return {key:'microbiology'",
        '<script defer src="microbiology_visual_metadata.js"></script>',
    ):
        assert page.count(marker) == 1, marker
    # A stem that points at a picture must have a released question figure, so
    # the learner is never asked about an image that is not there.
    for q, raw in zip(questions, raw_rows):
        stem = raw["question_stem"].strip()
        if not QUESTION_FIGURE_CUE.search(stem):
            continue
        figures = (q.get("structuredExplanation") or {}).get("figures") or []
        has_question_figure = any(f.get("location") == "question_stem" for f in figures)
        if not has_question_figure:
            assert (
                q["sourceQuestionId"] in PENDING_QUESTION_FIGURES
                or q["sourceQuestionId"] in WITHDRAWN_QUESTION_FIGURES
            ), (
                f"{q['id']} points at a picture the bank does not bind and is not a known pending/withdrawn question"
            )
    # The builder must run the gate over every question it ships.
    import build_microbiology_marrow_bank as builder
    checked: list[str] = []
    original_gate = builder.check_question_figure
    builder.check_question_figure = lambda qid, stem, images: checked.append(qid)
    try:
        builder.normalize(raw_rows)
    finally:
        builder.check_question_figure = original_gate
    assert len(checked) == len(questions), "the builder must check every question for a figure cue"
    assert all(q["sourceQuestionId"] in checked for q in questions), "the gate must run for every question"

    # The gate must fire for a question that is not on the pending list.
    visual_stem = "The structure marked in the image is which of the following?"
    try:
        check_question_figure("MICRO_CH99_Q999", visual_stem, [])
    except SystemExit as error:
        assert "stem refers to a figure the bank does not bind" in str(error), error
    else:
        raise AssertionError("the figure gate must reject a stem that points at an unbound picture")
    # A stem with a released question figure passes, and a stem without a cue is not checked.
    check_question_figure("MICRO_CH99_Q999", visual_stem,
                          [{"image_id": "x", "location": "question_stem"}])
    check_question_figure("MICRO_CH99_Q999", "Which organism causes cholera?", [])
    # A bare "shown by" is ordinary question wording, not visual deixis.
    check_question_figure("MICRO_CH99_Q999", "Tumbling motility is shown by _______.", [])
    # A pending question is reported, not blocked.
    for qid in PENDING_QUESTION_FIGURES:
        check_question_figure(qid, "Tumbling motility is shown by _______.", [])

    print(f"MICROBIOLOGY_MARROW_TEST_OK questions={len(questions)} topics={len(record['topics'])} "
          f"figures={len(visuals['figures'])} incomplete={manifest['incompleteTopics']}")


if __name__ == "__main__":
    main()
