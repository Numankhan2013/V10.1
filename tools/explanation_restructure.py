#!/usr/bin/env python3
"""Restructure PrepLadder Pathology explanations with an outside model, safely.

The PDF prints every explanation as running text, so lists, option rulings
and tables arrive as one paragraph. A model reads each explanation and returns
the same words as paragraphs, points and tables; this tool takes nothing else.

  export              write batches to data/Prepladder/pathology/restructure/batches/
  check  <result...>  validate model output; writes nothing
  import <result...>  validate, then merge passing questions into the overlay

A result passes only when its words, read in order, are exactly the source's
words (punctuation, spacing, case of nothing; see words()). Figures must keep
their order. The builder applies the overlay and refuses entries whose source
explanation has since changed. Instructions: docs/EXPLANATION_RESTRUCTURE.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_prepladder_pathology_bank import source_hash  # noqa: E402

DIR = ROOT / "data/Prepladder/pathology/restructure"
BATCHES = DIR / "batches"
OVERLAY = DIR / "restructured.json"
BATCH_SIZE = 20
INSTRUCTIONS = "docs/EXPLANATION_RESTRUCTURE.md"

WORD = re.compile(r"[^\W_]+")
KINDS = {"paragraph", "heading", "bullets", "table", "figure"}


def words(text: str) -> list[str]:
    """Letters and digits only: punctuation, '**' and spacing may change."""
    return WORD.findall(str(text))


def body_words(blocks: list[dict]) -> tuple[list[str], list[str]]:
    """The words and figure ids of a block list, in reading order."""
    out, figures = [], []

    def items(rows):
        for item in rows or []:
            out.extend(words(item.get("text", "")))
            items(item.get("items"))

    for b in blocks:
        kind = b.get("type")
        if kind in ("paragraph", "heading"):
            out.extend(words(b.get("text", "")))
        elif kind == "bullets":
            items(b.get("items"))
        elif kind == "table":
            out.extend(words(b.get("title", "")))
            for cell in b.get("columns", []):
                out.extend(words(cell))
            for row in b.get("rows", []):
                for cell in row:
                    out.extend(words(cell))
        elif kind == "figure":
            figures.append(b.get("figure_id"))
    return out, figures


def problems(source: list[dict], result: list[dict]) -> list[str]:
    """Why a result is rejected; empty when it passes."""
    errors = []
    if not isinstance(result, list) or not result:
        return ["blocks must be a non-empty list"]
    for i, b in enumerate(result):
        if not isinstance(b, dict) or b.get("type") not in KINDS:
            errors.append(f"block {i}: type must be one of {sorted(KINDS)}")
            continue
        kind = b["type"]
        if kind in ("paragraph", "heading") and not str(b.get("text", "")).strip():
            errors.append(f"block {i}: empty {kind}")
        if kind == "heading" and len(words(b.get("text", ""))) > 8:
            errors.append(f"block {i}: a heading is a short label (8 words at most)")
        if kind == "bullets":
            rows = b.get("items")
            if not isinstance(rows, list) or len(rows) < 2:
                errors.append(f"block {i}: a list needs at least two items")
            elif not all(isinstance(r, dict) and str(r.get("text", "")).strip() for r in rows):
                errors.append(f"block {i}: every item needs text")
            elif any(not all(isinstance(c, dict) and str(c.get("text", "")).strip() for c in r.get("items") or [])
                     or any(c.get("items") for c in r.get("items") or []) for r in rows):
                errors.append(f"block {i}: sub-items need text and go one level deep only")
        if kind == "table":
            cols, rows = b.get("columns"), b.get("rows")
            if not isinstance(cols, list) or len(cols) < 2 or not isinstance(rows, list) or not rows:
                errors.append(f"block {i}: a table needs 2+ columns and 1+ rows")
            elif any(not isinstance(r, list) or len(r) != len(cols) for r in rows):
                errors.append(f"block {i}: every row needs exactly {len(cols)} cells (use \"\" for an empty cell)")
    if errors:
        return errors
    want, want_figs = body_words(source)
    got, got_figs = body_words(result)
    if got_figs != want_figs:
        errors.append(f"figures must stay, in order: expected {want_figs}, got {got_figs}")
    if got != want:
        at = next((i for i, (a, b) in enumerate(zip(want, got)) if a != b), min(len(want), len(got)))
        errors.append(f"words differ at word {at + 1}: source has {' '.join(want[at:at + 6])!r}, "
                      f"result has {' '.join(got[at:at + 6])!r} (source {len(want)} words, result {len(got)})")
    return errors


# --- source ---------------------------------------------------------------------

def bank_bodies() -> dict[str, dict]:
    """Every question's explanation body (blocks without references) and context."""
    from build_prepladder_pathology_bank import NO_EXPLANATION, load_source, normalize

    out = {}
    for q in normalize(load_source(), overlay=False)[0]["questions"]:
        body = [b for b in q["structuredExplanation"]["blocks"] if b["type"] != "references"]
        if not body or body[0].get("text") == NO_EXPLANATION:
            continue
        out[q["id"]] = {"q": q, "body": body}
    return out


def export() -> None:
    bodies = bank_bodies()
    BATCHES.mkdir(parents=True, exist_ok=True)
    for old in BATCHES.glob("*.json"):
        old.unlink()
    ids = list(bodies)
    for n in range(0, len(ids), BATCH_SIZE):
        name = f"pathology-{n // BATCH_SIZE + 1:03d}"
        questions = []
        for qid in ids[n:n + BATCH_SIZE]:
            q, body = bodies[qid]["q"], bodies[qid]["body"]
            questions.append({
                "id": qid,
                "question": q["question"],
                "options": {o["letter"]: o["text"] for o in q["options"]},
                "answer": q["options"][q["correctOption"] - 1]["letter"],
                "explanation": body,
            })
        batch = {"batch": name, "instructions": INSTRUCTIONS,
                 "reply_with": {"batch": name, "results": [{"id": "<question id>", "blocks": ["..."]},
                                                           {"id": "<question id>", "unchanged": True}]},
                 "questions": questions}
        (BATCHES / f"{name}.json").write_text(json.dumps(batch, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"RESTRUCTURE_EXPORT_OK questions={len(ids)} batches={-(-len(ids) // BATCH_SIZE)} dir={BATCHES.relative_to(ROOT)}")


def load_results(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        text = path.read_text(encoding="utf-8").strip()
        # Chat replies often arrive wrapped in a ```json fence.
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise SystemExit(f"{path}: not valid JSON ({error})")
        results = data.get("results") if isinstance(data, dict) else data
        if not isinstance(results, list):
            raise SystemExit(f"{path}: expected {{\"batch\": ..., \"results\": [...]}}")
        rows.extend({**r, "_file": path.name} for r in results)
    return rows


def judge(paths: list[Path]) -> tuple[dict, list[str], int]:
    bodies = bank_bodies()
    passed, report, unchanged = {}, [], 0
    for r in load_results(paths):
        qid = r.get("id")
        if qid not in bodies:
            report.append(f"{r['_file']}: {qid!r} is not a question in the batches")
            continue
        if r.get("unchanged") is True:
            unchanged += 1
            continue
        errors = problems(bodies[qid]["body"], r.get("blocks"))
        if errors:
            report.append(f"{r['_file']}: {qid}: " + "; ".join(errors))
        else:
            passed[qid] = {"sourceHash": source_hash(bodies[qid]["body"]), "blocks": r["blocks"]}
    return passed, report, unchanged


def check(paths: list[Path], write: bool) -> None:
    passed, report, unchanged = judge(paths)
    for line in report:
        print("REJECTED", line)
    if write and passed:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8")) if OVERLAY.exists() else {}
        overlay.update(passed)
        OVERLAY.parent.mkdir(parents=True, exist_ok=True)
        OVERLAY.write_text(json.dumps(dict(sorted(overlay.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    verb = "IMPORT" if write else "CHECK"
    print(f"RESTRUCTURE_{verb}_{'OK' if not report else 'REJECTIONS'} passed={len(passed)} unchanged={unchanged} "
          f"rejected={len(report)}")
    if report:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("export", "check", "import"))
    parser.add_argument("results", nargs="*", type=Path)
    args = parser.parse_args()
    if args.command == "export":
        export()
    elif not args.results:
        parser.error(f"{args.command} needs one or more result files")
    else:
        check(args.results, write=args.command == "import")


if __name__ == "__main__":
    main()
