#!/usr/bin/env python3
"""Read a PrepLadder "prep11" QBank PDF (First Prof, 2025 edition) into the
extraction schema the text banks import (tools/prepladder_text_bank.py).

The PDF prints every lesson twice: Part A (questions) and Part B (answer,
explanation, references). Each lesson opens "N.Title — Part A/B Quick Jump"
(long titles wrap, leaving "Quick Jump" or "Jump" on a line of its own) and
each question "Qn: stem (Qxxxxxx)". The PDF text is the source: its stems,
options, keys and figures. An outside extraction of the same PDF (Gemini,
master.jsonl) supplies only the lesson titles and sections, and must agree with
the PDF on every question's PrepLadder QID and key.

Characters the PDF could not print (Greek letters, sub- and superscripts,
arrows) it draws as one ZapfDingbats glyph each; they are read as PLACEHOLDER
and restored from their context by the subject's rules (`--glyphs`). A
placeholder no rule restores fails the run.

  python3 tools/prepladder_prep11_pdf.py <pdf> <gemini master.jsonl> <out.jsonl> <images-dir> --glyphs biochemistry

Needs PyMuPDF and Pillow. The output imports with
`tools/build_prepladder_<subject>_bank.py import <out.jsonl> <images-dir>`.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import io
import json
import re
import sys
from pathlib import Path

PLACEHOLDER = ""
SKIP = re.compile(r"^(@Neet_pg_bot|See Answer in Part B → Q\d+|↑ Back to this question in Part A|Q\d+ \(p\. \d+\)|Part [AB] — .*)$")
# Audio and contact links the later PDFs print under a question, behind an icon glyph.
LINKS = re.compile(r"^" + PLACEHOLDER + r"?\s*(Listen \((?:English|Hindi)\)|Listen to Audio \d*|Click here to contact the creator of this PDF|For queries & support: .*)$")
LESSON_HEAD = re.compile(r"(— Part [AB] Quick Jump|^(?:[AB] )?Quick Jump|^Jump)$")
# The PDF's own <img> tags leaked into a few explanations, after the image's alt text.
HTML = re.compile(r'(?:\s*[A-Za-z][\w-]*(?: [\w-]+)?)?\s*"\s*data-author="[^>]*/>')
CAPTION = re.compile(r"\s*(?:\(image\)\s*)?\{\{caption_text\}\}\s*")
# Gemini's notes that still hold for the PDF text; the rest describe its own extraction.
KEEP_FLAGS = ("answer_key_explanation_conflict", "source_pdf_explanation_truncated_or_placeholder")
MIN_FIGURE = 40  # px; smaller images are bullets and icons
# Some explanations open "Correct option: Option A. Heparin is…" or "Correct Answer C)
# Biotin Biotin is…". The lead goes, and the option's text with it only where it stands
# as a label (followed by punctuation, the end, or a new sentence), not where it opens
# the first sentence ("Heparin is…", "Thermogenin, also known as…").
ANSWER_LEAD = re.compile(r"^\s*correct\s+(?:answer|ans\.?|option)\s*[:\-–.]?\s*(?:is\s+)?(?:option\s*[:\-–.]?\s*)?"
                         r"[:\-–]?\s*\(?([A-F])\b\)?\s*[:\-–.)]?\s*", re.I)


def fail(message: str) -> None:
    raise SystemExit(f"PREP11_PDF_FAIL: {message}")


# --- PDF ------------------------------------------------------------------------

def tokens(doc):
    """('line', page, text, block) and ('img', page, figure) in reading order."""
    for pno in range(doc.page_count):
        for bi, block in enumerate(doc[pno].get_text("dict")["blocks"]):
            if block["type"] == 1:
                if block["width"] >= MIN_FIGURE and block["height"] >= MIN_FIGURE:
                    yield ("img", pno + 1, {"data": block["image"], "page": pno + 1})
                continue
            for line in block["lines"]:
                text = "".join(PLACEHOLDER * len(s["text"]) if s["font"] == "ZapfDingbats" else s["text"]
                               for s in line["spans"])
                yield ("line", pno + 1, text, (pno, bi))


def lesson_streams(doc) -> dict:
    part, lesson, prev, streams = None, None, [], {}
    for tok in tokens(doc):
        if tok[0] == "line":
            text = tok[2].strip()
            if text.startswith("Part A — All Questions"):
                part = "A"
            elif text.startswith("Part B — All Answers"):
                part = "B"
            if LESSON_HEAD.search(text):
                for back in [text] + prev[::-1]:
                    if m := re.match(r"^(\d+)\.", back):
                        lesson = int(m.group(1))
                        break
                prev = []
                streams.setdefault((part, lesson), [])
                continue
            prev = (prev + [text])[-4:]
        if part and lesson:
            streams.setdefault((part, lesson), []).append(tok)
    return streams


def cut_questions(stream: list) -> dict:
    qs, cur = {}, None
    for tok in stream:
        if tok[0] == "line" and (m := re.match(r"^Q(\d+): (.*)$", tok[2].strip())):
            cur = {"pages": [tok[1]], "toks": [("line", tok[1], m.group(2), tok[3])]}
            qs[int(m.group(1))] = cur
            continue
        if cur is not None:
            if tok[1] not in cur["pages"]:
                cur["pages"].append(tok[1])
            cur["toks"].append(tok)
    return qs


def paragraphs(lines: list) -> list[str]:
    """A new PDF text block starts a new paragraph."""
    out, last = [], None
    for text, block in lines:
        if not out or block != last:
            out.append(text.strip())
        else:
            out[-1] = (out[-1] + " " + text.strip()).strip()
        last = block
    return [re.sub(r"\s+", " ", p).strip() for p in out if p.strip()]


def parse(q: dict) -> dict:
    stage, stem, opts, cur, answer, expl, refs = "stem", [], {}, None, None, [], []
    figures = {"stem": [], "explanation": []}
    for tok in q["toks"]:
        if tok[0] == "img":
            where = "stem" if stage in ("stem", "options") else "explanation"
            figures[where].append({**tok[2], "para": len(paragraphs(expl))})
            continue
        text = tok[2].strip()
        if not text or SKIP.match(text) or LINKS.match(text):
            continue
        m = re.match(r"^#?\s*([A-F])\. (.*)$", text)  # "#" marks the keyed option
        if stage in ("stem", "options") and m and (stage == "options" or m.group(1) == "A"):
            stage, cur = "options", m.group(1)
            opts[cur] = m.group(2)
            continue
        if text.startswith("Correct Answer:"):
            # A few print no key ("Correct Answer:" blank or "Unknown"); the extraction's,
            # read from the explanation, stands in and the question is flagged.
            stage, answer = "answer", (re.match(r"Correct Answer:\s*([A-F])\b", text) or [None, ""])[1]
            continue
        if text.startswith("Explanation:"):
            stage, text = "explanation", text[len("Explanation:"):].strip()
            if not text:
                continue
        if text.startswith("References:"):
            stage, text = "refs", text[len("References:"):].strip()
        if stage == "stem":
            stem.append((text, tok[3]))
        elif stage == "options":
            opts[cur] += " " + text
        elif stage == "explanation":
            expl.append((text, tok[3]))
        elif stage == "refs":
            refs.append(text)
    stem_text = " ".join(paragraphs(stem))
    m = re.search(r"\s*\((Q\d{5,7})\)\s*$", stem_text)
    return {"qid": m.group(1) if m else None, "stem": stem_text[:m.start()].strip() if m else stem_text,
            "options": {k: re.sub(r"\s+", " ", v).strip() for k, v in opts.items()}, "answer": answer,
            "explanation": paragraphs(expl), "references": " ".join(refs).strip(" ,"), "figures": figures,
            "pages": q["pages"]}


def read_pdf(path: Path) -> dict:
    import pymupdf

    records: dict[str, dict] = {}
    for (part, lesson), stream in lesson_streams(pymupdf.open(path)).items():
        for number, q in cut_questions(stream).items():
            records.setdefault(f"{lesson}-{number}", {})[part] = parse(q)
    broken = [k for k, r in records.items() if set(r) != {"A", "B"} or r["B"]["answer"] is None]
    if broken:
        fail(f"questions missing a part or key: {broken[:5]}")
    return records


# --- extraction schema ----------------------------------------------------------

def save_jpeg(data: bytes, target: Path) -> None:
    from PIL import Image

    if target.exists():
        return
    image = Image.open(io.BytesIO(data))
    if image.mode in ("RGBA", "LA", "P"):
        image = image.convert("RGBA")
        white = Image.new("RGB", image.size, "white")
        white.paste(image, mask=image.split()[-1])
        image = white
    image.convert("RGB").save(target, "JPEG", quality=90)


def drop_answer_lead(text: str, options: dict) -> str:
    match = ANSWER_LEAD.match(text)
    if not match or match.group(1).upper() not in options:
        return text
    rest = text[match.end():]
    label = options[match.group(1).upper()].strip()
    # The label may carry its abbreviation: "Phenylketonuria (PKU): PKU is…".
    after = re.sub(r"^\s*\([^)]{1,30}\)(?=\s*[.:\-–])", "", rest[len(label):])
    if label and rest.lower().startswith(label.lower()) and re.match(r"^(?:\s*[.:\-–]|\s*$|\s+[A-Z])", after):
        rest = re.sub(r"^\s*[.:\-–]?\s*", "", after)
    return rest[:1].upper() + rest[1:]


def drop_key_tail(text: str, key_text: str) -> str:
    """The PDF cut some "Correct Option C - DNA replication: …" leads mid-label, leaving
    "replication: Mismatch repair: …"; a lower-case opening that is the keyed option's
    tail, followed by a colon, is what is left of the label."""
    words = key_text.rstrip(" .").split()
    for n in range(len(words) - 1, 0, -1):
        tail = " ".join(words[n:])
        if tail[:1].islower() and re.match(re.escape(tail) + r"\s*:\s*", text):
            rest = re.sub(re.escape(tail) + r"\s*:\s*", "", text, count=1)
            return rest[:1].upper() + rest[1:]
    return text


def extraction_text(row: dict) -> str:
    parts = [row["question_stem_structured"]["text"]] + [o["text"] for o in row["options"]]
    return "\n".join(parts + [json.dumps(block, ensure_ascii=False) for block in row["explanation_blocks"]])


def restore_from(text: str, reference: str) -> str:
    """Each placeholder run the subject's rules left, taken from the extraction's text of
    the same question where the same words (up to 14 before, 10 after) surround it."""
    def loose(part: str) -> str:
        return r"\s*".join(re.escape(c) for c in part if not c.isspace())

    for run in reversed(list(re.finditer(PLACEHOLDER + "+", text))):
        left = text[:run.start()].split(PLACEHOLDER)[-1][-14:]
        right = text[run.end():].split(PLACEHOLDER)[0][:10]
        if len(re.sub(r"\s", "", left + right)) < 6:
            continue
        if hit := re.search(loose(left) + r"\s*(.{0,3}?)\s*" + loose(right), reference):
            text = text[:run.start()] + hit.group(1) + text[run.end():]
    return text


def to_rows(records: dict, gemini: dict, fix, prefix: str, images: Path, pdf_name: str,
            align: bool = False) -> list[dict]:
    def clean(text: str) -> str:
        restored = fix(text, lambda t: restore_from(t, reference)) if align else fix(text)
        text = CAPTION.sub(" ", HTML.sub("", restored))
        # Bold runs end in a space before the punctuation that follows ("carboxylase , which").
        text = re.sub(r"\(\s+", "(", re.sub(r"(?<=[\w)])\s+(?=[,;)]|\.(?:\s|$))", "", text))
        return re.sub(r"\s+", " ", text).strip()

    if set(gemini) != set(records):
        fail(f"the PDF and the extraction disagree on the question set: {sorted(set(gemini) ^ set(records))[:5]}")
    images.mkdir(parents=True, exist_ok=True)
    rows = []
    for key in sorted(records, key=lambda k: tuple(map(int, k.split("-")))):
        a, b, g = records[key]["A"], records[key]["B"], gemini[key]
        reference = extraction_text(g)
        lesson, number = map(int, key.split("-"))
        if not a["qid"] == b["qid"] == g["prepladder_qid"] or b["answer"] not in ("", g["correct_option"]):
            fail(f"{key}: QID or key differs from the extraction")
        unkeyed = not b["answer"]
        if unkeyed:
            b["answer"] = g["correct_option"]
        # Options the PDF prints only inside a figure (or not at all) come from the
        # extraction, and the question is flagged.
        unprinted = sorted(b["options"]) != sorted(o["id"] for o in g["options"])
        if unprinted:
            b["options"] = {o["id"]: o["text"] for o in g["options"]}
        base = f"{prefix}_L{lesson:02d}_Q{number:03d}"
        imgs, placed = [], {}
        for n, fig in enumerate(a["figures"]["stem"], 1):
            save_jpeg(fig["data"], images / f"{base}_S{n}.jpg")
            imgs.append({"image_id": f"{base}_S{n}", "location": "question_stem", "caption": None,
                         "source_page": fig["page"], "table_id": None})
        for n, fig in enumerate(b["figures"]["explanation"], 1):
            save_jpeg(fig["data"], images / f"{base}_E{n}.jpg")
            imgs.append({"image_id": f"{base}_E{n}", "location": "explanation", "caption": None,
                         "source_page": fig["page"], "table_id": None})
            placed.setdefault(fig["para"], []).append(f"{base}_E{n}")
        paras, blocks = [clean(p) for p in b["explanation"]], []
        if paras:
            options = {k: clean(v) for k, v in b["options"].items()}
            paras[0] = drop_key_tail(drop_answer_lead(paras[0], options), options[b["answer"]])
            # A bare tail ("of Option D", "given above") is a fragment; ended with a stop, the
            # text bank recognises it as one and says the PDF prints no explanation.
            if re.fullmatch(r"[a-z][^.:]{0,40}", paras[0]):
                paras[0] += "."
        for i in range(len(paras) + 1):
            blocks += [{"type": "image", "image_id": image_id} for image_id in placed.get(i, [])]
            if i < len(paras) and re.search("[A-Za-z]{2}", paras[i]):
                blocks.append({"type": "text", "content": paras[i]})
        if refs := clean(b["references"]).strip(" ,."):
            blocks.append({"type": "text", "content": "References: " + refs})
        flags = [f for f in g["quality_flags"] if f.startswith(KEEP_FLAGS)]
        if unkeyed:
            flags.append("source_pdf_answer_key_missing: key taken from the explanation")
        if unprinted:
            flags.append("source_pdf_options_missing: options taken from the extraction")
        rows.append({
            "id": g["id"], "prepladder_qid": b["qid"], "module_index": lesson, "module_name": g["module_name"],
            "section_category": g["section_category"], "is_pyq_lesson": g["is_pyq_lesson"],
            "module_total_questions_in_app": g["module_total_questions_in_app"], "question_number": number,
            "question_stem_structured": {"text": clean(a["stem"]), "tables": []},
            "options": [{"id": k, "text": clean(v), "is_correct": k == b["answer"]} for k, v in sorted(b["options"].items())],
            "correct_option": b["answer"], "correct_options_list": [b["answer"]],
            "explanation_blocks": blocks, "images": imgs,
            "reviewStatus": "needs_review" if flags else "pass", "quality_flags": flags,
            "provenance": {"source_pdf": pdf_name, "question_pages": sorted(set(a["pages"])),
                           "explanation_pages": sorted(set(b["pages"]))},
        })
    left = sorted({r["id"] for r in rows if PLACEHOLDER in json.dumps(r, ensure_ascii=False)})
    if left:
        fail(f"{len(left)} questions keep an unrestored character, e.g. {left[:3]}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("gemini", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("images", type=Path)
    parser.add_argument("--glyphs", required=True, help="subject whose rules restore lost characters")
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    rules = importlib.import_module(f"prepladder_{args.glyphs}_glyphs")
    gemini = {f"{r['module_index']}-{r['question_number']}": r
              for r in map(json.loads, filter(str.strip, args.gemini.read_text(encoding="utf-8").splitlines()))}
    records = read_pdf(args.pdf)
    rows = to_rows(records, gemini, rules.fix, rules.PREFIX, args.images, args.pdf.name, getattr(rules, "ALIGN", False))
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    figures = sum(len(r["images"]) for r in rows)
    print(f"PREP11_PDF_OK questions={len(rows)} figures={figures} "
          f"sha256={hashlib.sha256(args.pdf.read_bytes()).hexdigest()[:16]}")


if __name__ == "__main__":
    main()
