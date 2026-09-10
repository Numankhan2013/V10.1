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
    "Anatomy": "anatomy_ch001_048_plus_060_063",
    "Biochemistry": "biochemistry_phase_a",
    "Physiology": "physiology_ch001_043",
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


def enhanced_ids() -> set[str]:
    anatomy = json.loads((DATA / "explanation_gold_pilot.json").read_text(encoding="utf-8"))["questions"]
    physiology, _ = load_sharded("explanation_physio_pilot")
    ids = set(anatomy) | set(physiology["questions"])
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
    assert inventory["summary"]["questions"] == 2455
    assert inventory["summary"]["enhancementStatus"] == {"enhanced-reference": enhanced, "pending": 2455 - enhanced}
    assert len(inventory["biochemistryGoldSample"]) == 20
    assert len({row["id"] for row in inventory["questions"]}) == 2455
    if args.write:
        target = DATA / "explanation_inventory_v1.json"
        target.write_text(json.dumps(inventory_manifest(inventory), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = inventory["summary"]
    print(f"MARROW_EXPLANATION_INVENTORY_OK questions={summary['questions']} enhanced={enhanced} pending={2455-enhanced} biochem_sample=20 flags={summary['flags']}")


if __name__ == "__main__":
    main()
