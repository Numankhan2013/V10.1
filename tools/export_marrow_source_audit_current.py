#!/usr/bin/env python3
"""Generate connector-readable per-chapter audit views for the live 2,711-question Marrow corpus.

This is derived read-only audit material. Immutable sharded ED8 bundles remain the source of truth.
"""
from __future__ import annotations

import base64
import hashlib
import json
import shutil
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
OUT = DATA / "source_audit_current"

BANKS = {
    "Anatomy": "anatomy_ch001_063",
    "Biochemistry": "biochemistry_ch001_028",
    "Physiology": "physiology_ch001_043",
}
SLUGS = {
    "Anatomy": "anatomy",
    "Biochemistry": "biochemistry",
    "Physiology": "physiology",
}
EXPECTED_COUNTS = {
    "Anatomy": 1115,
    "Biochemistry": 582,
    "Physiology": 1014,
}


def load_sharded(prefix: str) -> tuple[dict, str]:
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if not parts:
        raise FileNotFoundError(f"no source shards found for {prefix}")
    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in parts)
    raw = zlib.decompress(base64.b64decode(encoded))
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def as_int(question: dict, key: str) -> int:
    try:
        return int(question.get(key))
    except (TypeError, ValueError):
        return 0


def write_subject(subject: str, prefix: str) -> dict:
    bank, raw_sha = load_sharded(prefix)
    questions = bank.get("questions") or []
    expected = EXPECTED_COUNTS[subject]
    if len(questions) != expected:
        raise AssertionError(f"{subject} count changed: expected {expected}, got {len(questions)}")

    grouped: dict[int, list[dict]] = defaultdict(list)
    seen: set[str] = set()
    for question in questions:
        qid = str(question.get("id") or "")
        if not qid or qid in seen:
            raise AssertionError(f"missing/duplicate source id in {subject}: {qid!r}")
        seen.add(qid)
        chapter = as_int(question, "chapterId")
        if chapter <= 0:
            raise AssertionError(f"invalid chapterId for {qid}: {question.get('chapterId')!r}")
        grouped[chapter].append(question)

    subject_dir = OUT / SLUGS[subject]
    subject_dir.mkdir(parents=True, exist_ok=True)
    chapter_manifest = []
    for chapter in sorted(grouped):
        rows = sorted(grouped[chapter], key=lambda q: (as_int(q, "questionNumber"), str(q.get("id") or "")))
        payload = {
            "schemaVersion": 1,
            "purpose": "Derived read-only audit view of the live 2,711-question corpus.",
            "subject": subject,
            "chapterId": str(chapter),
            "questionCount": len(rows),
            "immutableSourcePrefix": prefix,
            "sourceRawSha256": raw_sha,
            "questions": rows,
        }
        filename = f"chapter_{chapter:03d}.json"
        (subject_dir / filename).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        chapter_manifest.append({"chapterId": str(chapter), "file": f"{SLUGS[subject]}/{filename}", "questionCount": len(rows)})

    return {
        "subject": subject,
        "immutableSourcePrefix": prefix,
        "sourceRawSha256": raw_sha,
        "questionCount": len(questions),
        "chapterCount": len(grouped),
        "chapters": chapter_manifest,
    }


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    subjects = [write_subject(subject, prefix) for subject, prefix in BANKS.items()]
    total = sum(row["questionCount"] for row in subjects)
    if total != 2711:
        raise AssertionError(f"unexpected total source count: {total}")
    manifest = {
        "schemaVersion": 1,
        "purpose": "Deterministic connector-readable audit views derived from immutable Marrow source bundles.",
        "derivedOnly": True,
        "totalQuestions": total,
        "subjects": subjects,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("MARROW_SOURCE_AUDIT_CURRENT_OK total=2711 " + " ".join(f"{row['subject']}={row['questionCount']}/{row['chapterCount']}ch" for row in subjects))


if __name__ == "__main__":
    main()
