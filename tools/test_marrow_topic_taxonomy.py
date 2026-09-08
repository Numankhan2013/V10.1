#!/usr/bin/env python3
"""Validate the explicit Marrow topic-to-major-index taxonomy."""
from __future__ import annotations

import base64
import json
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
BANKS = {
    "Anatomy": "anatomy_phase_a",
    "Biochemistry": "biochemistry_phase_a",
    "Physiology": "physiology_ch001_033",
}


def load_bank(prefix: str) -> dict:
    encoded = "".join(
        part.read_text(encoding="utf-8").strip()
        for part in sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    )
    return json.loads(zlib.decompress(base64.b64decode(encoded)))


def main() -> None:
    taxonomy = json.loads((DATA / "topic_index_taxonomy.json").read_text(encoding="utf-8"))
    assert taxonomy["schemaVersion"] == 1
    subjects = taxonomy["subjects"]
    assert set(subjects) == set(BANKS)

    total = 0
    for subject, prefix in BANKS.items():
        bank = load_bank(prefix)
        source_topics = bank["topics"]
        config = subjects[subject]
        configured = config["topics"]
        assert len(configured) == len(source_topics), subject
        assert len({str(item["id"]) for item in configured}) == len(configured), subject
        assert [str(item["id"]) for item in configured] == [str(item["id"]) for item in source_topics], subject
        by_id = {str(item["id"]): item for item in configured}
        for source in source_topics:
            item = by_id[str(source["id"])]
            assert item["title"] == source["title"], (subject, source["id"])
            assert item["section"] in config["sectionOrder"], (subject, source["id"])

        for section in config["sectionOrder"]:
            ids = [int(item["id"]) for item in configured if item["section"] == section]
            assert ids == sorted(ids), (subject, section)
            titles = [item["title"].lower() for item in configured if item["section"] == section]
            pyq_positions = [index for index, title in enumerate(titles) if "pyq" in title or "previous year" in title]
            if pyq_positions:
                assert pyq_positions == list(range(pyq_positions[0], len(titles))), (subject, section)
        total += len(configured)

    anatomy_review = {
        item["id"] for item in subjects["Anatomy"]["topics"]
        if item.get("reviewStatus") == "needs-review"
    }
    assert anatomy_review == {"6", "7", "9", "10"}
    assert subjects["Biochemistry"]["topics"][0]["section"] == "Carbohydrate Chemistry"
    assert total == 107
    print("MARROW_TOPIC_TAXONOMY_OK subjects=3 topics=107 review_needed=4 source_order=preserved")


if __name__ == "__main__":
    main()
