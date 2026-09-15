#!/usr/bin/env python3
"""Promote reviewed Marrow cleanup proposals into source-fingerprinted v2 overrides.

Proposal files are inert review artifacts. This tool verifies their stable IDs
against the immutable complete Marrow bundles, computes a fingerprint from the
exact raw learner fields, and writes active v2 override files. It never mutates
source bundles or answer indexes.

A proposal may safely extend an existing active chapter override. Existing fields
are retained, new fields are merged, and any conflicting value hard-fails. This
allows independently reviewed stem/options and explanation passes to coexist.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
PROPOSALS = DATA / "content_hygiene_proposals"
OUT = DATA / "content_hygiene_overrides_v2"
V1 = DATA / "content_hygiene_overrides_v1.json"

BANKS = {
    "Anatomy": "anatomy_ch001_063",
    "Biochemistry": "biochemistry_ch001_028",
    "Physiology": "physiology_ch001_043",
}
SLUGS = {"Anatomy": "anatomy", "Biochemistry": "biochemistry", "Physiology": "physiology"}
FORBIDDEN = ("[object Object]", '{\"text\"', '{\"type\"', '\"content\":', "```")


def load(prefix: str) -> dict:
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


def validate_clean(qid: str, override: dict) -> None:
    allowed = {"question", "options", "explanation"}
    if not isinstance(override, dict) or not override or not set(override).issubset(allowed):
        raise SystemExit(f"Invalid cleanup fields for {qid}: {override!r}")
    if "question" in override:
        value = override["question"]
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"Empty question cleanup: {qid}")
    if "options" in override:
        values = override["options"]
        if not isinstance(values, list) or len(values) != 4 or any(not isinstance(v, str) or not v.strip() for v in values):
            raise SystemExit(f"Invalid option cleanup: {qid}")
    if "explanation" in override:
        value = override["explanation"]
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"Empty explanation cleanup: {qid}")
    values = []
    for key in ("question", "explanation"):
        if key in override:
            values.append(override[key])
    values.extend(override.get("options") or [])
    for value in values:
        if any(marker in value for marker in FORBIDDEN):
            raise SystemExit(f"Serialized/code leakage remains in reviewed cleanup: {qid}")


def merge_questions(existing: dict, proposed: dict, path: Path) -> dict:
    merged = copy.deepcopy(existing)
    for qid, proposal_override in proposed.items():
        target = merged.setdefault(qid, {})
        if not isinstance(target, dict):
            raise SystemExit(f"Invalid existing override for {qid}: {path}")
        for field, value in proposal_override.items():
            if field in target and target[field] != value:
                raise SystemExit(f"Reviewed proposal conflicts with active {field}: {path} {qid}")
            target[field] = copy.deepcopy(value)
    return merged


def v1_compatible(qid: str, override: dict, v1_ids: set[str], where: Path) -> None:
    if qid in v1_ids and (not isinstance(override, dict) or set(override) != {"explanation"}):
        raise SystemExit(f"Cleanup conflicts with accepted v1 question/options ownership: {where} {qid}")


def main() -> None:
    if not PROPOSALS.exists():
        print("MARROW_CLEANUP_PROPOSALS_NONE")
        return
    banks = {subject: load(prefix) for subject, prefix in BANKS.items()}
    source_by_id = {
        str(q.get("id")): q
        for bank in banks.values()
        for q in bank.get("questions", [])
    }
    if len(source_by_id) != 2711:
        raise SystemExit(f"Canonical Marrow source count changed: {len(source_by_id)}")
    v1_ids = set(json.loads(V1.read_text(encoding="utf-8"))["questions"])
    seen: set[str] = set()
    promoted = 0
    fields = 0

    for path in sorted(PROPOSALS.glob("**/*.json")):
        proposal = json.loads(path.read_text(encoding="utf-8"))
        if proposal.get("proposalVersion") != 1 or proposal.get("reviewStatus") != "REVIEWED":
            raise SystemExit(f"Proposal is not explicitly reviewed: {path}")
        subject = str(proposal.get("subject") or "")
        chapter = str(proposal.get("chapterId") or "")
        questions = proposal.get("questions") or {}
        if subject not in BANKS or not chapter or not isinstance(questions, dict) or not questions:
            raise SystemExit(f"Proposal identity/content invalid: {path}")
        ids = set(questions)
        if ids & seen:
            raise SystemExit(f"Duplicate proposal stable IDs: {path}")
        if not ids.issubset(source_by_id):
            raise SystemExit(f"Proposal includes unknown IDs: {path}")
        for qid, override in questions.items():
            source = source_by_id[qid]
            if source.get("subject") != subject or str(source.get("chapterId")) != chapter:
                raise SystemExit(f"Proposal scope escape: {path} {qid}")
            validate_clean(qid, override)
            v1_compatible(qid, override, v1_ids, path)
            fields += len(override)

        out_path = OUT / SLUGS[subject] / f"chapter_{int(chapter):03d}.json"
        existing_questions: dict = {}
        existing_purpose = ""
        if out_path.exists():
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if existing.get("schemaVersion") != 2 or existing.get("subject") != subject or str(existing.get("chapterId")) != chapter:
                raise SystemExit(f"Unexpected active chapter identity: {out_path}")
            existing_questions = existing.get("questions") or {}
            existing_purpose = str(existing.get("purpose") or "")

        merged = merge_questions(existing_questions, questions, path)
        merged_ids = set(merged)
        for qid in merged_ids & v1_ids:
            v1_compatible(qid, merged[qid], v1_ids, out_path)
        purpose = str(proposal.get("purpose") or "Reviewed source-faithful learner-display cleanup.")
        if existing_purpose and existing_purpose != purpose:
            purpose = existing_purpose.rstrip(". ") + "; additional reviewed source-faithful cleanup."
        payload = {
            "schemaVersion": 2,
            "purpose": purpose,
            "subject": subject,
            "chapterId": chapter,
            "sourceFingerprint": fingerprint(source_by_id, merged_ids),
            "questions": merged,
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        seen.update(ids)
        promoted += len(ids)
    print(f"MARROW_CLEANUP_PROPOSALS_PROMOTED files={len(list(PROPOSALS.glob('**/*.json')))} questions={promoted} fields={fields}")


if __name__ == "__main__":
    main()
