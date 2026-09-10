#!/usr/bin/env python3
"""Keep the explanation triage inventory complete and reproducible."""
from __future__ import annotations

import json
from pathlib import Path

from inventory_marrow_explanations import DATA, build_inventory, enhanced_ids, inventory_manifest


def main() -> None:
    stored = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    generated = build_inventory()
    manifest = inventory_manifest(generated)
    assert stored == manifest
    assert stored["summary"]["questions"] == 2455
    assert stored["summary"]["subjects"] == {"Anatomy": 898, "Biochemistry": 543, "Physiology": 1014}
    enhanced = len(enhanced_ids())
    assert stored["summary"]["enhancementStatus"] == {"enhanced-reference": enhanced, "pending": 2455 - enhanced}
    assert len(stored["biochemistryGoldSample"]) == 20
    assert all(item["status"] == "approved-reference" for item in stored["biochemistryGoldSample"])
    assert stored["questionRecords"] == 2455
    assert len(stored["questionRecordsSha256"]) == 64
    assert all("sourceText" not in item for item in generated["questions"])
    print(f"MARROW_EXPLANATION_INVENTORY_TEST_OK questions=2455 enhanced={enhanced} pending={2455-enhanced} sample=20 raw_text=excluded")


if __name__ == "__main__":
    main()
