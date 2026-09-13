#!/usr/bin/env python3
"""Run the existing debris detector/review-packet splitter on effective Marrow text."""
from __future__ import annotations

from pathlib import Path

import find_marrow_visible_debris as detector
import split_marrow_debris_review as splitter

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "marrow" / "content_audit_effective"


def main() -> None:
    detector.AUDIT = AUDIT
    detector.OUT = AUDIT / "debris_candidates.json"
    detector.SUMMARY = AUDIT / "debris_summary.json"
    detector.main()

    splitter.AUDIT = AUDIT
    splitter.OUT = AUDIT / "review_packets"
    splitter.main()
    print("EFFECTIVE_MARROW_VISIBLE_DEBRIS_AUDIT_OK")


if __name__ == "__main__":
    main()
