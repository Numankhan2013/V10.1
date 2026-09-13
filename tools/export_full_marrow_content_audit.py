#!/usr/bin/env python3
"""Generate read-only full-corpus Marrow content audit projections.

This is a side-lane review aid only. Immutable canonical ED8 source bundles are
never modified. The output intentionally exposes learner-facing raw text so
OCR/code debris can be reviewed by stable ID before display overrides are
created.
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
OUT = DATA / "content_audit_full"

BANKS = {
    "Anatomy": ("anatomy_ch001_063", 1115),
    "Biochemistry": ("biochemistry_ch001_028", 582),
    "Physiology": ("physiology_ch001_043", 1014),
}
SLUGS = {"Anatomy": "anatomy", "Biochemistry": "biochemistry", "Physiology": "physiology"}


def load_bank(prefix: str) -> tuple[dict, str]:
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if not parts:
        raise FileNotFoundError(f"no source shards found for {prefix}")
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    raw = zlib.decompress(base64.b64decode(encoded))
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def qnum(q: dict) -> int:
    try:
        return int(q.get("questionNumber") or 0)
    except (TypeError, ValueError):
        return 0


def chapter_num(q: dict) -> int:
    try:
        return int(q.get("chapterId"))
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"invalid chapterId for {q.get('id')}: {q.get('chapterId')!r}") from exc


def project(q: dict) -> dict:
    structured = q.get("structuredExplanation")
    structured_text = structured.get("text") if isinstance(structured, dict) else None
    return {
        "id": q.get("id"),
        "sourceQuestionId": q.get("sourceQuestionId"),
        "subject": q.get("subject"),
        "chapterId": q.get("chapterId"),
        "chapter": q.get("chapter"),
        "questionNumber": q.get("questionNumber"),
        "question": q.get("question"),
        "options": [
            {"letter": o.get("letter"), "text": o.get("text")}
            for o in (q.get("options") or [])
        ],
        "correctOption": q.get("correctOption"),
        "correctAnswerText": q.get("correctAnswerText"),
        "explanation": q.get("explanation"),
        "structuredExplanationText": structured_text,
        "reviewStatus": q.get("reviewStatus"),
        "sourcePage": q.get("sourcePage"),
        "provenance": q.get("provenance"),
    }


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    manifest = {
        "schemaVersion": 1,
        "purpose": "Read-only full-corpus audit projection for reviewed learner-display cleanup.",
        "derivedOnly": True,
        "immutableSourceModified": False,
        "subjects": [],
    }
    total = 0
    all_ids: set[str] = set()

    for subject, (prefix, expected) in BANKS.items():
        bank, raw_sha = load_bank(prefix)
        questions = bank.get("questions") or []
        if len(questions) != expected:
            raise AssertionError(f"{subject}: expected {expected}, got {len(questions)}")
        grouped: dict[int, list[dict]] = defaultdict(list)
        for q in questions:
            qid = str(q.get("id") or "")
            if not qid or qid in all_ids:
                raise AssertionError(f"missing/duplicate stable ID: {qid!r}")
            all_ids.add(qid)
            grouped[chapter_num(q)].append(q)

        subject_dir = OUT / SLUGS[subject]
        subject_dir.mkdir(parents=True)
        chapters = []
        for chapter in sorted(grouped):
            rows = sorted(grouped[chapter], key=lambda item: (qnum(item), str(item.get("id") or "")))
            payload = {
                "schemaVersion": 1,
                "subject": subject,
                "chapterId": str(chapter),
                "chapter": rows[0].get("chapter") if rows else None,
                "questionCount": len(rows),
                "immutableSourcePrefix": prefix,
                "sourceRawSha256": raw_sha,
                "questions": [project(q) for q in rows],
            }
            path = subject_dir / f"chapter_{chapter:03d}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            chapters.append({"chapterId": str(chapter), "file": str(path.relative_to(OUT)), "questionCount": len(rows)})

        manifest["subjects"].append({
            "subject": subject,
            "immutableSourcePrefix": prefix,
            "sourceRawSha256": raw_sha,
            "questionCount": len(questions),
            "chapterCount": len(grouped),
            "chapters": chapters,
        })
        total += len(questions)

    if total != 2711 or len(all_ids) != 2711:
        raise AssertionError(f"global count mismatch: total={total} unique={len(all_ids)}")
    manifest["totalQuestions"] = total
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FULL_MARROW_CONTENT_AUDIT_OK total=2711 chapters=134")


if __name__ == "__main__":
    main()
