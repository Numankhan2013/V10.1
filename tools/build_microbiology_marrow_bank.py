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
BULLET_V2 = re.compile(r"^(\s*)(?:[*•▪◦-]|(\d+)[.)])\s*(.*\S.*)$")
V2_PEARL = re.compile(r"^\[Marrow Pearl #(\d+):\s*(.+?)\]\s*$")
V2_TABLE_SLOT = re.compile(r"^\[Tables?:[^\]]*\]\s*$")
V2_TOKEN = re.compile(r"^@@V2BLOCK:(\d+)@@$")

# How each extracted JSONL part maps onto the one Microbiology PDF and the app's
# module list. Every part after 01 was extracted from its own split PDF
# ("Microbiology Marrow Qbank-0N.pdf", pages from 1) and numbers its modules
# from 1. `pageOffset` turns a split-PDF page into the page of
# data/marrow/source_pdfs/Microbiology Marrow Qbank.pdf; the splits partition
# the 173-page PDF contiguously, and each split's page 1 was matched against
# the full PDF by its embedded page-image hash (part 02 = full 27 [MA1545 OCR
# cross-check], 03 = 48, 04 = 74, 05 = 100, 06 = 126). `moduleOffset` turns the
# part's module index into the app module; a part whose first module continues
# the previous part's last module joins it (part 03 module 1 = module 7 Q21).
PART_LAYOUT = {
    "Microbiology_Marrow_Qbank_01.jsonl": {"schema": 1, "pageOffset": 0, "moduleOffset": 0},
    "Microbiology_Marrow_Qbank_02.jsonl": {"schema": 2, "pageOffset": 26, "moduleOffset": 4},
    "Microbiology_Marrow_Qbank_03.jsonl": {"schema": 2, "pageOffset": 47, "moduleOffset": 6},
    "Microbiology_Marrow_Qbank_04.jsonl": {"schema": 2, "pageOffset": 73, "moduleOffset": 9},
    "Microbiology_Marrow_Qbank_05.jsonl": {"schema": 2, "pageOffset": 99, "moduleOffset": 12},
    "Microbiology_Marrow_Qbank_06.jsonl": {"schema": 2, "pageOffset": 125, "moduleOffset": 16},
}
# A module that spans two parts gets one app title: the continuation's name
# without "(continued)" (module 5) or the two halves combined (module 13, 17),
# with the true total from the final part.
MODULE_OVERRIDES = {
    5: {"title": "Staphylococcus, Streptococcus, Enterococcus & Pneumococcus", "total": 60},
    7: {"title": "Clostridium, Bacillus, Lactobacillus & Nocardia", "total": 44},
    10: {"title": "Vibrio, Campylobacter, Helicobacter pylori, Legionella & Bartonella", "total": 38},
    13: {"title": "Rickettsiaceae, Orientia tsutsugamushi, Coxiella burnetii, Bartonella, Ehrlichia, Chlamydia & Mycoplasma", "total": 29},
    17: {"title": "Hepatitis Viruses (HAV, HBV, HCV, HDV & HEV)", "total": 25},
}


def fail(message: str) -> None:
    raise SystemExit(f"MICROBIOLOGY_BANK_ERROR: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_parts() -> list[Path]:
    # Only parts with a PART_LAYOUT entry are integrated. Source parts that are
    # uploaded but not integrated yet stay in the directory (their layout
    # offsets are added when they are built in) and must not fail the build.
    found = sorted(SOURCE_DIR.glob("Microbiology_Marrow_Qbank_*.jsonl"))
    parts = [path for path in found if path.name in PART_LAYOUT]
    pending = [path.name for path in found if path.name not in PART_LAYOUT]
    if pending:
        print("MICROBIOLOGY_MARROW_PARTS_PENDING " + " ".join(pending))
    if not parts:
        fail(f"no integrated source JSONL under {SOURCE_DIR.relative_to(ROOT)}")
    return parts


def load_source() -> tuple[list[dict], list[dict]]:
    rows, files = [], []
    for path in source_parts():
        raw = path.read_bytes()
        part_rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
        layout = PART_LAYOUT.get(path.name)
        if layout is None:
            fail(f"{path.name}: add its page/module offsets to PART_LAYOUT before building")
        files.append({"file": path.name, "sha256": sha256(raw), "questions": len(part_rows),
                      "schema": layout["schema"], "pageOffset": layout["pageOffset"],
                      "moduleOffset": layout["moduleOffset"]})
        rows.extend(adapt_v2(row, layout, path.name) if layout["schema"] == 2 else row for row in part_rows)
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


CLIPPED_NOTE = re.compile(r"\s*\[clipped[^\]]*\]", re.I)
CELL_RECONSTRUCTION = re.compile(r"^(.*?)\s*\[([^\]\n]+)\]$")
WORD_RECONSTRUCTION = re.compile(r"(\S+) \[([^\]\n]+)\]")
# An extractor can eat the space before a bold opener, gluing it to the word
# ("resembling**\"flow of seed\"**"). Keep the marker but separate it.
GLUED_BOLD_OPENER = re.compile(r"(\w)\*\*(?=[\"'«“‘(\[{])")


def _fold(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def clean_v2(text: str, hygiene: "Hygiene", cell: bool = False) -> str:
    """Part 02+ convention: clipped screenshot text is kept as `visible [full]`.

    Show the reconstruction instead of the clipped fragment, and drop the
    extractor's `[clipped at right margin as ...]` notes. Applied to display
    only; the raw JSONL keeps both strings.
    """
    value = str(text or "")
    out = CLIPPED_NOTE.sub("", value)
    if out != value:
        hygiene.notes.add("removed extractor clipping notes")
    separated = GLUED_BOLD_OPENER.sub(r"\1 **", out)
    if separated != out:
        hygiene.notes.add("separated an extractor-glued bold opener")
    out = separated
    if cell:
        lines = []
        for line in out.split("\n"):
            m = CELL_RECONSTRUCTION.match(line.strip())
            if m and not V2_TABLE_SLOT.match(line.strip()):
                hygiene.notes.add("showed reconstructions of screenshot-clipped table text")
                lines.append(m.group(2).strip())
            else:
                lines.append(line)
        out = "\n".join(lines)

    def word(m: re.Match) -> str:
        visible, full = m.group(1), m.group(2)
        head = _fold(visible)[:3]
        if head and _fold(full).startswith(head):
            hygiene.notes.add("showed reconstructions of screenshot-clipped words")
            return full
        return m.group(0)
    return WORD_RECONSTRUCTION.sub(word, out)


def _plain_line(text: str) -> str:
    text = re.sub(r"^\s*(?:[*•▪◦-]\s*|\d+[.)]\s*)", "", str(text or ""))
    return _fold(re.sub(r"[*_`]", "", text))


def adapt_v2(q: dict, layout: dict, part: str) -> dict:
    """Map a part-02-style record onto the field names the normalizer reads.

    Field renames only (question_stem object -> text, correct_answer ->
    correct_option, source_provenance -> provenance); pages and modules are
    shifted onto the full PDF and the app's module list via PART_LAYOUT.
    """
    prov = q.get("source_provenance") or {}
    offset = int(layout["pageOffset"])
    options = q.get("options") or []
    key = str(q.get("correct_answer") or "").strip().upper()
    keyed = next((o for o in options if str(o.get("id", "")).upper() == key), {})
    stem = q.get("question_stem") or {}
    blocks = q.get("explanation_blocks") or []
    first = blocks[0] if blocks else {}
    summary = ""
    if first.get("type") == "text" and "\n" not in str(first.get("content") or "").strip():
        summary = str(first.get("content") or "").strip()
    images = []
    for image in q.get("images") or []:
        box = dict(image.get("bounding_box") or {})
        if box:
            box["page"] = int(box.get("page") or image.get("source_page")) + offset
        images.append({**image, "source_page": int(image.get("source_page")) + offset, "bounding_box": box})
    module_index = int(q["module_index"]) + int(layout["moduleOffset"])
    return {
        **q,
        "_schema": 2,
        "_part": part,
        "module_index": module_index,
        "question_stem": str(stem.get("text") if isinstance(stem, dict) else stem or "").strip(),
        "correct_option": key,
        "correct_answer_text": str(keyed.get("text") or "").strip(),
        "answer_summary": summary,
        "images": images,
        "provenance": {
            "source_pdf": prov.get("source_pdf_filename"),
            "split_pdf_pages": prov.get("source_pages") or [],
            "source_pages": [int(p) + offset for p in prov.get("source_pages") or []],
            "quality_flags": q.get("quality_flags") or [],
        },
        "source_attempt_metadata": {"qbank_version_header": prov.get("qbank_version_header")
                                     or (q.get("source_attempt_metadata") or {}).get("qbank_version_header")},
    }


def _v2_table(meta: dict, hygiene: "Hygiene", pearl_id: str | None = None) -> dict:
    headers = list(meta.get("headers") or [])
    rows = [list(r) for r in meta.get("rows") or []]
    if not headers or not rows:
        fail(f"table {meta.get('table_id')} has no headers or rows")
    columns = [clean_v2(c, hygiene, cell=True).strip() for c in headers]
    body = [[clean_v2(c, hygiene, cell=True).strip() for c in (r + [""] * len(columns))[:len(columns)]] for r in rows]
    table = {"table_id": meta["table_id"], "title": clean_v2(meta.get("title") or "", hygiene),
             "columns": columns, "rows": body}
    if pearl_id:
        table["pearl_id"] = pearl_id
    return table


def parse_v2(q: dict, hygiene: "Hygiene") -> tuple[list[dict], list[dict]]:
    """Part 02+: explanation_blocks give the order (text, list, image, table,
    pearl, callout); explanation_markdown gives the formatting of the text.

    The markdown carries only the text and one `[Marrow Pearl #N: Title]` line
    per pearl, so images, tables and callouts are slotted in after the
    markdown line that ends the text block before them, and each pearl expands
    in place to its heading, body, tables and pearl images.
    """
    md = str(q.get("explanation_markdown") or "").replace("\r", "")
    for wrong, right, _evidence in SOURCE_CORRECTIONS.get(q["id"], []):
        if md.count(wrong) != 1:
            fail(f"{q['id']}: source correction {wrong!r} no longer matches the raw explanation")
        md = md.replace(wrong, right)
        hygiene.notes.add(f"source-checked correction: {wrong} -> {right}")
    lines = md.split("\n")
    plains = [_plain_line(l) for l in lines]
    images = {img["image_id"]: img for img in q.get("images") or []}
    pearls = {str(p.get("pearl_id")): p for p in q.get("pearls") or []}
    table_meta: dict[str, dict] = {}
    for t in q.get("tables") or []:
        table_meta[t["table_id"]] = t
    for p in pearls.values():
        for t in p.get("tables") or []:
            table_meta.setdefault(t["table_id"], t)
    payloads: list[list[dict]] = []
    tables: list[dict] = []
    used_tables: set[str] = set()
    figures_seen: set[str] = set()
    inserts: dict[int, list[int]] = {}
    cursor = 0
    misses = 0

    def table_blocks(meta: dict, pearl_id: str | None) -> list[dict]:
        if meta["table_id"] in used_tables:
            # A table already shown in this explanation is shown once.
            return []
        used_tables.add(meta["table_id"])
        tables.append(_v2_table(meta, hygiene, pearl_id))
        out = [{"type": "table", "table_id": meta["table_id"]}]
        return out

    def figure(image_id: str) -> dict:
        meta = images.get(image_id)
        if not meta:
            fail(f"{q['id']}: image {image_id} has no image metadata")
        figures_seen.add(image_id)
        return {"type": "figure", "figure_id": image_id, "caption": str(meta.get("caption") or "").strip()}

    def pearl_blocks(pearl_id: str, number: str, title: str) -> list[dict]:
        meta = pearls.get(pearl_id)
        if not meta:
            fail(f"{q['id']}: {pearl_id} has no pearl metadata")
        out: list[dict] = [{"type": "pearl", "pearl_id": pearl_id,
                            "category": str(meta.get("category") or "").strip(),
                            "title": str(meta.get("title") or title).strip()}]
        ptables = list(meta.get("tables") or [])
        footnotes = {_plain_line(f) for t in ptables for f in t.get("footnotes") or []}
        body_lines = str(meta.get("body_text") or "").replace("\r", "").split("\n")
        titles = {_fold(out[0]["title"])} | {_fold(t.get("title") or "") for t in ptables}
        meaningful = [l for l in body_lines if l.strip()]
        if meaningful and _fold(meaningful[0]) in titles:
            body_lines = body_lines[body_lines.index(meaningful[0]) + 1:]
            meaningful = meaningful[1:]
        footnote_body = bool(meaningful) and all(
            _plain_line(l) in footnotes or re.fullmatch(r"note\s*:?", l.strip(), re.I) for l in meaningful)
        slot = next((i for i, l in enumerate(body_lines) if V2_TABLE_SLOT.match(l.strip())), None)
        pearl_table_blocks = [b for t in ptables for b in table_blocks(t, pearl_id)]
        body_text = "\n".join(body_lines)
        if footnote_body:
            out += pearl_table_blocks
            out += [{"type": "note", "text": clean_v2(" ".join(l.strip() for l in meaningful), hygiene)}]
        elif slot is not None:
            out += _v2_text_blocks("\n".join(body_lines[:slot]), hygiene)
            out += pearl_table_blocks
            out += _v2_text_blocks("\n".join(body_lines[slot + 1:]), hygiene)
        else:
            out += _v2_text_blocks(body_text, hygiene)
            out += pearl_table_blocks
        if not footnote_body:
            for t in ptables:
                notes = [f for f in t.get("footnotes") or [] if _plain_line(f) not in {_plain_line(l) for l in body_lines}]
                if notes:
                    out.append({"type": "note", "text": clean_v2(" ".join(notes), hygiene)})
        out += [figure(i) for i in meta.get("embedded_image_ids") or []]
        return out

    pearl_lines = {i for i, l in enumerate(lines) if V2_PEARL.match(l.strip())}
    for block in q.get("explanation_blocks") or []:
        kind = block.get("type")
        if kind in ("text", "list"):
            parts = [block.get("content")] if kind == "text" else block.get("items") or []
            last = ""
            for part in reversed(parts):
                part = part.get("text") if isinstance(part, dict) else part
                candidates = [x for x in str(part or "").split("\n") if _plain_line(x)]
                if candidates:
                    last = _plain_line(candidates[-1])
                    break
            hit = next((j for j in range(cursor, len(lines)) if j not in pearl_lines and last
                        and (plains[j] == last or (len(last) > 12 and plains[j].endswith(last)))), None)
            if hit is None:
                misses += 1
            else:
                cursor = hit + 1
            continue
        if kind == "pearl":
            pearl_id = str(block.get("pearl_id"))
            number = pearl_id.split("#")[-1]
            hit = next((j for j in range(cursor, len(lines)) if (m := V2_PEARL.match(lines[j].strip())) and m.group(1) == number), None)
            if hit is None:
                fail(f"{q['id']}: {pearl_id} block has no [Marrow Pearl] line in the markdown")
            payloads.append(pearl_blocks(pearl_id, number, V2_PEARL.match(lines[hit].strip()).group(2)))
            lines[hit] = f"@@V2BLOCK:{len(payloads) - 1}@@"
            pearl_lines.discard(hit)
            cursor = hit + 1
            continue
        if kind == "image":
            # Some extractions repeat a pearl's embedded figure as a standalone
            # image block; the pearl placement (in_pearl metadata) wins.
            if block["image_id"] in figures_seen:
                continue
            payload = [figure(block["image_id"])]
        elif kind == "table":
            meta = table_meta.get(block.get("table_id"))
            if not meta:
                fail(f"{q['id']}: table block {block.get('table_id')} has no table metadata")
            payload = table_blocks(meta, None)
            notes = meta.get("footnotes") or []
            if notes:
                payload.append({"type": "note", "text": clean_v2(" ".join(notes), hygiene)})
        elif kind == "callout_note":
            payload = [{"type": "note", "text": clean_v2(block.get("content") or "", hygiene)}]
        elif kind == "reference_url":
            continue  # source viewer links (UpToDate search URLs) are not shown, like Ref lines
        else:
            fail(f"{q['id']}: unknown explanation block type {kind!r}")
        payloads.append(payload)
        inserts.setdefault(cursor, []).append(len(payloads) - 1)
    if pearl_lines:
        fail(f"{q['id']}: markdown pearl line(s) without a pearl block")
    merged: list[str] = []
    for i, line in enumerate(lines + [""]):
        for token in inserts.get(i, []):
            merged += ["", f"@@V2BLOCK:{token}@@", ""]
        if i < len(lines):
            merged.append(line)
    blocks = _v2_text_blocks("\n".join(merged), hygiene, payloads)
    if misses:
        hygiene.anchor_misses = misses
    figure_ids = sorted(b["figure_id"] for b in blocks if b["type"] == "figure")
    explanation_images = sorted(k for k, v in images.items() if v.get("location") != "question_stem")
    if figure_ids != explanation_images:
        fail(f"{q['id']}: figure blocks {figure_ids} differ from explanation image metadata {explanation_images}")
    expected_tables = sorted(table_meta)
    if sorted(used_tables) != expected_tables:
        fail(f"{q['id']}: tables shown {sorted(used_tables)} differ from table metadata {expected_tables}")
    return blocks, tables


def _v2_text_blocks(markdown: str, hygiene: "Hygiene", payloads: list[list[dict]] | None = None) -> list[dict]:
    """Paragraphs, bullet lists (•, -, *, 1.) and block tokens, in order."""
    blocks: list[dict] = []
    para: list[str] = []
    lines = markdown.split("\n")

    def flush() -> None:
        text = " ".join(x for x in para if x).strip()
        para.clear()
        if text:
            blocks.append({"type": "paragraph", "text": text})
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        token = V2_TOKEN.match(stripped)
        bullet = re.match(r"^(\s*)(?:[*-]\s+|[•▪◦]\s*|(\d+)[.)]\s*)(\S.*)$", line)
        if not stripped:
            flush(); i += 1; continue
        if token:
            flush()
            blocks.extend((payloads or [])[int(token.group(1))])
            i += 1
            continue
        if stripped.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip()); i += 1
            text = re.sub(r"^\*\*Note:\*\*\s*", "", " ".join(x for x in quote if x))
            blocks.append({"type": "note", "text": clean_v2(text, hygiene)})
            continue
        if bullet and not re.match(r"^\*\*", stripped):
            flush()
            ordered = bool(bullet.group(2))
            start = int(bullet.group(2)) if ordered else 1
            items: list[dict] = []
            pattern = r"^(\s*)(?:[*-]\s+|[•▪◦]\s*|(\d+)[.)]\s*)(\S.*)$"
            while i < len(lines):
                if not lines[i].strip() and ordered:
                    # "1. Heading / • items / (blank) / 2. Heading": one numbered list.
                    j = i
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    nxt = re.match(pattern, lines[j]) if j < len(lines) else None
                    if nxt and nxt.group(2) and int(nxt.group(2)) == start + len(items):
                        i = j
                        continue
                    break
                m = re.match(pattern, lines[i])
                if not m or re.match(r"^\*\*", lines[i].strip()):
                    break
                depth = len(m.group(1).replace("\t", "  ")) // 2
                entry = {"text": clean_v2(m.group(3).strip(), hygiene), "items": []}
                if ordered and not m.group(2) and items:
                    # unnumbered bullets under a numbered heading belong to it
                    items[-1]["items"].append(entry)
                elif bool(m.group(2)) != ordered and depth == 0:
                    break
                elif depth == 0 or not items:
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
            block = {"type": "bullets", "ordered": ordered, "items": items}
            if ordered and start != 1:
                block["start"] = start
            blocks.append(block)
            continue
        para.append(clean_v2(stripped, hygiene))
        i += 1
    flush()
    return blocks


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
        override = MODULE_OVERRIDES.get(module_index)
        if override:
            module["title"] = override["title"]
            module["sourceQuestionTotal"] = int(override["total"])
            aliases = module.setdefault("sourceModules", [])
            alias = {"part": q.get("_part") or "Microbiology_Marrow_Qbank_01.jsonl", "moduleId": q["module_id"],
                     "title": str(q["module_name"]).strip(), "reportedTotal": int(q["module_total_questions_in_app"])}
            if alias not in aliases:
                aliases.append(alias)
        elif module["title"] != str(q["module_name"]).strip() or module["moduleId"] != q["module_id"]:
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
        blocks, tables = parse_v2(q, hygiene) if q.get("_schema") == 2 else parse_markdown(q, hygiene)
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
        if getattr(hygiene, "anchor_misses", 0):
            record["layoutNotes"] = [f"{hygiene.anchor_misses} text block(s) not matched to a markdown line; following media placed at the last matched line"]
        if len(record["keyTakeaway"]) < 24:
            record.pop("keyTakeaway")
        questions.append(record)

    for record in questions:
        record["chapter"] = modules[int(record["chapterId"])]["title"]
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
