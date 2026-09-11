#!/usr/bin/env python3
"""Run the canonical complete-corpus Physiology explanation rollout checks."""
from pathlib import Path

CORE = Path(__file__).with_name("test_marrow_physio_explanation_rollout_ui_core.py")
source = CORE.read_text(encoding="utf-8")
exec(
    compile(source, str(CORE), "exec"),
    {"__name__": "__main__", "__file__": str(CORE), "__builtins__": __builtins__},
)
