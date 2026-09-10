#!/usr/bin/env python3
"""Validate the explicit Marrow topic-to-major-index taxonomy."""
from __future__ import annotations

import base64
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
BANKS = {
    "Anatomy": "anatomy_phase_a",
    "Biochemistry": "biochemistry_phase_a",
    "Physiology": "physiology_ch001_043",
}

ANATOMY_SECTION_ORDER = [
    "Embryology", "Histology", "Neuroanatomy", "Head, neck, and face",
    "Upper limb", "Thorax", "Abdomen and pelvis", "Lower limb", "Back", "General anatomy",
]
ANATOMY_PLANNED = {
    "Embryology": [
        "Gametogenesis", "Pre-embryonic phase of development", "Embryonic phase of development",
        "Placenta", "Fetal membranes and twinning", "Pharyngeal arches", "Skeleton and muscular system",
        "Cardiovascular system", "Respiratory system", "Elementary hepatobiliary systems and pancreas and spleen",
        "Face, nose and palate", "Eye and ear", "Nervous system and endocrine glands", "Urogenital system",
    ],
    "Histology": [
        "Cell structure", "Epithelia, glands, and connective tissue", "Bone, cartilage, and muscular tissue",
        "Nervous and endocrine systems", "Cardiovascular, lymphatic, and respiratory systems",
        "Digestive, hepatobiliary, and genitourinary systems", "Skin and special senses: eye and ear",
    ],
    "Neuroanatomy": [
        "Cranial nerves", "Meninges and dural venous sinuses", "Ventricular systems and supratentorial space",
        "Cerebrum", "White matter of the brain", "Basal ganglia and limbic system", "Diencephalon",
        "Brainstem", "Cerebellum", "Vascular supply of brain", "Spinal cord",
    ],
    "Head, neck, and face": [
        "Osteology", "Scalp and face", "Deep fascia and triangle of the neck",
        "Muscle and neurovascular anatomy of head and neck", "Glands of the head and neck",
        "Tongue and palate", "Pharynx", "Larynx",
    ],
    "Upper limb": [
        "Upper limb bones and joints", "Fossa and spaces of the upper limb", "Breast",
        "Brachial plexus and nerves", "Muscle of upper limb", "Vessels of upper limb",
    ],
    "Thorax": ["General anatomy of thorax", "Thoracic wall", "Mediastinum", "Diaphragm", "Heart", "Lungs and pleura"],
    "Abdomen and pelvis": [
        "Anterior abdominal wall", "Abdominal cavity and peritoneum", "GI tract", "Hepatobiliary system",
        "Spleen and pancreas", "Kidneys and adrenal gland", "Internal and external genitalia", "Pelvis and perineum",
    ],
    "Lower limb": [
        "Bones of lower limb", "Joints of lower limb", "Muscles of lower limb",
        "Nerves and vessels of lower limb", "Important structures of lower limb",
    ],
    "Back": ["Vertebral column"],
    "General anatomy": [
        "Bones, joints, and cartilage", "Muscles and tendon", "Cardiovascular, lymphatic, and nervous systems",
        "Skin", "Connective tissue and ligaments",
    ],
}

BIOCHEM_SECTION_ORDER = [
    "Carbohydrates", "Amino acids and proteins", "Lipids", "Enzymes and phenylketonuria",
    "Clinical biochemistry and nutrition", "Genetics",
]
BIOCHEM_PLANNED = {
    "Carbohydrates": [
        "Chemistry of carbohydrates", "Amino sugars and mucopolysaccharides", "Glycolysis and gluconeogenesis",
        "Glycogen metabolism and glycogen storage disorders", "HMP shunt pathway", "Fructose and galactose metabolism",
        "ETC and bioenergetics", "Krebs cycle",
    ],
    "Amino acids and proteins": [
        "Amino acid basics", "Amino acid metabolism", "Amino acid metabolic disorder",
        "Protein structure and function", "Urea cycle and its disorders",
    ],
    "Lipids": [
        "Lipid basics", "Fatty acid oxidation and ketogenesis", "Biosynthesis of fatty acids and eicosanoids",
        "Metabolism of acylglycerols and sphingolipids", "Cholesterol synthesis, transport, and excretion",
    ],
    "Enzymes and phenylketonuria": [
        "Phenylketonuria and bile pigments", "Enzyme mechanism of action and clinical importance",
        "Enzyme kinetics and regulation of activity",
    ],
    "Clinical biochemistry and nutrition": [
        "Fats", "Soluble vitamins", "Energy-releasing vitamins", "Hematopoietic and other vitamins", "Antioxidants and minerals",
    ],
    "Genetics": [
        "Basics of genetics", "Nucleotide metabolism and disorders", "DNA organization, replication, and repair",
        "RNA synthesis, processing, and modification", "Regulation of gene expression",
        "Molecular genetics and recombinant DNA and genomic technology",
    ],
}

PHYSIOLOGY_SECTION_ORDER = [
    "General physiology", "Nerve and muscle physiology", "Gastrointestinal system", "Cardiovascular system",
    "Respiratory system", "Renal physiology", "Endocrine physiology", "Reproductive physiology",
    "Central nervous system", "Integrated physiology",
]
PHYSIOLOGY_PLANNED = {
    "General physiology": [
        "Homeostasis and cellular physiology", "Cellular messengers and receptors",
        "Transport across the cell membrane", "Membrane potentials", "Body fluids",
    ],
    "Nerve and muscle physiology": ["Physiology of nerve", "Muscle physiology", "Synapse and junctional transmission"],
    "Gastrointestinal system": [
        "Gastrointestinal secretion", "Gastrointestinal hormones", "Digestion and absorption", "GI peristalsis and motility",
    ],
    "Cardiovascular system": [
        "Vascular system and regional circulation", "Cardiac cycle and cardiac output",
        "Electrophysiology of the heart", "Blood pressure and regulation",
    ],
    "Respiratory system": [
        "Functional anatomy", "Lung mechanics", "Alveolar gas exchange",
        "Gas transport in the lung volumes and lung function tests",
        "Respiratory adaptations in hypoxia, anemia, and pressure changes", "Regulations of respiration",
    ],
    "Renal physiology": [
        "Glomerular filtration rate, renal blood flow, and renal clearance",
        "Renal tubular functions, urine concentration and dilution, and acid-base physiology",
        "Renal hormones and maturation reflex",
    ],
    "Endocrine physiology": ["Pituitary and thyroid", "The pancreas", "The adrenals", "Calcium homeostasis"],
    "Reproductive physiology": ["Male reproductive physiology", "Female reproductive physiology"],
    "Central nervous system": [
        "Neurotransmitters", "Sensory receptors", "Somatosensory pathways", "Special senses", "Motor physiology",
        "Basal ganglia", "Cerebellum", "Hypothalamus", "Limbic system", "Higher mental functions",
    ],
    "Integrated physiology": ["Exercise physiology"],
}

PHYSIOLOGY_VISIBLE_IDS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '31', '32', '33', '26', '27', '28', '29', '30', '19', '20', '21', '22', '23', '24', '25', '34', '35', '36', '37', '38', '39', '40', '41', '42', '10', '11', '12', '13', '14', '15', '16', '17', '18', '43']
PHYSIOLOGY_SLOT_MAP = {
    "1": ["general-physiology:01"],
    "2": ["general-physiology:02"],
    "3": ["general-physiology:03"],
    "4": ["general-physiology:04"],
    "5": ["general-physiology:05"],
    "6": ["nerve-and-muscle-physiology:01"],
    "7": ["nerve-and-muscle-physiology:02"],
    "8": ["nerve-and-muscle-physiology:02"],
    "9": ["nerve-and-muscle-physiology:03"],
    "10": ["central-nervous-system:01"],
    "11": ["central-nervous-system:02"],
    "12": ["central-nervous-system:03"],
    "13": ["central-nervous-system:04"],
    "14": ["central-nervous-system:05"],
    "15": ["central-nervous-system:05"],
    "16": ["central-nervous-system:06", "central-nervous-system:07"],
    "17": ["central-nervous-system:08", "central-nervous-system:09"],
    "18": ["central-nervous-system:10"],
    "19": ["respiratory-system:01"],
    "20": ["respiratory-system:02"],
    "21": ["respiratory-system:03"],
    "22": ["respiratory-system:04"],
    "23": ["respiratory-system:04"],
    "24": ["respiratory-system:05"],
    "25": ["respiratory-system:06"],
    "26": ["cardiovascular-system:01"],
    "27": ["cardiovascular-system:01"],
    "28": ["cardiovascular-system:02"],
    "29": ["cardiovascular-system:03"],
    "30": ["cardiovascular-system:04"],
    "31": ["gastrointestinal-system:01", "gastrointestinal-system:02"],
    "32": ["gastrointestinal-system:03"],
    "33": ["gastrointestinal-system:04"],
    "34": ["renal-physiology:01"],
    "35": ["renal-physiology:02"],
    "36": ["renal-physiology:02", "renal-physiology:03"],
    "37": ["endocrine-physiology:01"],
    "38": ["endocrine-physiology:02"],
    "39": ["endocrine-physiology:03"],
    "40": ["endocrine-physiology:04"],
    "41": ["reproductive-physiology:01"],
    "42": ["reproductive-physiology:02"],
    "43": ["integrated-physiology:01"],
}


def load_bank(prefix: str) -> dict:
    encoded = "".join(part.read_text(encoding="utf-8").strip() for part in sorted(DATA.glob(f"{prefix}.zlib.b64.part*")))
    return json.loads(zlib.decompress(base64.b64decode(encoded)))


def planned_map(config: dict) -> dict[str, list[str]]:
    return {section["title"]: [topic["title"] for topic in section["topics"]] for section in config["plannedIndex"]}


def validate_planned(subject: str, config: dict, section_order: list[str], planned: dict[str, list[str]], count: int) -> set[str]:
    assert config["catalogVersion"] == 2, subject
    assert config["sectionOrder"] == section_order, subject
    assert config["displayNumbering"] == "visible-contiguous", subject
    assert [section["title"] for section in config["plannedIndex"]] == section_order, subject
    assert planned_map(config) == planned, subject
    slots = [topic["slot"] for section in config["plannedIndex"] for topic in section["topics"]]
    assert len(slots) == count, (subject, len(slots))
    assert len(slots) == len(set(slots)), subject
    slot_set = set(slots)
    for item in config["topics"]:
        assert item.get("plannedSlots"), (subject, item["id"])
        assert set(item["plannedSlots"]) <= slot_set, (subject, item["id"], item["plannedSlots"])
    return slot_set


def flatten_current(config: dict) -> list[str]:
    return [
        str(item["id"])
        for section in config["sectionOrder"]
        for item in config["topics"]
        if item["section"] == section
    ]


def nonempty_sections(config: dict) -> list[str]:
    return [section for section in config["sectionOrder"] if any(item["section"] == section for item in config["topics"])]


def main() -> None:
    taxonomy = json.loads((DATA / "topic_index_taxonomy.json").read_text(encoding="utf-8"))
    assert taxonomy["schemaVersion"] == 1
    subjects = taxonomy["subjects"]
    assert set(subjects) == set(BANKS)

    total = 0
    for subject, prefix in BANKS.items():
        source_topics = load_bank(prefix)["topics"]
        config = subjects[subject]
        configured = config["topics"]
        assert len(configured) == len(source_topics), subject
        assert [str(item["id"]) for item in configured] == [str(item["id"]) for item in source_topics], subject
        assert len({str(item["id"]) for item in configured}) == len(configured), subject
        by_id = {str(item["id"]): item for item in configured}
        for source in source_topics:
            item = by_id[str(source["id"])]
            assert item["title"] == source["title"], (subject, source["id"])
            assert item["section"] in config["sectionOrder"], (subject, source["id"])
        for section in config["sectionOrder"]:
            ids = [int(item["id"]) for item in configured if item["section"] == section]
            assert ids == sorted(ids), (subject, section)
        total += len(configured)

    anatomy = subjects["Anatomy"]
    validate_planned("Anatomy", anatomy, ANATOMY_SECTION_ORDER, ANATOMY_PLANNED, 71)
    assert nonempty_sections(anatomy) == ANATOMY_SECTION_ORDER[:7]
    assert flatten_current(anatomy) == [str(i) for i in range(1, 49)]

    biochem = subjects["Biochemistry"]
    validate_planned("Biochemistry", biochem, BIOCHEM_SECTION_ORDER, BIOCHEM_PLANNED, 32)
    assert nonempty_sections(biochem) == BIOCHEM_SECTION_ORDER
    assert flatten_current(biochem) == [str(i) for i in range(1, 27)]

    phys = subjects["Physiology"]
    validate_planned("Physiology", phys, PHYSIOLOGY_SECTION_ORDER, PHYSIOLOGY_PLANNED, 42)
    assert nonempty_sections(phys) == PHYSIOLOGY_SECTION_ORDER
    assert flatten_current(phys) == PHYSIOLOGY_VISIBLE_IDS
    assert {str(item["id"]): item["plannedSlots"] for item in phys["topics"]} == PHYSIOLOGY_SLOT_MAP
    assert set(PHYSIOLOGY_VISIBLE_IDS) == {str(i) for i in range(1, 44)}

    assert total == 117
    print(
        "MARROW_TOPIC_TAXONOMY_OK subjects=3 current_topics=117 "
        "anatomy_plan=71 anatomy_visible=48 biochemistry_plan=32 biochemistry_visible=26 "
        "physiology_plan=42 physiology_visible=43 numbering=contiguous placeholders=none"
    )


if __name__ == "__main__":
    main()
