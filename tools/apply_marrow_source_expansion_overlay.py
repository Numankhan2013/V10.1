#!/usr/bin/env python3
"""Overlay the newest verified Marrow source bundles onto the generated app.

This intentionally runs after the approved UI/explanation transformer so the UI
branch keeps its current explanation augmentations while learner navigation uses
the corrected topic-index v2 source scope and newly ingested chapters.
"""
from __future__ import annotations

import json
from pathlib import Path

from inventory_marrow_explanations import load_sharded

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
HTML = ROOT / "app" / "src" / "main" / "assets" / "index.html"

EXPECTED = (
    ("Anatomy", "anatomy_ch001_048_plus_060_063", 898, 52),
    ("Biochemistry", "biochemistry_phase_a", 543, 26),
    ("Physiology", "physiology_ch001_043", 1014, 43),
)


def main() -> None:
    records = []
    ids = []
    for subject, prefix, question_count, topic_count in EXPECTED:
        record, raw_sha = load_sharded(prefix)
        manifest = json.loads((DATA / f"{prefix}_manifest.json").read_text(encoding="utf-8"))
        if record.get("subject") != subject or record.get("bank") != "Marrow":
            raise SystemExit(f"{subject} expanded identity mismatch")
        if len(record.get("questions", [])) != question_count or len(record.get("topics", [])) != topic_count:
            raise SystemExit(f"{subject} expanded count mismatch")
        if raw_sha != manifest.get("raw_sha256"):
            raise SystemExit(f"{subject} expanded raw SHA mismatch")
        question_ids = [str(q.get("id", "")) for q in record.get("questions", [])]
        if len(question_ids) != len(set(question_ids)) or any(not qid.startswith("marrow__") for qid in question_ids):
            raise SystemExit(f"{subject} expanded IDs invalid")
        ids.extend(question_ids)
        records.append(record)

    if len(ids) != 2455 or len(ids) != len(set(ids)):
        raise SystemExit(f"Expanded Marrow global ID mismatch: {len(ids)}")

    source = HTML.read_text(encoding="utf-8")
    marker = "  const MARROW_DATA = "
    if source.count(marker) != 1:
        raise SystemExit(f"Marrow data declaration count: {source.count(marker)}")
    start = source.index(marker) + len(marker)
    end = source.index(";\n", start)
    payload = json.dumps({"records": records}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    source = source[:start] + payload + source[end:]
    HTML.write_text(source, encoding="utf-8")
    print("MARROW_SOURCE_INTEGRATION_OK anatomy=898/52 biochemistry=543/26 physiology=1014/43 total=2455")


if __name__ == "__main__":
    main()
