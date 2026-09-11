#!/usr/bin/env python3
"""Run the verified Marrow transformer, then install bounded Anatomy explanation rollouts."""
from __future__ import annotations

import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data" / "marrow"
HTML = ROOT / "app/src/main/assets/index.html"

runpy.run_path(str(HERE / "_apply_marrow_bank_pilot_base.py"), run_name="__main__")

from inventory_marrow_explanations import load_sharded  # noqa: E402

bank, _ = load_sharded("anatomy_phase_a")
source_questions = {str(q.get("id", "")): q for q in bank["questions"]}
reference = json.loads((DATA / "explanation_gold_pilot.json").read_text(encoding="utf-8"))["questions"]
rollout = {}
file_counts = {}

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
        raise SystemExit(f"Marrow Anatomy explanation batch identity/status mismatch: {path.name}")
    if int(scope.get("questions", 0)) != len(questions):
        raise SystemExit(f"Marrow Anatomy explanation batch count mismatch: {path.name}")
    overlap = (set(reference) | set(rollout)) & set(questions)
    if overlap:
        raise SystemExit(f"Marrow Anatomy explanation batch ID collision: {path.name} {sorted(overlap)[:3]}")
    if not set(questions).issubset(source_questions):
        raise SystemExit(f"Marrow Anatomy explanation batch has unknown source IDs: {path.name}")
    chapter = str(scope.get("chapterId"))
    order = []
    for qid, cfg in questions.items():
        source = source_questions[qid]
        if str(source.get("chapterId")) != chapter:
            raise SystemExit(f"Marrow Anatomy explanation chapter mismatch: {qid}")
        order.append(int(source.get("questionNumber") or 0))
        if not str(cfg.get("takeaway", "")).strip() or not str(cfg.get("displayText", "")).strip():
            raise SystemExit(f"Marrow Anatomy explanation missing takeaway/displayText: {qid}")
        emphasis = cfg.get("emphasis", [])
        if not (1 <= len(emphasis) <= 4) or any(str(p) not in str(cfg["displayText"]) for p in emphasis):
            raise SystemExit(f"Marrow Anatomy emphasis invalid: {qid}")
        correct = int(source.get("correctOption", 0))
        wrong_letters = {
            str(option.get("letter") or chr(64 + index)).lower()
            for index, option in enumerate(source.get("options", []), 1)
            if index != correct
        }
        rationales = cfg.get("rationales", {})
        if len(rationales) != 3 or set(rationales) != wrong_letters or any(not str(v).strip() for v in rationales.values()):
            raise SystemExit(f"Marrow Anatomy distractor rationales mismatch: {qid}")
        reconstruction = cfg.get("reconstruction")
        if reconstruction is not None:
            if reconstruction.get("status") not in {"resolved_reconstruction", "needs_manual_review"}:
                raise SystemExit(f"Marrow Anatomy reconstruction status invalid: {qid}")
            if any(not str(reconstruction.get(k, "")).strip() for k in ("sourceProblem", "reconstructedContent", "reviewNote")):
                raise SystemExit(f"Marrow Anatomy reconstruction metadata incomplete: {qid}")
            evidence = reconstruction.get("evidenceBasis")
            if not isinstance(evidence, list) or not evidence or any(not str(x).strip() for x in evidence):
                raise SystemExit(f"Marrow Anatomy reconstruction evidence invalid: {qid}")
    if sorted(order) != list(range(min(order), max(order) + 1)):
        raise SystemExit(f"Marrow Anatomy rollout must be contiguous source order: {path.name}")
    if "questionStart" in scope and int(scope["questionStart"]) != min(order):
        raise SystemExit(f"Marrow Anatomy rollout questionStart mismatch: {path.name}")
    if "questionEnd" in scope and int(scope["questionEnd"]) != max(order):
        raise SystemExit(f"Marrow Anatomy rollout questionEnd mismatch: {path.name}")
    rollout.update(questions)
    file_counts[path.name] = len(questions)

if rollout:
    source = HTML.read_text(encoding="utf-8")
    marker = "  const NK_MARROW_EXPLANATION_GOLD_V1="
    if source.count(marker) != 1:
        raise SystemExit(f"Marrow explanation config marker count: {source.count(marker)}")
    start = source.index(marker) + len(marker)
    end_marker = ";\n\n  function nkGoldText"
    end = source.index(end_marker, start)
    existing = json.loads(source[start:end])
    collision = set(existing) & set(rollout)
    if collision:
        raise SystemExit(f"Marrow Anatomy generated-config collision: {sorted(collision)[:3]}")
    merged = {**existing, **rollout}
    encoded = json.dumps(merged, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    source = source[:start] + encoded + source[end:]
    HTML.write_text(source, encoding="utf-8")
    print(
        "MARROW_ANATOMY_EXPLANATION_ROLLOUT_OK "
        f"files={len(file_counts)} questions={len(rollout)} rendered_total={len(merged)} "
        f"batches={file_counts} raw_source=preserved"
    )
else:
    print("MARROW_ANATOMY_EXPLANATION_ROLLOUT_OK files=0 questions=0")
