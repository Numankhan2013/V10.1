#!/usr/bin/env python3
"""Wire the canonical two-bank Subject flow and every approved Marrow explanation into runtime.

This runs after the Marrow bank transform. It does not rewrite imported source text.
It only repairs two integration contracts:
1. Home/Study subject cards aggregate PrepLadder + Marrow and open the bank chooser.
2. Every explanation counted as enhanced in the canonical inventory is present in
   the learner-facing Marrow explanation map.
"""
from __future__ import annotations

import base64
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/marrow"
HTML = ROOT / "app/src/main/assets/index.html"
MARKER = "NK_CANONICAL_BANK_EXPLANATION_WIRING_V1"


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
    if "raw_bytes" in manifest and len(raw) != int(manifest["raw_bytes"]):
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
            scope = record.get("scope", {})
            questions = record.get("questions", {})
            if (
                scope.get("subject") != expected_subject
                or scope.get("bank") != "Marrow"
                or scope.get("status") not in {"approved-reference", "approved-rollout"}
                or not questions
            ):
                fail(f"{path.name}: explanation batch identity/status mismatch")
            if int(scope.get("questions", 0)) != len(questions):
                fail(f"{path.name}: declared explanation count mismatch")
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


def patch_home_bank_flow(html: str) -> str:
    start_marker = "  function nkSubjectStatsV3(subject){"
    end_marker = "  function nkOpenSubjectChapter(subject,bank,topicId){"
    if html.count(start_marker) != 1 or html.count(end_marker) != 1:
        fail("Home subject-bank integration anchors are missing or duplicated")
    start = html.index(start_marker)
    end = html.index(end_marker, start)
    replacement = r'''  function nkSubjectStatsV3(subject){
    const records=typeof nkBankRecords==='function'?nkBankRecords(subject):[];
    const fallback=(SUBJECTS||[]).find(r=>r.subject===subject)||null;
    const scoped=records.length?records:(fallback?[fallback]:[]);
    const byId=new Map();
    scoped.forEach(record=>(record.questions||[]).forEach(q=>{const id=String(q?.id||'');if(id&&!byId.has(id))byId.set(id,q);}));
    const questions=[...byId.values()];
    const topics=scoped.reduce((n,record)=>n+(Array.isArray(record.topics)?record.topics.length:0),0);
    const attempted=questions.filter(q=>qAttempts(q.id).length>0).length;
    const pct=questions.length?Math.round(attempted/questions.length*100):0;
    return {record:nkPreferredRecord(subject),records:scoped,questions:questions.length,topics,attempted,pct};
  }
  function nkOpenSubjectLibrary(subject){
    const records=typeof nkBankRecords==='function'?nkBankRecords(subject):[];
    const fallback=(SUBJECTS||[]).find(r=>r.subject===subject)||null;
    if(!records.length&&!fallback){showToast('This subject is not available.','bad');return;}
    if(typeof openSubjectTopics==='function'){openSubjectTopics(subject);return;}
    activeSubject=subject;localStorage.setItem('qbank_active_subject_v1',subject);navigate('banks',subject);
  }
'''
    html = html[:start] + replacement + html[end:]
    html = html.replace(
        "Choose a subject to open its complete topic journey.",
        "Choose a subject, then choose PrepLadder or Marrow.",
    )
    html = html.replace(
        "Subjects open the full Topics page. No popup topic picker is used.",
        "Each subject opens its question-bank chooser before Topics.",
    )
    return html


def patch_explanation_map(html: str, merged: dict[str, dict]) -> str:
    const_marker = "  const NK_MARROW_EXPLANATION_GOLD_V1="
    function_marker = "\n\n  function nkGoldText"
    if html.count(const_marker) != 1:
        fail(f"runtime explanation const count: {html.count(const_marker)}")
    start = html.index(const_marker)
    end = html.index(function_marker, start)
    cfg = json.dumps(merged, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    replacement = f"  /* {MARKER} */\n  const NK_MARROW_EXPLANATION_GOLD_V1={cfg};"
    return html[:start] + replacement + html[end:]


def install() -> None:
    if not HTML.exists():
        fail("generated app index.html is missing")
    source_by_id = canonical_source_questions()
    merged = merged_explanations(source_by_id)
    html = HTML.read_text(encoding="utf-8")
    html = patch_home_bank_flow(html)
    html = patch_explanation_map(html, merged)
    if html.count(MARKER) != 1:
        fail("canonical wiring marker count mismatch")
    if "if(typeof openSubjectTopics==='function'){openSubjectTopics(subject);return;}" not in html:
        fail("subject cards are not routed through the bank chooser")
    HTML.write_text(html, encoding="utf-8")
    print("CANONICAL_SUBJECT_BANK_FLOW_OK aggregate=PrepLadder+Marrow route=bank-chooser")
    print(f"CANONICAL_RUNTIME_EXPLANATIONS_OK enhanced={len(merged)} denominator=2711")


if __name__ == "__main__":
    install()
