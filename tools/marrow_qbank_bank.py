#!/usr/bin/env python3
"""Marrow QBank subjects imported from the Marrow web export (2026 edition).

Second Prof Pathology and Pharmacology, Third Prof (Community Medicine,
Forensic Medicine, Ophthalmology, ENT) and Final Prof subjects come from
`marrowqbank.html` through tools/marrow_qbank_import.py, which writes
data/marrow/qbank/<slug>/source.jsonl and the original figures. This builder
turns each subject into a `marrow-bank-1.0` record with ordered-block
explanations (the HTML's paragraphs, lists, tables and emphasis), writes its
hash-pinned shards, inventories the figures and releases them to the app.

Marrow Anatomy, Biochemistry, Physiology and Microbiology are separate banks
(tools/marrow_bank_data.py) and are not touched.

  python3 tools/marrow_qbank_bank.py            # rebuild every subject's shards + visuals.json
  python3 tools/marrow_qbank_bank.py --check    # fail if any shard or inventory is stale
  python3 tools/marrow_qbank_bank.py release    # copy figures to the app + runtime metadata
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import zlib
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QBANK = ROOT / "data/marrow/qbank"
ASSETS = ROOT / "app/src/main/assets"
RUNTIME = ASSETS / "marrow_qbank_visual_metadata.js"
SHARD_CHARS = 60000
SOURCE_LABEL = "Marrow QBank (web export, 2026)"


def r(a: int, b: int) -> list[int]:
    return list(range(a, b + 1))


# slug: export folder, app subject, ID code, prof group, expected counts and the
# study index (section, lessons). Pathology and Pharmacology sections are the
# extraction's `section_category` per lesson; the others group the export's
# lesson list by system, in export order, so lesson numbers stay the source's.
SUBJECTS: dict[str, dict] = {
    "pathology": {
        "folder": "6_Pathology", "subject": "Pathology", "code": "PATHO", "prof": "second",
        "expected": {"questions": 1371, "topics": 71},
        "index": [("General Pathology", r(1, 7)), ("Genetics and Pediatric Diseases", r(8, 10)),
                  ("Neoplasia", r(11, 13)), ("Immunopathology and Amyloidosis", r(14, 17)),
                  ("Hematopathology", r(18, 34)), ("Cardiovascular Pathology", r(35, 42)),
                  ("Renal and Urinary Tract Pathology", r(43, 46)),
                  ("Male and Female Genital Tract Pathology", r(47, 48)),
                  ("Hepatobiliary and Pancreatic Pathology", r(49, 52)),
                  ("Gastrointestinal Pathology", r(53, 57)), ("Respiratory Pathology", r(58, 60)),
                  ("Endocrine Pathology", r(61, 63)), ("Breast Pathology", [64]),
                  ("Musculoskeletal and Skin Pathology", r(65, 67)),
                  ("Central and Peripheral Nervous System Pathology", r(68, 71))],
    },
    "pharmacology": {
        "folder": "4_Pharmacology", "subject": "Pharmacology", "code": "PHARMA", "prof": "second",
        "expected": {"questions": 1275, "topics": 67},
        "index": [("General Pharmacology", r(1, 4)), ("Autonomic Nervous System", r(5, 9)),
                  ("Cardiovascular System", [10, 11, 12, 14, 15, 16]), ("Renal Pharmacology", [13, 17]),
                  ("Central Nervous System", r(18, 29)), ("Antimicrobials", r(30, 44)),
                  ("Endocrine Pharmacology", r(45, 53)), ("Autacoids and NSAIDs", r(54, 57)),
                  ("Hematology", r(58, 60)), ("Respiratory Pharmacology", [61]),
                  ("Gastrointestinal Pharmacology", r(62, 63)),
                  ("Anticancer and Immunomodulators", r(64, 67))],
    },
    "community-medicine": {
        "folder": "7_Community Medicine", "subject": "Community Medicine", "code": "PSM", "prof": "third",
        "expected": {"questions": 1319, "topics": 64},
        "index": [("Concepts of Health and Disease", r(1, 3)), ("Epidemiology", r(4, 9) + [13]),
                  ("Immunization and Disinfection", r(10, 12)), ("Communicable Diseases", r(14, 20)),
                  ("Non-Communicable Diseases", r(21, 22)), ("National Health Programmes", r(23, 25)),
                  ("Demography and Family Planning", r(26, 28)),
                  ("Preventive Obstetrics, Paediatrics and Geriatrics", [29]), ("Nutrition", r(30, 32)),
                  ("Social Sciences", r(33, 34)), ("Environment and Health", r(35, 41)),
                  ("Medical Entomology", r(42, 44)), ("Waste and Disaster Management", r(45, 46)),
                  ("Occupational Health", r(47, 48)), ("Health Education and Management", r(49, 50)),
                  ("Health Care in India and International Health", r(51, 53)), ("Biostatistics", r(54, 62)),
                  ("Mental Health and Genetics", r(63, 64))],
    },
    "forensic-medicine": {
        "folder": "8_Forensic Medicine", "subject": "Forensic Medicine", "code": "FMT", "prof": "third",
        "expected": {"questions": 436, "topics": 21},
        "index": [("Identification", r(1, 3)), ("Legal Procedures", [4]), ("Thanatology and Autopsy", r(5, 6)),
                  ("Injuries", r(7, 10)), ("Asphyxia", r(11, 12)), ("Sexual Offences and Child Abuse", r(13, 14)),
                  ("Toxicology", r(15, 21))],
    },
    "ophthalmology": {
        "folder": "9_Ophthalmology", "subject": "Ophthalmology", "code": "OPHTH", "prof": "third",
        "expected": {"questions": 633, "topics": 28},
        "index": [("Anatomy, Optics and Refraction", r(1, 4)), ("Conjunctiva, Sclera and Cornea", r(5, 8)),
                  ("Retina and Vitreous", r(9, 10)), ("Lens", r(11, 12)), ("Glaucoma", [13]), ("Uvea", r(14, 15)),
                  ("Lids, Lacrimal Apparatus and Orbit", r(16, 19)), ("Strabismus", r(20, 21)),
                  ("Neuro-ophthalmology", r(22, 23)), ("Ocular Tumors and Systemic Disease", [24, 26]),
                  ("Practical and Community Ophthalmology", [25, 27, 28])],
    },
    "ent": {
        "folder": "10_ENT", "subject": "ENT", "code": "ENT", "prof": "third",
        "expected": {"questions": 583, "topics": 38},
        "index": [("Ear", r(1, 12) + [15]), ("Facial Nerve", r(13, 14)), ("Hearing", r(16, 17)),
                  ("Nose and Paranasal Sinuses", r(18, 27)), ("Pharynx", r(28, 33)), ("Larynx", r(34, 37)),
                  ("Instruments", [38])],
    },
    "medicine": {
        "folder": "15_Medicine", "subject": "Medicine", "code": "MED", "prof": "final",
        "expected": {"questions": 1870, "topics": 104},
        "index": [("General Medicine", r(1, 2)), ("Endocrinology", r(3, 18)), ("Hepatology", r(19, 25)),
                  ("Gastroenterology", r(26, 32)), ("Rheumatology", r(33, 41)), ("Pulmonology", r(42, 49)),
                  ("Nephrology", r(50, 56)), ("Cardiology", r(57, 71)), ("Neurology", r(72, 86)),
                  ("Hematology", r(87, 98)), ("Infectious Diseases", r(99, 104))],
    },
    "surgery": {
        "folder": "16_Surgery", "subject": "Surgery", "code": "SURG", "prof": "final",
        "expected": {"questions": 1256, "topics": 54},
        "index": [("General Surgery", r(1, 3)), ("Paediatric Surgery", [4]), ("Trauma", r(5, 6) + [44]),
                  ("Breast", r(7, 11)), ("Endocrine Surgery", r(12, 15)), ("Gastrointestinal Surgery", r(16, 27)),
                  ("Hepatobiliary, Pancreas and Spleen", r(28, 37)), ("Urology", r(38, 43)),
                  ("Head and Neck", [45]), ("Burns, Wounds and Plastic Surgery", r(46, 48) + [54]),
                  ("Thoracic Surgery", [49]), ("Vascular Surgery", r(50, 53))],
    },
    "obstetrics-gynaecology": {
        "folder": "19_Obstetrics & Gynaecology", "subject": "Obstetrics & Gynaecology", "code": "OBG", "prof": "final",
        "expected": {"questions": 988, "topics": 47},
        "index": [("Basic Sciences", r(1, 5)), ("Normal Pregnancy", r(6, 9)), ("Labour and Puerperium", r(10, 16)),
                  ("Complications of Pregnancy", r(17, 23)), ("Medical Disorders in Pregnancy", r(24, 29)),
                  ("Gynaecology", r(30, 42)), ("Gynaecological Oncology", r(43, 46)), ("Instruments", [47])],
    },
    "paediatrics": {
        "folder": "18_Paediatrics", "subject": "Paediatrics", "code": "PEDS", "prof": "final",
        "expected": {"questions": 800, "topics": 39},
        "index": [("Neonatology", r(1, 4)), ("Growth and Development", r(5, 6)), ("Nutrition", r(7, 11)),
                  ("Genetics and Metabolic Disorders", r(12, 15)), ("Infectious Diseases", r(16, 18)),
                  ("Gastroenterology and Hepatology", r(19, 21)), ("Respiratory Disorders", r(22, 23)),
                  ("Cardiology", r(24, 26)), ("Nephrology and Urology", r(27, 28)), ("Neurology", [29]),
                  ("Endocrinology", r(30, 33)), ("Hemato-Oncology", r(34, 35) + r(38, 39)),
                  ("Musculoskeletal and Rheumatology", r(36, 37))],
    },
    "orthopaedics": {
        "folder": "17_Orthopaedics", "subject": "Orthopaedics", "code": "ORTHO", "prof": "final",
        "expected": {"questions": 501, "topics": 31},
        "index": [("Fractures: General Principles", r(1, 2)), ("Upper Limb", r(4, 7)), ("Lower Limb", r(8, 11)),
                  ("Spine and Pelvis", [3] + r(12, 15)), ("Bone and Joint Infections", r(16, 17)),
                  ("Paediatric Orthopaedics", r(18, 21)), ("Metabolic Bone Diseases", r(22, 23)),
                  ("Arthritis", r(24, 25)), ("Nerve Injuries", [26]), ("Bone Tumors", r(27, 28)),
                  ("Implants, Amputations and Sports Injuries", r(29, 31))],
    },
    "dermatology": {
        "folder": "12_Dermatology", "subject": "Dermatology", "code": "DERM", "prof": "final",
        "expected": {"questions": 510, "topics": 23},
        "index": [("Basics of Dermatology", r(1, 3)), ("Appendages and Pigmentation", r(4, 6)),
                  ("Dermatitis and Reactive Disorders", r(7, 9)), ("Papulosquamous and Bullous Disorders", r(10, 12)),
                  ("Infections", r(13, 17)), ("Sexually Transmitted Infections", r(18, 19)),
                  ("Genetic, Connective Tissue and Systemic Disorders", [20, 21, 23]), ("Skin Malignancies", [22])],
    },
    "psychiatry": {
        "folder": "13_Psychiatry", "subject": "Psychiatry", "code": "PSY", "prof": "final",
        "expected": {"questions": 432, "topics": 33},
        "index": [("Basics of Psychiatry", r(1, 5)), ("Psychotic Disorders", r(6, 7)),
                  ("Neurocognitive Disorders", r(8, 10)), ("Mood Disorders", r(11, 12)),
                  ("Substance Use Disorders", r(13, 14)), ("Anxiety, Somatic and Dissociative Disorders", r(15, 17) + r(19, 21)),
                  ("Personality Disorders", [18]), ("Sleep, Eating and Impulse Control Disorders", r(22, 24)),
                  ("Psychiatric Emergencies", [25]), ("Sexuality and Sexual Disorders", r(26, 27)),
                  ("Child and Adolescent Psychiatry", r(28, 32)), ("Forensic Psychiatry", [33])],
    },
    "radiology": {
        "folder": "14_Radiology", "subject": "Radiology", "code": "RADIO", "prof": "final",
        "expected": {"questions": 342, "topics": 21},
        "index": [("Basics of Radiology", r(1, 4)), ("Chest Imaging", r(5, 8)), ("Neuroimaging, Head and Neck", r(9, 12)),
                  ("Gastrointestinal and Hepatobiliary Imaging", r(13, 15)),
                  ("Genitourinary and Women's Imaging", r(16, 17)), ("Musculoskeletal Imaging", [18]),
                  ("Nuclear Medicine and Radiotherapy", r(19, 20)), ("Emergency and Interventional Radiology", [21])],
    },
    "anaesthesia": {
        "folder": "11_Anaesthesia", "subject": "Anaesthesia", "code": "ANAES", "prof": "final",
        "expected": {"questions": 549, "topics": 25},
        "index": [("Introduction and Preoperative Assessment", r(1, 2)), ("Monitoring", r(3, 4)),
                  ("Airway and Equipment", r(5, 8) + [11]), ("Resuscitation", r(9, 10)),
                  ("Muscle Relaxants", r(12, 13)), ("General Anaesthetics", r(14, 17)),
                  ("Local and Regional Anaesthesia", r(18, 22)),
                  ("Special Situations and Complications", r(23, 25))],
    },
}

PROF_TITLES = {"second": "Second Prof", "third": "Final Prof Part 1", "final": "Final Prof Part 2"}


def fail(message: str) -> None:
    raise SystemExit(f"MARROW_QBANK_FAIL: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- lesson titles --------------------------------------------------------------

ACRONYMS = {w.lower(): w for w in (
    "ACLS AIDS ALS APS ARDS AVN BLS BNS BNSS BSA CNS COPD CSOM CT CTEV CVS DVT ECG ENT ER ESI GCS GERD GI HIV "
    "IOLs IPHS IVDP JSY MEN MRI MTP N2O NACO NIS NLEP NSAIDs NTEP NVBDCP O2 PALS PNS RBSK SCFE SIADH SLE STDs "
    "TB VBAC ADH HAV HBV HCV DNA RNA CBC II III IV G6PD AML ANS OCPs").split()}
SMALL = {"and", "of", "the", "in", "on", "for", "to", "with", "a", "an", "or", "by", "at", "its", "as", "into"}
# The export spells a dash or slash as a run of spaces; these titles read wrong
# with the general rule and are written out.
TITLE_FIXES = {
    ("community-medicine", 36): "Water II - Disinfection of Water",
    ("community-medicine", 26): "Demography I - Demographic Cycle, Annual Growth Rate and Age Pyramid",
    ("community-medicine", 27): "Demography II - Demographic Indicators",
    ("community-medicine", 52): "Healthcare in India - IPHS 2022 Update",
    ("medicine", 99): "HIV/AIDS - Epidemiology and Clinical Features",
    ("medicine", 100): "HIV/AIDS - Management and Prophylaxis",
    ("medicine", 101): "COVID-19 - Epidemiology and Clinical Features",
    ("medicine", 102): "COVID-19 - Investigations",
    ("medicine", 103): "COVID-19 - Treatment",
    ("medicine", 104): "COVID-19 - Prophylaxis and Complications",
    ("medicine", 20): "Alcoholic Liver Disease and Non-Alcoholic Fatty Liver Disease",
    ("orthopaedics", 4): "Injuries of Clavicle, Shoulder and Arm",
    ("community-medicine", 35): "Water I - Sources and Purification of Water",
    ("community-medicine", 37): "Water III - Water Quality and Standards",
    ("pathology", 26): "Acute Lymphocytic Leukemia (ALL)",
    ("pathology", 69): "Degenerative, Toxic & Metabolic CNS Disorders",
}


def lesson_title(slug: str, lesson: int, raw: str) -> str:
    if (slug, lesson) in TITLE_FIXES:
        return TITLE_FIXES[(slug, lesson)]
    title = re.sub(r"\s{2,}", " - ", raw.strip())
    title = re.sub(r"\s*,\s*", ", ", title)

    def word(m: re.Match) -> str:
        w = m.group(0)
        low = w.lower()
        if low in ACRONYMS:
            return ACRONYMS[low]
        if m.start() and low in SMALL and title[max(0, m.start() - 2):m.start()] != "- ":
            return low
        return w
    title = re.sub(r"[A-Za-z0-9]+", word, title)
    return re.sub(r"(?<=\w)['’]S\b", lambda m: m.group(0)[0] + "s", title)


# --- explanation HTML -> ordered blocks ----------------------------------------

VOID = {"br", "col", "img", "hr", "wbr", "input", "meta", "link", "source"}
BLOCK = {"p", "div", "ul", "ol", "li", "table", "tbody", "thead", "tfoot", "tr", "td", "th", "h1", "h2", "h3",
         "h4", "h5", "h6", "blockquote", "section", "article", "dl", "dt", "dd", "colgroup", "caption", "figure", "pre"}
DROP = {"script", "style", "img", "colgroup", "col", "svg", "button"}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag: str, attrs: dict, parent: "Node | None"):
        self.tag, self.attrs, self.children, self.parent = tag, attrs, [], parent


class Tree(HTMLParser):
    """A forgiving DOM: unknown end tags are ignored, a block closes an open <p>."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {}, None)
        self.cur = self.root

    def open_tags(self):
        node, tags = self.cur, []
        while node is not None:
            tags.append(node.tag)
            node = node.parent
        return tags

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK and tag != "p" or tag == "p":
            # <p> cannot contain blocks: the browser closes it first.
            node = self.cur
            while node is not None and node.tag not in ("p",) and node.tag not in ("td", "th", "li", "root"):
                node = node.parent
            if node is not None and node.tag == "p":
                self.cur = node.parent
        if tag in ("li",) and self.cur.tag == "li":
            self.cur = self.cur.parent
        if tag in ("td", "th"):
            while self.cur.tag in ("td", "th") or (self.cur.tag not in ("tr", "table", "root") and "tr" in self.open_tags()):
                self.cur = self.cur.parent
        if tag == "tr":
            while self.cur.tag not in ("table", "tbody", "thead", "tfoot", "root") and "table" in self.open_tags():
                self.cur = self.cur.parent
        node = Node(tag, dict(attrs), self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        node = self.cur
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.tag != "root":
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(data)


LABEL = re.compile(r"(?:Other|Incorrect) options?\s*:|Explanation\s*:|Extra edge\s*:", re.I)
SCRIPT_TEXT = re.compile(r"^[A-Za-z0-9+\-−–,.()]{1,8}$")


def tidy(text: str) -> str:
    """Whitespace and emphasis markers: '**a **b' -> '**a** b', no empty or doubled runs."""
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    if text.count("**") % 2 == 0:
        # A bold run across a line break closes and reopens on each line.
        parts = text.split("**")
        text = "**".join(p.replace("\n", "**\n**") if n % 2 else p for n, p in enumerate(parts))
    for _ in range(3):
        text = text.replace("****", "")
        # Adjacent runs on one line merge; a line break between runs stays a break.
        text = re.sub(r"\*\*( *)\*\*", r"\1", text)
    # Move spaces that sit inside a bold run outside it.
    out = []
    parts = text.split("**")
    if len(parts) % 2 == 0:  # unbalanced: keep the words, drop the markers
        return re.sub(r" {2,}", " ", text.replace("**", "")).strip()
    for n, part in enumerate(parts):
        if n % 2 == 1:
            core = part.strip()
            if not core:
                out.append(part)
                continue
            lead = part[:len(part) - len(part.lstrip())]
            trail = part[len(part.rstrip()):]
            out.append(f"{lead}**{core}**{trail}")
        else:
            out.append(part)
    text = "".join(out)
    # A bold run of bare punctuation ("diverticulum**.**") is just the punctuation.
    text = re.sub(r"\*\*([^\w\s*]{1,3})\*\*", r"\1", text)
    text = re.sub(r" {2,}", " ", text)
    return "\n".join(line.strip() for line in text.split("\n")).strip()


class Converter:
    def __init__(self):
        self.tables: list[dict] = []
        self.qid = ""

    # inline text ---------------------------------------------------------------
    def inline(self, node, mode: str = "p") -> str:
        """Text of a subtree with ** for bold. mode 'cell' keeps line breaks and list bullets."""
        if isinstance(node, str):
            return node.replace("\n", " ")
        tag = node.tag
        if tag in DROP:
            return ""
        if tag == "br":
            return "\n"
        inner = "".join(self.inline(c, mode) for c in node.children)
        if tag in ("strong", "b"):
            return f"**{inner}**" if inner.strip() and "**" not in inner else inner
        if tag in ("em", "i"):
            return inner
        if tag in ("sub", "sup"):
            core = inner.strip()
            if SCRIPT_TEXT.match(core):
                return ("_{" if tag == "sub" else "^{") + core.replace("–", "-") + "}"
            return inner
        if tag == "li":
            return ("\n• " if mode == "cell" else " ") + inner.strip() + ("\n" if mode == "cell" else " ")
        if tag in BLOCK:
            return "\n" + inner + "\n"
        return inner

    def text(self, node, mode="p") -> str:
        return tidy(self.inline(node, mode))

    # blocks --------------------------------------------------------------------
    def convert(self, html: str, qid: str) -> tuple[list[dict], list[dict]]:
        self.tables, self.qid = [], qid
        tree = Tree()
        tree.feed(html)
        tree.close()
        blocks: list[dict] = []
        self.walk(tree.root, blocks)
        return [b for b in blocks if b], self.tables

    def paragraphs(self, buffer: list, blocks: list[dict]) -> None:
        if not buffer:
            return
        text = tidy("".join(buffer))
        buffer.clear()
        for line in text.split("\n"):
            line = line.strip()
            if not line or not re.search(r"[^\W_]", line):
                continue
            plain = line.replace("**", "").strip()
            if LABEL.fullmatch(plain):
                blocks.append({"type": "heading", "text": plain})
                continue
            # A short line that is one bold run is a section label.
            if (line.startswith("**") and line.endswith("**") and line.count("**") == 2
                    and len(re.findall(r"[^\W_]+", plain)) <= 8 and len(plain) <= 70):
                blocks.append({"type": "heading", "text": plain})
            else:
                blocks.append({"type": "paragraph", "text": line})

    def walk(self, node: Node, blocks: list[dict]) -> None:
        buffer: list[str] = []
        for child in node.children:
            if isinstance(child, str) or (child.tag not in BLOCK and child.tag != "br"):
                buffer.append(self.inline(child))
                continue
            if child.tag == "br":
                buffer.append("\n")
                continue
            self.paragraphs(buffer, blocks)
            tag = child.tag
            if tag in DROP:
                continue
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                text = self.text(child).replace("**", "").replace("\n", " ").strip()
                if text:
                    blocks.append({"type": "heading", "text": text} if len(re.findall(r"[^\W_]+", text)) <= 8
                                  else {"type": "paragraph", "text": f"**{text}**"})
            elif tag in ("ul", "ol"):
                self.bullets(child, blocks)
            elif tag == "table":
                self.table(child, blocks)
            elif tag == "li":  # a stray item outside a list
                text = self.text(child, "li").replace("\n", " ")
                if text:
                    blocks.append({"type": "paragraph", "text": text})
            else:
                self.walk(child, blocks)
        self.paragraphs(buffer, blocks)

    def items(self, node: Node, depth: int) -> list[dict]:
        out = []
        for li in node.children:
            if isinstance(li, str):
                if li.strip():
                    out.append({"text": tidy(li)})
                continue
            if li.tag in ("ul", "ol"):  # a list nested straight in a list
                sub = self.items(li, depth + 1)
                if out and depth == 0:
                    out[-1].setdefault("items", []).extend(s for s in sub)
                else:
                    out.extend(sub)
                continue
            if li.tag != "li":
                text = tidy(self.inline(li, "li")).replace("\n", " ")
                if text:
                    out.append({"text": text})
                continue
            own = [c for c in li.children if isinstance(c, str) or c.tag not in ("ul", "ol")]
            text = tidy("".join(self.inline(c, "li") for c in own)).replace("\n", " ").strip()
            children = []
            for c in li.children:
                if not isinstance(c, str) and c.tag in ("ul", "ol"):
                    children.extend(self.items(c, depth + 1))
            # One level of sub-items: deeper levels join the sub-list in order.
            flat = []
            for c in children:
                flat.append({"text": c["text"]})
                flat.extend({"text": g["text"]} for g in c.get("items", []))
            if not text and flat:
                text, flat = flat[0]["text"], flat[1:]
            if not text:
                continue
            item = {"text": text}
            if flat:
                item["items"] = flat
            out.append(item)
        return [o for o in out if re.search(r"[^\W_]", o["text"])]

    def bullets(self, node: Node, blocks: list[dict]) -> None:
        items = self.items(node, 0)
        if not items:
            return
        block = {"type": "bullets", "ordered": node.tag == "ol", "items": items}
        start = node.attrs.get("start")
        if block["ordered"] and start and start.isdigit() and int(start) > 1:
            block["start"] = int(start)
        blocks.append(block)

    def table(self, node: Node, blocks: list[dict]) -> None:
        rows: list[list[str]] = []
        heads: list[bool] = []

        def collect(n: Node):
            for c in n.children:
                if isinstance(c, str):
                    continue
                if c.tag == "tr":
                    cells, header = [], True
                    for cell in c.children:
                        if isinstance(cell, str) or cell.tag not in ("td", "th"):
                            continue
                        text = self.text(cell, "cell")
                        text = "\n".join(l.strip() for l in text.split("\n") if l.strip())
                        bare = text.replace("**", "").strip()
                        header = header and (cell.tag == "th" or not bare or text.replace("**", "") != text and
                                             re.fullmatch(r"(\*\*[^*]+\*\*\s*)+", text) is not None)
                        span = cell.attrs.get("colspan") or "1"
                        span = int(span) if span.isdigit() and 0 < int(span) <= 12 else 1
                        cells.append(bare if (cell.tag == "th") else text)
                        cells.extend([""] * (span - 1))
                    if any(x.strip() for x in cells):
                        rows.append(cells)
                        heads.append(header)
                elif c.tag in ("thead", "tbody", "tfoot"):
                    collect(c)
                elif c.tag == "table":  # nested table: read it as its own table
                    self.table(c, blocks)
        collect(node)
        if not rows:
            return
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        title = ""
        # A first row that is one spanning cell over a wider table is the title.
        if width > 1 and len(rows) > 1 and sum(1 for x in rows[0] if x.strip()) == 1 and rows[0][0].strip():
            title = rows[0][0].replace("**", "").replace("\n", " ").strip()
            rows, heads = rows[1:], heads[1:]
        if width == 1:
            # A one-column table is a boxed list of lines.
            lines = [l for r in rows for l in r[0].split("\n") if l.strip()]
            if title:
                blocks.append({"type": "heading", "text": title})
            for line in lines:
                self.paragraphs([line], blocks)
            return
        if len(rows) > 1 and heads[0]:
            columns, body = [c.replace("**", "") for c in rows[0]], rows[1:]
        else:
            columns, body = [""] * width, rows
        table_id = f"{self.qid}_T{len(self.tables) + 1}"
        self.tables.append({"table_id": table_id, "title": title, "columns": columns, "rows": body})
        blocks.append({"type": "table", "table_id": table_id})


def plain_text(blocks: list[dict], tables: dict[str, dict]) -> str:
    out = []
    for b in blocks:
        if b["type"] in ("paragraph", "heading"):
            out.append(b["text"])
        elif b["type"] == "bullets":
            lines = []
            for n, item in enumerate(b["items"], b.get("start", 1)):
                lines.append((f"{n}. " if b["ordered"] else "• ") + item["text"])
                lines.extend("• " + c["text"] for c in item.get("items", []))
            out.append("\n".join(lines))
        elif b["type"] == "table":
            t = tables[b["table_id"]]
            lines = [t["title"]] if t["title"] else []
            if any(t["columns"]):
                lines.append(" | ".join(t["columns"]))
            lines.extend(" | ".join(c.replace("\n", "; ") for c in row) for row in t["rows"])
            out.append("\n".join(lines))
    return "\n\n".join(x for x in out if x.strip())


STEM_HTML = re.compile(r"</?(?:p|div|span|ul|ol|li|table|tr|td|th|br|strong|b|em|i|sub|sup)\b[^>]*>", re.I)


def unescape(text: str) -> str:
    """Entities, however many times the export escaped them ('D&amp;gt;E' -> 'D>E')."""
    for _ in range(4):
        plain = html.unescape(text)
        if plain == text:
            break
        text = plain
    return text.replace("\xa0", " ")


def stem(raw: str, converter: Converter, table_prefix: str) -> tuple[str, list[dict]]:
    """A stem as display text (one line per paragraph or list item) and its tables.

    Stems are shown as plain text, so emphasis markers are dropped; a table in the
    stem (match the following) becomes a stemTables entry under the text."""
    if not STEM_HTML.search(raw):
        lines = [re.sub(r"[ \t]+", " ", unescape(l)).strip() for l in raw.split("\n")]
        return "\n".join(l for l in lines if l), []
    blocks, tables = converter.convert(raw, table_prefix)
    by_id = {t["table_id"]: t for t in tables}
    lines, stem_tables = [], []
    flat = lambda s: unescape(s.replace("**", "")).strip()
    for b in blocks:
        if b["type"] in ("paragraph", "heading"):
            lines.append(flat(b["text"]))
        elif b["type"] == "bullets":
            for n, item in enumerate(b["items"], b.get("start", 1)):
                lines.append((f"{n}. " if b["ordered"] else "• ") + flat(item["text"]))
                lines.extend("   • " + flat(c["text"]) for c in item.get("items", []))
        elif b["type"] == "table":
            t = by_id[b["table_id"]]
            columns, rows = [flat(c) for c in t["columns"]], [[flat(c) for c in r] for r in t["rows"]]
            if not any(columns) and len(rows) > 1:
                columns, rows = rows[0], rows[1:]
            # Match lists come as label/text column pairs ("1." | "Coal dust" | "a." | "Byssinosis"),
            # with the header on either column: each pair is one column.
            label = lambda v: not v or re.fullmatch(r"\w{1,3}[.)]?", v) is not None
            pairs = range(0, len(columns), 2)
            if (len(columns) % 2 == 0 and len(columns) > 2
                    and all(all(label(r[i]) for r in rows) and not (columns[i] and columns[i + 1]) for i in pairs)):
                columns = [columns[i] or columns[i + 1] for i in pairs]
                rows = [[f"{r[i]} {r[i + 1]}".strip() for i in pairs] for r in rows]
            if t["title"]:
                lines.append(flat(t["title"]))
            stem_tables.append({"columns": columns, "rows": rows})
    return "\n".join(l for l in lines if l), stem_tables


# --- bank record ----------------------------------------------------------------

def load_source(slug: str) -> list[dict]:
    path = QBANK / slug / "source.jsonl"
    if not path.exists():
        fail(f"{slug}: {path.relative_to(ROOT)} missing; run tools/marrow_qbank_import.py")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def pending_figures(slug: str) -> dict[str, list[str]]:
    """Questions held back because an original figure could not be downloaded yet.

    data/marrow/qbank/pending_figures.json names each figure. A listed file that
    has since arrived fails the build, so the ledger cannot outlive the gap."""
    path = QBANK / "pending_figures.json"
    held: dict[str, list[str]] = {}
    if not path.exists():
        return held
    for entry in json.loads(path.read_text(encoding="utf-8"))["figures"]:
        if entry["subject"] != slug:
            continue
        if any((QBANK / slug / "visuals").glob(f"{entry['figure']}.*")):
            fail(f"{slug}: {entry['figure']} has arrived; remove it from pending_figures.json")
        held.setdefault(entry["qid"], []).append(entry["figure"])
    return held


def content(q: dict) -> str:
    return json.dumps([q["question"], q["options"], q["explanationHtml"], [i["url"] for i in q["images"]]])


def topic_id(slug: str, lesson: int) -> str:
    return f"marrow-{slug}-{lesson}"


def normalize(slug: str, rows: list[dict] | None = None) -> dict:
    cfg = SUBJECTS[slug]
    rows = load_source(slug) if rows is None else rows
    code, subject = cfg["code"], cfg["subject"]
    order = [k for _, lessons in cfg["index"] for k in lessons]
    section_of = {k: name for name, lessons in cfg["index"] for k in lessons}
    lessons: dict[int, dict] = {}
    questions, seen, converter = [], {}, Converter()
    held = pending_figures(slug)
    for q in rows:
        qid, lesson = q["qid"], int(q["lesson"])
        if not re.fullmatch(r"M[A-Z]\d{4}", qid):
            fail(f"{slug}: blank or malformed Marrow QID {qid!r}")
        # Marrow files one question under two lessons now and then; the repeat
        # keeps its place with a lesson-suffixed ID. A repeat that differs fails.
        app_id = f"marrow__{code}_{qid}"
        if qid in seen:
            if content(seen[qid]) != content(q):
                fail(f"{slug}: QID {qid} appears twice with different content")
            app_id += f"_L{lesson}"
        else:
            seen[qid] = q
        topic = lessons.setdefault(lesson, {
            "id": topic_id(slug, lesson), "subject": subject, "bank": "Marrow",
            "title": lesson_title(slug, lesson, q["lessonTitle"]), "section": section_of.get(lesson),
            "sourceTestId": q["testId"], "count": 0,
        })
        topic["source"] = topic.get("source", 0) + 1
        if int(q["number"]) != topic["source"]:
            fail(f"{qid}: question numbers in lesson {lesson} are not contiguous")
        for image in q["images"]:
            missing = not (QBANK / slug / "visuals" / image["file"]).exists()
            if missing and Path(image["file"]).stem not in held.get(qid, []):
                fail(f"{qid}: figure {image['file']} is missing and not in pending_figures.json")
        if qid in held:
            continue
        topic["count"] += 1
        letters = [o["letter"] for o in q["options"]]
        if letters != ["A", "B", "C", "D"]:
            fail(f"{qid}: options must be exactly A-D, got {letters}")
        keyed = [i for i, o in enumerate(q["options"], 1) if o["correct"]]
        if len(keyed) != 1:
            fail(f"{qid}: {len(keyed)} options are keyed correct")
        key = keyed[0]
        answer = q["options"][key - 1]
        if not q["correctAnswer"].startswith(f"{answer['letter']}."):
            fail(f"{qid}: correct_answer {q['correctAnswer']!r} disagrees with the keyed option")
        if not q["question"] or any(not o["text"] for o in q["options"]):
            fail(f"{qid}: blank stem or option")
        question, stem_tables = stem(q["question"], converter, f"{code}_{qid}_S")
        options = [{"letter": o["letter"], "text": unescape(o["text"]).strip()} for o in q["options"]]
        if not question or any(not o["text"] or STEM_HTML.search(o["text"]) for o in options):
            fail(f"{qid}: blank stem or option, or markup left in an option")
        blocks, tables = converter.convert(q["explanationHtml"], f"{code}_{qid}")
        if not blocks:
            blocks = [{"type": "paragraph", "text": "No explanation is given for this question in the source."}]
        table_map = {t["table_id"]: t for t in tables}
        text = plain_text(blocks, table_map)
        stem_figures = [i for i in q["images"] if i["role"] == "question"]
        record = {
            "id": app_id,
            "sourceQuestionId": qid,
            "mcqId": qid,
            "subject": subject,
            "bank": "Marrow",
            "chapterId": topic["id"],
            "chapter": topic["title"],
            "questionNumber": int(q["number"]),
            "questionType": "single_best_answer",
            "question": question,
            "options": options,
            "correctOption": key,
            "correctAnswerText": options[key - 1]["text"],
            "explanationFormat": "structured",
            "explanation": text,
            "structuredExplanation": {"layout": "ordered-blocks", "text": text, "blocks": blocks,
                                      "tables": tables, "figures": [i["file"] for i in q["images"]]},
            "provenance": {"sourceFile": "marrowqbank.html", "sourceLabel": SOURCE_LABEL,
                           "sourceTestId": q["testId"]},
            "reviewStatus": "pass",
            "imageDependent": bool(stem_figures),
        }
        if stem_tables:
            record["stemTables"] = stem_tables
        questions.append(record)
    if sorted(lessons) != list(range(1, len(lessons) + 1)) or sorted(order) != sorted(lessons):
        fail(f"{slug}: the study index must list every lesson once "
             f"(missing {sorted(set(lessons) - set(order))}, unknown {sorted(set(order) - set(lessons))})")
    topics = []
    for k in order:
        t = lessons[k]
        count = t.pop("count")
        source = t.pop("source")
        topics.append({**t, "questionCount": count, "sourceQuestionTotal": source, "complete": count == source})
    position = {t["id"]: n for n, t in enumerate(topics)}
    questions.sort(key=lambda r: (position[r["chapterId"]], r["questionNumber"]))
    record = {
        "schema_version": "marrow-bank-1.0", "subject": subject, "bank": "Marrow", "prof": cfg["prof"],
        "scope": f"lessons_001_{len(topics):03d}",
        "stats": {"questions": len(questions), "topics": len(topics),
                  "completeTopics": sum(t["complete"] for t in topics), "heldForFigures": sorted(held)},
        "topics": topics, "questions": questions,
    }
    counts = {"questions": len(questions) + len(held), "topics": len(topics)}
    if counts != cfg["expected"]:
        fail(f"{slug}: expected {cfg['expected']}, built {counts} (held {len(held)})")
    return record


def prefix(slug: str) -> str:
    return f"{slug.replace('-', '_')}_marrow_qbank"


def shard(slug: str, record: dict) -> tuple[list[str], dict]:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    parts = [encoded[i:i + SHARD_CHARS] for i in range(0, len(encoded), SHARD_CHARS)]
    source = (QBANK / slug / "source.jsonl").read_bytes()
    return parts, {
        "schema_version": "1.0", "subject": record["subject"], "bank": "Marrow", "scope": record["scope"],
        "source": f"data/marrow/qbank/{slug}/source.jsonl", "sourceSha256": sha256(source),
        "builder": "tools/marrow_qbank_bank.py", "topics": len(record["topics"]),
        "questions": len(record["questions"]), "parts": len(parts), "base64_chars": len(encoded),
        "compressed_bytes": len(compressed), "compressed_sha256": sha256(compressed),
        "raw_bytes": len(raw), "raw_sha256": sha256(raw),
        "topicCounts": {t["id"]: t["questionCount"] for t in record["topics"]},
    }


def app_record(slug: str) -> dict:
    """The hash-verified bank, as embedded in MARROW_DATA.records."""
    folder = QBANK / slug
    manifest = json.loads((folder / f"{prefix(slug)}_manifest.json").read_text(encoding="utf-8"))
    parts = sorted(folder.glob(f"{prefix(slug)}.zlib.b64.part*"))
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    if len(parts) != manifest["parts"] or len(encoded) != manifest["base64_chars"]:
        fail(f"{slug}: shards do not match the manifest")
    compressed = base64.b64decode(encoded, validate=True)
    if sha256(compressed) != manifest["compressed_sha256"]:
        fail(f"{slug}: compressed SHA-256 mismatch")
    raw = zlib.decompress(compressed)
    if sha256(raw) != manifest["raw_sha256"]:
        fail(f"{slug}: raw SHA-256 mismatch")
    record = json.loads(raw)
    counts = {"questions": len(record["questions"]) + len(record["stats"]["heldForFigures"]), "topics": len(record["topics"])}
    if counts != SUBJECTS[slug]["expected"] or record["bank"] != "Marrow" or record["subject"] != SUBJECTS[slug]["subject"]:
        fail(f"{slug}: unexpected bank identity or counts {counts}")
    return record


def app_records() -> list[dict]:
    return [app_record(slug) for slug in SUBJECTS]


# --- figures --------------------------------------------------------------------

def image_size(data: bytes) -> tuple[int, int]:
    from PIL import Image  # noqa: PLC0415 (only the inventory step reads pixels)
    import io
    with Image.open(io.BytesIO(data)) as im:
        return im.size


def inventory(slug: str, record: dict) -> dict:
    """Every figure the subject uses, with its hash and size. Files are the originals."""
    folder = QBANK / slug
    path = folder / "visuals.json"
    previous = {}
    if path.exists():
        previous = {f["file"]: f for f in json.loads(path.read_text(encoding="utf-8"))["figures"]}
    images_of = {row["qid"]: row["images"] for row in load_source(slug)}
    figures = []
    for q in record["questions"]:
        for image in images_of[q["sourceQuestionId"]]:
            rel = f"data/marrow/qbank/{slug}/visuals/{image['file']}"
            data = (ROOT / rel).read_bytes()
            digest = sha256(data)
            old = previous.get(rel)
            width, height = (old["width"], old["height"]) if old and old["sha256"] == digest else image_size(data)
            figures.append({"questionId": q["id"], "role": image["role"], "order": image["order"],
                            "file": rel, "sha256": digest, "bytes": len(data), "width": width, "height": height,
                            "sourceUrl": image["url"]})
    used = {Path(f["file"]).name for f in figures}
    held = set(pending_figures(slug))
    stray = sorted(p.name for p in (folder / "visuals").iterdir()
                   if p.name not in used and p.name.split("_")[0] not in held)
    if stray:
        fail(f"{slug}: figure files no question uses: {stray[:5]}")
    return {"schemaVersion": 1, "subject": record["subject"], "bank": "Marrow",
            "note": "Original files as served by the Marrow web export; never re-encoded.", "figures": figures}


def release() -> None:
    """Copy every figure to app/src/main/assets/marrow_visuals/<sha256>.<ext> and write the runtime metadata."""
    runtime: dict[str, list[dict]] = {}
    total = 0
    for slug, cfg in SUBJECTS.items():
        value = json.loads((QBANK / slug / "visuals.json").read_text(encoding="utf-8"))
        for figure in value["figures"]:
            data = (ROOT / figure["file"]).read_bytes()
            if sha256(data) != figure["sha256"]:
                fail(f"figure changed since inventory: {figure['file']}")
            rel = f"marrow_visuals/{figure['sha256']}{Path(figure['file']).suffix}"
            target = ASSETS / rel
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            n = figure["order"]
            runtime.setdefault(figure["questionId"], []).append({
                "id": f"marrow-qbank-{Path(figure['file']).stem}", "role": figure["role"], "order": n,
                "src": rel, "alt": f"{cfg['subject']} {'question' if figure['role'] == 'question' else 'explanation'} figure {n}",
                "status": "PASS", "width": figure["width"], "height": figure["height"],
            })
            total += 1
    payload = json.dumps(runtime, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")
    RUNTIME.write_text("/* Marrow QBank figures (generated by tools/marrow_qbank_bank.py). */\n"
                       f"window.MARROW_VISUALS=Object.assign(window.MARROW_VISUALS||{{}},{payload});\n", encoding="utf-8")
    print(f"MARROW_QBANK_VISUALS_OK questions={len(runtime)} figures={total}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", choices=["build", "release"], default="build")
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.command == "release":
        release()
        return
    stale = []
    for slug in args.slugs or list(SUBJECTS):
        folder = QBANK / slug
        record = normalize(slug)
        parts, manifest = shard(slug, record)
        outputs = {f"{prefix(slug)}.zlib.b64.part{i:02d}": p + "\n" for i, p in enumerate(parts)}
        outputs[f"{prefix(slug)}_manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        outputs["visuals.json"] = json.dumps(inventory(slug, record), ensure_ascii=False, indent=1) + "\n"
        existing = {p.name for p in folder.glob(f"{prefix(slug)}.zlib.b64.part*")}
        if args.check:
            if existing != {n for n in outputs if ".part" in n} or any(
                    not (folder / n).exists() or (folder / n).read_text(encoding="utf-8") != text
                    for n, text in outputs.items()):
                stale.append(slug)
        else:
            for name in existing - set(outputs):
                (folder / name).unlink()
            for name, text in outputs.items():
                (folder / name).write_text(text, encoding="utf-8")
        print(f"MARROW_QBANK_BANK_OK {slug} questions={manifest['questions']} topics={manifest['topics']} "
              f"parts={manifest['parts']} figures={sum(len(q['structuredExplanation']['figures']) for q in record['questions'])}")
    if stale:
        fail(f"stale shards or inventory for {stale}; run tools/marrow_qbank_bank.py")


if __name__ == "__main__":
    main()
