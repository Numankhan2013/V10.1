#!/usr/bin/env python3
"""Stable entrypoint for canonical Marrow browser regression."""
from pathlib import Path

TARGET = Path(__file__).with_name("verify_marrow_bank_browser_v2.py")
source = TARGET.read_text(encoding="utf-8")
exec(compile(source, str(TARGET), "exec"), {"__name__":"__main__", "__file__":str(TARGET), "__builtins__":__builtins__})
