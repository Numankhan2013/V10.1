#!/usr/bin/env python3
"""Find likely learner-visible OCR/code debris in the full Marrow audit projection.

This is deliberately an over-inclusive REVIEW QUEUE, not an automatic rewriter.
It never mutates source or learner data. Stable-ID reviewed overrides remain the
only accepted path for OCR/source-transcription cleanup.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "marrow" / "content_audit_full"
OUT = AUDIT / "debris_candidates.json"
SUMMARY = AUDIT / "debris_summary.json"

BRAND_RE = re.compile(r"(?i)\b(?:prepladder|marrow\s*qbank|qbank\s*page|©\s*marrow)\b")
SERIALIZED_RE = re.compile(r"(?:\[object Object\]|\{\s*[\"'](?:text|type|content|value)[\"']\s*:|\"(?:text|type|content)\"\s*:)")
PUNCT_RUN_RE = re.compile(r"[^\w\s]{4,}", re.UNICODE)
ISOLATED_LETTER_RE = re.compile(r"(?<!\w)[A-Za-z](?!\w)")
WEIRD_EDGE_RE = re.compile(r"^(?:[\s~|\\<>{}\[\]`^_*=.,;:'\"“”‘’!?/+-]*[A-Za-z0-9]{0,2}[\s~|\\<>{}\[\]`^_*=.,;:'\"“”‘’!?/+-]{2,})|(?:[~|\\<>{}`^_*=]{2,}\s*)$", re.UNICODE)

# Characters that are highly unusual as standalone learner prose but can occur
# in diagrams/code leakage. We do not flag ordinary medical operators (+ - = < > / %).
HARD_NOISE = set("~|\\{} `^")


def line_reasons(line: str) -> list[str]:
    reasons: list[str] = []
    stripped = line.strip()
    if not stripped:
        return reasons
    if BRAND_RE.search(stripped):
        reasons.append("brand_or_footer")
    if SERIALIZED_RE.search(stripped):
        reasons.append("serialized_value")
    if any(ch in stripped for ch in HARD_NOISE):
        reasons.append("hard_noise_char")
    if PUNCT_RUN_RE.search(stripped):
        reasons.append("punctuation_run")
    if WEIRD_EDGE_RE.search(stripped):
        reasons.append("edge_noise")

    nonspace = [c for c in stripped if not c.isspace()]
    alnum = sum(c.isalnum() for c in nonspace)
    alpha = sum(c.isalpha() for c in nonspace)
    punct = len(nonspace) - alnum
    if len(nonspace) >= 4 and punct >= 3 and (punct / len(nonspace)) >= 0.45:
        reasons.append("symbol_dense_line")
    isolated = len(ISOLATED_LETTER_RE.findall(stripped))
    if isolated >= 4 and isolated >= max(4, alpha // 3):
        reasons.append("many_isolated_letters")
    return sorted(set(reasons))


def field_reasons(value: object, field: str) -> tuple[list[str], list[dict]]:
    if not isinstance(value, str):
        return (["non_string"] if value is not None else []), []
    reasons: list[str] = []
    suspect_lines: list[dict] = []
    if SERIALIZED_RE.search(value):
        reasons.append("serialized_value")
    if BRAND_RE.search(value):
        reasons.append("brand_or_footer")
    if "[object Object]" in value:
        reasons.append("object_string")
    if "```" in value:
        reasons.append("code_fence")
    if "\\" in value:
        reasons.append("literal_backslash")
    if field in {"question", "option"} and value.count("\n") >= 4:
        reasons.append("many_linebreaks")
    for idx, line in enumerate(value.splitlines(), start=1):
        lr = line_reasons(line)
        if lr:
            suspect_lines.append({"line": idx, "text": line, "reasons": lr})
            reasons.extend(lr)
    return sorted(set(reasons)), suspect_lines


def severity(reasons: list[str], field: str) -> int:
    weights = {
        "serialized_value": 8,
        "object_string": 8,
        "code_fence": 6,
        "brand_or_footer": 5,
        "hard_noise_char": 4,
        "literal_backslash": 3,
        "punctuation_run": 3,
        "symbol_dense_line": 3,
        "edge_noise": 3,
        "many_isolated_letters": 2,
        "many_linebreaks": 1,
        "non_string": 5,
    }
    score = sum(weights.get(r, 1) for r in set(reasons))
    if field in {"question", "option"}:
        score += 2
    return score


def main() -> None:
    if not (AUDIT / "manifest.json").exists():
        raise SystemExit("Run export_full_marrow_content_audit.py first")
    candidates: list[dict] = []
    counts = Counter()
    by_subject = Counter()
    by_chapter: dict[str, Counter] = defaultdict(Counter)

    for subject_dir in (AUDIT / "anatomy", AUDIT / "biochemistry", AUDIT / "physiology"):
        for path in sorted(subject_dir.glob("chapter_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for q in payload["questions"]:
                qid = str(q["id"])
                fields: list[tuple[str, str, object]] = [("question", "question", q.get("question"))]
                for opt in q.get("options") or []:
                    fields.append(("option", f"option_{opt.get('letter')}", opt.get("text")))
                fields.append(("explanation", "explanation", q.get("explanation")))
                structured = q.get("structuredExplanationText")
                if structured and structured != q.get("explanation"):
                    fields.append(("structuredExplanation", "structuredExplanationText", structured))

                for kind, label, value in fields:
                    reasons, suspect_lines = field_reasons(value, kind)
                    if not reasons:
                        continue
                    row = {
                        "id": qid,
                        "subject": q.get("subject"),
                        "chapterId": str(q.get("chapterId")),
                        "chapter": q.get("chapter"),
                        "questionNumber": q.get("questionNumber"),
                        "fieldKind": kind,
                        "field": label,
                        "severity": severity(reasons, kind),
                        "reasons": reasons,
                        "value": value,
                        "suspectLines": suspect_lines,
                        "sourcePage": q.get("sourcePage"),
                        "reviewStatus": q.get("reviewStatus"),
                    }
                    candidates.append(row)
                    counts[kind] += 1
                    by_subject[str(q.get("subject"))] += 1
                    by_chapter[str(q.get("subject"))][str(q.get("chapterId"))] += 1

    candidates.sort(key=lambda r: (-r["severity"], r["subject"], int(r["chapterId"]), int(r.get("questionNumber") or 0), r["field"]))
    OUT.write_text(json.dumps({
        "schemaVersion": 1,
        "purpose": "Over-inclusive review queue for visible OCR/code debris; not an auto-rewrite list.",
        "candidateFieldCount": len(candidates),
        "candidateQuestionCount": len({r['id'] for r in candidates}),
        "candidates": candidates,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "candidateFieldCount": len(candidates),
        "candidateQuestionCount": len({r['id'] for r in candidates}),
        "byFieldKind": dict(sorted(counts.items())),
        "bySubject": dict(sorted(by_subject.items())),
        "bySubjectChapter": {subject: dict(sorted(ch.items(), key=lambda x: int(x[0]))) for subject, ch in sorted(by_chapter.items())},
        "severityBuckets": {
            "10_plus": sum(r["severity"] >= 10 for r in candidates),
            "6_to_9": sum(6 <= r["severity"] <= 9 for r in candidates),
            "1_to_5": sum(r["severity"] <= 5 for r in candidates),
        },
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MARROW_VISIBLE_DEBRIS_REVIEW_QUEUE_OK", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
