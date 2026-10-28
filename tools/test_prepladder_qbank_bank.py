#!/usr/bin/env python3
"""PrepLadder QBank (web export): shards current, structure and content clean, figures listed, app wired."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import prepladder_qbank_bank as bank  # noqa: E402
from test_marrow_qbank_bank import TAG, ZERO_WIDTH, texts  # noqa: E402

# Professional parts as the owner set them (Home groups); supplements keep their First/Second Prof.
PROF = {"Forensic Medicine": "third", "Community Medicine": "third", "ENT": "third", "Ophthalmology": "third",
        "Obstetrics & Gynaecology": "final", "Paediatrics": "final", "Surgery": "final", "Medicine": "final",
        "Radiology": "final-minor", "Anaesthesia": "final-minor", "Orthopaedics": "final-minor",
        "Psychiatry": "final-minor", "Dermatology": "final-minor"}


def check_question(q: dict, slug: str, topic_ids: set[str]) -> None:
    assert q["chapterId"] in topic_ids and q["bank"] == "PrepLadder", q["id"]
    assert q["subject"] == bank.SUBJECTS[slug]["subject"], q["id"]
    assert len(q["options"]) == 4 and q["correctOption"] in (1, 2, 3, 4), q["id"]
    assert q["correctAnswerText"] == q["options"][q["correctOption"] - 1]["text"], q["id"]
    assert q["explanationFormat"] == "structured", q["id"]
    data = q["structuredExplanation"]
    assert data["layout"] == "ordered-blocks" and data["blocks"], q["id"]
    table_ids = {t["table_id"] for t in data["tables"]}
    for b in data["blocks"]:
        assert b["type"] in ("paragraph", "heading", "bullets", "table"), (q["id"], b["type"])
        if b["type"] == "table":
            assert b["table_id"] in table_ids, q["id"]
    for t in data["tables"]:
        assert len(t["columns"]) >= 2 and all(len(r) == len(t["columns"]) for r in t["rows"]), q["id"]
    for text in texts(q):
        assert not ZERO_WIDTH.search(text), f"{q['id']}: watermark character left in {text[:60]!r}"
        assert not TAG.search(text), f"{q['id']}: raw HTML left in {text[:80]!r}"
        assert "@neet" not in text and "Correct answer:" not in text, f"{q['id']}: export chrome left"
        assert text.count("**") % 2 == 0, f"{q['id']}: unbalanced bold in {text[:80]!r}"


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/prepladder_qbank_bank.py"), "--check"], check=True)
    page = (ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8")
    build = (ROOT / "tools/build_app_data.py").read_text(encoding="utf-8")
    assert '<script defer src="prepladder_qbank_visual_metadata.js"></script>' in page
    assert "prepladder_qbank_records()" in build and "merged_record(slug, base)" in build
    assert "release_prepladder_qbank()" in build
    assert "prepladder_qbank_visual_metadata.js" in (ROOT / "tools/build_web_dist.py").read_text(encoding="utf-8")
    renderer = (ROOT / "app/src/main/assets/marrow_visual_renderer.js").read_text(encoding="utf-8")
    assert "HOLD_BYTES" in renderer and "^https:" in renderer, "renderer must take links and hold very large figures"
    groups = re.search(r"const NK_PROF_GROUP_BY_SUBJECT=(\{[^;]*\});", page).group(1)
    runtime = bank.runtime_visuals()
    ids, totals = set(), {"bank": 0, "supplement": 0, "figures": 0}
    for slug, cfg in bank.SUBJECTS.items():
        record = bank.stored_record(slug)
        if cfg.get("supplement"):
            base = bank.existing_bank(slug)
            merged = bank.merged_record(slug, base)
            assert len(merged["questions"]) == len(base["questions"]) + len(record["questions"]), slug
            assert [t["id"] for t in merged["topics"]] == [t["id"] for t in base["topics"]], slug
            for t in merged["topics"]:
                assert t["questionCount"] == sum(1 for q in merged["questions"] if q["chapterId"] == t["id"]), t["id"]
            topic_ids = {t["id"] for t in base["topics"]}
            totals["supplement"] += len(record["questions"])
        else:
            prof = PROF[cfg["subject"]]
            assert f"'{cfg['subject']}':'{prof}'" in groups or f"{cfg['subject']}:'{prof}'" in groups, \
                f"{cfg['subject']} is not filed under {prof}"
            sections = [t["section"] for t in record["topics"]]
            assert all(sections) and all(t["title"] for t in record["topics"]), f"{slug}: a topic lacks a name"
            runs = [s for i, s in enumerate(sections) if i == 0 or sections[i - 1] != s]
            assert len(runs) == len(set(runs)), f"{slug}: an index is split: {runs}"
            for t in record["topics"]:
                assert t["questionCount"] == sum(1 for q in record["questions"] if q["chapterId"] == t["id"]) > 0
            topic_ids = {t["id"] for t in record["topics"]}
            totals["bank"] += len(record["questions"])
        for q in record["questions"]:
            assert q["id"] not in ids, q["id"]
            ids.add(q["id"])
            check_question(q, slug, topic_ids)
        inventory = json.loads((bank.QBANK / slug / "visuals.json").read_text(encoding="utf-8"))["figures"]
        own = {q["id"] for q in record["questions"]}
        for f in inventory:
            assert f["questionId"] in own and f["url"].startswith("https://image.prepladder.com/"), f
            assert f["width"] > 0 and f["height"] > 0 and f["bytes"] > 0, f
            assert any(v["src"] == f["url"] for v in runtime[f["questionId"]]), f
        totals["figures"] += len(inventory)
    print(f"PREPLADDER_QBANK_BANK_TEST_OK subjects={len(bank.SUBJECTS)} bank={totals['bank']} "
          f"supplement={totals['supplement']} figures={totals['figures']}")


if __name__ == "__main__":
    main()
