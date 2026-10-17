#!/usr/bin/env python3
"""Build the PrepLadder Pathology bank from its structured extraction.

The pipeline is shared with the other PrepLadder text banks
(tools/prepladder_text_bank.py); this file holds Pathology's identity.

  python3 tools/build_prepladder_pathology_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_pathology_bank.py           # rebuild the shards
  python3 tools/build_prepladder_pathology_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_pathology_bank.py release   # copy figures into the app

The app build loads the bank with `app_record()` and releases the figures with
`release()` (tools/build_app_data.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prepladder_text_bank import NO_EXPLANATION, TextBank, source_hash  # noqa: E402,F401

BANK = TextBank(
    slug="pathology",
    subject="Pathology",
    source_pdfs=", ".join(f"pathoprep11-{r}.pdf" for r in (
        "1-300", "301-600", "601-900", "901-1200", "1201-1500", "1501-1800", "1801-2100", "2101-2400", "2401-2889")),
    expected={"questions": 1459, "topics": 90},
    acronyms={"er": "ER", "rhd": "RHD", "git": "GIT", "ibd": "IBD", "cns": "CNS", "cml": "CML", "cll": "CLL",
              "wbc": "WBC", "all": "ALL", "aml": "AML", "i": "I", "ii": "II"},
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
