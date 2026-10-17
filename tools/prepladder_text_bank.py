#!/usr/bin/env python3
"""Shared builder for PrepLadder text banks (Pathology, Pharmacology).

These subjects arrive like the PrepLadder Microbiology November 2025 edition:
a structured extraction (text, option analysis and image blocks) of the
November 2025 QBank PDFs, whose explanations were printed as flat text. The
text cleanup and block rules are Microbiology's
(tools/build_prepladder_microbiology_bank.py); this file adds the layout every
text bank shares. Explanations render through the Marrow ordered-block
renderer while the bank stays labelled PrepLadder.

Layout (data/Prepladder/<slug>/):
  source/prepladder_<slug>_qbank.jsonl.gz   slim extraction
  visuals/<image_id>.jpg                    figures, extraction borders trimmed
  visuals.json                              figure inventory (hash, size, trim box)
  prepladder_<slug>_qbank.zlib.b64.partNN   built bank (hash-pinned shards)
  prepladder_<slug>_qbank_manifest.json
  restructure/restructured.json             optional restructured explanations

Each subject's builder (tools/build_prepladder_<slug>_bank.py) makes one
TextBank and hands its command line to TextBank.main().
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_prepladder_microbiology_bank as micro  # noqa: E402
from prepladder_microbiology_edition import fix_record  # noqa: E402

ASSETS = ROOT / "app/src/main/assets"
SOURCE_LABEL = "PrepLadder November 2025 edition"
SMALL = {"and", "of", "to", "in", "the", "with", "for", "or", "on", "at", "by", "vs"}

# For some questions the source PDF itself prints only a sentence tail as the
# explanation ("Explanation: of the correct answer.", "for Assertion."). The
# fragment goes; the question says so instead of showing it.
FRAGMENT = re.compile(r"^[a-z][^.]{0,40}\.$")
NO_EXPLANATION = "The source PDF prints no explanation for this question."

# The extraction turned "&source=" in reference URLs into "&source;=" (the
# PDF also wraps URLs with spaces, so the fix cannot look for whole URLs);
# ";=" and ";_" never occur in prose.
ENTITY_LEAK = re.compile(r"(?<=[A-Za-z]);(?=[=_])")

# "References: Robbins and Cotran Pathologic Basis of Disease, 10th edition,
# Page 37; https://..." becomes a references block, one item per source. A
# book's title (the text before its edition, page or chapter) shows in italics;
# URLs and "PrepLadder Notes" stay plain. The app draws it below the figures.
REFERENCES = re.compile(r"^References?\s*:\s*", re.I)
LOCATOR = re.compile(r",?\s*(?:\d+(?:st|nd|rd|th)\s+ed(?:ition)?\b|pages?\b|pg\.|chapter\b)", re.I)


def fix_urls(text: str) -> str:
    return ENTITY_LEAK.sub("", text)


def reference_item(text: str) -> dict:
    m = LOCATOR.search(text)
    title = text[:m.start()] if m else ""
    if len(title) < 3 or "(" in title or "http" in text.lower() or "prepladder" in title.lower():
        return {"rest": text}
    return {"title": title, "rest": text[m.start():]}


def references_block(block: dict) -> dict:
    if block["type"] != "paragraph" or not REFERENCES.match(block["text"]):
        return block
    items = [reference_item(part.strip()) for part in REFERENCES.sub("", block["text"]).split(";") if part.strip()]
    return {"type": "references", "text": block["text"], "items": items} if items else block


def source_hash(body: list[dict]) -> str:
    """Restructured explanations name the hash of the body they were made from."""
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


class TextBank:
    def __init__(self, slug: str, subject: str, source_pdfs: str, expected: dict, acronyms: dict[str, str]):
        self.slug, self.subject, self.source_pdfs, self.expected = slug, subject, source_pdfs, expected
        # The extraction title-cases every word ("Cml And Cll", "Hodgkin'S").
        self.acronyms = acronyms
        self.tag = f"PREPLADDER_{slug.upper()}"
        self.builder = f"tools/build_prepladder_{slug}_bank.py"
        self.data = ROOT / f"data/Prepladder/{slug}"
        self.prefix = f"prepladder_{slug}_qbank"
        self.source = self.data / f"source/{self.prefix}.jsonl.gz"
        self.visuals = self.data / "visuals"
        self.inventory_path = self.data / "visuals.json"
        self.runtime = ASSETS / f"prepladder_{slug}_visual_metadata.js"
        # Explanations restructured by an outside model (tools/explanation_restructure.py):
        # the same words as paragraphs, points and tables.
        self.overlay = self.data / "restructure" / "restructured.json"

    def fail(self, message: str) -> None:
        raise SystemExit(f"{self.tag}_FAIL: {message}")

    def lesson_title(self, title: str) -> str:
        def word(m: re.Match) -> str:
            w = m.group(0)
            low = w.lower()
            if low in self.acronyms:
                return self.acronyms[low]
            if m.start() and low in SMALL:
                return low
            return w
        title = re.sub(r"[A-Za-z]+", word, title.strip())
        return re.sub(r"'S\b", "'s", title)

    def topic_id(self, module: int) -> str:
        return f"{self.slug}-{module}"

    # --- import -------------------------------------------------------------------

    def import_source(self, master: Path, images: Path) -> None:
        lines = [line for line in master.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = []
        for line in lines:
            raw = json.loads(line)
            rows.append({**micro.slim(raw), "prepladder_qid": raw["prepladder_qid"]})
        micro.write_source(self.source, rows)
        self.sync_figures(images)
        print(f"{self.tag}_IMPORT_OK questions={len(rows)}")

    def sync_figures(self, images: Path) -> None:
        """Trim the figures the bank uses into visuals/ and drop the rest."""
        from figure_trim import trim_file

        _, figures = self.normalize(self.load_source())
        used = {f["imageId"] for f in figures}
        self.visuals.mkdir(parents=True, exist_ok=True)
        trims = {}
        for image_id in sorted(used):
            target = self.visuals / f"{image_id}.jpg"
            if target.exists():
                continue
            src = images / f"{image_id}.jpg"
            if not src.exists():
                self.fail(f"missing figure {src}")
            box = trim_file(src, target)
            if box:
                trims[image_id] = list(box)
        for path in self.visuals.glob("*.jpg"):
            if path.stem not in used:
                path.unlink()
        missing = [i for i in used if not (self.visuals / f"{i}.jpg").exists()]
        if missing:
            self.fail(f"{len(missing)} figures in use have no file, e.g. {missing[0]}")
        self.inventory(trims)
        print(f"{self.tag}_FIGURES_OK in_use={len(used)} trimmed_now={len(trims)}")

    def load_source(self) -> list[dict]:
        return micro.read_source(self.source)

    # --- bank ---------------------------------------------------------------------

    def apply_overlay(self, app_id: str, blocks: list[dict], tables: list[dict], entry: dict) -> list[dict]:
        body = [b for b in blocks if not (b["type"] == "paragraph" and REFERENCES.match(b["text"]))]
        if source_hash(body) != entry["sourceHash"]:
            self.fail(f"{app_id}: restructured explanation was made from a different source; re-run it")
        out = []
        for block in entry["blocks"]:
            if block["type"] == "table":
                table_id = f"{app_id}-t{len(tables) + 1}"
                tables.append({"table_id": table_id, "title": block.get("title", ""),
                               "columns": block["columns"], "rows": block["rows"]})
                out.append({"type": "table", "table_id": table_id})
            else:
                out.append(block)
        return out + [b for b in blocks if b not in body]

    @staticmethod
    def join_reference_tail(blocks: list[dict]) -> list[dict]:
        """The extraction sometimes starts a new paragraph inside the references
        ("... Effects of aspirin at different dosages. While aspirin acts as an...");
        text after the references belongs to them."""
        out: list[dict] = []
        refs = None
        for block in blocks:
            if refs is not None and block["type"] == "paragraph":
                refs["text"] += " " + block["text"]
                continue
            if block["type"] == "paragraph" and REFERENCES.match(block["text"]):
                refs = block = dict(block)
            out.append(block)
        return out

    def normalize(self, rows: list[dict], overlay: bool = True) -> tuple[dict, list[dict]]:
        """The app record and the figures in use; `overlay` applies restructured explanations."""
        restructured = json.loads(self.overlay.read_text(encoding="utf-8")) if overlay and self.overlay.exists() else {}
        micro.count_words(rows)
        rows = [fix_record(q) for q in rows]
        topics: dict[int, dict] = {}
        for q in rows:
            k = int(q["module_index"])
            topics.setdefault(k, {"id": self.topic_id(k), "subject": self.subject, "bank": "PrepLadder",
                                  "title": self.lesson_title(q["module_name"]), "section": q["section_category"],
                                  "pyq": bool(q["is_pyq_lesson"]), "startPage": None, "questions": []})["questions"].append(q)
        questions, figures = [], []
        for k in sorted(topics):
            topic = topics[k]
            items = sorted(topic.pop("questions"), key=lambda q: int(q["question_number"]))
            for number, q in enumerate(items, 1):
                if int(q["question_number"]) != number:
                    self.fail(f"{q['id']}: lesson {k} numbering has a gap at {number}")
                letters, texts, key, flagged = micro.answer_parts(q)
                stem, stem_tables, stem_images = micro.stem_parts(q)
                blocks, tables, explain_images = micro.explanation_parts(q, flattened=True)
                for block in blocks:
                    if block["type"] == "paragraph":
                        block["text"] = fix_urls(block["text"])
                fragment = bool(blocks) and blocks[0]["type"] == "paragraph" and bool(FRAGMENT.match(blocks[0]["text"]))
                if fragment:
                    blocks.pop(0)
                # Some print nothing else, or only references, after "Explanation:"
                # (a figure alone is an explanation).
                bare = not any(b["type"] == "figure" or b["type"] == "paragraph" and not REFERENCES.match(b["text"])
                               for b in blocks)
                lost = fragment and bare
                if bare:
                    blocks.insert(0, {"type": "paragraph", "text": NO_EXPLANATION})
                blocks = self.join_reference_tail(blocks)
                explanation = micro.plain_text(blocks)
                app_id = f"{topic['id']}-{number}"
                if app_id in restructured:
                    blocks = self.apply_overlay(app_id, blocks, tables, restructured[app_id])
                if not stem or not all(texts):
                    self.fail(f"{q['id']}: blank stem or option")
                if topic["startPage"] is None and q["pages"]["question_pages"]:
                    topic["startPage"] = q["pages"]["question_pages"][0]
                notes = list(q["quality_flags"])
                if lost:
                    notes.append("source PDF prints no explanation, only a sentence fragment")
                elif bare:
                    notes.append("source PDF prints no explanation, only references")
                elif fragment:
                    notes.append("source PDF explanation opens mid-sentence; the fragment is left out")
                if len(flagged) > 1:
                    notes.append(f"source key lists {len(flagged)} correct options; scored on {letters[key - 1]}")
                record = {
                    "id": app_id,
                    "sourceQuestionId": q["id"],
                    "prepladderQid": q["prepladder_qid"],
                    "subject": self.subject,
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
                    "explanation": explanation,
                    "structuredExplanation": {"layout": "ordered-blocks", "blocks": [references_block(b) for b in blocks],
                                              "tables": tables,
                                              "figures": sorted(i["image_id"] for i in stem_images + explain_images)},
                    "provenance": {"sourceFile": self.source_pdfs, "sourceLabel": SOURCE_LABEL,
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
            self.fail("a figure is used twice")
        record = {"schema_version": "prepladder-text-bank-1.0", "subject": self.subject, "bank": "PrepLadder",
                  "explanationFormat": "structured", "topics": [topics[k] for k in sorted(topics)],
                  "questions": questions}
        return record, figures

    def shard(self, record: dict) -> tuple[list[str], dict]:
        raw = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        compressed = zlib.compress(raw, 9)
        encoded = base64.b64encode(compressed).decode("ascii")
        parts = [encoded[i:i + micro.SHARD_CHARS] for i in range(0, len(encoded), micro.SHARD_CHARS)]
        manifest = {
            "schema_version": "1.0", "subject": self.subject, "bank": "PrepLadder",
            "source": self.source.relative_to(ROOT).as_posix(), "source_sha256": micro.sha256(self.source.read_bytes()),
            "sourcePdfs": self.source_pdfs, "builder": self.builder,
            "topics": len(record["topics"]), "questions": len(record["questions"]), "parts": len(parts),
            "base64_chars": len(encoded), "compressed_sha256": micro.sha256(compressed),
            "raw_sha256": micro.sha256(raw),
            "topicCounts": {t["id"]: t["questionCount"] for t in record["topics"]},
        }
        return parts, manifest

    def app_record(self) -> dict:
        """The hash-verified bank, as embedded in MARROW_DATA.records."""
        manifest = json.loads((self.data / f"{self.prefix}_manifest.json").read_text(encoding="utf-8"))
        parts = sorted(self.data.glob(f"{self.prefix}.zlib.b64.part*"))
        if len(parts) != manifest["parts"]:
            self.fail("shard count mismatch")
        encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
        compressed = base64.b64decode(encoded, validate=True)
        if len(encoded) != manifest["base64_chars"] or micro.sha256(compressed) != manifest["compressed_sha256"]:
            self.fail("shards do not match the manifest")
        raw = zlib.decompress(compressed)
        if micro.sha256(raw) != manifest["raw_sha256"]:
            self.fail("raw SHA-256 mismatch")
        record = json.loads(raw)
        counts = {"questions": len(record["questions"]), "topics": len(record["topics"])}
        if counts != self.expected or record["bank"] != "PrepLadder" or record["subject"] != self.subject:
            self.fail(f"unexpected bank identity or counts: {counts}")
        return record

    # --- figures ------------------------------------------------------------------

    def inventory(self, trims: dict | None = None) -> None:
        """Record every figure the bank uses. `trims` holds crops taken just now;
        other figures keep the crop recorded when they were imported."""
        previous = {}
        if self.inventory_path.exists():
            previous = {f["imageId"]: f.get("trimBox")
                        for f in json.loads(self.inventory_path.read_text(encoding="utf-8"))["figures"]}
        previous.update(trims or {})
        _, used = self.normalize(self.load_source())
        figures = []
        for figure in used:
            path = self.visuals / f"{figure['imageId']}.jpg"
            data = path.read_bytes()
            width, height = micro.jpeg_size(data)
            figures.append({
                "imageId": figure["imageId"], "questionId": figure["questionId"], "role": figure["role"],
                "order": figure["order"], "alt": micro.alt_text(figure, figure["order"], figure["role"]),
                "file": path.relative_to(ROOT).as_posix(), "sha256": micro.sha256(data), "width": width,
                "height": height, "sourcePage": figure["sourcePage"], "trimBox": previous.get(figure["imageId"]),
            })
        self.inventory_path.write_text(json.dumps({
            "schemaVersion": 1, "subject": self.subject, "bank": "PrepLadder", "sourcePdfs": self.source_pdfs,
            "note": "trimBox is the crop tools/figure_trim.py took from the extracted figure (null: untouched).",
            "figures": figures,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def release(self) -> None:
        value = json.loads(self.inventory_path.read_text(encoding="utf-8"))
        runtime: dict[str, list[dict]] = {}
        for figure in value["figures"]:
            data = (ROOT / figure["file"]).read_bytes()
            if micro.sha256(data) != figure["sha256"]:
                self.fail(f"figure changed since inventory: {figure['imageId']}")
            rel = f"marrow_visuals/{figure['sha256']}.jpg"
            target = ASSETS / rel
            if not target.exists():
                target.write_bytes(data)
            runtime.setdefault(figure["questionId"], []).append({
                "id": f"prepladder-{figure['imageId']}", "role": figure["role"], "order": figure["order"],
                "src": rel, "alt": figure["alt"], "status": "PASS", "width": figure["width"], "height": figure["height"],
            })
        payload = json.dumps(runtime, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")
        self.runtime.write_text(
            f"/* PrepLadder {self.subject} figures (generated by {self.builder}). */\n"
            f"window.MARROW_VISUALS=Object.assign(window.MARROW_VISUALS||{{}},{payload});\n",
            encoding="utf-8",
        )
        print(f"{self.tag}_VISUALS_OK questions={len(runtime)} figures={len(value['figures'])}")

    def main(self, doc: str | None = None) -> None:
        parser = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("command", nargs="?", choices=["build", "import", "release"], default="build")
        parser.add_argument("paths", nargs="*")
        parser.add_argument("--check", action="store_true")
        args = parser.parse_args()
        if args.command == "import":
            self.import_source(Path(args.paths[0]), Path(args.paths[1]))
        elif args.command == "release":
            self.release()
            return
        record, _ = self.normalize(self.load_source())
        parts, manifest = self.shard(record)
        manifest_path = self.data / f"{self.prefix}_manifest.json"
        manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        existing = sorted(self.data.glob(f"{self.prefix}.zlib.b64.part*"))
        if args.check:
            current = [p.read_text(encoding="utf-8").strip() for p in existing]
            if current != parts or not manifest_path.exists() or manifest_path.read_text(encoding="utf-8") != manifest_text:
                self.fail(f"shards/manifest are stale; run {self.builder}")
        else:
            for path in existing:
                path.unlink()
            for index, part in enumerate(parts):
                (self.data / f"{self.prefix}.zlib.b64.part{index:02d}").write_text(part + "\n", encoding="utf-8")
            manifest_path.write_text(manifest_text, encoding="utf-8")
        print(f"{self.tag}_BANK_OK questions={manifest['questions']} topics={manifest['topics']} parts={manifest['parts']}")
