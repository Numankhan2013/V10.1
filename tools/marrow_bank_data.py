#!/usr/bin/env python3
"""Load, validate and compile the Marrow bank data the app embeds.

Every Marrow question, learner-display override and approved explanation comes
from the hash-verified shards and reviewed JSON files under data/marrow. Nothing
here edits the app; tools/build_app_data.py writes the results into index.html.
"""
from __future__ import annotations

import base64
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/marrow"


def fail(message: str) -> None:
    raise SystemExit(f"CANONICAL_WIRING_ERROR: {message}")


def load_sharded(prefix: str) -> dict:
    manifest_path = DATA / f"{prefix}_manifest.json"
    if not manifest_path.exists():
        fail(f"missing manifest: {manifest_path.name}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if len(parts) != int(manifest.get("parts", 0)):
        fail(f"{prefix} shard count mismatch: {len(parts)}")
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    if "base64_chars" in manifest and len(encoded) != int(manifest["base64_chars"]):
        fail(f"{prefix} base64 length mismatch")
    try:
        compressed = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        fail(f"{prefix} invalid base64: {exc}")
    if "compressed_bytes" in manifest and len(compressed) != int(manifest["compressed_bytes"]):
        fail(f"{prefix} compressed length mismatch")
    if hashlib.sha256(compressed).hexdigest() != manifest.get("compressed_sha256"):
        fail(f"{prefix} compressed SHA-256 mismatch")
    try:
        raw = zlib.decompress(compressed)
    except Exception as exc:
        fail(f"{prefix} invalid zlib payload: {exc}")
    if "raw_bytes" in manifest and len(raw) != int(manifest.get("raw_bytes", 0)):
        fail(f"{prefix} raw length mismatch")
    if hashlib.sha256(raw).hexdigest() != manifest.get("raw_sha256"):
        fail(f"{prefix} raw SHA-256 mismatch")
    return json.loads(raw.decode("utf-8"))


def canonical_source_questions() -> dict[str, dict]:
    specs = (
        ("anatomy_ch001_063", "Anatomy", 1115),
        ("biochemistry_ch001_028", "Biochemistry", 582),
        ("physiology_ch001_043", "Physiology", 1014),
    )
    by_id: dict[str, dict] = {}
    for prefix, subject, expected in specs:
        record = load_sharded(prefix)
        if record.get("subject") != subject or record.get("bank") != "Marrow":
            fail(f"{subject} canonical source identity mismatch")
        questions = record.get("questions", [])
        if len(questions) != expected:
            fail(f"{subject} canonical source count mismatch: {len(questions)}")
        for q in questions:
            qid = str(q.get("id", ""))
            if not qid or qid in by_id:
                fail(f"duplicate/blank canonical source ID: {qid}")
            by_id[qid] = q
    if len(by_id) != 2711:
        fail(f"canonical source total mismatch: {len(by_id)}")
    return by_id


def physiology_reference_questions() -> dict[str, dict]:
    record = load_sharded("explanation_physio_pilot")
    questions = record.get("questions", {})
    if record.get("scope", {}).get("subject") != "Physiology" or len(questions) != 80:
        fail("Physiology reference explanation identity/count mismatch")
    return questions


def validate_augmented_question(qid: str, cfg: dict, source_q: dict, origin: str) -> None:
    takeaway = str(cfg.get("takeaway", "")).strip()
    display = str(cfg.get("displayText", "")).strip()
    if not takeaway or not display:
        fail(f"{origin}: missing takeaway/displayText for {qid}")
    emphasis = cfg.get("emphasis", [])
    if not isinstance(emphasis, list) or not (1 <= len(emphasis) <= 4):
        fail(f"{origin}: invalid emphasis count for {qid}")
    if any(not str(p).strip() for p in emphasis):
        fail(f"{origin}: blank emphasis anchor for {qid}")
    if any(str(p) not in display for p in emphasis):
        fail(f"{origin}: emphasis anchor absent from display text for {qid}")
    if "sourceText" in cfg:
        fail(f"{origin}: learner augmentation embeds forbidden sourceText for {qid}")
    options = source_q.get("options", [])
    correct = int(source_q.get("correctOption", 0))
    if len(options) != 4 or correct not in (1, 2, 3, 4):
        fail(f"{origin}: invalid canonical option shape for {qid}")
    wrong = {
        str(opt.get("letter") or chr(64 + index)).lower()
        for index, opt in enumerate(options, 1)
        if index != correct
    }
    rationales = cfg.get("rationales", {})
    if len(rationales) != 3 or set(rationales) != wrong:
        fail(f"{origin}: distractor rationale mapping mismatch for {qid}")
    if any(not str(reason).strip() for reason in rationales.values()):
        fail(f"{origin}: blank distractor rationale for {qid}")
    if 'displayTables' in cfg:
        reconstruction = cfg.get('reconstruction', {})
        if reconstruction.get('status') != 'resolved_reconstruction' or not all(
            reconstruction.get(key) for key in ('sourceProblem', 'reconstructedContent', 'evidenceBasis', 'reviewNote')
        ):
            fail(f"{origin}: display tables require resolved source reconstruction for {qid}")
        native = reviewed_table_sources(source_q, cfg)
        reviewed = cfg['displayTables']
        if not isinstance(reviewed, list) or len(reviewed) != len(native):
            fail(f"{origin}: display table ownership/count mismatch for {qid}")
        for table, source_table in zip(reviewed, native):
            if table.get('source_page') != source_table.get('source_page'):
                fail(f"{origin}: display table source page mismatch for {qid}")
            columns, rows = table.get('columns'), table.get('rows')
            if not isinstance(columns, list) or not columns or not isinstance(rows, list) or not rows:
                fail(f"{origin}: empty reviewed display table for {qid}")
            if any(not isinstance(label, str) or not label.strip() for label in columns):
                fail(f"{origin}: invalid reviewed table header for {qid}")
            if any(not isinstance(row, list) or len(row) != len(columns) or any(
                not isinstance(cell, str) or not cell.strip() for cell in row
            ) for row in rows):
                fail(f"{origin}: invalid reviewed table cells for {qid}")


def reviewed_table_sources(source_q: dict, cfg: dict) -> list[dict]:
    """Include explicitly recovered source table blocks whose objects were omitted."""
    structured = source_q.get('structuredExplanation') or {}
    native = structured.get('tables') or []
    reconstruction = cfg.get('reconstruction') or {}
    recovered = reconstruction.get('orphanTableIds') or []
    native_ids = {table.get('table_id') for table in native}
    block_ids = {block.get('table_id') for block in structured.get('blocks', []) if block.get('type') == 'table'}
    if len(set(recovered)) != len(recovered) or not set(recovered) <= block_ids - native_ids:
        fail('Recovered table must match an omitted native source block')
    provenance = source_q.get('provenance') or {}
    pages = provenance.get('explanationPages') or provenance.get('explanation_pages') or []
    reviewed = cfg.get('displayTables') or []
    result = list(native)
    for table_id in recovered:
        matches = [table for table in reviewed if table.get('table_id') == table_id]
        if len(matches) != 1 or matches[0].get('source_page') not in pages:
            fail('Recovered table must have a unique ID and original explanation page')
        result.append({'table_id': table_id, 'source_page': matches[0]['source_page']})
    return result


def approved_batch(record: dict, path: Path, expected_subject: str) -> bool:
    scope = record.get("scope", {})
    questions = record.get("questions", {})
    if scope.get("subject") != expected_subject or scope.get("bank") != "Marrow" or not questions:
        fail(f"{path.name}: explanation batch identity/status mismatch")
    status = scope.get("status")
    if status not in {"candidate-rollout", "approved-reference", "approved-rollout"}:
        fail(f"{path.name}: explanation batch identity/status mismatch")
    if int(scope.get("questions", 0)) != len(questions):
        fail(f"{path.name}: declared explanation count mismatch")
    return status != "candidate-rollout"


def merged_explanations(source_by_id: dict[str, dict]) -> dict[str, dict]:
    anatomy_reference = json.loads((DATA / "explanation_gold_pilot.json").read_text(encoding="utf-8")).get("questions", {})
    if len(anatomy_reference) != 62:
        fail(f"Anatomy reference count mismatch: {len(anatomy_reference)}")
    phys_reference = physiology_reference_questions()

    merged: dict[str, dict] = {}
    for origin, questions in (("Anatomy reference", anatomy_reference), ("Physiology reference", phys_reference)):
        for qid, cfg in questions.items():
            if qid not in source_by_id:
                fail(f"{origin}: unknown source ID {qid}")
            if qid in merged:
                fail(f"{origin}: duplicate explanation ID {qid}")
            if len(cfg.get("rationales", {})) != 3:
                fail(f"{origin}: expected three rationales for {qid}")
            merged[qid] = cfg

    patterns = (
        ("Anatomy", "explanation_anatomy_ch*_v1.json"),
        ("Biochemistry", "explanation_biochem_*_v1.json"),
        ("Physiology", "explanation_physio_ch*_v1.json"),
    )
    batch_counts: dict[str, int] = {}
    for expected_subject, pattern in patterns:
        paths = sorted(DATA.glob(pattern))
        if not paths:
            fail(f"no approved {expected_subject} rollout files found for {pattern}")
        for path in paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            if not approved_batch(record, path, expected_subject):
                continue
            questions = record["questions"]
            for qid, cfg in questions.items():
                if qid in merged:
                    fail(f"{path.name}: duplicate explanation ID {qid}")
                source_q = source_by_id.get(qid)
                if not source_q:
                    fail(f"{path.name}: unknown canonical source ID {qid}")
                if str(source_q.get("subject", expected_subject)) != expected_subject:
                    fail(f"{path.name}: source subject mismatch for {qid}")
                validate_augmented_question(qid, cfg, source_q, path.name)
                merged[qid] = cfg
            batch_counts[path.name] = len(questions)

    inventory = json.loads((DATA / "explanation_inventory_v1.json").read_text(encoding="utf-8"))
    summary = inventory.get("summary", {})
    expected_enhanced = int(summary.get("enhancementStatus", {}).get("enhanced-reference", -1))
    if int(summary.get("questions", 0)) != 2711:
        fail("explanation inventory denominator is not the canonical 2,711 questions")
    if len(merged) != expected_enhanced:
        fail(f"runtime enhanced map mismatch: runtime={len(merged)} inventory={expected_enhanced}")
    for required in (
        "marrow__ANAT_CH05_Q001",
        "marrow__ANAT_CH05_Q019",
        "marrow__BIOCHEM_CH11_Q001",
        "marrow__PHYS_CH10_Q018",
    ):
        if required not in merged:
            fail(f"verified rollout missing from runtime map: {required}")
    print(f"CANONICAL_EXPLANATION_MAP_OK enhanced={len(merged)} batches={len(batch_counts)}")
    return merged


def load_expanded_bank(prefix: str, expected_subject: str):
    manifest_path=DATA/f"{prefix}_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Expanded Marrow manifest missing: {manifest_path.name}")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    parts=sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if len(parts)!=int(manifest.get("parts",0)):
        raise SystemExit(f"{expected_subject} expanded shard count mismatch: {len(parts)}")
    encoded="".join(p.read_text(encoding="utf-8").strip() for p in parts)
    if len(encoded)!=int(manifest.get("base64_chars",0)):
        raise SystemExit(f"{expected_subject} expanded base64 length mismatch")
    try:
        compressed=base64.b64decode(encoded,validate=True)
    except Exception as exc:
        raise SystemExit(f"{expected_subject} expanded base64 invalid: {exc}") from exc
    if len(compressed)!=int(manifest.get("compressed_bytes",0)):
        raise SystemExit(f"{expected_subject} expanded compressed length mismatch")
    if hashlib.sha256(compressed).hexdigest()!=manifest.get("compressed_sha256"):
        raise SystemExit(f"{expected_subject} expanded compressed SHA-256 mismatch")
    try:
        raw=zlib.decompress(compressed)
    except Exception as exc:
        raise SystemExit(f"{expected_subject} expanded zlib invalid: {exc}") from exc
    if len(raw)!=int(manifest.get("raw_bytes",0)):
        raise SystemExit(f"{expected_subject} expanded raw length mismatch")
    if hashlib.sha256(raw).hexdigest()!=manifest.get("raw_sha256"):
        raise SystemExit(f"{expected_subject} expanded raw SHA-256 mismatch")
    record=json.loads(raw.decode("utf-8"))
    if record.get("subject")!=expected_subject or record.get("bank")!="Marrow":
        raise SystemExit(f"{expected_subject} expanded identity mismatch")
    topics=record.get("topics",[])
    questions=record.get("questions",[])
    if len(topics)!=int(manifest.get("topics",0)):
        raise SystemExit(f"{expected_subject} expanded topic count mismatch")
    if len(questions)!=int(manifest.get("questions",0)):
        raise SystemExit(f"{expected_subject} expanded question count mismatch")
    ids=[str(q.get("id","")) for q in questions]
    if len(ids)!=len(set(ids)) or any(not qid.startswith("marrow__") for qid in ids):
        raise SystemExit(f"{expected_subject} expanded IDs are not unique/namespaced")
    topic_ids={str(t.get("id")) for t in topics}
    if any(str(q.get("chapterId")) not in topic_ids for q in questions):
        raise SystemExit(f"{expected_subject} expanded question/topic linkage mismatch")
    if any(len(q.get("options",[]))!=4 or q.get("correctOption") not in (1,2,3,4) or not str(q.get("question","")).strip() for q in questions):
        raise SystemExit(f"{expected_subject} expanded question shape invalid")
    expected_letters=["A","B","C","D"]
    if any([str(opt.get("letter","")).strip() for opt in q.get("options",[])]!=expected_letters for q in questions):
        raise SystemExit(f"{expected_subject} expanded option-letter contract invalid; expected uppercase A-D")
    return record,manifest


# The immutable ED8 transport preserves source transcription, including OCR
# debris. Apply separately reviewed learner-display overrides only after source
# verification and only to the exact stable IDs/fields declared below.
CONTENT_OVERRIDE_PATHS=(
    DATA/"content_hygiene_overrides_v1.json",
    DATA/"content_hygiene_nerve_ch6_q01_17_v1.json",
    DATA/"content_hygiene_nerve_ch6_q18_34_v1.json",
    DATA/"content_hygiene_phys_ch09_10_v1.json",
    DATA/"content_hygiene_phys_ch11_12_v1.json",
)
CONTENT_OVERRIDE_RANGES={
    "content_hygiene_nerve_ch6_q01_17_v1.json":((6,1,17),),
    "content_hygiene_nerve_ch6_q18_34_v1.json":((6,18,34),),
    "content_hygiene_phys_ch09_10_v1.json":((9,1,27),(10,1,18)),
    "content_hygiene_phys_ch11_12_v1.json":((11,1,21),(12,1,23)),
}


def apply_content_overrides(expanded_records: list[dict]) -> set[str]:
    """Apply the reviewed learner-display overrides in place; return the IDs changed."""
    expanded_source_by_id={
        str(q.get("id","")):q for record in expanded_records for q in record.get("questions",[])
    }
    applied_content_ids=set()
    for content_path in CONTENT_OVERRIDE_PATHS:
        content_overrides=json.loads(content_path.read_text(encoding="utf-8"))
        override_questions=content_overrides.get("questions",{})
        if content_overrides.get("schemaVersion")!=1 or not override_questions:
            raise SystemExit(f"Marrow content-hygiene override identity/count mismatch: {content_path.name}")
        ids=set(override_questions)
        ranges=CONTENT_OVERRIDE_RANGES.get(content_path.name)
        if ranges:
            expected_ids={
                f"marrow__PHYS_CH{chapter:02d}_Q{number:03d}"
                for chapter,start,end in ranges for number in range(start,end+1)
            }
            if ids!=expected_ids or not content_overrides.get("sourcePdfSha256"):
                raise SystemExit(f"Marrow Physiology override range/source identity mismatch: {content_path.name}")
        if not ids.issubset(expanded_source_by_id) or ids & applied_content_ids:
            raise SystemExit(f"Marrow content-hygiene override IDs unknown or duplicated: {content_path.name}")
        source_payload=[{
            "id":qid,
            "question":expanded_source_by_id[qid].get("question"),
            "options":[option.get("text") for option in expanded_source_by_id[qid].get("options",[])],
        } for qid in sorted(ids)]
        source_fingerprint=hashlib.sha256(json.dumps(
            source_payload,ensure_ascii=False,separators=(",",":"),sort_keys=True
        ).encode("utf-8")).hexdigest()
        if source_fingerprint!=content_overrides.get("sourceFingerprint"):
            raise SystemExit(f"Marrow content-hygiene source fingerprint mismatch: {content_path.name} {source_fingerprint}")
        if content_overrides.get("sourcePdfSha256"):
            source_pdf=DATA/"source_pdfs"/"physiologyed8.pdf"
            if hashlib.sha256(source_pdf.read_bytes()).hexdigest()!=content_overrides["sourcePdfSha256"]:
                raise SystemExit(f"Marrow source PDF changed: {content_path.name}")
        for qid,override in override_questions.items():
            question=expanded_source_by_id[qid]
            clean_question=override.get("question")
            clean_options=override.get("options")
            if not isinstance(clean_question,str) or not clean_question.strip():
                raise SystemExit(f"Marrow content override question is empty: {qid}")
            if not isinstance(clean_options,list) or len(clean_options)!=4 or any(
                not isinstance(value,str) or not value.strip() for value in clean_options
            ):
                raise SystemExit(f"Marrow content override options are invalid: {qid}")
            question["question"]=clean_question.strip()
            for option,value in zip(question.get("options",[]),clean_options):
                option["text"]=value.strip()
            correct_option=int(question.get("correctOption",0))
            if correct_option not in (1,2,3,4):
                raise SystemExit(f"Marrow content override answer index is invalid: {qid}")
            question["correctAnswerText"]=clean_options[correct_option-1].strip()
        applied_content_ids.update(ids)
    return applied_content_ids


def expanded_marrow_records() -> list[dict]:
    """The three canonical expanded banks with reviewed display overrides applied."""
    records = [
        load_expanded_bank("anatomy_ch001_063", "Anatomy")[0],
        load_expanded_bank("biochemistry_ch001_028", "Biochemistry")[0],
        load_expanded_bank("physiology_ch001_043", "Physiology")[0],
    ]
    applied = apply_content_overrides(records)
    print(f"MARROW_CONTENT_HYGIENE_OVERRIDES_OK questions={len(applied)} manifests={len(CONTENT_OVERRIDE_PATHS)}")
    ids = [q["id"] for record in records for q in record["questions"]]
    if len(ids) != 2711 or len(ids) != len(set(ids)):
        raise SystemExit(f"Expanded Marrow global ID mismatch: {len(ids)}")
    return records


# Microbiology is a Marrow-only subject (no PrepLadder bank). It is built from the
# extracted Marrow QBank JSONL by tools/build_microbiology_marrow_bank.py and is
# kept outside the canonical ED8 corpus above, so the 2,711-question ED8 gates
# (explanation inventory, image registry, content overrides) are unchanged.
MICROBIOLOGY_PREFIX = "microbiology_marrow_qbank"


def microbiology_record() -> dict:
    """The hash-verified Microbiology Marrow bank."""
    record, manifest = load_expanded_bank(MICROBIOLOGY_PREFIX, "Microbiology")
    counts = {str(t["id"]): int(t.get("questionCount", 0)) for t in record["topics"]}
    actual = {}
    for q in record["questions"]:
        actual[str(q["chapterId"])] = actual.get(str(q["chapterId"]), 0) + 1
        if not str(q["id"]).startswith("marrow__MICRO_CH") or q.get("subject") != "Microbiology":
            fail(f"Microbiology question identity mismatch: {q.get('id')}")
        structured = q.get("structuredExplanation") or {}
        table_ids = {t.get("table_id") for t in structured.get("tables", [])}
        for block in structured.get("blocks", []):
            if block.get("type") == "table" and block.get("table_id") not in table_ids:
                fail(f"Microbiology table block without table: {q['id']} {block.get('table_id')}")
    if counts != actual or counts != manifest.get("topicCounts"):
        fail(f"Microbiology topic counts mismatch: topics={counts} questions={actual}")
    print(f"MICROBIOLOGY_MARROW_BANK_OK questions={len(record['questions'])} topics={len(record['topics'])}")
    return record


def app_marrow_records() -> list[dict]:
    """Every Marrow bank the app embeds: the canonical ED8 three, then Microbiology."""
    return expanded_marrow_records() + [microbiology_record()]


def validate_biochemistry_batches(expanded_biochemistry: dict) -> dict:
    """Biochemistry batches must all be approved; a candidate batch fails the build."""
    biochem_paths=sorted(DATA.glob("explanation_biochem_*_v1.json"))
    if not biochem_paths:
        raise SystemExit("Marrow Biochemistry explanation augmentation files missing")
    biochem_source_q={str(q.get("id","")):q for q in expanded_biochemistry.get("questions",[])}
    biochem_gold_q={}
    biochem_file_counts={}
    for path in biochem_paths:
        record=json.loads(path.read_text(encoding="utf-8"))
        scope=record.get("scope",{})
        questions=record.get("questions",{})
        if (
            scope.get("subject")!="Biochemistry"
            or scope.get("bank")!="Marrow"
            or scope.get("status") not in {"approved-reference","approved-rollout"}
            or not questions
        ):
            raise SystemExit(f"Marrow Biochemistry explanation batch identity/status mismatch: {path.name}")
        declared=int(scope.get("questions",0))
        if declared!=len(questions):
            raise SystemExit(f"Marrow Biochemistry explanation batch count mismatch: {path.name}")
        overlap=set(biochem_gold_q)&set(questions)
        if overlap:
            raise SystemExit(f"Marrow Biochemistry explanation batch ID collision: {path.name} {sorted(overlap)[:3]}")
        biochem_gold_q.update(questions)
        biochem_file_counts[path.name]=len(questions)

    inventory=json.loads((DATA/"explanation_inventory_v1.json").read_text(encoding="utf-8"))
    sample_ids={str(row.get("id","")) for row in inventory.get("biochemistryGoldSample",[])}
    gold_sample=json.loads((DATA/"explanation_biochem_gold_sample_v1.json").read_text(encoding="utf-8"))
    if set(gold_sample.get("questions",{}))!=sample_ids or len(sample_ids)!=20:
        raise SystemExit("Marrow Biochemistry gold-sample IDs do not match inventory")

    if not set(biochem_gold_q).issubset(biochem_source_q):
        raise SystemExit("Marrow Biochemistry explanation rollout has unknown source IDs")
    for qid,cfg in biochem_gold_q.items():
        if not str(cfg.get("takeaway","")).strip() or not str(cfg.get("displayText","")).strip():
            raise SystemExit(f"Marrow Biochemistry explanation missing takeaway/displayText: {qid}")
        emphasis=cfg.get("emphasis",[])
        if not (1<=len(emphasis)<=4):
            raise SystemExit(f"Marrow Biochemistry emphasis count invalid: {qid}")
        source_q=biochem_source_q[qid]
        correct=int(source_q.get("correctOption",0))
        wrong_letters={
            str(option.get("letter") or chr(64+index)).lower()
            for index,option in enumerate(source_q.get("options",[]),1)
            if index!=correct
        }
        if len(cfg.get("rationales",{}))!=3 or set(cfg.get("rationales",{}))!=wrong_letters:
            raise SystemExit(f"Marrow Biochemistry distractor rationales mismatch: {qid}")
    return biochem_gold_q
