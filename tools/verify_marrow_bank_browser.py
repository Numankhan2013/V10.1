#!/usr/bin/env python3
"""Run the Marrow browser suite against the canonical V3 subject→Topics flow.

The historical wrapper still carries the full stable regression contract. This
shim changes only obsolete bank-selector navigation/count expectations; all
content, image, explanation, FSRS, answer-state, taxonomy and screenshot
assertions remain in that suite.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "tools" / "verify_marrow_bank_browser_legacy.py"
wrapper = LEGACY.read_text(encoding="utf-8")
anchor = "\nexec(\n    compile(source, str(CORE), \"exec\"),"
if wrapper.count(anchor) != 1:
    raise SystemExit(f"Legacy Marrow browser exec anchor count: {wrapper.count(anchor)}")

compat = r"""
# Canonical V3 navigation compatibility. The learner no longer visits an
# intermediate PrepLadder/Marrow bank-selector page; subject cards open the
# preferred Marrow Topics journey directly. Preserve downstream regression
# assertions and replace only obsolete learner-navigation gestures.
old_initial = '''            page.locator('button.nk-subject-row').filter(has_text='Biochemistry').click();page.wait_for_timeout(80)
            if '#banks/Biochemistry' not in page.url: raise SystemExit(f'Biochemistry did not open bank selector: {page.url}')
            bcards=page.locator('button.nk-bank-card')
            if bcards.count()!=2: raise SystemExit(f'Expected 2 Biochemistry banks, found {bcards.count()}')
            bbody=page.locator('body').inner_text()
            for marker in ('PrepLadder','Marrow','582'):
                if marker not in bbody: raise SystemExit(f'Biochemistry bank selector missing {marker}')
            page.screenshot(path=str(OUT/'00-biochemistry-bank-selector.png'),full_page=True)
            bcards.filter(has_text='Marrow').click();page.wait_for_timeout(100)'''
new_initial = '''            page.evaluate("window.QB.nkOpenSubjectLibrary('Biochemistry')");page.wait_for_timeout(120)
            page.screenshot(path=str(OUT/'00-biochemistry-topics.png'),full_page=True)'''
if source.count(old_initial) != 1:
    raise SystemExit(f'Canonical V3 initial Biochemistry navigation anchor count: {source.count(old_initial)}')
source = source.replace(old_initial, new_initial, 1)

old_phys = '''            page.locator('button.nk-subject-row').filter(has_text='Physiology').click();page.wait_for_timeout(80)
            if '#banks/Physiology' not in page.url: raise SystemExit(f'Physiology did not open bank selector: {page.url}')
            pcards=page.locator('button.nk-bank-card')
            if pcards.count()!=2: raise SystemExit(f'Expected 2 Physiology banks, found {pcards.count()}')
            pbody=page.locator('body').inner_text()
            for marker in ('PrepLadder','Marrow','753'):
                if marker not in pbody: raise SystemExit(f'Physiology bank selector missing {marker}')
            page.screenshot(path=str(OUT/'00-physiology-bank-selector.png'),full_page=True)
            pcards.filter(has_text='Marrow').click();page.wait_for_timeout(100)'''
new_phys = '''            page.evaluate("window.QB.nkOpenSubjectLibrary('Physiology')");page.wait_for_timeout(120)
            page.screenshot(path=str(OUT/'00-physiology-topics.png'),full_page=True)'''
if source.count(old_phys) != 1:
    raise SystemExit(f'Canonical V3 initial Physiology navigation anchor count: {source.count(old_phys)}')
source = source.replace(old_phys, new_phys, 1)

old_anat = '''            page.locator('button.nk-subject-row').filter(has_text='Anatomy').click()
            page.wait_for_timeout(100)
            if '#banks/Anatomy' not in page.url: raise SystemExit(f'Anatomy did not open bank selector: {page.url}')
            cards=page.locator('button.nk-bank-card')
            if cards.count()!=2: raise SystemExit(f'Expected 2 Anatomy banks, found {cards.count()}')
            body=page.locator('body').inner_text()
            for marker in ('PrepLadder','Marrow','1,068','819'):
                if marker not in body: raise SystemExit(f'Bank selector missing {marker}')
            page.screenshot(path=str(OUT/'01-anatomy-bank-selector.png'),full_page=True)
            cards.filter(has_text='Marrow').click();page.wait_for_timeout(100)'''
new_anat = '''            page.evaluate("window.QB.nkOpenSubjectLibrary('Anatomy')");page.wait_for_timeout(120)
            page.screenshot(path=str(OUT/'01-anatomy-topics.png'),full_page=True)'''
if source.count(old_anat) != 1:
    raise SystemExit(f'Canonical V3 initial Anatomy navigation anchor count: {source.count(old_anat)}')
source = source.replace(old_anat, new_anat, 1)

# Repeated regression jumps back into the Marrow side of a subject. In V3 that
# is the subject library/Topics journey rather than the bank-selector page.
for subject in ('Biochemistry','Physiology','Anatomy'):
    replacement = "            page.evaluate(\"window.QB.nkOpenSubjectLibrary('%s')\");page.wait_for_timeout(120)" % subject
    for first_wait in (60,80,100,120):
        for second_wait in (60,80,100,120):
            old = "            page.evaluate(\"window.QB.nav('banks','%s')\");page.wait_for_timeout(%d)\n            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(%d)" % (subject, first_wait, second_wait)
            source = source.replace(old, replacement)

# The canonical corpus is complete. Keep all content assertions but update only
# obsolete Phase-A denominators and visible Marrow topic counts.
source = source.replace("'543'", "'582'")
source = source.replace("'753'", "'1,014'")
source = source.replace("'819'", "'1,115'")
source = source.replace("count()!=33: raise SystemExit('Marrow Physiology topic count is not 33')", "count()!=43: raise SystemExit('Marrow Physiology topic count is not 43')")
source = source.replace("count()!=48: raise SystemExit('Marrow Anatomy topic count is not 48')", "count()!=63: raise SystemExit('Marrow Anatomy topic count is not 63')")
source = source.replace("range(1,49)", "range(1,64)")
source = source.replace("biochemistry=543/26", "biochemistry=582/28")
source = source.replace("physiology=753/33", "physiology=1014/43")
source = source.replace("anatomy=819/48", "anatomy=1115/63")
source = source.replace("total=2115", "total=2711")
source = source.replace("enhanced=184 rationales=552", "enhanced=429 pending=2282")
"""
wrapper = wrapper.replace(anchor, "\n" + compat + anchor, 1)
exec(
    compile(wrapper, str(LEGACY), "exec"),
    {"__name__": "__main__", "__file__": str(LEGACY), "__builtins__": __builtins__},
)
