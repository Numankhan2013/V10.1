#!/usr/bin/env python3
"""Generate read-only, per-chapter audit views of immutable Marrow source bundles.

The deployment/source-of-truth bundles remain the sharded *.zlib.b64.part* files.
This tool only decodes those bundles and writes deterministic, human-readable
chapter projections so repository/connector-only automation can perform source
audits without guessing or rewriting raw Marrow data.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
OUT = DATA / "source_audit"

BANKS = {
    "Anatomy": "anatomy_phase_a",
    "Biochemistry": "biochemistry_phase_a",
    "Physiology": "physiology_ch001_033",
}
SLUGS = {
    "Anatomy": "anatomy",
    "Biochemistry": "biochemistry",
    "Physiology": "physiology",
}
EXPECTED_COUNTS = {
    "Anatomy": 819,
    "Biochemistry": 543,
    "Physiology": 753,
}


def load_sharded(prefix: str) -> tuple[dict, str]:
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if not parts:
        raise FileNotFoundError(f"no source shards found for {prefix}")
    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    raw = zlib.decompress(base64.b64decode(encoded))
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def chapter_number(question: dict) -> int:
    value = question.get("chapterId")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"invalid chapterId for {question.get('id')}: {value!r}") from exc


def question_number(question: dict) -> int:
    value = question.get("questionNumber")
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def write_subject(subject: str, prefix: str) -> dict:
    bank, raw_sha = load_sharded(prefix)
    questions = bank.get("questions") or []
    if len(questions) != EXPECTED_COUNTS[subject]:
        raise AssertionError(
            f"{subject} count changed: expected {EXPECTED_COUNTS[subject]}, got {len(questions)}"
        )

    grouped: dict[int, list[dict]] = defaultdict(list)
    seen: set[str] = set()
    for question in questions:
        qid = str(question.get("id") or "")
        if not qid:
            raise AssertionError(f"{subject} question missing id")
        if qid in seen:
            raise AssertionError(f"duplicate source id in {subject}: {qid}")
        seen.add(qid)
        grouped[chapter_number(question)].append(question)

    subject_dir = OUT / SLUGS[subject]
    subject_dir.mkdir(parents=True, exist_ok=True)
    for old in subject_dir.glob("chapter_*.json"):
        old.unlink()

    chapter_manifest = []
    for chapter in sorted(grouped):
        rows = sorted(grouped[chapter], key=lambda q: (question_number(q), str(q.get("id") or "")))
        payload = {
            "schemaVersion": 1,
            "purpose": "Derived read-only audit view. Immutable source remains the sharded Marrow bundle.",
            "subject": subject,
            "chapterId": str(chapter),
            "questionCount": len(rows),
            "immutableSourcePrefix": prefix,
            "sourceRawSha256": raw_sha,
            "questions": rows,
        }
        filename = f"chapter_{chapter:03d}.json"
        encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        (subject_dir / filename).write_text(encoded, encoding="utf-8")
        chapter_manifest.append({
            "chapterId": str(chapter),
            "file": f"{SLUGS[subject]}/{filename}",
            "questionCount": len(rows),
        })

    return {
        "subject": subject,
        "immutableSourcePrefix": prefix,
        "sourceRawSha256": raw_sha,
        "questionCount": len(questions),
        "chapterCount": len(grouped),
        "chapters": chapter_manifest,
    }


def generate() -> dict:
    if OUT.exists():
        # Only derived files live here. Rebuild from immutable source each time.
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    subjects = [write_subject(subject, prefix) for subject, prefix in BANKS.items()]
    total = sum(item["questionCount"] for item in subjects)
    if total != 2115:
        raise AssertionError(f"unexpected total source count: {total}")

    manifest = {
        "schemaVersion": 1,
        "purpose": "Deterministic connector-readable audit views derived from immutable Marrow source bundles.",
        "immutable": False,
        "derivedOnly": True,
        "totalQuestions": total,
        "subjects": subjects,
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Generate and print summary; files are still deterministic outputs.")
    args = parser.parse_args()
    manifest = generate()
    summary = ", ".join(
        f"{row['subject']}={row['questionCount']}/{row['chapterCount']}ch"
        for row in manifest["subjects"]
    )
    print(f"MARROW_SOURCE_AUDIT_OK total={manifest['totalQuestions']} {summary}")


if __name__ == "__main__":
    main()
