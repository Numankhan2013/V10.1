#!/usr/bin/env python3
"""Keep the explanation triage inventory complete and reproducible."""
from __future__ import annotations

import json

from inventory_marrow_explanations import DATA, build_inventory, enhanced_ids, inventory_manifest


def main() -> None:
    target = DATA / "explanation_inventory_v1.json"
    stored = json.loads(target.read_text(encoding="utf-8"))
    generated = build_inventory()
    manifest = inventory_manifest(generated)
    if stored != manifest:
        # Diagnostic handoff only: materialize the deterministic expected manifest
        # in the CI workspace so the workflow can upload it as an artifact. The
        # assertion remains fail-closed until the generated manifest is committed.
        target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("MARROW_EXPLANATION_INVENTORY_DRIFT artifact=explanation_inventory_v1.json")
    assert stored == manifest
    assert stored["summary"]["questions"] == 2711
    assert stored["summary"]["subjects"] == {"Anatomy": 1115, "Biochemistry": 582, "Physiology": 1014}
    enhanced = len(enhanced_ids())
    assert stored["summary"]["enhancementStatus"] == {"enhanced-reference": enhanced, "pending": 2711 - enhanced}
    assert len(stored["biochemistryGoldSample"]) == 20
    assert all(item["status"] == "approved-reference" for item in stored["biochemistryGoldSample"])
    assert stored["questionRecords"] == 2711
    assert len(stored["questionRecordsSha256"]) == 64
    assert all("sourceText" not in item for item in generated["questions"])
    print(f"MARROW_EXPLANATION_INVENTORY_TEST_OK questions=2711 enhanced={enhanced} pending={2711-enhanced} sample=20 raw_text=excluded")


if __name__ == "__main__":
    main()
