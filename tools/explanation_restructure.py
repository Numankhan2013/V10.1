#!/usr/bin/env python3
"""Restructure PrepLadder text-bank explanations with an outside model, safely.

The PDF prints every explanation as running text, so lists, option rulings
and tables arrive as one paragraph. A model reads each explanation and returns
the same words as paragraphs, points and tables; this tool takes nothing else.

  export --bank B     write batches to data/Prepladder/B/restructure/batches/
  check  <result...>  validate model output; writes nothing
  import <result...>  validate, then merge passing questions into the overlay

The bank (pathology, pharmacology) comes from --bank or else from the result
files' names or folders (pharmacology-007.result.json); it defaults to pathology.

A result passes only when its words, read in order, are exactly the source's
words (punctuation, spacing, case of nothing; see words()). Figures must keep
their order. The builder applies the overlay and refuses entries whose source
explanation has since changed. Instructions: docs/EXPLANATION_RESTRUCTURE.md.
"""
from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from prepladder_text_bank import NO_EXPLANATION, source_hash  # noqa: E402

BANKS = ("pathology", "pharmacology", "biochemistry", "physiology")
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

def paths(bank: str) -> tuple[Path, Path]:
    """The batch folder and the overlay of a bank."""
    folder = ROOT / "data/Prepladder" / bank / "restructure"
    return folder / "batches", folder / "restructured.json"


BATCHES, OVERLAY = paths("pathology")


def bank_bodies(bank: str) -> dict[str, dict]:
    """Every question's explanation body (blocks without references) and context."""
    builder = importlib.import_module(f"build_prepladder_{bank}_bank")

    out = {}
    for q in builder.normalize(builder.load_source(), overlay=False)[0]["questions"]:
        # Earlier-edition questions keep their PDF-page explanations: nothing to format.
        if "structuredExplanation" not in q or not q["options"]:
            continue
        body = [b for b in q["structuredExplanation"]["blocks"] if b["type"] != "references"]
        if not body or body[0].get("text") == NO_EXPLANATION:
            continue
        out[q["id"]] = {"q": q, "body": body}
    return out


def export(bank: str) -> None:
    bodies = bank_bodies(bank)
    batches, _ = paths(bank)
    batches.mkdir(parents=True, exist_ok=True)
    for old in batches.glob("*.json"):
        old.unlink()
    ids = list(bodies)
    for n in range(0, len(ids), BATCH_SIZE):
        name = f"{bank}-{n // BATCH_SIZE + 1:03d}"
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
        (batches / f"{name}.json").write_text(json.dumps(batch, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"RESTRUCTURE_EXPORT_OK questions={len(ids)} batches={-(-len(ids) // BATCH_SIZE)} dir={batches.relative_to(ROOT)}")


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


def judge(bank: str, files: list[Path]) -> tuple[dict, list[str], int]:
    bodies = bank_bodies(bank)
    passed, report, unchanged = {}, [], 0
    for r in load_results(files):
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


def check(bank: str, files: list[Path], write: bool) -> None:
    passed, report, unchanged = judge(bank, files)
    for line in report:
        print("REJECTED", line)
    if write and passed:
        _, target = paths(bank)
        overlay = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
        overlay.update(passed)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(dict(sorted(overlay.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    verb = "IMPORT" if write else "CHECK"
    print(f"RESTRUCTURE_{verb}_{'OK' if not report else 'REJECTIONS'} passed={len(passed)} unchanged={unchanged} "
          f"rejected={len(report)}")
    if report:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("export", "check", "import"))
    parser.add_argument("results", nargs="*", type=Path)
    parser.add_argument("--bank", choices=BANKS)
    args = parser.parse_args()
    named = {b for path in args.results for b in BANKS if path.name.startswith(b + "-") or b in path.resolve().parts}
    if len(named) > 1:
        parser.error("result files from more than one bank; check one bank at a time")
    bank = args.bank or next(iter(named), "pathology")
    if args.command == "export":
        export(bank)
    elif not args.results:
        parser.error(f"{args.command} needs one or more result files")
    else:
        check(bank, args.results, write=args.command == "import")


if __name__ == "__main__":
    main()
