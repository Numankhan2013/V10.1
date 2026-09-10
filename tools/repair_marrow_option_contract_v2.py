#!/usr/bin/env python3
"""Second-pass driver for the Marrow option-letter regression repair.

The first migration correctly identified 261 Physiology + 79 Anatomy affected
questions but intentionally failed before commit because one browser-test anchor
belongs to verify_marrow_bank_browser_core.py rather than its taxonomy wrapper.
This driver keeps the same fail-closed repair and places the checks at their
actual owners.
"""
from __future__ import annotations

from pathlib import Path
import repair_marrow_option_contract as base

ROOT = Path(__file__).resolve().parents[1]


def patch_core_existing_answer_regression() -> None:
    path = ROOT / "tools" / "verify_marrow_bank_browser_core.py"
    text = path.read_text(encoding="utf-8")
    old = """            page.locator('.option-list button').first.click();page.wait_for_timeout(120)\n            bsupport=page.locator('.nk-study-support').inner_text().lower()\n"""
    new = """            page.locator('.option-list button').first.click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('Existing Marrow wrong-answer visual state must show one red wrong and one green correct option')\n            if page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")!='rgb(16, 154, 99)':\n                raise SystemExit('Existing Marrow correct option is not visually green after a wrong answer')\n            if page.locator('.option-list .option.wrong .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")!='rgb(201, 75, 87)':\n                raise SystemExit('Existing Marrow selected wrong option is not visually red')\n            bsupport=page.locator('.nk-study-support').inner_text().lower()\n"""
    if new in text:
        return
    if text.count(old) != 1:
        raise SystemExit(f"core existing-answer browser anchor count={text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("MARROW_OPTION_CORE_BROWSER_GUARD_OK existing")


def patch_wrapper_new_answer_regressions() -> None:
    path = ROOT / "tools" / "verify_marrow_bank_browser.py"
    text = path.read_text(encoding="utf-8")

    old_phys = """            if not page.locator('.question-text').inner_text().strip(): raise SystemExit('Exercise Physiology source question did not render as a learner question')\n            page.evaluate(\"window.QB.nav('banks','Physiology')\");page.wait_for_timeout(80)\n"""
    new_phys = """            if not page.locator('.question-text').inner_text().strip(): raise SystemExit('Exercise Physiology source question did not render as a learner question')\n            phys_qid=page.evaluate(\"state.activeSession.questionIds[state.activeSession.index]\")\n            if phys_qid!='marrow__PHYSIO_CH43_Q001': raise SystemExit(f'Unexpected new Physiology regression target: {phys_qid}')\n            phys_correct=int(page.evaluate(\"(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()\"))-1\n            page.locator('.option-list button').nth((phys_correct+1)%4).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('New Physiology wrong answer must render exactly one red wrong and one green correct option')\n            phys_green=page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            phys_red=page.locator('.option-list .option.wrong .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            if phys_green!='rgb(16, 154, 99)' or phys_red!='rgb(201, 75, 87)':\n                raise SystemExit(f'New Physiology answer colors regressed: correct={phys_green} wrong={phys_red}')\n            # Exercise the exact learner entry point reported in the regression.\n            page.evaluate(\"window.QB.startLibrary('wrong')\");page.wait_for_timeout(100)\n            wrong_ids=page.evaluate(\"state.activeSession.questionIds\")\n            if 'marrow__PHYSIO_CH43_Q001' not in wrong_ids:\n                raise SystemExit(f'Wrong Questions library did not include the newly missed Physiology question: {wrong_ids}')\n            wrong_index=wrong_ids.index('marrow__PHYSIO_CH43_Q001')\n            page.evaluate(\"i=>window.QB.goIndex(i)\", wrong_index);page.wait_for_timeout(80)\n            phys_correct_again=int(page.evaluate(\"(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()\"))-1\n            page.locator('.option-list button').nth((phys_correct_again+1)%4).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('Wrong Questions flow failed to show both wrong/red and correct/green states')\n            if page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")!='rgb(16, 154, 99)':\n                raise SystemExit('Wrong Questions flow correct answer is not green')\n            page.evaluate(\"window.QB.nav('banks','Physiology')\");page.wait_for_timeout(80)\n"""
    if new_phys not in text:
        if text.count(old_phys) != 1:
            raise SystemExit(f"wrapper new-Physiology answer anchor count={text.count(old_phys)}")
        text = text.replace(old_phys, new_phys, 1)

    old_anatomy = """            if 'total number of bones' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('New Anatomy Ch60 source question did not render normally')\n            page.evaluate(\"window.QB.nav('banks','Anatomy')\");page.wait_for_timeout(80)\n"""
    new_anatomy = """            if 'total number of bones' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('New Anatomy Ch60 source question did not render normally')\n            anatomy_qid=page.evaluate(\"state.activeSession.questionIds[state.activeSession.index]\")\n            if anatomy_qid!='marrow__ANAT_CH60_Q001': raise SystemExit(f'Unexpected new Anatomy regression target: {anatomy_qid}')\n            anatomy_correct=int(page.evaluate(\"(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()\"))-1\n            page.locator('.option-list button').nth((anatomy_correct+1)%4).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('New Anatomy wrong answer must render exactly one red wrong and one green correct option')\n            anatomy_green=page.locator('.option-list .option.correct .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            anatomy_red=page.locator('.option-list .option.wrong .option-letter').evaluate(\"el=>getComputedStyle(el).backgroundColor\")\n            if anatomy_green!='rgb(16, 154, 99)' or anatomy_red!='rgb(201, 75, 87)':\n                raise SystemExit(f'New Anatomy answer colors regressed: correct={anatomy_green} wrong={anatomy_red}')\n            page.evaluate(\"window.QB.nav('banks','Anatomy')\");page.wait_for_timeout(80)\n"""
    if new_anatomy not in text:
        if text.count(old_anatomy) != 1:
            raise SystemExit(f"wrapper new-Anatomy answer anchor count={text.count(old_anatomy)}")
        text = text.replace(old_anatomy, new_anatomy, 1)

    text = text.replace(
        "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2376",
        "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2455",
    )
    path.write_text(text, encoding="utf-8")
    print("MARROW_OPTION_WRAPPER_BROWSER_GUARDS_OK physiology+wrong-library+anatomy")


def main() -> None:
    base.normalize_bundle("physiology_ch001_043", expected_changed_questions=261)
    base.normalize_bundle("anatomy_ch001_048_plus_060_063", expected_changed_questions=79)
    base.patch_importers()
    base.patch_runtime_validator()
    base.patch_static_test()
    base.patch_session_renderer()
    patch_core_existing_answer_regression()
    patch_wrapper_new_answer_regressions()
    base.patch_state()
    print("MARROW_OPTION_CONTRACT_REPAIR_V2_OK source_jsonl=unchanged runtime=A-D fail_closed=yes browser=red+green")


if __name__ == "__main__":
    main()
