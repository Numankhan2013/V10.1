#!/usr/bin/env python3
"""Run the full Marrow browser regression core with current taxonomy assertions."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools" / "verify_marrow_bank_browser_core.py"

source = CORE.read_text(encoding="utf-8")
old = "            assert_sections(['CNS Physiology','General Physiology','Cellular Physiology','Neuromuscular Physiology','Cardiovascular System','Respiratory System','Gastrointestinal System'])"
new = """            assert_sections(['General physiology','Nerve and muscle physiology','Gastrointestinal system','Cardiovascular system','Respiratory system','Renal physiology','Endocrine physiology','Reproductive physiology','Central nervous system','Integrated physiology'])
            pnums=[int(x) for x in page.locator('.nk-topic-index').all_inner_texts()]
            if pnums!=list(range(1,44)): raise SystemExit(f'Marrow Physiology learner numbering is not contiguous 1-43: {pnums!r}')"""
if source.count(old) != 1:
    raise SystemExit(f"Physiology browser taxonomy assertion anchor count: {source.count(old)}")
source = source.replace(old, new, 1)
old_summary = "biochemistry=543/26 physiology=753/33 total=2115"
new_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous total=2376"
if source.count(old_summary) != 1:
    raise SystemExit(f"Marrow browser summary anchor count: {source.count(old_summary)}")
source = source.replace(old_summary, new_summary, 1)

exec(
    compile(source, str(CORE), "exec"),
    {"__name__": "__main__", "__file__": str(CORE), "__builtins__": __builtins__},
)
