#!/usr/bin/env python3
"""Build the PrepLadder Physiology bank (First Prof) from the 2025 edition.

The 2025 edition (prep11physio.pdf, 958 questions in 49 lessons) replaces the
earlier PDF-page bank (the Physiology record in
app/src/main/assets/subjects_qbank_data.js, 899 questions in 38 chapters), whose
attempts, reviews and saved tests point at its IDs ("physiology-1-1"). How
questions carry over is shared with the other 2025 editions
(tools/prepladder_edition_bank.py).

  python3 tools/build_prepladder_physiology_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_physiology_bank.py           # rebuild the shards
  python3 tools/build_prepladder_physiology_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_physiology_bank.py release   # copy figures into the app

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
    return next(s for s in subjects if s["subject"] == "Physiology")["questions"]


BANK = EditionBank(
    load_old=load_old,
    old_pdf="Physiology_QBank_Source.pdf",
    footer=r"Prepladder X Qbank\s*•\s*Physiology\s*Page \d+ of \d+",
    slug="physiology",
    subject="Physiology",
    source_pdfs="prep11physio.pdf",
    reviewed={
        "physiology-q866658": "2025 PDF prints no key; A (conduction velocity increases) checked against the "
                              "question and its explanation",
        "physiology-q866344": "2025 PDF prints no key or choice text; the choices are the sarcomere diagrams a-d "
                              "in the question figure, and D (diagram 4, full overlap without double overlap) is "
                              "the optimal overlap the explanation names",
    },
    links={"Q843131": "physiology-24-6"},
    withdrawn={"physiology-24-6": "the compliance-curve choices are graphs neither edition's PDF prints; "
                                  "answering is disabled"},
    expected={"questions": 988, "topics": 49},
    acronyms={"eeg": "EEG", "rmp": "RMP", "ecg": "ECG", "bp": "BP", "git": "GIT", "rs": "RS", "co": "CO"},
    # Sections in the PDF's order; each previous-year lesson sits with the section
    # its questions ask about.
    index=[
        ("Central Nervous System", [1, 2, 3, 4, 5, 6, 7, 40, 41, 46]),
        ("General Physiology", [13, 14]),
        ("Nerve and Muscle Physiology", [15, 16, 17, 18]),
        ("Cardiovascular System", [19, 20, 21, 22, 23, 12]),
        ("Blood Physiology", [24, 25, 26]),
        ("Renal Physiology", [27, 28, 29, 30, 8]),
        ("Respiratory System", [31, 32, 33, 34, 35, 36, 9]),
        ("Gastrointestinal System", [37, 38, 39, 11]),
        ("Endocrine System", [42, 43, 44, 45, 10, 47]),
        ("Reproductive Physiology", [48, 49]),
    ],
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
