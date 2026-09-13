#!/usr/bin/env python3
"""Generate a conservative review artifact for Marrow explanation cleanup.

This tool is intentionally deletion-only and does NOT activate overrides. It may:
- remove explicit PDF page separators / source-brand-only lines,
- remove very short symbol/OCR-only lines,
- trim very short OCR prefixes/suffixes around otherwise intact prose,
- replace literal backslashes with spaces.

It refuses any edit that would delete a substantive alphabetic word (>3 letters),
except explicit page-marker/brand metadata. Ambiguous medical prose is deferred.
"""
from __future__ import annotations

import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
AUDIT = DATA / "content_audit_effective"
OUT = DATA / "explanation_cleanup_auto_review"
SLUGS = {"Anatomy": "anatomy", "Biochemistry": "biochemistry", "Physiology": "physiology"}

PAGE_RE = re.compile(r"^\s*=+\s*PDF\s+PAGE\s+\d+\s*=+\s*$", re.I)
BRAND_ONLY_RE = re.compile(r"^\s*(?:©\s*)?(?:MARROW|PREPLADDER|QBANK)(?:\s+ED\s*\d+)?\s*$", re.I)
WORD_RE = re.compile(r"[A-Za-z]+")
HARD = set("~|\\{}`€™")


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def substantive_words(text: str) -> list[str]:
    return [w for w in words(text) if len(w) > 3]


def symbol_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    symbols = sum(not c.isalnum() for c in chars)
    return symbols / len(chars)


def pure_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    ws = words(s)
    max_word = max((len(w) for w in ws), default=0)
    has_hard = any(c in s for c in HARD)
    if len(s) <= 36 and max_word <= 3 and (has_hard or symbol_ratio(s) >= 0.35):
        return True
    if len(s) <= 18 and len(ws) <= 2 and max_word <= 2 and symbol_ratio(s) >= 0.25:
        return True
    return False


def safe_short_fragment(fragment: str, *, require_signal: bool = False) -> bool:
    if len(fragment.strip()) > 28:
        return False
    if substantive_words(fragment):
        return False
    if not words(fragment) and fragment.strip():
        return True
    if require_signal and not (any(c in fragment for c in HARD) or symbol_ratio(fragment) >= 0.25):
        return False
    return True


def trim_prefix(line: str) -> tuple[str, str | None]:
    # Find first normal word (>=4 letters). Only discard a short prefix that has
    # no substantive word of its own and carries an OCR/symbol signal.
    for match in re.finditer(r"[A-Za-z]{4,}", line):
        prefix = line[:match.start()]
        if not prefix.strip():
            return line, None
        if len(prefix) <= 24 and safe_short_fragment(prefix, require_signal=True):
            return line[match.start():].lstrip(), prefix
        break
    return line, None


def trim_suffix(line: str) -> tuple[str, str | None]:
    # Strongest case: short junk after a completed sentence.
    last = max(line.rfind("."), line.rfind("?"), line.rfind("!"))
    if last >= 0 and last + 1 < len(line):
        suffix = line[last + 1:]
        if safe_short_fragment(suffix, require_signal=False):
            return line[:last + 1].rstrip(), suffix
    # Otherwise trim only a short tail with explicit OCR/symbol evidence.
    m = re.search(r"(\s+[^\s]{1,8}(?:\s+[^\s]{1,5}){0,3})$", line)
    if m:
        suffix = m.group(1)
        if safe_short_fragment(suffix, require_signal=True):
            return line[:m.start()].rstrip(), suffix
    return line, None


def normalize_line(line: str) -> tuple[str, list[str], list[str]]:
    operations: list[str] = []
    removed: list[str] = []
    current = line
    new, prefix = trim_prefix(current)
    if prefix is not None:
        removed.append(prefix)
        operations.append("trim_short_ocr_prefix")
        current = new
    new, suffix = trim_suffix(current)
    if suffix is not None:
        removed.append(suffix)
        operations.append("trim_short_ocr_suffix")
        current = new
    if "\\" in current:
        current = current.replace("\\", " ")
        operations.append("replace_literal_backslash_with_space")
    current = re.sub(r"[ \t]{2,}", " ", current).strip()
    return current, operations, removed


def clean_explanation(text: str) -> tuple[str, list[str], list[str]]:
    out: list[str] = []
    operations: list[str] = []
    removed_fragments: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if PAGE_RE.fullmatch(stripped):
            operations.append("remove_pdf_page_marker")
            removed_fragments.append(stripped)
            continue
        if BRAND_ONLY_RE.fullmatch(stripped):
            operations.append("remove_brand_only_line")
            removed_fragments.append(stripped)
            continue
        if pure_noise_line(line):
            operations.append("remove_short_ocr_noise_line")
            removed_fragments.append(stripped)
            continue
        cleaned, ops, removed = normalize_line(line)
        operations.extend(ops)
        removed_fragments.extend(removed)
        if cleaned:
            out.append(cleaned)
    cleaned_text = "\n".join(out).strip()
    return cleaned_text, sorted(set(operations)), removed_fragments


def main() -> None:
    if not (AUDIT / "manifest.json").exists() or not (AUDIT / "debris_candidates.json").exists():
        raise SystemExit("Effective audit/debris queue is missing")
    debris = json.loads((AUDIT / "debris_candidates.json").read_text(encoding="utf-8"))["candidates"]
    explanation_ids = {row["id"] for row in debris if row["fieldKind"] in {"explanation", "structuredExplanation"}}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    by_chapter: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    op_counts = Counter()
    changed = 0
    deferred = 0
    samples = []

    for subject, slug in SLUGS.items():
        for chapter_path in sorted((AUDIT / slug).glob("chapter_*.json")):
            payload = json.loads(chapter_path.read_text(encoding="utf-8"))
            chapter_id = str(payload["chapterId"])
            for q in payload["questions"]:
                qid = str(q["id"])
                if qid not in explanation_ids:
                    continue
                original = q.get("explanation")
                if not isinstance(original, str) or not original.strip():
                    deferred += 1
                    continue
                cleaned, operations, removed = clean_explanation(original)
                if not cleaned or cleaned == original:
                    deferred += 1
                    continue
                # Fail closed: no generic cleanup may delete a substantive word.
                unsafe_removed = [
                    fragment for fragment in removed
                    if substantive_words(fragment)
                    and not PAGE_RE.fullmatch(fragment.strip())
                    and not BRAND_ONLY_RE.fullmatch(fragment.strip())
                ]
                if unsafe_removed:
                    deferred += 1
                    continue
                row = {
                    "id": qid,
                    "questionNumber": q.get("questionNumber"),
                    "sourcePage": q.get("sourcePage"),
                    "provenance": q.get("provenance"),
                    "operations": operations,
                    "original": original,
                    "cleaned": cleaned,
                    "removedFragments": removed,
                }
                by_chapter[(subject, chapter_id)][qid] = row
                changed += 1
                op_counts.update(operations)
                if len(samples) < 30:
                    samples.append({
                        "subject": subject,
                        "chapterId": chapter_id,
                        "id": qid,
                        "operations": operations,
                        "original": original[:700],
                        "cleaned": cleaned[:700],
                    })

    chapter_index = []
    for (subject, chapter_id), questions in sorted(by_chapter.items(), key=lambda x: (x[0][0], int(x[0][1]))):
        slug = SLUGS[subject]
        path = OUT / slug / f"chapter_{int(chapter_id):03d}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "schemaVersion": 1,
            "policy": "safe-deletion-only-v1",
            "active": False,
            "subject": subject,
            "chapterId": chapter_id,
            "questionCount": len(questions),
            "questions": questions,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        chapter_index.append({
            "subject": subject,
            "chapterId": chapter_id,
            "file": str(path.relative_to(OUT)),
            "questionCount": len(questions),
        })

    summary = {
        "schemaVersion": 1,
        "policy": "safe-deletion-only-v1",
        "active": False,
        "effectiveExplanationCandidates": len(explanation_ids),
        "safeChangedQuestions": changed,
        "deferredCandidates": len(explanation_ids) - changed,
        "chaptersWithSafeChanges": len(chapter_index),
        "operationCounts": dict(sorted(op_counts.items())),
        "chapters": chapter_index,
        "samples": samples,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("SAFE_MARROW_EXPLANATION_CLEANUP_REVIEW_OK", json.dumps({
        "candidates": len(explanation_ids), "safeChanged": changed,
        "deferred": len(explanation_ids) - changed, "chapters": len(chapter_index)
    }, sort_keys=True))


if __name__ == "__main__":
    main()
