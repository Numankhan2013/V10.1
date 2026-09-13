#!/usr/bin/env python3
"""Promote only non-semantic, detector-clean explanation cleanup edits.

This is intentionally stricter than the review generator. An edit is eligible only
when the safe-cleanup preview leaves that question with zero explanation flags and
every deleted fragment is either an explicit PDF/page/brand marker or contains no
letters or digits at all. Literal backslash-to-space normalization is permitted.

The tool merges eligible explanation fields into existing v2 chapter overrides,
recomputes exact raw-source fingerprints, never touches v1 IDs, and never mutates
immutable source bundles or answer indices.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
REVIEW = DATA / "explanation_cleanup_auto_review"
OUT = DATA / "content_hygiene_overrides_v2"
V1 = DATA / "content_hygiene_overrides_v1.json"

BANKS = {
    "Anatomy": "anatomy_ch001_063",
    "Biochemistry": "biochemistry_ch001_028",
    "Physiology": "physiology_ch001_043",
}
SLUGS = {"Anatomy": "anatomy", "Biochemistry": "biochemistry", "Physiology": "physiology"}
PAGE_RE = re.compile(r"^\s*=+\s*PDF\s+PAGE\s+\d+\s*=+\s*$", re.I)
BRAND_ONLY_RE = re.compile(r"^\s*(?:©\s*)?(?:MARROW|PREPLADDER|QBANK)(?:\s+ED\s*\d+)?\s*$", re.I)
ALNUM_RE = re.compile(r"[A-Za-z0-9]")


def load_bank(prefix: str) -> dict:
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if not parts:
        raise SystemExit(f"Missing Marrow shards: {prefix}")
    raw = zlib.decompress(base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in parts)))
    return json.loads(raw.decode("utf-8"))


def fingerprint(source_by_id: dict[str, dict], ids: set[str]) -> str:
    payload = [{
        "id": qid,
        "question": source_by_id[qid].get("question"),
        "options": [o.get("text") for o in source_by_id[qid].get("options", [])],
        "explanation": source_by_id[qid].get("explanation"),
    } for qid in sorted(ids)]
    return hashlib.sha256(json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")).hexdigest()


def fragment_is_ultrasafe(fragment: str) -> bool:
    s = fragment.strip()
    if not s:
        return True
    if PAGE_RE.fullmatch(s) or BRAND_ONLY_RE.fullmatch(s):
        return True
    return ALNUM_RE.search(s) is None


def main() -> None:
    preview_summary = REVIEW / "preview_summary.json"
    residual_index = REVIEW / "preview_residual_index.json"
    if not preview_summary.exists() or not residual_index.exists():
        raise SystemExit("Run safe explanation cleanup preview first")

    residual = json.loads(residual_index.read_text(encoding="utf-8"))
    residual_ids = {
        q["id"]
        for chapter in residual.get("chapters", [])
        for q in chapter.get("questions", [])
    }
    v1_ids = set(json.loads(V1.read_text(encoding="utf-8"))["questions"])

    source_by_id = {
        str(q["id"]): q
        for prefix in BANKS.values()
        for q in load_bank(prefix).get("questions", [])
    }
    if len(source_by_id) != 2711:
        raise SystemExit(f"Canonical Marrow source count changed: {len(source_by_id)}")

    eligible: dict[tuple[str, str], dict[str, str]] = {}
    rejected_semantic = 0
    rejected_residual = 0
    rejected_v1 = 0

    for path in sorted(REVIEW.glob("**/chapter_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("policy") != "safe-deletion-only-v1" or payload.get("active") is not False:
            continue
        subject = str(payload["subject"])
        chapter = str(payload["chapterId"])
        for qid, row in (payload.get("questions") or {}).items():
            if qid in residual_ids:
                rejected_residual += 1
                continue
            if qid in v1_ids:
                rejected_v1 += 1
                continue
            removed = row.get("removedFragments") or []
            if any(not fragment_is_ultrasafe(fragment) for fragment in removed):
                rejected_semantic += 1
                continue
            cleaned = row.get("cleaned")
            if not isinstance(cleaned, str) or not cleaned.strip():
                raise SystemExit(f"Invalid cleaned explanation: {qid}")
            source = source_by_id.get(qid)
            if source is None or source.get("subject") != subject or str(source.get("chapterId")) != chapter:
                raise SystemExit(f"Review artifact scope mismatch: {qid}")
            eligible.setdefault((subject, chapter), {})[qid] = cleaned

    added = 0
    touched_files = 0
    for (subject, chapter), cleanups in sorted(eligible.items(), key=lambda item: (item[0][0], int(item[0][1]))):
        out_path = OUT / SLUGS[subject] / f"chapter_{int(chapter):03d}.json"
        if out_path.exists():
            active = json.loads(out_path.read_text(encoding="utf-8"))
            if active.get("schemaVersion") != 2 or active.get("subject") != subject or str(active.get("chapterId")) != chapter:
                raise SystemExit(f"Unexpected active override identity: {out_path}")
            questions = active.get("questions") or {}
        else:
            active = {
                "schemaVersion": 2,
                "purpose": "Ultra-safe non-semantic learner-display explanation cleanup.",
                "subject": subject,
                "chapterId": chapter,
                "sourceFingerprint": "",
                "questions": {},
            }
            questions = active["questions"]

        before = json.dumps(questions, ensure_ascii=False, sort_keys=True)
        for qid, cleaned in cleanups.items():
            row = questions.setdefault(qid, {})
            existing = row.get("explanation")
            if existing is not None and existing != cleaned:
                # A manually reviewed explanation always wins over automation.
                continue
            if existing is None:
                row["explanation"] = cleaned
                added += 1

        if json.dumps(questions, ensure_ascii=False, sort_keys=True) == before:
            continue
        ids = set(questions)
        if ids & v1_ids:
            raise SystemExit(f"v2/v1 overlap introduced: {out_path}")
        active["sourceFingerprint"] = fingerprint(source_by_id, ids)
        if "Ultra-safe" not in str(active.get("purpose") or ""):
            active["purpose"] = (str(active.get("purpose") or "Reviewed source-faithful learner-display cleanup.").rstrip(". ") + "; Ultra-safe non-semantic explanation debris cleanup.")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(active, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        touched_files += 1

    print("ULTRASAFE_MARROW_EXPLANATION_PROMOTION_OK", json.dumps({
        "eligibleQuestions": sum(len(v) for v in eligible.values()),
        "addedExplanations": added,
        "touchedFiles": touched_files,
        "rejectedResidual": rejected_residual,
        "rejectedSemanticFragments": rejected_semantic,
        "rejectedV1Overlap": rejected_v1,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
