#!/usr/bin/env python3
"""Run the Marrow browser suite against the canonical V3 subject→Topics flow.

The historical wrapper still carries the full stable regression contract. This
shim changes only obsolete bank-selector navigation; all content, image,
explanation, FSRS, answer-state, taxonomy and screenshot assertions remain in
that suite.
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
# preferred Marrow Topics journey directly. Preserve every downstream
# regression assertion and replace only the obsolete navigation gestures.
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

for subject in ('Biochemistry','Physiology','Anatomy'):
    replacement = "            page.evaluate(\"window.QB.nkOpenSubjectLibrary('%s')\");page.wait_for_timeout(120)" % subject
    for first_wait in (60,80,100,120):
        for second_wait in (60,80,100,120):
            old = "            page.evaluate(\"window.QB.nav('banks','%s')\");page.wait_for_timeout(%d)\n            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(%d)" % (subject, first_wait, second_wait)
            source = source.replace(old, replacement)

# The canonical corpus is complete and no browser assertion may regress to an
# intermediate denominator.
source = source.replace("'543'", "'582'")
source = source.replace("'753'", "'1,014'")
source = source.replace("biochemistry=543/26", "biochemistry=582/28")
source = source.replace("physiology=753/33", "physiology=1014/43")
source = source.replace("total=2115", "total=2711")
"""
wrapper = wrapper.replace(anchor, "\n" + compat + anchor, 1)
exec(
    compile(wrapper, str(LEGACY), "exec"),
    {"__name__": "__main__", "__file__": str(LEGACY), "__builtins__": __builtins__},
)
