#!/usr/bin/env python3
"""Build the PrepLadder source-PDF glyph repair map.

The PrepLadder explanation PDFs were generated with non-embedded Helvetica (WinAnsi),
which has no subscript/superscript characters. The generator replaced every missing
character with a ZapfDingbats "I" glyph, which prints as a black box: "pCO■", "HCO■■",
"Na■". The characters are gone from the files, so no PDF renderer can show them.

This tool finds every such box with PyMuPDF (exact glyph box, baseline, font size and
the colour of the surrounding text), infers the intended character from the chemical
or physiological token it belongs to (CO■ -> CO₂, HCO■■ -> HCO₃⁻, Ca²■ -> Ca²⁺,
FEV■ -> FEV₁ ...) and writes app/src/main/assets/pdf_glyph_repairs.json. The web
renderer paints each repair over its box after PDF.js draws the page. Boxes whose
meaning is not certain from context are left untouched (counted as "unresolved").

  python3 tools/build_pdf_glyph_repairs.py          # writes the JSON, prints coverage
"""
import json, re, sys
from collections import Counter
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app/src/main/assets"
SOURCES = {"physiology": "Physiology_QBank_Source.pdf",
           "biochemistry": "Biochemistry_QBank_Source.pdf",
           "anatomy": "Anatomy_QBank_Source.pdf"}
BOX = "￼"  # placeholder for an unresolved box inside a line string

SUB = {"1": "₁", "2": "₂", "3": "₃", "4": "₄"}
ION_PLUS = {"Na", "K", "Li", "NADP", "NAD", "NH4", "H3O", "Ag"}
DIVALENT = re.compile(r"(Ca|Fe|Mg|Zn|Cu|Mn|Co|Ni|Ba|Sr|Hg|Pb|Cd)[²³]$")
O2_TOKENS = {"O", "PO", "pO", "PaO", "PAO", "PvO", "SaO", "SpO", "SvO", "VO", "CaO", "CvO", "FiO", "FIO"}
CO2_TOKENS = {"CO", "PCO", "pCO", "PaCO", "PACO", "PvCO", "PECO", "ETCO", "VCO", "tCO"}


def core_token(prefix):
    """The chemical token the box belongs to: text after the last space/delimiter."""
    p = prefix.rstrip(" ")  # "HCO3 ■" still belongs to HCO3
    return re.split(r"[\s(\[{/,;:=+\-–—•·]", p)[-1] if p else ""


def resolve(prefix, after):
    """Replacement for the first box of a run, given resolved text before it and raw text after it."""
    t = core_token(prefix)
    nxt = after[:1]
    # Word-internal losses seen in the sources (non-breaking hyphen, "fi" ligature, degree sign).
    if prefix.endswith("voltage") and after.startswith("gat"):
        return "-", "base"
    if prefix.endswith("strati") and after.startswith("ed"):
        return "fi", "base"
    if prefix.endswith("90") and after.startswith("clock"):
        return "°", "base"
    if prefix.endswith("[A") and after.startswith("]"):
        return "⁻", "sup"      # [A⁻], conjugate base
    if t.endswith("HCO3"):
        return "⁻", "sup"
    if t.endswith("H₂CO"):
        return "₃", "sub"
    if t.endswith("HCO₃"):
        return "⁻", "sup"
    if t.endswith("HCO"):
        return "₃", "sub"
    if t in CO2_TOKENS or t.endswith("CO") and t[:-2] in {"P", "p", "Pa", "PA", "Pv"}:
        return "₂", "sub"
    if t in O2_TOKENS:
        return "₂", "sub"
    if t == "H" or t.endswith("(H"):
        if after.startswith("CO"):
            return "₂", "sub"   # H₂CO₃
        if nxt == "O":
            return "₂", "sub"   # H₂O
        if not nxt.isalpha():
            return "⁺", "sup"   # H⁺
        return None
    if t == "Cl":
        return "⁻", "sup"
    if t in ION_PLUS:
        return "⁺", "sup"
    if DIVALENT.search(t):
        return "⁺", "sup"
    if t in {"FADH", "FMNH", "CONH", "-CONH"} or t.endswith("CONH"):
        return "₂", "sub"
    if t == "FEV":
        return "₁", "sub"
    if t == "NH" and after.startswith(BOX):
        return "₄", "sub"       # NH■■ -> NH₄⁺ (the second box resolves as NH4-like below)
    if t == "NH₄":
        return "⁺", "sup"
    return None


def line_items(line):
    """Flatten a PyMuPDF line into (char, is_box, char_dict, span) tuples."""
    out = []
    for s in line["spans"]:
        box = "Dingbat" in s["font"]
        for c in s["chars"]:
            if box and c["c"] != "I":
                out.append((c["c"], False, c, s))   # real dingbat (e.g. §-style marks): keep
            else:
                out.append((c["c"], box, c, s))
    return out


def text_style(items, i):
    """Font size, colour and baseline of the nearest real text left (else right) of a box."""
    for j in list(range(i - 1, -1, -1)) + list(range(i + 1, len(items))):
        ch, box, c, s = items[j]
        if not box and ch.strip():
            col = s["color"]
            return s["size"], "#%06x" % col, c["origin"][1]
    return 11.0, "#000000", items[i][2]["bbox"][3] - 2


def build():
    repairs, stats = {}, Counter()
    unresolved = Counter()
    for subject, name in SOURCES.items():
        doc = pymupdf.open(ASSETS / name)
        pages = {}
        for pno in range(len(doc)):
            for b in doc[pno].get_text("rawdict")["blocks"]:
                for line in b.get("lines", []):
                    items = line_items(line)
                    if not any(box for _, box, _, _ in items):
                        continue
                    text = [BOX if box else ch for ch, box, _, _ in items]
                    for i, (ch, box, c, s) in enumerate(items):
                        if not box:
                            continue
                        prefix = "".join(text[:i])
                        after = "".join(text[i + 1:])
                        res = resolve(prefix, after)
                        stats[subject + ":boxes"] += 1
                        if not res:
                            unresolved[(core_token(prefix)[-8:], after[:3])] += 1
                            continue
                        char, kind = res
                        text[i] = char
                        size, color, baseline = text_style(items, i)
                        # Cover the whole cell the fallback glyph may paint: from the box's left
                        # edge to the next character, over the full line height.
                        x0 = c["bbox"][0]
                        x1 = items[i + 1][2]["bbox"][0] if i + 1 < len(items) else c["bbox"][2]
                        x1 = max(x1, c["bbox"][2])
                        y0, y1 = line["bbox"][1], line["bbox"][3]
                        pages.setdefault(str(pno + 1), []).append(
                            [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2), char, kind,
                             round(size, 2), color, round(baseline, 2)])
                        stats[subject + ":repaired"] += 1
        repairs[subject] = pages
    return repairs, stats, unresolved


def main():
    repairs, stats, unresolved = build()
    out = ASSETS / "pdf_glyph_repairs.json"
    payload = {"version": 1,
               "about": "Box glyphs (ZapfDingbats 'I') in the PrepLadder source PDFs replaced by their intended characters. "
                        "Entry: [x0, y0, x1, y1, char, sub|sup, fontSize, color, baseline] in PDF points, top-left origin.",
               "subjects": repairs}
    out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for subject in SOURCES:
        print(f"{subject}: {stats[subject + ':repaired']}/{stats[subject + ':boxes']} boxes repaired")
    print(f"unresolved {sum(unresolved.values())}:", ", ".join(f"{k[0]!r}+{k[1]!r}×{v}" for k, v in unresolved.most_common(25)))
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
