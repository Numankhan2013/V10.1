#!/usr/bin/env python3
"""Regenerate and verify the explanation inventory for the integrated source scope."""
import json

from inventory_marrow_explanations import DATA, build_inventory, inventory_manifest


def refresh_inventory() -> None:
    target = DATA / "explanation_inventory_v1.json"
    manifest = inventory_manifest(build_inventory())
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


refresh_inventory()
from test_marrow_explanation_inventory_expanded_core import main

if __name__ == "__main__":
    main()
