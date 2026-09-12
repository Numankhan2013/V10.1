#!/usr/bin/env python3
"""Stable entrypoint for canonical Marrow browser regressions."""
from pathlib import Path

for name in (
    "verify_marrow_bank_browser_v2.py",
    "verify_marrow_anatomy_ch06_q002_browser.py",
    "verify_marrow_anatomy_ch06_q018_browser.py",
):
    target = Path(__file__).with_name(name)
    source = target.read_text(encoding="utf-8")
    exec(
        compile(source, str(target), "exec"),
        {"__name__":"__main__", "__file__":str(target), "__builtins__":__builtins__},
    )
