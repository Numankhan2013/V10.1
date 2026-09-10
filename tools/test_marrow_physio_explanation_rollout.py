#!/usr/bin/env python3
"""Keep the current Physiology rollout checks while using the expanded source bank."""
from pathlib import Path

CORE = Path(__file__).with_name("test_marrow_physio_explanation_rollout_ui_core.py")
source = CORE.read_text(encoding="utf-8")
replacements = {
    '"physiology_ch001_033"': '"physiology_ch001_043"',
    "2115": "2455",
}
for old, new in replacements.items():
    if old not in source:
        raise SystemExit(f"Physiology rollout integration anchor missing: {old}")
    source = source.replace(old, new)
exec(compile(source, str(CORE), "exec"), {"__name__": "__main__", "__file__": str(CORE), "__builtins__": __builtins__})
