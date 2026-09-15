#!/usr/bin/env python3
"""Fail-closed validation for chapter-scoped Marrow learner-display overrides v2."""
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
V2 = DATA / "content_hygiene_overrides_v2"
V1 = DATA / "content_hygiene_overrides_v1.json"
BANKS = {
    "Anatomy": "anatomy_ch001_063",
    "Biochemistry": "biochemistry_ch001_028",
    "Physiology": "physiology_ch001_043",
}
SERIALIZED = ("[object Object]", '{\"text\"', '{\"type\"', '\"content\":', "```")
BRAND_LINE = re.compile(r"(?im)^\s*(?:©?\s*MARROW|Sold by\s+@\w+)\s*$")


def load(prefix: str) -> dict:
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if not parts:
        raise SystemExit(f"Missing source shards: {prefix}")
    raw = zlib.decompress(base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in parts)))
    return json.loads(raw.decode("utf-8"))


def fp(source_by_id: dict[str, dict], ids: set[str]) -> str:
    payload = [{
        "id": qid,
        "question": source_by_id[qid].get("question"),
        "options": [o.get("text") for o in source_by_id[qid].get("options", [])],
        "explanation": source_by_id[qid].get("explanation"),
    } for qid in sorted(ids)]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def main() -> None:
    banks = {subject: load(prefix) for subject, prefix in BANKS.items()}
    source_by_id = {
        str(q.get("id")): q
        for bank in banks.values()
        for q in bank.get("questions", [])
    }
    if len(source_by_id) != 2711:
        raise SystemExit(f"Canonical corpus count changed: {len(source_by_id)}")
    v1_ids = set(json.loads(V1.read_text(encoding="utf-8"))["questions"])
    seen: set[str] = set()
    changed_fields = 0
    explanation_count = 0
    files = sorted(V2.glob("**/*.json")) if V2.exists() else []

    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schemaVersion") != 2:
            raise SystemExit(f"Bad v2 schema: {path}")
        subject = str(payload.get("subject") or "")
        chapter = str(payload.get("chapterId") or "")
        questions = payload.get("questions") or {}
        ids = set(questions)
        if not ids or not ids.issubset(source_by_id):
            raise SystemExit(f"Unknown/empty v2 IDs: {path}")
        # V1 owns reviewed question/options for Physiology Ch5/Ch7. V2 may
        # safely add an explanation for the same stable ID, but may never
        # replace or duplicate those v1-owned learner fields.
        for qid in ids & v1_ids:
            override = questions[qid]
            if not isinstance(override, dict) or set(override) != {"explanation"}:
                raise SystemExit(f"v2 conflicts with accepted v1 question/options ownership: {path} {qid}")
        if ids & seen:
            raise SystemExit(f"Duplicate stable IDs across v2 files: {path}")
        if fp(source_by_id, ids) != payload.get("sourceFingerprint"):
            raise SystemExit(f"Source fingerprint mismatch: {path}")

        for qid, override in questions.items():
            source = source_by_id[qid]
            if source.get("subject") != subject or str(source.get("chapterId")) != chapter:
                raise SystemExit(f"Subject/chapter scope escape: {path} {qid}")
            before = copy.deepcopy(source)
            after = copy.deepcopy(source)
            allowed = {"question", "options", "explanation"}
            if not isinstance(override, dict) or not override or not set(override).issubset(allowed):
                raise SystemExit(f"Invalid override shape: {qid}")
            if "question" in override:
                after["question"] = override["question"].strip()
                changed_fields += 1
            if "options" in override:
                values = override["options"]
                if not isinstance(values, list) or len(values) != 4:
                    raise SystemExit(f"Invalid option count: {qid}")
                for option, value in zip(after.get("options", []), values):
                    option["text"] = value.strip()
                after["correctAnswerText"] = values[int(before["correctOption"]) - 1].strip()
                changed_fields += 4
            if "explanation" in override:
                after["explanation"] = override["explanation"].strip()
                changed_fields += 1
                explanation_count += 1

            if after.get("correctOption") != before.get("correctOption"):
                raise SystemExit(f"Answer index changed: {qid}")
            if [o.get("letter") for o in after.get("options", [])] != ["A", "B", "C", "D"]:
                raise SystemExit(f"Option-letter contract changed: {qid}")
            visible = [after.get("question", ""), after.get("explanation", ""), after.get("correctAnswerText", "")]
            visible.extend(o.get("text", "") for o in after.get("options", []))
            for value in visible:
                if not isinstance(value, str):
                    raise SystemExit(f"Non-string learner value: {qid}")
                if any(marker in value for marker in SERIALIZED):
                    raise SystemExit(f"Serialized/code marker remains: {qid}")
                if BRAND_LINE.search(value):
                    raise SystemExit(f"Source footer/brand line remains in reviewed override: {qid}")
        seen.update(ids)

    print(
        "MARROW_CONTENT_OVERRIDES_V2_TEST_OK "
        f"files={len(files)} questions={len(seen)} changed_fields={changed_fields} explanations={explanation_count}"
    )


if __name__ == "__main__":
    main()
