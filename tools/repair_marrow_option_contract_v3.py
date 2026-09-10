#!/usr/bin/env python3
"""Final fail-closed driver for the Marrow option-state regression repair.

The runtime repair is already source-safe: canonical automation JSONL remains
unchanged, generated Marrow bundles use uppercase A-D, and the shared session
renderer tolerates option-letter case. This pass hardens browser coverage using
only learner-visible UI so CI validates the same paths a learner actually uses.
"""
from __future__ import annotations

from pathlib import Path
import repair_marrow_option_contract as base
import repair_marrow_option_contract_v2 as v2

ROOT = Path(__file__).resolve().parents[1]


def replace_between(text: str, start: str, end: str, replacement: str, label: str) -> str:
    """Replace one already-injected block while preserving its trailing anchor."""
    if replacement.strip() in text:
        return text
    if text.count(start) != 1:
        raise SystemExit(f"{label}: expected one start marker, found {text.count(start)}")
    start_i = text.index(start)
    end_i = text.find(end, start_i)
    if end_i < 0:
        raise SystemExit(f"{label}: trailing anchor missing")
    return text[:start_i] + replacement + text[end_i:]


def patch_wrapper() -> None:
    path = ROOT / "tools" / "verify_marrow_bank_browser.py"
    text = path.read_text(encoding="utf-8")

    # Ch43 Q1 is deliberately fixed as the regression target. Its source answer
    # is option A, so selecting visible option B is a deterministic wrong answer.
    # The Wrong Questions check then enters through the real dashboard/library UI.
    phys_start = '            phys_qid=page.evaluate("state.activeSession.questionIds[state.activeSession.index]")\n'
    phys_end = '            page.evaluate(\\"window.QB.nav(\'banks\',\'Physiology\')\\");page.wait_for_timeout(80)\n'
    phys_ui = r'''            phys_question=page.locator('.question-text').inner_text().lower()
            if 'maximum contractile force' not in phys_question:
                raise SystemExit(f'Unexpected new Physiology regression target: {phys_question!r}')
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('New Physiology wrong answer must render exactly one red wrong and one green correct option')
            phys_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            phys_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if phys_green!='rgb(16, 154, 99)' or phys_red!='rgb(201, 75, 87)':
                raise SystemExit(f'New Physiology answer colors regressed: correct={phys_green} wrong={phys_red}')

            # Reproduce the user-reported path without reaching into module-scoped state.
            page.evaluate("window.QB.nav('dashboard')");page.wait_for_timeout(100)
            wrong_button=page.locator('.nk-quick-grid button').filter(has_text='Wrong questions')
            if wrong_button.count()!=1: raise SystemExit(f'Wrong Questions dashboard entry count={wrong_button.count()}')
            wrong_button.click();page.wait_for_timeout(100)
            wrong_row=page.locator('.library-row').filter(has_text='maximum contractile force')
            if wrong_row.count()!=1: raise SystemExit(f'New Physiology miss not present once in Wrong Questions: {wrong_row.count()}')
            wrong_row.locator('button').filter(has_text='Practice').click();page.wait_for_timeout(100)
            if 'maximum contractile force' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Wrong Questions did not reopen the expected Physiology question')
            page.locator('.option-list button').nth(1).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('Wrong Questions flow failed to show both wrong/red and correct/green states')
            wrong_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            wrong_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if wrong_green!='rgb(16, 154, 99)' or wrong_red!='rgb(201, 75, 87)':
                raise SystemExit(f'Wrong Questions answer colors regressed: correct={wrong_green} wrong={wrong_red}')
'''
    text = replace_between(text, phys_start, phys_end, phys_ui, "Physiology learner-UI answer-state guard")

    # Ch60 Q1 source answer is D, so visible option A is a deterministic wrong answer.
    anatomy_start = '            anatomy_qid=page.evaluate("state.activeSession.questionIds[state.activeSession.index]")\n'
    anatomy_end = '            page.evaluate("window.QB.nav(\'banks\',\'Anatomy\')");page.wait_for_timeout(80)\n'
    anatomy_ui = r'''            anatomy_question=page.locator('.question-text').inner_text().lower()
            if 'total number of bones' not in anatomy_question:
                raise SystemExit(f'Unexpected new Anatomy regression target: {anatomy_question!r}')
            page.locator('.option-list button').nth(0).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('New Anatomy wrong answer must render exactly one red wrong and one green correct option')
            anatomy_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            anatomy_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if anatomy_green!='rgb(16, 154, 99)' or anatomy_red!='rgb(201, 75, 87)':
                raise SystemExit(f'New Anatomy answer colors regressed: correct={anatomy_green} wrong={anatomy_red}')
'''
    text = replace_between(text, anatomy_start, anatomy_end, anatomy_ui, "Anatomy learner-UI answer-state guard")

    text = text.replace(
        'new_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2376"',
        'new_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2455"',
    )
    path.write_text(text, encoding="utf-8")
    print("MARROW_OPTION_WRAPPER_BROWSER_GUARDS_V4_OK learner_ui=physiology+wrong-library+anatomy")


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
    print("MARROW_OPTION_CONTRACT_REPAIR_V4_OK affected=340 source_jsonl=unchanged runtime=A-D browser=learner-ui-red+green")


if __name__ == "__main__":
    main()
