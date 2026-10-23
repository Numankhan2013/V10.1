#!/usr/bin/env python3
"""Build the PrepLadder Anatomy bank (First Prof) from the 2025 edition.

The 2025 edition (anatprep11.pdf, 1,102 questions in 54 lessons) replaces the
earlier PDF-page bank (the Anatomy record in
app/src/main/assets/subjects_qbank_data.js, 1,068 questions in 50 chapters), whose
attempts, reviews and saved tests point at its IDs ("anatomy-1-1"). How
questions carry over is shared with the other 2025 editions
(tools/prepladder_edition_bank.py).

  python3 tools/build_prepladder_anatomy_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_anatomy_bank.py           # rebuild the shards
  python3 tools/build_prepladder_anatomy_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_anatomy_bank.py release   # copy figures into the app

`import` also rewrites the edition map. The app build loads the bank with
`app_record()` and releases the figures with `release()` (tools/build_app_data.py).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prepladder_edition_bank import EditionBank  # noqa: E402
from prepladder_text_bank import ROOT  # noqa: E402

OLD_BANK = ROOT / "app/src/main/assets/subjects_qbank_data.js"


def load_old() -> list[dict]:
    text = OLD_BANK.read_text(encoding="utf-8")
    subjects = json.loads(text[text.index("{"):text.rindex("}") + 1])["subjects"]
    return next(s for s in subjects if s["subject"] == "Anatomy")["questions"]


BANK = EditionBank(
    load_old=load_old,
    old_pdf="Anatomy_QBank_Source.pdf",
    footer=r"Prepladder X Qbank\s*•\s*Anatomy\s*Page \d+ of \d+",
    slug="anatomy",
    subject="Anatomy",
    source_pdfs="anatprep11.pdf",
    key_fixes={
        "anatomy-15-52": (2, "2025 PDF keys Arytenoid; its explanation names the thyroid cartilage as the unpaired "
                             "one, as the earlier edition keyed"),
        "anatomy-45-16": (2, "2025 PDF keys Falciform ligament; its explanation says the spleen develops from the "
                             "dorsal mesogastrium, as the earlier edition keyed"),
    },
    reviewed={
        "anatomy-q848227": "2025 PDF prints no key or choice text; the choices are the labelled heads a-d in the "
                           "question figure, and B (short head of biceps femoris) is the one its explanation names",
    },
    expected={"questions": 1135, "topics": 54},
    acronyms={"ivf": "IVF"},
    # The PDF's own regions, in its order; each previous-year lesson closes its region.
    index=[
        ("Neuroanatomy", [1, 2, 3, 4, 5, 6]),
        ("Head and Neck", [7, 8, 9, 10, 11, 12, 13, 14, 15]),
        ("Upper Limb", [16, 17, 18, 19, 20, 21]),
        ("Lower Limb", [22, 23, 24, 25]),
        ("Thorax", [26, 27, 28, 29]),
        ("Abdomen", [30, 31, 32, 33, 34, 35, 36]),
        ("Pelvis and Perineum", [37, 38, 39, 40, 41]),
        ("General Embryology", [42, 43, 44, 45, 46]),
        ("Histology", [47, 48, 49, 50, 51, 52]),
        ("Back Region", [53, 54]),
    ],
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
