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
    # The owner's study index (2026-10-20). Lesson 57 (antidotes) stays with Anaesthesia, as in
    # the source; the index's "Recent updates" has no lessons in this edition.
    index=[
        ("General Pharmacology", [1, 2, 3, 4, 5]),
        ("ANS Pharmacology", [6, 7, 8, 9, 10]),
        ("CVS Pharmacology", [17, 18, 19, 20, 21]),
        ("Renal Pharmacology", [15, 16]),
        ("CNS Pharmacology", [22, 23, 24, 25, 26, 27]),
        ("Antimicrobials", [34, 35, 36, 37, 38, 39, 40, 41, 42]),
        ("Endocrine Pharmacology", [28, 29, 30, 31, 32, 33]),
        ("Autacoids", [11, 12, 13, 14]),
        ("Drugs Affecting Blood and Blood Formation", [49, 50, 51, 52]),
        ("Respiratory Pharmacology", [43, 44]),
        ("GIT Pharmacology", [45, 46, 47, 48]),
        ("Anticancer Drugs", [53, 54, 55, 56]),
        ("Anaesthesia", [57, 58, 59]),
    ],
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
