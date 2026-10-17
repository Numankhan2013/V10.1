#!/usr/bin/env python3
"""Build the PrepLadder Microbiology bank from the extracted Version X QBank.

PrepLadder's other subjects show each explanation as the original PDF page.
Microbiology arrives as a structured extraction instead (ordered text, list,
table and image blocks), so its explanations render through the same ordered
text renderer as the Marrow banks while the bank stays labelled PrepLadder.

Layout (data/Prepladder/microbiology/):
  source/prepladder_microbiology_qbank.jsonl.gz   slim copy of the extraction
  visuals/<image_id>.jpg                          figures, extraction borders trimmed
  visuals.json                                    figure inventory (hash, size, trim box)
  prepladder_microbiology_qbank.zlib.b64.partNN   built bank (hash-pinned shards)
  prepladder_microbiology_qbank_manifest.json

  python3 tools/build_prepladder_microbiology_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_microbiology_bank.py           # rebuild the shards
  python3 tools/build_prepladder_microbiology_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_microbiology_bank.py release   # copy figures into the app

The app build loads the bank with `app_record()` and releases the figures with
`release()` (tools/build_app_data.py).
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import re
import sys
import zlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/Prepladder/microbiology"
SOURCE = DATA / "source/prepladder_microbiology_qbank.jsonl.gz"
VISUALS = DATA / "visuals"
INVENTORY = DATA / "visuals.json"
PREFIX = "prepladder_microbiology_qbank"
SHARD_CHARS = 60000
SUBJECT = "Microbiology"
SOURCE_PDF = "data/Prepladder/SourcePDFs/compressed_microprep (1).pdf"
SOURCE_LABEL = "PrepLadder Version X"
ASSETS = ROOT / "app/src/main/assets"
RUNTIME = ASSETS / "prepladder_microbiology_visual_metadata.js"
EXPECTED = {"questions": 1042, "topics": 42}


def fail(message: str) -> None:
    raise SystemExit(f"PREPLADDER_MICROBIOLOGY_FAIL: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- import: slim source + trimmed figures ----------------------------------

def slim(q: dict) -> dict:
    """Keep the fields the builder reads; the extraction repeats most of them."""
    stem = q["question_stem_structured"]
    blocks = []
    for block in q["explanation_blocks"]:
        block = {k: v for k, v in block.items() if k not in ("block_type", "markdown", "items")}
        blocks.append(block)
    return {
        "id": q["id"],
        "module_index": q["module_index"],
        "module_name": q["module_name"],
        "section_category": q["section_category"],
        "is_pyq_lesson": q["is_pyq_lesson"],
        "module_total_questions_in_app": q["module_total_questions_in_app"],
        "question_number": q["question_number"],
        "question": stem["text"],
        "stem_tables": [{k: t[k] for k in ("table_id", "headers", "rows")} for t in stem.get("tables") or []],
        "options": [{k: o[k] for k in ("id", "text", "is_correct")} for o in q["options"]],
        "correct_option": q["correct_option"],
        "correct_options_list": q["correct_options_list"],
        "explanation_blocks": blocks,
        "images": [{k: i.get(k) for k in ("image_id", "location", "caption", "source_page", "table_id")} for i in q["images"]],
        "review_status": q["reviewStatus"],
        "quality_flags": q["quality_flags"],
        "pages": {k: q["provenance"].get(k) or [] for k in ("question_pages", "explanation_pages")},
    }


def import_source(master: Path, images: Path) -> None:
    sys.path.insert(0, str(ROOT / "tools"))
    from figure_trim import trim_file

    rows = [slim(json.loads(line)) for line in master.read_text(encoding="utf-8").splitlines() if line.strip()]
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0, compresslevel=9) as handle:
        handle.write("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows).encode("utf-8"))
    SOURCE.write_bytes(buffer.getvalue())
    VISUALS.mkdir(parents=True, exist_ok=True)
    trims = {}
    for q in rows:
        for image in q["images"]:
            src = images / f"{image['image_id']}.jpg"
            if not src.exists():
                fail(f"missing figure {src}")
            box = trim_file(src, VISUALS / src.name)
            if box:
                trims[image["image_id"]] = list(box)
    inventory(trims)
    print(f"PREPLADDER_MICROBIOLOGY_IMPORT_OK questions={len(rows)} figures={sum(len(q['images']) for q in rows)} trimmed={len(trims)}")


def load_source() -> list[dict]:
    if not SOURCE.exists():
        fail(f"source missing: {SOURCE.relative_to(ROOT)}")
    return [json.loads(line) for line in gzip.decompress(SOURCE.read_bytes()).decode("utf-8").splitlines() if line.strip()]


# --- text cleanup -------------------------------------------------------------

MD_IMAGE = re.compile(r"\s*!\[[^\]]*\]\([^)]*\)")
# Leftovers of the source's <img alt="..." data-*="..." src="..." /> markup. A
# leak runs from the line holding the alt text to "/>", or to the end of the
# block or cell when the extraction split the tag.
HTML_LEAK = re.compile(r'"\s*(?:data-[a-z]+|src|height|width)="')
HTML_TAIL = re.compile(r'[^\s"]*\.(?:pn\s?g|jpe?g|gif|webp)"(?:\s+[a-z-]+="[^"]*")*\s*/>')
TRUNCATED = re.compile(r"\s*(?:\.\.\.|…)\s*\(content\s+truncated\)")
WRAP_END = re.compile(r"(?:[,(/–-]|\b(?:and|or|of|the|a|an|in|to|with|for|by|on|at|from|as|is|are|than|via|into))$", re.I)


def strip_leak(text: str) -> str:
    match = HTML_LEAK.search(text)
    if not match:
        return text
    start = text.rfind("\n", 0, match.start()) + 1
    end = text.find("/>", match.end())
    return strip_leak(text[:start] + (text[end + 2:] if end >= 0 else ""))


def strip_markup(text: str) -> str:
    text = str(text or "").replace("\r", "").replace("<br>", "\n")
    text = MD_IMAGE.sub("", text)
    text = strip_leak(text)
    text = HTML_TAIL.sub("", text)
    # The extraction cut long cells short; a cell that held only an image
    # (now shown with the figures) or nothing readable becomes blank.
    text = TRUNCATED.sub(" …", text)
    if text.strip() == "…":
        text = ""
    if text.count("**") % 2:
        cut = text.rfind("**")
        text = text[:cut] + text[cut + 2:]
    return text


def wraps(prev: str, nxt: str) -> bool:
    """A PDF line wrap rather than a new line of content."""
    first = nxt[0]
    if re.match(r"(?:\d+[.)]|[ivx]+\)|[a-z]\))\s", nxt):
        return False
    return first.islower() or first in "(),;:.%/–-" or first.isdigit() or bool(WRAP_END.search(prev))


# Word counts over the whole extraction. Narrow table columns broke words
# across lines ("Chorioretinit" / "is", "hoo" / "ks"): a split is mended when
# the halves are rare and the whole word occurs elsewhere in the source.
VOCAB: Counter = Counter()
WORD = re.compile(r"[A-Za-z]+")


def count_words(rows: list[dict]) -> None:
    VOCAB.clear()
    for q in rows:
        VOCAB.update(w.lower() for w in WORD.findall(json.dumps(q, ensure_ascii=False).replace("\\n", " ")))


def mend(left: str, right: str) -> str:
    a, b = re.search(r"([A-Za-z]+)$", left), re.match(r"([a-z]+)", right)
    if a and b:
        head, tail = a.group(1).lower(), b.group(1)
        if VOCAB[head + tail] >= 2 and min(VOCAB[head], VOCAB[tail]) <= 1:
            return left + right
    return left + " " + right


def clean(text: str, keep_breaks: bool = False) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in strip_markup(text).split("\n")]
    out: list[str] = []
    for line in filter(None, lines):
        if out and (not keep_breaks or wraps(out[-1], line)):
            out[-1] = mend(out[-1], line)
        else:
            out.append(line)
    # The same split also survives inside a line ("suctoria l grooves").
    return re.sub(r"([A-Za-z]+) ([a-z]+)\b", lambda m: mend(m.group(1), m.group(2)), "\n".join(out)).strip()


OPTION_ANALYSIS = re.compile(r"^(.{1,160}?\(Options? [A-E](?:[,/ &and]+[A-E])*\))\s*:\s*(.+)$", re.S)
ANSWER_LINE = re.compile(r"^\s*(?:Correct\s+)?Answer\s*(?::|[A-E]\))", re.I)


def build_blocks(q: dict) -> tuple[list[dict], list[dict]]:
    blocks: list[dict] = []
    tables: list[dict] = []
    source = list(q["explanation_blocks"])
    # The answer line repeats what the app already marks; a leading
    # "Explanation:" heading repeats the section header.
    if source and source[0]["type"] in ("text", "heading") and ANSWER_LINE.match(source[0]["content"]):
        source.pop(0)
    if source and source[0]["type"] == "heading" and source[0]["content"].strip().rstrip(":").lower() == "explanation":
        source.pop(0)
    for block in source:
        kind = block["type"]
        if kind == "text":
            text = clean(block["content"])
            if text:
                blocks.append({"type": "paragraph", "text": text})
        elif kind == "heading":
            text = clean(block["content"]).rstrip(":").strip()
            if text:
                blocks.append({"type": "heading", "text": text})
        elif kind == "list":
            items = [{"text": clean(item["text"])} for item in block["structured_items"]]
            items = [item for item in items if item["text"]]
            if items:
                blocks.append({"type": "bullets", "ordered": False, "items": items})
        elif kind == "option_analysis":
            text = clean(block["content"])
            match = OPTION_ANALYSIS.match(text)
            blocks.append({"type": "paragraph", "text": f"**{match.group(1).strip()}:** {match.group(2).strip()}" if match else text})
        elif kind == "table":
            columns = [clean(c, keep_breaks=True) for c in block["headers"]]
            rows = [[clean(c, keep_breaks=True) for c in (list(r) + [""] * len(columns))[:len(columns)]] for r in block["rows"]]
            # A row whose cells were all images keeps only its label: drop it.
            rows = [r for r in rows if any(r[1:]) or (any(r) and len(r) == 1)]
            if not columns:
                fail(f"{q['id']}: table {block.get('table_id')} has no columns")
            if not rows:
                # A header-only table is a row that crossed a page break: it joins
                # the table before it, or else reads as text.
                if blocks and blocks[-1]["type"] == "table" and len(tables[-1]["columns"]) == len(columns):
                    tables[-1]["rows"].append(columns)
                    continue
                for cell in filter(None, columns):
                    head, *rest = cell.split("\n")
                    if rest and head.endswith(":"):
                        blocks.append({"type": "heading", "text": head.rstrip(":").strip()})
                        blocks.append({"type": "bullets", "ordered": False, "items": [{"text": t} for t in rest]})
                    else:
                        blocks.append({"type": "paragraph", "text": cell.replace("\n", " ")})
                continue
            # Titles are generic ("Table 1"); a real one is kept.
            title = clean(block.get("title") or "")
            tables.append({"table_id": block["table_id"], "title": "" if re.fullmatch(r"Table \d+", title) else title,
                           "columns": columns, "rows": rows})
            blocks.append({"type": "table", "table_id": block["table_id"]})
        elif kind == "image":
            blocks.append({"type": "figure", "figure_id": block["image_id"]})
        else:
            fail(f"{q['id']}: unknown block type {kind}")
    return blocks, tables


def plain_text(blocks: list[dict]) -> str:
    out = []
    for block in blocks:
        if block["type"] in ("paragraph", "heading"):
            out.append(block["text"])
        elif block["type"] == "bullets":
            out.append("\n".join("• " + item["text"] for item in block["items"]))
    return "\n\n".join(out)


# --- bank -----------------------------------------------------------------------

def topic_id(module: int) -> str:
    return f"microbiology-{module}"


def normalize(rows: list[dict]) -> dict:
    count_words(rows)
    topics: dict[int, dict] = {}
    questions = []
    for q in rows:
        module = int(q["module_index"])
        topic = topics.setdefault(module, {
            "id": topic_id(module), "subject": SUBJECT, "bank": "PrepLadder", "title": q["module_name"].strip(),
            "section": q["section_category"], "pyq": bool(q["is_pyq_lesson"]),
            "sourceQuestionTotal": int(q["module_total_questions_in_app"]), "numbers": [], "startPage": None,
        })
        if topic["title"] != q["module_name"].strip():
            fail(f"{q['id']}: lesson title drift")
        number = int(q["question_number"])
        topic["numbers"].append(number)
        options = q["options"]
        letters = [o["id"].strip().upper() for o in options]
        if letters != [chr(65 + i) for i in range(len(options))] or len(options) not in (4, 5):
            fail(f"{q['id']}: options must run A-D or A-E, got {letters}")
        # One record keys two options ("B, C"); the app scores one, the first.
        key = letters.index(q["correct_options_list"][0].strip().upper()) + 1
        flagged = [i for i, o in enumerate(options, 1) if o["is_correct"]]
        if key not in flagged:
            fail(f"{q['id']}: correct_option {q['correct_option']} is not flagged correct")
        stem = clean(q["question"])
        texts = [clean(o["text"]) for o in options]
        if not stem or not all(texts):
            fail(f"{q['id']}: blank stem or option")
        blocks, tables = build_blocks(q)
        image_ids = {i["image_id"] for i in q["images"]}
        for block in blocks:
            if block["type"] == "figure" and block["figure_id"] not in image_ids:
                fail(f"{q['id']}: figure block {block['figure_id']} has no image")
        pages = q["pages"]
        if topic["startPage"] is None and pages["question_pages"]:
            topic["startPage"] = pages["question_pages"][0]
        notes = list(q["quality_flags"])
        if len(flagged) > 1:
            notes.append(f"source key lists {len(flagged)} correct options; scored on {letters[key - 1]}")
        record = {
            "id": f"{topic['id']}-{number}",
            "sourceQuestionId": q["id"],
            "subject": SUBJECT,
            "bank": "PrepLadder",
            "explanationFormat": "structured",
            "chapterId": topic["id"],
            "chapter": topic["title"],
            "topic": topic["title"],
            "topicIndex": module,
            "questionNumber": number,
            "question": stem,
            "options": [{"letter": letters[i], "text": texts[i]} for i in range(len(options))],
            "correctOption": key,
            "correctAnswerText": texts[key - 1],
            "explanation": plain_text(blocks),
            "structuredExplanation": {"layout": "ordered-blocks", "blocks": blocks,
                                      "tables": tables, "figures": sorted(image_ids)},
            "provenance": {"sourceFile": SOURCE_PDF, "sourceLabel": SOURCE_LABEL,
                           "questionPages": pages["question_pages"], "explanationPages": pages["explanation_pages"]},
            "sourcePage": (pages["question_pages"] or [None])[0],
            "reviewStatus": q["review_status"],
        }
        if q["stem_tables"]:
            record["stemTables"] = [{"columns": [clean(c, keep_breaks=True) for c in t["headers"]],
                                     "rows": [[clean(c, keep_breaks=True) for c in r] for r in t["rows"]]}
                                    for t in q["stem_tables"]]
        if notes:
            record["reviewNotes"] = notes
        questions.append(record)
    out_topics = []
    for module in sorted(topics):
        topic = topics[module]
        numbers = topic.pop("numbers")
        if numbers != list(range(1, len(numbers) + 1)):
            fail(f"lesson {module}: question numbers are not contiguous from 1")
        topic["questionCount"] = len(numbers)
        topic["complete"] = len(numbers) == topic["sourceQuestionTotal"]
        out_topics.append(topic)
    if [t["id"] for t in out_topics] != [topic_id(n) for n in range(1, len(out_topics) + 1)]:
        fail("lessons are not contiguous from 1")
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        fail("duplicate question IDs")
    return {"schema_version": "prepladder-text-bank-1.0", "subject": SUBJECT, "bank": "PrepLadder",
            "explanationFormat": "structured", "topics": out_topics, "questions": questions}


def shard(record: dict) -> tuple[list[str], dict]:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    parts = [encoded[i:i + SHARD_CHARS] for i in range(0, len(encoded), SHARD_CHARS)]
    manifest = {
        "schema_version": "1.0", "subject": SUBJECT, "bank": "PrepLadder",
        "source": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": sha256(SOURCE.read_bytes()),
        "sourcePdf": SOURCE_PDF, "builder": "tools/build_prepladder_microbiology_bank.py",
        "topics": len(record["topics"]), "questions": len(record["questions"]), "parts": len(parts),
        "base64_chars": len(encoded), "compressed_sha256": sha256(compressed), "raw_sha256": sha256(raw),
        "topicCounts": {t["id"]: t["questionCount"] for t in record["topics"]},
    }
    return parts, manifest


def app_record() -> dict:
    """The hash-verified bank, as embedded in MARROW_DATA.records."""
    manifest = json.loads((DATA / f"{PREFIX}_manifest.json").read_text(encoding="utf-8"))
    parts = sorted(DATA.glob(f"{PREFIX}.zlib.b64.part*"))
    if len(parts) != manifest["parts"]:
        fail("shard count mismatch")
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    compressed = base64.b64decode(encoded, validate=True)
    if len(encoded) != manifest["base64_chars"] or sha256(compressed) != manifest["compressed_sha256"]:
        fail("shards do not match the manifest")
    raw = zlib.decompress(compressed)
    if sha256(raw) != manifest["raw_sha256"]:
        fail("raw SHA-256 mismatch")
    record = json.loads(raw)
    counts = {"questions": len(record["questions"]), "topics": len(record["topics"])}
    if counts != EXPECTED or record["bank"] != "PrepLadder" or record["subject"] != SUBJECT:
        fail(f"unexpected bank identity or counts: {counts}")
    return record


# --- figures ---------------------------------------------------------------------

def jpeg_size(data: bytes) -> tuple[int, int]:
    sys.path.insert(0, str(ROOT / "tools"))
    from microbiology_visuals import jpeg_size as size
    return size(data)


def alt_text(image: dict, n: int, role: str) -> str:
    caption = re.sub(r"^\s*Description:\s*-\s*", "", clean(image.get("caption") or "")).strip()
    if len(caption) < 3 or re.fullmatch(r"(?:Question|Image|Figure)\s*\d+.*", caption, re.I):
        return f"{'Question' if role == 'question' else 'Explanation'} figure {n}"
    return caption


def inventory(trims: dict | None = None) -> None:
    previous = {}
    if INVENTORY.exists():
        previous = {f["imageId"]: f for f in json.loads(INVENTORY.read_text(encoding="utf-8"))["figures"]}
    figures = []
    for q in load_source():
        app_id = f"{topic_id(int(q['module_index']))}-{int(q['question_number'])}"
        order: dict[str, int] = {}
        for image in q["images"]:
            role = "question" if image["location"].startswith("question_stem") else "explanation"
            order[role] = order.get(role, 0) + 1
            path = VISUALS / f"{image['image_id']}.jpg"
            data = path.read_bytes()
            width, height = jpeg_size(data)
            trim = (trims or {}).get(image["image_id"]) if trims is not None else previous.get(image["image_id"], {}).get("trimBox")
            figures.append({
                "imageId": image["image_id"], "questionId": app_id, "role": role, "order": order[role],
                "alt": alt_text(image, order[role], role), "file": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(data), "width": width, "height": height, "sourcePage": image.get("source_page"),
                "trimBox": trim,
            })
    INVENTORY.write_text(json.dumps({
        "schemaVersion": 1, "subject": SUBJECT, "bank": "PrepLadder", "sourcePdf": SOURCE_PDF,
        "note": "trimBox is the crop tools/figure_trim.py took from the extracted figure (null: untouched).",
        "figures": figures,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def release() -> None:
    value = json.loads(INVENTORY.read_text(encoding="utf-8"))
    runtime: dict[str, list[dict]] = {}
    for figure in value["figures"]:
        data = (ROOT / figure["file"]).read_bytes()
        if sha256(data) != figure["sha256"]:
            fail(f"figure changed since inventory: {figure['imageId']}")
        rel = f"marrow_visuals/{figure['sha256']}.jpg"
        target = ASSETS / rel
        if not target.exists():
            target.write_bytes(data)
        runtime.setdefault(figure["questionId"], []).append({
            "id": f"prepladder-{figure['imageId']}", "role": figure["role"], "order": figure["order"],
            "src": rel, "alt": figure["alt"], "status": "PASS", "width": figure["width"], "height": figure["height"],
        })
    payload = json.dumps(runtime, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")
    RUNTIME.write_text(
        "/* PrepLadder Microbiology figures (generated by tools/build_prepladder_microbiology_bank.py). */\n"
        f"window.MARROW_VISUALS=Object.assign(window.MARROW_VISUALS||{{}},{payload});\n",
        encoding="utf-8",
    )
    print(f"PREPLADDER_MICROBIOLOGY_VISUALS_OK questions={len(runtime)} figures={len(value['figures'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", choices=["build", "import", "release"], default="build")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.command == "import":
        import_source(Path(args.paths[0]), Path(args.paths[1]))
    elif args.command == "release":
        release()
        return
    record = normalize(load_source())
    parts, manifest = shard(record)
    manifest_path = DATA / f"{PREFIX}_manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    existing = sorted(DATA.glob(f"{PREFIX}.zlib.b64.part*"))
    if args.check:
        current = [p.read_text(encoding="utf-8").strip() for p in existing]
        if current != parts or not manifest_path.exists() or manifest_path.read_text(encoding="utf-8") != manifest_text:
            fail("shards/manifest are stale; run tools/build_prepladder_microbiology_bank.py")
    else:
        for path in existing:
            path.unlink()
        for index, part in enumerate(parts):
            (DATA / f"{PREFIX}.zlib.b64.part{index:02d}").write_text(part + "\n", encoding="utf-8")
        manifest_path.write_text(manifest_text, encoding="utf-8")
    print(f"PREPLADDER_MICROBIOLOGY_BANK_OK questions={manifest['questions']} topics={manifest['topics']} parts={manifest['parts']}")


if __name__ == "__main__":
    main()
