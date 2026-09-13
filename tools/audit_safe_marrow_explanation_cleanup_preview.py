#!/usr/bin/env python3
"""Preview the safe explanation review edits and re-run debris detection.

This never writes active overrides. It copies the effective learner audit into an
inert preview directory, overlays review-only cleaned explanation strings, and
runs the same detector/splitter there so the residual workload is measurable.
"""
from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path

import find_marrow_visible_debris as detector
import split_marrow_debris_review as splitter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
EFFECTIVE = DATA / "content_audit_effective"
REVIEW = DATA / "explanation_cleanup_auto_review"
PREVIEW = REVIEW / "preview_effective"
SLUGS = {"Anatomy": "anatomy", "Biochemistry": "biochemistry", "Physiology": "physiology"}


def main() -> None:
    if not (REVIEW / "summary.json").exists():
        raise SystemExit("Generate safe explanation cleanup review first")
    if PREVIEW.exists():
        shutil.rmtree(PREVIEW)
    PREVIEW.mkdir(parents=True)

    manifest = json.loads((EFFECTIVE / "manifest.json").read_text(encoding="utf-8"))
    manifest.update({
        "purpose": "INERT preview after safe-deletion-only explanation cleanup.",
        "previewOnly": True,
        "active": False,
    })
    (PREVIEW / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cleanup_by_id: dict[str, str] = {}
    for path in REVIEW.glob("**/chapter_*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("active") is not False or payload.get("policy") != "safe-deletion-only-v1":
            raise SystemExit(f"Unexpected review artifact identity: {path}")
        for qid, row in (payload.get("questions") or {}).items():
            cleanup_by_id[qid] = row["cleaned"]

    applied = 0
    for subject, slug in SLUGS.items():
        target = PREVIEW / slug
        target.mkdir(parents=True)
        for source_path in sorted((EFFECTIVE / slug).glob("chapter_*.json")):
            payload = json.loads(source_path.read_text(encoding="utf-8"))
            for q in payload["questions"]:
                qid = str(q["id"])
                if qid in cleanup_by_id:
                    q["explanation"] = cleanup_by_id[qid]
                    q["structuredExplanationText"] = cleanup_by_id[qid]
                    applied += 1
            (target / source_path.name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if applied != len(cleanup_by_id):
        raise SystemExit(f"Safe-preview application mismatch: applied={applied} cleanups={len(cleanup_by_id)}")

    detector.AUDIT = PREVIEW
    detector.OUT = PREVIEW / "debris_candidates.json"
    detector.SUMMARY = PREVIEW / "debris_summary.json"
    detector.main()
    splitter.AUDIT = PREVIEW
    splitter.OUT = PREVIEW / "review_packets"
    splitter.main()

    residual = json.loads((PREVIEW / "review_packets" / "summary.json").read_text(encoding="utf-8"))
    candidates = json.loads((PREVIEW / "debris_candidates.json").read_text(encoding="utf-8"))["candidates"]
    by_question: dict[tuple[str, str, str], dict] = {}
    by_chapter: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in candidates:
        if row.get("fieldKind") not in {"explanation", "structuredExplanation"}:
            continue
        key = (str(row["subject"]), str(row["chapterId"]), str(row["id"]))
        current = by_question.setdefault(key, {
            "id": str(row["id"]),
            "questionNumber": row.get("questionNumber"),
            "maxSeverity": 0,
            "reasons": set(),
            "suspectLines": [],
        })
        current["maxSeverity"] = max(current["maxSeverity"], int(row.get("severity") or 0))
        current["reasons"].update(row.get("reasons") or [])
        for line in row.get("suspectLines") or []:
            if line not in current["suspectLines"]:
                current["suspectLines"].append(line)

    for (subject, chapter, _qid), item in by_question.items():
        item["reasons"] = sorted(item["reasons"])
        item["suspectLines"] = item["suspectLines"][:8]
        by_chapter[(subject, chapter)].append(item)

    residual_index = {
        "schemaVersion": 1,
        "active": False,
        "previewOnly": True,
        "chapters": [],
    }
    for (subject, chapter), questions in sorted(by_chapter.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
        questions.sort(key=lambda q: (-(q["maxSeverity"]), int(q.get("questionNumber") or 0), q["id"]))
        residual_index["chapters"].append({
            "subject": subject,
            "chapterId": chapter,
            "questionCount": len(questions),
            "maxSeverity": max(q["maxSeverity"] for q in questions),
            "questions": questions,
        })

    report = {
        "schemaVersion": 1,
        "active": False,
        "previewOnly": True,
        "safeCleanupQuestionsApplied": applied,
        "residual": residual,
        "residualExplanationQuestions": len(by_question),
        "residualChapters": len(by_chapter),
    }
    (REVIEW / "preview_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REVIEW / "preview_residual_index.json").write_text(json.dumps(residual_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("SAFE_MARROW_EXPLANATION_PREVIEW_OK", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
