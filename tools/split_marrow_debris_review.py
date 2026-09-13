#!/usr/bin/env python3
"""Split the Marrow debris queue into compact per-chapter review packets."""
from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "marrow" / "content_audit_full"
OUT = AUDIT / "review_packets"
SLUGS = {"Anatomy": "anatomy", "Biochemistry": "biochemistry", "Physiology": "physiology"}


def main() -> None:
    queue = json.loads((AUDIT / "debris_candidates.json").read_text(encoding="utf-8"))["candidates"]
    by_key: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in queue:
        by_key[(row["subject"], row["chapterId"], row["id"])].append(row)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    index = []

    for subject, slug in SLUGS.items():
        source_dir = AUDIT / slug
        target_dir = OUT / slug
        target_dir.mkdir(parents=True)
        for chapter_path in sorted(source_dir.glob("chapter_*.json")):
            chapter = json.loads(chapter_path.read_text(encoding="utf-8"))
            rows = []
            for q in chapter["questions"]:
                key = (subject, str(q["chapterId"]), str(q["id"]))
                flagged = by_key.get(key)
                if not flagged:
                    continue
                qopt = [r for r in flagged if r["fieldKind"] in {"question", "option"}]
                expl = [r for r in flagged if r["fieldKind"] in {"explanation", "structuredExplanation"}]
                rows.append({
                    "id": q["id"],
                    "questionNumber": q.get("questionNumber"),
                    "sourcePage": q.get("sourcePage"),
                    "reviewStatus": q.get("reviewStatus"),
                    "question": q.get("question"),
                    "options": q.get("options"),
                    "correctOption": q.get("correctOption"),
                    "questionOptionFlags": [
                        {"field": r["field"], "severity": r["severity"], "reasons": r["reasons"], "suspectLines": r["suspectLines"]}
                        for r in qopt
                    ],
                    "explanationFlags": [
                        {"field": r["field"], "severity": r["severity"], "reasons": r["reasons"], "suspectLines": r["suspectLines"]}
                        for r in expl
                    ],
                    "explanation": q.get("explanation") if expl else None,
                })
            if not rows:
                continue
            out_path = target_dir / chapter_path.name
            out_path.write_text(json.dumps({
                "schemaVersion": 1,
                "purpose": "Compact manual-review packet. No automatic rewrite authority.",
                "subject": subject,
                "chapterId": chapter["chapterId"],
                "chapter": chapter.get("chapter"),
                "candidateQuestionCount": len(rows),
                "questionOptionCandidateCount": sum(bool(r["questionOptionFlags"]) for r in rows),
                "explanationCandidateCount": sum(bool(r["explanationFlags"]) for r in rows),
                "questions": rows,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            index.append({
                "subject": subject,
                "chapterId": chapter["chapterId"],
                "chapter": chapter.get("chapter"),
                "file": str(out_path.relative_to(AUDIT)),
                "candidateQuestionCount": len(rows),
                "questionOptionCandidateCount": sum(bool(r["questionOptionFlags"]) for r in rows),
                "explanationCandidateCount": sum(bool(r["explanationFlags"]) for r in rows),
            })

    (OUT / "index.json").write_text(json.dumps({"chapters": index}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MARROW_DEBRIS_REVIEW_PACKETS_OK chapters={len(index)}")


if __name__ == "__main__":
    main()
