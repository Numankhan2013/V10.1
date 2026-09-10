#!/usr/bin/env python3
"""Run the full Marrow browser regression core with current taxonomy assertions."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools" / "verify_marrow_bank_browser_core.py"

source = CORE.read_text(encoding="utf-8")

replacements = {
    "            for marker in ('PrepLadder','Marrow','753'):": "            for marker in ('PrepLadder','Marrow','1,014'):",
    "            if page.locator('button.nk-topic-row').count()!=33: raise SystemExit('Marrow Physiology topic count is not 33')": "            if page.locator('button.nk-topic-row').count()!=43: raise SystemExit('Marrow Physiology topic count is not 43')",
}
for old, new in replacements.items():
    if source.count(old) != 1:
        raise SystemExit(f"Physiology browser source-count anchor count for {old!r}: {source.count(old)}")
    source = source.replace(old, new, 1)

old = "            assert_sections(['CNS Physiology','General Physiology','Cellular Physiology','Neuromuscular Physiology','Cardiovascular System','Respiratory System','Gastrointestinal System'])"
new = """            assert_sections(['General physiology','Nerve and muscle physiology','Gastrointestinal system','Cardiovascular system','Respiratory system','Renal physiology','Endocrine physiology','Reproductive physiology','Central nervous system','Integrated physiology'])
            pnums=[int(x) for x in page.locator('.nk-topic-index').all_inner_texts()]
            if pnums!=list(range(1,44)): raise SystemExit(f'Marrow Physiology learner numbering is not contiguous 1-43: {pnums!r}')

            # New automation-ingested content must render as normal learner content,
            # never as serialized JSON/schema text.
            page.locator('button.nk-topic-row').filter(has_text='Exercise Physiology').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=16: raise SystemExit('Marrow Physiology Exercise Physiology count is not 16')
            page.locator('button.nk-library-row').nth(0).click();page.wait_for_timeout(80)
            learner_text=page.locator('body').inner_text()
            for raw_marker in ('chapter_number','source_provenance','source_answer','schema_version','review_status','source_fidelity_notes'):
                if raw_marker in learner_text: raise SystemExit(f'Raw automation JSON key leaked into learner view: {raw_marker}')
            for raw_fragment in ('{\"chapter\"','\"source_answer\":','\"source_provenance\":'):
                if raw_fragment in learner_text: raise SystemExit(f'Serialized automation JSON leaked into learner view: {raw_fragment}')
            if not page.locator('.question-text').inner_text().strip(): raise SystemExit('Exercise Physiology source question did not render as a learner question')
            phys_question=page.locator('.question-text').inner_text().lower()
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
            page.evaluate("window.QB.nav('banks','Physiology')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)"""
if source.count(old) != 1:
    raise SystemExit(f"Physiology browser taxonomy assertion anchor count: {source.count(old)}")
source = source.replace(old, new, 1)

old_summary = "biochemistry=543/26 physiology=753/33 total=2115"
new_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2455"
if source.count(old_summary) != 1:
    raise SystemExit(f"Marrow browser summary anchor count: {source.count(old_summary)}")
source = source.replace(old_summary, new_summary, 1)

# Anatomy Ch60-63 source expansion layered on top of the current core.
anatomy_replacements = {
    "            for marker in ('PrepLadder','Marrow','1,068','819'):": "            for marker in ('PrepLadder','Marrow','1,068','898'):",
    "            if page.locator('button.nk-topic-row').count()!=48: raise SystemExit('Marrow Anatomy topic count is not 48')": "            if page.locator('button.nk-topic-row').count()!=52: raise SystemExit('Marrow Anatomy topic count is not 52')",
    "            assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis'])": "            assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis','General anatomy'])",
    "            if serials!=[str(i) for i in range(1,49)]: raise SystemExit(f'Marrow Anatomy learner numbering is not contiguous: {serials!r}')": "            if serials!=[str(i) for i in range(1,53)]: raise SystemExit(f'Marrow Anatomy learner numbering is not contiguous 1-52: {serials!r}')",
}
for old, new in anatomy_replacements.items():
    if source.count(old) != 1:
        raise SystemExit(f"Anatomy browser source-count/taxonomy anchor count for {old!r}: {source.count(old)}")
    source = source.replace(old, new, 1)

shot_anchor = "            page.screenshot(path=str(OUT/'02-marrow-topics.png'),full_page=True)"
shot_new = shot_anchor + """
            page.locator('button.nk-topic-row').filter(has_text='Bones, Joints and Cartilage').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=30: raise SystemExit('Marrow Anatomy Bones, Joints and Cartilage count is not 30')
            page.locator('button.nk-library-row').nth(0).click();page.wait_for_timeout(80)
            anatomy_learner_text=page.locator('body').inner_text()
            for raw_marker in ('question_id','chapter_number','correct_option','schema_version','review_status','source_fidelity'):
                if raw_marker in anatomy_learner_text: raise SystemExit(f'Raw Anatomy automation JSON key leaked into learner view: {raw_marker}')
            for raw_fragment in ('{\"question_id\"','\"correct_option\":','\"source_fidelity\":'):
                if raw_fragment in anatomy_learner_text: raise SystemExit(f'Serialized Anatomy automation JSON leaked into learner view: {raw_fragment}')
            if 'total number of bones' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('New Anatomy Ch60 source question did not render normally')
            anatomy_question=page.locator('.question-text').inner_text().lower()
            if 'total number of bones' not in anatomy_question:
                raise SystemExit(f'Unexpected new Anatomy regression target: {anatomy_question!r}')
            page.locator('.option-list button').nth(0).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('New Anatomy wrong answer must render exactly one red wrong and one green correct option')
            anatomy_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            anatomy_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if anatomy_green!='rgb(16, 154, 99)' or anatomy_red!='rgb(201, 75, 87)':
                raise SystemExit(f'New Anatomy answer colors regressed: correct={anatomy_green} wrong={anatomy_red}')
            page.evaluate("window.QB.nav('banks','Anatomy')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
"""
if source.count(shot_anchor) != 1:
    raise SystemExit(f"Anatomy learner leakage insertion anchor count: {source.count(shot_anchor)}")
source = source.replace(shot_anchor, shot_new, 1)
source = source.replace('anatomy=819/48', 'anatomy=898/52')

# Biochemistry Ch27-28 source expansion: keep the core smoke suite and extend it.
biochem_replacements = {
    "            for marker in ('PrepLadder','Marrow','543'):": "            for marker in ('PrepLadder','Marrow','582'):",
    "            if page.locator('button.nk-topic-row').count()!=26: raise SystemExit('Marrow Biochemistry topic count is not 26')": "            if page.locator('button.nk-topic-row').count()!=28: raise SystemExit('Marrow Biochemistry topic count is not 28')",
    "            if bnums!=list(range(1,27)): raise SystemExit(f'Marrow Biochemistry learner numbering is not contiguous 1-26: {bnums!r}')": "            if bnums!=list(range(1,29)): raise SystemExit(f'Marrow Biochemistry learner numbering is not contiguous 1-28: {bnums!r}')",
}
for old, new in biochem_replacements.items():
    if source.count(old) != 1:
        raise SystemExit(f"Biochemistry browser source-count/numbering anchor count for {old!r}: {source.count(old)}")
    source = source.replace(old, new, 1)

biochem_anchor = "            page.locator('button.nk-topic-row').filter(has_text='Chemistry of Carbohydrates, Amino sugars and Mucopolysaccharides').click();page.wait_for_timeout(80)"
biochem_guard = """            # User-supplied Ch27-28 must render as ordinary learner content and preserve answer-state feedback.
            page.locator('button.nk-topic-row').filter(has_text='Regulation of gene expression').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=12: raise SystemExit('Marrow Biochemistry Ch27 count is not 12')
            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)
            if 'housekeeping genes' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Ch27 Q1 did not render')
            learner_text=page.locator('body').inner_text()
            for raw_marker in ('question_id','chapter_number','correct_option','schema_version','review_status','source_fidelity'):
                if raw_marker in learner_text: raise SystemExit(f'Raw Biochemistry JSON key leaked into learner view: {raw_marker}')
            for raw_fragment in ('{\"question_id\"','\"correct_option\":','\"source_fidelity\":'):
                if raw_fragment in learner_text: raise SystemExit(f'Serialized Biochemistry JSON leaked into learner view: {raw_fragment}')
            page.locator('.option-list button').nth(0).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('New Biochemistry Ch27 wrong answer must show exactly one red wrong and one green correct option')
            ch27_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            ch27_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if ch27_green!='rgb(16, 154, 99)' or ch27_red!='rgb(201, 75, 87)':
                raise SystemExit(f'New Biochemistry Ch27 answer colors regressed: correct={ch27_green} wrong={ch27_red}')

            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
            page.locator('button.nk-topic-row').filter(has_text='Molecular genetics, recombinant DNA & genomic technologies').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=27: raise SystemExit('Marrow Biochemistry Ch28 count is not 27')
            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)
            if 'enzymes that cut dna' not in page.locator('.question-text').inner_text().lower():
                raise SystemExit('Biochemistry Ch28 Q1 did not render')
            learner_text=page.locator('body').inner_text()
            for raw_marker in ('question_id','chapter_number','correct_option','schema_version','review_status','source_fidelity'):
                if raw_marker in learner_text: raise SystemExit(f'Raw Biochemistry Ch28 JSON key leaked into learner view: {raw_marker}')
            page.locator('.option-list button').nth(0).click();page.wait_for_timeout(120)
            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:
                raise SystemExit('New Biochemistry Ch28 wrong answer must show exactly one red wrong and one green correct option')
            ch28_green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            ch28_red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")
            if ch28_green!='rgb(16, 154, 99)' or ch28_red!='rgb(201, 75, 87)':
                raise SystemExit(f'New Biochemistry Ch28 answer colors regressed: correct={ch28_green} wrong={ch28_red}')

            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)
"""
if source.count(biochem_anchor) < 1:
    raise SystemExit('Biochemistry browser insertion anchor missing')
source = source.replace(biochem_anchor, biochem_guard + biochem_anchor, 1)

old_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2455"
new_summary = "biochemistry=582/28 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2494"
if source.count(old_summary) != 1:
    raise SystemExit(f"Expanded Marrow browser summary anchor count: {source.count(old_summary)}")
source = source.replace(old_summary, new_summary, 1)

exec(
    compile(source, str(CORE), "exec"),
    {"__name__": "__main__", "__file__": str(CORE), "__builtins__": __builtins__},
)
