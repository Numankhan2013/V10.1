#!/usr/bin/env python3
"""Build the PrepLadder Biochemistry bank (First Prof) from the 2025 edition.

The 2025 edition (biochemprep11.pdf, 821 questions in 39 lessons) replaces the
earlier PDF-page bank (app/src/main/assets/qbank_data.js, 719 questions in 28
chapters), whose attempts, reviews and saved tests point at its IDs ("1-1").
How questions carry over is shared with the other 2025 editions
(tools/prepladder_edition_bank.py).

  python3 tools/build_prepladder_biochemistry_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_biochemistry_bank.py           # rebuild the shards
  python3 tools/build_prepladder_biochemistry_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_biochemistry_bank.py release   # copy figures into the app

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

OLD_BANK = ROOT / "app/src/main/assets/qbank_data.js"
# 2025 keys checked against the question and the 2025 explanation itself. 11-33 asks
# for the least likely cause of virilisation in a girl; the explanation describes
# 17-hydroxylase deficiency (no androgens), but the key prints 21-hydroxylase.
KEY_FIXES = {"11-33": (1, "2025 key prints B (21-hydroxylase deficiency); its own explanation and the "
                          "earlier edition give A (17-hydroxylase deficiency causes no virilisation)")}


def load_old() -> list[dict]:
    text = OLD_BANK.read_text(encoding="utf-8")
    return json.loads(text[text.index("{"):text.rindex("}") + 1])["questions"]


BANK = EditionBank(
    load_old=load_old,
    old_pdf="Biochemistry_QBank_Source.pdf",
    footer=r"Prepladder X Qbank\s*•\s*Biochemistry\s*Page \d+ of \d+",
    key_fixes=KEY_FIXES,
    slug="biochemistry",
    subject="Biochemistry",
    source_pdfs="biochemprep11.pdf",
    expected={"questions": 867, "topics": 39},
    acronyms={"hmp": "HMP", "pdh": "PDH", "glut": "GLUT", "epp": "EPP", "dna": "DNA", "rna": "RNA", "pcr": "PCR",
              "crispr": "CRISPR"},
    # The owner's study index (PrepLadder app sections). Previous-year lessons sit with
    # the section whose topics they ask about: 27 (heme, iron, 2,3-BPG) joins Heme
    # Synthesis; 37 and 38 (free radicals, minerals) and the mixed sets 21, 35 and 39
    # close the Free Radicals, Trace Elements and Miscellaneous section.
    index=[
        ("Introduction", [1]),
        ("Carbohydrate Chemistry", [2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ("Lipid Chemistry", [11, 12, 13, 14, 15]),
        ("Amino Acid and Protein Chemistry", [16, 17, 18, 19, 20]),
        ("Heme Synthesis", [30, 31, 27]),
        ("Enzymes", [28, 29]),
        ("Free Radicals, Antioxidants, Trace Elements and Miscellaneous", [37, 38, 21, 35, 39]),
        ("Genetics", [22, 23, 24, 25, 26, 36]),
        ("Vitamins", [32, 33, 34]),
    ],
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
