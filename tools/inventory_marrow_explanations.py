#!/usr/bin/env python3
"""Build a text-free, deterministic inventory for Marrow explanation review."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import zlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
BANKS = {
    "Anatomy": "anatomy_phase_a",
    "Biochemistry": "biochemistry_phase_a",
    "Physiology": "physiology_ch001_033",
}
BIOCHEM_SAMPLE_CHAPTERS = (1, 2, 4, 5, 7, 8, 10, 11, 12, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26)
OCR_SIGNALS = (
    re.compile(r"\ufffd"),
    re.compile(r"\b(?:wok\s+no|internalef)\b", re.I),
    re.compile(r"[a-z][A-Z][a-z]"),
    re.compile(r"(?:\.{3,}|,{2,}|;;+)"),
    re.compile(r"\b(?:option|ans(?:wer)?)\s*[a-d1-4]\s*[:.)-]", re.I),
)
FIGURE_SIGNAL = re.compile(r"\b(?:image|figure|diagram|graph|flowchart)\b", re.I)


def load_sharded(prefix: str) -> tuple[dict, str]:
    encoded = "".join(
        part.read_text(encoding="utf-8").strip()
        for part in sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    )
    raw = zlib.decompress(base64.b64decode(encoded))
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def _validate_rollout_cfg(qid: str, cfg: dict, source: dict, label: str) -> None:
    if not str(cfg.get("takeaway", "")).strip() or not str(cfg.get("displayText", "")).strip():
        raise AssertionError(f"{label} missing takeaway/displayText: {qid}")
    emphasis = cfg.get("emphasis", [])
    if not (1 <= len(emphasis) <= 4) or any(str(p) not in str(cfg["displayText"]) for p in emphasis):
        raise AssertionError(f"{label} emphasis invalid: {qid}")
    if "sourceText" in cfg:
        raise AssertionError(f"{label} must not duplicate immutable source text: {qid}")
    correct = int(source.get("correctOption", 0))
    wrong_letters = {
        str(option.get("letter") or chr(64 + index)).lower()
        for index, option in enumerate(source.get("options", []), 1)
        if index != correct
    }
    rationales = cfg.get("rationales", {})
    if len(rationales) != 3 or set(rationales) != wrong_letters or any(not str(v).strip() for v in rationales.values()):
        raise AssertionError(f"{label} distractor rationales mismatch: {qid}")
    reconstruction = cfg.get("reconstruction")
    if reconstruction is not None:
        if reconstruction.get("status") not in {"resolved_reconstruction", "needs_manual_review"}:
            raise AssertionError(f"{label} reconstruction status invalid: {qid}")
        for field in ("sourceProblem", "reconstructedContent", "reviewNote"):
            if not str(reconstruction.get(field, "")).strip():
                raise AssertionError(f"{label} reconstruction {field} missing: {qid}")
        evidence = reconstruction.get("evidenceBasis")
        if not isinstance(evidence, list) or not evidence or any(not str(item).strip() for item in evidence):
            raise AssertionError(f"{label} reconstruction evidence invalid: {qid}")


def enhanced_ids() -> set[str]:
    anatomy_reference = json.loads((DATA / "explanation_gold_pilot.json").read_text(encoding="utf-8"))["questions"]
    ids = set(anatomy_reference)

    anatomy_bank, _ = load_sharded("anatomy_phase_a")
    anatomy_source = {str(q.get("id", "")): q for q in anatomy_bank["questions"]}
    anatomy_rollout_ids: set[str] = set()
    for path in sorted(DATA.glob("explanation_anatomy_ch*_v1.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        scope = record.get("scope", {})
        questions = record.get("questions", {})
        if (
            scope.get("subject") != "Anatomy"
            or scope.get("bank") != "Marrow"
            or scope.get("status") != "approved-rollout"
            or not questions
        ):
            raise AssertionError(f"Anatomy explanation batch identity/status mismatch: {path.name}")
        if int(scope.get("questions", 0)) != len(questions):
            raise AssertionError(f"Anatomy explanation batch count mismatch: {path.name}")
        overlap = (ids | anatomy_rollout_ids) & set(questions)
        if overlap:
            raise AssertionError(f"duplicate enhanced IDs in {path.name}: {sorted(overlap)[:3]}")
        if not set(questions).issubset(anatomy_source):
            raise AssertionError(f"Anatomy explanation batch has unknown source IDs: {path.name}")
        chapter = str(scope.get("chapterId"))
        source_order = []
        for qid, cfg in questions.items():
            source = anatomy_source[qid]
            if str(source.get("chapterId")) != chapter:
                raise AssertionError(f"Anatomy explanation chapter mismatch: {qid}")
            _validate_rollout_cfg(qid, cfg, source, "Anatomy")
            source_order.append(int(source.get("questionNumber") or 0))
        expected = list(range(min(source_order), max(source_order) + 1))
        if sorted(source_order) != expected:
            raise AssertionError(f"Anatomy explanation batch is not contiguous source order: {path.name}")
        if "questionStart" in scope and int(scope["questionStart"]) != min(source_order):
            raise AssertionError(f"Anatomy explanation questionStart mismatch: {path.name}")
        if "questionEnd" in scope and int(scope["questionEnd"]) != max(source_order):
            raise AssertionError(f"Anatomy explanation questionEnd mismatch: {path.name}")
        anatomy_rollout_ids.update(questions)
    ids.update(anatomy_rollout_ids)

    physiology, _ = load_sharded("explanation_physio_pilot")
    overlap = ids & set(physiology["questions"])
    if overlap:
        raise AssertionError(f"duplicate enhanced IDs in Physiology pilot: {sorted(overlap)[:3]}")
    ids.update(physiology["questions"])
    for path in sorted(DATA.glob("explanation_physio_ch*_v1.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        scope = record.get("scope", {})
        if (
            scope.get("subject") != "Physiology"
            or scope.get("bank") != "Marrow"
            or scope.get("status") != "approved-rollout"
        ):
            continue
        questions = record.get("questions", {})
        overlap = ids & set(questions)
        if overlap:
            raise AssertionError(f"duplicate enhanced IDs in {path.name}: {sorted(overlap)[:3]}")
        ids.update(questions)

    for path in sorted(DATA.glob("explanation_biochem_*_v1.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        scope = record.get("scope", {})
        if scope.get("status") not in {"approved-reference", "approved-rollout"}:
            continue
        questions = record.get("questions", {})
        overlap = ids & set(questions)
        if overlap:
            raise AssertionError(f"duplicate enhanced IDs in {path.name}: {sorted(overlap)[:3]}")
        ids.update(questions)
    return ids


def classify(question: dict, enhanced: set[str]) -> dict:
    structured = question.get("structuredExplanation") or {}
    text = str(structured.get("text") or question.get("explanation") or "")
    tables = structured.get("tables") or []
    figures = structured.get("figures") or []
    flags = []
    if tables:
        flags.append("source-table")
    if figures or FIGURE_SIGNAL.search(text):
        flags.append("image-dependent-review")
    if any(pattern.search(text) for pattern in OCR_SIGNALS):
        flags.append("ocr-cleanup-candidate")
    if len(text.strip()) < 20:
        flags.append("source-omission-review")
    review_status = str(question.get("reviewStatus") or "")
    if review_status.startswith("needs_manual_review"):
        flags.append("source-review-status")
    elif review_status not in {"", "pass", "resolved_reconstruction"}:
        flags.append("source-provenance-note")
    return {
        "id": str(question["id"]),
        "sourceQuestionId": str(question.get("sourceQuestionId") or ""),
        "subject": str(question["subject"]),
        "chapterId": str(question["chapterId"]),
        "questionNumber": int(question.get("questionNumber") or 0),
        "enhancementStatus": "enhanced-reference" if question["id"] in enhanced else "pending",
        "reviewStatus": review_status,
        "flags": sorted(set(flags)),
        "sourceTextChars": len(text),
    }


def choose_biochem_sample(rows: list[dict]) -> list[dict]:
    selected = []
    for chapter in BIOCHEM_SAMPLE_CHAPTERS:
        choices = [row for row in rows if int(row["chapterId"]) == chapter]
        choices.sort(key=lambda row: (-len(row["flags"]), -row["sourceTextChars"], row["questionNumber"], row["id"]))
        selected.append(choices[0])
    return [
        {
            "id": row["id"],
            "chapterId": row["chapterId"],
            "flags": row["flags"],
            "status": "approved-reference" if row["enhancementStatus"] == "enhanced-reference" else "pending-human-review",
        }
        for row in selected
    ]


def build_inventory() -> dict:
    enhanced = enhanced_ids()
    records = []
    source_hashes = {}
    for subject, prefix in BANKS.items():
        bank, source_hash = load_sharded(prefix)
        source_hashes[subject] = source_hash
        records.extend(classify(question, enhanced) for question in bank["questions"])
    records.sort(key=lambda row: (row["subject"], int(row["chapterId"]), row["questionNumber"], row["id"]))
    flags = Counter(flag for row in records for flag in row["flags"])
    subjects = Counter(row["subject"] for row in records)
    statuses = Counter(row["enhancementStatus"] for row in records)
    biochem = [row for row in records if row["subject"] == "Biochemistry"]
    return {
        "schemaVersion": 1,
        "purpose": "Triage only; classifications never alter source or learner-facing text.",
        "sourceRawSha256": source_hashes,
        "summary": {
            "questions": len(records),
            "subjects": dict(sorted(subjects.items())),
            "enhancementStatus": dict(sorted(statuses.items())),
            "flags": dict(sorted(flags.items())),
        },
        "biochemistryGoldSample": choose_biochem_sample(biochem),
        "questions": records,
    }


def inventory_manifest(inventory: dict) -> dict:
    records = inventory["questions"]
    encoded = json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        key: value for key, value in inventory.items() if key != "questions"
    } | {
        "questionRecords": len(records),
        "questionRecordsSha256": hashlib.sha256(encoded).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    inventory = build_inventory()
    enhanced = len(enhanced_ids())
    assert inventory["summary"]["questions"] == 2115
    assert inventory["summary"]["enhancementStatus"] == {"enhanced-reference": enhanced, "pending": 2115 - enhanced}
    assert len(inventory["biochemistryGoldSample"]) == 20
    assert len({row["id"] for row in inventory["questions"]}) == 2115
    if args.write:
        target = DATA / "explanation_inventory_v1.json"
        target.write_text(json.dumps(inventory_manifest(inventory), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = inventory["summary"]
    print(f"MARROW_EXPLANATION_INVENTORY_OK questions={summary['questions']} enhanced={enhanced} pending={2115-enhanced} biochem_sample=20 flags={summary['flags']}")


if __name__ == "__main__":
    main()
