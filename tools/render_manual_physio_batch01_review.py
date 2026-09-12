#!/usr/bin/env python3
"""Render the bounded manual Physiology batch for source review in Linux CI."""
from __future__ import annotations

import hashlib
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/marrow/source_pdfs/physiologyed8.pdf"
OUTPUT = ROOT / "build/manual-physiology-batch01-source-review"
EXPECTED_SHA256 = "03834d3e9ec9723484387cd828a6f68cd999ec5187d167213f0bab9b967e0cfe"


def render(page, rect, dpi, target):
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(dpi / 72, dpi / 72), clip=rect, alpha=False
    )
    target.write_bytes(pixmap.tobytes("png"))


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED_SHA256
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with fitz.open(SOURCE) as document:
        for page_number in (14, 18, 19, 25, 44):
            page = document[page_number - 1]
            assert page.rotation == 0
            render(page, page.rect, 180, OUTPUT / f"physiology-page-{page_number:03d}.png")

        clinical_page = document[24]
        clinical_region = fitz.Rect(161.52, 55.775, 450.48, 272.225)
        assert clinical_page.rect.contains(clinical_region)
        render(
            clinical_page,
            clinical_region,
            300,
            OUTPUT / "phys-ch02-q020-question-clinical-region-300dpi.png",
        )


if __name__ == "__main__":
    main()
