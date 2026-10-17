#!/usr/bin/env python3
"""Build the PrepLadder Pathology bank from its structured extraction.

Pathology arrives like the PrepLadder Microbiology November 2025 edition: a
structured extraction (text, option analysis and image blocks) of the
November 2025 QBank PDFs, whose explanations were printed as flat text. The
text cleanup and block rules are Microbiology's
(tools/build_prepladder_microbiology_bank.py); this file adds the Pathology
layout. Explanations render through the Marrow ordered-block renderer while
the bank stays labelled PrepLadder.

Layout (data/Prepladder/pathology/):
  source/prepladder_pathology_qbank.jsonl.gz   slim extraction
  visuals/<image_id>.jpg                       figures, extraction borders trimmed
  visuals.json                                 figure inventory (hash, size, trim box)
  prepladder_pathology_qbank.zlib.b64.partNN   built bank (hash-pinned shards)
  prepladder_pathology_qbank_manifest.json

  python3 tools/build_prepladder_pathology_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_pathology_bank.py           # rebuild the shards
  python3 tools/build_prepladder_pathology_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_pathology_bank.py release   # copy figures into the app

The app build loads the bank with `app_record()` and releases the figures with
`release()` (tools/build_app_data.py).
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_prepladder_microbiology_bank as micro  # noqa: E402
from prepladder_microbiology_edition import fix_record  # noqa: E402

DATA = ROOT / "data/Prepladder/pathology"
SOURCE = DATA / "source/prepladder_pathology_qbank.jsonl.gz"
VISUALS = DATA / "visuals"
INVENTORY = DATA / "visuals.json"
PREFIX = "prepladder_pathology_qbank"
SUBJECT = "Pathology"
SOURCE_LABEL = "PrepLadder November 2025 edition"
SOURCE_PDFS = ", ".join(f"pathoprep11-{r}.pdf" for r in (
    "1-300", "301-600", "601-900", "901-1200", "1201-1500", "1501-1800", "1801-2100", "2101-2400", "2401-2889"))
ASSETS = ROOT / "app/src/main/assets"
RUNTIME = ASSETS / "prepladder_pathology_visual_metadata.js"
EXPECTED = {"questions": 1459, "topics": 90}

# The extraction title-cases every word ("Cml And Cll", "Hodgkin'S").
ACRONYMS = {"er": "ER", "rhd": "RHD", "git": "GIT", "ibd": "IBD", "cns": "CNS", "cml": "CML", "cll": "CLL",
            "wbc": "WBC", "all": "ALL", "aml": "AML", "i": "I", "ii": "II"}
SMALL = {"and", "of", "to", "in", "the", "with", "for", "or"}


# 17 explanations survive only as the tail of a lost sentence ("of the correct
# answer.", "for Assertion."): the extraction lost the text before it. The
# fragment goes; the question says so instead of showing it.
FRAGMENT = re.compile(r"^[a-z][^.]{0,40}\.$")
NO_EXPLANATION = "The source PDF prints no explanation for this question."


# The extraction turned "&source=" in reference URLs into "&source;=" (the
# PDF also wraps URLs with spaces, so the fix cannot look for whole URLs);
# ";=" and ";_" never occur in prose.
ENTITY_LEAK = re.compile(r"(?<=[A-Za-z]);(?=[=_])")


def fix_urls(text: str) -> str:
    return ENTITY_LEAK.sub("", text)


def fail(message: str) -> None:
    raise SystemExit(f"PREPLADDER_PATHOLOGY_FAIL: {message}")


def lesson_title(title: str) -> str:
    def word(m: re.Match) -> str:
        w = m.group(0)
        low = w.lower()
        if low in ACRONYMS:
            return ACRONYMS[low]
        if m.start() and low in SMALL:
            return low
        return w
    title = re.sub(r"[A-Za-z]+", word, title.strip())
    return re.sub(r"'S\b", "'s", title)


# --- import -----------------------------------------------------------------------

def import_source(master: Path, images: Path) -> None:
    rows = [micro.slim(json.loads(line)) for line in master.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row, line in zip(rows, filter(str.strip, master.read_text(encoding="utf-8").splitlines())):
        row["prepladder_qid"] = json.loads(line)["prepladder_qid"]
    micro.write_source(SOURCE, rows)
    sync_figures(images)
    print(f"PREPLADDER_PATHOLOGY_IMPORT_OK questions={len(rows)}")


def sync_figures(images: Path) -> None:
    """Trim the figures the bank uses into visuals/ and drop the rest."""
    from figure_trim import trim_file

    _, figures = normalize(load_source())
    used = {f["imageId"] for f in figures}
    VISUALS.mkdir(parents=True, exist_ok=True)
    trims = {}
    for image_id in sorted(used):
        target = VISUALS / f"{image_id}.jpg"
        if target.exists():
            continue
        src = images / f"{image_id}.jpg"
        if not src.exists():
            fail(f"missing figure {src}")
        box = trim_file(src, target)
        if box:
            trims[image_id] = list(box)
    for path in VISUALS.glob("*.jpg"):
        if path.stem not in used:
            path.unlink()
    missing = [i for i in used if not (VISUALS / f"{i}.jpg").exists()]
    if missing:
        fail(f"{len(missing)} figures in use have no file, e.g. {missing[0]}")
    inventory(trims)
    print(f"PREPLADDER_PATHOLOGY_FIGURES_OK in_use={len(used)} trimmed_now={len(trims)}")


def load_source() -> list[dict]:
    return micro.read_source(SOURCE)


# --- bank -----------------------------------------------------------------------

def topic_id(module: int) -> str:
    return f"pathology-{module}"


def normalize(rows: list[dict]) -> tuple[dict, list[dict]]:
    """The app record and the figures in use."""
    micro.count_words(rows)
    rows = [fix_record(q) for q in rows]
    topics: dict[int, dict] = {}
    for q in rows:
        k = int(q["module_index"])
        topics.setdefault(k, {"id": topic_id(k), "subject": SUBJECT, "bank": "PrepLadder",
                              "title": lesson_title(q["module_name"]), "section": q["section_category"],
                              "pyq": bool(q["is_pyq_lesson"]), "startPage": None, "questions": []})["questions"].append(q)
    questions, figures = [], []
    for k in sorted(topics):
        topic = topics[k]
        items = sorted(topic.pop("questions"), key=lambda q: int(q["question_number"]))
        for number, q in enumerate(items, 1):
            if int(q["question_number"]) != number:
                fail(f"{q['id']}: lesson {k} numbering has a gap at {number}")
            letters, texts, key, flagged = micro.answer_parts(q)
            stem, stem_tables, stem_images = micro.stem_parts(q)
            blocks, tables, explain_images = micro.explanation_parts(q, flattened=True)
            for block in blocks:
                if block["type"] == "paragraph":
                    block["text"] = fix_urls(block["text"])
            lost = bool(blocks) and blocks[0]["type"] == "paragraph" and bool(FRAGMENT.match(blocks[0]["text"]))
            if lost:
                blocks[0] = {"type": "paragraph", "text": NO_EXPLANATION}
            if not stem or not all(texts):
                fail(f"{q['id']}: blank stem or option")
            app_id = f"{topic['id']}-{number}"
            if topic["startPage"] is None and q["pages"]["question_pages"]:
                topic["startPage"] = q["pages"]["question_pages"][0]
            notes = list(q["quality_flags"])
            if lost:
                notes.append("source explanation lost in extraction; only a sentence fragment survived")
            if len(flagged) > 1:
                notes.append(f"source key lists {len(flagged)} correct options; scored on {letters[key - 1]}")
            record = {
                "id": app_id,
                "sourceQuestionId": q["id"],
                "prepladderQid": q["prepladder_qid"],
                "subject": SUBJECT,
                "bank": "PrepLadder",
                "explanationFormat": "structured",
                "chapterId": topic["id"],
                "chapter": topic["title"],
                "topic": topic["title"],
                "topicIndex": k,
                "questionNumber": number,
                "question": stem,
                "options": [{"letter": letters[i], "text": texts[i]} for i in range(len(texts))],
                "correctOption": key,
                "correctAnswerText": texts[key - 1],
                "explanation": micro.plain_text(blocks),
                "structuredExplanation": {"layout": "ordered-blocks", "blocks": blocks, "tables": tables,
                                          "figures": sorted(i["image_id"] for i in stem_images + explain_images)},
                "provenance": {"sourceFile": SOURCE_PDFS, "sourceLabel": SOURCE_LABEL,
                               "questionPages": q["pages"]["question_pages"],
                               "explanationPages": q["pages"]["explanation_pages"]},
                "sourcePage": (q["pages"]["question_pages"] or [None])[0],
                "reviewStatus": q["review_status"],
            }
            if stem_tables:
                record["stemTables"] = stem_tables
            if notes:
                record["reviewNotes"] = notes
            questions.append(record)
            for role, images in (("question", stem_images), ("explanation", explain_images)):
                for n, image in enumerate(images, 1):
                    figures.append({"imageId": image["image_id"], "questionId": app_id, "role": role, "order": n,
                                    "caption": image.get("caption"), "sourcePage": image.get("source_page")})
        topic["questionCount"] = number
        topic["sourceQuestionTotal"] = number
        topic["complete"] = True
    if len(figures) != len({f["imageId"] for f in figures}):
        fail("a figure is used twice")
    record = {"schema_version": "prepladder-text-bank-1.0", "subject": SUBJECT, "bank": "PrepLadder",
              "explanationFormat": "structured", "topics": [topics[k] for k in sorted(topics)], "questions": questions}
    return record, figures


def shard(record: dict) -> tuple[list[str], dict]:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    parts = [encoded[i:i + micro.SHARD_CHARS] for i in range(0, len(encoded), micro.SHARD_CHARS)]
    manifest = {
        "schema_version": "1.0", "subject": SUBJECT, "bank": "PrepLadder",
        "source": SOURCE.relative_to(ROOT).as_posix(), "source_sha256": micro.sha256(SOURCE.read_bytes()),
        "sourcePdfs": SOURCE_PDFS, "builder": "tools/build_prepladder_pathology_bank.py",
        "topics": len(record["topics"]), "questions": len(record["questions"]), "parts": len(parts),
        "base64_chars": len(encoded), "compressed_sha256": micro.sha256(compressed), "raw_sha256": micro.sha256(raw),
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
    if len(encoded) != manifest["base64_chars"] or micro.sha256(compressed) != manifest["compressed_sha256"]:
        fail("shards do not match the manifest")
    raw = zlib.decompress(compressed)
    if micro.sha256(raw) != manifest["raw_sha256"]:
        fail("raw SHA-256 mismatch")
    record = json.loads(raw)
    counts = {"questions": len(record["questions"]), "topics": len(record["topics"])}
    if counts != EXPECTED or record["bank"] != "PrepLadder" or record["subject"] != SUBJECT:
        fail(f"unexpected bank identity or counts: {counts}")
    return record


# --- figures ---------------------------------------------------------------------

def inventory(trims: dict | None = None) -> None:
    """Record every figure the bank uses. `trims` holds crops taken just now;
    other figures keep the crop recorded when they were imported."""
    previous = {}
    if INVENTORY.exists():
        previous = {f["imageId"]: f.get("trimBox") for f in json.loads(INVENTORY.read_text(encoding="utf-8"))["figures"]}
    previous.update(trims or {})
    _, used = normalize(load_source())
    figures = []
    for figure in used:
        path = VISUALS / f"{figure['imageId']}.jpg"
        data = path.read_bytes()
        width, height = micro.jpeg_size(data)
        figures.append({
            "imageId": figure["imageId"], "questionId": figure["questionId"], "role": figure["role"],
            "order": figure["order"], "alt": micro.alt_text(figure, figure["order"], figure["role"]),
            "file": path.relative_to(ROOT).as_posix(), "sha256": micro.sha256(data), "width": width, "height": height,
            "sourcePage": figure["sourcePage"], "trimBox": previous.get(figure["imageId"]),
        })
    INVENTORY.write_text(json.dumps({
        "schemaVersion": 1, "subject": SUBJECT, "bank": "PrepLadder", "sourcePdfs": SOURCE_PDFS,
        "note": "trimBox is the crop tools/figure_trim.py took from the extracted figure (null: untouched).",
        "figures": figures,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def release() -> None:
    value = json.loads(INVENTORY.read_text(encoding="utf-8"))
    runtime: dict[str, list[dict]] = {}
    for figure in value["figures"]:
        data = (ROOT / figure["file"]).read_bytes()
        if micro.sha256(data) != figure["sha256"]:
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
        "/* PrepLadder Pathology figures (generated by tools/build_prepladder_pathology_bank.py). */\n"
        f"window.MARROW_VISUALS=Object.assign(window.MARROW_VISUALS||{{}},{payload});\n",
        encoding="utf-8",
    )
    print(f"PREPLADDER_PATHOLOGY_VISUALS_OK questions={len(runtime)} figures={len(value['figures'])}")


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
    record, _ = normalize(load_source())
    parts, manifest = shard(record)
    manifest_path = DATA / f"{PREFIX}_manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    existing = sorted(DATA.glob(f"{PREFIX}.zlib.b64.part*"))
    if args.check:
        current = [p.read_text(encoding="utf-8").strip() for p in existing]
        if current != parts or not manifest_path.exists() or manifest_path.read_text(encoding="utf-8") != manifest_text:
            fail("shards/manifest are stale; run tools/build_prepladder_pathology_bank.py")
    else:
        for path in existing:
            path.unlink()
        for index, part in enumerate(parts):
            (DATA / f"{PREFIX}.zlib.b64.part{index:02d}").write_text(part + "\n", encoding="utf-8")
        manifest_path.write_text(manifest_text, encoding="utf-8")
    print(f"PREPLADDER_PATHOLOGY_BANK_OK questions={manifest['questions']} topics={manifest['topics']} parts={manifest['parts']}")


if __name__ == "__main__":
    main()
