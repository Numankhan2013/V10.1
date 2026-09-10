#!/usr/bin/env python3
"""Integrate canonical Anatomy automation JSONL Ch60-63 into the Marrow bank.

Ch49-59 are intentionally absent: this script does not fabricate continuity.
It adapts storage/schema only; source stems, options, answers, explanations,
tables, figures and provenance remain source-faithful.
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
OLD_PREFIX = "anatomy_phase_a"
NEW_PREFIX = "anatomy_ch001_048_plus_060_063"
PART_SIZE = 60000

NEW_FILES = {
    60: "data/marrow/automation_ingest/anatomy/qbank_chunk_060_bones_joints_cartilage.jsonl",
    61: "data/marrow/automation_ingest/anatomy/qbank_chunk_061_muscles_tendons.jsonl",
    62: "data/marrow/automation_ingest/anatomy/qbank_chunk_062_cardiovascular_lymphatic_nervous_systems.jsonl",
    63: "data/marrow/automation_ingest/anatomy/qbank_chunk_063_skin_connective_tissue_ligaments.jsonl",
}
EXPECTED_COUNTS = {60: 30, 61: 16, 62: 20, 63: 13}
TAXONOMY = {
    60: ("General anatomy", ["general-anatomy:01"]),
    61: ("General anatomy", ["general-anatomy:02"]),
    62: ("General anatomy", ["general-anatomy:03"]),
    63: ("General anatomy", ["general-anatomy:04", "general-anatomy:05"]),
}
EXPECTED_VISIBLE = [*map(str, range(1, 49)), "60", "61", "62", "63"]


def load_bundle(prefix: str) -> tuple[dict, dict]:
    manifest = json.loads((DATA / f"{prefix}_manifest.json").read_text(encoding="utf-8"))
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    assert len(parts) == manifest["parts"], (prefix, len(parts), manifest["parts"])
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
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
        assert row.get("subject") == "Anatomy"
        assert int(row.get("chapter_number", 0)) == chapter
        assert str(row.get("question_text", "")).strip()
        assert len(row.get("options", [])) == 4
        assert str(row.get("correct_option", "")).lower() in {"a", "b", "c", "d"}
        rid = str(row.get("question_id", ""))
        assert rid and rid not in ids
        ids.add(rid)
        titles.add(str(row.get("chapter", "")).strip())
        qnums.append(int(row.get("question_number", 0)))
    assert len(titles) == 1 and "" not in titles
    assert qnums == list(range(1, len(rows) + 1)), (chapter, qnums)
    return rows


def adapt_question(row: dict) -> dict:
    answer = str(row["correct_option"]).lower()
    correct = "abcd".index(answer) + 1
    options = [
        {"letter": str(opt.get("label", "")).lower(), "text": str(opt.get("text", ""))}
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
    for rows in new_rows.values():
        review_counts.update(str(row.get("review_status", "")) for row in rows)
    manifest = dict(old_manifest)
    manifest.update({
        "scope": "ch001_048_plus_ch060_063",
        "chapters": [*range(1, 49), 60, 61, 62, 63],
        "topics": 52,
        "questions": 898,
        "parts": len(parts),
        "part_size": PART_SIZE,
        "base64_chars": len(encoded),
        "raw_bytes": len(raw),
        "compressed_bytes": len(compressed),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
        "source_archive": "Marrow ED8 Anatomy canonical JSONL Ch01-Ch48 + Ch60-Ch63",
        "source_files": list(old_manifest.get("source_files", [])) + [Path(NEW_FILES[ch]).name for ch in range(60, 64)],
        "review_status_counts": dict(sorted(review_counts.items())),
        "automation_handoff_ref": "feature/marrow-bank-pilot",
        "known_source_gap": "Ch49-Ch59 are not present in the committed automation handoff",
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


def update_taxonomy(titles: dict[int, str]) -> None:
    path = DATA / "topic_index_taxonomy.json"
    taxonomy = json.loads(path.read_text(encoding="utf-8"))
    anatomy = taxonomy["subjects"]["Anatomy"]
    assert [str(x["id"]) for x in anatomy["topics"]] == [str(i) for i in range(1, 49)]
    planned_slots = {topic["slot"] for section in anatomy["plannedIndex"] for topic in section["topics"]}
    for chapter in range(60, 64):
        section, slots = TAXONOMY[chapter]
        assert set(slots) <= planned_slots
        anatomy["topics"].append({"id": str(chapter), "title": titles[chapter], "section": section, "plannedSlots": slots})
    path.write_text(json.dumps(taxonomy, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def update_runtime_and_tests() -> None:
    apply = ROOT / "tools" / "apply_marrow_bank_pilot.py"
    replace_exact(apply, 'load_expanded_bank("anatomy_phase_a","Anatomy")', f'load_expanded_bank("{NEW_PREFIX}","Anatomy")', 1)
    replace_exact(apply, "if len(expanded_ids)!=2376 or len(expanded_ids)!=len(set(expanded_ids)):", "if len(expanded_ids)!=2455 or len(expanded_ids)!=len(set(expanded_ids)):", 1)

    pilot = ROOT / "tools" / "test_marrow_bank_pilot.py"
    replace_exact(pilot, "load_expanded('anatomy_phase_a')", f"load_expanded('{NEW_PREFIX}')", 1)
    replace_exact(pilot, "full_anatomy_manifest['scope']=='phase_a_ch001_048' and len(fa_q)==819 and len(fa_t)==48", "full_anatomy_manifest['scope']=='ch001_048_plus_ch060_063' and len(fa_q)==898 and len(fa_t)==52", 1)
    replace_exact(pilot, "len(all_expanded)==2376 and len({q['id'] for q in all_expanded})==2376", "len(all_expanded)==2455 and len({q['id'] for q in all_expanded})==2455", 1)
    replace_exact(pilot, "'marrow__ANAT_CH48_Q011'", "'marrow__ANAT_CH48_Q011','marrow__ANAT_CH60_Q001','marrow__ANAT_CH63_Q013'", 1)
    replace_exact(pilot, "MARROW_DATA_OK anatomy=819/48 biochemistry=543/26 physiology=1014/43 total=2376", "MARROW_DATA_OK anatomy=898/52 biochemistry=543/26 physiology=1014/43 total=2455", 1)
    replace_exact(pilot, "MARROW_BANK_PILOT_TEST_OK anatomy=819/48 biochemistry=543/26 physiology=1014/43 total=2376", "MARROW_BANK_PILOT_TEST_OK anatomy=898/52 biochemistry=543/26 physiology=1014/43 total=2455", 1)

    inv = ROOT / "tools" / "inventory_marrow_explanations.py"
    replace_exact(inv, '"Anatomy": "anatomy_phase_a"', f'"Anatomy": "{NEW_PREFIX}"', 1)
    replace_exact(inv, '== 2376', '== 2455')
    replace_exact(inv, '2376 - enhanced', '2455 - enhanced')
    replace_exact(inv, 'pending={2376-enhanced}', 'pending={2455-enhanced}')

    invtest = ROOT / "tools" / "test_marrow_explanation_inventory.py"
    replace_exact(invtest, '== 2376', '== 2455')
    replace_exact(invtest, '{"Anatomy": 819, "Biochemistry": 543, "Physiology": 1014}', '{"Anatomy": 898, "Biochemistry": 543, "Physiology": 1014}', 1)
    replace_exact(invtest, '2376 - enhanced', '2455 - enhanced')
    replace_exact(invtest, 'questions=2376', 'questions=2455')
    replace_exact(invtest, 'pending={2376-enhanced}', 'pending={2455-enhanced}')

    biochem_rollout = ROOT / "tools" / "test_marrow_biochem_explanation_rollout.py"
    if biochem_rollout.exists():
        replace_exact(biochem_rollout, '"pending": 2192', '"pending": 2271', 1)
        replace_exact(biochem_rollout, 'pending=2192', 'pending=2271', 1)

    images = ROOT / "tools" / "marrow_images.py"
    replace_exact(images, "'Anatomy': ('anatomy_phase_a', 'Anatomy_ed8.pdf')", f"'Anatomy': ('{NEW_PREFIX}', 'Anatomy_ed8.pdf')", 1)
    image_test = ROOT / "tools" / "test_marrow_images.py"
    replace_exact(image_test, 'assert len(questions())==2376', 'assert len(questions())==2455', 1)


def update_taxonomy_test() -> None:
    path = ROOT / "tools" / "test_marrow_topic_taxonomy.py"
    text = path.read_text(encoding="utf-8")
    anchors = {
        '"Anatomy": "anatomy_phase_a"': f'"Anatomy": "{NEW_PREFIX}"',
        'assert nonempty_sections(anatomy) == ANATOMY_SECTION_ORDER[:7]': 'assert nonempty_sections(anatomy) == ANATOMY_SECTION_ORDER[:7] + ["General anatomy"]',
        'assert flatten_current(anatomy) == [str(i) for i in range(1, 49)]': 'assert flatten_current(anatomy) == [str(i) for i in range(1, 49)] + ["60", "61", "62", "63"]',
        'assert total == 117': 'assert total == 121',
        'current_topics=117': 'current_topics=121',
        'anatomy_visible=48': 'anatomy_visible=52',
    }
    for old, new in anchors.items():
        if text.count(old) != 1:
            raise AssertionError(f"taxonomy test anchor {old!r}: {text.count(old)}")
        text = text.replace(old, new, 1)
    slot_anchor = '    assert flatten_current(anatomy) == [str(i) for i in range(1, 49)] + ["60", "61", "62", "63"]\n'
    slot_assert = '''    assert {str(item["id"]): item["plannedSlots"] for item in anatomy["topics"] if int(item["id"]) >= 60} == {\n        "60": ["general-anatomy:01"],\n        "61": ["general-anatomy:02"],\n        "62": ["general-anatomy:03"],\n        "63": ["general-anatomy:04", "general-anatomy:05"],\n    }\n'''
    assert text.count(slot_anchor) == 1
    text = text.replace(slot_anchor, slot_anchor + slot_assert, 1)
    path.write_text(text, encoding="utf-8")


def update_browser_wrapper() -> None:
    path = ROOT / "tools" / "verify_marrow_bank_browser.py"
    text = path.read_text(encoding="utf-8")
    insertion = '''\n# Anatomy Ch60-63 source expansion layered on top of the current core.\nanatomy_replacements = {\n    "            for marker in ('PrepLadder','Marrow','1,068','819'):": "            for marker in ('PrepLadder','Marrow','1,068','898'):",\n    "            if page.locator('button.nk-topic-row').count()!=48: raise SystemExit('Marrow Anatomy topic count is not 48')": "            if page.locator('button.nk-topic-row').count()!=52: raise SystemExit('Marrow Anatomy topic count is not 52')",\n    "            assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis'])": "            assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis','General anatomy'])",\n    "            if serials!=[str(i) for i in range(1,49)]: raise SystemExit(f'Marrow Anatomy learner numbering is not contiguous: {serials!r}')": "            if serials!=[str(i) for i in range(1,53)]: raise SystemExit(f'Marrow Anatomy learner numbering is not contiguous 1-52: {serials!r}')",\n}\nfor old, new in anatomy_replacements.items():\n    if source.count(old) != 1:\n        raise SystemExit(f"Anatomy browser source-count/taxonomy anchor count for {old!r}: {source.count(old)}")\n    source = source.replace(old, new, 1)\n\nshot_anchor = "            page.screenshot(path=str(OUT/'02-marrow-topics.png'),full_page=True)"\nshot_new = shot_anchor + """\n            page.locator('button.nk-topic-row').filter(has_text='Bones, Joints and Cartilage').click();page.wait_for_timeout(80)\n            if page.locator('button.nk-library-row').count()!=30: raise SystemExit('Marrow Anatomy Bones, Joints and Cartilage count is not 30')\n            page.locator('button.nk-library-row').nth(0).click();page.wait_for_timeout(80)\n            anatomy_learner_text=page.locator('body').inner_text()\n            for raw_marker in ('question_id','chapter_number','correct_option','schema_version','review_status','source_fidelity'):\n                if raw_marker in anatomy_learner_text: raise SystemExit(f'Raw Anatomy automation JSON key leaked into learner view: {raw_marker}')\n            for raw_fragment in ('{\\\"question_id\\\"','\\\"correct_option\\\":','\\\"source_fidelity\\\":'):\n                if raw_fragment in anatomy_learner_text: raise SystemExit(f'Serialized Anatomy automation JSON leaked into learner view: {raw_fragment}')\n            if 'total number of bones' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('New Anatomy Ch60 source question did not render normally')\n            page.evaluate(\"window.QB.nav('banks','Anatomy')\");page.wait_for_timeout(80)\n            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)\n"""\nif source.count(shot_anchor) != 1:\n    raise SystemExit(f"Anatomy learner leakage insertion anchor count: {source.count(shot_anchor)}")\nsource = source.replace(shot_anchor, shot_new, 1)\nsource = source.replace('anatomy=819/48', 'anatomy=898/52')\n'''
    exec_anchor = "\nexec(\n    compile(source, str(CORE), \"exec\"),"
    if text.count(exec_anchor) != 1:
        raise AssertionError(f"browser exec anchor count: {text.count(exec_anchor)}")
    text = text.replace(exec_anchor, insertion + exec_anchor, 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    old, old_manifest = load_bundle(OLD_PREFIX)
    assert old.get("subject") == "Anatomy" and old.get("bank") == "Marrow"
    assert len(old.get("topics", [])) == 48 and len(old.get("questions", [])) == 819
    old_ids = {str(q["id"]) for q in old["questions"]}

    source_rows = {chapter: read_rows(chapter, path) for chapter, path in NEW_FILES.items()}
    assert sum(len(rows) for rows in source_rows.values()) == 79
    titles = {chapter: str(rows[0]["chapter"]) for chapter, rows in source_rows.items()}

    topics = list(old["topics"])
    questions = list(old["questions"])
    for chapter in range(60, 64):
        rows = source_rows[chapter]
        pages = [p for row in rows for p in ((row.get("source") or {}).get("question_pages") or [])]
        topics.append({
            "id": str(chapter), "title": titles[chapter], "subject": "Anatomy", "bank": "Marrow",
            "questionCount": len(rows), "startPage": min(pages) if pages else None,
        })
        questions.extend(adapt_question(row) for row in rows)

    ids = [str(q["id"]) for q in questions]
    assert len(topics) == 52 and len(questions) == 898
    assert len(ids) == len(set(ids)) == 898
    assert old_ids.issubset(set(ids))
    assert all(qid.startswith("marrow__") for qid in ids)

    record = dict(old)
    record["scope"] = "ch001_048_plus_ch060_063"
    record["topics"] = topics
    record["questions"] = questions
    stats = dict(record.get("stats") or {})
    for key in list(stats):
        low = key.lower().replace("_", "")
        if low in {"topics", "topiccount"}: stats[key] = 52
        if low in {"questions", "questioncount"}: stats[key] = 898
    record["stats"] = stats

    write_bundle(record, old_manifest, source_rows)
    update_taxonomy(titles)
    update_runtime_and_tests()
    update_taxonomy_test()
    update_browser_wrapper()
    print("ANATOMY_AUTOMATION_INGEST_OK chapters=60-63 source_gap=49-59 new_questions=79 anatomy=898/52 global=2455/121 raw_ui_schema=adapted")


if __name__ == "__main__":
    main()
