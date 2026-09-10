#!/usr/bin/env python3
"""Run the preserved Marrow browser suite with current Home navigation.

The full regression suite is retained byte-for-byte in
verify_marrow_bank_browser_legacy.py. The approved Home redesign intentionally
changes the old recommendation hierarchy and removes legacy subject-row cards,
so this adapter updates only those obsolete Home assertions/navigation calls
before executing the complete legacy Marrow regression suite.
"""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE / "verify_marrow_bank_browser_legacy.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8")

    old_home = """            if 'recommended now' not in home_focus.inner_text().lower():
                raise SystemExit('Home recommendation hierarchy is not visible')
            if 'Practice 20 Random Questions' not in home_focus.locator('.nk-focus-primary').inner_text():
                raise SystemExit('Clean-state Home recommendation is not Practice 20')
            secondary=home_focus.locator('.nk-focus-secondary').inner_text()
            for marker in ('Continue Practice','Timed CBT'):
                if marker not in secondary:
                    raise SystemExit(f'Home command center lost {marker}')
"""
    new_home = """            home_text=home_focus.inner_text()
            for marker in (\"TODAY'S FOCUS\",'Continue Practice','Timed Test','Practice','FSRS','Bookmarks'):
                if marker not in home_text:
                    raise SystemExit(f'Approved Home command center lost {marker}')
            if 'Continue Practice' not in home_focus.locator('.nk-focus-primary').inner_text():
                raise SystemExit('Approved Today’s Focus primary action is not Continue Practice')
"""
    if source.count(old_home) != 1:
        raise SystemExit(f"Expected exactly one stale Home hierarchy assertion block, found {source.count(old_home)}")
    source = source.replace(old_home, new_home, 1)

    replacements = {
        "page.locator('button.nk-subject-row').filter(has_text='Biochemistry').click();page.wait_for_timeout(80)":
            "page.evaluate(\"window.QB.nav('banks','Biochemistry')\");page.wait_for_timeout(80)",
        "page.locator('button.nk-subject-row').filter(has_text='Physiology').click();page.wait_for_timeout(80)":
            "page.evaluate(\"window.QB.nav('banks','Physiology')\");page.wait_for_timeout(80)",
        "page.locator('button.nk-subject-row').filter(has_text='Anatomy').click()":
            "page.evaluate(\"window.QB.nav('banks','Anatomy')\")",
    }
    for old, new in replacements.items():
        count = source.count(old)
        if count != 1:
            raise SystemExit(f"Expected exactly one stale Home navigation call, found {count}: {old}")
        source = source.replace(old, new, 1)

    namespace = {
        "__name__": "__main__",
        "__file__": str(LEGACY),
        "__package__": None,
    }
    exec(compile(source, str(LEGACY), "exec"), namespace, namespace)


if __name__ == "__main__":
    main()
