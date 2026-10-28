#!/usr/bin/env python3
"""PrepLadder Version XI from the saved web exports (QBank, Elite QBank, All PYQs).

tools/prepladder_qbank_import.py merges the three exports into
data/Prepladder/qbank/<slug>/source.jsonl plus the original figures. This builder
turns each subject into a `prepladder-qbank-1.0` record with ordered-block
explanations (tools/marrow_qbank_bank.py's HTML converter), writes its hash-pinned
shards and lists the figures, which the app loads from PrepLadder's image server.

Two kinds of subject:

  * new subjects (Third and Final Prof): a whole bank, lessons = the QBank's lesson tests;
  * supplements to the PDF banks (Anatomy, Physiology, Biochemistry, Microbiology,
    Pathology, Pharmacology): only the questions those banks lack, each filed under
    the existing lesson; `merged_record()` adds them to the PDF bank's record.

  python3 tools/prepladder_qbank_bank.py            # rebuild shards + visuals.json
  python3 tools/prepladder_qbank_bank.py --check    # fail if any shard or inventory is stale
"""
from __future__ import annotations

import argparse
import base64
import importlib
import json
import re
import zlib
from pathlib import Path

from marrow_qbank_bank import Converter, STEM_HTML, fail, plain_text, sha256, stem, unescape

ROOT = Path(__file__).resolve().parents[1]
QBANK = ROOT / "data/Prepladder/qbank"
SHARD_CHARS = 60000
SOURCE_LABEL = "PrepLadder Version XI (web export)"
SOURCE_FILES = {"elite": "PrepLadder Version XI Elite QBank.html", "qbank": "PrepLadder Version XI QBank.html",
                "qbank-earlier": "PrepLadder Version XI QBank.html", "pyq": "All PYQs PrepLadder.html"}

# slug: export folder, app subject, prof group, expected counts after the build.
SUBJECTS: dict[str, dict] = {
    "community-medicine": {"folder": "PSM", "subject": "Community Medicine", "prof": "third"},
    "forensic-medicine": {"folder": "Forensic Medicine", "subject": "Forensic Medicine", "prof": "third"},
    "ophthalmology": {"folder": "Ophthalmology", "subject": "Ophthalmology", "prof": "third"},
    "ent": {"folder": "ENT", "subject": "ENT", "prof": "third"},
    "medicine": {"folder": "Medicine", "subject": "Medicine", "prof": "final"},
    "surgery": {"folder": "Surgery", "subject": "Surgery", "prof": "final"},
    "obstetrics-gynaecology": {"folder": "Gynaecology _ Obstetrics", "subject": "Obstetrics & Gynaecology", "prof": "final"},
    "paediatrics": {"folder": "Pediatrics", "subject": "Paediatrics", "prof": "final"},
    "orthopaedics": {"folder": "Orthopaedics", "subject": "Orthopaedics", "prof": "final"},
    "dermatology": {"folder": "Dermatology", "subject": "Dermatology", "prof": "final"},
    "psychiatry": {"folder": "Psychiatry", "subject": "Psychiatry", "prof": "final"},
    "radiology": {"folder": "Radiology", "subject": "Radiology", "prof": "final"},
    "anaesthesia": {"folder": "Anaesthesia", "subject": "Anaesthesia", "prof": "final"},
    # Supplements: the PDF bank module whose app_record() they extend, and its ID prefix.
    "anatomy": {"folder": "Anatomy", "subject": "Anatomy", "prof": "first", "supplement": "build_prepladder_anatomy_bank"},
    "physiology": {"folder": "Physiology", "subject": "Physiology", "prof": "first", "supplement": "build_prepladder_physiology_bank"},
    "biochemistry": {"folder": "Biochemistry", "subject": "Biochemistry", "prof": "first", "supplement": "build_prepladder_biochemistry_bank"},
    "microbiology": {"folder": "Microbiology", "subject": "Microbiology", "prof": "second", "supplement": "build_prepladder_microbiology_bank"},
    "pathology": {"folder": "Pathology", "subject": "Pathology", "prof": "second", "supplement": "build_prepladder_pathology_bank"},
    "pharmacology": {"folder": "Pharmacology", "subject": "Pharmacology", "prof": "second", "supplement": "build_prepladder_pharmacology_bank"},
}
EXPECTED_PATH = QBANK / "expected.json"
RUNTIME = ROOT / "app/src/main/assets/prepladder_qbank_visual_metadata.js"
ANSWER_LEAD = re.compile(r"^\W*Correct answer\s*:", re.I)


def existing_bank(slug: str) -> dict:
    """The PDF bank a supplement extends, exactly as the app ships it today."""
    return importlib.import_module(SUBJECTS[slug]["supplement"]).app_record()


def load_source(slug: str) -> list[dict]:
    path = QBANK / slug / "source.jsonl"
    if not path.exists():
        fail(f"{slug}: {path.relative_to(ROOT)} missing; run tools/prepladder_qbank_import.py")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def question_id(slug: str, qid: str) -> str:
    return f"prepladder-{slug}-q{qid}"


def topic_id(slug: str, lesson: str) -> str:
    return f"prepladder-{slug}-{lesson}"


def question(slug: str, q: dict, converter: Converter, chapter: dict) -> dict:
    qid = q["qid"]
    letters = [o["letter"] for o in q["options"]]
    if letters != ["A", "B", "C", "D"]:
        fail(f"{slug} {qid}: options must be exactly A-D, got {letters}")
    keyed = [i for i, o in enumerate(q["options"], 1) if o["correct"]]
    if len(keyed) != 1:
        fail(f"{slug} {qid}: {len(keyed)} options are keyed correct")
    key = keyed[0]
    code = slug.replace("-", "_").upper()
    text, stem_tables = stem(q["question"], converter, f"{code}_{qid}_S")
    options = [{"letter": o["letter"], "text": unescape(o["text"]).strip()} for o in q["options"]]
    if not text and stem_tables:  # a matching question whose stem is only the table
        text = "Match the following:"
    if not text or any(not o["text"] or STEM_HTML.search(o["text"]) for o in options):
        fail(f"{slug} {qid}: blank stem or option, or markup left in an option")
    blocks, tables = converter.convert(q["explanationHtml"], f"{code}_{qid}")
    # A leading "Correct answer: Option B) …" line in a form the importer's patterns miss;
    # the app shows the key itself.
    while blocks and blocks[0]["type"] in ("paragraph", "heading") and ANSWER_LEAD.match(blocks[0]["text"]):
        blocks = blocks[1:]
    if not blocks:
        blocks = [{"type": "paragraph", "text": "No explanation is given for this question in the source."}]
    flat = plain_text(blocks, {t["table_id"]: t for t in tables})
    record = {
        "id": question_id(slug, qid), "sourceQuestionId": f"PREPLADDER_QBANK_{qid}", "prepladderQid": f"Q{qid}",
        "subject": SUBJECTS[slug]["subject"], "bank": "PrepLadder",
        "chapterId": chapter["id"], "chapter": chapter["title"], "topic": chapter["title"],
        "questionNumber": int(q["number"]), "questionType": "single_best_answer",
        "question": text, "options": options, "correctOption": key, "correctAnswerText": options[key - 1]["text"],
        "explanation": flat, "explanationFormat": "structured",
        "structuredExplanation": {"layout": "ordered-blocks", "text": flat, "blocks": blocks, "tables": tables,
                                  "figures": [i["url"] for i in q["images"]]},
        "provenance": {"sourceFile": SOURCE_FILES[q["origin"]], "sourceLabel": SOURCE_LABEL,
                       "origin": q["origin"], "sourceTestId": q["testId"]},
        "reviewStatus": "pass", "imageDependent": any(i["role"] == "question" for i in q["images"]),
    }
    if stem_tables:
        record["stemTables"] = stem_tables
    if q.get("exams"):
        record["exams"] = q["exams"]
    return record


def normalize(slug: str) -> dict:
    cfg = SUBJECTS[slug]
    rows = load_source(slug)
    converter, questions, seen = Converter(), [], set()
    if cfg.get("supplement"):
        bank = existing_bank(slug)
        chapters = {t["id"]: t for t in bank["topics"]}
        prefix = bank["questions"][0]["id"].split("-")[0]
        taken = {q["id"] for q in bank["questions"]}
        for q in rows:
            chapter = chapters.get(q["topicId"])
            if not chapter:
                fail(f"{slug} {q['qid']}: unknown lesson {q['topicId']}")
            record = question(slug, q, converter, chapter)
            record["id"] = f"{prefix}-q{q['qid']}"
            if record["id"] in taken or record["id"] in seen:
                fail(f"{slug}: question ID {record['id']} is already used")
            seen.add(record["id"])
            questions.append(record)
        record = {"schema_version": "prepladder-qbank-1.0", "kind": "supplement", "subject": cfg["subject"],
                  "bank": "PrepLadder", "extends": cfg["supplement"], "topics": [], "questions": questions}
    else:
        # Topics come ordered and titled by the importer (the official app's indexes, indexes.json).
        topics: dict[str, dict] = {}
        for q in rows:
            lesson = str(q["lesson"])
            t = topics.setdefault(lesson, {
                "id": topic_id(slug, lesson), "subject": cfg["subject"], "bank": "PrepLadder",
                "title": q["lessonTitle"], "section": q["section"], "pyq": bool(q["pyq"]),
                "sourceTestId": q["testId"], "order": int(q["topicOrder"]), "count": 0})
            if t["order"] != int(q["topicOrder"]) or t["section"] != q["section"]:
                fail(f"{slug} {q['qid']}: topic {lesson} has two places")
            record = question(slug, q, converter, t)
            if record["id"] in seen:
                fail(f"{slug}: question ID {record['id']} twice")
            seen.add(record["id"])
            t["count"] += 1
            questions.append(record)
        ordered = sorted(topics, key=lambda k: topics[k]["order"])
        sections = [topics[k]["section"] for k in ordered]
        if len(set(sections)) != len([s for n, s in enumerate(sections) if not n or s != sections[n - 1]]):
            fail(f"{slug}: an index is split into two runs")
        topic_list = []
        for k in ordered:
            t = topics[k]
            t.pop("order")
            count = t.pop("count")
            topic_list.append({**t, "questionCount": count, "sourceQuestionTotal": count, "complete": True})
        position = {t["id"]: n for n, t in enumerate(topic_list)}
        questions.sort(key=lambda r: (position[r["chapterId"]], r["questionNumber"]))
        record = {"schema_version": "prepladder-qbank-1.0", "kind": "bank", "subject": cfg["subject"],
                  "bank": "PrepLadder", "prof": cfg["prof"], "explanationFormat": "structured",
                  "topics": topic_list, "questions": questions}
    record["stats"] = {"questions": len(questions), "topics": len(record["topics"]),
                       "byOrigin": {o: sum(1 for q in questions if q["provenance"]["origin"] == o)
                                    for o in sorted({q["provenance"]["origin"] for q in questions})},
                       "withExams": sum(1 for q in questions if q.get("exams"))}
    return record


def prefix(slug: str) -> str:
    return f"{slug.replace('-', '_')}_prepladder_qbank"


def shard(slug: str, record: dict) -> tuple[list[str], dict]:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    parts = [encoded[i:i + SHARD_CHARS] for i in range(0, len(encoded), SHARD_CHARS)]
    return parts, {
        "schema_version": "1.0", "subject": record["subject"], "bank": "PrepLadder", "kind": record["kind"],
        "source": f"data/Prepladder/qbank/{slug}/source.jsonl",
        "sourceSha256": sha256((QBANK / slug / "source.jsonl").read_bytes()),
        "builder": "tools/prepladder_qbank_bank.py", "topics": len(record["topics"]),
        "questions": len(record["questions"]), "parts": len(parts), "base64_chars": len(encoded),
        "compressed_sha256": sha256(compressed), "raw_sha256": sha256(raw),
    }


def stored_record(slug: str) -> dict:
    """The hash-verified shards of one subject."""
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
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))[slug]
    if record["stats"]["questions"] != expected["questions"] or record["subject"] != SUBJECTS[slug]["subject"]:
        fail(f"{slug}: unexpected identity or counts {record['stats']['questions']} (expected {expected})")
    return record


def app_records() -> list[dict]:
    """New PrepLadder subjects, as embedded in MARROW_DATA.records."""
    return [stored_record(slug) for slug, cfg in SUBJECTS.items() if not cfg.get("supplement")]


def shipped_counts(slug: str) -> dict:
    """What a PDF bank shows once merged: questions, and questions in its Previous Year Questions lessons."""
    record = merged_record(slug, existing_bank(slug))
    pyq = sum(t["questionCount"] for t in record["topics"] if "Previous Year" in t["title"])
    return {"questions": len(record["questions"]), "pyq": pyq}


def merged_record(slug: str, base: dict) -> dict:
    """A PDF bank's record with the web-export questions it lacked filed under its lessons."""
    extra = stored_record(slug)["questions"]
    if not extra:
        return base
    taken = {q["id"] for q in base["questions"]}
    clash = [q["id"] for q in extra if q["id"] in taken]
    if clash:
        fail(f"{slug}: supplement IDs already in the PDF bank: {clash[:3]}")
    added: dict[str, list[dict]] = {}
    for q in extra:
        added.setdefault(q["chapterId"], []).append(q)
    own: dict[str, list[dict]] = {}
    for q in base["questions"]:
        own.setdefault(q["chapterId"], []).append(q)
    unknown = sorted(set(added) - {t["id"] for t in base["topics"]})
    if unknown:
        fail(f"{slug}: supplement questions in unknown lessons {unknown[:3]}")
    questions, topics = [], []
    for t in base["topics"]:
        mine, more = own.get(t["id"], []), added.get(t["id"], [])
        last = max([q.get("questionNumber") or 0 for q in mine] or [0])
        questions += mine + [{**q, "questionNumber": last + n} for n, q in enumerate(more, 1)]
        topic = dict(t)
        if more:
            topic["questionCount"] = len(mine) + len(more)
            if "sourceQuestionTotal" in topic:
                topic["sourceQuestionTotal"] += len(more)
        topics.append(topic)
    # Questions of the PDF bank outside any topic keep their place at the end.
    listed = {t["id"] for t in base["topics"]}
    questions += [q for q in base["questions"] if q["chapterId"] not in listed]
    return {**base, "topics": topics, "questions": questions}


def inventory(slug: str, record: dict) -> dict:
    """Every figure the subject uses: PrepLadder's link plus the type and size the importer probed."""
    images_of = {f"PREPLADDER_QBANK_{row['qid']}": row["images"] for row in load_source(slug)}
    figures = []
    for q in record["questions"]:
        for image in images_of[q["sourceQuestionId"]]:
            if not image.get("width") or not image.get("height") or not image.get("type"):
                fail(f"{q['id']}: figure {image['url']} was never probed; rerun tools/prepladder_qbank_import.py")
            if not image["url"].startswith("https://image.prepladder.com/"):
                fail(f"{q['id']}: figure link outside PrepLadder's image server: {image['url']}")
            figures.append({"questionId": q["id"], "role": image["role"], "order": image["order"],
                            "url": image["url"], "type": image["type"], "bytes": image["bytes"],
                            "width": image["width"], "height": image["height"]})
    return {"schemaVersion": 2, "subject": record["subject"], "bank": "PrepLadder",
            "note": "Originals on PrepLadder's image server, shown in place (owner's choice, 2026-10-28).",
            "figures": figures}


def runtime_visuals() -> dict[str, list[dict]]:
    """window.MARROW_VISUALS entries (marrow_visual_renderer.js) for every subject."""
    runtime: dict[str, list[dict]] = {}
    for slug, cfg in SUBJECTS.items():
        for f in json.loads((QBANK / slug / "visuals.json").read_text(encoding="utf-8"))["figures"]:
            n = f["order"]
            runtime.setdefault(f["questionId"], []).append({
                "id": f"prepladder-qbank-{f['questionId']}-{f['role'][0]}{n}", "role": f["role"], "order": n,
                "src": f["url"], "alt": f"{cfg['subject']} {f['role']} figure {n}", "status": "PASS",
                "width": f["width"], "height": f["height"], "bytes": f["bytes"]})
    return runtime


def release() -> None:
    """Write the runtime figure metadata (the figures themselves stay on PrepLadder's server)."""
    runtime = runtime_visuals()
    payload = json.dumps(runtime, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")
    RUNTIME.write_text("/* PrepLadder QBank figures (generated by tools/prepladder_qbank_bank.py). */\n"
                       f"window.MARROW_VISUALS=Object.assign(window.MARROW_VISUALS||{{}},{payload});\n", encoding="utf-8")
    print(f"PREPLADDER_QBANK_VISUALS_OK questions={len(runtime)} figures={sum(map(len, runtime.values()))}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = json.loads(EXPECTED_PATH.read_text(encoding="utf-8")) if EXPECTED_PATH.exists() else {}
    stale = []
    for slug in args.slugs or list(SUBJECTS):
        folder = QBANK / slug
        record = normalize(slug)
        parts, manifest = shard(slug, record)
        visuals = inventory(slug, record)
        files = {f"{prefix(slug)}.zlib.b64.part{i:02d}": p for i, p in enumerate(parts)}
        files[f"{prefix(slug)}_manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        files["visuals.json"] = json.dumps(visuals, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
        if args.check:
            for name, text in files.items():
                if not (folder / name).exists() or (folder / name).read_text(encoding="utf-8") != text:
                    stale.append(f"{slug}/{name}")
            extra = {p.name for p in folder.glob(f"{prefix(slug)}.zlib.b64.part*")} - set(files)
            stale += [f"{slug}/{n} (extra)" for n in sorted(extra)]
            if expected.get(slug, {}).get("questions") != record["stats"]["questions"]:
                stale.append(f"{slug}/expected.json")
        else:
            for old in folder.glob(f"{prefix(slug)}.zlib.b64.part*"):
                old.unlink()
            for name, text in files.items():
                (folder / name).write_text(text, encoding="utf-8")
            expected[slug] = {"questions": record["stats"]["questions"], "topics": record["stats"]["topics"]}
        print(f"PREPLADDER_QBANK_BANK_OK {slug} {record['kind']} questions={record['stats']['questions']} "
              f"topics={record['stats']['topics']} figures={len(visuals['figures'])} parts={len(parts)}")
    if args.check and stale:
        fail("stale PrepLadder QBank outputs (run tools/prepladder_qbank_bank.py): " + ", ".join(stale[:8]))
    if not args.check:
        EXPECTED_PATH.write_text(json.dumps(expected, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
