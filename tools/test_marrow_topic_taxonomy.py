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
    "Physiology": "physiology_ch001_033",
}

ANATOMY_SECTION_ORDER = [
    "Embryology",
    "Histology",
    "Neuroanatomy",
    "Head, neck, and face",
    "Upper limb",
    "Thorax",
    "Abdomen and pelvis",
    "Lower limb",
    "Back",
    "General anatomy",
]
ANATOMY_PLANNED = {
    "Embryology": [
        "Gametogenesis",
        "Pre-embryonic phase of development",
        "Embryonic phase of development",
        "Placenta",
        "Fetal membranes and twinning",
        "Pharyngeal arches",
        "Skeleton and muscular system",
        "Cardiovascular system",
        "Respiratory system",
        "Elementary hepatobiliary systems and pancreas and spleen",
        "Face, nose and palate",
        "Eye and ear",
        "Nervous system and endocrine glands",
        "Urogenital system",
    ],
    "Histology": [
        "Cell structure",
        "Epithelia, glands, and connective tissue",
        "Bone, cartilage, and muscular tissue",
        "Nervous and endocrine systems",
        "Cardiovascular, lymphatic, and respiratory systems",
        "Digestive, hepatobiliary, and genitourinary systems",
        "Skin and special senses: eye and ear",
    ],
    "Neuroanatomy": [
        "Cranial nerves",
        "Meninges and dural venous sinuses",
        "Ventricular systems and supratentorial space",
        "Cerebrum",
        "White matter of the brain",
        "Basal ganglia and limbic system",
        "Diencephalon",
        "Brainstem",
        "Cerebellum",
        "Vascular supply of brain",
        "Spinal cord",
    ],
    "Head, neck, and face": [
        "Osteology",
        "Scalp and face",
        "Deep fascia and triangle of the neck",
        "Muscle and neurovascular anatomy of head and neck",
        "Glands of the head and neck",
        "Tongue and palate",
        "Pharynx",
        "Larynx",
    ],
    "Upper limb": [
        "Upper limb bones and joints",
        "Fossa and spaces of the upper limb",
        "Breast",
        "Brachial plexus and nerves",
        "Muscle of upper limb",
        "Vessels of upper limb",
    ],
    "Thorax": [
        "General anatomy of thorax",
        "Thoracic wall",
        "Mediastinum",
        "Diaphragm",
        "Heart",
        "Lungs and pleura",
    ],
    "Abdomen and pelvis": [
        "Anterior abdominal wall",
        "Abdominal cavity and peritoneum",
        "GI tract",
        "Hepatobiliary system",
        "Spleen and pancreas",
        "Kidneys and adrenal gland",
        "Internal and external genitalia",
        "Pelvis and perineum",
    ],
    "Lower limb": [
        "Bones of lower limb",
        "Joints of lower limb",
        "Muscles of lower limb",
        "Nerves and vessels of lower limb",
        "Important structures of lower limb",
    ],
    "Back": ["Vertebral column"],
    "General anatomy": [
        "Bones, joints, and cartilage",
        "Muscles and tendon",
        "Cardiovascular, lymphatic, and nervous systems",
        "Skin",
        "Connective tissue and ligaments",
    ],
}


def load_bank(prefix: str) -> dict:
    encoded = "".join(
        part.read_text(encoding="utf-8").strip()
        for part in sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    )
    return json.loads(zlib.decompress(base64.b64decode(encoded)))


def main() -> None:
    taxonomy = json.loads((DATA / "topic_index_taxonomy.json").read_text(encoding="utf-8"))
    assert taxonomy["schemaVersion"] == 1
    subjects = taxonomy["subjects"]
    assert set(subjects) == set(BANKS)

    total = 0
    for subject, prefix in BANKS.items():
        bank = load_bank(prefix)
        source_topics = bank["topics"]
        config = subjects[subject]
        configured = config["topics"]
        assert len(configured) == len(source_topics), subject
        assert len({str(item["id"]) for item in configured}) == len(configured), subject
        assert [str(item["id"]) for item in configured] == [str(item["id"]) for item in source_topics], subject
        by_id = {str(item["id"]): item for item in configured}
        for source in source_topics:
            item = by_id[str(source["id"])]
            assert item["title"] == source["title"], (subject, source["id"])
            assert item["section"] in config["sectionOrder"], (subject, source["id"])

        for section in config["sectionOrder"]:
            ids = [int(item["id"]) for item in configured if item["section"] == section]
            assert ids == sorted(ids), (subject, section)
            titles = [item["title"].lower() for item in configured if item["section"] == section]
            pyq_positions = [index for index, title in enumerate(titles) if "pyq" in title or "previous year" in title]
            if pyq_positions:
                assert pyq_positions == list(range(pyq_positions[0], len(titles))), (subject, section)
        total += len(configured)

    anatomy = subjects["Anatomy"]
    assert anatomy["catalogVersion"] == 2
    assert anatomy["sectionOrder"] == ANATOMY_SECTION_ORDER
    assert anatomy["displayNumbering"] == "visible-contiguous"

    planned = anatomy["plannedIndex"]
    assert [section["title"] for section in planned] == ANATOMY_SECTION_ORDER
    assert {section["title"]: [topic["title"] for topic in section["topics"]] for section in planned} == ANATOMY_PLANNED
    all_slots = [topic["slot"] for section in planned for topic in section["topics"]]
    assert len(all_slots) == 71
    assert len(set(all_slots)) == len(all_slots)

    current = anatomy["topics"]
    slot_set = set(all_slots)
    for item in current:
        assert item.get("plannedSlots"), item["id"]
        assert set(item["plannedSlots"]) <= slot_set, (item["id"], item["plannedSlots"])

    nonempty_sections = [
        section for section in anatomy["sectionOrder"]
        if any(item["section"] == section for item in current)
    ]
    assert nonempty_sections == [
        "Embryology",
        "Histology",
        "Neuroanatomy",
        "Head, neck, and face",
        "Upper limb",
        "Thorax",
        "Abdomen and pelvis",
    ]

    # Current imported Anatomy chapters are deliberately grouped as contiguous
    # source blocks. The existing renderer numbers cards by current CHAPTERS
    # position, so flattening these non-empty groups must produce 1..48 with no
    # learner-facing jump. Empty planned groups never render.
    flattened_ids = [
        item["id"]
        for section in anatomy["sectionOrder"]
        for item in current
        if item["section"] == section
    ]
    assert flattened_ids == [str(i) for i in range(1, 49)]

    assert subjects["Biochemistry"]["topics"][0]["section"] == "Carbohydrate Chemistry"
    assert total == 107
    print("MARROW_TOPIC_TAXONOMY_OK subjects=3 current_topics=107 anatomy_plan=71 anatomy_visible=48 numbering=contiguous placeholders=none")


if __name__ == "__main__":
    main()
