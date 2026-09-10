#!/usr/bin/env python3
"""Repair and lock the Marrow A-D runtime option contract.

Root cause addressed:
- automation JSONL uses lowercase a/b/c/d labels;
- the NK session renderer historically converted option letters with
  charCodeAt(0)-64, which requires uppercase A-D;
- newly adapted questions therefore could mark a chosen answer red while no
  correct option could ever receive the green `correct` state.

This migration changes only the runtime adapter representation of option labels.
Canonical JSONL source content is not rewritten. It also installs fail-closed
static/runtime/browser guardrails so the same regression cannot pass CI again.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
EXPECTED_LETTERS = ["A", "B", "C", "D"]


def patch_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text and old not in text:
        print(f"OPTION_CONTRACT_PATCH_ALREADY_OK {label}")
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one repair anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"OPTION_CONTRACT_PATCH_OK {label}")


def load_bundle(prefix: str) -> tuple[dict, dict]:
    manifest_path = DATA / f"{prefix}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parts = sorted(DATA.glob(f"{prefix}.zlib.b64.part*"))
    if len(parts) != int(manifest["parts"]):
        raise SystemExit(f"{prefix}: shard count mismatch")
    encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    if len(encoded) != int(manifest["base64_chars"]):
        raise SystemExit(f"{prefix}: base64 length mismatch")
    compressed = base64.b64decode(encoded, validate=True)
    if len(compressed) != int(manifest["compressed_bytes"]):
        raise SystemExit(f"{prefix}: compressed length mismatch")
    if hashlib.sha256(compressed).hexdigest() != manifest["compressed_sha256"]:
        raise SystemExit(f"{prefix}: compressed SHA mismatch")
    raw = zlib.decompress(compressed)
    if len(raw) != int(manifest["raw_bytes"]):
        raise SystemExit(f"{prefix}: raw length mismatch")
    if hashlib.sha256(raw).hexdigest() != manifest["raw_sha256"]:
        raise SystemExit(f"{prefix}: raw SHA mismatch")
    return json.loads(raw.decode("utf-8")), manifest


def write_bundle(prefix: str, record: dict, manifest: dict) -> None:
    raw = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, 9)
    encoded = base64.b64encode(compressed).decode("ascii")
    part_size = int(manifest.get("part_size", 60000))
    chunks = [encoded[i:i + part_size] for i in range(0, len(encoded), part_size)]
    for stale in DATA.glob(f"{prefix}.zlib.b64.part*"):
        stale.unlink()
    for index, chunk in enumerate(chunks):
        (DATA / f"{prefix}.zlib.b64.part{index:02d}").write_text(chunk + "\n", encoding="utf-8")
    manifest = dict(manifest)
    manifest.update(
        {
            "parts": len(chunks),
            "part_size": part_size,
            "base64_chars": len(encoded),
            "raw_bytes": len(raw),
            "compressed_bytes": len(compressed),
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
            "runtime_option_letter_contract": "A-D uppercase",
        }
    )
    (DATA / f"{prefix}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def normalize_bundle(prefix: str, expected_changed_questions: int) -> None:
    record, manifest = load_bundle(prefix)
    changed_questions = 0
    changed_letters = 0
    for question in record.get("questions", []):
        options = question.get("options", [])
        if len(options) != 4:
            raise SystemExit(f"{prefix}: {question.get('id')} does not have four options")
        normalized = [str(option.get("letter", "")).strip().upper() for option in options]
        if normalized != EXPECTED_LETTERS:
            raise SystemExit(
                f"{prefix}: {question.get('id')} option labels are not an A-D permutation in order: {normalized!r}"
            )
        changed = False
        for option, letter in zip(options, EXPECTED_LETTERS):
            if option.get("letter") != letter:
                option["letter"] = letter
                changed = True
                changed_letters += 1
        if changed:
            changed_questions += 1
        correct = question.get("correctOption")
        if correct not in (1, 2, 3, 4):
            raise SystemExit(f"{prefix}: {question.get('id')} invalid correctOption={correct!r}")
    if changed_questions not in (0, expected_changed_questions):
        raise SystemExit(
            f"{prefix}: expected {expected_changed_questions} affected questions (or 0 if rerun), found {changed_questions}"
        )
    if changed_questions:
        write_bundle(prefix, record, manifest)
    # Re-read what will actually be consumed and fail closed on the final bytes.
    final_record, _ = load_bundle(prefix)
    for question in final_record.get("questions", []):
        letters = [str(option.get("letter", "")).strip() for option in question.get("options", [])]
        if letters != EXPECTED_LETTERS:
            raise SystemExit(f"{prefix}: final option contract failed for {question.get('id')}: {letters!r}")
    print(
        f"MARROW_OPTION_BUNDLE_OK prefix={prefix} questions={len(final_record.get('questions', []))} "
        f"normalized_questions={changed_questions} normalized_letters={changed_letters} contract=A-D"
    )


def patch_importers() -> None:
    for path in (
        ROOT / "tools" / "integrate_physio_automation_ch034_043.py",
        ROOT / "tools" / "integrate_anatomy_automation_ch060_063.py",
    ):
        text = path.read_text(encoding="utf-8")
        old = '"letter": str(opt.get("label", "")).lower()'
        new = '"letter": str(opt.get("label", "")).strip().upper()'
        if new in text and old not in text:
            continue
        if text.count(old) != 1:
            raise SystemExit(f"{path}: importer option-normalization anchor count={text.count(old)}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("MARROW_OPTION_IMPORTERS_OK uppercase=A-D")


def patch_runtime_validator() -> None:
    path = ROOT / "tools" / "apply_marrow_bank_pilot.py"
    old = '''    if any(len(q.get("options",[]))!=4 or q.get("correctOption") not in (1,2,3,4) or not str(q.get("question","")).strip() for q in questions):\n        raise SystemExit(f"{expected_subject} expanded question shape invalid")\n    return record,manifest\n'''
    new = '''    if any(len(q.get("options",[]))!=4 or q.get("correctOption") not in (1,2,3,4) or not str(q.get("question","")).strip() for q in questions):\n        raise SystemExit(f"{expected_subject} expanded question shape invalid")\n    expected_letters=["A","B","C","D"]\n    if any([str(opt.get("letter","")).strip() for opt in q.get("options",[])]!=expected_letters for q in questions):\n        raise SystemExit(f"{expected_subject} expanded option-letter contract invalid; expected uppercase A-D")\n    return record,manifest\n'''
    patch_once(path, old, new, "expanded-bank-validator")


def patch_static_test() -> None:
    path = ROOT / "tools" / "test_marrow_bank_pilot.py"
    old = '''    assert all(len(q['options'])==4 and q['correctOption'] in (1,2,3,4) and q['question'] for q in all_expanded)\n    full_repaired={q['sourceQuestionId']:q for q in fa_q if q.get('reviewStatus')=='resolved_reconstruction'}\n'''
    new = '''    assert all(len(q['options'])==4 and q['correctOption'] in (1,2,3,4) and q['question'] for q in all_expanded)\n    assert all([str(o.get('letter','')).strip() for o in q['options']]==['A','B','C','D'] for q in all_expanded), 'Marrow runtime option labels must be uppercase A-D'\n    full_repaired={q['sourceQuestionId']:q for q in fa_q if q.get('reviewStatus')=='resolved_reconstruction'}\n'''
    patch_once(path, old, new, "static-A-D-invariant")


def patch_session_renderer() -> None:
    path = ROOT / "tools" / "apply_session_experience_v2.py"
    old = "const n=o.letter.charCodeAt(0)-64,isChosen=Number(selected)===n,isCorrect=Number(q.correctOption)===n;"
    new = "const n=String(o?.letter||'').trim().toUpperCase().charCodeAt(0)-64,isChosen=Number(selected)===n,isCorrect=Number(q.correctOption)===n;"
    patch_once(path, old, new, "session-option-normalization")


def patch_browser_regressions() -> None:
    path = ROOT / "tools" / "verify_marrow_bank_browser.py"
    text = path.read_text(encoding="utf-8")

    # Existing Marrow question: verify the classic wrong/red + correct/green behavior too.
    old_biochem = """            page.locator('.option-list button').first.click();page.wait_for_timeout(120)\n            bsupport=page.locator('.nk-study-support').inner_text().lower()\n"""
    new_biochem = """            page.locator('.option-list button').first.click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('Existing Marrow wrong-answer visual state must show one red wrong and one green correct option')\n            if page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")!='rgb(16, 154, 99)':\n                raise SystemExit('Existing Marrow correct option is not visually green after a wrong answer')\n            if page.locator('.option-list .option.wrong .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")!='rgb(201, 75, 87)':\n                raise SystemExit('Existing Marrow selected wrong option is not visually red')\n            bsupport=page.locator('.nk-study-support').inner_text().lower()\n"""
    if new_biochem not in text:
        if text.count(old_biochem) != 1:
            raise SystemExit(f"browser existing-answer anchor count={text.count(old_biochem)}")
        text = text.replace(old_biochem, new_biochem, 1)

    old_phys = """            if not page.locator('.question-text').inner_text().strip(): raise SystemExit('Exercise Physiology source question did not render as a learner question')\n            page.evaluate(\"window.QB.nav('banks','Physiology')\");page.wait_for_timeout(80)\n"""
    new_phys = """            if not page.locator('.question-text').inner_text().strip(): raise SystemExit('Exercise Physiology source question did not render as a learner question')\n            phys_correct=int(page.evaluate(\"(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()\"))-1\n            phys_wrong=(phys_correct+1)%4\n            page.locator('.option-list button').nth(phys_wrong).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('New Physiology wrong answer must render exactly one red wrong and one green correct option')\n            phys_green=page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            phys_red=page.locator('.option-list .option.wrong .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            if phys_green!='rgb(16, 154, 99)' or phys_red!='rgb(201, 75, 87)':\n                raise SystemExit(f'New Physiology answer colors regressed: correct={phys_green} wrong={phys_red}')\n            # Re-enter through the exact Wrong Questions library flow reported by the user.\n            page.evaluate(\"window.QB.startLibrary('wrong')\");page.wait_for_timeout(100)\n            wrong_library_id=page.evaluate(\"state.activeSession.questionIds[state.activeSession.index]\")\n            if wrong_library_id!='marrow__PHYSIO_CH43_Q001':\n                raise SystemExit(f'Wrong Questions did not reopen the newly missed Physiology question: {wrong_library_id}')\n            phys_correct_again=int(page.evaluate(\"(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()\"))-1\n            page.locator('.option-list button').nth((phys_correct_again+1)%4).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('Wrong Questions flow failed to show both wrong/red and correct/green states')\n            if page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")!='rgb(16, 154, 99)':\n                raise SystemExit('Wrong Questions flow correct answer is not green')\n            page.evaluate(\"window.QB.nav('banks','Physiology')\");page.wait_for_timeout(80)\n"""
    if new_phys not in text:
        if text.count(old_phys) != 1:
            raise SystemExit(f"browser new-Physiology answer anchor count={text.count(old_phys)}")
        text = text.replace(old_phys, new_phys, 1)

    old_anatomy = """            if 'total number of bones' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('New Anatomy Ch60 source question did not render normally')\n            page.evaluate(\"window.QB.nav('banks','Anatomy')\");page.wait_for_timeout(80)\n"""
    new_anatomy = """            if 'total number of bones' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('New Anatomy Ch60 source question did not render normally')\n            anatomy_correct=int(page.evaluate(\"(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()\"))-1\n            page.locator('.option-list button').nth((anatomy_correct+1)%4).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('New Anatomy wrong answer must render exactly one red wrong and one green correct option')\n            anatomy_green=page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            anatomy_red=page.locator('.option-list .option.wrong .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            if anatomy_green!='rgb(16, 154, 99)' or anatomy_red!='rgb(201, 75, 87)':\n                raise SystemExit(f'New Anatomy answer colors regressed: correct={anatomy_green} wrong={anatomy_red}')\n            page.evaluate(\"window.QB.nav('banks','Anatomy')\");page.wait_for_timeout(80)\n"""
    if new_anatomy not in text:
        if text.count(old_anatomy) != 1:
            raise SystemExit(f"browser new-Anatomy answer anchor count={text.count(old_anatomy)}")
        text = text.replace(old_anatomy, new_anatomy, 1)

    # The previous wrapper inherited an obsolete total in its browser summary.
    text = text.replace(
        "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2376",
        "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2455",
    )
    path.write_text(text, encoding="utf-8")
    print("MARROW_OPTION_BROWSER_GUARDS_OK existing+physiology+wrong-library+anatomy")


def patch_state() -> None:
    path = ROOT / ".project-memory" / "STATE.md"
    text = path.read_text(encoding="utf-8")
    old = "- Full feature browser/APK/PWA CI for the finalized Anatomy candidate is the remaining build gate.\n"
    new = (
        "- Full feature browser/APK/PWA CI for Anatomy Ch60–63 passed in run `34451249088`; preview deployment succeeded.\n"
        "- Regression incident found after device preview: automation-adapted Physiology Ch34–43 and Anatomy Ch60–63 emitted lowercase option labels, while the session renderer expected uppercase A–D. This could show the chosen wrong option red without highlighting the actual correct option green. The repair normalizes runtime labels to uppercase, hardens the renderer case handling, adds fail-closed A–D validation, and adds browser red+green checks including the Wrong Questions flow.\n"
    )
    if new not in text:
        if text.count(old) != 1:
            raise SystemExit(f"STATE verification anchor count={text.count(old)}")
        text = text.replace(old, new, 1)
    old_next = "1. Run full feature browser/APK/PWA verification for Anatomy Ch60–63 and capture the stable + immutable preview URLs.\n2. Have the user device-check the resulting Anatomy/Physiology expansion preview.\n3. Integrate real Biochemistry Ch27/28 when supplied; integrate Anatomy Ch49–59 when their canonical artifacts are found.\n"
    new_next = "1. Treat option-state regression verification as the blocking gate; do not resume source expansion until red+green browser checks pass on the repaired bundles.\n2. Have the user device-check the repaired preview, especially a deliberately wrong new Physiology/Anatomy question and the Wrong Questions flow.\n3. Only after that, resume missing Anatomy source integration; then integrate real Biochemistry Ch27/28 when supplied.\n"
    if new_next not in text:
        if text.count(old_next) != 1:
            raise SystemExit(f"STATE next-step anchor count={text.count(old_next)}")
        text = text.replace(old_next, new_next, 1)
    path.write_text(text, encoding="utf-8")
    print("MARROW_OPTION_STATE_OK regression-blocking")


def main() -> None:
    # Repair the two generated bundles that contain automation-adapted lowercase labels.
    normalize_bundle("physiology_ch001_043", expected_changed_questions=261)
    normalize_bundle("anatomy_ch001_048_plus_060_063", expected_changed_questions=79)

    # Prevent recurrence at source adapter, bank loader, generated UI, and CI layers.
    patch_importers()
    patch_runtime_validator()
    patch_static_test()
    patch_session_renderer()
    patch_browser_regressions()
    patch_state()
    print("MARROW_OPTION_CONTRACT_REPAIR_OK source_jsonl=unchanged runtime=A-D fail_closed=yes")


if __name__ == "__main__":
    main()
