#!/usr/bin/env python3
"""Build the canonical complete Marrow corpus on the V3 product lineage.

Input state is the already repaired source layer:
- Anatomy Ch01-48 + Ch60-63 (898 questions)
- Biochemistry Ch01-28 (582 questions)
- Physiology Ch01-43 (1,014 questions)

This script inserts the validated canonical Anatomy Ch49-59 handoff without
rewriting source content, yielding Anatomy Ch01-63 (1,115) and 2,711 questions
globally. Backend source IDs stay unchanged; taxonomy only fills already-planned
learner slots.
"""
from __future__ import annotations

import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
SRC = DATA / "automation_ingest" / "anatomy"
OLD_PREFIX = "anatomy_ch001_048_plus_060_063"
NEW_PREFIX = "anatomy_ch001_063"
PART_SIZE = 60000

FILES = {
    49: "qbank_chunk_049_gi_tract.jsonl",
    50: "qbank_chunk_050_hepatobiliary_spleen_pancreas.jsonl",
    51: "qbank_chunk_051_kub_adrenal_gland.jsonl",
    52: "qbank_chunk_052_internal_external_genitalia.jsonl",
    53: "qbank_chunk_053_pelvis_perineum.jsonl",
    54: "qbank_chunk_054_bones_lower_limb.jsonl",
    55: "qbank_chunk_055_joints_lower_limb.jsonl",
    56: "qbank_chunk_056_muscles_lower_limb.jsonl",
    57: "qbank_chunk_057_nerves_vessels_lower_limb.jsonl",
    58: "qbank_chunk_058_important_structures_lower_limb.jsonl",
    59: "qbank_chunk_059_vertebral_column.jsonl",
}
EXPECTED_COUNTS = {49:17, 50:23, 51:25, 52:22, 53:20, 54:15, 55:18, 56:23, 57:21, 58:19, 59:14}
TAXONOMY = {
    49: ("Abdomen and pelvis", ["abdomen-and-pelvis:03"]),
    50: ("Abdomen and pelvis", ["abdomen-and-pelvis:04", "abdomen-and-pelvis:05"]),
    51: ("Abdomen and pelvis", ["abdomen-and-pelvis:06"]),
    52: ("Abdomen and pelvis", ["abdomen-and-pelvis:07"]),
    53: ("Abdomen and pelvis", ["abdomen-and-pelvis:08"]),
    54: ("Lower limb", ["lower-limb:01"]),
    55: ("Lower limb", ["lower-limb:02"]),
    56: ("Lower limb", ["lower-limb:03"]),
    57: ("Lower limb", ["lower-limb:04"]),
    58: ("Lower limb", ["lower-limb:05"]),
    59: ("Back", ["back:01"]),
}


def load_bundle(prefix: str) -> tuple[dict, dict]:
    manifest = json.loads((DATA / f"{prefix}_manifest.json").read_text(encoding="utf-8"))
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    assert len(parts) == int(manifest["parts"]), (prefix, len(parts), manifest["parts"])
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    assert len(encoded) == int(manifest["base64_chars"])
    compressed = base64.b64decode(encoded, validate=True)
    assert len(compressed) == int(manifest["compressed_bytes"])
    assert hashlib.sha256(compressed).hexdigest() == manifest["compressed_sha256"]
    raw = zlib.decompress(compressed)
    assert len(raw) == int(manifest["raw_bytes"])
    assert hashlib.sha256(raw).hexdigest() == manifest["raw_sha256"]
    return json.loads(raw.decode("utf-8")), manifest


def read_rows(chapter: int) -> list[dict]:
    path = SRC / FILES[chapter]
    assert path.exists(), path
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == EXPECTED_COUNTS[chapter], (chapter, len(rows), EXPECTED_COUNTS[chapter])
    ids: list[str] = []
    qnums: list[int] = []
    titles: set[str] = set()
    for row in rows:
        assert row.get("schema_version") == "1.1"
        assert row.get("subject") == "Anatomy"
        assert int(row.get("chapter_number", 0)) == chapter
        qn = int(row.get("question_number", 0))
        expected_id = f"ANAT_CH{chapter:02d}_Q{qn:03d}"
        assert row.get("question_id") == expected_id, (row.get("question_id"), expected_id)
        assert str(row.get("question_text", "")).strip()
        options = row.get("options") or []
        assert len(options) == 4
        assert [str(o.get("label", "")).lower() for o in options] == ["a", "b", "c", "d"]
        assert str(row.get("correct_option", "")).lower() in {"a", "b", "c", "d"}
        ids.append(expected_id)
        qnums.append(qn)
        titles.add(str(row.get("chapter", "")).strip())
    assert qnums == list(range(1, len(rows) + 1)), (chapter, qnums)
    assert len(ids) == len(set(ids)) == len(rows)
    assert len(titles) == 1 and "" not in titles
    return rows


def adapt(row: dict) -> dict:
    answer = str(row["correct_option"]).lower()
    correct = "abcd".index(answer) + 1
    options = [
        {"letter": str(opt.get("label", "")).strip().upper(), "text": str(opt.get("text", ""))}
        for opt in row["options"]
    ]
    explanation = row.get("explanation") or {}
    structured = {
        "text": str(explanation.get("text", "")),
        "blocks": explanation.get("blocks", []),
        "tables": explanation.get("tables", []),
        "figures": explanation.get("figures", []),
    }
    source = row.get("source") or {}
    question_pages = source.get("question_pages") or []
    question_figures = [f for f in structured["figures"] if str(f.get("role", "")).lower() == "question"]
    return {
        "id": "marrow__" + str(row["question_id"]),
        "sourceQuestionId": str(row["question_id"]),
        "subject": "Anatomy",
        "bank": "Marrow",
        "chapter": str(row["chapter"]),
        "chapterId": str(row["chapter_number"]),
        "questionNumber": int(row["question_number"]),
        "questionType": str(row.get("question_type") or "single_best_answer"),
        "question": str(row["question_text"]),
        "options": options,
        "correctOption": correct,
        "correctAnswerText": str(row.get("correct_answer_text") or options[correct - 1]["text"]),
        "explanation": structured["text"],
        "structuredExplanation": structured,
        "sourcePage": min(question_pages) if question_pages else None,
        "provenance": source,
        "sourceFidelity": row.get("source_fidelity", {}),
        "reviewStatus": str(row.get("review_status", "")),
        "imageDependent": bool(question_figures),
    }


def replace_exact(path: Path, old: str, new: str, count: int | None = None, optional: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    found = text.count(old)
    if optional and found == 0:
        return
    if count is not None and found != count:
        raise AssertionError(f"{path}: expected {count} occurrences of {old!r}, found {found}")
    if found == 0:
        raise AssertionError(f"{path}: anchor not found: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def write_bundle(record: dict, old_manifest: dict, rows_by_chapter: dict[int, list[dict]]) -> None:
    raw = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    parts = [encoded[i:i + PART_SIZE] for i in range(0, len(encoded), PART_SIZE)]
    for stale in DATA.glob(f"{NEW_PREFIX}.zlib.b64.part*"):
        stale.unlink()
    for i, part in enumerate(parts):
        (DATA / f"{NEW_PREFIX}.zlib.b64.part{i:02d}").write_text(part + "\n", encoding="utf-8")

    reviews = Counter(old_manifest.get("review_status_counts", {}))
    for rows in rows_by_chapter.values():
        reviews.update(str(r.get("review_status", "")) for r in rows)
    source_files = list(old_manifest.get("source_files", []))
    source_files.extend(FILES[ch] for ch in range(49, 60))
    manifest = dict(old_manifest)
    manifest.update({
        "scope": "complete_ch001_063",
        "chapters": list(range(1, 64)),
        "topics": 63,
        "questions": 1115,
        "parts": len(parts),
        "part_size": PART_SIZE,
        "base64_chars": len(encoded),
        "raw_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
        "source_archive": "Marrow ED8 Anatomy canonical complete Ch01-Ch63",
        "source_files": source_files,
        "review_status_counts": dict(sorted(reviews.items())),
        "automation_handoff_ref": "feature/marrow-canonical-full-current",
        "known_source_gap": None,
    })
    (DATA / f"{NEW_PREFIX}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def update_taxonomy(titles: dict[int, str]) -> None:
    path = DATA / "topic_index_taxonomy.json"
    taxonomy = json.loads(path.read_text(encoding="utf-8"))
    anatomy = taxonomy["subjects"]["Anatomy"]
    current_ids = [int(x["id"]) for x in anatomy["topics"]]
    assert current_ids == list(range(1, 49)) + [60, 61, 62, 63], current_ids
    planned_slots = {topic["slot"] for section in anatomy["plannedIndex"] for topic in section["topics"]}
    by_id = {int(x["id"]): x for x in anatomy["topics"]}
    for chapter in range(49, 60):
        section, slots = TAXONOMY[chapter]
        assert set(slots) <= planned_slots
        by_id[chapter] = {"id": str(chapter), "title": titles[chapter], "section": section, "plannedSlots": slots}
    anatomy["topics"] = [by_id[i] for i in range(1, 64)]
    path.write_text(json.dumps(taxonomy, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def update_tools() -> None:
    apply = ROOT / "tools" / "apply_marrow_bank_pilot.py"
    replace_exact(apply, 'load_expanded_bank("anatomy_ch001_048_plus_060_063","Anatomy")', f'load_expanded_bank("{NEW_PREFIX}","Anatomy")', 1)
    replace_exact(apply, 'if len(expanded_ids)!=2494 or len(expanded_ids)!=len(set(expanded_ids)):', 'if len(expanded_ids)!=2711 or len(expanded_ids)!=len(set(expanded_ids)):', 1)

    pilot = ROOT / "tools" / "test_marrow_bank_pilot.py"
    replace_exact(pilot, "load_expanded('anatomy_ch001_048_plus_060_063')", f"load_expanded('{NEW_PREFIX}')", 1)
    replace_exact(pilot, "full_anatomy_manifest['scope']=='ch001_048_plus_ch060_063' and len(fa_q)==898 and len(fa_t)==52", "full_anatomy_manifest['scope']=='complete_ch001_063' and len(fa_q)==1115 and len(fa_t)==63", 1)
    replace_exact(pilot, "len(all_expanded)==2494 and len({q['id'] for q in all_expanded})==2494", "len(all_expanded)==2711 and len({q['id'] for q in all_expanded})==2711", 1)
    replace_exact(pilot, "MARROW_DATA_OK anatomy=898/52 biochemistry=582/28 physiology=1014/43 total=2494", "MARROW_DATA_OK anatomy=1115/63 biochemistry=582/28 physiology=1014/43 total=2711", 1)
    replace_exact(pilot, "MARROW_BANK_PILOT_TEST_OK anatomy=898/52 biochemistry=582/28 physiology=1014/43 total=2494", "MARROW_BANK_PILOT_TEST_OK anatomy=1115/63 biochemistry=582/28 physiology=1014/43 total=2711", 1)

    inv = ROOT / "tools" / "inventory_marrow_explanations.py"
    replace_exact(inv, '"Anatomy": "anatomy_ch001_048_plus_060_063"', f'"Anatomy": "{NEW_PREFIX}"', 1)
    replace_exact(inv, "2494", "2711")

    invtest = ROOT / "tools" / "test_marrow_explanation_inventory.py"
    replace_exact(invtest, "2494", "2711")
    replace_exact(invtest, '"Anatomy": 898', '"Anatomy": 1115', optional=True)
    replace_exact(invtest, '"pending": 2310', '"pending": 2527', optional=True)

    for name in ("test_marrow_biochem_explanation_rollout.py", "test_marrow_biochem_explanation_sample.py"):
        p = ROOT / "tools" / name
        if p.exists():
            replace_exact(p, "2494", "2711", optional=True)
            replace_exact(p, "2310", "2527", optional=True)

    images = ROOT / "tools" / "marrow_images.py"
    replace_exact(images, "'Anatomy': ('anatomy_ch001_048_plus_060_063', 'Anatomy_ed8.pdf')", f"'Anatomy': ('{NEW_PREFIX}', 'Anatomy_ed8.pdf')", 1)
    image_test = ROOT / "tools" / "test_marrow_images.py"
    replace_exact(image_test, "2494", "2711", optional=True)


def update_taxonomy_test() -> None:
    p = ROOT / "tools" / "test_marrow_topic_taxonomy.py"
    text = p.read_text(encoding="utf-8")
    old_block = '''    assert nonempty_sections(anatomy) == ANATOMY_SECTION_ORDER[:7] + ["General anatomy"]\n    assert flatten_current(anatomy) == [str(i) for i in range(1, 49)] + ["60", "61", "62", "63"]\n    assert {str(item["id"]): item["plannedSlots"] for item in anatomy["topics"] if int(item["id"]) >= 60} == {\n        "60": ["general-anatomy:01"],\n        "61": ["general-anatomy:02"],\n        "62": ["general-anatomy:03"],\n        "63": ["general-anatomy:04", "general-anatomy:05"],\n    }\n'''
    new_block = '''    assert nonempty_sections(anatomy) == ANATOMY_SECTION_ORDER\n    assert flatten_current(anatomy) == [str(i) for i in range(1, 64)]\n    assert {str(item["id"]): item["plannedSlots"] for item in anatomy["topics"] if int(item["id"]) >= 49} == {\n        "49": ["abdomen-and-pelvis:03"],\n        "50": ["abdomen-and-pelvis:04", "abdomen-and-pelvis:05"],\n        "51": ["abdomen-and-pelvis:06"],\n        "52": ["abdomen-and-pelvis:07"],\n        "53": ["abdomen-and-pelvis:08"],\n        "54": ["lower-limb:01"],\n        "55": ["lower-limb:02"],\n        "56": ["lower-limb:03"],\n        "57": ["lower-limb:04"],\n        "58": ["lower-limb:05"],\n        "59": ["back:01"],\n        "60": ["general-anatomy:01"],\n        "61": ["general-anatomy:02"],\n        "62": ["general-anatomy:03"],\n        "63": ["general-anatomy:04", "general-anatomy:05"],\n    }\n'''
    if text.count(old_block) != 1:
        raise AssertionError("Anatomy taxonomy assertion block drifted")
    text = text.replace(old_block, new_block, 1)
    text = text.replace('"Anatomy": "anatomy_ch001_048_plus_060_063"', f'"Anatomy": "{NEW_PREFIX}"', 1)
    text = text.replace("assert total == 123", "assert total == 134", 1)
    text = text.replace("current_topics=123", "current_topics=134", 1)
    text = text.replace("anatomy_visible=52", "anatomy_visible=63", 1)
    p.write_text(text, encoding="utf-8")


def update_browser_wrapper() -> None:
    p = ROOT / "tools" / "verify_marrow_bank_browser.py"
    text = p.read_text(encoding="utf-8")
    anchors = {
        "('PrepLadder','Marrow','1,068','898')": "('PrepLadder','Marrow','1,068','1,115')",
        "count()!=52: raise SystemExit('Marrow Anatomy topic count is not 52')": "count()!=63: raise SystemExit('Marrow Anatomy topic count is not 63')",
        "['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis','General anatomy']": "['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis','Lower limb','Back','General anatomy']",
        "range(1,53)]: raise SystemExit(f'Marrow Anatomy learner numbering is not contiguous 1-52": "range(1,64)]: raise SystemExit(f'Marrow Anatomy learner numbering is not contiguous 1-63",
        "source = source.replace('anatomy=819/48', 'anatomy=898/52')": "source = source.replace('anatomy=819/48', 'anatomy=1115/63')",
    }
    for old, new in anchors.items():
        if text.count(old) != 1:
            raise AssertionError(f"browser anchor drifted: {old!r} count={text.count(old)}")
        text = text.replace(old, new, 1)
    text = text.replace("total=2494", "total=2711")
    p.write_text(text, encoding="utf-8")


def main() -> None:
    old, old_manifest = load_bundle(OLD_PREFIX)
    assert old.get("subject") == "Anatomy" and old.get("bank") == "Marrow"
    assert len(old.get("topics", [])) == 52 and len(old.get("questions", [])) == 898
    assert [int(t["id"]) for t in old["topics"]] == list(range(1, 49)) + [60, 61, 62, 63]

    rows_by_chapter = {chapter: read_rows(chapter) for chapter in range(49, 60)}
    assert sum(len(rows) for rows in rows_by_chapter.values()) == 217
    titles = {chapter: str(rows[0]["chapter"]) for chapter, rows in rows_by_chapter.items()}

    topics = list(old["topics"])
    questions = list(old["questions"])
    existing_ids = {str(q["id"]) for q in questions}
    for chapter in range(49, 60):
        rows = rows_by_chapter[chapter]
        pages = [p for row in rows for p in ((row.get("source") or {}).get("question_pages") or [])]
        topics.append({
            "id": str(chapter), "title": titles[chapter], "subject": "Anatomy", "bank": "Marrow",
            "questionCount": len(rows), "startPage": min(pages) if pages else None,
        })
        questions.extend(adapt(row) for row in rows)

    topics.sort(key=lambda t: int(t["id"]))
    questions.sort(key=lambda q: (int(q["chapterId"]), int(q.get("questionNumber") or 0), str(q["id"])))
    ids = [str(q["id"]) for q in questions]
    assert len(topics) == 63 and [int(t["id"]) for t in topics] == list(range(1, 64))
    assert len(questions) == 1115 and len(ids) == len(set(ids)) == 1115
    assert existing_ids.issubset(set(ids))
    assert all([str(o.get("letter", "")) for o in q.get("options", [])] == ["A", "B", "C", "D"] for q in questions)

    record = dict(old)
    record["scope"] = "complete_ch001_063"
    record["topics"] = topics
    record["questions"] = questions
    stats = dict(record.get("stats") or {})
    for key in list(stats):
        low = key.lower().replace("_", "")
        if low in {"topics", "topiccount"}: stats[key] = 63
        if low in {"questions", "questioncount"}: stats[key] = 1115
    record["stats"] = stats

    write_bundle(record, old_manifest, rows_by_chapter)
    update_taxonomy(titles)
    update_tools()
    update_taxonomy_test()
    update_browser_wrapper()
    print("MARROW_FULL_CORPUS_BUILD_OK anatomy=1115/63 biochemistry=582/28 physiology=1014/43 total=2711 topics=134")


if __name__ == "__main__":
    main()
