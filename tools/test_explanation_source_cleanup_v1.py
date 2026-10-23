#!/usr/bin/env python3
"""Shipped Marrow explanations and stems carry no scanned-OCR debris.

data/marrow/explanation_source_cleanup_v1.json replaces the source-detail text of
explanations whose scan carried figure labels, page markers, OCR bullet glyphs
and broken words; data/marrow/content_hygiene_glyphs_v1.json fixes stems with a
lost glyph. This checks the cleanup still applies and that no shipped text has
those defects again.
"""
from __future__ import annotations

import re

from marrow_bank_data import (
    SOURCE_DEBRIS_MARKERS, app_marrow_records, apply_explanation_source_cleanup,
    canonical_source_questions, merged_explanations,
)

# Bullets the OCR read as other glyphs, a lost Δ, and the "@" shorthand for "in the".
OCR_BULLET = re.compile(r"^[+¢«*] ", re.M)
LOST_GLYPH = re.compile(r"■| @ ")


def main() -> None:
    merged = merged_explanations(canonical_source_questions())
    shipped = apply_explanation_source_cleanup(merged)
    texts = {qid: str(cfg.get("displayText", "")) for qid, cfg in shipped.items() if cfg.get("displayText")}
    for qid, text in texts.items():
        if any(marker in text for marker in SOURCE_DEBRIS_MARKERS) or "MARROW" in text:
            raise AssertionError(f"OCR debris in shipped explanation {qid}")
        if OCR_BULLET.search(text) or LOST_GLYPH.search(text):
            raise AssertionError(f"OCR bullet or lost glyph in shipped explanation {qid}")
        if shipped[qid] is not merged[qid] and any(str(p) not in text for p in shipped[qid].get("emphasis", [])):
            raise AssertionError(f"Emphasis anchor missing from cleaned explanation {qid}")

    records = app_marrow_records()
    questions = [q for record in records for q in record["questions"]]
    for q in questions:
        visible = " | ".join([str(q.get("question", ""))] + [str(o.get("text", "")) for o in q.get("options", [])])
        if LOST_GLYPH.search(visible) or "MARROW" in visible:
            raise AssertionError(f"Lost glyph in shipped stem or options {q['id']}")
        if q["id"] not in texts:
            source = str((q.get("structuredExplanation") or {}).get("text", ""))
            if OCR_BULLET.search(source) or LOST_GLYPH.search(source):
                raise AssertionError(f"OCR bullet or lost glyph in shipped source explanation {q['id']}")

    copd = next(q for q in questions if q["id"] == "marrow__PHYSIO_CH23_Q017")
    if "1. Functional residual capacity" not in copd["question"] or copd["correctAnswerText"] != "1 and 2":
        raise AssertionError("COPD stem must carry the numbered list its options refer to")
    print(f"EXPLANATION_SOURCE_CLEANUP_OK explanations={len(texts)} questions={len(questions)}")


if __name__ == "__main__":
    main()
