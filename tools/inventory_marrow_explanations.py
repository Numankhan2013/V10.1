#!/usr/bin/env python3
"""Compatibility loader: current explanation inventory logic + expanded source scope."""
from pathlib import Path

CORE = Path(__file__).with_name("inventory_marrow_explanations_ui_core.py")
source = CORE.read_text(encoding="utf-8")
replacements = {
    '"Anatomy": "anatomy_phase_a"': '"Anatomy": "anatomy_ch001_048_plus_060_063"',
    '"Physiology": "physiology_ch001_033"': '"Physiology": "physiology_ch001_043"',
    "2115": "2455",
}
for old, new in replacements.items():
    if old not in source:
        raise SystemExit(f"Inventory integration anchor missing: {old}")
    source = source.replace(old, new)
exec(compile(source, str(CORE), "exec"), globals(), globals())
