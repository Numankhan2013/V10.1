#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAX = ROOT / "data" / "marrow" / "topic_index_taxonomy.json"
TEST = ROOT / "tools" / "test_marrow_topic_taxonomy.py"
BROWSER = ROOT / "tools" / "verify_marrow_bank_browser.py"
DOC = ROOT / "docs" / "MARROW_TOPIC_INDEX_TAXONOMY.md"
STATE = ROOT / ".project-memory" / "STATE.md"

SECTION_ORDER = [
    "Carbohydrates",
    "Amino acids and proteins",
    "Lipids",
    "Enzymes and phenylketonuria",
    "Clinical biochemistry and nutrition",
    "Genetics",
]
PLANNED = {
    "Carbohydrates": [
        "Chemistry of carbohydrates",
        "Amino sugars and mucopolysaccharides",
        "Glycolysis and gluconeogenesis",
        "Glycogen metabolism and glycogen storage disorders",
        "HMP shunt pathway",
        "Fructose and galactose metabolism",
        "ETC and bioenergetics",
        "Krebs cycle",
    ],
    "Amino acids and proteins": [
        "Amino acid basics",
        "Amino acid metabolism",
        "Amino acid metabolic disorder",
        "Protein structure and function",
        "Urea cycle and its disorders",
    ],
    "Lipids": [
        "Lipid basics",
        "Fatty acid oxidation and ketogenesis",
        "Biosynthesis of fatty acids and eicosanoids",
        "Metabolism of acylglycerols and sphingolipids",
        "Cholesterol synthesis, transport, and excretion",
    ],
    "Enzymes and phenylketonuria": [
        "Phenylketonuria and bile pigments",
        "Enzyme mechanism of action and clinical importance",
        "Enzyme kinetics and regulation of activity",
    ],
    "Clinical biochemistry and nutrition": [
        "Fats",
        "Soluble vitamins",
        "Energy-releasing vitamins",
        "Hematopoietic and other vitamins",
        "Antioxidants and minerals",
    ],
    "Genetics": [
        "Basics of genetics",
        "Nucleotide metabolism and disorders",
        "DNA organization, replication, and repair",
        "RNA synthesis, processing, and modification",
        "Regulation of gene expression",
        "Molecular genetics and recombinant DNA and genomic technology",
    ],
}
SLUGS = {
    "Carbohydrates": "carbohydrates",
    "Amino acids and proteins": "amino-acids-and-proteins",
    "Lipids": "lipids",
    "Enzymes and phenylketonuria": "enzymes-and-phenylketonuria",
    "Clinical biochemistry and nutrition": "clinical-biochemistry-and-nutrition",
    "Genetics": "genetics",
}

# Current source chapters stay source-faithful; only learner placement metadata changes.
MAPPING = {
    "1": ("Carbohydrates", ["carbohydrates:01", "carbohydrates:02"]),
    "2": ("Carbohydrates", ["carbohydrates:03"]),
    "3": ("Carbohydrates", ["carbohydrates:04"]),
    "4": ("Carbohydrates", ["carbohydrates:05", "carbohydrates:06"]),
    "5": ("Carbohydrates", ["carbohydrates:07"]),
    "6": ("Carbohydrates", ["carbohydrates:08"]),
    "7": ("Amino acids and proteins", ["amino-acids-and-proteins:01"]),
    "8": ("Amino acids and proteins", ["amino-acids-and-proteins:02"]),
    "9": ("Amino acids and proteins", ["amino-acids-and-proteins:03"]),
    "10": ("Amino acids and proteins", ["amino-acids-and-proteins:04"]),
    "11": ("Amino acids and proteins", ["amino-acids-and-proteins:05"]),
    "12": ("Lipids", ["lipids:01"]),
    "13": ("Lipids", ["lipids:02"]),
    "14": ("Lipids", ["lipids:03"]),
    "15": ("Lipids", ["lipids:04"]),
    "16": ("Lipids", ["lipids:05"]),
    "17": ("Enzymes and phenylketonuria", ["enzymes-and-phenylketonuria:01"]),
    "18": ("Enzymes and phenylketonuria", ["enzymes-and-phenylketonuria:02"]),
    "19": ("Enzymes and phenylketonuria", ["enzymes-and-phenylketonuria:03"]),
    "20": ("Clinical biochemistry and nutrition", ["clinical-biochemistry-and-nutrition:01", "clinical-biochemistry-and-nutrition:02"]),
    "21": ("Clinical biochemistry and nutrition", ["clinical-biochemistry-and-nutrition:03"]),
    "22": ("Clinical biochemistry and nutrition", ["clinical-biochemistry-and-nutrition:04"]),
    "23": ("Clinical biochemistry and nutrition", ["clinical-biochemistry-and-nutrition:05"]),
    "24": ("Genetics", ["genetics:01", "genetics:02"]),
    "25": ("Genetics", ["genetics:03"]),
    "26": ("Genetics", ["genetics:04"]),
}


def apply_taxonomy() -> None:
    data = json.loads(TAX.read_text(encoding="utf-8"))
    current = data["subjects"]["Biochemistry"]["topics"]
    assert [str(x["id"]) for x in current] == [str(i) for i in range(1, 27)]
    planned_index = []
    for title in SECTION_ORDER:
        slug = SLUGS[title]
        planned_index.append({
            "id": slug,
            "title": title,
            "topics": [
                {"slot": f"{slug}:{i:02d}", "title": topic}
                for i, topic in enumerate(PLANNED[title], 1)
            ],
        })
    configured = []
    for item in current:
        ident = str(item["id"])
        section, slots = MAPPING[ident]
        configured.append({
            "id": ident,
            "title": item["title"],
            "section": section,
            "plannedSlots": slots,
        })
    data["subjects"]["Biochemistry"] = {
        "catalogVersion": 2,
        "sectionOrder": SECTION_ORDER,
        "displayNumbering": "visible-contiguous",
        "plannedIndex": planned_index,
        "topics": configured,
    }
    TAX.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")


def patch_test() -> None:
    s = TEST.read_text(encoding="utf-8")
    if "BIOCHEM_SECTION_ORDER = [" not in s:
        marker = "\n\ndef load_bank(prefix: str) -> dict:\n"
        block = '''\n\nBIOCHEM_SECTION_ORDER = [\n    "Carbohydrates",\n    "Amino acids and proteins",\n    "Lipids",\n    "Enzymes and phenylketonuria",\n    "Clinical biochemistry and nutrition",\n    "Genetics",\n]\nBIOCHEM_PLANNED = {\n    "Carbohydrates": [\n        "Chemistry of carbohydrates",\n        "Amino sugars and mucopolysaccharides",\n        "Glycolysis and gluconeogenesis",\n        "Glycogen metabolism and glycogen storage disorders",\n        "HMP shunt pathway",\n        "Fructose and galactose metabolism",\n        "ETC and bioenergetics",\n        "Krebs cycle",\n    ],\n    "Amino acids and proteins": [\n        "Amino acid basics",\n        "Amino acid metabolism",\n        "Amino acid metabolic disorder",\n        "Protein structure and function",\n        "Urea cycle and its disorders",\n    ],\n    "Lipids": [\n        "Lipid basics",\n        "Fatty acid oxidation and ketogenesis",\n        "Biosynthesis of fatty acids and eicosanoids",\n        "Metabolism of acylglycerols and sphingolipids",\n        "Cholesterol synthesis, transport, and excretion",\n    ],\n    "Enzymes and phenylketonuria": [\n        "Phenylketonuria and bile pigments",\n        "Enzyme mechanism of action and clinical importance",\n        "Enzyme kinetics and regulation of activity",\n    ],\n    "Clinical biochemistry and nutrition": [\n        "Fats",\n        "Soluble vitamins",\n        "Energy-releasing vitamins",\n        "Hematopoietic and other vitamins",\n        "Antioxidants and minerals",\n    ],\n    "Genetics": [\n        "Basics of genetics",\n        "Nucleotide metabolism and disorders",\n        "DNA organization, replication, and repair",\n        "RNA synthesis, processing, and modification",\n        "Regulation of gene expression",\n        "Molecular genetics and recombinant DNA and genomic technology",\n    ],\n}\n'''
        assert marker in s
        s = s.replace(marker, block + marker, 1)
    old = '    assert subjects["Biochemistry"]["topics"][0]["section"] == "Carbohydrate Chemistry"\n'
    new = '''    biochem = subjects["Biochemistry"]\n    assert biochem["catalogVersion"] == 2\n    assert biochem["sectionOrder"] == BIOCHEM_SECTION_ORDER\n    assert biochem["displayNumbering"] == "visible-contiguous"\n    bplanned = biochem["plannedIndex"]\n    assert [section["title"] for section in bplanned] == BIOCHEM_SECTION_ORDER\n    assert {section["title"]: [topic["title"] for topic in section["topics"]] for section in bplanned} == BIOCHEM_PLANNED\n    bslots = [topic["slot"] for section in bplanned for topic in section["topics"]]\n    assert len(bslots) == 32\n    assert len(set(bslots)) == len(bslots)\n    bslot_set = set(bslots)\n    bcurrent = biochem["topics"]\n    for item in bcurrent:\n        assert item.get("plannedSlots"), item["id"]\n        assert set(item["plannedSlots"]) <= bslot_set, (item["id"], item["plannedSlots"])\n    bnonempty = [section for section in biochem["sectionOrder"] if any(item["section"] == section for item in bcurrent)]\n    assert bnonempty == BIOCHEM_SECTION_ORDER\n    bflattened = [item["id"] for section in biochem["sectionOrder"] for item in bcurrent if item["section"] == section]\n    assert bflattened == [str(i) for i in range(1, 27)]\n'''
    assert old in s
    s = s.replace(old, new, 1)
    s = s.replace(
        'print("MARROW_TOPIC_TAXONOMY_OK subjects=3 current_topics=107 anatomy_plan=71 anatomy_visible=48 numbering=contiguous placeholders=none")',
        'print("MARROW_TOPIC_TAXONOMY_OK subjects=3 current_topics=107 anatomy_plan=71 anatomy_visible=48 biochemistry_plan=32 biochemistry_visible=26 numbering=contiguous placeholders=none")',
        1,
    )
    TEST.write_text(s, encoding="utf-8")


def patch_browser() -> None:
    s = BROWSER.read_text(encoding="utf-8")
    old = "            assert_sections(['Carbohydrate Chemistry','Lipid Chemistry','Amino Acid & Protein Chemistry','Heme Synthesis','Enzymes','Free Radicals, Antioxidants, Trace Elements & Miscellaneous','Genetics','Vitamins'])\n"
    new = "            assert_sections(['Carbohydrates','Amino acids and proteins','Lipids','Enzymes and phenylketonuria','Clinical biochemistry and nutrition','Genetics'])\n            bnums=[int(x) for x in page.locator('.nk-topic-index').all_inner_texts()]\n            if bnums!=list(range(1,27)): raise SystemExit(f'Marrow Biochemistry learner numbering is not contiguous 1-26: {bnums!r}')\n"
    assert old in s
    s = s.replace(old, new, 1)
    BROWSER.write_text(s, encoding="utf-8")


def patch_doc() -> None:
    s = DOC.read_text(encoding="utf-8")
    s = s.replace(
        "> Status: **implemented for the current Anatomy import; Anatomy future-slot metadata is authoritative**.\n> Physiology and Biochemistry remain on their previously recorded taxonomy until the user supplies their revised arrangements.\n",
        "> Status: **implemented for Anatomy and Biochemistry; their future-slot metadata is authoritative**.\n> Physiology remains on its previously recorded taxonomy until the user supplies its revised arrangement.\n",
        1,
    )
    start = s.index("## Biochemistry — existing taxonomy retained pending user revision")
    end = s.index("## Implementation contract", start)
    section = '''## Biochemistry — authoritative intended major-index order\n\n1. **Carbohydrates**\n2. **Amino acids and proteins**\n3. **Lipids**\n4. **Enzymes and phenylketonuria**\n5. **Clinical biochemistry and nutrition**\n6. **Genetics**\n\n### Carbohydrates\n\n1. Chemistry of carbohydrates\n2. Amino sugars and mucopolysaccharides\n3. Glycolysis and gluconeogenesis\n4. Glycogen metabolism and glycogen storage disorders\n5. HMP shunt pathway\n6. Fructose and galactose metabolism\n7. ETC and bioenergetics\n8. Krebs cycle\n\n### Amino acids and proteins\n\n1. Amino acid basics\n2. Amino acid metabolism\n3. Amino acid metabolic disorder\n4. Protein structure and function\n5. Urea cycle and its disorders\n\n### Lipids\n\n1. Lipid basics\n2. Fatty acid oxidation and ketogenesis\n3. Biosynthesis of fatty acids and eicosanoids\n4. Metabolism of acylglycerols and sphingolipids\n5. Cholesterol synthesis, transport, and excretion\n\n### Enzymes and phenylketonuria\n\n1. Phenylketonuria and bile pigments\n2. Enzyme mechanism of action and clinical importance\n3. Enzyme kinetics and regulation of activity\n\n### Clinical biochemistry and nutrition\n\n1. Fats\n2. Soluble vitamins\n3. Energy-releasing vitamins\n4. Hematopoietic and other vitamins\n5. Antioxidants and minerals\n\n### Genetics\n\n1. Basics of genetics\n2. Nucleotide metabolism and disorders\n3. DNA organization, replication, and repair\n4. RNA synthesis, processing, and modification\n5. Regulation of gene expression\n6. Molecular genetics and recombinant DNA and genomic technology\n\n## Current Marrow Biochemistry Ch 1–26 placement\n\nThe current imported source records remain exactly 26 source topics and 543 questions. They are arranged as follows:\n\n- Ch 1–6 → **Carbohydrates**\n- Ch 7–11 → **Amino acids and proteins**\n- Ch 12–16 → **Lipids**\n- Ch 17–19 → **Enzymes and phenylketonuria**\n- Ch 20–23 → **Clinical biochemistry and nutrition**\n- Ch 24–26 → **Genetics**\n\nThe enumerated learner catalog contains 32 planned slots. Missing future slots do not render. Current combined source chapters remain single source topics: Ch 1 maps to Chemistry of carbohydrates + Amino sugars and mucopolysaccharides; Ch 4 maps to HMP shunt pathway + Fructose and galactose metabolism; Ch 20 maps to Fats + Soluble vitamins; and Ch 24 maps to Basics of genetics + Nucleotide metabolism and disorders. Genetics slots for Regulation of gene expression and Molecular genetics/recombinant DNA/genomic technology are metadata-only until corresponding source topics are imported.\n\nLearner-facing numbering is contiguous across the currently visible arranged source topics (1–26); source chapter IDs remain unchanged underneath.\n\n'''
    s = s[:start] + section + s[end:]
    DOC.write_text(s, encoding="utf-8")


def patch_state() -> None:
    s = STATE.read_text(encoding="utf-8")
    s = s.replace(
        "- Physiology and Biochemistry taxonomy are unchanged pending the user's exact\n  revised arrangements.\n",
        "- Physiology taxonomy remains unchanged; Biochemistry now has its own v2 contract below.\n",
        1,
    )
    marker = "\n## User/device verification\n"
    block = '''\n## Biochemistry topic index v2 — 2026-09-10\n\nUser-authoritative major-index order: **Carbohydrates → Amino acids and proteins →\nLipids → Enzymes and phenylketonuria → Clinical biochemistry and nutrition → Genetics**.\n\n- `plannedIndex` stores all **32 supplied learner slots** while current source remains **26 topics / 543 questions**.\n- Current placement: Ch 1–6 Carbohydrates; 7–11 Amino acids/proteins; 12–16 Lipids; 17–19 Enzymes/phenylketonuria; 20–23 Clinical biochemistry/nutrition; 24–26 Genetics.\n- Combined source chapters stay combined; `plannedSlots` maps Ch 1, 4, 20 and 24 to multiple finer learner slots.\n- Missing future topics never render as placeholders; learner numbering is visible-contiguous 1–26; source IDs/titles/question linkage/FSRS remain untouched.\n- Physiology taxonomy is still pending the user's revised arrangement.\n'''
    assert marker in s
    s = s.replace(marker, block + marker, 1)
    STATE.write_text(s, encoding="utf-8")


def cleanup_one_time_files() -> None:
    for rel in [
        ".github/workflows/inspect-biochem-taxonomy.yml",
        ".github/workflows/apply-biochem-taxonomy.yml",
        "tools/apply_biochemistry_topic_index_v2.py",
    ]:
        p = ROOT / rel
        if p.exists():
            p.unlink()


def main() -> None:
    apply_taxonomy()
    patch_test()
    patch_browser()
    patch_doc()
    patch_state()
    cleanup_one_time_files()
    print("BIOCHEM_TOPIC_INDEX_V2_APPLIED planned=32 current=26 sections=6 numbering=visible-contiguous")


if __name__ == "__main__":
    main()
