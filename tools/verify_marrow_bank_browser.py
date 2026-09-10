#!/usr/bin/env python3
"""Run the preserved Marrow browser suite with current Home navigation.

The full regression suite is retained byte-for-byte in
verify_marrow_bank_browser_legacy.py. The approved Home redesign intentionally
removes legacy subject-row cards, so only those three obsolete navigation calls
are adapted to the stable public QB bank-navigation API before execution.
"""

from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE / "verify_marrow_bank_browser_legacy.py"


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8")
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
