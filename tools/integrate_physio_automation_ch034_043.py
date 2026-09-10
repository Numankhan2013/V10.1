#!/usr/bin/env python3
"""Integrate canonical Physiology automation JSONL Ch34-43 into the Marrow bank.

The automation handoff remains source-faithful. This script only adapts the JSONL
schema into the existing NK QBank Marrow runtime schema and packages it using the
same hash-verified compressed shard contract as the existing expanded banks.
"""
from __future__ import annotations

import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
SOURCE_REF = "origin/feature/marrow-bank-pilot"
OLD_PREFIX = "physiology_ch001_033"
NEW_PREFIX = "physiology_ch001_043"
PART_SIZE = 60000

NEW_FILES = {
    34: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_034_glomerular_filtration_rate_renal_blood_flow_and_renal_clearance.jsonl",
    35: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_035_renal_tubular_functions_urine_concentration_and_dilution.jsonl",
    36: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_036_acid_base_balance_renal_hormones_and_micturition_reflex.jsonl",
    37: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_037_pituitary_and_thyroid.jsonl",
    38: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_038_the_pancreas.jsonl",
    39: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_039_the_adrenals.jsonl",
    40: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_040_calcium_homeostasis.jsonl",
    41: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_041_male_reproductive_physiology.jsonl",
    42: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_042_female_reproductive_physiology.jsonl",
    43: "data/marrow/automation_ingest/physiology/qbank_physio_chunk_043_exercise_physiology.jsonl",
}

EXPECTED_COUNTS = {34: 35, 35: 32, 36: 25, 37: 24, 38: 25, 39: 21, 40: 25, 41: 28, 42: 30, 43: 16}

TAXONOMY = {
    34: ("Renal physiology", ["renal-physiology:01"]),
    35: ("Renal physiology", ["renal-physiology:02"]),
    36: ("Renal physiology", ["renal-physiology:02", "renal-physiology:03"]),
    37: ("Endocrine physiology", ["endocrine-physiology:01"]),
    38: ("Endocrine physiology", ["endocrine-physiology:02"]),
    39: ("Endocrine physiology", ["endocrine-physiology:03"]),
    40: ("Endocrine physiology", ["endocrine-physiology:04"]),
    41: ("Reproductive physiology", ["reproductive-physiology:01"]),
    42: ("Reproductive physiology", ["reproductive-physiology:02"]),
    43: ("Integrated physiology", ["integrated-physiology:01"]),
}

EXPECTED_VISIBLE = [
    *map(str, range(1, 10)),
    "31", "32", "33",
    *map(str, range(26, 31)),
    *map(str, range(19, 26)),
    "34", "35", "36",
    "37", "38", "39", "40",
    "41", "42",
    *map(str, range(10, 19)),
    "43",
]


def load_bundle(prefix: str) -> tuple[dict, dict]:
    manifest = json.loads((DATA / f"{prefix}_manifest.json").read_text(encoding="utf-8"))
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in sorted(DATA.glob(f"{prefix}.zlib.b64.part*")))
    compressed = base64.b64decode(encoded, validate=True)
    assert len(compressed) == manifest["compressed_bytes"]
    assert hashlib.sha256(compressed).hexdigest() == manifest["compressed_sha256"]
    raw = zlib.decompress(compressed)
    assert len(raw) == manifest["raw_bytes"]
    assert hashlib.sha256(raw).hexdigest() == manifest["raw_sha256"]
    return json.loads(raw.decode("utf-8")), manifest


def git_show(path: str) -> str:
    return subprocess.check_output(["git", "show", f"{SOURCE_REF}:{path}"], text=True)


def read_rows(chapter: int, path: str) -> list[dict]:
    rows = [json.loads(line) for line in git_show(path).splitlines() if line.strip()]
    assert len(rows) == EXPECTED_COUNTS[chapter], (chapter, len(rows))
    ids: set[str] = set()
    titles: set[str] = set()
    qnums: list[int] = []
    for row in rows:
        assert row.get("subject") == "Physiology", (chapter, row.get("subject"))
        assert int(row.get("chapter_number", 0)) == chapter
        assert str(row.get("stem", "")).strip()
        assert len(row.get("options", [])) == 4
        assert str(row.get("source_answer", "")).lower() in {"a", "b", "c", "d"}
        rid = str(row.get("id", ""))
        assert rid and rid not in ids
        ids.add(rid)
        titles.add(str(row.get("chapter", "")).strip())
        qnums.append(int(row.get("question_number", 0)))
    assert len(titles) == 1 and "" not in titles
    assert qnums == list(range(1, len(rows) + 1)), (chapter, qnums[:5], qnums[-5:])
    return rows


def adapt_question(row: dict, question_type: str) -> dict:
    answer = str(row["source_answer"]).lower()
    correct = "abcd".index(answer) + 1
    options = [{"letter": str(opt.get("label", "")).strip().upper(), "text": str(opt.get("text", ""))} for opt in row["options"]]
    structured = {
        "text": str((row.get("explanation") or {}).get("text", "")),
        "blocks": (row.get("explanation") or {}).get("blocks", []),
        "tables": row.get("tables", []),
        "figures": row.get("visuals", []),
    }
    if row.get("equations"):
        structured["equations"] = row["equations"]
    if row.get("reconstruction") is not None:
        structured["reconstruction"] = row["reconstruction"]
    return {
        "id": "marrow__" + str(row["id"]),
        "sourceQuestionId": str(row["id"]),
        "subject": "Physiology",
        "bank": "Marrow",
        "chapter": str(row["chapter"]),
        "chapterId": str(row["chapter_number"]),
        "questionNumber": int(row["question_number"]),
        "questionType": question_type,
        "question": str(row["stem"]),
        "options": options,
        "correctOption": correct,
        "correctAnswerText": options[correct - 1]["text"],
        "explanation": structured["text"],
        "structuredExplanation": structured,
        "sourcePage": row.get("source_pdf_page"),
        "provenance": row.get("source_provenance", {}),
        "sourceFidelity": row.get("source_fidelity_notes", []),
        "reviewStatus": str(row.get("review_status", "")),
        "imageDependent": bool(row.get("image_dependent", False)),
    }


def write_bundle(record: dict, old_manifest: dict, new_rows: dict[int, list[dict]]) -> None:
    raw = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    parts = [encoded[i:i + PART_SIZE] for i in range(0, len(encoded), PART_SIZE)]
    for stale in DATA.glob(f"{NEW_PREFIX}.zlib.b64.part*"):
        stale.unlink()
    for i, part in enumerate(parts):
        (DATA / f"{NEW_PREFIX}.zlib.b64.part{i:02d}").write_text(part + "\n", encoding="utf-8")

    review_counts = Counter(old_manifest.get("review_status_counts", {}))
    # Counter(mapping) preserves old counts; add the 261 new source statuses.
    for rows in new_rows.values():
        review_counts.update(str(row.get("review_status", "")) for row in rows)
    source_files = list(old_manifest.get("source_files", [])) + [Path(NEW_FILES[ch]).name for ch in range(34, 44)]
    manifest = dict(old_manifest)
    manifest.update({
        "scope": "complete_ch001_043",
        "chapters": list(range(1, 44)),
        "topics": 43,
        "questions": 1014,
        "parts": len(parts),
        "part_size": PART_SIZE,
        "base64_chars": len(encoded),
        "raw_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
        "source_archive": "Marrow ED8 Physiology canonical JSONL Ch01-Ch43",
        "source_files": source_files,
        "review_status_counts": dict(sorted(review_counts.items())),
        "automation_handoff_ref": "feature/marrow-bank-pilot",
    })
    (DATA / f"{NEW_PREFIX}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_exact(path: Path, old: str, new: str, count: int | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    found = text.count(old)
    if count is not None and found != count:
        raise AssertionError(f"{path}: expected {count} occurrences of {old!r}, found {found}")
    if found == 0:
        raise AssertionError(f"{path}: anchor not found: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def update_runtime_and_tests() -> None:
    apply = ROOT / "tools" / "apply_marrow_bank_pilot.py"
    replace_exact(apply, 'load_expanded_bank("physiology_ch001_033","Physiology")', 'load_expanded_bank("physiology_ch001_043","Physiology")', 1)
    replace_exact(apply, "if len(expanded_ids)!=2115 or len(expanded_ids)!=len(set(expanded_ids)):", "if len(expanded_ids)!=2376 or len(expanded_ids)!=len(set(expanded_ids)):", 1)

    pilot = ROOT / "tools" / "test_marrow_bank_pilot.py"
    replace_exact(pilot, "load_expanded('physiology_ch001_033')", "load_expanded('physiology_ch001_043')", 1)
    replace_exact(pilot, "full_phys_manifest['scope']=='complete_ch001_033' and len(fp_q)==753 and len(fp_t)==33", "full_phys_manifest['scope']=='complete_ch001_043' and len(fp_q)==1014 and len(fp_t)==43", 1)
    replace_exact(pilot, "len(all_expanded)==2115 and len({q['id'] for q in all_expanded})==2115", "len(all_expanded)==2376 and len({q['id'] for q in all_expanded})==2376", 1)
    replace_exact(pilot, "'marrow__PHYSIO_CH33_Q025'", "'marrow__PHYSIO_CH33_Q025','marrow__PHYSIO_CH43_Q016'", 1)
    replace_exact(pilot, "physiology=753/33 total=2115", "physiology=1014/43 total=2376")

    inv = ROOT / "tools" / "inventory_marrow_explanations.py"
    replace_exact(inv, '"Physiology": "physiology_ch001_033"', '"Physiology": "physiology_ch001_043"', 1)
    replace_exact(inv, '== 2115', '== 2376')
    replace_exact(inv, '2115 - enhanced', '2376 - enhanced')
    replace_exact(inv, 'pending={2115-enhanced}', 'pending={2376-enhanced}')

    invtest = ROOT / "tools" / "test_marrow_explanation_inventory.py"
    replace_exact(invtest, '== 2115', '== 2376')
    replace_exact(invtest, '{"Anatomy": 819, "Biochemistry": 543, "Physiology": 753}', '{"Anatomy": 819, "Biochemistry": 543, "Physiology": 1014}', 1)
    replace_exact(invtest, '2115 - enhanced', '2376 - enhanced')
    replace_exact(invtest, 'questions=2115', 'questions=2376')
    replace_exact(invtest, 'pending={2115-enhanced}', 'pending={2376-enhanced}')

    numbering = ROOT / "tools" / "apply_marrow_topic_numbering_v1.py"
    text = numbering.read_text(encoding="utf-8")
    start = text.index('    expected = [')
    end = text.index('    if phys != expected:', start)
    expected_literal = "    expected = " + repr(EXPECTED_VISIBLE) + "\n"
    text = text[:start] + expected_literal + text[end:]
    text = text.replace('physiology_visible=33 learner_serials=1-33', 'physiology_visible=43 learner_serials=1-43')
    numbering.write_text(text, encoding="utf-8")

    browser = ROOT / "tools" / "verify_marrow_bank_browser.py"
    replace_exact(browser,
        "assert_sections(['General physiology','Nerve and muscle physiology','Gastrointestinal system','Cardiovascular system','Respiratory system','Central nervous system'])",
        "assert_sections(['General physiology','Nerve and muscle physiology','Gastrointestinal system','Cardiovascular system','Respiratory system','Renal physiology','Endocrine physiology','Reproductive physiology','Central nervous system','Integrated physiology'])", 1)
    replace_exact(browser, "list(range(1,34))", "list(range(1,44))", 1)
    replace_exact(browser, "contiguous 1-33", "contiguous 1-43", 1)
    replace_exact(browser, "biochemistry=543/26 physiology=753/33 physiology_plan=42 physiology_numbering=contiguous total=2115",
                  "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous total=2376", 1)


def update_taxonomy(titles: dict[int, str]) -> None:
    path = DATA / "topic_index_taxonomy.json"
    taxonomy = json.loads(path.read_text(encoding="utf-8"))
    phys = taxonomy["subjects"]["Physiology"]
    existing = {int(item["id"]): item for item in phys["topics"]}
    assert set(existing) == set(range(1, 34)), sorted(existing)
    for chapter in range(34, 44):
        section, slots = TAXONOMY[chapter]
        phys["topics"].append({"id": str(chapter), "title": titles[chapter], "section": section, "plannedSlots": slots})
    path.write_text(json.dumps(taxonomy, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def update_taxonomy_test() -> None:
    path = ROOT / "tools" / "test_marrow_topic_taxonomy.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('"Physiology": "physiology_ch001_033"', '"Physiology": "physiology_ch001_043"')
    start = text.index('PHYSIOLOGY_VISIBLE_IDS = [')
    end = text.index('PHYSIOLOGY_SLOT_MAP = {', start)
    visible = "PHYSIOLOGY_VISIBLE_IDS = " + repr(EXPECTED_VISIBLE) + "\n"
    text = text[:start] + visible + text[end:]
    marker = '    "33": ["gastrointestinal-system:04"],\n'
    additions = (
        '    "34": ["renal-physiology:01"],\n'
        '    "35": ["renal-physiology:02"],\n'
        '    "36": ["renal-physiology:02", "renal-physiology:03"],\n'
        '    "37": ["endocrine-physiology:01"],\n'
        '    "38": ["endocrine-physiology:02"],\n'
        '    "39": ["endocrine-physiology:03"],\n'
        '    "40": ["endocrine-physiology:04"],\n'
        '    "41": ["reproductive-physiology:01"],\n'
        '    "42": ["reproductive-physiology:02"],\n'
        '    "43": ["integrated-physiology:01"],\n'
    )
    assert text.count(marker) == 1
    text = text.replace(marker, marker + additions, 1)
    old_sections = '''    assert nonempty_sections(phys) == [\n        "General physiology", "Nerve and muscle physiology", "Gastrointestinal system",\n        "Cardiovascular system", "Respiratory system", "Central nervous system",\n    ]'''
    text = text.replace(old_sections, '    assert nonempty_sections(phys) == PHYSIOLOGY_SECTION_ORDER')
    text = text.replace('set(PHYSIOLOGY_VISIBLE_IDS) == {str(i) for i in range(1, 34)}', 'set(PHYSIOLOGY_VISIBLE_IDS) == {str(i) for i in range(1, 44)}')
    text = text.replace('assert total == 107', 'assert total == 117')
    text = text.replace('current_topics=107', 'current_topics=117')
    text = text.replace('physiology_visible=33', 'physiology_visible=43')
    path.write_text(text, encoding="utf-8")


def main() -> None:
    old, old_manifest = load_bundle(OLD_PREFIX)
    assert old.get("subject") == "Physiology" and old.get("bank") == "Marrow"
    assert len(old.get("topics", [])) == 33 and len(old.get("questions", [])) == 753
    old_ids = {str(q["id"]) for q in old["questions"]}
    question_type = str(old["questions"][0].get("questionType") or "single_best_answer")

    source_rows = {chapter: read_rows(chapter, path) for chapter, path in NEW_FILES.items()}
    assert sum(len(rows) for rows in source_rows.values()) == 261
    titles = {chapter: str(rows[0]["chapter"]) for chapter, rows in source_rows.items()}

    topics = list(old["topics"])
    questions = list(old["questions"])
    for chapter in range(34, 44):
        rows = source_rows[chapter]
        topic = {
            "id": str(chapter),
            "title": titles[chapter],
            "subject": "Physiology",
            "bank": "Marrow",
            "questionCount": len(rows),
            "startPage": min(int(row["source_pdf_page"]) for row in rows if row.get("source_pdf_page") is not None),
        }
        topics.append(topic)
        questions.extend(adapt_question(row, question_type) for row in rows)

    new_ids = [str(q["id"]) for q in questions]
    assert len(topics) == 43 and len(questions) == 1014
    assert len(new_ids) == len(set(new_ids)) == 1014
    assert old_ids.issubset(set(new_ids))
    assert all(qid.startswith("marrow__") for qid in new_ids)
    record = dict(old)
    record["scope"] = "complete_ch001_043"
    record["topics"] = topics
    record["questions"] = questions
    stats = dict(record.get("stats") or {})
    for key in list(stats):
        low = key.lower().replace("_", "")
        if low in {"topics", "topiccount"}: stats[key] = 43
        if low in {"questions", "questioncount"}: stats[key] = 1014
    record["stats"] = stats

    write_bundle(record, old_manifest, source_rows)
    update_taxonomy(titles)
    update_runtime_and_tests()
    update_taxonomy_test()

    print("PHYSIO_AUTOMATION_INGEST_OK chapters=34-43 new_questions=261 physiology=1014/43 global=2376/117 raw_ui_schema=adapted")


if __name__ == "__main__":
    main()
