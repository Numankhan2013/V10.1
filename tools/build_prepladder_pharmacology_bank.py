#!/usr/bin/env python3
"""Build the PrepLadder Pharmacology bank from its structured extraction.

The pipeline is shared with the other PrepLadder text banks
(tools/prepladder_text_bank.py); this file holds Pharmacology's identity.

  python3 tools/build_prepladder_pharmacology_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_pharmacology_bank.py           # rebuild the shards
  python3 tools/build_prepladder_pharmacology_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_pharmacology_bank.py release   # copy figures into the app

The app build loads the bank with `app_record()` and releases the figures with
`release()` (tools/build_app_data.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prepladder_text_bank import NO_EXPLANATION, TextBank, source_hash  # noqa: E402,F401

BANK = TextBank(
    slug="pharmacology",
    subject="Pharmacology",
    source_pdfs="pharmaprep11.pdf",
    expected={"questions": 1321, "topics": 59},
    acronyms={"ans": "ANS", "hpa": "HPA", "git": "GIT"},
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
