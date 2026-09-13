#!/usr/bin/env python3
"""Build a read-only audit of the *effective* learner-visible Marrow bank.

The immutable ED8 projection under content_audit_full is copied and then the
accepted v1 plus chapter-scoped v2 display overrides are applied. Every override
is re-fingerprinted against the raw projection before it is allowed to affect the
audit. correctOption is never mutated. This gives QA the text learners actually
see instead of repeatedly auditing known-dirty raw source strings.
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
RAW = DATA / "content_audit_full"
OUT = DATA / "content_audit_effective"
V1 = DATA / "content_hygiene_overrides_v1.json"
V2 = DATA / "content_hygiene_overrides_v2"
SLUGS = {"Anatomy": "anatomy", "Biochemistry": "biochemistry", "Physiology": "physiology"}


def digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")).hexdigest()


def main() -> None:
    manifest_path = RAW / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit("Run export_full_marrow_content_audit.py first")
    raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if int(raw_manifest.get("totalQuestions", 0)) != 2711:
        raise SystemExit("Raw audit corpus count changed")

    chapters: dict[tuple[str, str], dict] = {}
    raw_by_id: dict[str, dict] = {}
    effective_by_id: dict[str, dict] = {}
    correct_by_id: dict[str, int] = {}
    for subject, slug in SLUGS.items():
        for path in sorted((RAW / slug).glob("chapter_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            copied = copy.deepcopy(payload)
            chapters[(subject, str(payload["chapterId"]))] = copied
            for raw_q, effective_q in zip(payload["questions"], copied["questions"]):
                qid = str(raw_q["id"])
                if qid in raw_by_id:
                    raise SystemExit(f"Duplicate stable ID in raw audit: {qid}")
                raw_by_id[qid] = raw_q
                effective_by_id[qid] = effective_q
                correct_by_id[qid] = int(raw_q["correctOption"])
    if len(raw_by_id) != 2711:
        raise SystemExit(f"Effective audit source count mismatch: {len(raw_by_id)}")

    applied_ids: set[str] = set()
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    v1_questions = v1.get("questions") or {}
    v1_source = [{
        "id": qid,
        "question": raw_by_id[qid].get("question"),
        "options": [o.get("text") for o in raw_by_id[qid].get("options", [])],
    } for qid in sorted(v1_questions)]
    if digest(v1_source) != v1.get("sourceFingerprint"):
        raise SystemExit("V1 content-hygiene fingerprint mismatch in effective audit")
    for qid, override in v1_questions.items():
        q = effective_by_id[qid]
        q["question"] = str(override["question"]).strip()
        clean_options = [str(v).strip() for v in override["options"]]
        for option, value in zip(q["options"], clean_options):
            option["text"] = value
        q["correctAnswerText"] = clean_options[int(q["correctOption"]) - 1]
        applied_ids.add(qid)

    v2_files = sorted(V2.glob("**/*.json")) if V2.exists() else []
    v2_explanation_count = 0
    for path in v2_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        questions = payload.get("questions") or {}
        ids = set(questions)
        if ids & applied_ids:
            raise SystemExit(f"V2 overlaps another active cleanup: {path}")
        if not ids.issubset(raw_by_id):
            raise SystemExit(f"V2 has unknown IDs: {path}")
        source = [{
            "id": qid,
            "question": raw_by_id[qid].get("question"),
            "options": [o.get("text") for o in raw_by_id[qid].get("options", [])],
            "explanation": raw_by_id[qid].get("explanation"),
        } for qid in sorted(ids)]
        if digest(source) != payload.get("sourceFingerprint"):
            raise SystemExit(f"V2 fingerprint mismatch: {path}")
        for qid, override in questions.items():
            raw_q = raw_by_id[qid]
            q = effective_by_id[qid]
            if str(raw_q.get("subject")) != str(payload.get("subject")) or str(raw_q.get("chapterId")) != str(payload.get("chapterId")):
                raise SystemExit(f"V2 scope escape: {path} {qid}")
            if "question" in override:
                q["question"] = str(override["question"]).strip()
            if "options" in override:
                clean_options = [str(v).strip() for v in override["options"]]
                if len(clean_options) != 4:
                    raise SystemExit(f"V2 option count mismatch: {qid}")
                for option, value in zip(q["options"], clean_options):
                    option["text"] = value
                q["correctAnswerText"] = clean_options[int(q["correctOption"]) - 1]
            if "explanation" in override:
                text = str(override["explanation"]).strip()
                q["explanation"] = text
                q["structuredExplanationText"] = text
                v2_explanation_count += 1
            applied_ids.add(qid)

    for qid, expected in correct_by_id.items():
        if int(effective_by_id[qid]["correctOption"]) != expected:
            raise SystemExit(f"Answer index changed while applying display cleanup: {qid}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    effective_manifest = copy.deepcopy(raw_manifest)
    effective_manifest.update({
        "schemaVersion": 1,
        "purpose": "Read-only effective learner-display audit after source-fingerprinted Marrow overrides.",
        "derivedOnly": True,
        "immutableSourceModified": False,
        "appliedDisplayOverrideQuestions": len(applied_ids),
        "appliedV1Questions": len(v1_questions),
        "appliedV2Files": len(v2_files),
        "appliedV2ExplanationQuestions": v2_explanation_count,
    })
    for subject, slug in SLUGS.items():
        (OUT / slug).mkdir(parents=True)
        for (chapter_subject, chapter_id), payload in chapters.items():
            if chapter_subject != subject:
                continue
            path = OUT / slug / f"chapter_{int(chapter_id):03d}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(effective_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "EFFECTIVE_MARROW_CONTENT_AUDIT_OK "
        f"questions=2711 override_questions={len(applied_ids)} v1={len(v1_questions)} "
        f"v2_files={len(v2_files)} v2_explanations={v2_explanation_count}"
    )


if __name__ == "__main__":
    main()
