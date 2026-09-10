#!/usr/bin/env python3
"""Final fail-closed driver for the Marrow option-state regression repair."""
from __future__ import annotations

from pathlib import Path
import repair_marrow_option_contract as base
import repair_marrow_option_contract_v2 as v2

ROOT = Path(__file__).resolve().parents[1]


def insert_after_once(text: str, anchor: str, addition: str, label: str) -> str:
    if addition.strip() in text:
        return text
    if text.count(anchor) != 1:
        raise SystemExit(f"{label}: expected one anchor, found {text.count(anchor)}")
    return text.replace(anchor, anchor + addition, 1)


def patch_wrapper() -> None:
    path = ROOT / "tools" / "verify_marrow_bank_browser.py"
    text = path.read_text(encoding="utf-8")

    phys_anchor = "            if not page.locator('.question-text').inner_text().strip(): raise SystemExit('Exercise Physiology source question did not render as a learner question')\n"
    phys_add = r'''            phys_qid=page.evaluate("state.activeSession.questionIds[state.activeSession.index]")
            if phys_qid!='marrow__PHYSIO_CH43_Q001': raise SystemExit(f'Unexpected new Physiology regression target: {phys_qid}')
            phys_correct=int(page.evaluate("(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()"))-1
            page.locator('.option-list button').nth((phys_correct+1)%4).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('New Physiology wrong answer must render exactly one red wrong and one green correct option')
            phys_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            phys_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if phys_green!='rgb(16, 154, 99)' or phys_red!='rgb(201, 75, 87)':
                raise SystemExit(f'New Physiology answer colors regressed: correct={phys_green} wrong={phys_red}')
            page.evaluate("window.QB.startLibrary('wrong')");page.wait_for_timeout(100)
            wrong_ids=page.evaluate("state.activeSession.questionIds")
            if 'marrow__PHYSIO_CH43_Q001' not in wrong_ids:
                raise SystemExit(f'Wrong Questions library did not include the newly missed Physiology question: {wrong_ids}')
            wrong_index=wrong_ids.index('marrow__PHYSIO_CH43_Q001')
            page.evaluate("i=>window.QB.goIndex(i)",wrong_index);page.wait_for_timeout(80)
            phys_correct_again=int(page.evaluate("(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()"))-1
            page.locator('.option-list button').nth((phys_correct_again+1)%4).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('Wrong Questions flow failed to show both wrong/red and correct/green states')
            if page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")!='rgb(16, 154, 99)':
                raise SystemExit('Wrong Questions flow correct answer is not green')
'''
    text = insert_after_once(text, phys_anchor, phys_add, "Physiology answer-state browser guard")

    anatomy_anchor = "            if 'total number of bones' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('New Anatomy Ch60 source question did not render normally')\n"
    anatomy_add = r'''            anatomy_qid=page.evaluate("state.activeSession.questionIds[state.activeSession.index]")
            if anatomy_qid!='marrow__ANAT_CH60_Q001': raise SystemExit(f'Unexpected new Anatomy regression target: {anatomy_qid}')
            anatomy_correct=int(page.evaluate("(()=>{const s=state.activeSession,q=BY_ID[s.questionIds[s.index]];return Number(q.correctOption)})()"))-1
            page.locator('.option-list button').nth((anatomy_correct+1)%4).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('New Anatomy wrong answer must render exactly one red wrong and one green correct option')
            anatomy_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            anatomy_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if anatomy_green!='rgb(16, 154, 99)' or anatomy_red!='rgb(201, 75, 87)':
                raise SystemExit(f'New Anatomy answer colors regressed: correct={anatomy_green} wrong={anatomy_red}')
'''
    text = insert_after_once(text, anatomy_anchor, anatomy_add, "Anatomy answer-state browser guard")

    text = text.replace(
        'new_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2376"',
        'new_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2455"',
    )
    path.write_text(text, encoding="utf-8")
    print("MARROW_OPTION_WRAPPER_BROWSER_GUARDS_V3_OK physiology+wrong-library+anatomy")


def main() -> None:
    base.normalize_bundle("physiology_ch001_043", expected_changed_questions=261)
    base.normalize_bundle("anatomy_ch001_048_plus_060_063", expected_changed_questions=79)
    base.patch_importers()
    base.patch_runtime_validator()
    base.patch_static_test()
    base.patch_session_renderer()
    v2.patch_core_existing_answer_regression()
    patch_wrapper()
    base.patch_state()
    print("MARROW_OPTION_CONTRACT_REPAIR_V3_OK affected=340 source_jsonl=unchanged runtime=A-D browser=wrong+correct")


if __name__ == "__main__":
    main()
