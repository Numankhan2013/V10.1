#!/usr/bin/env python3
"""Keep the explanation triage inventory complete and reproducible."""
from __future__ import annotations

import json
from pathlib import Path

from inventory_marrow_explanations import DATA, build_inventory


def main() -> None:
    stored = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    generated = build_inventory()
    assert stored == generated
    assert stored["summary"]["questions"] == 2115
    assert stored["summary"]["subjects"] == {"Anatomy": 819, "Biochemistry": 543, "Physiology": 753}
    assert stored["summary"]["enhancementStatus"] == {"enhanced-reference": 142, "pending": 1973}
    assert len(stored["biochemistryGoldSample"]) == 20
    assert all(item["status"] == "pending-human-review" for item in stored["biochemistryGoldSample"])
    assert all("sourceText" not in item for item in stored["questions"])
    print("MARROW_EXPLANATION_INVENTORY_TEST_OK questions=2115 enhanced=142 pending=1973 sample=20 raw_text=excluded")


if __name__ == "__main__":
    main()
