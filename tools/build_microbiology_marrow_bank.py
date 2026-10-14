#!/usr/bin/env python3
"""Normalize the Microbiology Marrow QBank JSONL into the shared Marrow bank schema.

Source of truth: the extracted JSONL parts under data/marrow/microbiology/source/
(cross-checked against data/marrow/source_pdfs/Microbiology Marrow Qbank.pdf).
The raw JSONL is never edited. This script turns it into the same
`marrow-bank-1.0` record the other Marrow subjects use (topics + questions with
namespaced IDs, four A-D options, a 1-based correct option, structured
explanation) and writes the hash-pinned shards that tools/marrow_bank_data.py
loads, exactly like the Anatomy/Biochemistry/Physiology banks.

  python3 tools/build_microbiology_marrow_bank.py           # rebuild shards + manifest
  python3 tools/build_microbiology_marrow_bank.py --check   # fail if shards are stale

Display hygiene (recorded per question under `displayHygiene`, raw untouched):
  * extractor annotations such as "(as visible in source screenshot ...)" are
    removed from table headers;
  * bracketed completions of screenshot-clipped words ("permeabili[ty]") are
    shown as plain words ("permeability").
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/marrow"
SOURCE_DIR = DATA / "microbiology/source"
PREFIX = "microbiology_marrow_qbank"
SUBJECT = "Microbiology"
SOURCE_PDF = "Microbiology Marrow Qbank.pdf"
SOURCE_LABEL = "Marrow QBank v3.0"
SHARD_CHARS = 60000

ANNOTATION = re.compile(r"\s*\((?:as visible in source screenshot[^)]*|[^)]*bracketed completions[^)]*)\)", re.I)
BRACKET_COMPLETION = re.compile(r"\[([A-Za-z][A-Za-z0-9 \-]{0,28})\]")
IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
PEARL = re.compile(r"^\*\*MARROW Pearl #(\d+)\s*•\s*([^:*]+?):\s*(.+?)\*\*\s*$")
# Exact source-checked corrections of extraction typos: {MCQ ID: [(wrong, right, evidence)]}.
# Each `wrong` must occur in the raw JSONL exactly as written or the build fails.
SOURCE_CORRECTIONS = {
    "MA1527": [("Pemphighus neonatorum", "Pemphigus neonatorum",
                "source PDF page 24 reads 'Milder form - Pemphigus neonatorum'")],
}
BULLET = re.compile(r"^(\s*)(?:[*-]|(\d+)[.)])\s+(.*)$")


def fail(message: str) -> None:
    raise SystemExit(f"MICROBIOLOGY_BANK_ERROR: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_parts() -> list[Path]:
    parts = sorted(SOURCE_DIR.glob("Microbiology_Marrow_Qbank_*.jsonl"))
    if not parts:
        fail(f"no source JSONL under {SOURCE_DIR.relative_to(ROOT)}")
    return parts


def load_source() -> tuple[list[dict], list[dict]]:
    rows, files = [], []
    for path in source_parts():
        raw = path.read_bytes()
        part_rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
        files.append({"file": path.name, "sha256": sha256(raw), "questions": len(part_rows)})
        rows.extend(part_rows)
    return rows, files


class Hygiene:
    def __init__(self) -> None:
        self.notes: set[str] = set()

    def clean(self, text: str) -> str:
        value = str(text or "")
        stripped = ANNOTATION.sub("", value)
        if stripped != value:
            self.notes.add("removed extractor annotation from table text")
        merged = BRACKET_COMPLETION.sub(r"\1", stripped)
        if merged != stripped:
            self.notes.add("merged bracketed completions of screenshot-clipped words")
        return merged


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [cell.strip() for cell in body.split("|")]


def cell_text(cell: str, hygiene: Hygiene) -> str:
    return hygiene.clean(re.sub(r"\s*<br\s*/?>\s*", "\n", cell)).strip()


def parse_markdown(q: dict, hygiene: Hygiene) -> tuple[list[dict], list[dict]]:
    """Markdown explanation -> ordered blocks + tables (in source order)."""
    markdown = str(q.get("explanation_markdown") or "")
    for wrong, right, _evidence in SOURCE_CORRECTIONS.get(q["id"], []):
        if markdown.count(wrong) != 1:
            fail(f"{q['id']}: source correction {wrong!r} no longer matches the raw explanation")
        markdown = markdown.replace(wrong, right)
        hygiene.notes.add(f"source-checked correction: {wrong} -> {right}")
    lines = markdown.replace("\r", "").split("\n")
    source_tables = list(q.get("tables") or [])
    images = {img["image_id"]: img for img in q.get("images") or []}
    image_by_path = {Path(str(img.get("asset_path") or "")).stem: img for img in images.values()}
    pearls = {str(p.get("pearl_id")): p for p in q.get("pearls") or []}
    blocks: list[dict] = []
    tables: list[dict] = []
    current_pearl: str | None = None
    i = 0

    def add_paragraph(text: str) -> None:
        text = text.strip()
        if text:
            blocks.append({"type": "paragraph", "text": text})

    para: list[str] = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            add_paragraph(" ".join(para)); para = []
            i += 1
            continue
        pearl = PEARL.match(stripped)
        image = IMAGE.match(stripped)
        bullet = BULLET.match(line)
        if pearl:
            add_paragraph(" ".join(para)); para = []
            pearl_id = f"Pearl #{pearl.group(1)}"
            meta = pearls.get(pearl_id, {})
            current_pearl = pearl_id
            blocks.append({"type": "pearl", "pearl_id": pearl_id,
                           "category": str(meta.get("category") or pearl.group(2)).strip(),
                           "title": str(meta.get("title") or pearl.group(3)).strip()})
            i += 1
            continue
        if image:
            add_paragraph(" ".join(para)); para = []
            stem = Path(image.group(2)).stem
            meta = images.get(stem) or image_by_path.get(stem)
            if not meta:
                fail(f"{q['id']}: markdown image {stem} has no image metadata")
            blocks.append({"type": "figure", "figure_id": meta["image_id"], "caption": image.group(1).strip()})
            i += 1
            continue
        if stripped.startswith("|"):
            add_paragraph(" ".join(para)); para = []
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            if len(rows) < 2 or not all(re.fullmatch(r":?-{3,}:?", c) for c in rows[1]):
                fail(f"{q['id']}: malformed markdown table")
            header, body = rows[0], rows[2:]
            if not source_tables:
                fail(f"{q['id']}: markdown table without table metadata")
            meta = source_tables.pop(0)
            if len(meta.get("headers") or []) != len(header) or len(meta.get("rows") or []) != len(body):
                fail(f"{q['id']}: markdown table {meta.get('table_id')} shape differs from table metadata")
            columns = [cell_text(c, hygiene) for c in header]
            table_rows = [[cell_text(c, hygiene) for c in (row + [""] * len(columns))[:len(columns)]] for row in body]
            table = {"table_id": meta["table_id"], "title": hygiene.clean(meta.get("title") or ""),
                     "columns": columns, "rows": table_rows}
            if meta.get("in_pearl"):
                table["pearl_id"] = meta.get("pearl_id")
            tables.append(table)
            blocks.append({"type": "table", "table_id": meta["table_id"]})
            continue
        if stripped.startswith(">"):
            add_paragraph(" ".join(para)); para = []
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            text = " ".join(x for x in quote if x)
            text = re.sub(r"^\*\*Note:\*\*\s*", "", text)
            blocks.append({"type": "note", "text": text})
            continue
        if stripped.startswith("Ref:") or stripped.startswith("Ref "):
            add_paragraph(" ".join(para)); para = []
            blocks.append({"type": "reference", "text": stripped})
            i += 1
            continue
        if bullet:
            add_paragraph(" ".join(para)); para = []
            ordered = bool(bullet.group(2))
            items: list[dict] = []
            while i < len(lines):
                m = BULLET.match(lines[i])
                if not m:
                    # continuation line of the previous item
                    if lines[i].strip() and lines[i].startswith("  ") and items:
                        target = items[-1]["items"][-1] if items[-1]["items"] else items[-1]
                        target["text"] += " " + lines[i].strip()
                        i += 1
                        continue
                    break
                depth = len(m.group(1).replace("\t", "  ")) // 2
                entry = {"text": hygiene.clean(m.group(3).strip()), "items": []}
                if depth == 0 or not items:
                    items.append(entry)
                else:
                    items[-1]["items"].append(entry)
                i += 1
            for entry in items:
                if not entry["items"]:
                    del entry["items"]
                else:
                    for child in entry["items"]:
                        child.pop("items", None)
            blocks.append({"type": "bullets", "ordered": ordered, "items": items})
            continue
        para.append(hygiene.clean(stripped))
        i += 1
    add_paragraph(" ".join(para))
    if source_tables:
        fail(f"{q['id']}: {len(source_tables)} table(s) in metadata missing from markdown")
    figure_ids = [b["figure_id"] for b in blocks if b["type"] == "figure"]
    explanation_images = sorted(k for k, v in images.items() if v.get("location") != "question_stem")
    if sorted(figure_ids) != explanation_images:
        fail(f"{q['id']}: figure blocks {figure_ids} differ from explanation image metadata {explanation_images}")
    return blocks, tables


def plain_text(blocks: list[dict], tables: dict[str, dict]) -> str:
    out: list[str] = []
    for block in blocks:
        kind = block["type"]
        if kind == "paragraph" or kind == "note":
            out.append(block["text"])
        elif kind == "pearl":
            out.append(f"Marrow Pearl: {block['title']}")
        elif kind == "bullets":
            lines = []
            for n, item in enumerate(block["items"], 1):
                lines.append((f"{n}. " if block["ordered"] else "• ") + item["text"])
                lines.extend("• " + child["text"] for child in item.get("items", []))
            out.append("\n".join(lines))
        elif kind == "table":
            title = tables[block["table_id"]].get("title")
            if title:
                out.append(title)
    return "\n\n".join(x for x in out if x.strip())


def normalize(rows: list[dict]) -> dict:
    modules: dict[int, dict] = {}
    questions: list[dict] = []
    seen_mcq: set[str] = set()
    for q in rows:
        mcq = str(q.get("mcq_id") or q.get("id") or "").strip()
        if not mcq or mcq in seen_mcq:
            fail(f"blank or duplicate MCQ ID {mcq!r}")
        seen_mcq.add(mcq)
        module_index = int(q["module_index"])
        module = modules.setdefault(module_index, {
            "id": str(module_index), "subject": SUBJECT, "bank": "Marrow",
            "title": str(q["module_name"]).strip(), "moduleId": q["module_id"],
            "sourceQuestionTotal": int(q["module_total_questions_in_app"]), "questionNumbers": [],
            "startPage": None,
        })
        if module["title"] != str(q["module_name"]).strip() or module["moduleId"] != q["module_id"]:
            fail(f"{mcq}: module identity drift")
        number = int(q["question_number"])
        module["questionNumbers"].append(number)
        options = q.get("options") or []
        letters = [str(o.get("id", "")).strip().upper() for o in options]
        if letters != ["A", "B", "C", "D"]:
            fail(f"{mcq}: options must be exactly A-D, got {letters}")
        correct_flags = [i for i, o in enumerate(options, 1) if o.get("is_correct") is True]
        key = "ABCD".index(str(q.get("correct_option", "")).strip().upper()) + 1
        if correct_flags != [key]:
            fail(f"{mcq}: correct_option {q.get('correct_option')} disagrees with is_correct flags {correct_flags}")
        if str(q.get("correct_answer_text", "")).strip() != str(options[key - 1].get("text", "")).strip():
            fail(f"{mcq}: correct_answer_text differs from the keyed option text")
        stem = str(q.get("question_stem") or "").strip()
        if not stem or any(not str(o.get("text", "")).strip() for o in options):
            fail(f"{mcq}: blank stem or option")
        hygiene = Hygiene()
        blocks, tables = parse_markdown(q, hygiene)
        table_map = {t["table_id"]: t for t in tables}
        pages = [int(p) for p in (q.get("provenance") or {}).get("source_pages") or []]
        if not pages:
            fail(f"{mcq}: no source pages")
        if module["startPage"] is None:
            module["startPage"] = pages[0]
        figures = []
        for img in q.get("images") or []:
            figures.append({k: img.get(k) for k in ("image_id", "location", "type", "caption", "source_page", "bounding_box", "in_pearl", "pearl_id")})
        flags = list((q.get("provenance") or {}).get("quality_flags") or [])
        qid = f"MICRO_CH{module_index:02d}_Q{number:03d}"
        record = {
            "id": f"marrow__{qid}",
            "sourceQuestionId": qid,
            "mcqId": mcq,
            "subject": SUBJECT,
            "bank": "Marrow",
            "chapterId": str(module_index),
            "chapter": module["title"],
            "questionNumber": number,
            "questionType": "single_best_answer",
            "question": stem,
            "options": [{"letter": letters[i], "text": str(o["text"]).strip()} for i, o in enumerate(options)],
            "correctOption": key,
            "correctAnswerText": str(options[key - 1]["text"]).strip(),
            "keyTakeaway": str(q.get("answer_summary") or "").strip(),
            "explanation": plain_text(blocks, table_map),
            "structuredExplanation": {
                "layout": "ordered-blocks",
                "text": plain_text(blocks, table_map),
                "blocks": blocks,
                "tables": tables,
                "figures": figures,
            },
            "sourceStats": {
                "peerAccuracyPercent": q.get("peer_accuracy_percentage"),
                "optionPollPercent": {letters[i]: o.get("poll_percentage") for i, o in enumerate(options)},
            },
            "references": q.get("references") or [],
            "provenance": {
                "sourceFile": SOURCE_PDF,
                "sourceLabel": SOURCE_LABEL,
                "extractedFrom": (q.get("provenance") or {}).get("source_pdf"),
                "questionPages": pages[:1],
                "explanationPages": pages,
                "qbankVersion": (q.get("source_attempt_metadata") or {}).get("qbank_version_header"),
            },
            "sourcePage": pages[0],
            "reviewStatus": "pass_with_source_note" if flags else "pass",
            "imageDependent": int(q.get("stem_image_count") or 0) > 0,
        }
        if flags:
            record["reviewNotes"] = flags
        if q.get("callout_notes"):
            record["calloutNotes"] = q["callout_notes"]
        if hygiene.notes:
            record["displayHygiene"] = sorted(hygiene.notes)
        if len(record["keyTakeaway"]) < 24:
            record.pop("keyTakeaway")
        questions.append(record)

    topics = []
    for index in sorted(modules):
        module = modules[index]
        numbers = module.pop("questionNumbers")
        if numbers != list(range(1, len(numbers) + 1)):
            fail(f"module {index}: question numbers are not contiguous from 1: {numbers}")
        if len(numbers) > module["sourceQuestionTotal"]:
            fail(f"module {index}: more questions than the source module total")
        module["questionCount"] = len(numbers)
        module["complete"] = len(numbers) == module["sourceQuestionTotal"]
        topics.append(module)
    if [t["id"] for t in topics] != [str(n) for n in range(1, len(topics) + 1)]:
        fail("modules are not contiguous from 1")
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        fail("duplicate namespaced question IDs")
    return {
        "schema_version": "marrow-bank-1.0",
        "subject": SUBJECT,
        "bank": "Marrow",
        "scope": f"modules_001_{len(topics):03d}",
        "stats": {"questions": len(questions), "topics": len(topics),
                  "completeTopics": sum(t["complete"] for t in topics)},
        "topics": topics,
        "questions": questions,
    }


def shard(record: dict, files: list[dict]) -> tuple[list[str], dict]:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    parts = [encoded[i:i + SHARD_CHARS] for i in range(0, len(encoded), SHARD_CHARS)]
    manifest = {
        "schema_version": "1.0",
        "subject": SUBJECT,
        "bank": "Marrow",
        "scope": record["scope"],
        "sourcePdf": f"data/marrow/source_pdfs/{SOURCE_PDF}",
        "sourceJsonl": files,
        "builder": "tools/build_microbiology_marrow_bank.py",
        "topics": len(record["topics"]),
        "questions": len(record["questions"]),
        "parts": len(parts),
        "base64_chars": len(encoded),
        "compressed_bytes": len(compressed),
        "compressed_sha256": sha256(compressed),
        "raw_bytes": len(raw),
        "raw_sha256": sha256(raw),
        "topicCounts": {t["id"]: t["questionCount"] for t in record["topics"]},
        "incompleteTopics": {t["id"]: f"{t['questionCount']}/{t['sourceQuestionTotal']}" for t in record["topics"] if not t["complete"]},
    }
    return parts, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows, files = load_source()
    record = normalize(rows)
    parts, manifest = shard(record, files)
    manifest_path = DATA / f"{PREFIX}_manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    existing = sorted(DATA.glob(f"{PREFIX}.zlib.b64.part*"))
    if args.check:
        current = [p.read_text(encoding="utf-8").strip() for p in existing]
        if current != parts or not manifest_path.exists() or manifest_path.read_text(encoding="utf-8") != manifest_text:
            fail("Microbiology shards/manifest are stale; run tools/build_microbiology_marrow_bank.py")
    else:
        for path in existing:
            path.unlink()
        for index, part in enumerate(parts):
            (DATA / f"{PREFIX}.zlib.b64.part{index:02d}").write_text(part + "\n", encoding="utf-8")
        manifest_path.write_text(manifest_text, encoding="utf-8")
    print(f"MICROBIOLOGY_BANK_OK questions={manifest['questions']} topics={manifest['topics']} parts={manifest['parts']} incomplete={manifest['incompleteTopics']}")


if __name__ == "__main__":
    main()
