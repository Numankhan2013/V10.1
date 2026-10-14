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
from marrow_bank_data import MICROBIOLOGY_PREFIX, app_marrow_records, load_sharded, microbiology_record  # noqa: E402
import microbiology_visuals  # noqa: E402


def main() -> None:
    # The committed shards are exactly what the normalizer makes from the raw JSONL.
    subprocess.run([sys.executable, str(ROOT / "tools/build_microbiology_marrow_bank.py"), "--check"], check=True)
    manifest = json.loads((ROOT / f"data/marrow/{MICROBIOLOGY_PREFIX}_manifest.json").read_text(encoding="utf-8"))
    raw_rows = [json.loads(line) for part in sorted((ROOT / "data/marrow/microbiology/source").glob("*.jsonl"))
                for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]

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
        assert tables == {t["table_id"] for t in raw.get("tables") or []}, q["id"]
        assert all(t["columns"] and t["rows"] for t in q["structuredExplanation"]["tables"]), q["id"]

    # Microbiology joins the app's Marrow records after the canonical ED8 three,
    # which stay exactly 2,711 questions.
    records = app_marrow_records()
    assert [r["subject"] for r in records] == ["Anatomy", "Biochemistry", "Physiology", "Microbiology"]
    assert sum(len(r["questions"]) for r in records[:3]) == 2711
    ids = [q["id"] for r in records for q in r["questions"]]
    assert len(ids) == len(set(ids))

    taxonomy = json.loads((ROOT / "data/marrow/topic_index_taxonomy.json").read_text(encoding="utf-8"))["subjects"]
    assert [t["id"] for t in taxonomy["Microbiology"]["topics"]] == [t["id"] for t in record["topics"]]

    visuals = microbiology_visuals.validate()
    bound = {f["questionId"] for f in visuals["figures"]}
    assert bound <= {q["id"] for q in questions}
    assert sum(len(r.get("images") or []) for r in raw_rows) == len(visuals["figures"])

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    for marker in (
        "SUBJECTS.push(record);",
        "function nkRenderMarrowOrdered(q)",
        "layout==='ordered-blocks'",
        "if(key.includes('microbiology')) return {key:'microbiology'",
        '<script defer src="microbiology_visual_metadata.js"></script>',
    ):
        assert page.count(marker) == 1, marker
    print(f"MICROBIOLOGY_MARROW_TEST_OK questions={len(questions)} topics={len(record['topics'])} "
          f"figures={len(visuals['figures'])} incomplete={manifest['incompleteTopics']}")


if __name__ == "__main__":
    main()
