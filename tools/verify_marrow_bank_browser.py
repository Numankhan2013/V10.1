#!/usr/bin/env python3
"""Run the preserved Marrow browser suite with the approved Home V3 navigation.

The full regression suite remains byte-for-byte in
verify_marrow_bank_browser_legacy.py. This adapter updates only intentionally
superseded Home assertions/navigation before executing that complete suite.
"""

from pathlib import Path

HERE=Path(__file__).resolve().parent
LEGACY=HERE/'verify_marrow_bank_browser_legacy.py'


def main():
    source=LEGACY.read_text(encoding='utf-8')
    old_home="""            if 'recommended now' not in home_focus.inner_text().lower():
                raise SystemExit('Home recommendation hierarchy is not visible')
            if 'Practice 20 Random Questions' not in home_focus.locator('.nk-focus-primary').inner_text():
                raise SystemExit('Clean-state Home recommendation is not Practice 20')
            secondary=home_focus.locator('.nk-focus-secondary').inner_text()
            for marker in ('Continue Practice','Timed CBT'):
                if marker not in secondary:
                    raise SystemExit(f'Home command center lost {marker}')
"""
    new_home="""            home_text=home_focus.inner_text()
            for marker in (\"TODAY'S FOCUS\",'Continue Practice','FSRS','Bookmarks','My Subjects','My Progress','Strongest Chapters','Study Sessions',\"Today's Review\"):
                if marker not in home_text:
                    raise SystemExit(f'Approved Home V3 lost {marker}')
            if 'Continue Practice' not in home_focus.locator('.nk-focus-primary').inner_text():
                raise SystemExit('Approved Today’s Focus primary action is not Continue Practice')
            quick=home_focus.locator('.nk-home-quick-grid').inner_text()
            for marker in ('FSRS','Bookmarks'):
                if marker not in quick:
                    raise SystemExit(f'Home V3 review shortcuts lost {marker}')
            if 'Timed Test' in quick or 'Practice' in quick:
                raise SystemExit('Home V3 quick shortcuts must contain only FSRS and Bookmarks')
"""
    if source.count(old_home)!=1:raise SystemExit(f'Expected one stale Home assertion block, found {source.count(old_home)}')
    source=source.replace(old_home,new_home,1)

    replacements={
        "page.locator('button.nk-subject-row').filter(has_text='Biochemistry').click();page.wait_for_timeout(80)":"page.evaluate(\"window.QB.nav('banks','Biochemistry')\");page.wait_for_timeout(80)",
        "page.locator('button.nk-subject-row').filter(has_text='Physiology').click();page.wait_for_timeout(80)":"page.evaluate(\"window.QB.nav('banks','Physiology')\");page.wait_for_timeout(80)",
        "page.locator('button.nk-subject-row').filter(has_text='Anatomy').click()":"page.evaluate(\"window.QB.nav('banks','Anatomy')\")",
    }
    for old,new in replacements.items():
        count=source.count(old)
        if count!=1:raise SystemExit(f'Expected one stale Home navigation call, found {count}: {old}')
        source=source.replace(old,new,1)

    namespace={'__name__':'__main__','__file__':str(LEGACY),'__package__':None}
    exec(compile(source,str(LEGACY),'exec'),namespace,namespace)


if __name__=='__main__':main()
