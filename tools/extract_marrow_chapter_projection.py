#!/usr/bin/env python3
"""Extract one chapter from an immutable canonical Marrow sharded bundle.

This is a read-only automation utility. It never rewrites source bundles. It exists
so explanation workers can resolve exact source ownership from the complete corpus
without falling back to stale Phase-A audit projections.
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
SUBJECT_BUNDLES = {
    "Anatomy": "data/marrow/anatomy_ch001_063.zlib.b64.part*",
    "Biochemistry": "data/marrow/biochemistry_ch001_028.zlib.b64.part*",
    "Physiology": "data/marrow/physiology_ch001_043.zlib.b64.part*",
}


def load_bundle(pattern: str):
    paths = sorted(Path(p) for p in glob.glob(str(ROOT / pattern)))
    if not paths:
        raise SystemExit(f"No bundle shards matched {pattern}")
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in paths)
    raw = zlib.decompress(base64.b64decode(encoded))
    return json.loads(raw.decode("utf-8"))


def records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("questions", "records", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise SystemExit("Unsupported canonical bundle JSON shape")


def chapter_of(q):
    for key in ("chapterId", "chapter_id", "chapter"):
        if key in q and q[key] is not None:
            value = q[key]
            if isinstance(value, dict):
                value = value.get("id") or value.get("number")
            try:
                return int(str(value).strip())
            except (TypeError, ValueError):
                pass
    qid = str(q.get("id", ""))
    marker = "_CH"
    if marker in qid:
        tail = qid.split(marker, 1)[1]
        digits = "".join(c for c in tail.split("_", 1)[0] if c.isdigit())
        if digits:
            return int(digits)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", choices=SUBJECT_BUNDLES, required=True)
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    source = records(load_bundle(SUBJECT_BUNDLES[args.subject]))
    selected = [q for q in source if chapter_of(q) == args.chapter]
    if not selected:
        raise SystemExit(f"No {args.subject} chapter {args.chapter} records found")

    out = {
        "subject": args.subject,
        "chapter": args.chapter,
        "count": len(selected),
        "sourceBundle": SUBJECT_BUNDLES[args.subject],
        "questions": selected,
    }
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
