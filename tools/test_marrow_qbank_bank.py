#!/usr/bin/env python3
"""Marrow QBank subjects (web export): shards current, content clean, figures intact, app wired."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import marrow_qbank_bank as bank  # noqa: E402

ZERO_WIDTH = re.compile("[​‌‍⁠﻿­]")
TAG = re.compile(r"</?(?:p|div|span|strong|em|li|ul|ol|table|tr|td|th|br|sub|sup|b|i)\b[^>]*>", re.I)


def texts(q: dict):
    yield q["question"]
    for o in q["options"]:
        yield o["text"]
    data = q["structuredExplanation"]
    for b in data["blocks"]:
        if b["type"] in ("paragraph", "heading"):
            yield b["text"]
        elif b["type"] == "bullets":
            for item in b["items"]:
                yield item["text"]
                for child in item.get("items", []):
                    yield child["text"]
    for t in data["tables"]:
        yield t["title"]
        yield from t["columns"]
        for row in t["rows"]:
            yield from row


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/marrow_qbank_bank.py"), "--check"], check=True)
    page = (ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8")
    assert '<script defer src="marrow_qbank_visual_metadata.js"></script>' in page
    assert "marrow_qbank_records()" in (ROOT / "tools/build_app_data.py").read_text(encoding="utf-8")
    assert "release_marrow_qbank()" in (ROOT / "tools/build_app_data.py").read_text(encoding="utf-8")
    assert "marrow_qbank_visual_metadata.js" in (ROOT / "tools/build_web_dist.py").read_text(encoding="utf-8")
    groups = re.search(r"const NK_PROF_GROUP_BY_SUBJECT=(\{[^;]*\});", page).group(1)
    ids, totals, figures = set(), {"questions": 0, "topics": 0}, 0
    for slug, cfg in bank.SUBJECTS.items():
        record = bank.app_record(slug)
        # Final Prof Part 2 shows its minor subjects as a group of their own ('final-minor').
        filed = re.search(rf"(?:'{re.escape(cfg['subject'])}'|\b{re.escape(cfg['subject'])}):'([a-z-]+)'", groups)
        assert filed and filed.group(1) in (cfg["prof"], f"{cfg['prof']}-minor"), \
            f"{cfg['subject']} is not filed under {cfg['prof']} prof"
        sections = [t["section"] for t in record["topics"]]
        assert all(sections), f"{slug}: a topic has no section"
        # Sections are contiguous in topic order, so each shows as one group.
        runs = [s for i, s in enumerate(sections) if i == 0 or sections[i - 1] != s]
        assert len(runs) == len(set(runs)), f"{slug}: a section is split: {runs}"
        topic_ids = {t["id"] for t in record["topics"]}
        for q in record["questions"]:
            assert q["id"] not in ids, q["id"]
            ids.add(q["id"])
            assert q["chapterId"] in topic_ids and q["bank"] == "Marrow" and q["subject"] == cfg["subject"]
            assert len(q["options"]) == 4 and q["correctOption"] in (1, 2, 3, 4)
            assert q["correctAnswerText"] == q["options"][q["correctOption"] - 1]["text"]
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
        inventory = json.loads((bank.QBANK / slug / "visuals.json").read_text(encoding="utf-8"))["figures"]
        by_question = {}
        for f in inventory:
            by_question.setdefault(f["questionId"], []).append(f)
            path = ROOT / f["file"]
            assert path.exists() and path.stat().st_size == f["bytes"], f["file"]
        for q in record["questions"]:
            assert len(by_question.get(q["id"], [])) == len(q["structuredExplanation"]["figures"]), q["id"]
            if q["imageDependent"]:
                assert any(f["role"] == "question" for f in by_question[q["id"]]), q["id"]
        figures += len(inventory)
        totals["questions"] += len(record["questions"])
        totals["topics"] += len(record["topics"])
    print(f"MARROW_QBANK_TEST_OK subjects={len(bank.SUBJECTS)} questions={totals['questions']} "
          f"topics={totals['topics']} figures={figures}")


if __name__ == "__main__":
    main()
