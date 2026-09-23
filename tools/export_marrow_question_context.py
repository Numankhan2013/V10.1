#!/usr/bin/env python3
"""Export a bounded stable-ID slice from immutable canonical Marrow bundles.

This is a read-only automation helper. It validates the canonical bundle manifest,
decodes the source records, selects a contiguous chapter/question range, and
writes JSON to stdout. It never rewrites source bundles.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
PREFIX = {
    "Anatomy": "anatomy_ch001_063",
    "Biochemistry": "biochemistry_ch001_028",
    "Physiology": "physiology_ch001_043",
}


def load_bundle(subject: str) -> dict:
    prefix = PREFIX[subject]
    manifest = json.loads((DATA / f"{prefix}_manifest.json").read_text(encoding="utf-8"))
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    assert len(parts) == int(manifest["parts"]), (prefix, len(parts), manifest["parts"])
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    assert len(encoded) == int(manifest["base64_chars"])
    compressed = base64.b64decode(encoded, validate=True)
    assert len(compressed) == int(manifest["compressed_bytes"])
    assert hashlib.sha256(compressed).hexdigest() == manifest["compressed_sha256"]
    raw = zlib.decompress(compressed)
    assert len(raw) == int(manifest["raw_bytes"])
    assert hashlib.sha256(raw).hexdigest() == manifest["raw_sha256"]
    return json.loads(raw.decode("utf-8"))


def records(bundle: dict) -> list[dict]:
    for key in ("questions", "records"):
        value = bundle.get(key)
        if isinstance(value, list):
            return value
    topics = bundle.get("topics")
    if isinstance(topics, list):
        out = []
        for topic in topics:
            if isinstance(topic, dict) and isinstance(topic.get("questions"), list):
                out.extend(topic["questions"])
        if out:
            return out
    raise SystemExit("canonical bundle has no recognized question collection")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", choices=tuple(PREFIX), required=True)
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    args = ap.parse_args()
    if args.start < 1 or args.end < args.start:
        raise SystemExit("invalid question range")
    selected = []
    for row in records(load_bundle(args.subject)):
        chapter = int(row.get("chapterId", row.get("chapter_number", 0)) or 0)
        qnum = int(row.get("questionNumber", row.get("question_number", 0)) or 0)
        if chapter == args.chapter and args.start <= qnum <= args.end:
            selected.append(row)
    selected.sort(key=lambda row: int(row.get("questionNumber", row.get("question_number", 0)) or 0))
    expected = list(range(args.start, args.end + 1))
    actual = [int(row.get("questionNumber", row.get("question_number", 0)) or 0) for row in selected]
    if actual != expected:
        raise SystemExit(f"non-contiguous/missing source slice: expected {expected}, got {actual}")
    print(json.dumps(selected, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
