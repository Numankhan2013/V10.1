#!/usr/bin/env python3
"""Audit visible Marrow question/option text for likely OCR/code debris.

The detector is deliberately report-only. It never mutates source or learner data.
"""
from __future__ import annotations

import base64
import json
import re
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
OUT = DATA / "content_hygiene_debris_audit_v1.json"
BANKS = (
    ("Anatomy", "anatomy_ch001_063"),
    ("Biochemistry", "biochemistry_ch001_028"),
    ("Physiology", "physiology_ch001_043"),
)

HARD_MARKERS = (
    "[object Object]", '{"text"', '{"type"', '"content":', '"attrs":', '"marks":', "```",
)
WEIRD_CHARS = set("{}\\|~^<>€")
QUESTION_STARTERS = re.compile(
    r"\b(?:Which|What|Who|Where|When|Why|How|All\b|Choose\b|Identify\b|Select\b|The\b|A\b|An\b|Following\b|Regarding\b|In\b|During\b|After\b|Before\b|Most\b|Least\b|One\b|Among\b)",
    re.I,
)


def load(prefix: str) -> dict:
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    raw = zlib.decompress(base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in parts)))
    return json.loads(raw)


def field_reasons(value: object, kind: str) -> list[str]:
    text = "" if value is None else str(value)
    stripped = text.strip()
    reasons: list[str] = []
    if not stripped:
        return ["empty"]
    if any(marker in stripped for marker in HARD_MARKERS):
        reasons.append("serialized_marker")
    if "\\" in stripped:
        reasons.append("backslash")
    weird = sum(ch in WEIRD_CHARS for ch in stripped)
    if weird >= 1:
        reasons.append("weird_symbol")
    if re.search(r"(?:^|\s)[~<>|^]+(?:\s|$)", stripped):
        reasons.append("isolated_symbol_token")
    if re.search(r"[^\w\s.,;:!?()/%+−–—'’\-×=₂₃₄₅₆₇₈₉°μ²³αβγδΔ]+", stripped, re.UNICODE):
        reasons.append("unusual_character_run")
    if re.search(r"(?:[A-Za-z]{1,3}\s+){1,2}\d+[\"'“”‘’.,;:!?<>~^|\\]*$", stripped):
        reasons.append("short_alpha_numeric_tail")
    if re.search(r"\b[A-Za-z]{1,2}\s*[<>~^|\\]\s*[A-Za-z0-9]*", stripped):
        reasons.append("mixed_noise_token")
    if re.search(r"[“”‘’]\s*[xX]\s*$", stripped):
        reasons.append("quote_x_tail")
    # Questions with obvious garbage before a normal interrogative/statement starter.
    if kind == "question":
        match = QUESTION_STARTERS.search(stripped)
        if match and match.start() >= 3:
            prefix = stripped[:match.start()].strip()
            alpha = sum(c.isalpha() for c in prefix)
            punct = sum(not c.isalnum() and not c.isspace() for c in prefix)
            if punct >= alpha or re.search(r"[~<>|\\{}^]", prefix):
                reasons.append("noisy_question_prefix")
        if "?" in stripped and stripped.rfind("?") < len(stripped) - 4:
            tail = stripped[stripped.rfind("?") + 1:].strip()
            if tail and (sum(not c.isalnum() and not c.isspace() for c in tail) >= 1 or len(tail.split()) <= 3):
                reasons.append("post_question_tail")
    # OCR debris frequently produces punctuation-dense short lines.
    for line in stripped.splitlines():
        line = line.strip()
        if not line:
            continue
        alpha = sum(c.isalpha() for c in line)
        punct = sum(not c.isalnum() and not c.isspace() for c in line)
        if len(line) <= 24 and punct >= 2 and punct >= alpha:
            reasons.append("punctuation_dense_line")
            break
    return sorted(set(reasons))


def main() -> None:
    rows = []
    counts = Counter()
    total = 0
    for subject, prefix in BANKS:
        bank = load(prefix)
        for question in bank.get("questions", []):
            total += 1
            fields = []
            q_reasons = field_reasons(question.get("question"), "question")
            if q_reasons:
                fields.append({"field": "question", "text": question.get("question"), "reasons": q_reasons})
            for idx, option in enumerate(question.get("options", []), 1):
                reasons = field_reasons(option.get("text"), "option")
                if reasons:
                    fields.append({"field": f"option{idx}", "text": option.get("text"), "reasons": reasons})
            if fields:
                for field in fields:
                    counts.update(field["reasons"])
                rows.append({
                    "id": question.get("id"),
                    "subject": subject,
                    "chapterId": str(question.get("chapterId")),
                    "questionNumber": question.get("questionNumber"),
                    "question": question.get("question"),
                    "options": [o.get("text") for o in question.get("options", [])],
                    "flaggedFields": fields,
                })
    if total != 2711:
        raise SystemExit(f"canonical corpus count mismatch: {total}")
    payload = {
        "schemaVersion": 1,
        "purpose": "Report-only candidate list for stable-ID reviewed learner-display cleanup; no source mutation.",
        "totalQuestions": total,
        "candidateQuestions": len(rows),
        "reasonCounts": dict(sorted(counts.items())),
        "questions": rows,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MARROW_VISIBLE_DEBRIS_AUDIT_OK total={total} candidates={len(rows)} reasons={dict(counts)}")


if __name__ == "__main__":
    main()
