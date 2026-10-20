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
    # The owner's study index (2026-10-20). Mixed PYQ sets are placed by their content:
    # 64 (molluscum, connective tissue) with Skin; 66-67 (bone, soft-tissue tumors) with Bone;
    # 87 (inherited coagulopathy) with Platelets; 85 and 88-90 (lab methods, mixed) Miscellaneous.
    index=[
        ("Cell Injury", [1, 2, 3, 4, 5]),
        ("Inflammation", [6, 7, 8, 9]),
        ("Genetics", [10, 11, 12, 13]),
        ("Neoplasia", [14, 15, 16, 17, 18]),
        ("Immunity", [19, 20, 21, 22, 23, 24, 25]),
        ("CVS: Blood Vessels and Vasculitis", [26, 27, 28, 29, 30, 31]),
        ("Respiratory System", [32, 33, 34, 35, 36]),
        ("Salivary Gland", [37, 38]),
        ("Gastrointestinal Tract", [39, 40, 41, 42, 43]),
        ("Liver, Biliary System and Pancreas", [44, 45, 46, 47]),
        ("Renal System", [48, 49, 50, 51]),
        ("Genital System", [52, 53, 54, 55]),
        ("Endocrinology", [61, 62, 63]),
        ("Breast Pathology", [56, 57, 58]),
        ("Central Nervous System", [59, 60]),
        ("Skin and Musculoskeletal", [86, 64]),
        ("Hematology: Red Blood Cells", [68, 69, 70, 71, 72, 73]),
        ("Hematology: White Blood Cells", [74, 75, 76, 77, 78, 79, 80]),
        ("Hematology: Platelets and Bleeding Disorders", [81, 82, 87]),
        ("Blood Banking and Transfusion Medicine", [83, 84]),
        ("Bone Disorders", [65, 66, 67]),
        ("Miscellaneous", [85, 88, 89, 90]),
    ],
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
