#!/usr/bin/env python3
"""Keep the current Biochemistry rollout checks while using the expanded bank total."""
from pathlib import Path

CORE = Path(__file__).with_name("test_marrow_biochem_explanation_rollout_ui_core.py")
source = CORE.read_text(encoding="utf-8")
if "2115" not in source:
    raise SystemExit("Biochemistry rollout integration total anchor missing")
source = source.replace("2115", "2455")
exec(compile(source, str(CORE), "exec"), {"__name__": "__main__", "__file__": str(CORE), "__builtins__": __builtins__})
